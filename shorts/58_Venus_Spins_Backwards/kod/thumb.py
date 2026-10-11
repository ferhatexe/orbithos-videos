import sys; sys.path.insert(0,"/home/claude/toolkit")
from r58 import *
import thumbstd
b,_=s_hook(5.0); b=np.clip(b,0,1.1)*GRAIN
img=Image.fromarray(cv2.resize((np.clip(b,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
d=ImageDraw.Draw(img); tag(d,"WEST",220,880,44)
thumbstd.make(img.convert("RGB"),"ON VENUS THE SUN","RISES IN THE WEST",(255,196,120),"SPACE · VENUS","/mnt/user-data/outputs/orbithos_venus_backwards_kucuk_resim.jpg",band=(16,28,52,230),label_col=(196,52,36))
