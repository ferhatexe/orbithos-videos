import sys; sys.path.insert(0,"/home/claude/toolkit")
from r41 import *
import thumbstd
t=4.0; buf=np.zeros((h,w,3),np.float32)
parchment(buf,0.1); nightsky(buf,470,t); frame(buf)
pines(buf,470,14,3,0.95,110)
house(buf,90,560,0.9,lit=1.0); house(buf,450,555,0.85,lit=1.0)
meeting_house(buf,270,560,1.1)
hl=M(); hl.poly([(26,600),(150,570),(390,580),(w-26,600),(w-26,654),(26,654)]); wc(buf,hl,0.3)
girl(buf,140,650,1.45,t,fit=1.0,face=1)
rye(buf,410,700,1.25,0.0,ergot=1.5)
buf=np.clip(buf,0,1.2)*PT*VIG+GR[0]
buf*=(1-0.55*np.clip((yy-660)/120,0,1))[...,None]
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"SALEM'S WITCHES","…OR A POISONOUS FUNGUS?",(205,150,230),"SALEM · 1692","/mnt/user-data/outputs/orbithos_salem_kucuk_resim.jpg",band=(18,14,12,230),label_col=(150,30,24))
