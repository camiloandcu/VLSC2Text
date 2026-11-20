import json,time,numpy as np,pathlib,cv2
root=pathlib.Path(__file__).resolve().parents[2]; D=root/'data/train'; OUT=root/'artifacts/diagnostics/x2'
man=json.load(open(root/'artifacts/cpu-pilot/train_manifest.json'))['samples']
t0=time.time(); feats=[]; ids=[]
for s in man:
    assert s['video_path'].startswith('videos/')
    cap=cv2.VideoCapture(str(D/s['video_path'])); ok,f=cap.read()  # first frame only
    h,w=f.shape[:2]; f=f.astype(np.float32)/255
    strips=[f[:int(.08*h)], f[:, :int(.12*w)], f[:, int(.88*w):]]
    v=[]
    for st in strips:
        px=st.reshape(-1,3); v+=list(px.mean(0))+list(px.std(0))+list(np.percentile(px,[10,50,90],axis=0).ravel())
    feats.append(v); ids.append(s['id'])
np.savez_compressed(OUT/'border_feats.npz',ids=np.array(ids),X=np.array(feats,np.float32))
print('seconds',time.time()-t0)
