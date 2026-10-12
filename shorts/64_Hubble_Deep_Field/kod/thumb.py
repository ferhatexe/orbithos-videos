import sys; sys.path.insert(0,"/home/claude/toolkit")
from r64 import *
import thumbstd
b=board(); box(b,70,300,470,650,1.0); galaxies(b,78,308,462,642,1.0)
stroke(b,circle_pts(300,470,40,seed=7),1.0,2.5,YEL)
img=Image.fromarray(cv2.resize((np.clip(b,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"AN \"EMPTY\" PATCH OF SKY","HELD 3,000 GALAXIES",(250,230,140),"SPACE · HUBBLE","/mnt/user-data/outputs/orbithos_hubble_deep_field_kucuk_resim.jpg",band=(10,18,14,228),label_col=(60,90,140))
