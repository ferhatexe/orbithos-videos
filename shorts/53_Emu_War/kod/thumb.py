import sys; sys.path.insert(0,"/home/claude/toolkit")
from r53 import *
import thumbstd
t=0.8; buf=region(0)
chip(buf,140,560,"hq",1.0,1.5); chip(buf,200,620,"inf",1.0,1.4); chip(buf,120,650,"mg",1.0,1.4)
herd(buf,370,560,30,t,60,1.0,-26,1,1.1)
arrow(buf,[(500,420),(400,470),(270,540),(230,560)],1.0,EMUR,1.0,18,30)
buf=np.clip(buf,0,1.2)*PT*VIG
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"ARMY VS. EMUS","THE BIRDS WON",(255,120,100),"AUSTRALIA · 1932","/mnt/user-data/outputs/orbithos_emu_war_kucuk_resim.jpg",band=(40,30,20,228),label_col=(190,40,30))
