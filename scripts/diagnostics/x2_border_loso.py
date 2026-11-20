import json,numpy as np,pathlib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
root=pathlib.Path(__file__).resolve().parents[2]
z=np.load(root/'artifacts/diagnostics/x2/border_feats.npz'); man={s['id']:s for s in json.load(open(root/'artifacts/cpu-pilot/train_manifest.json'))['samples']}
ids=z['ids']; X=z['X']; y=np.array([int(man[i]['label'][-2:])-1 for i in ids]); S=np.array([man[i]['signer'] for i in ids])
out={}
for held in ['M02','M03','M04']:
    tr=S!=held; sc=StandardScaler().fit(X[tr]); clf=LogisticRegression(max_iter=5000,C=1.0).fit(sc.transform(X[tr]),y[tr])
    out[held]=int((clf.predict(sc.transform(X[~tr]))==y[~tr]).sum())
# within-signer (does background separate classes inside one person?) 5-fold by clip parity
within={}
for sg in ['M02','M03','M04']:
    m=S==sg; idx=np.where(m)[0]; a=idx[::2]; b=idx[1::2]
    sc=StandardScaler().fit(X[a]); clf=LogisticRegression(max_iter=5000).fit(sc.transform(X[a]),y[a]); within[sg]=float((clf.predict(sc.transform(X[b]))==y[b]).mean())
res={'loso_correct':out,'loso_total':sum(out.values()),'loso_acc':sum(out.values())/1125,'within_signer_halfsplit_acc':within,'features':'first frame; top 8% + left/right 12% strips; RGB mean/std/p10/p50/p90'}
print(json.dumps(res,indent=1)); json.dump(res,open(root/'artifacts/diagnostics/x2/result.json','w'),indent=1)
