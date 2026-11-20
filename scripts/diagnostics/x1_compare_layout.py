import json,sys,numpy as np,pathlib
root=pathlib.Path(__file__).resolve().parents[2]; D=root/'data/train'
man={s['id']:s for s in json.load(open(root/'artifacts/cpu-pilot/train_manifest.json'))['samples']}
mpz=np.load(root/f'artifacts/diagnostics/x1/{sys.argv[1]}.npz')
B={'pose':(0,132,4),'face':(132,1536,3),'lh':(1536,1599,3),'rh':(1599,1662,3)}
def blk(x,b): a,e,k=B[b]; return x[:,a:e].reshape(len(x),-1,k)
stats={b:{'n':0,'xy_med':[],'corr':[]} for b in ['pose','face','lh','rh','lh_vs_rh','rh_vs_lh','pose_mirror']}
zero_agree={b:[] for b in ['lh','rh']}; Tmatch=0
for i in mpz.files:
    ours=mpz[i]; theirs=np.load(D/man[i]['landmarks_path'])
    Tmatch+=int(len(ours)==len(theirs)); L=min(len(ours),len(theirs)); o=ours[:L]; t=theirs[:L]
    for name,(bo,bt,mir) in {'pose':('pose','pose',0),'face':('face','face',0),'lh':('lh','lh',0),'rh':('rh','rh',0),'lh_vs_rh':('lh','rh',0),'rh_vs_lh':('rh','lh',0),'pose_mirror':('pose','pose',1)}.items():
        O=blk(o,bo)[...,:2].copy(); T=blk(t,bt)[...,:2]
        if mir: O[...,0]=1-O[...,0]
        ok=(np.abs(O).sum((1,2))>0)&(np.abs(T).sum((1,2))>0)
        if ok.sum()==0: continue
        d=np.abs(O[ok]-T[ok]); stats[name]['xy_med'].append(np.median(d)); stats[name]['n']+=int(ok.sum())
        stats[name]['corr'].append(np.corrcoef(O[ok].ravel(),T[ok].ravel())[0,1])
    for b in ['lh','rh']:
        zo=(blk(o,b)==0).all((1,2)); zt=(blk(t,b)==0).all((1,2)); zero_agree[b].append((zo==zt).mean())
out={'clips':len(mpz.files),'T_equal':Tmatch}
for k,v in stats.items():
    if v['n']: out[k]={'frames_both_detected':v['n'],'median_abs_xy':float(np.median(v['xy_med'])),'corr_min':float(np.min(v['corr'])),'corr_median':float(np.median(v['corr']))}
for b in zero_agree: out[b+'_zero_block_agreement']=float(np.mean(zero_agree[b]))
# visibility / z check pose
print(json.dumps(out,indent=1)); json.dump(out,open(root/f'artifacts/diagnostics/x1/compare_{sys.argv[1]}.json','w'),indent=1)
