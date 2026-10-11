import sys; sys.path.insert(0,"/home/claude/toolkit")
from r38 import *
import thumbstd
buf=np.zeros((h,w,3),np.float32); bg(buf,CR)
sunburst(buf,290,470,900,24,0.3,YL,a=1.0)
comp(buf,M().circ(320,450,170),RD,sh=0.12)
P=head(buf,250,490,330)
beamline(buf,(-20,P(-0.6,-0.08)[1]),(w+20,P(0.8,0.06)[1]),1.0,th=7)
rgrad(buf,*P(-0.55,-0.10),30,YL,0.9); rgrad(buf,*P(0.62,0.04),30,YL,0.9)
buf=np.clip(buf,0,1.2)*PT*VIG+GR[0]
buf*=(1-0.6*np.clip((yy-640)/200,0,1))[...,None]
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"HE PUT HIS HEAD IN A","PARTICLE ACCELERATOR",(250,205,65),"PROTVINO · 1978","/mnt/user-data/outputs/orbithos_bugorski_kucuk_resim.jpg",band=(25,22,22,230),label_col=(205,35,30))
