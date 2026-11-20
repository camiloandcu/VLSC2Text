import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from conftest import training_fixture
from lsc5 import budget, rgb_budget
from lsc5.io import atomic_json, digest, read_json, sha256
from lsc5.rgb_frames import decode, indices, letterbox, select_pilot


def test_rgb_rounding_letterbox_stream_decode_and_scope(tmp_path):
    assert indices(1).tolist() == [0]*16
    assert indices(3).tolist() == [0]*4+[1]*8+[2]*4
    assert indices(33)[[0, -1]].tolist() == [0, 32]
    with pytest.raises(ValueError):
        indices(0)
    red = np.full((18, 32, 3), [255, 0, 0], dtype=np.uint8)
    boxed = letterbox(red)
    assert boxed.shape == (224, 224, 3) and boxed.dtype == np.uint8
    np.testing.assert_array_equal(boxed[0, 0], [124, 116, 104])
    np.testing.assert_array_equal(boxed[112, 112], [255, 0, 0])
    train = tmp_path/'train'
    p = train/'videos/sign_01/S01_M02_V01_C01_Clip1.mp4'
    p.parent.mkdir(parents=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=32x18:rate=5',
                    '-frames:v', '5', '-c:v', 'libx264', '-crf', '0', '-threads', '1', str(p)], check=True)
    sample = {'id': p.stem, 'video_path': str(p.relative_to(train)), 'video_sha256': sha256(p)}
    a, info = decode(train, sample)
    b, repeated = decode(train, sample)
    old, old_info = decode(train, sample, selected_transport=False)
    assert info['video_frames'] == 5 and info['indices'] == indices(5).tolist()
    assert info['pixels_sha256'] == repeated['pixels_sha256']
    np.testing.assert_array_equal(a, b)
    np.testing.assert_array_equal(a, old)
    assert old_info['pixels_sha256'] == info['pixels_sha256']
    with pytest.raises(ValueError, match='hash'):
        decode(train, dict(sample, video_sha256='0'*64))
    with pytest.raises(ValueError):
        decode(train, dict(sample, video_path='../test/hidden.mp4'))


def test_probe_rejects_rotation(monkeypatch):
    from types import SimpleNamespace
    from lsc5.rgb_frames import probe
    monkeypatch.setattr('lsc5.rgb_frames.subprocess.run', lambda *a, **k: SimpleNamespace(
        stdout=json.dumps({'streams': [{'width': 32, 'height': 18, 'nb_read_frames': '5',
                                        'side_data_list': [{'rotation': 90}]}]}), stderr=''))
    with pytest.raises(ValueError, match='rotation'):
        probe('synthetic')


@pytest.fixture
def rgb_fixture(tmp_path):
    train, manifest = training_fixture(tmp_path/'source', per_class=75)
    ledger = tmp_path/'budget.json'
    budget.initialize(ledger)
    budget.reserve(ledger, 'previous')
    budget.bind_job(ledger, 'previous', '1')
    budget.settle(ledger, 'previous', 3, '1', 'COMPLETED')
    prior = read_json(ledger)['attempts'][0]
    rgb_budget.reserve_local(ledger, 'rgb', manifest)
    reservation = rgb_budget.claim_local(ledger, 'rgb', tmp_path/'supervised', rgb_budget.machine_identity())
    return train, manifest, ledger, reservation, prior


