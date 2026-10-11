import sys; sys.path.insert(0,"/home/claude/toolkit")
from r40 import *
import thumbstd
t=3.0; buf=np.zeros((h,w,3),np.float32)
vase_bg(buf,t)
# shift the frieze down a bit for thumbnail framing: draw content in the panel
rock(buf,-20,150,280)
man(buf,230,PY1-10,1.25,face=1,kneel=True,arms_up=True)
ch=M()
for k in range(7): ch.ell(150+k*10,PY1-232+k*2,4,3)
comp(buf,ch,AWH,sh=0,rim=0)
eagle(buf,400,PY1-265,0.9,0.15)
liver(buf,252,PY1-145,0.24,ARED)
comp(buf,M().circ(470,PY0+60,26),ARED,sh=0,rim=0)
buf=np.clip(buf,0,1.2)*PT*VIG+GR[0]
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"AN EAGLE ATE HIS LIVER","EVERY DAY — IT GREW BACK",(240,150,80),"PROMETHEUS · GREEK MYTH","/mnt/user-data/outputs/orbithos_prometheus_kucuk_resim.jpg",band=(14,10,8,225),label_col=(140,35,28))
