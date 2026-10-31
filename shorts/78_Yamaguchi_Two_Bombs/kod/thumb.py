import sys; sys.path.insert(0,"/home/claude/vid78"); sys.path.insert(0,"/home/claude/toolkit")
import r78, pro, thumbstd, numpy as np
b,_,z=r78.sh_hook(1.0); b=np.clip(b,0,1.1)*(0.80+0.20*pro.VIG)*1.06; img=pro.to_img(b,0)
thumbstd.make(img,"SURVIVED TWO","ATOMIC BOMBS",(230,40,35),"HIROSHIMA · NAGASAKI · 1945","/mnt/user-data/outputs/orbithos_yamaguchi_two_bombs_kucuk_resim.jpg",band=(20,18,18,215),label_col=(160,30,25))
