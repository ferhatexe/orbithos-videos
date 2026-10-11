import sys; sys.path.insert(0,"/home/claude/toolkit")
from r37 import *
import thumbstd
sc=B.SC[0]; buf,_,_,_=s_hook(16.0,sc); buf=sepia(buf)
buf=zoom(buf,225,640,1.6,270,610)
buf=np.clip(buf,0,1.2)*VIG+GR[0]
bg=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
d=ImageDraw.Draw(bg)
card(d,"Tamám Shud",540,760,fs=110,fg=(25,22,18),bg=(240,232,210),fn=SERIF,ang=-5,pad=(50,24))
stamp(d,"NO NAME",830,1090,80,1.0,-10)
thumbstd.make(bg,"A MAN WITH NO NAME","AND A SECRET CODE",(240,200,120),"SOMERTON BEACH · 1948","/mnt/user-data/outputs/orbithos_tamam_shud_kucuk_resim.jpg",band=(20,16,12,220),label_col=(150,35,30))
