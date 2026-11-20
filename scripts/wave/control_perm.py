import json,sys,numpy as np
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parents[2]/'src'))
from lsc5 import wave
R=str(__import__('pathlib').Path(__file__).resolve().parents[2])+'/'
man=json.load(open(R+'artifacts/cpu-pilot/train_manifest.json'))
ids,xs,y,S=wave.load_train(R+'data/train',man); perm=np.load(R+'artifacts/wave/face_perm.npy')
bc=[wave.masked_stats(wave.body_sequence(wave.canonical(x,perm))) for x in xs]
rng=np.random.default_rng(0); out={}
for held in ('M02','M03','M04'):
    fit=np.where(S!=held)[0]; val=np.where(S==held)[0]
    yp=y[fit].copy()
    for s in np.unique(S[fit]):  # permute labels within each fit signer, keeping strata balanced
        k=np.where(S[fit]==s)[0]; yp[k]=yp[rng.permutation(k)]
    p=wave.fit_mlp([bc[i] for i in fit],yp,S[fit],17)
    out[held]=int((p([bc[i] for i in val]).argmax(1)==y[val]).sum())
print('permuted-label control (correct of 375 each):',out,'total',sum(out.values()))
json.dump(out,open(R+'artifacts/wave/control_permuted_labels.json','w'))
