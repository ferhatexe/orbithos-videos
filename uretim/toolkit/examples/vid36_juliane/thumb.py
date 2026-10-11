import sys; sys.path.insert(0,"/home/claude/toolkit")
from r36 import *
import thumbstd
buf=np.zeros((h,w,3),np.float32)
grad(buf,[(0,(0.10,0.09,0.30)),(420,(0.62,0.26,0.48)),(760,(1.0,0.62,0.34))])
rgrad(buf,400,520,170,(1.0,0.75,0.45),0.55)
for k,(m,col) in enumerate(zip(CLS,[(0.75,0.45,0.62),(0.85,0.55,0.65),(0.95,0.70,0.70)])): comp(buf,m,col,sh=0.15,ox=-int(k*120),oy=int(-20-60*k),a=0.9)
bolt(buf,60,280,170,560,7,a=0.9,th=4)
seats(buf,285,450,2.0,-0.35,0.95)
jungle(buf,4.0,40,[(0.20,0.35,0.42),G1,GD,G1,GD],oy=330,skip=(3,4))
buf=np.clip(buf,0,1.2)*PT*VIG+GR[0]
bg=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(bg,"SHE FELL 10,000 FT","AND SURVIVED",(255,190,90),"LANSA 508 · AMAZON · 1971","/mnt/user-data/outputs/orbithos_juliane_koepcke_kucuk_resim.jpg",label_col=(205,70,50))
