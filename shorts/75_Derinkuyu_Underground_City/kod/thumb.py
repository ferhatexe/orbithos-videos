import sys; sys.path.insert(0,"/home/claude/vid75"); sys.path.insert(0,"/home/claude/toolkit")
import r75, pro, thumbstd
b,M=r75.cutview(0.3,790,770,0.62,r75.RV(0.3)); b=pro.post(b,0.5,0.62,(1.04,0.99,0.92)); img=pro.to_img(b,0)
thumbstd.make(img,"HE BROKE A WALL","FOUND A LOST CITY",(255,168,28),"DERINKUYU · 1963","/mnt/user-data/outputs/orbithos_derinkuyu_underground_city_kucuk_resim.jpg",band=(30,16,6,215),label_col=(170,90,20))
