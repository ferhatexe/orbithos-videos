import sys; sys.path.insert(0,"/home/claude/toolkit")
from r66 import *
import thumbstd
b=page(); panel(b,PX0,PY0,PX1,PY1,"burst"); cerberus(b,230,640,1.05,50,0.3)
img=Image.fromarray(cv2.resize((np.clip(b,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"CERBERUS ONCE HAD","FIFTY HEADS",(255,220,80),"GREEK MYTH · CERBERUS","/mnt/user-data/outputs/orbithos_cerberus_fifty_heads_kucuk_resim.jpg",band=(20,14,18,230),label_col=(190,40,30))
