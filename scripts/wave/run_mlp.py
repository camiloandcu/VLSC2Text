import json,sys,time,numpy as np
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parents[2]/'src'))
from lsc5 import wave
R=str(__import__('pathlib').Path(__file__).resolve().parents[2])+'/'; OUT=R+'artifacts/wave/'
man=json.load(open(R+'artifacts/cpu-pilot/train_manifest.json'))
ids,xs,y,S=wave.load_train(R+'data/train',man)
ref=np.load(R+'artifacts/e01-delivery/oof_avg_17_29_43.npz'); assert ref['ids'].tolist()==ids; refp=ref['probabilities']
faces=[]
for s,x in zip(man['samples'],xs):
    if s['view']=='V01':
        f=x[:,wave.FACE].reshape(len(x),468,3); ok=(f!=0).any((1,2))
        if ok.any(): faces.append(np.median(f[ok],0))
perm=wave.face_permutation(faces); np.save(OUT+'face_perm.npy',perm)
print('face perm involution fraction',float((perm[perm]==np.arange(468)).mean()))
canon=[wave.canonical(x,perm) for x in xs]; mir=[wave.mirror(x,perm) for x in xs]
print('left-dominant clips per signer',{h:int(sum(wave.left_dominant(x) for x,s in zip(xs,S) if s==h)) for h in ('M02','M03','M04')})
res={}
def run(name,feats,**kw):
    t=time.time(); per=wave.loso(feats,y,S,wave.fit_mlp,**kw); r,avg=wave.summarise(per,y,S,refp); r['seconds']=time.time()-t
    res[name]=r; np.savez_compressed(OUT+f'{name}.npz',ids=np.array(ids),probabilities=avg,**{f's{k}':v for k,v in per.items()})
    print(name,json.dumps(r)); json.dump(res,open(OUT+'results_mlp.json','w'),indent=1)
r0o=[wave.r0(x) for x in xs]; r0c=[wave.r0(x) for x in canon]; r0m=[wave.r0(x) for x in mir]
run('X8a_r0_canonical',r0c)
# X8b: mirror augmentation + test-time average of original and mirrored
class TTA:
    pass
def fit_tta(fx,fy,fs,seed):
    p=wave.fit_mlp(fx,fy,fs,seed); return p
per={}
for seed in wave.SEEDS:
    probs=np.zeros((len(y),5),np.float32)
    for held in ('M02','M03','M04'):
        fit=np.where(S!=held)[0]; val=np.where(S==held)[0]
        p=wave.fit_mlp([r0o[i] for i in fit]+[r0m[i] for i in fit],np.concatenate([y[fit],y[fit]]),np.concatenate([S[fit],S[fit]]),seed)
        probs[val]=(p([r0o[i] for i in val])+p([r0m[i] for i in val]))/2
    per[seed]=probs
r,avg=wave.summarise(per,y,S,refp); res['X8b_r0_mirror_aug_tta']=r; np.savez_compressed(OUT+'X8b_r0_mirror_aug_tta.npz',ids=np.array(ids),probabilities=avg)
print('X8b_r0_mirror_aug_tta',json.dumps(r))
bo=[wave.masked_stats(wave.body_sequence(x)) for x in xs]; bc=[wave.masked_stats(wave.body_sequence(x)) for x in canon]
run('X4_body_stats_original',bo)
run('X4_body_stats_canonical',bc)
json.dump(res,open(OUT+'results_mlp.json','w'),indent=1)
