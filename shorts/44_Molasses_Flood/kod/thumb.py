import sys; sys.path.insert(0,"/home/claude/toolkit")
from r44 import *
import thumbstd
buf=PAGE.copy(); t=1.2
railway(buf,GY+60,GY-170,a=1.0); city(buf,GY+60,1.0,crush=lambda x: cl((300-x)/50),t=t); molwave(buf,280,GY+60,320,t)
ink(buf,M().rect(14,GY+60,w-14,GY+63),1.0)
buf=np.clip(buf,0,1.2)*PT*VIG
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"MOLASSES WAVE","KILLED 21 PEOPLE",(255,190,110),"BOSTON · JANUARY 1919","/mnt/user-data/outputs/orbithos_molasses_flood_kucuk_resim.jpg",band=(40,20,8,228),label_col=(110,48,16))
