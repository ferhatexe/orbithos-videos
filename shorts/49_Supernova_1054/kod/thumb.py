import sys; sys.path.insert(0,"/home/claude/toolkit")
from r49 import *
import thumbstd
buf=PAPERR.copy(); t=1.0
mountains(buf,600,90,3,1.0,220,0.55); mist(buf,640,40,0.6); mountains(buf,680,60,8,1.0,200,0.85)
redsun(buf,150,420,44); gstar(buf,360,440,22,t,1.0,1.2)
buf=np.clip(buf,0,1.2)*PT*VIG
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
d=ImageDraw.Draw(img); seal(d,"客星",880,1220,70)
thumbstd.make(img,"A STAR SO BRIGHT","YOU COULD SEE IT AT NOON",(255,190,120),"CHINA · JULY 1054","/mnt/user-data/outputs/orbithos_supernova_1054_kucuk_resim.jpg",band=(28,22,22,228),label_col=(196,40,26))
