"""Iteration 2: MLP variants on canonical body-normalised landmarks (train-only LOSO, seeds 17/29/43)."""
import json,sys,time,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'src'))
from lsc5 import wave, wave_iter as wi
OUT=ROOT/'artifacts/iter2'
man=json.load(open(ROOT/'artifacts/cpu-pilot/train_manifest.json'))
ids,xs,y,S=wave.load_train(ROOT/'data/train',man); perm=np.load(ROOT/'artifacts/wave/face_perm.npy')
canon=[wave.canonical(x,perm) for x in xs]
ref=np.load(ROOT/'artifacts/wave/X4_body_stats_canonical.npz')['probabilities']
log=json.load(open(OUT/'log.json')) if (OUT/'log.json').exists() else {}
def run(name,feat_fn,n_aug=0,aug_fn=None):
    t=time.time(); feats=[feat_fn(c) for c in canon]
    rng=np.random.default_rng(123)
    extra=[[feat_fn(aug_fn(c,rng)) for _ in range(n_aug)] for c in canon] if n_aug else None
    per={}
    for seed in wave.SEEDS:
        probs=np.zeros((len(y),5),np.float32)
        for held in ('M02','M03','M04'):
            fit=np.where(S!=held)[0]; val=np.where(S==held)[0]
            fx=[feats[i] for i in fit]; fy=y[fit]; fs=S[fit]
            if n_aug:
                for k in range(n_aug): fx=fx+[extra[i][k] for i in fit]
                fy=np.tile(y[fit],n_aug+1); fs=np.tile(S[fit],n_aug+1)
            probs[val]=wave.fit_mlp(fx,fy,fs,seed)([feats[i] for i in val])
        per[seed]=probs
    r,avg=wave.summarise(per,y,S,ref); r['seconds']=round(time.time()-t,1); log[name]=r
    np.savez_compressed(OUT/f'{name}.npz',ids=np.array(ids),probabilities=avg)
    json.dump(log,open(OUT/'log.json','w'),indent=1)
    print(f"{name:34s} {r['avg_correct']} {r['per_signer']} vsX4 {r['vs_reference']['per_signer_delta']} seeds {r['seeds']}",flush=True)
st=wave.masked_stats
variants=sys.argv[1:]
for v in variants:
    if v=='base': run('mlp_base',lambda c: st(wave.body_sequence(c)))
    if v=='rel': run('mlp_rel',lambda c: st(wi.sequence(c,relations=True)))
    if v=='shape': run('mlp_shape',lambda c: st(wi.sequence(c,handshape=True)))
    if v=='relshape': run('mlp_relshape',lambda c: st(wi.sequence(c,relations=True,handshape=True)))
    if v=='active': run('mlp_active',lambda c: st(wave.body_sequence(c[wave.active_segment(c)])))
    if v=='viewaug': run('mlp_viewaug4',lambda c: st(wave.body_sequence(c)),4,wi.view_augment)
    if v=='viewtimeaug': run('mlp_viewtimeaug4',lambda c: st(wave.body_sequence(c)),4,lambda c,r: wi.time_augment(wi.view_augment(c,r),r))
    if v=='combo': run('mlp_shape_active_viewaug4',lambda c: st(wi.sequence(c[wave.active_segment(c)],handshape=True)),4,wi.view_augment)
    if v=='shape_viewaug': run('mlp_shape_viewaug4',lambda c: st(wi.sequence(c,handshape=True)),4,wi.view_augment)
    if v=='vel': run('mlp_vel',lambda c: (lambda s: st(np.concatenate([s,wi.velocity_features(s)],1)))(wave.body_sequence(c)))
    if v=='rest': run('mlp_rest',lambda c: (lambda s: st(np.concatenate([s,wi.rest_relative(s)],1)))(wave.body_sequence(c)))
    if v=='present': run('mlp_present',lambda c: (lambda s: np.concatenate([st(s),wi.present_stats(s)]))(wave.body_sequence(c)))
    def velshape(c):
        s=wi.sequence(c,handshape=True); return st(np.concatenate([s,wi.velocity_features(s)],1))
    if v=='velshape': run('mlp_velshape',velshape)
    if v=='velshape_aug': run('mlp_velshape_viewaug4',velshape,4,wi.view_augment)
    if v=='velshape_active_aug': run('mlp_velshape_active_viewaug4',lambda c: velshape(c[wave.active_segment(c)]),4,wi.view_augment)
    if v=='vel_aug': run('mlp_vel_viewaug4',lambda c: (lambda s: st(np.concatenate([s,wi.velocity_features(s)],1)))(wave.body_sequence(c)),4,wi.view_augment)
