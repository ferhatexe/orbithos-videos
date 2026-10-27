import sys; sys.path.insert(0,"/home/claude/vid71"); sys.path.insert(0,"/home/claude/toolkit")
import r71, pro, thumbstd
b,_,z=r71.sh_hook(1.0); b=pro.post(b,0.5,0.65,(1.04,1.0,0.94)); img=pro.to_img(b,0)
thumbstd.make(img,"80 MILLION TREES","AND NO CRATER",(255,168,28),"SIBERIA · 1908","/mnt/user-data/outputs/orbithos_tunguska_no_crater_kucuk_resim.jpg",band=(30,16,10,215),label_col=(150,70,30))
