import sys; sys.path.insert(0,"/home/claude/toolkit")
from r47 import *
import thumbstd
t=3.9; buf,_=s_hook(t,B.S("hook")); buf=paintify(buf)
buf=np.clip(buf,0,1.2)*PT*VIG
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"IT SNOWED IN JUNE","…AND CREATED FRANKENSTEIN",(214,236,190),"1816 · THE YEAR WITHOUT A SUMMER","/mnt/user-data/outputs/orbithos_year_without_summer_kucuk_resim.jpg",band=(18,22,30,228),label_col=(150,40,22))
