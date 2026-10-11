import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid46"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
def vib(f,dur=1.4,amp=0.03):
    """vibraphone"""
    tt=T_(dur); trem=1+0.25*np.sin(2*np.pi*5.5*tt)
    s=(np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*6))*np.exp(-tt*1.8)*trem
    return lp(s*amp*np.clip(tt/0.004,0,1),5000)
def walkbass(t0,t1,roots,step=0.42,amp=0.05):
    x=t0;k=0; pat=[0,4,7,9]
    while x<t1-0.2:
        r=roots[(k//8)%len(roots)]; f=D(-2,r+pat[k%4]); tt=T_(0.4)
        add(x,lp(np.sin(2*np.pi*f*tt)*np.exp(-tt*5)*amp*np.clip(tt/0.01,0,1),600)); x+=step; k+=1
def brush(t0,t1,step=0.42,amp=0.012):
    x=t0;k=0
    while x<t1-0.1:
        tt=T_(0.18); add(x+step/2,bp(rng.normal(0,1,len(tt)),2000,8000)*np.exp(-tt*20)*amp*(1.4 if k%2 else 0.8)); x+=step; k+=1
def lounge(t0,t1,chords,cl=1.68,amp=0.016):
    x=t0;k=0
    while x<t1-0.3:
        for j,s_ in enumerate(chords[k%len(chords)]): add(x+j*0.03,vib(D(0,s_),1.6,amp*0.6))
        add(x+cl*0.5,vib(D(1,chords[k%len(chords)][k%3]),1.0,amp*0.4)); x+=cl; k+=1
CH=[[0,4,7,11],[-3,0,4,7],[2,5,9,12],[-5,-1,2,5]]
a,b=sec("hook"); add(0,drone(D(-2,0),2.0,0.02,0.1,1.0,500)); lounge(1.0,b,CH,1.68,0.014)
a,b=sec("strike"); lounge(a,EV["across"],CH,1.68,0.016); walkbass(a,EV["across"],[0,-3,2,-5],0.42,0.04); brush(a,EV["across"])
add(EV["across"],drone(D(-2,-1),EV["wakes"]-EV["across"],0.024,0.5,0.4,420)); add(EV["across"],pad(D(-1,1),EV["stone"]-EV["across"],0.010,0.5,0.4))
lounge(EV["wakes"],b,[[0,4,7,11],[5,9,12,16]],1.68,0.014)
a,b=sec("fight"); lounge(a,b,[[0,3,7,10],[5,8,12,15],[-2,2,5,9]],1.68,0.014); walkbass(a,b,[0,5,-2],0.42,0.045); brush(a,b)
a,b=sec("end"); lounge(a,TOTAL+0.2,CH,1.68,0.015); walkbass(a,EV["allb"],[0,-3,2,-5],0.42,0.04); brush(a,EV["allb"])
# ---------------- sfx ----------------
for s_ in SC[1:]: add(s_["s"]-0.3,whoosh(0.6,0.03,400,2500)); add(s_["s"]-0.05,chime(D(2,7),0.012,1.4))
add(TOTAL-0.6,whoosh(0.6,0.03,400,2500)); add(TOTAL-0.35,chime(D(2,7),0.012,1.4))
add(-0.3,whoosh(1.3,0.05,300,2400)); add(TOTAL-0.3,whoosh(1.3,0.05,300,2400))
add(0.95,boom(0.11,55,3,1.4)); add(0.95,crack(0.06)); add(0.20,crack(0.04))
add(EV["survived"],chime(D(2,0),0.016,2.0)); add(EV["strangest"],vib(D(0,1),1.8,0.03))
add(EV["nov"],pap(0.03)); add(EV["syl"],vib(D(1,4),1.2,0.02))
for k in range(3): add(EV["napping"]+k*0.5,lp(bp(noise(0.4),200,900),1000)*np.sin(np.pi*T_(0.4)/0.4)*0.008)
add(EV["fireball"]-0.4,whoosh(1.6,0.05,200,2200)); add(EV["boom"],boom(0.11,45,1.5,2.5))
add(EV["stone"],whoosh(0.9,0.04,500,2500)); add(EV["ceiling"],crack(0.06)); add(EV["ceiling"],boom(0.08,90,6,0.5))
add(EV["radio"],crack(0.04)); tt=T_(0.6); add(EV["radio"]+0.05,bp(rng.normal(0,1,len(tt)),800,4000)*np.exp(-tt*5)*0.015)
add(EV["hip"],boom(0.12,70,6,0.6)); add(EV["bruise"],vib(D(0,-1),1.5,0.025))
add(EV["officials"],pap(0.03)); add(EV["airforce"],whoosh(1.6,0.05,200,3000))
add(EV["sues"],gavel(0.16)); add(EV["landowner"],pap(0.02))
for k in range(6): add(EV["public"]+k*0.12,lp(bp(noise(0.5),300,2500),2800)*np.sin(np.pi*T_(0.5)/0.5)*0.012)
add(EV["keeps"],chime(D(2,4),0.018,2.2))
add(EV["farmer"],pap(0.025)); add(EV["sold"],chime(D(3,0),0.016,1.2)); add(EV["sold"]+0.06,chime(D(3,4),0.014,1.2))
add(EV["car"],beep(440,0.12,0.012)); add(EV["car"]+0.18,beep(440,0.12,0.012))
add(EV["doorstop"],lp(bp(noise(0.25),100,800),900)*np.exp(-T_(0.25)*14)*0.08)
add(EV["museum"],shimmer(0.016,1.4)); add(EV["quiet"],vib(D(0,7),1.6,0.02))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
