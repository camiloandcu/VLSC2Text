"""Nested LOSO estimate of the *selection procedure* over all MLP variants tried in iteration 2.
Outer: hold out one signer. Inner: choose the variant using only the other two signers (train on one, validate on
the other, both directions, seed 17). Outer score: that variant's saved seed-averaged OOF on the held-out signer."""
import json,sys,time,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'src'))
from lsc5 import wave, wave_iter as wi
OUT=ROOT/'artifacts/iter2'
man=json.load(open(ROOT/'artifacts/cpu-pilot/train_manifest.json'))
ids,xs,y,S=wave.load_train(ROOT/'data/train',man); perm=np.load(ROOT/'artifacts/wave/face_perm.npy')
canon=[wave.canonical(x,perm) for x in xs]; st=wave.masked_stats
def vs(c,shape=False,vel=False,active=False,rest=False,rel=False):
    if active: c=c[wave.active_segment(c)]
    s=wi.sequence(c,relations=rel,handshape=shape); parts=[s]
    if vel: parts.append(wi.velocity_features(s))
    if rest: parts.append(wi.rest_relative(s))
    return st(np.concatenate(parts,1))
R={'mlp_base':(dict(),0),'mlp_rel':(dict(rel=True),0),'mlp_shape':(dict(shape=True),0),'mlp_relshape':(dict(rel=True,shape=True),0),
   'mlp_active':(dict(active=True),0),'mlp_viewaug4':(dict(),4),'mlp_shape_active_viewaug4':(dict(shape=True,active=True),4),
   'mlp_shape_viewaug4':(dict(shape=True),4),'mlp_vel':(dict(vel=True),0),'mlp_rest':(dict(rest=True),0),
   'mlp_velshape':(dict(vel=True,shape=True),0),'mlp_vel_viewaug4':(dict(vel=True),4),'mlp_velshape_viewaug4':(dict(vel=True,shape=True),4),
   'mlp_velshape_active_viewaug4':(dict(vel=True,shape=True,active=True),4)}
# skipped from the registry: mlp_viewtimeaug4 and mlp_present (different augmentation / stats path); both were below the winner
t0=time.time(); inner={}; oof={k:np.load(OUT/f'{k}.npz')['probabilities'] for k in R}
for name,(kw,n_aug) in R.items():
    rng=np.random.default_rng(123)
    feats=[vs(c,**kw) for c in canon]
    extra=[[vs(wi.view_augment(c,rng),**kw) for _ in range(n_aug)] for c in canon] if n_aug else None
    sc={}
    for outer in ('M02','M03','M04'):
        a,b=[h for h in ('M02','M03','M04') if h!=outer]; tot=0
        for tr,va in ((a,b),(b,a)):
            fit=np.where(S==tr)[0]; val=np.where(S==va)[0]
            fx=[feats[i] for i in fit]; fy=y[fit]; fs=S[fit]
            if n_aug:
                for k in range(n_aug): fx=fx+[extra[i][k] for i in fit]
                fy=np.tile(fy,n_aug+1); fs=np.tile(fs,n_aug+1)
            tot+=int((wave.fit_mlp(fx,fy,fs,17)([feats[i] for i in val]).argmax(1)==y[val]).sum())
        sc[outer]=tot
    inner[name]=sc; print(name,sc,round(time.time()-t0),flush=True)
res={'inner_scores':inner,'outer':{}}
total=0
for outer in ('M02','M03','M04'):
    best=max(R,key=lambda k:(inner[k][outer],-list(R).index(k)))
    ok=int((oof[best].argmax(1)==y)[S==outer].sum()); total+=ok
    res['outer'][outer]={'selected':best,'correct':ok}
res['nested_total']=total; res['nested_accuracy']=total/1125
res['best_in_hindsight']=max(int((oof[k].argmax(1)==y).sum()) for k in R)
print(json.dumps(res['outer']),total,total/1125); json.dump(res,open(OUT/'nested_selection.json','w'),indent=1)
