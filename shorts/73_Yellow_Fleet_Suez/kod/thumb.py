import sys; sys.path.insert(0,"/home/claude/vid73"); sys.path.insert(0,"/home/claude/toolkit")
import r73, pro, thumbstd
b,_,z=r73.sh_yellow(r73.Ls(4)+3.5); b=pro.post(b,0.45,0.68,(1.03,1.0,0.95)); img=pro.to_img(b,0)
thumbstd.make(img,"15 SHIPS TRAPPED","FOR 8 YEARS",(255,206,60),"SUEZ CANAL · 1967–1975","/mnt/user-data/outputs/orbithos_yellow_fleet_suez_kucuk_resim.jpg",band=(40,28,10,215),label_col=(160,110,20))