def test_local_ledger_denies_cross_profile_and_preserves_history(rgb_fixture):
    _, manifest, ledger, reservation, prior = rgb_fixture
    rgb_budget.validate_reservation(reservation, manifest)
    assert budget.totals(read_json(ledger)) == (3, 660)
    assert reservation['job_id'] is None
    with pytest.raises(ValueError, match='one authorized'):
        rgb_budget.reserve_local(ledger, 'another', manifest)
    with pytest.raises(ValueError, match='unclaimed'):
        rgb_budget.claim_local(ledger, 'rgb', Path(reservation['run_directory']), rgb_budget.machine_identity())
    with pytest.raises(ValueError):
        budget.bind_job(ledger, 'rgb', '99')
    with pytest.raises(ValueError, match='incompatible'):
        rgb_budget.validate_reservation(dict(reservation, producer_hash='0'*64), manifest)
    stale = dict(reservation, claimed_unix=reservation['claimed_unix']-3601)
    stale['reservation_hash'] = digest({k: v for k, v in stale.items() if k != 'reservation_hash'})
    with pytest.raises(ValueError, match='expired'):
        rgb_budget.validate_reservation(stale, manifest)
    receipt = {'attempt_id': 'rgb', 'reservation_hash': reservation['reservation_hash'],
               'producer_hash': reservation['producer_hash'], 'terminal_state': 'FAILED', 'actual_seconds': 12}
    with pytest.raises(ValueError, match='Measured'):
        rgb_budget.settle_local(ledger, dict(receipt, actual_seconds=float('nan')))
    with pytest.raises(ValueError, match='evidence'):
        rgb_budget.settle_local(ledger, dict(receipt, terminal_state='COMPLETED'))
    rgb_budget.settle_local(ledger, receipt)
    final = read_json(ledger)
    assert budget.totals(final) == (15, 0) and final['attempts'][0] == prior
    assert final['cash_paid_usd'] == 0 and final['final_reserve_seconds'] == 43200
    with pytest.raises(ValueError):
        rgb_budget.settle_local(ledger, receipt)


def test_explicit_retry_preserves_failed_original_and_cannot_chain(rgb_fixture):
    _, manifest, ledger, original, prior = rgb_fixture
    with pytest.raises(ValueError, match='settled failed original'):
        rgb_budget.reserve_local(ledger, 'retry', manifest, retry_of='rgb')
    with pytest.raises(ValueError, match='settled failed original'):
        rgb_budget.reserve_local(ledger, 'retry', manifest, retry_of='missing')
    failure = {'attempt_id': 'rgb', 'reservation_hash': original['reservation_hash'],
               'producer_hash': original['producer_hash'], 'terminal_state': 'FAILED', 'actual_seconds': 12}
    rgb_budget.settle_local(ledger, failure)
    before = read_json(ledger)
    with pytest.raises(ValueError, match='one authorized'):
        rgb_budget.reserve_local(ledger, 'retry', manifest)
    rgb_budget.reserve_local(ledger, 'retry', manifest, retry_of='rgb')
    reservation = rgb_budget.claim_local(ledger, 'retry', Path(original['run_directory']).parent/'retry',
                                        rgb_budget.machine_identity())
    rgb_budget.validate_reservation(reservation, manifest)
    assert reservation['scope'] == rgb_budget.RETRY_SCOPE and reservation['retry_of'] == 'rgb'
    assert reservation['retry_parent_receipt_hash'] == digest(failure)
    assert read_json(ledger)['attempts'][:-1] == before['attempts']
    assert budget.totals(read_json(ledger)) == (15, 660)
    malformed = dict(reservation, scope=rgb_budget.SCOPE)
    malformed['reservation_hash'] = digest({k: v for k, v in malformed.items() if k != 'reservation_hash'})
    with pytest.raises(ValueError, match='profile'):
        rgb_budget.validate_reservation(malformed, manifest)
    for parent in ['rgb', 'retry']:
        with pytest.raises(ValueError, match='one authorized'):
            rgb_budget.reserve_local(ledger, 'third', manifest, retry_of=parent)
    rgb_budget.settle_local(ledger, dict(failure, attempt_id='retry',
                                       reservation_hash=reservation['reservation_hash'], actual_seconds=9))
    final = read_json(ledger)
    assert budget.totals(final) == (24, 0) and final['attempts'][:-1] == before['attempts']
    assert final['cash_paid_usd'] == 0 and final['final_reserve_seconds'] == 43200
    with pytest.raises(ValueError, match='one authorized'):
        rgb_budget.reserve_local(ledger, 'third', manifest, retry_of='rgb')


