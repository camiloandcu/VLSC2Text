import json,sys,time,numpy as np,pathlib,cv2
import mediapipe as mp
root=pathlib.Path(__file__).resolve().parents[2]; D=root/'data/train'; OUT=root/'artifacts/diagnostics/x9'
ids=[r['id'] for r in json.load(open(root/'artifacts/rgb-feasibility/video_preflight.json'))['records']]
man={s['id']:s for s in json.load(open(root/'artifacts/cpu-pilot/train_manifest.json'))['samples']}
mode=sys.argv[1]  # c2 | crop
def hands(res,ox=0,oy=0,sw=1,sh=1,W=1920,H=1080):
    out=[]
    for h in (res.left_hand_landmarks,res.right_hand_landmarks):
        out.append(None if h is None else np.array([[ (ox+l.x*sw)/W,(oy+l.y*sh)/H,l.z] for l in h.landmark]))
    return out
t0=time.time(); stats={'frames':0,'npy_lh':0,'npy_rh':0,'new_lh':0,'new_rh':0,'npy_any':0,'new_any':0,'new_any_given_npy_none':0,'npy_none':0}
for i in ids:
    s=man[i]; x=np.load(D/s['landmarks_path']); pose=x[:,:132].reshape(-1,33,4)
    cap=cv2.VideoCapture(str(D/s['video_path']))
    if mode=='crop':
        pts=pose[:,[0,11,12,13,14,15,16,17,18,19,20],:2].reshape(-1,2); pts=pts[(pts>0).all(1)]
        x0,y0=np.clip(pts.min(0)-0.08,0,1); x1,y1=np.clip(pts.max(0)+0.08,0,1)
        X0,Y0,X1,Y1=int(x0*1920),int(y0*1080),int(x1*1920),int(y1*1080)
    with mp.solutions.holistic.Holistic(static_image_mode=False,model_complexity=2 if mode=='c2' else 1,min_detection_confidence=0.5,min_tracking_confidence=0.5) as h:
        k=0
        while True:
            ok,fr=cap.read()
            if not ok: break
            if mode=='crop':
                crop=np.ascontiguousarray(fr[Y0:Y1,X0:X1]); res=h.process(cv2.cvtColor(crop,cv2.COLOR_BGR2RGB))
            else:
                res=h.process(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB))
            nl=res.left_hand_landmarks is not None; nr=res.right_hand_landmarks is not None
            ol=(x[k,1536:1599]!=0).any(); orr=(x[k,1599:]!=0).any()
            stats['frames']+=1; stats['npy_lh']+=ol; stats['npy_rh']+=orr; stats['new_lh']+=nl; stats['new_rh']+=nr
            stats['npy_any']+=(ol or orr); stats['new_any']+=(nl or nr)
            if not(ol or orr): stats['npy_none']+=1; stats['new_any_given_npy_none']+=(nl or nr)
            k+=1
stats={k:int(v) for k,v in stats.items()}; stats['seconds']=time.time()-t0; stats['mode']=mode
print(json.dumps(stats)); json.dump(stats,open(OUT/f'{mode}.json','w'))
