import sys; sys.path.insert(0,"/home/claude/vid74"); sys.path.insert(0,"/home/claude/toolkit")
import r74, pro, thumbstd
# dedicated thumbnail composition: Saturn V climbing, bolt striking the nose (below the title band)
b=r74.storm_sky(2.0,top=(0.07,0.08,0.11),bot=(0.26,0.28,0.33),flash=0.3)
x,y,s,ang=400,840,6.0,8
r74.flame(b,x,y,s,ang,60,1.0,1.0,9); r74.rocket(b,x,y,s,ang,60,1.0,0.25)
nx,ny=r74.axis_pt(x,y,s,ang,60,1); r74.bolt(b,11,(60,330),(nx,ny),1.1,8,3)
tx,ty=r74.axis_pt(x,y,s,ang,60,117); r74.bolt(b,12,(tx,ty),(120,1300),0.8,5,2)
r74.rain(b,1.0,0.14)
b=pro.post(b,0.5,0.70,(0.98,1.0,1.04)); img=pro.to_img(b,0)
thumbstd.make(img,"HIT BY LIGHTNING","TWICE AFTER LIFTOFF",(255,206,60),"APOLLO 12 · NOV 14, 1969","/mnt/user-data/outputs/orbithos_apollo12_lightning_kucuk_resim.jpg",band=(10,14,30,215),label_col=(40,70,150))
