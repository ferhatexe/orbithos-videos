import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid47"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
def strings(t0,t1,prog,step,amp=0.012,oct_=-1):
    x=t0;k=0
    while x<t1-0.4:
        for s_ in prog[k%len(prog)]: add(x,cello(D(oct_,s_),min(step+0.9,t1-x+0.6),amp,0.5,0.8))
        x+=step;k+=1
def harpsi(f,dur=0.9,amp=0.02):
    tt=T_(dur); s=sum(np.sign(np.sin(2*np.pi*f*k*tt))/k**1.6 for k in (1,2,3))*np.exp(-tt*5)
    return lp(s*amp*np.clip(tt/0.002,0,1),3800)
def arp_h(t0,t1,chords,step=0.2,amp=0.010,cl=2.4):
    x=t0;k=0
    while x<t1-0.2:
        ch=chords[int((x-t0)/cl)%len(chords)]; add(x,harpsi(D(1,ch[k%len(ch)]+(12 if (k//3)%2 else 0)),0.7,amp)); x+=step;k+=1
def wind(t0,t1,amp=0.02):
    d=t1-t0; tt=T_(d); x=bp(rng.normal(0,1,len(tt)),300,1500)*(0.6+0.4*np.sin(2*np.pi*0.23*tt)+0.2*np.sin(2*np.pi*0.61*tt))
    add(t0,x*np.clip(tt/0.8,0,1)*np.clip((d-tt)/0.8,0,1)*amp)
def thunder(at,amp=0.12):
    add(at,crack(amp*0.5)); add(at+0.05,boom(amp,40,1.0,3.0)); add(at,lp(rng.normal(0,1,int(2.5*SR)),300)*np.exp(-T_(2.5)*1.4)*amp*2)
Dm=[[0,3,7],[-4,0,3],[-2,2,5],[-5,-2,2]]
a,b=sec("hook"); strings(0,b,Dm,2.6,0.012); wind(0,b+0.3,0.018); arp_h(0.0,b,Dm,0.22,0.008,2.6)
thunder(EV["frank"]-0.05,0.10)
a,b=sec("erupt"); add(a,drone(D(-3,0),b-a,0.03,0.5,0.8,260)); strings(a,b,[[0,3,7],[1,5,8]],2.4,0.012)
a,b=sec("cold"); strings(a,EV["sunsets"],[[0,3,7],[-4,0,3]],2.6,0.012); wind(a,EV["sunsets"]+0.4,0.022); arp_h(a,EV["sunsets"],[[0,3,7],[-4,0,3]],0.24,0.008,2.6)
strings(EV["sunsets"]-0.2,b,[[3,7,10],[5,8,12]],1.4,0.012)
a,b=sec("villa"); wind(a,EV["byron"]+0.3,0.025)
for x in np.arange(a,EV["byron"],0.02): pass
add(a,lp(bp(rng.normal(0,1,int((EV["byron"]-a+0.3)*SR)),1500,6000),7000)*0.010)
strings(a,TOTAL+0.2,[[0,3,7],[-4,0,3],[-2,2,5],[-5,-2,2]],2.4,0.011); arp_h(EV["byron"],EV["avol"],[[0,3,7],[-4,0,3],[-2,2,5]],0.2,0.009,2.4)
# ---------------- sfx ----------------
for s_ in SC[1:]: add(s_["s"]-0.32,whoosh(0.7,0.035,300,2400)); add(s_["s"]-0.25,lp(bp(rng.normal(0,1,int(0.5*SR)),1500,6000),7000)*np.sin(np.pi*T_(0.5)/0.5)*0.012)
add(TOTAL-0.6,whoosh(0.7,0.035,300,2400))
add(EV["y1816"],bell(D(-1,0),0.02,3.0)); add(EV["how"],boom(0.05,60,4,1.0)); add(EV["monster"],cello(D(-2,1),1.4,0.02,0.1,0.8))
add(EV["april"],pap(0.025)); add(EV["tambora"],boom(0.06,40,1.2,3.0))
add(EV["explodes"]-0.05,boom(0.11,32,0.8,4.5)); add(EV["explodes"],crack(0.07)); add(EV["explodes"]+0.1,whoosh(2.5,0.05,100,900))
for k in range(5): add(EV["explodes"]+0.6+k*0.7,boom(0.04,50,4,0.8))
thunder(EV["recorded"],0.06); add(EV["tens"],bell(D(-1,-4),0.02,3.0))
add(EV["ash"],whoosh(2.0,0.035,150,800)); add(EV["dims"],cello(D(-1,0),2.0,0.015,0.3,1.0))
add(EV["snows"],chime(D(2,3),0.012,2.0)); add(EV["frost"],crack(0.025)); add(EV["europe"],cello(D(-2,-4),1.8,0.016,0.2,1.0))
add(EV["froze"],bell(D(-1,-2),0.018,2.8)); add(EV["red"],shimmer(0.014,1.6))
thunder(EV["storms"],0.09); thunder(EV["villa"]+0.6,0.06)
add(EV["byron"],pap(0.025)); add(EV["ghost"],chime(D(2,6),0.012,2.4))
for k in range(5): add(EV["mary"]+0.3+k*0.18,lp(bp(rng.normal(0,1,int(0.12*SR)),2500,6000),7000)*np.exp(-T_(0.12)*25)*0.010)
add(EV["builds"],thunder(EV["builds"],0.08) or np.zeros(1))
add(EV["vampire"],whoosh(0.6,0.02,800,3000)); add(EV["vampire"]+0.1,cello(D(-1,1),1.6,0.014,0.1,0.8))
add(EV["avol"],boom(0.10,36,1.0,3.5)); add(EV["themonster"],bell(D(-1,0),0.02,2.5))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
