import sys; sys.path.insert(0,"/home/claude/toolkit")
from r50 import *
import thumbstd
t=0.35; buf=BG_STREET.copy()
building(buf,70,GY,110,170); building(buf,360,GY,110,200)
for k in range(6): fig(buf,90+k*72,GY+24,0.75,[ULTRA,VERD,PURP,ROSEP,WOODC,GOLDL][k],t,1.0,k*1.7,hat=["coif","cap",None][k%3])
fig(buf,270,GY+6,1.7,VERM,t,1.0,0.0,hat="coif")
buf=np.clip(buf,0,1.2)*PT*VIG
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"THEY DANCED","AND COULDN'T STOP",(255,196,120),"STRASBOURG · 1518","/mnt/user-data/outputs/orbithos_dancing_plague_kucuk_resim.jpg",band=(40,16,10,228),label_col=(176,36,24))
