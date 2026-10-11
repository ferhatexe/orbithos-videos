import sys; sys.path.insert(0,"/home/claude/toolkit")
from r54 import *
import r54 as RR
import thumbstd
t=1.0; pr=Proj(); titan(pr,270,700,0.95,1.0,1.0,GOLDP); cel_sphere(pr,270,700-245*0.95-66,74,t,1.0,1.0)
buf=DOME+pr.render(); buf=buf*(1-RR._aA)+np.array((0.01,0.01,0.02),np.float32)*RR._aA
buf=np.clip(buf,0,1.3)*DOMEV
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"ATLAS NEVER","CARRIED THE EARTH",(255,190,170),"GREEK MYTH · THE SKY","/mnt/user-data/outputs/orbithos_atlas_sky_kucuk_resim.jpg",band=(8,12,34,228),label_col=(150,110,40))
