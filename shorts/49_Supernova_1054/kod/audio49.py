import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid49"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
PENT=[0,2,4,7,9]
def guzheng(f,dur=2.2,amp=0.03):
    tt=T_(dur); bend=1+0.012*np.exp(-tt*6)
    s=sum(a_*np.sin(2*np.pi*f*k*np.cumsum(bend)/SR*SR/SR) for k,a_ in ((1,1),(2,0.5),(3,0.25),(4,0.1)))
    s=sum(a_*np.sin(2*np.pi*f*k*tt*(1+0.004*np.exp(-tt*5))) for k,a_ in ((1,1),(2,0.45),(3,0.22),(4,0.1)))*np.exp(-tt*2.2)
    return lp(s*amp*np.clip(tt/0.003,0,1),4200)
def zheng_line(t0,t1,step=0.36,amp=0.022,oct_=0,seed=1):
    g=np.random.default_rng(seed); x=t0; k=0
    while x<t1-0.3:
        s_=PENT[g.integers(0,5)]+12*g.integers(0,2); add(x,guzheng(D(oct_,s_),2.0,amp))
        if g.random()<0.25: add(x+step*0.5,guzheng(D(oct_,PENT[g.integers(0,5)]+12),1.4,amp*0.6))
        x+=step*(1 if g.random()<0.7 else 2); k+=1
def gong(at,amp=0.05,f=110):
    tt=T_(4.0); s=sum(a_*np.sin(2*np.pi*f*r*tt*(1+0.002*np.sin(2*np.pi*3*tt)))*np.exp(-tt*d) for a_,r,d in ((1,1,0.7),(0.6,1.48,1.0),(0.4,2.1,1.3),(0.3,2.9,1.8)))
    add(at,lp(s*amp*np.clip(tt/0.01,0,1),3000))
a,b=sec("hook"); add(0,drone(D(-2,0),b+0.4,0.02,0.2,1.0,360)); zheng_line(0.0,b,0.36,0.020,0,1); pads(0.0,b,[[0,7,14]],3.6,0.007)
a,b=sec("record"); zheng_line(a,EV["southwest"],0.40,0.022,0,2); add(a,drone(D(-2,0),EV["southwest"]-a,0.016,0.6,0.6,360))
pads(EV["southwest"]-0.2,b,[[-3,4,9]],2.8,0.008)
a,b=sec("boom"); add(a,drone(D(-3,0),b-a,0.03,0.4,0.8,260)); pads(EV["weeks"],b,[[0,4,7],[2,7,11]],2.4,0.008)
a,b=sec("crab"); zheng_line(a,TOTAL+0.2,0.36,0.018,0,4); pads(a,TOTAL+0.2,[[0,7,14],[-3,4,9]],2.8,0.008)
# ---------------- sfx ----------------
for s_ in SC[1:]: add(s_["s"]-0.32,whoosh(0.7,0.03,300,1800)); add(s_["s"]-0.32,lp(bp(rng.normal(0,1,int(0.6*SR)),400,3000),3500)*np.sin(np.pi*T_(0.6)/0.6)*0.012)
add(TOTAL-0.6,whoosh(0.7,0.03,300,1800))
gong(0.1,0.035,98); add(EV["blazed"],shimmer(0.016,1.6)); add(EV["spinning"],chime(D(2,7),0.012,1.6))
gong(EV["july"],0.03,110); add(EV["guest"],shimmer(0.014,1.4)); add(EV["venus"],chime(D(2,4),0.012,2.0))
for k in range(23): add(EV["days23"]+k*(1.2/23),click(0.025,1600,260))
add(EV["night"],pad(D(-1,9),2.0,0.008,0.3,1.0)); add(EV["disappears"],whoosh(1.0,0.02,2500,400))
add(EV["painted"],lp(bp(noise(0.8),300,1500),1800)*np.sin(np.pi*T_(0.8)/0.8)*0.02)
add(EV["supernova"],boom(0.07,60,2,2.0)); add(EV["exploding"]-0.2,whoosh(0.6,0.04,200,3000)); add(EV["exploding"],boom(0.13,36,1.0,3.5)); add(EV["exploding"],crack(0.05))
add(EV["outshine"],shimmer(0.018,1.6)); add(EV["years"],whoosh(2.0,0.025,300,1200)); add(EV["earth"],chime(D(2,0),0.012,2.0))
gong(EV["crab"],0.03,82)
x=EV["spins"]
while x<EV["first"]: add(x,beep(1200,0.012,0.006)); x+=1/15
add(EV["lighthouse"],chime(D(2,9),0.012,2.0)); add(EV["thousand"],gong(EV["thousand"],0.025,98) or np.zeros(1))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
