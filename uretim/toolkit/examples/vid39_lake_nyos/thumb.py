import sys; sys.path.insert(0,"/home/claude/toolkit")
from r39 import *
import thumbstd
t=5.0; buf=np.zeros((h,w,3),np.float32)
grad(buf,[(0,NAVY),(520,DEEP)]); stars(buf,t,1.0)
F_(buf,M().circ(420,330,34),MOON,sh=0); rgrad(buf,420,330,110,(0.7,0.75,0.9),0.15)
hills(buf,470,[H1,H2],40)
F_(buf,M().ell(270,520,100,18),LAKE,sh=0)
for k in range(7): gasblob(buf,40+k*80,600+15*math.sin(k),90,t,k+50,a=0.22)
hills(buf,600,[H3],25,1.0)
F_(buf,M().rect(-5,690,w+5,h+5),(0.10,0.16,0.14))
for k,(x,y,s) in enumerate(((70,690,1.3),(190,700,1.6),(330,690,1.4),(460,705,1.6))): hut(buf,x,y,s,light=0.0)
fogm=M().rect(-5,600,w+5,760); F_(buf,fogm,GAS,a=0.22,sh=0)
buf=np.clip(buf,0,1.2)*VIG+GR[0]
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"THIS LAKE KILLED 1,746","PEOPLE IN ONE NIGHT",(140,250,125),"LAKE NYOS · 1986","/mnt/user-data/outputs/orbithos_lake_nyos_kucuk_resim.jpg",band=(10,14,30,225),label_col=(30,110,60))
