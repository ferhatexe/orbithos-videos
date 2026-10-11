import sys; sys.path.insert(0,"/home/claude/toolkit")
from r55 import *
import thumbstd
buf,hud=render_scene(1.2,B.SC[0])
buf=np.clip(buf,0,1.2)*VIG*SCAN
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"IT SURVIVED","NAKED IN SPACE",(255,190,120),"SCIENCE · TARDIGRADES","/mnt/user-data/outputs/orbithos_tardigrades_space_kucuk_resim.jpg",band=(10,10,12,228),label_col=(150,100,40))
