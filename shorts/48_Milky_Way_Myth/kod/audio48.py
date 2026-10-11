import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid48"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
def harp(t0,t1,chords,step=0.18,amp=0.012,cl=2.6):
    x=t0;k=0
    while x<t1-0.2:
        ch=chords[int((x-t0)/cl)%len(chords)]; s_=ch[k%len(ch)]+(12 if (k//len(ch))%2 else 0)
        add(x,kal(D(0,s_),1.8,amp)); x+=step;k+=1
def ney(f,dur,amp=0.012):
    tt=T_(dur); vib=1+0.006*np.sin(2*np.pi*5*tt)*np.clip((tt-0.3)/0.5,0,1)
    s=np.sin(2*np.pi*np.cumsum(f*vib)/SR)+0.3*np.sin(2*np.pi*2*np.cumsum(f*vib)/SR)
    br=bp(rng.normal(0,1,len(tt)),f*0.8,f*3)*0.25
    return lp((s+br)*np.clip(tt/0.25,0,1)*np.clip((dur-tt)/0.4,0,1)*amp,3500)
def drip(at,amp=0.02,f0=900):
    add(at,plip(amp,f0,f0*1.9))
H=[[0,4,7],[-3,0,4],[-7,-3,0],[-5,-1,2]]
a,b=sec("hook"); add(0,drone(D(-2,0),b+0.4,0.02,0.2,1.0,380)); harp(0,b,H,0.2,0.010)
for k,(s_,d_) in enumerate(((7,1.6),(9,1.0),(7,1.2),(4,2.0))): add(0.3+sum(x[1] for x in ((7,1.6),(9,1.0),(7,1.2),(4,2.0))[:k]),ney(D(1,s_),d_+0.2,0.010))
a,b=sec("birth"); harp(a,EV["placed"],[[0,4,7],[5,9,12],[7,11,14],[0,4,7]],0.2,0.011); add(a,drone(D(-2,0),EV["placed"]-a,0.016,0.5,0.6,380))
pads(EV["placed"]-0.2,b,[[-3,0,4],[-5,-1,2]],2.6,0.008); harp(EV["placed"],b,[[-3,0,4],[-5,-1,2]],0.32,0.008)
a,b=sec("spill"); add(a,drone(D(-2,-3),EV["pushed"]-a,0.02,0.3,0.4,380)); pads(EV["pushed"],b,[[0,4,7,11],[5,9,12,16]],2.4,0.009); harp(EV["pushed"],b,[[0,4,7,11],[5,9,12,16]],0.15,0.010,2.4)
a,b=sec("word"); pads(a,TOTAL+0.2,H,2.6,0.008); harp(a,TOTAL+0.1,H,0.2,0.010)
x=EV["kyklos"]
for k,(s_,d_) in enumerate(((0,1.0),(4,1.0),(7,1.6),(12,2.2))): add(EV["greeks"]+k*1.1,ney(D(1,s_),d_,0.009))
# ---------------- sfx ----------------
for s_ in SC[1:]:
    b_=s_["s"]; add(b_-0.33,whoosh(0.8,0.03,200,1400)); 
    for k in range(4): drip(b_-0.2+k*0.08,0.010,700+k*150)
add(TOTAL-0.6,whoosh(0.8,0.03,200,1400))
add(EV["spilled"],drip(EV["spilled"],0.03,800) or np.zeros(1)); add(EV["goddess"]+0.6,plip(0.03,600,1200)); add(EV["how"],chime(D(2,4),0.014,2.0))
add(EV["zeus"],boom(0.06,60,3,1.2)); add(EV["zeus"]+0.1,crack(0.03)); add(EV["heracles"],chime(D(2,0),0.016,2.2)); add(EV["glory"],chime(D(2,7),0.012,2.0))
add(EV["immortal"],shimmer(0.016,1.4)); drip(EV["divine"],0.03,700)
add(EV["woke"],boom(0.05,90,6,0.6)); add(EV["notchild"],cello(D(-1,1),1.2,0.012,0.1,0.6))
add(EV["pushed"],whoosh(0.6,0.025,500,2000))
for k in range(36): drip(EV["sprayed"]-0.2+k*1.6/36,0.010,900+k*20)
add(EV["stars"],shimmer(0.018,1.6)); add(EV["river"],chime(D(2,9),0.012,2.4))
add(EV["tintoretto"],pap(0.025)); add(EV["rubens"],pap(0.025))
add(EV["greeks"],bell(D(-1,0),0.016,2.6)); add(EV["romans"],bell(D(-1,5),0.016,2.6))
for k in range(12): add(EV["astro"]+k*0.12,chime(D(2,[0,4,7,11,14,12,7,4,0,7,11,14][k]),0.008,1.6))
add(EV["billions"],shimmer(0.016,1.6))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