def test_retry_rejects_completed_original_and_preserves_final_reserve(rgb_fixture):
    _, manifest, ledger, reservation, _ = rgb_fixture
    receipt = {'attempt_id': 'rgb', 'reservation_hash': reservation['reservation_hash'],
               'producer_hash': reservation['producer_hash'], 'terminal_state': 'FAILED', 'actual_seconds': 12}
    rgb_budget.settle_local(ledger, receipt)
    before = read_json(ledger)
    with budget.ledger(ledger) as data:
        data['attempts'][-1]['terminal_state'] = 'COMPLETED'
    with pytest.raises(ValueError, match='settled failed original'):
        rgb_budget.reserve_local(ledger, 'retry', manifest, retry_of='rgb')
    with budget.ledger(ledger) as data:
        data['attempts'][-1] = before['attempts'][-1]
        data['cpu_limit_seconds'] = data['final_reserve_seconds']+674
    with pytest.raises(ValueError, match='preserve final reserve'):
        rgb_budget.reserve_local(ledger, 'retry', manifest, retry_of='rgb')
    assert len(read_json(ledger)['attempts']) == 2


def test_pilot_cache_and_replay_with_fixed_encoder_fixture(rgb_fixture, tmp_path, monkeypatch):
    from lsc5 import rgb_pilot
    from lsc5.rgb_encoder import COMMIT, WEIGHT_SHA256, SOURCE_INVENTORY_HASH
    train, manifest, ledger, reservation, _ = rgb_fixture
    identity = {'commit': COMMIT, 'weight_sha256': WEIGHT_SHA256,
                'source_inventory_hash': SOURCE_INVENTORY_HASH, 'license': 'Apache-2.0',
                'architecture': 'dinov2_vits14_no_registers', 'eval': True, 'frozen': True,
                'weight_url': 'https://dl.fbaipublicfiles.com/dinov2/dinov2_vits14/dinov2_vits14_pretrain.pth'}
    class FixedEncoder:
        def __init__(self, _):
            self.identity = identity
            self.parameter_count = 1
            self.versions = {'torch': '2.4.1+cu121', 'torchvision': '0.19.1+cu121', 'pillow': '11.3.0'}
        def extract(self, pixels, batch_size=4):
            x = np.arange(384, dtype=np.float32)[None, :]+pixels[:, 0, 0, 0].astype(np.float32)[:, None]
            return x, [{'forward_seconds': 0., 'h2d_and_normalization_seconds': 0., 'd2h_seconds': 0.}
                       for _ in range(0, len(pixels), batch_size)]
        def memory_stats(self):
            return {'torch_peak_allocated_bytes': 0, 'torch_peak_reserved_bytes': 0}
    def fixed_decode(_, sample):
        pixels = np.full((16, 224, 224, 3), sum(map(ord, sample['id'])) % 256, dtype=np.uint8)
        return pixels, {'id': sample['id'], 'video_sha256': sample['video_sha256'],
                        'video_frames': 3, 'indices': indices(3).tolist(),
                        'pixels_sha256': hashlib.sha256(pixels.tobytes()).hexdigest()}
    monkeypatch.setattr(rgb_pilot, 'Encoder', FixedEncoder)
    monkeypatch.setattr(rgb_pilot, 'decode', fixed_decode)
    monkeypatch.setattr(rgb_pilot, 'require_supervisor', lambda: None)
    run = tmp_path/'pilot'
    metrics = rgb_pilot.run_pilot(train, manifest, None, reservation, run)
    assert metrics['measured_batches'] == 120 and metrics['warmup_batches'] == 5
    assert not metrics['whole_chain_admitted']
    meta = rgb_pilot.load_cache(run/'cache', manifest)
    assert len(meta['ids']) == 30 and meta['learned_dependencies'] == []
    with pytest.raises(ValueError, match='coverage'):
        rgb_pilot.load_cache(run/'cache', manifest, [s['id'] for s in manifest['samples']])
    result = rgb_pilot.replay(train, manifest, None, run, tmp_path/'replay.json')
    assert result['relative_l2_batch1_batch4_vs_reference'] == [0., 0.]
    exact = FixedEncoder.extract
    def opposite_errors(self, pixels, batch_size=4):
        x, timing = exact(self, pixels, batch_size)
        return x*(1+(.000075 if batch_size == 1 else -.000075)), timing
    monkeypatch.setattr(FixedEncoder, 'extract', opposite_errors)
    with pytest.raises(ValueError, match='relative L2'):
        rgb_pilot.replay(train, manifest, None, run, tmp_path/'must_not_publish.json')
    assert not (tmp_path/'must_not_publish.json').exists()
    monkeypatch.setattr(FixedEncoder, 'extract', exact)
    original = read_json(run/'cache/metadata.json')
    atomic_json(run/'cache/metadata.json', dict(original, encoder=dict(identity, weight_sha256='0'*64)))
    with pytest.raises(ValueError, match='encoder'):
        rgb_pilot.load_cache(run/'cache', manifest)
    atomic_json(run/'cache/metadata.json', original)
    (run/'cache/0000.npz').write_bytes(b'corrupt')
    with pytest.raises(ValueError, match='provenance'):
        rgb_pilot.load_cache(run/'cache', manifest)


