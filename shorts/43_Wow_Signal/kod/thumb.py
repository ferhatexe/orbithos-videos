import sys; sys.path.insert(0,"/home/claude/toolkit")
from r43 import *
import thumbstd
t=EV["wow"]+0.6; buf,hud=s_print(t,B.S("print"))
buf=np.clip(buf,0,1.2)*PT*VIG
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
printout(d,PR_ROWS); redring(d,1.0); wow(d,1.0)
img.alpha_composite(ov)
thumbstd.make(img,"THE WOW! SIGNAL","NEVER HEARD AGAIN",(255,204,92),"OHIO · AUGUST 1977","/mnt/user-data/outputs/orbithos_wow_signal_kucuk_resim.jpg",band=(20,24,52,228),label_col=(204,34,28))
