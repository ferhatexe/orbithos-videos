import sys; sys.path.insert(0,"/home/claude/toolkit")
from r67 import *
import thumbstd
b=sky(); stars(b)
for k in (0,1): nstar(b,270+math.cos(k*math.pi+0.4)*70,420+math.sin(k*math.pi+0.4)*25,13)
glow(b,270,420,60,(1.0,0.7,0.4),0.6); ring(b,270,600,1.15,0.4)
img=pointil(np.clip(b,0,1)); pil=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8))
thumbstd.make(pil,"YOUR GOLD CAME FROM","COLLIDING DEAD STARS",(255,215,90),"SPACE · KILONOVA","/mnt/user-data/outputs/orbithos_gold_from_neutron_stars_kucuk_resim.jpg",band=(10,10,30,228),label_col=(150,100,20))
