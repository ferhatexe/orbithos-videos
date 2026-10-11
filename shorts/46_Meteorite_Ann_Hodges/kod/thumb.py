import sys; sys.path.insert(0,"/home/claude/toolkit")
from r46 import *
import thumbstd
buf=PAGE.copy(); t=0.5
room(buf,1.0,hole=1.0); radio(buf,420,600,1.0); couch(buf,90,602,1.0); sleeper(buf,110,550,1.0,t)
rock(buf,300,440,34,1.0,rot=0.4,tail=200,tdir=(0.25,-1.0)); burst(buf,300,470,60,MUST,a=0.0)
buf=np.clip(buf,0,1.2)*PT*VIG
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"HIT BY A METEORITE","WHILE NAPPING ON HER COUCH",(255,200,90),"ALABAMA · 1954","/mnt/user-data/outputs/orbithos_meteorite_ann_hodges_kucuk_resim.jpg",band=(30,40,48,228),label_col=(220,96,78))
