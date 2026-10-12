import sys; sys.path.insert(0,"/home/claude/toolkit")
from r69 import *
import thumbstd
b=MIRROR.copy(); m=M(); medusa(m,CX,CY+150,0.85,0.3); engrave(b,m.f()); m2=M(); horse(m2,CX-20,CY+40,1.05,1,wing=1.0,t=0.3); engrave(b,m2.f())
Mz=np.float32([[1,0,0],[0,1,80]]); b=cv2.warpAffine(b,Mz,(w,h),borderMode=cv2.BORDER_REFLECT)
img=Image.fromarray(cv2.resize((np.clip(b,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"PEGASUS WAS BORN","FROM MEDUSA'S NECK",(240,205,140),"GREEK MYTH · MEDUSA","/mnt/user-data/outputs/orbithos_medusa_pegasus_kucuk_resim.jpg",band=(10,18,20,230),label_col=(40,90,80))
