import sys; sys.path.insert(0,"/home/claude/toolkit")
from r68 import *
import thumbstd
img=CORK.copy(); paste(img,P_SKY,560,880,-4,1.15); paste(img,sticky("MEAT?!"),300,1180,-8,1.0,pin_col=(240,200,40))
thumbstd.make(img.convert("RGB"),"IT RAINED MEAT","IN KENTUCKY, 1876",(255,120,100),"HISTORY · MYSTERY","/mnt/user-data/outputs/orbithos_kentucky_meat_shower_kucuk_resim.jpg",band=(30,18,10,228),label_col=(160,40,30))
