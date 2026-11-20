import json,sys,numpy as np,pathlib,cv2
root=pathlib.Path(__file__).resolve().parents[2]; D=root/'data/train'; OUT=root/'artifacts/diagnostics/x3'
man=[s for s in json.load(open(root/'artifacts/cpu-pilot/train_manifest.json'))['samples']]
def frames(path,k=6):
    cap=cv2.VideoCapture(str(path)); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); out=[]
    for j in np.linspace(0,n-1,k).round().astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES,int(j)); ok,f=cap.read(); out.append(f if ok else np.zeros((1080,1920,3),np.uint8))
    return out
label=sys.argv[1]; view=sys.argv[2]; scale=float(sys.argv[3]) if len(sys.argv)>3 else 0.15
rows=[]
for sig in ['M02','M03','M04']:
    s=sorted([x for x in man if x['label']==label and x['signer']==sig and x['view']==view],key=lambda x:x['id'])[0]
    fs=[cv2.resize(f,None,fx=scale,fy=scale) for f in frames(D/s['video_path'])]
    rows.append(np.hstack(fs))
cv2.imwrite(str(OUT/f'{label}_{view}.jpg'),np.vstack(rows))
