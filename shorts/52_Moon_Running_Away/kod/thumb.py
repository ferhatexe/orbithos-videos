import sys; sys.path.insert(0,"/home/claude/toolkit")
from r52 import *
import thumbstd
ly=Lay(); ex,ey=160,620; earth(ly,ex,ey,90,1,1,0.5); mx,my=400,370; moon(ly,mx,my,46,1,1)
m=M(); dashl(m,(ex+70,ey-60),(mx-40,my+36),10,8,3); arrowhead(m,(mx-40,my+36),-0.75); ly.add(m,YEL,1)
ly.add(dl(M(),[(ex,ey-110),(mx-24,my+30)],1,2.5),GRN,0.0)
buf=np.clip(WALL+ly.light(),0,1.3)*VIG
img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
thumbstd.make(img,"THE MOON IS","RUNNING AWAY FROM US",(255,90,170),"+3.8 CM EVERY YEAR","/mnt/user-data/outputs/orbithos_moon_running_away_kucuk_resim.jpg",band=(14,10,24,228),label_col=(200,40,120))
