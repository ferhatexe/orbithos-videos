import sys; sys.path.insert(0,"/home/claude/vid77"); sys.path.insert(0,"/home/claude/toolkit")
import r77, pro, thumbstd
b,_,z=r77.sh_hook(1.0); b=pro.camera(b,1.05,0.5,0.55); b=pro.post(b,0.5,0.65,(0.96,1.0,1.05)); img=pro.to_img(b,0)
thumbstd.make(img,"HIS SALIVA BOILED","IN A VACUUM",(255,168,28),"NASA · HOUSTON · 1966","/mnt/user-data/outputs/orbithos_vacuum_saliva_boiled_kucuk_resim.jpg",band=(10,16,30,215),label_col=(40,70,140))
