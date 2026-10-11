import sys; sys.path.insert(0,"/home/claude/toolkit")
from r60 import *
import thumbstd
b=linen(); leg_big(b,230,585,1.1,hl=1.0); arrow(b,350,568,200,552); borders(b)
img=Image.fromarray(cv2.resize((np.clip(b,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"HOMER NEVER","MENTIONED THE HEEL",(240,190,110),"GREEK MYTH · ACHILLES","/mnt/user-data/outputs/orbithos_achilles_heel_kucuk_resim.jpg",band=(22,26,44,230),label_col=(150,50,30))
