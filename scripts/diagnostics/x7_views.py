import json,re,numpy as np,pathlib,itertools
root=pathlib.Path(__file__).resolve().parents[2]; D=root/'data/train'
m=json.load(open(root/'artifacts/cpu-pilot/train_manifest.json'))['samples']
idx={}
for s in m:
    n=int(re.search(r'Clip(\d+)$',s['id']).group(1)); idx[(s['label'],s['signer'],s['view'],n)]=s
def energy(s):
    x=np.load(D/s['landmarks_path'],allow_pickle=False); d=np.abs(np.diff(x,axis=0)).sum(1); return x.shape[0],d
res={'same_T':0,'pairs':0,'corr_aligned':[],'corr_shuffled':[]}
rng=np.random.default_rng(0)
groups={}
for (lab,sig,view,n),s in idx.items(): groups.setdefault((lab,sig,view),[]).append((n,s))
for (lab,sig,view),lst in groups.items():
    if view!='V01': continue
    lst.sort()
    other={v:sorted(groups[(lab,sig,v)]) for v in ['V02','V03']}
    for i,(n,s) in enumerate(lst):
        T0,e0=energy(s)
        for v in ['V02','V03']:
            n2,s2=other[v][i]; T2,e2=energy(s2); res['pairs']+=1; res['same_T']+=int(T0==T2)
            L=min(len(e0),len(e2)); res['corr_aligned'].append(float(np.corrcoef(e0[:L],e2[:L])[0,1]))
            j=rng.integers(len(other[v])); 
            if j==i: j=(j+1)%len(other[v])
            T3,e3=energy(other[v][j][1]); L=min(len(e0),len(e3)); res['corr_shuffled'].append(float(np.corrcoef(e0[:L],e3[:L])[0,1]))
a=np.array(res['corr_aligned']); b=np.array(res['corr_shuffled'])
out={'pairs':res['pairs'],'same_T_fraction':res['same_T']/res['pairs'],'energy_corr_aligned_median':float(np.nanmedian(a)),'energy_corr_aligned_p10':float(np.nanquantile(a,.1)),'energy_corr_other_clip_median':float(np.nanmedian(b)),'note':'V01 clip i paired with i-th clip of V02/V03 in same signer/class; energy = sum abs frame diff over all 1662 columns (layout-agnostic)'}
print(json.dumps(out,indent=1)); json.dump(out,open(root/'artifacts/diagnostics/x7/views.json','w'),indent=1)
