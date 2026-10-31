import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid78"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import master
from sfxlib import *
import r78
LINES=r78.LINES; TOTAL=r78.TOTAL; wt=r78.wt; Ls=r78.Ls; SHOTS=r78.SHOTS
init(TOTAL)
# ---- music: sparse koto-like plucks in the in-scale (D), low drone, soft taiko ----
Dk=lambda o,s=0:146.83*2**o*2**(s/12)
INS=[0,1,5,7,8,12,13,17]
def koto(f,dur=2.2,amp=0.012):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt*(1+0.0008*k))*np.exp(-tt*(2.2+k*0.9))/k**1.1 for k in range(1,7))
    s+=np.sin(2*np.pi*f*tt)*np.exp(-tt*1.2)*0.3
    return lp(s*amp*np.clip(tt/0.002,0,1),5000)
MEL=[7,5,1,0,1,5,8,7,12,8,7,5,1,0]
x=0.2;k=0
while x<TOTAL:
    add(x,koto(Dk(0,MEL[k%len(MEL)]),2.4,0.011)); x+=0.62 if k%4!=3 else 1.0; k+=1
add(0,drone(Dk(-2,0),TOTAL+0.4,0.016,0.6,0.8,260)); add(0,drone(Dk(-1,7),TOTAL+0.4,0.005,0.8,0.8,400))
def taiko(at,amp=0.07): tt=T_(0.8); add(at,lp(np.sin(2*np.pi*np.cumsum(55+30*np.exp(-tt*20))/SR)*np.exp(-tt*5)*amp,300))
for st,fn,kind in SHOTS[1:]:
    add(st-0.25,lp(bp(noise(0.5),400,3500),4000)*np.sin(np.pi*T_(0.5)/0.5)**2*0.010)   # brush swish
    taiko(st,0.05)
add(TOTAL-0.5,lp(bp(noise(0.5),400,3500),4000)*np.sin(np.pi*T_(0.5)/0.5)**2*0.010)
add(wt(1,"three")-0.6,boom(0.10,36,1.4,3.5)); add(wt(3,"Nagasaki")-0.1,boom(0.10,36,1.4,3.5))
add(wt(4,"survived"),bell(Dk(0,0),0.012,3.5)); add(wt(5,"officially"),taiko(wt(5,"officially")+0.0,0.06) or np.zeros(1))
bus=lp(out(),9500); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 2.05
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
