import sys; sys.path.insert(0,"/home/claude/toolkit")
from r59 import *
import thumbstd
G=backdrop(); portrait(G,270,400,0.82,0.0); G=finish(G)
img=tone(G); buf=img*(1-CASEA[...,None])+CASE*CASEA[...,None]
pil=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
pil=pil.convert('RGBA'); plate_title(ImageDraw.Draw(pil),'PHINEAS GAGE'); pil=pil.convert('RGB')
thumbstd.make(pil,"AN IRON ROD WENT","THROUGH HIS HEAD",(240,200,120),"HISTORY · 1848","/mnt/user-data/outputs/orbithos_phineas_gage_kucuk_resim.jpg",band=(22,14,8,228),label_col=(110,70,30))
