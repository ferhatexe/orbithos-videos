import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid51"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
def piano(f,dur=2.0,amp=0.03):
    tt=T_(dur); s=sum(a_*np.sin(2*np.pi*f*k*tt*(1+0.0004*k*k))*np.exp(-tt*(1.2+k*0.8)) for k,a_ in ((1,1),(2,0.4),(3,0.2),(4,0.08)))
    return lp(s*amp*np.clip(tt/0.004,0,1),4200)
def waltz(t0,t1,prog,beat=0.42,amp=0.02,mel=None):
    x=t0;k=0
    while x<t1-0.2:
        ch=prog[(k//6)%len(prog)]
        if k%3==0: add(x,piano(D(-1,ch[0]),2.0,amp))
        else: 
            for s_ in ch[1:]: add(x,piano(D(0,s_),1.0,amp*0.45))
        if mel and k%3==0: add(x+0.02,piano(D(1,mel[(k//3)%len(mel)]),2.4,amp*0.6))
        x+=beat;k+=1
P1=[[2,9,14],[7,11,14],[2,9,14],[7,11,16]]; M1=[14,16,14,11,9,7,9,11]
P2=[[0,3,7],[5,8,12],[-2,5,10],[0,3,7]]; M2=[12,10,8,7,5,7,8,10]
a,b=sec("hook"); waltz(0.0,b,P1,0.42,0.018,M1)
a,b=sec("myth"); waltz(a,EV["lid"],P1,0.42,0.018,M1); add(EV["lid"],drone(D(-2,0),b-EV["lid"]+0.3,0.02,0.3,0.6,360)); pads(EV["lid"],b,[[0,3,6],[1,4,7]],1.6,0.009)
add(EV["hope"],shimmer(0.02,1.8))
a,b=sec("jar"); waltz(a,b,[[0,4,7],[5,9,12],[7,11,14],[0,4,7]],0.42,0.017,[12,11,9,7,9,11,12,14])
a,b=sec("error"); waltz(a,EV["nexttime"],P2,0.42,0.016,M2); waltz(EV["nexttime"],TOTAL+0.2,P1,0.42,0.018,M1)
# ---------------- sfx ----------------
for s_ in SC[1:]: add(s_["s"]-0.32,whoosh(0.7,0.03,400,2600)); add(s_["s"]-0.1,chime(D(2,9),0.010,1.6))
add(TOTAL-0.6,whoosh(0.7,0.03,400,2600))
add(EV["nbox"],chime(D(2,2),0.014,1.8)); add(EV["never"],pap(0.03)); add(EV["never"]+0.2,pap(0.025))
add(EV["zeus"],boom(0.07,60,3,1.4)); add(EV["zeus"],crack(0.04)); add(EV["first"],shimmer(0.016,1.6))
for k in range(6): add(EV["gift"]+k*0.12,chime(D(2,[0,4,7,11,14,16][k]),0.009,1.4))
add(EV["sealed"],boom(0.05,110,8,0.4)); add(EV["lid"],lp(bp(noise(0.3),300,1500),1800)*np.exp(-T_(0.3)*10)*0.04)
add(EV["escaped"]-0.1,whoosh(1.6,0.05,150,1400)); add(EV["escaped"]+0.2,lp(bp(noise(1.5),80,500),600)*np.sin(np.pi*T_(1.5)/1.5)*0.05)
add(EV["hope"],chime(D(2,7),0.016,2.4))
add(EV["hesiod"],lp(bp(noise(0.6),900,4000),4500)*np.sin(np.pi*T_(0.6)/0.6)*0.02); add(EV["pithos"],boom(0.05,90,4,0.8))
add(EV["jar"],boom(0.06,70,4,0.8)); add(EV["diog"],pap(0.025))
add(EV["y1508"],bell(D(-1,0),0.02,2.6)); add(EV["pyxis"],pap(0.03)); add(EV["abox"],boom(0.04,140,10,0.3))
add(EV["five"],shimmer(0.014,1.4)); add(EV["remember"],chime(D(2,2),0.014,2.0))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
