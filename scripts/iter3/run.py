"""Iteration 3: configurable MLP variants with outer LOSO (seeds 17/29/43) and inner scores for nested selection.
Usage: run.py <variant> [...]; 'nested' recomputes the nested estimate over iteration-2 + iteration-3 variants."""
import json,sys,time,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'src'))
from lsc5 import wave, wave_iter as wi
OUT=ROOT/'artifacts/iter3'; I2=ROOT/'artifacts/iter2'
W=dict(shape=True,vel=True,active=True,aug=('view',),n_aug=4)
REG={
 'v3_base':dict(W),
 'v3_jitter4':dict(W,jitter=4),
 'v3_peak':dict(W,peak=True),
 'v3_aug8':dict(W,n_aug=8),
 'v3_wide':dict(W,hidden=256,dropout=0.5),
 'v3_wd':dict(W,wd=1e-2),
 'v3_peak_jitter4':dict(W,peak=True,jitter=4),
 'v3_jitter4_aug8':dict(W,jitter=4,n_aug=8),
 'v3_peak_jitter4_aug8':dict(W,peak=True,jitter=4,n_aug=8),
 'v3_gate13':dict(W,gate=1.3),
 'v3_gate16':dict(W,gate=1.6),
 'v4_contact':dict(W,gate=1.3,contact=True),
 'v4_bimanual':dict(W,gate=1.3,bimanual=True),
 'v4_contact_bimanual':dict(W,gate=1.3,contact=True,bimanual=True),
 # iteration 5 (pre-registered 21 Nov 2026): onset cues, wider yaw augmentation, yaw-robust contact scale
 'v5_early':dict(W,gate=1.3,contact=True,bimanual=True,early=True),
 'v5_yaw':dict(W,gate=1.3,contact=True,bimanual=True,yaw_lo=0.5,roll=12.0),
 'v5_scale':dict(W,gate=1.3,contact=True,bimanual=True,contact_scale='geo'),
 'v5_early_yaw':dict(W,gate=1.3,contact=True,bimanual=True,early=True,yaw_lo=0.5,roll=12.0),
 'v5_all':dict(W,gate=1.3,contact=True,bimanual=True,early=True,yaw_lo=0.5,roll=12.0,contact_scale='geo'),
}
man=json.load(open(ROOT/'artifacts/cpu-pilot/train_manifest.json'))
ids,xs,y,S=wave.load_train(ROOT/'data/train',man); perm=np.load(ROOT/'artifacts/wave/face_perm.npy')
canon=[wave.canonical(x,perm) for x in xs]
ref=np.load(OUT/'v3_gate13.npz')['probabilities'] if (OUT/'v3_gate13.npz').exists() and any(a.startswith(('v4','v5')) for a in sys.argv[1:]) else np.load(I2/'mlp_velshape_active_viewaug4.npz')['probabilities']
def fit(cfg,fx,fy,fs,seed): return wi.fit_mlp_cfg(fx,fy,fs,seed,hidden=cfg.get('hidden',128),dropout=cfg.get('dropout',0.3),wd=cfg.get('wd',1e-3))
def run(name):
    cfg=REG[name]; t=time.time(); rng=np.random.default_rng(123); n=cfg.get('n_aug',0)
    feats=[wi.features(c,cfg) for c in canon]
    extra=[[wi.features(c,cfg,rng,augment=True) for _ in range(n)] for c in canon]
    def data(idx):
        fx=[feats[i] for i in idx]+[extra[i][k] for k in range(n) for i in idx]
        return fx,np.tile(y[idx],n+1),np.tile(S[idx],n+1)
    per={}
    for seed in wave.SEEDS:
        probs=np.zeros((len(y),5),np.float32)
        for held in ('M02','M03','M04'):
            f=np.where(S!=held)[0]; v=np.where(S==held)[0]
            probs[v]=fit(cfg,*data(f),seed)([feats[i] for i in v])
        per[seed]=probs
    inner={}
    for outer in ('M02','M03','M04'):
        a,b=[h for h in ('M02','M03','M04') if h!=outer]; tot=0
        for tr,va in ((a,b),(b,a)):
            f=np.where(S==tr)[0]; v=np.where(S==va)[0]
            tot+=int((fit(cfg,*data(f),17)([feats[i] for i in v]).argmax(1)==y[v]).sum())
        inner[outer]=tot
    r,avg=wave.summarise(per,y,S,ref); r['inner']=inner; r['cfg']={k:(list(v) if isinstance(v,tuple) else v) for k,v in cfg.items()}; r['seconds']=round(time.time()-t)
    np.savez_compressed(OUT/f'{name}.npz',ids=np.array(ids),probabilities=avg)
    log=json.load(open(OUT/'log.json')) if (OUT/'log.json').exists() else {}; log[name]=r; json.dump(log,open(OUT/'log.json','w'),indent=1)
    print(f"{name:22s} {r['avg_correct']} {r['per_signer']} vsIter2 {r['vs_reference']['per_signer_delta']} seeds {r['seeds']} inner {inner} {r['seconds']}s",flush=True)
def nested():
    n2=json.load(open(I2/'nested_selection.json'))['inner_scores']; log=json.load(open(OUT/'log.json'))
    cands={k:(v,I2/f'{k}.npz') for k,v in n2.items()}; cands.update({k:(v['inner'],OUT/f'{k}.npz') for k,v in log.items()})
    oof={k:np.load(p)['probabilities'] for k,(_,p) in cands.items()}; tot=0; res={}
    for outer in ('M02','M03','M04'):
        best=max(cands,key=lambda k:cands[k][0][outer]); ok=int((oof[best].argmax(1)==y)[S==outer].sum()); tot+=ok; res[outer]=(best,ok)
    hind=max(cands,key=lambda k:int((oof[k].argmax(1)==y).sum()))
    out={'variants':len(cands),'outer':res,'nested_total':tot,'nested_accuracy':tot/1125,'best_hindsight':[hind,int((oof[hind].argmax(1)==y).sum())]}
    print(json.dumps(out)); json.dump(out,open(OUT/'nested.json','w'),indent=1)
for v in sys.argv[1:]:
    nested() if v=='nested' else run(v)
