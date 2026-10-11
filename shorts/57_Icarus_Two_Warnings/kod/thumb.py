import sys; sys.path.insert(0,"/home/claude/toolkit")
from r57 import *
import thumbstd
t=1.3; st=Stage(); sea(st,t,555); sun(st,370,395,72,t)
st.sil(flyer(200,470,1.05,0.15,1,tilt=-0.30,lost=0),0.8)
for i,(x,y,a) in enumerate(((300,500,0.6),(330,530,1.9),(270,520,2.6))): fm=M(); feather(fm,x,y,0.75,a); st.sil(fm,0.9)
buf=st.render(t); buf=buf*(1-FA[...,None])*(1-FSH[...,None])+FR*FA[...,None]
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"HE WAS ALSO WARNED","NOT TO FLY TOO LOW",(240,200,115),"GREEK MYTH · ICARUS","/mnt/user-data/outputs/orbithos_icarus_two_warnings_kucuk_resim.jpg",band=(30,12,8,228),label_col=(120,20,20))
