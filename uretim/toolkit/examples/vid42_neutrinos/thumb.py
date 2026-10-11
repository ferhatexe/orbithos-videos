import sys; sys.path.insert(0,"/home/claude/toolkit")
from r42 import *
import thumbstd
t=6.0; buf=CY.copy()
streaks(buf,t,60,1,a=1.0,ang=1.35,spread=0.12,spd=1.1,box=(0,250,w,720))
for k in range(5): glow(buf,270,520,140,(0.05,0.10,0.20),-0.25) if False else None
person(buf,270,690,1.3,a=1.0,bones=0.9)
glow(buf,262,420,40,GOLD,0.35)
buf=buf*P3+PAP*(1-P3); buf=np.clip(buf,0,1.4)*PT*VIG
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"GHOST PARTICLES","ARE PASSING THROUGH YOU",(255,204,92),"100 TRILLION · EVERY SECOND","/mnt/user-data/outputs/orbithos_neutrinos_kucuk_resim.jpg",band=(8,20,46,225),label_col=(200,70,55))
