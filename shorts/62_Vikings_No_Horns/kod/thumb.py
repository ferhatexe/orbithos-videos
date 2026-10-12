import sys; sys.path.insert(0,"/home/claude/toolkit")
from r62 import *
import thumbstd
b,s=slab(0); warrior(s,280,560,1.15,horns=1.0); carve(s,M().line((200,300),(360,420),6).line((360,300),(200,420),6),1.0,RED)
buf=finish_slab(b,s)
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"VIKINGS NEVER WORE","HORNED HELMETS",(240,120,90),"HISTORY · VIKINGS","/mnt/user-data/outputs/orbithos_viking_horns_kucuk_resim.jpg",band=(20,24,30,228),label_col=(150,40,28))
