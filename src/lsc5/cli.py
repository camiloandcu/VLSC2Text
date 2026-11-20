"""Train-only CPU diagnostic, fixed baseline and OOF commands."""
import argparse
import json
import os
from pathlib import Path

from . import budget
from .data import build_manifest, make_splits
from .features import prepare_stats
from .io import atomic_json, read_json


def main(argv=None):
    os.umask(0o077)
    parser = argparse.ArgumentParser(prog="lsc5")
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit-train")
    audit.add_argument("--data-root", type=Path, required=True)
    audit.add_argument("--out", type=Path, required=True)
    split = commands.add_parser("make-splits")
    split.add_argument("--manifest", type=Path, required=True)
    split.add_argument("--out", type=Path, required=True)
    stats = commands.add_parser("prepare-stats")
    stats.add_argument("--data-root", type=Path, required=True)
    stats.add_argument("--manifest", type=Path, required=True)
    stats.add_argument("--out", type=Path, required=True)
    init = commands.add_parser("budget-init")
    init.add_argument("--budget", type=Path, required=True)
    enable = commands.add_parser("budget-enable-baseline")
    enable.add_argument("--budget", type=Path, required=True)
    for name in ["budget-reserve", "budget-bind", "budget-settle"]:
        item = commands.add_parser(name)
        item.add_argument("--budget", type=Path, required=True)
        item.add_argument("--attempt", required=True)
        if name == "budget-reserve":
            item.add_argument("--kill-wait", type=int, required=True)
            item.add_argument("--scope", choices=[budget.SCOPE, budget.BASELINE_SCOPE], default=budget.SCOPE)
        else:
            item.add_argument("--job-id", required=True)
        if name == "budget-settle":
            item.add_argument("--actual-seconds", type=float, required=True)
            item.add_argument("--state", required=True)
    for profile in ["pilot", "fit-baseline"]:
        fit = commands.add_parser(profile)
        for name in ["manifest", "split", "cache", "budget", "out"]:
            fit.add_argument("--" + name, type=Path, required=True)
        fit.add_argument("--attempt", required=True)
    aggregate = commands.add_parser("aggregate-oof")
    aggregate.add_argument("--manifest", type=Path, required=True)
    aggregate.add_argument("--runs", nargs=3, type=Path, required=True)
    aggregate.add_argument("--out", type=Path, required=True)
    aggregate.add_argument("--rgb-restoration", type=Path)
    restore = commands.add_parser("predict-train")
    for name in ["data-root", "manifest", "run", "out"]:
        restore.add_argument("--" + name, type=Path, required=True)
    for command in ["temporal-enable", "temporal-reserve", "temporal-admit"]:
        item = commands.add_parser(command)
        item.add_argument("--budget", type=Path, required=True)
        if command == "temporal-reserve":
            item.add_argument("--attempt", required=True)
            item.add_argument("--kill-wait", type=int, required=True)
            item.add_argument("--pilot", action="store_true")
        if command == "temporal-admit":
            item.add_argument("--manifest", type=Path, required=True)
            item.add_argument("--run", type=Path, required=True)
            item.add_argument("--restoration-receipt", type=Path, required=True)
    item = commands.add_parser("fit-temporal")
    for name in ["manifest", "split", "cache", "budget", "out"]:
        item.add_argument("--"+name, type=Path, required=True)
    item.add_argument("--attempt", required=True)
    item.add_argument("--pilot", action="store_true")
    item.add_argument("--train-zip", type=Path)
    item = commands.add_parser("compare-oof")
    for name in ["manifest", "candidate", "baseline", "out"]:
        item.add_argument("--"+name, type=Path, required=True)
    item.add_argument("--baseline-report-sha256", required=True)
    for command in ["rgb-budget-reserve", "rgb-budget-claim", "rgb-budget-settle"]:
        item = commands.add_parser(command)
        item.add_argument("--budget", type=Path, required=True)
        if command == "rgb-budget-reserve":
            item.add_argument("--manifest", type=Path, required=True)
            item.add_argument("--retry-of", help="Explicitly authorized single retry of a failed original RGB pilot")
        if command == "rgb-budget-settle":
            item.add_argument("--receipt", type=Path, required=True)
        else:
            item.add_argument("--attempt", required=True)
        if command == "rgb-budget-claim":
            item.add_argument("--run-directory", required=True)
            item.add_argument("--machine-id-sha256", required=True)
    for command in ["rgb-pilot", "rgb-replay", "rgb-supervise"]:
        item = commands.add_parser(command)
        for name in ["data-root", "manifest", "assets", "out"]:
            item.add_argument("--"+name, type=Path, required=True)
        if command in {"rgb-pilot", "rgb-supervise"}:
            item.add_argument("--reservation", type=Path, required=True)
        else:
            item.add_argument("--run", type=Path, required=True)
    for command in ["rgb-loso-enable", "rgb-loso-reserve", "rgb-loso-admit"]:
        item = commands.add_parser(command)
        item.add_argument("--budget", type=Path, required=True)
        item.add_argument("--manifest", type=Path, required=True)
        if command == "rgb-loso-reserve":
            item.add_argument("--attempt", required=True)
            item.add_argument("--profile", choices=["extract", "restore", "pilot", "M02", "M03", "M04"], required=True)
        if command == "rgb-loso-admit":
            item.add_argument("--run", type=Path, required=True)
            item.add_argument("--restoration-receipt", type=Path, required=True)
    for command in ["rgb-full-claim", "rgb-full-settle"]:
        item = commands.add_parser(command)
        item.add_argument("--budget", type=Path, required=True)
        if command == "rgb-full-settle":
            item.add_argument("--receipt", type=Path, required=True)
        else:
            item.add_argument("--attempt", required=True)
            item.add_argument("--run-directory", required=True)
            item.add_argument("--machine-id-sha256", required=True)
    for command in ["rgb-full-supervise", "rgb-full-worker"]:
        item = commands.add_parser(command)
        for name in ["data-root", "manifest", "assets", "reservation", "out"]:
            item.add_argument("--"+name, type=Path, required=True)
        item.add_argument("--runs", type=Path, nargs=3)
    for command in ["fit-rgb-head", "restore-rgb-cache"]:
        item = commands.add_parser(command)
        for name in ["manifest", "cache", "out"]:
            item.add_argument("--"+name, type=Path, required=True)
        if command == "fit-rgb-head":
            item.add_argument("--split", type=Path, required=True)
            item.add_argument("--budget", type=Path, required=True)
            item.add_argument("--attempt", required=True)
            item.add_argument("--pilot", action="store_true")
        else:
            item.add_argument("--run", type=Path, required=True)
    item = commands.add_parser("delivery-loso")
    item.add_argument("--data-root", type=Path, required=True)
    item.add_argument("--manifest", type=Path, required=True)
    item.add_argument("--splits", type=Path, required=True)
    item.add_argument("--seed", type=int, required=True)
    item.add_argument("--out", type=Path, required=True)
    item = commands.add_parser("finalfit-baseline")
    item.add_argument("--data-root", type=Path, required=True)
    item.add_argument("--manifest", type=Path, required=True)
    item.add_argument("--seeds", type=int, nargs="+", required=True)
    item.add_argument("--out", type=Path, required=True)
    item = commands.add_parser("validate-submission")
    item.add_argument("--template", type=Path, required=True)
    item.add_argument("--submission", type=Path, required=True)
    item = commands.add_parser("wave-finalfit")
    item.add_argument("--data-root", type=Path, required=True)
    item.add_argument("--manifest", type=Path, required=True)
    item.add_argument("--out", type=Path, required=True)
    item = commands.add_parser("wave-predict-csv")
    item.add_argument("--bundle", type=Path, required=True)
    item.add_argument("--landmarks-dir", type=Path, required=True)
    item.add_argument("--template", type=Path, required=True)
    item.add_argument("--out", type=Path, required=True)
    item.add_argument("--authorized-test-run", action="store_true",
                      help="Required to read test payloads; only for a frozen, authorised bundle")
    args = parser.parse_args(argv)
    result = {"command": args.command}
    if args.command in {"wave-finalfit", "wave-predict-csv"}:
        from . import delivery, wave
        if args.command == "wave-finalfit":
            result = wave.finalfit(args.data_root, read_json(args.manifest), args.out)
        else:
            ids = [l.split(",")[0] for l in args.template.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
            paths = [args.landmarks_dir / f"{i}.npy" for i in ids]
            missing = [str(p) for p in paths if not p.is_file()]
            if missing:
                raise ValueError(f"{len(missing)} template IDs without landmarks file")
            probs = wave.predict_bundle(args.bundle, paths, allow_test=args.authorized_test_run)
            result = delivery.write_submission(args.template, ids, probs, args.out)
        print(json.dumps(result, indent=2, allow_nan=False, default=str))
        return
    if args.command in {"delivery-loso", "finalfit-baseline", "validate-submission"}:
        from . import delivery
        if args.command == "validate-submission":
            result = delivery.validate_submission(args.template, args.submission)
        else:
            manifest = read_json(args.manifest)
            data_root = args.data_root / "train" if args.data_root.name != "train" else args.data_root
            if args.command == "delivery-loso":
                result = delivery.loso(data_root, manifest, args.splits, delivery.check_seed(args.seed), args.out)
            else:
                result = delivery.finalfit(data_root, manifest, args.seeds, args.out)
        print(json.dumps(result, indent=2, allow_nan=False))
        return
    if args.command == "audit-train":
        manifest = build_manifest(args.data_root / "train", expected_count=1125)
        if args.out.exists():
            raise FileExistsError(args.out)
        atomic_json(args.out, manifest)
        result.update(clips=len(manifest["samples"]), manifest_hash=manifest["manifest_hash"],
                      schema_status=manifest["schema_status"])
    elif args.command == "make-splits":
        args.out.mkdir(parents=True, exist_ok=False, mode=0o700)
        splits = make_splits(read_json(args.manifest))
        for split in splits:
            atomic_json(args.out / (split["outer_signer"] + ".json"), split)
        result["folds"] = len(splits)
    elif args.command == "prepare-stats":
        prepare_stats(args.data_root / "train", read_json(args.manifest), args.out)
        result["cache_complete"] = True
    elif args.command == "budget-init":
        budget.initialize(args.budget)
    elif args.command == "budget-reserve":
        budget.reserve(args.budget, args.attempt, kill_wait=args.kill_wait, scope=args.scope)
    elif args.command == "budget-enable-baseline":
        budget.enable_baseline(args.budget)
    elif args.command == "budget-bind":
        budget.bind_job(args.budget, args.attempt, args.job_id)
    elif args.command == "budget-settle":
        budget.settle(args.budget, args.attempt, args.actual_seconds, args.job_id, args.state)
    elif args.command in {"pilot", "fit-baseline"}:
        from .training import run_pilot, run_baseline
        fit = run_pilot if args.command == "pilot" else run_baseline
        result = fit(read_json(args.manifest), read_json(args.split), args.cache, args.budget,
                           args.attempt, args.out)
    elif args.command == "aggregate-oof":
        from .evaluation import aggregate_oof
        result = aggregate_oof(read_json(args.manifest), args.runs, args.out, args.rgb_restoration)
    elif args.command == "predict-train":
        if read_json(args.run / "run.json").get("recipe") == "opaque_tcn_v1":
            from .temporal_restore import predict_temporal as predict_train
        else:
            from .restore import predict_train
        result = predict_train(args.data_root / "train", read_json(args.manifest), args.run, args.out)
    elif args.command == "temporal-enable":
        budget.enable_temporal(args.budget)
    elif args.command == "temporal-reserve":
        budget.reserve_temporal(args.budget, args.attempt, args.kill_wait, args.pilot)
    elif args.command == "temporal-admit":
        result = budget.admit_temporal(args.budget, read_json(args.manifest), args.run, args.restoration_receipt)
    elif args.command == "fit-temporal":
        from .temporal_training import fit_temporal
        result = fit_temporal(read_json(args.manifest), read_json(args.split), args.cache, args.budget,
                              args.attempt, args.out, args.pilot, args.train_zip)
    elif args.command == "compare-oof":
        from .evaluation import compare_oof
        result = compare_oof(read_json(args.manifest), args.candidate, args.baseline, args.out, args.baseline_report_sha256)
    elif args.command.startswith("rgb-budget-"):
        from . import rgb_budget
        if args.command == "rgb-budget-reserve":
            result = rgb_budget.reserve_local(args.budget, args.attempt, read_json(args.manifest), args.retry_of)
        elif args.command == "rgb-budget-claim":
            result = rgb_budget.claim_local(args.budget, args.attempt, args.run_directory, args.machine_id_sha256)
        else:
            result = rgb_budget.settle_local(args.budget, read_json(args.receipt))
    elif args.command == "rgb-supervise":
        from .rgb_supervisor import supervise
        result = supervise(args.data_root/"train", args.manifest, args.assets, args.reservation, args.out)
    elif args.command == "rgb-pilot":
        from .rgb_pilot import run_pilot
        result = run_pilot(args.data_root/"train", read_json(args.manifest), args.assets,
                           read_json(args.reservation), args.out)
    elif args.command == "rgb-replay":
        from .rgb_pilot import replay
        result = replay(args.data_root/"train", read_json(args.manifest), args.assets, args.run, args.out)
    elif args.command.startswith("rgb-loso-"):
        from . import rgb_loso_budget as rb
        if args.command == "rgb-loso-enable":
            rb.enable(args.budget, read_json(args.manifest))
        elif args.command == "rgb-loso-reserve":
            result = rb.reserve(args.budget, args.attempt, args.profile, read_json(args.manifest))
        else:
            result = rb.admit(args.budget, read_json(args.manifest), args.run, args.restoration_receipt)
    elif args.command == "rgb-full-claim":
        from .rgb_loso_budget import claim_gpu
        result = claim_gpu(args.budget, args.attempt, args.run_directory, args.machine_id_sha256)
    elif args.command == "rgb-full-settle":
        from .rgb_loso_budget import settle_gpu
        result = settle_gpu(args.budget, read_json(args.receipt))
    elif args.command == "rgb-full-supervise":
        from .rgb_supervisor import supervise
        result = supervise(args.data_root/"train", args.manifest, args.assets, args.reservation, args.out, args.runs)
    elif args.command == "rgb-full-worker":
        from .rgb_full import run_full
        result = run_full(args.data_root/"train", read_json(args.manifest), args.assets,
                          read_json(args.reservation), args.out, args.runs)
    elif args.command == "fit-rgb-head":
        from .rgb_head_training import fit
        result = fit(read_json(args.manifest), read_json(args.split), args.cache, args.budget, args.attempt, args.out, args.pilot)
    elif args.command == "restore-rgb-cache":
        from .rgb_head_restore import restore_cache
        result = restore_cache(read_json(args.manifest), args.run, args.cache, args.out)
    print(json.dumps({k:v for k,v in result.items() if k != "gpu_memory_samples"}, indent=2, allow_nan=False))
    if args.command in {"rgb-supervise", "rgb-full-supervise"} and result["terminal_state"] != "COMPLETED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
