"""Nested estimate with tie-averaging (no arbitrary order preference) and full-data selection by summed inner score.
Usage: nested_ties.py [--exclude PREFIX ...] [--out NAME.json]; the default writes nested_ties.json over every logged variant."""
import argparse,json,pathlib,numpy as np
ap=argparse.ArgumentParser(); ap.add_argument('--exclude',nargs='*',default=[]); ap.add_argument('--out',default='nested_ties.json'); args=ap.parse_args()
ROOT=pathlib.Path(__file__).resolve().parents[2]; I2=ROOT/'artifacts/iter2'; OUT=ROOT/'artifacts/iter3'
man=json.load(open(ROOT/'artifacts/cpu-pilot/train_manifest.json'))['samples']
y=np.array([int(s['label'][-2:])-1 for s in man]); S=np.array([s['signer'] for s in man])
n2=json.load(open(I2/'nested_selection.json'))['inner_scores']; log=json.load(open(OUT/'log.json'))
cands={k:(v,I2/f'{k}.npz') for k,v in n2.items()}; cands.update({k:(v['inner'],OUT/f'{k}.npz') for k,v in log.items()})
cands={k:v for k,v in cands.items() if not k.startswith(tuple(args.exclude))} if args.exclude else cands
ok={k:(np.load(p)['probabilities'].argmax(1)==y) for k,(_,p) in cands.items()}
res={'variants':len(cands),'excluded_prefixes':args.exclude,'outer':{}}; tot=0.0
for outer in ('M02','M03','M04'):
    best=max(v[0][outer] for v in cands.values()); tied=[k for k,v in cands.items() if v[0][outer]==best]
    val=float(np.mean([ok[k][S==outer].sum() for k in tied])); tot+=val; res['outer'][outer]={'tied':tied,'expected_correct':val}
res['nested_total']=tot; res['nested_accuracy']=tot/1125
rank=sorted(cands,key=lambda k:-sum(cands[k][0].values()))
res['full_data_rule']=[(k,sum(cands[k][0].values()),int(ok[k].sum())) for k in rank[:6]]
print(json.dumps(res,indent=1)); json.dump(res,open(OUT/args.out,'w'),indent=1)
