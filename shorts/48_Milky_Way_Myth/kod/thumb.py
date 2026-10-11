import sys; sys.path.insert(0,"/home/claude/toolkit")
from r48 import *
import thumbstd
buf=flow(vortex(GAL,270,430,0.6,140),0.3,2.5)
buf=np.clip(buf,0,1.2)*PT*VIG
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"EVERY GALAXY IS","NAMED AFTER SPILLED MILK",(255,214,120),"GREEK MYTH · HERA & HERACLES","/mnt/user-data/outputs/orbithos_milky_way_myth_kucuk_resim.jpg",band=(10,16,46,228),label_col=(160,58,38))
