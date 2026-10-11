import sys; sys.path.insert(0,"/home/claude/toolkit")
from r51 import *
import thumbstd
t=0.6; buf=BG_DUSK.copy()
pandora(buf,210,680,1.0,t,1.0,lift=1.0); pithos(buf,370,680,0.85,1.0,lid=1.0,t=t); wisps(buf,370,500,t,0.6,1.0); hopelight(buf,370,495,t,1.0)
buf=np.clip(buf,0,1.2)*PT*VIG
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"PANDORA NEVER","OPENED A BOX",(255,200,150),"A 500-YEAR-OLD MISTRANSLATION","/mnt/user-data/outputs/orbithos_pandoras_jar_kucuk_resim.jpg",band=(40,26,34,228),label_col=(150,70,58))
