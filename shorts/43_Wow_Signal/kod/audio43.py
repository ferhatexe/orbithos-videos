import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid43"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
Dm=[[0,3,7,10],[-2,2,5,9],[-4,0,3,7],[-5,-1,2,5]]
def sarp(t0,t1,chords,step=0.15,amp=0.010,oct_=1,cl=2.4,cut=2200):
    x=t0;k=0
    while x<t1-0.15:
        ch=chords[int((x-t0)/cl)%len(chords)]; s_=ch[k%len(ch)]+(12 if (k//len(ch))%2 else 0)
        tt=T_(0.35); add(x,saw(D(oct_,s_),0.35,amp,0.004,0.3,cut)*np.exp(-tt*7)); x+=step; k+=1
def spads(t0,t1,chords,cl=2.4,amp=0.008):
    x=t0;k=0
    while x<t1-0.3:
        for s_ in chords[k%len(chords)]: add(x,saw(D(-1,s_),min(cl+0.8,t1-x+0.4),amp,0.6,0.8,900))
        x+=cl;k+=1
def tone(f0,dur,amp,bend=0.0):
    tt=T_(dur); f=f0*(1+bend*tt/dur); return np.sin(2*np.pi*np.cumsum(f)/SR)*amp
# ---------------- music ----------------
a,b=sec("hook"); add(a,drone(D(-2,0),b-a+0.5,0.026,0.3,1.0,420)); add(0,static(b+0.3,0.006))
sarp(0.0,b,Dm[:2],0.15,0.007,1,2.6,1800)
a,b=sec("print"); add(a,drone(D(-2,0),b-a,0.020,1.0,1.0,400)); spads(a,b,Dm,2.6,0.006); sarp(a+0.1,b,Dm,0.15,0.009,1,2.6)
a,b=sec("search"); add(a,drone(D(-2,-2),b-a,0.022,0.8,1.0,400)); spads(a,b,[[-2,2,5,9],[-4,0,3,7]],2.6,0.006); sarp(a,b,[[-2,2,5,9],[-4,0,3,7]],0.15,0.008,1,2.6)
a,b=sec("answer"); add(a,drone(D(-2,-4),EV["bigear2"]-a,0.022,0.8,1.0,400)); spads(a,EV["sheet"],[[-4,0,3,7],[-5,-1,2,5],[0,3,7,10]],2.6,0.006)
sarp(EV["cloud"],EV["hypo"],[[-4,0,3,7],[-5,-1,2,5]],0.15,0.009,1,2.6); sarp(EV["bigear2"],EV["sheet"],Dm[2:],0.3,0.008,1,2.6)
spads(EV["sheet"]-0.2,TOTAL+0.3,[[0,3,7,10]],3.0,0.007); sarp(EV["sheet"],TOTAL+0.1,Dm[:2],0.15,0.007,1,2.6,1800); add(EV["sheet"],drone(D(-2,0),TOTAL-EV["sheet"]+0.6,0.022,0.8,0.2,420))
# ---------------- sfx ----------------
for s_ in SC[1:]: add(s_["s"]-0.30,feed(0.05))
add(TOTAL-0.45,feed(0.05))
# the signal itself: a tone that swells & fades with the plotted pulse (loop-safe: starts at t<0 -> clipped)
def sigtone(c,amp=0.03):
    tt=T_(1.8); env=np.exp(-((tt-0.9)/0.28)**2); return lp(np.sin(2*np.pi*1420/2*tt)*env*amp+np.sin(2*np.pi*710.5*tt)*env*amp*0.3,3000)
add(0.58-0.9,sigtone(0,0.028)); add(TOTAL+0.58-0.9,sigtone(0,0.028))
add(EV["s72"],beep(980,0.06,0.012)); add(EV["vanished"],stampfx(0.12)); add(EV["who"],boom(0.07,70,4,1.0))
add(EV["aug"],beep(760,0.06,0.012)); add(EV["bigear"],boom(0.06,55,3,1.2)); add(EV["scanning"],whoosh(1.2,0.02,300,1500))
add(EV["ehman"]-0.1,printer(1.6,0.016))
for k in range(6): add(EV[f"c{k}"],beep(600+k*90,0.07,0.014))
add(EV["thirty"],stampfx(0.12)); add(EV["noise"],static(0.9,0.006))
add(EV["circles"],scribble(0.9,0.010)); add(EV["oneword"],scribble(EV["wow"]-EV["oneword"]+0.4,0.010)); add(EV["wow"]+0.1,chime(D(2,0),0.02,2.4)); add(EV["wow"]+0.18,chime(D(2,7),0.014,2.4))
tt=T_(0.6); add(EV["hline"]-0.15,np.sin(2*np.pi*np.cumsum(500+700*np.clip(tt/0.4,0,1))/SR)*np.sin(np.pi*tt/0.6)*0.012)
add(EV["freq"],pap(0.03)); add(EV["notx"],stampfx(0.11))
n0=EV["went"]; n1=EV["nothing"]
for k in range(10): add(n0+(n1-n0-0.2)*k/10,plip(0.012,900,1500))
add(EV["nothing"],stampfx(0.14)); add(EV["nothing"],boom(0.06,60,4,0.8))
add(EV["y2024"],beep(760,0.06,0.012)); add(EV["cloud"],shimmer(0.012,1.4))
add(EV["flaring"]-0.1,whoosh(0.8,0.03,400,3000)); add(EV["flaring"],crack(0.04)); add(EV["flaring"],boom(0.10,45,1.6,2.5))
tt=T_(0.7); add(EV["laser"],lp(np.sin(2*np.pi*np.cumsum(300+1800*tt/0.7)/SR)*np.exp(-tt*2)*0.02,4000))
add(EV["moment"]+0.2,whoosh(0.5,0.015,2000,500))
add(EV["hypo"],stampfx(0.13))
add(EV["torn"]+0.1,crack(0.06)); add(EV["torn"]+0.2,boom(0.14,50,2.2,1.8)); add(EV["torn"]+0.35,crack(0.04))
add(EV["golf"]+0.2,plip(0.03,500,900)); add(EV["golf"]+0.45,pap(0.03))
add(EV["sheet"],pap(0.03)); add(EV["once"],chime(D(2,0),0.016,2.4)); add(EV["y1977b"],bell(D(-1,0),0.025,2.5))
# ======================== MASTER ========================
bus=lp(out(),9000)
N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
