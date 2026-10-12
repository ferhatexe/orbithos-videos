import sys; sys.path.insert(0,"/home/claude/toolkit")
from r65 import *
import thumbstd
b=base(); sunburst(b,270,500,40,330,28,0.12,GOLD,0.0)
y=520; gl(b,[(50,y),(490,y)],2.5,GOLDL); pyramid(b,100,y-12,0.45); cleo(b,300,y-120,0.75); moon(b,460,y-80,38); lander(b,460,y-12,0.55)
gl(b,[(60,y+40),(300,y+40)],7,RUST); gl(b,[(300,y+70),(470,y+70)],7,TEAL)
b=b*INT+FRAME*(1-INT)
img=Image.fromarray(cv2.resize((np.clip(b,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"CLEOPATRA LIVED CLOSER","TO THE MOON LANDING",(245,214,140),"HISTORY · TIME","/mnt/user-data/outputs/orbithos_cleopatra_moon_kucuk_resim.jpg",band=(12,12,14,230),label_col=(30,90,95))
