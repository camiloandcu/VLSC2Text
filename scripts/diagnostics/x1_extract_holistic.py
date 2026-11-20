import json,sys,time,numpy as np,pathlib,cv2
import mediapipe as mp
root=pathlib.Path(__file__).resolve().parents[2]; D=root/'data/train'
OUT=root/'artifacts/diagnostics/x1'
pre=json.load(open(root/'artifacts/rgb-feasibility/video_preflight.json'))
recs=pre['records']; ids=[r['id'] for r in recs]
man={s['id']:s for s in json.load(open(root/'artifacts/cpu-pilot/train_manifest.json'))['samples']}
complexity=int(sys.argv[1]) if len(sys.argv)>1 else 1
def ser(res):
    pose=np.array([[l.x,l.y,l.z,l.visibility] for l in res.pose_landmarks.landmark]).ravel() if res.pose_landmarks else np.zeros(132)
    face=np.array([[l.x,l.y,l.z] for l in res.face_landmarks.landmark]).ravel()[:1404] if res.face_landmarks else np.zeros(1404)
    lh=np.array([[l.x,l.y,l.z] for l in res.left_hand_landmarks.landmark]).ravel() if res.left_hand_landmarks else np.zeros(63)
    rh=np.array([[l.x,l.y,l.z] for l in res.right_hand_landmarks.landmark]).ravel() if res.right_hand_landmarks else np.zeros(63)
    return np.concatenate([pose,face,lh,rh])
t0=time.time(); allrows={}
for i in ids:
    s=man[i]; assert s['video_path'].startswith('videos/')
    cap=cv2.VideoCapture(str(D/s['video_path'])); rows=[]
    with mp.solutions.holistic.Holistic(static_image_mode=False,model_complexity=complexity,min_detection_confidence=0.5,min_tracking_confidence=0.5) as h:
        while True:
            ok,fr=cap.read()
            if not ok: break
            rows.append(ser(h.process(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB))))
    allrows[i]=np.array(rows)
np.savez_compressed(OUT/f'mp_c{complexity}.npz',**{k.replace('/','_'):v for k,v in allrows.items()})
print('seconds',time.time()-t0)
