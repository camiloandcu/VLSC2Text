import json,sys,time,resource,numpy as np
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parents[2]/'src'))
from lsc5 import wave
R=str(__import__('pathlib').Path(__file__).resolve().parents[2])+'/'; B=R+'artifacts/wave/bundle_x4x6_v1'
man={s['id']:s for s in json.load(open(R+'artifacts/cpu-pilot/train_manifest.json'))['samples']}
ref=np.load(B+'/train_reference.npz'); ids=ref['ids'].tolist(); paths=[R+'data/train/'+man[i]['landmarks_path'] for i in ids]
t=time.perf_counter(); p=wave.predict_bundle(B,paths); sec=time.perf_counter()-t
perm=np.random.default_rng(0).permutation(len(ids))[:200]; pp=wave.predict_bundle(B,[paths[k] for k in perm])
r={'max_diff_vs_inprocess':float(np.abs(p-ref['probabilities']).max()),'max_diff_reordered':float(np.abs(pp-p[perm]).max()),
   'seconds_1125':sec,'seconds_per_clip':sec/1125,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
   'train_fit_accuracy':float((p.argmax(1)==np.array([int(man[i]['label'][-2:])-1 for i in ids])).mean())}
print(json.dumps(r,indent=1)); json.dump(r,open(B+'_checks.json','w'),indent=1)
