import sys; sys.path.insert(0,"/home/claude/vid72"); sys.path.insert(0,"/home/claude/toolkit")
import r72, pro, thumbstd
b,_,z=r72.sh_hook(2.0); b=pro.camera(b,1.08,0.5,0.6); b=pro.post(b,0.5,0.65); img=pro.to_img(b,0)
thumbstd.make(img,"HE LEFT THE USSR","CAME BACK: IT WAS GONE",(255,168,28),"MIR · 1991–1992","/mnt/user-data/outputs/orbithos_last_soviet_citizen_kucuk_resim.jpg",band=(60,10,12,215),label_col=(150,25,30))
