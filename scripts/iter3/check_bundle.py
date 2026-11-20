"""New-process verification of the iteration-2 bundle on train NPY (no test access)."""
import json,sys,time,resource,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'src'))
from lsc5 import wave_iter
B=ROOT/'artifacts/iter3/bundle_iter3_v1'
man={s['id']:s for s in json.load(open(ROOT/'artifacts/cpu-pilot/train_manifest.json'))['samples']}
ref=np.load(B/'train_reference.npz'); ids=ref['ids'].tolist(); paths=[ROOT/'data/train'/man[i]['landmarks_path'] for i in ids]
t=time.perf_counter(); p=wave_iter.predict_bundle_v3(B,paths); sec=time.perf_counter()-t
perm=np.random.default_rng(0).permutation(len(ids))[:200]; pp=wave_iter.predict_bundle_v3(B,[paths[k] for k in perm])
r={'max_diff_vs_inprocess':float(np.abs(p-ref['probabilities']).max()),'max_diff_reordered':float(np.abs(pp-p[perm]).max()),
   'seconds_per_clip':sec/len(ids),'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
   'train_fit_accuracy':float((p.argmax(1)==np.array([int(man[i]['label'][-2:])-1 for i in ids])).mean())}
print(json.dumps(r,indent=1)); json.dump(r,open(str(B)+'_checks.json','w'),indent=1)