def test_supervisor_stops_own_process_on_ram_limit(rgb_fixture, tmp_path, monkeypatch):
    from lsc5 import rgb_supervisor as supervisor
    train, manifest, ledger, reservation, _ = rgb_fixture
    manifest_path, reservation_path = tmp_path/'manifest.json', tmp_path/'reservation.json'
    atomic_json(manifest_path, manifest); atomic_json(reservation_path, reservation)
    monkeypatch.setattr(supervisor, 'admission', lambda _: {})
    guard = tmp_path/'guard'; guard.mkdir()
    monkeypatch.setattr(supervisor, 'guard_directory', lambda: guard)
    readings = iter([3*1024**3, 0])
    monkeypatch.setattr(supervisor, 'available_ram', lambda: next(readings, 0))
    monkeypatch.setattr(supervisor, 'gpu_memory', lambda: {'used_bytes': 0})
    popen = subprocess.Popen
    children = []
    def sleeping_worker(*args, **kwargs):
        p = popen([sys.executable, '-c', 'import time; time.sleep(60)'], **kwargs)
        children.append(p)
        return p
    monkeypatch.setattr(supervisor.subprocess, 'Popen', sleeping_worker)
    result = supervisor.supervise(train, manifest_path, tmp_path, reservation_path, tmp_path/'supervised')
    assert result['terminal_state'] == 'RESOURCE_LIMIT' and result['actual_seconds'] < 15
    assert all(p.poll() is not None for p in children)
    rgb_budget.settle_local(ledger, result)
    assert budget.totals(read_json(ledger))[1] == 0
    # Settled receipts cannot launch a second execution even if their output was removed.
    import shutil
    shutil.rmtree(tmp_path/'supervised')
    with pytest.raises(FileExistsError):
        supervisor.supervise(train, manifest_path, tmp_path, reservation_path, tmp_path/'supervised')
    with pytest.raises(ValueError, match='atomically bound'):
        supervisor.supervise(train, manifest_path, tmp_path, reservation_path, tmp_path/'another')


def test_worker_requires_supervisor(monkeypatch):
    from lsc5.rgb_pilot import require_supervisor
    monkeypatch.delenv('LSC5_RGB_SUPERVISOR_PID', raising=False)
    with pytest.raises(ValueError, match='supervisor'):
        require_supervisor()


