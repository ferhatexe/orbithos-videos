import sys; sys.path.insert(0,"/home/claude/toolkit")
from r61 import *
import thumbstd
b=paper(); mars_land(b,0,glow=1.2); rover(b,140,640,1.0)
b=b*(1-BANDA[...,None])+BAND*BANDA[...,None]; b=b*PTEX
img=Image.fromarray(cv2.resize((np.clip(b,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"SUNSETS ON MARS","ARE BLUE",(140,190,255),"SPACE · MARS","/mnt/user-data/outputs/orbithos_mars_blue_sunset_kucuk_resim.jpg",band=(30,24,40,225),label_col=(170,70,40))
