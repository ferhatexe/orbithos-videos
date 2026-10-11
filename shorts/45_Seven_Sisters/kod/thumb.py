import sys; sys.path.insert(0,"/home/claude/toolkit")
from r45 import *
import thumbstd
t=4.0; buf=NIGHT.copy()
am=arch_mask(70,470,300,690); A=am.f()[...,None]; buf[:]=buf*(1-A)+GREEK*A; outl(buf,am,a=1,th=3,fill=0)
for k,(x,y) in enumerate(CL7):
    gstar(buf,270+x*2.6,480+y*2.6,(20 if k!=6 else 9),1.0 if k!=6 else 0.35,WHITEG,1.0)
for k in range(6): sister(buf,110+k*52,665,0.62,SIS[k],1.0,arm=0.2)
sister(buf,430,665,0.62,SIS[6],0.4,face=True)
buf=np.clip(buf*GT*LIGHT,0,1.3)*VIG
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"7 SISTERS · 1 LOST","THE OLDEST STORY ON EARTH?",(255,214,120),"GREECE · AUSTRALIA","/mnt/user-data/outputs/orbithos_seven_sisters_kucuk_resim.jpg",band=(10,14,40,225),label_col=(160,30,44))