@pytest.mark.parametrize('mode', ['sigterm', 'slow_gpu'])
def test_supervisor_interruptions_and_slow_gpu_keep_watchdog_live(rgb_fixture, tmp_path, monkeypatch, mode):
    import signal
    from lsc5 import rgb_supervisor as supervisor
    train, manifest, ledger, reservation, _ = rgb_fixture
    manifest_path, reservation_path = tmp_path/'manifest.json', tmp_path/'reservation.json'
    atomic_json(manifest_path, manifest); atomic_json(reservation_path, reservation)
    guard = tmp_path/'guard'; guard.mkdir()
    monkeypatch.setattr(supervisor, 'guard_directory', lambda: guard)
    monkeypatch.setattr(supervisor, 'admission', lambda _: {})
    monkeypatch.setattr(supervisor, 'group_rss', lambda _: 0)
    monkeypatch.setattr(supervisor, 'gpu_memory', lambda: {'used_bytes': 0})
    original_popen = subprocess.Popen
    unrelated = original_popen([sys.executable, '-c', 'import time; time.sleep(60)'], start_new_session=True)
    workers, queries, reads = [], [], []
    grandchild_file = tmp_path/'grandchild.pid'
    def worker(*args, **kwargs):
        code = ('import subprocess,sys,time,os,signal; from pathlib import Path; '
                'g=subprocess.Popen([sys.executable,"-c","import time; time.sleep(60)"]); '
                f'Path({str(grandchild_file)!r}).write_text(str(g.pid)); ')
        if mode == 'sigterm':
            code += 'time.sleep(.3); os.kill(os.getppid(),signal.SIGTERM); '
        code += 'time.sleep(60)'
        p = original_popen([sys.executable, '-c', code], **kwargs)
        workers.append(p)
        return p
    def slow_query():
        p = original_popen([sys.executable, '-c', 'import time; time.sleep(60)'],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        queries.append(p)
        return p
    def memory():
        reads.append(1)
        return 0 if queries else 3*1024**3
    monkeypatch.setattr(supervisor.subprocess, 'Popen', worker)
    monkeypatch.setattr(supervisor, 'start_gpu_query', slow_query)
    monkeypatch.setattr(supervisor, 'available_ram', memory)
    before = signal.getsignal(signal.SIGTERM)
    try:
        result = supervisor.supervise(train, manifest_path, tmp_path, reservation_path, tmp_path/'supervised')
        assert result['terminal_state'] == ('FAILED' if mode == 'sigterm' else 'RESOURCE_LIMIT')
        assert result['actual_seconds'] < 8
        assert all(p.poll() is not None for p in workers+queries)
        pid = int(grandchild_file.read_text())
        stat = Path(f'/proc/{pid}/stat')
        assert not stat.exists() or stat.read_text().rsplit(')', 1)[1].split()[0] == 'Z'
        assert unrelated.poll() is None and signal.getsignal(signal.SIGTERM) == before
        if mode == 'slow_gpu':
            assert len(reads) >= 10 and queries
        rgb_budget.settle_local(ledger, result)
    finally:
        unrelated.terminate()
        unrelated.wait(timeout=5)


def test_gpu_lock_is_canonical_across_output_parents(rgb_fixture, tmp_path, monkeypatch):
    import fcntl
    from lsc5 import rgb_supervisor as supervisor
    train, manifest, _, reservation, _ = rgb_fixture
    manifest_path, reservation_path = tmp_path/'manifest.json', tmp_path/'reservation.json'
    atomic_json(manifest_path, manifest); atomic_json(reservation_path, reservation)
    guard = tmp_path/'guard'; guard.mkdir()
    monkeypatch.setattr(supervisor, 'guard_directory', lambda: guard)
    with (guard/'local-gpu.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(BlockingIOError):
            supervisor.supervise(train, manifest_path, tmp_path, reservation_path, tmp_path/'supervised')
    assert not (tmp_path/'supervised').exists()


def test_cleanup_timeout_keeps_original_error_and_receipt(rgb_fixture, tmp_path, monkeypatch):
    from lsc5 import rgb_supervisor as supervisor
    train, manifest, _, reservation, _ = rgb_fixture
    mp, rp = tmp_path/'manifest.json', tmp_path/'reservation.json'
    atomic_json(mp, manifest); atomic_json(rp, reservation)
    guard = tmp_path/'guard'; guard.mkdir()
    monkeypatch.setattr(supervisor, 'guard_directory', lambda: guard)
    monkeypatch.setattr(supervisor, 'admission', lambda _: {})
    monkeypatch.setattr(supervisor, 'available_ram', lambda: 0)
    monkeypatch.setattr(supervisor, 'group_rss', lambda _: 0)
    monkeypatch.setattr(supervisor, 'gpu_memory', lambda: {})
    class Child:
        pid = 99999999
        def poll(self): return None
        def wait(self, timeout): raise subprocess.TimeoutExpired('fixture', timeout)
    monkeypatch.setattr(supervisor.subprocess, 'Popen', lambda *a, **k: Child())
    monkeypatch.setattr(supervisor, 'stop_group', lambda _: (_ for _ in ()).throw(RuntimeError('cleanup fixture')))
    result = supervisor.supervise(train, mp, tmp_path, rp, tmp_path/'supervised')
    saved = read_json(tmp_path/'supervised/execution.json')
    assert saved == result and result['error_type'] == 'MemoryError'
    assert result['terminal_state'] == 'RESOURCE_LIMIT'
    assert not result['worker_termination_confirmed']
    assert {x['operation'] for x in result['cleanup_errors']} == {'stop_worker_group', 'wait_worker'}
