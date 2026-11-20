import json,sys,numpy as np
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parents[2]/'src'))
from lsc5 import wave
R=str(__import__('pathlib').Path(__file__).resolve().parents[2])+'/'
man=json.load(open(R+'artifacts/cpu-pilot/train_manifest.json'))['samples']; by={s['id']:s for s in man}
z=np.load(R+'artifacts/wave/x5/embeddings.npz'); ids=z['ids'].tolist()
meta=json.load(open(R+'artifacts/rgb-loso/extract_execution/full/cache/metadata.json')); pos={i:k for k,i in enumerate(meta['ids'])}
glob=np.stack([np.load(R+f'artifacts/rgb-loso/extract_execution/full/cache/{pos[i]:04d}.npz')['embeddings'] for i in ids])
y=np.array([int(by[i]['label'][-2:])-1 for i in ids]); S=np.array([by[i]['signer'] for i in ids])
def pyr(e): return np.concatenate([e.mean(0),e.std(0),e[:5].mean(0),e[5:11].mean(0),e[11:].mean(0)]).astype(np.float32)
x4=np.load(R+'artifacts/wave/X4_body_stats_canonical.npz'); x6=np.load(R+'artifacts/wave/X6_tcn_canonical_active_aug.npz')
k={i:j for j,i in enumerate(x4['ids'].tolist())}; idx=[k[i] for i in ids]; lm=(x4['probabilities'][idx]+x6['probabilities'][idx])/2
res={'subset':len(ids),'per_signer_clips':{h:int((S==h).sum()) for h in ('M02','M03','M04')}}
probs={}
for name,E in [('global',glob),('roi',z['roi']),('hand',z['hand']),('hand+roi',np.concatenate([z['hand'],z['roi']],2))]:
    feats=[pyr(e) for e in E]
    # balanced sampler needs equal strata: subset is 19 per signer/class
    per=wave.loso(feats,y,S,wave.fit_mlp); r,avg=wave.summarise(per,y,S); probs[name]=avg; res[name]=r
c=lm.argmax(1)==y; res['landmarks_X4X6_same_subset']=int(c.sum())
for name in ('hand','hand+roi'):
    for w in (0.5,0.25):
        e=(1-w)*lm+w*probs[name]; res[f'landmarks+{name}_w{w}']=int((e.argmax(1)==y).sum())
print(json.dumps(res,indent=1)); json.dump(res,open(R+'artifacts/wave/x5/result.json','w'),indent=1)
