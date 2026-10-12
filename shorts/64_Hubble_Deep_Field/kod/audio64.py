import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid64"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sc_(n): s=S(n); return s["s"],s["e"]
E=lambda o,s=0:164.81*2**o*2**(s/12)
def chalkfx(t0,dur,amp=0.006):
    tt=T_(dur); g=np.random.default_rng(int(t0*100)); env=(0.5+0.5*np.sin(2*np.pi*g.uniform(4,7)*tt))**2
    add(t0,bp(noise(dur),1500,6000)*env*np.clip(tt/0.05,0,1)*np.clip((dur-tt)/0.05,0,1)*amp)
def tap(at,amp=0.012): tt=T_(0.05); add(at,bp(noise(0.05),800,4000)*np.exp(-tt*90)*amp)
def efx(at,dur=0.6):
    tt=T_(dur); add(at,lp(bp(noise(dur),300,2500),2600)*(0.6+0.4*np.sin(2*np.pi*7*tt))*np.sin(np.pi*tt/dur)*0.012)
def pp(f,dur=1.8,amp=0.008): return kal(f,dur,amp)
CH=[[0,4,7,11],[-3,0,4,7],[5,9,12,16],[2,5,9,12]]
add(0,drone(E(-2,0),TOTAL+0.4,0.012,0.4,0.8,300))
x=0.1;k=0
while x<TOTAL-0.2:
    ch=CH[int(x/2.6)%len(CH)]; add(x,pp(E(1,ch[k%4]+(12 if (k//4)%2 else 0)),1.6,0.007)); x+=0.33;k+=1
t_=0;k=0
while t_<TOTAL:
    for s_ in CH[k%4]: add(t_,pad(E(-1,s_),3.4,0.005,0.9,1.1))
    t_+=2.6;k+=1
for key,d in (("y1995",0.6),("hubble",0.9),("patch",0.8),("empty",0.5),("pin",0.7),("arm",0.7),("dipper",1.0),("nothing",0.6),("waste",0.6),("time",0.6),("ten",1.6),("stared",0.6),("image",0.6),("galaxy",0.6),("n3000",0.5),("spirals",0.5),("blobs",0.5),("smudges",0.5),("billions",0.8),("light",1.2),("y2004",0.8),("special",0.6),("anywhere",1.4),("remember",0.5)):
    chalkfx(EV[key]-0.2,d)
tap(EV["pin"]+0.4); tap(EV["n3000"]); 
add(EV["back"],shimmer(0.014,2.0)); add(EV["back"]+0.3,bell(E(1,0),0.012,3.0))
add(EV["n342"],click(0.01,2500,400)); add(EV["deeper"],shimmer(0.012,1.6)); add(EV["n10k"],bell(E(1,7),0.012,2.5))
add(EV["waste"],cello(E(-1,1),1.4,0.010,0.1,0.8))
SH=[Lx("Near the Big")[0]-0.3,S("stare")["s"],S("reveal")["s"],Lx("Spirals")[0]-0.3,S("deeper")["s"],Lx("And that patch")[0]-0.3]
for t_ in SH: efx(t_-0.4,0.56)
efx(TOTAL-0.7,0.5)
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.85
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
