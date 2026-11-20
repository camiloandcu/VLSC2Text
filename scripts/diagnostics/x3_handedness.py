import json,numpy as np,pathlib,collections
root=pathlib.Path(__file__).resolve().parents[2]; D=root/'data/train'
man=json.load(open(root/'artifacts/cpu-pilot/train_manifest.json'))['samples']
# pose layout: 33x4 (x,y,z,vis); 15=left wrist, 16=right wrist (subject's), 11/12 shoulders
tab=collections.defaultdict(lambda:[0,0]); per=[]
for s in man:
    x=np.load(D/s['landmarks_path'])[:,:132].reshape(-1,33,4)
    sh=np.abs(x[:,11,0]-x[:,12,0]); sc=np.median(sh[sh>1e-3]) if (sh>1e-3).any() else 1
    # height raised above rest: min y (higher in image = smaller y) relative to the clip's final frames
    lift={w:(np.median(x[-3:,w,1])-x[:,w,1].min())/sc for w in (15,16)}
    dom='L' if lift[15]>lift[16] else 'R'
    tab[(s['signer'],s['label'])][0 if dom=='L' else 1]+=1
    per.append({'id':s['id'],'dom':dom,'lift_L':float(lift[15]),'lift_R':float(lift[16])})
print('signer label  L  R')
for k in sorted(tab): print(*k, *tab[k])
root.joinpath('artifacts/diagnostics/x3/handedness.json').write_text(json.dumps({'method':'max wrist lift above final-rest position, scaled by shoulder width; pose 15=left,16=right wrist','table':{f'{a}|{b}':v for (a,b),v in tab.items()},'clips':per},indent=0))
