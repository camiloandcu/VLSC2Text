"""Iteration 2: TCN on velocity+handshape features of the active segment, with one view-augmented copy."""
import json,sys,time,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'src'))
from lsc5 import wave, wave_iter as wi
OUT=ROOT/'artifacts/iter2'
man=json.load(open(ROOT/'artifacts/cpu-pilot/train_manifest.json'))
ids,xs,y,S=wave.load_train(ROOT/'data/train',man); perm=np.load(ROOT/'artifacts/wave/face_perm.npy')
canon=[wave.canonical(x,perm) for x in xs]
def feat(c):
    c=c[wave.active_segment(c)]; s=wi.sequence(c,handshape=True); return np.concatenate([s,wi.velocity_features(s)],1)
rng=np.random.default_rng(123)
seqs=[feat(c) for c in canon]; aug=[feat(wi.view_augment(c,rng)) for c in canon]
ref=np.load(OUT/'mlp_velshape_active_viewaug4.npz')['probabilities']
t=time.time(); per={}
for seed in wave.SEEDS:
    probs=np.zeros((len(y),5),np.float32)
    for held in ('M02','M03','M04'):
        fit=np.where(S!=held)[0]; val=np.where(S==held)[0]
        p=wave.fit_tcn([seqs[i] for i in fit]+[aug[i] for i in fit],np.tile(y[fit],2),np.tile(S[fit],2),seed,augment=False)
        probs[val]=p([seqs[i] for i in val])
    per[seed]=probs; print('seed',seed,int((probs.argmax(1)==y).sum()),flush=True)
r,avg=wave.summarise(per,y,S,ref); r['seconds']=time.time()-t
np.savez_compressed(OUT/'tcn_velshape_active_viewaug1.npz',ids=np.array(ids),probabilities=avg)
e=(avg+ref)/2; ok=e.argmax(1)==y; r['ensemble_with_mlp']={'correct':int(ok.sum()),'per_signer':{h:int(ok[S==h].sum()) for h in ('M02','M03','M04')}}
print(json.dumps(r)); json.dump(r,open(OUT/'tcn_velshape_active_viewaug1.json','w'),indent=1)
