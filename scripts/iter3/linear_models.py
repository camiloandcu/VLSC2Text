"""Iteration 3 diversity check: linear/kernel models on the winning feature set (needs .venv-mp with scikit-learn).
Step 1 (.venv): dump features.  Step 2 (.venv-mp): fit LOSO models and test 50/50 pairs with the MLP."""
import json,sys,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[2]; OUT=ROOT/'artifacts/iter3'
if sys.argv[1]=='dump':
    sys.path.insert(0,str(ROOT/'src'))
    from lsc5 import wave, wave_iter as wi
    man=json.load(open(ROOT/'artifacts/cpu-pilot/train_manifest.json'))
    ids,xs,y,S=wave.load_train(ROOT/'data/train',man); perm=np.load(ROOT/'artifacts/wave/face_perm.npy')
    cfg=dict(shape=True,vel=True,active=True,aug=('view',),n_aug=4); rng=np.random.default_rng(123)
    canon=[wave.canonical(x,perm) for x in xs]
    F=np.stack([wi.features(c,cfg) for c in canon]); A=np.stack([np.stack([wi.features(c,cfg,rng,augment=True) for _ in range(4)]) for c in canon])
    np.savez_compressed(OUT/'features_winner.npz',ids=np.array(ids),F=F,A=A,y=y,S=S)
else:
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    z=np.load(OUT/'features_winner.npz'); F,A,y,S=z['F'],z['A'],z['y'],z['S']
    mlp=np.load(OUT/'v3_base.npz')['probabilities']; res={}
    for name,make in [('logreg_C0.1',lambda: LogisticRegression(C=0.1,max_iter=5000)),('logreg_C1',lambda: LogisticRegression(C=1,max_iter=5000)),
                      ('svc_rbf',lambda: SVC(C=3,probability=True,random_state=17))]:
        P=np.zeros((len(y),5))
        for held in ('M02','M03','M04'):
            f=np.where(S!=held)[0]; v=np.where(S==held)[0]
            X=np.concatenate([F[f]]+[A[f,k] for k in range(4)]); Y=np.tile(y[f],5)
            sc=StandardScaler().fit(X); m=make().fit(sc.transform(X),Y); P[v]=m.predict_proba(sc.transform(F[v]))
        ok=P.argmax(1)==y; e=(P+mlp)/2; oke=e.argmax(1)==y
        res[name]={'correct':int(ok.sum()),'per_signer':{h:int(ok[S==h].sum()) for h in ('M02','M03','M04')},
                   'pair_with_mlp':int(oke.sum()),'pair_per_signer':{h:int(oke[S==h].sum()) for h in ('M02','M03','M04')}}
        np.savez_compressed(OUT/f'{name}.npz',probabilities=P); print(name,json.dumps(res[name]),flush=True)
    json.dump(res,open(OUT/'linear_models.json','w'),indent=1)
