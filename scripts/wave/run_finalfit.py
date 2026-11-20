import json,sys,time,resource,numpy as np
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parents[2]/'src'))
from lsc5 import wave
R=str(__import__('pathlib').Path(__file__).resolve().parents[2])+'/'; B=R+'artifacts/wave/bundle_x4x6_v1'
man=json.load(open(R+'artifacts/cpu-pilot/train_manifest.json'))
t=time.time(); b=wave.finalfit(R+'data/train',man,B); print('fit seconds',time.time()-t,flush=True)
