import sys; sys.path.insert(0,"/home/claude/vid76"); sys.path.insert(0,"/home/claude/toolkit")
import r76, pro, thumbstd
b,_,z=r76.sh_hook(2.7,close=True); b=pro.camera(b,z*0.92,0.5,0.47); b=pro.post(b,0.5,0.70,(1.03,1.0,0.95)); img=pro.to_img(b,0)
thumbstd.make(img,"NAMED AFTER","HIS WORST ENEMY",(255,168,28),"GREEK MYTH · HERACLES","/mnt/user-data/outputs/orbithos_hercules_named_after_hera_kucuk_resim.jpg",band=(30,14,30,215),label_col=(150,100,30))
