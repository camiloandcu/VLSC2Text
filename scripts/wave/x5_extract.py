import json,sys,time,subprocess,numpy as np
from PIL import Image
R=str(__import__('pathlib').Path(__file__).resolve().parents[2])+'/'
sys.path.insert(0,R+'src')
from lsc5.rgb_encoder import Encoder
from lsc5.rgb_frames import indices, probe, letterbox
from lsc5 import wave
man=json.load(open(R+'artifacts/cpu-pilot/train_manifest.json'))['samples']
groups={}
for k,s in enumerate(man): groups.setdefault((s['signer'],s['label']),[]).append(k)
subset=sorted(k for g in groups.values() for k in g[::4][:19])  # ~19 per signer/class, spread over views
enc=Encoder(R+'artifacts/rgb-feasibility')
def frames(path,chosen,w,h):
    sel=sorted(set(chosen)); cmd=['ffmpeg','-v','error','-threads','1','-i',path,'-map','0:v:0','-an','-vsync','0','-vf','select='+'+'.join(f'eq(n\\,{i})' for i in sel),'-f','rawvideo','-pix_fmt','rgb24','pipe:1']
    raw=subprocess.run(cmd,capture_output=True,check=True).stdout; arr=np.frombuffer(raw,np.uint8).reshape(-1,h,w,3)
    assert len(arr)==len(sel); m={i:arr[j] for j,i in enumerate(sel)}; return [m[i] for i in chosen]
def square(fr,cx,cy,side,W,H):
    side=int(max(side,32)); x0=int(round(cx-side/2)); y0=int(round(cy-side/2))
    canvas=np.zeros((side,side,3),np.uint8)+np.array([124,116,104],np.uint8)
    sx0,sy0=max(x0,0),max(y0,0); sx1,sy1=min(x0+side,W),min(y0+side,H)
    if sx1>sx0 and sy1>sy0: canvas[sy0-y0:sy1-y0,sx0-x0:sx1-x0]=fr[sy0:sy1,sx0:sx1]
    return np.asarray(Image.fromarray(canvas).resize((224,224),Image.Resampling.BILINEAR))
out={'ids':[],'hand':[],'roi':[]}; t0=time.time()
for n_done,k in enumerate(subset):
    s=man[k]; path=R+'data/train/'+s['video_path']; x=np.load(R+'data/train/'+s['landmarks_path'])
    n,W,H=probe(path); chosen=indices(n).tolist(); frs=frames(path,chosen,W,H)
    left=wave.left_dominant(x); pose,_,lh,rh=wave.split_blocks(x); hand=lh if left else rh; wr=15 if left else 16
    sw=np.abs(pose[:,11,0]-pose[:,12,0]); sw=np.median(sw[sw>1e-3])*W
    up=pose[:,[0,11,12,13,14,15,16,17,18,19,20],:2].reshape(-1,2); up=up[(up>0).all(1)&(up<1).all(1)]
    (ux0,uy0),(ux1,uy1)=up.min(0)*[W,H],up.max(0)*[W,H]
    rside=max(1.25*(ux1-ux0),1.25*(uy1-uy0),0.5*min(W,H))
    hc,rc=[],[]
    for j,fi in enumerate(chosen):
        fi=min(fi,len(x)-1); fr=frs[j]
        if (hand[fi]!=0).any():
            p=hand[fi,:,:2]*[W,H]; c=(p.min(0)+p.max(0))/2; side=max(1.6*(p.max(0)-p.min(0)).max(),0.9*sw)
        else:
            c=pose[fi,wr,:2]*[W,H]; side=0.9*sw
        crop=square(fr,c[0],c[1],side,W,H); roi=square(fr,(ux0+ux1)/2,(uy0+uy1)/2,rside,W,H)
        if left: crop=crop[:,::-1].copy(); roi=roi[:,::-1].copy()
        hc.append(crop); rc.append(roi)
    eh,_=enc.extract(np.stack(hc)); er,_=enc.extract(np.stack(rc))
    out['ids'].append(s['id']); out['hand'].append(eh); out['roi'].append(er)
    if n_done%50==0: print(n_done,len(subset),round(time.time()-t0,1),flush=True)
np.savez_compressed(R+'artifacts/wave/x5/embeddings.npz',ids=np.array(out['ids']),hand=np.stack(out['hand']),roi=np.stack(out['roi']))
print('done',len(subset),time.time()-t0)
