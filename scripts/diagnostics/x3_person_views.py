"""Contact sheet: one signer, one class, three views (train only)."""
import json,sys,pathlib,numpy as np,cv2
root=pathlib.Path(__file__).resolve().parents[2]; D=root/'data/train'
man=json.load(open(root/'artifacts/cpu-pilot/train_manifest.json'))['samples']
sig,label=sys.argv[1],sys.argv[2]; rows=[]
for view in ('V01','V02','V03'):
    s=sorted([x for x in man if x['label']==label and x['signer']==sig and x['view']==view],key=lambda x:x['id'])[0]
    cap=cv2.VideoCapture(str(D/s['video_path'])); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fr=[]
    for j in np.linspace(0,n-1,6).round().astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES,int(j)); ok,f=cap.read(); fr.append(cv2.resize(f,None,fx=.12,fy=.12))
    rows.append(np.hstack(fr))
cv2.imwrite(str(root/f'artifacts/diagnostics/x3/{sig}_{label}_views.jpg'),np.vstack(rows))
