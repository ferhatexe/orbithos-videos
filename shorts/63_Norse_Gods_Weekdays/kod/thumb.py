import sys; sys.path.insert(0,"/home/claude/toolkit")
from r63 import *
import thumbstd
b=base(0,norse_k=[0,0,1,1,1,1,0],hl=[0,0,1,1,1,1,0],hand_ang=med_ang(4))
Mz=np.float32([[1,0,0],[0,1,110]]); b=cv2.warpAffine(b,Mz,(w,h),borderMode=cv2.BORDER_CONSTANT,borderValue=NAVY)
img=Image.fromarray(cv2.resize((np.clip(b,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"YOU SAY 4 NORSE GODS","EVERY SINGLE WEEK",(242,204,120),"MYTHOLOGY · WEEKDAYS","/mnt/user-data/outputs/orbithos_norse_weekdays_kucuk_resim.jpg",band=(10,14,34,228),label_col=(130,30,30))
