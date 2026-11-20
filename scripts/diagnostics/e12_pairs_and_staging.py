import numpy as np, json, pathlib, hashlib
R=pathlib.Path(__file__).resolve().parents[2]/'artifacts'
def load(p): z=np.load(p,allow_pickle=False); return {k:z[k] for k in z.files}
e01=load(R/'cpu-baseline/oof/oof.npz'); e02=load(R/'cpu-temporal/oof/oof.npz')
order={i:k for k,i in enumerate(e01['ids'])}
# E08 provisional
P=np.zeros((1125,5),np.float32); Pr=np.zeros_like(P); seen=np.zeros(1125,bool); sig=np.empty(1125,'<U3')
for s in ['m02','m03','m04']:
    v=load(R/f'rgb-loso/remote_heads/runs/r2-e08-{s}-s17-20261120-01/validation.npz')
    for i,ii in enumerate(v['ids']):
        k=order[ii]; assert not seen[k]; seen[k]=True; P[k]=v['probabilities'][i]; Pr[k]=v['reversed_probabilities'][i]
        assert v['labels'][i]==e01['labels'][k]
assert seen.all() and (e02['ids']==e01['ids']).all()
y=e01['labels']; S=e01['outer_signers']
def rep(name,prob):
    c=prob.argmax(1)==y
    print(f"{name:22s} {c.sum():4d}/1125 {100*c.mean():.2f}% ", {s:int(c[S==s].sum()) for s in ['M02','M03','M04']})
    return c
c1=rep('E01',e01['probabilities']); c2=rep('E02O',e02['probabilities']); c8=rep('E08prov',P); rep('E08prov reversed',Pr)
for nm,Q,cq in [('E01+E08prov',P,c8),('E01+E02O',e02['probabilities'],c2)]:
    ce=rep('50/50 '+nm,0.5*e01['probabilities']+0.5*Q)
    best=c1 if c1.sum()>=cq.sum() else cq
    print('   gain vs best comp',int(ce.sum()-best.sum()),'per person',{s:int(ce[S==s].sum()-best[S==s].sum()) for s in ['M02','M03','M04']})
    print('   complementary: comp right & E01 wrong',int((cq&~c1).sum()),' oracle',int((cq|c1).sum()))
# partial restoration equivalence (staging vs cache embeddings), diagnostic only
st=R/'rgb-loso/restore_execution/full/.cache-0_j9o83v'; ca=R/'rgb-loso/extract_execution/full/cache'
md=[];bad=0;n=0
for f in sorted(st.glob('*.npz')):
    try: a=np.load(f)['embeddings']; b=np.load(ca/f.name)['embeddings']
    except Exception as e: bad+=1; continue
    n+=1; md.append(float(np.abs(a-b).max()))
md=np.array(md); print('staging readable',n,'unreadable',bad,'max abs diff',md.max(),'frac exact',(md==0).mean(), 'p99',np.quantile(md,.99))
