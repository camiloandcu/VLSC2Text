"""Permuted-label control on the final iteration-4 pipeline: labels are permuted within each fit signer
(clip level, augmented copies keep their clip's permuted label), outer LOSO with seeds 17/29/43 averaged.
A leakage-free pipeline should stay near chance (20%). Pre-registered threshold: <= 25%."""
import json,sys,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'src'))
from lsc5 import wave, wave_iter as wi
OUT=ROOT/'artifacts/iter3'; cfg=wi.CANDIDATE_V4; n=cfg['n_aug']
man=json.load(open(ROOT/'artifacts/cpu-pilot/train_manifest.json'))
ids,xs,y,S=wave.load_train(ROOT/'data/train',man); perm=np.load(ROOT/'artifacts/wave/face_perm.npy')
canon=[wave.canonical(x,perm) for x in xs]; rng=np.random.default_rng(123)
feats=[wi.features(c,cfg) for c in canon]
extra=[[wi.features(c,cfg,rng,augment=True) for _ in range(n)] for c in canon]
prng=np.random.default_rng(0); yp_all={}
for held in ('M02','M03','M04'):
    fit=np.where(S!=held)[0]; yp=y.copy()
    for s in np.unique(S[fit]):
        k=fit[S[fit]==s]; yp[k]=y[prng.permutation(k)]
    yp_all[held]=yp
probs={}
for seed in wave.SEEDS:
    P=np.zeros((len(y),5),np.float32)
    for held in ('M02','M03','M04'):
        f=np.where(S!=held)[0]; v=np.where(S==held)[0]
        fx=[feats[i] for i in f]+[extra[i][k] for k in range(n) for i in f]
        P[v]=wi.fit_mlp_cfg(fx,np.tile(yp_all[held][f],n+1),np.tile(S[f],n+1),seed)([feats[i] for i in v])
    probs[seed]=P
avg=np.mean(list(probs.values()),0); ok=avg.argmax(1)==y
r={'pipeline':'v4_contact_bimanual','per_signer':{h:int(ok[S==h].sum()) for h in ('M02','M03','M04')},
   'total':int(ok.sum()),'accuracy':float(ok.mean()),'seeds':{int(s):int((p.argmax(1)==y).sum()) for s,p in probs.items()},
   'threshold':0.25,'passes':bool(ok.mean()<=0.25)}
print(json.dumps(r)); json.dump(r,open(OUT/'control_permuted_labels_v4.json','w'),indent=1)
