import sys; sys.path.insert(0,"/home/claude/vid70"); sys.path.insert(0,"/home/claude/toolkit")
import r70, pro, thumbstd
b,_,z=r70.sh_hook(1.2,1); b=pro.camera(b,1.05,0.5,0.6); b=pro.post(b,0.6,0.6); img=pro.to_img(b,0)
thumbstd.make(img,"IT RAINS GLASS","SIDEWAYS",(255,168,28),"HD 189733 b · 64 LIGHT-YEARS","/mnt/user-data/outputs/orbithos_glass_rain_planet_kucuk_resim.jpg",band=(8,14,40,215),label_col=(30,70,160))
