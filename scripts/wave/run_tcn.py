import json,sys,time,numpy as np
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parents[2]/'src'))
from lsc5 import wave
R=str(__import__('pathlib').Path(__file__).resolve().parents[2])+'/'; OUT=R+'artifacts/wave/'
man=json.load(open(R+'artifacts/cpu-pilot/train_manifest.json'))
ids,xs,y,S=wave.load_train(R+'data/train',man); perm=np.load(OUT+'face_perm.npy')
ref=np.load(OUT+'X4_body_stats_canonical.npz')['probabilities']
seqs=[]
for x in xs:
    c=wave.canonical(x,perm); seqs.append(wave.body_sequence(c[wave.active_segment(c)]))
t=time.time()
per=wave.loso(seqs,y,S,lambda fx,fy,fs,seed: wave.fit_tcn(fx,fy,fs,seed,augment=True))
r,avg=wave.summarise(per,y,S,ref); r['seconds']=time.time()-t; r['reference']='X4_body_stats_canonical'
np.savez_compressed(OUT+'X6_tcn_canonical_active_aug.npz',ids=np.array(ids),probabilities=avg,**{f's{k}':v for k,v in per.items()})
print(json.dumps(r)); json.dump(r,open(OUT+'results_tcn.json','w'),indent=1)
