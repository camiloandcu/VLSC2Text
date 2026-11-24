"""Iteration 7 (pre-registered 24 Nov 2026, docs/04 §24): E7a rule-fixed ensemble of the gate=1.3 variants from
saved OOF, and E7b fixed view TTA on v4_contact_bimanual with outer LOSO (seeds 17/29/43)."""
import json,sys,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'src'))
from lsc5 import wave, wave_iter as wi
OUT=ROOT/'artifacts/iter3'; H=('M02','M03','M04'); REF={'M02':373,'M03':368,'M04':367}
man=json.load(open(ROOT/'artifacts/cpu-pilot/train_manifest.json'))
ids,xs,y,S=wave.load_train(ROOT/'data/train',man)
def score(P): ok=P.argmax(1)==y; return int(ok.sum()),{h:int(ok[S==h].sum()) for h in H}
log=json.load(open(OUT/'log.json')); members=[k for k,v in log.items() if v['cfg'].get('gate')==1.3]
assert len(members)==10, members
E=np.mean([np.load(OUT/f'{k}.npz')['probabilities'] for k in members],0); ea,eps=score(E)
res={'E7a':{'members':members,'correct':ea,'per_signer':eps,'adopt':bool(ea>=1106 and all(eps[h]>=REF[h]-2 for h in H))}}
np.savez_compressed(OUT/'v7_ensemble_gate13.npz',ids=np.array(ids),probabilities=E); print('E7a',res['E7a'],flush=True)
perm=np.load(ROOT/'artifacts/wave/face_perm.npy'); canon=[wave.canonical(x,perm) for x in xs]
cfg=wi.CANDIDATE_V4; n=cfg['n_aug']; rng=np.random.default_rng(123)
feats=[wi.features(c,cfg) for c in canon]
extra=[[wi.features(c,cfg,rng,augment=True) for _ in range(n)] for c in canon]
views=[[wi.features(c,cfg,view=v) for c in canon] for v in wi.TTA_VIEWS]
assert all(np.array_equal(a,b) for a,b in zip(views[0],feats))
per_tta,per_id={},{}
for seed in wave.SEEDS:
    Pt=np.zeros((len(y),5),np.float32); Pi=np.zeros((len(y),5),np.float32)
    for held in H:
        f=np.where(S!=held)[0]; v=np.where(S==held)[0]
        fx=[feats[i] for i in f]+[extra[i][k] for k in range(n) for i in f]
        p=wi.fit_mlp_cfg(fx,np.tile(y[f],n+1),np.tile(S[f],n+1),seed)
        Pi[v]=p([feats[i] for i in v]); Pt[v]=np.mean([p([vw[i] for i in v]) for vw in views],0)
    per_tta[seed],per_id[seed]=Pt,Pi
T=np.mean(list(per_tta.values()),0); I=np.mean(list(per_id.values()),0)
ref=np.load(OUT/'v4_contact_bimanual.npz')['probabilities']
ta,tps=score(T)
res['E7b']={'views':wi.TTA_VIEWS,'correct':ta,'per_signer':tps,'seeds':{int(s):score(p)[0] for s,p in per_tta.items()},
            'identity_reproduces_iter4_max_diff':float(np.abs(I-ref).max()),'identity_correct':score(I)[0],
            'adopt':bool(ta>=1108 and all(tps[h]>=REF[h] for h in H))}
np.savez_compressed(OUT/'v7_tta.npz',ids=np.array(ids),probabilities=T); print('E7b',res['E7b'],flush=True)
json.dump(res,open(OUT/'iter7.json','w'),indent=1)
