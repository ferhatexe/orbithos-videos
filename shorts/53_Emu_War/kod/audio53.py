import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid53"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
def snare(amp=0.03):
    tt=T_(0.18); return (bp(rng.normal(0,1,len(tt)),1500,6000)*np.exp(-tt*22)+np.sin(2*np.pi*190*tt)*np.exp(-tt*30)*0.6)*amp
def brass(f,dur,amp=0.012):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt)/k**0.8 for k in range(1,8))*(1-np.exp(-tt*18))
    return lp(s*np.clip((dur-tt)/0.08,0,1)*amp*(0.7+0.3*np.exp(-tt*3)),2600)
def march(t0,t1,beat=0.3,amp=1.0,mel=True,seq=None):
    x=t0;k=0; seq=seq or [0,4,7,4,0,4,7,12,11,7,4,2,0,2,4,0]
    while x<t1-0.1:
        add(x,snare(0.022*amp*(1.4 if k%4==0 else 0.8)))
        if k%2==0: add(x,boom(0.04*amp,70,8,0.3))
        if mel and k%2==0: add(x,brass(D(0,seq[(k//2)%len(seq)]),beat*1.8,0.010*amp))
        x+=beat;k+=1
def kookaburra(at,amp=0.01):
    for k in range(6):
        tt=T_(0.12); f=900+500*np.sin(np.pi*tt/0.12)+200*k%3; add(at+k*0.13,lp(np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*tt/0.12)*amp,3000))
def mgun(at,n=8,amp=0.03,rate=0.08):
    for k in range(n): add(at+k*rate,crack(amp*rng.uniform(0.7,1.0))); add(at+k*rate,boom(amp*0.6,120,25,0.12))
def footsteps(t0,t1,amp=0.012,rate=0.07):
    x=t0
    while x<t1: tt=T_(0.05); add(x,lp(rng.normal(0,1,len(tt)),900)*np.exp(-tt*60)*amp*rng.uniform(0.5,1)); x+=rate*rng.uniform(0.6,1.4)
a,b=sec("hook"); march(0.0,b,0.3,0.8)
a,b=sec("setup"); march(a,EV["major"],0.3,0.6,mel=False); pads(a,EV["major"],[[0,4,7],[5,9,12]],2.4,0.007); march(EV["major"],b,0.28,0.9)
a,b=sec("battle"); march(a,b,0.24,0.7,True,[0,3,7,3,0,3,8,7,5,3,2,0]); footsteps(a,b,0.010)
a,b=sec("end"); add(a,drone(D(-2,0),EV["won"]-a,0.018,0.5,0.4,380)); pads(a,EV["won"],[[0,3,7],[-4,0,3]],2.4,0.008)
march(EV["won"]-0.1,TOTAL+0.2,0.3,0.8)
for k,s_ in enumerate((12,11,9,7,5,4,2,0)): add(EV["pulled"]+k*0.25,brass(D(0,s_),0.4,0.008))
# ---------------- sfx ----------------
for s_ in SC[1:]: add(s_["s"]-0.36,whoosh(0.75,0.035,250,1600)); add(s_["s"]-0.36,lp(bp(noise(0.7),200,1200),1400)*np.sin(np.pi*T_(0.7)/0.7)*0.02)
add(TOTAL-0.7,whoosh(0.75,0.035,250,1600))
footsteps(0.0,2.5,0.012); add(EV["lost"],boom(0.06,60,4,1.0)); add(EV["lost"],pap(0.03))
for e in ("soldiers","mguns","emus0"): add(EV[e],pap(0.03))
kookaburra(EV["wa"],0.010); add(EV["twenty"],footsteps(EV["twenty"],EV["twenty"]+1.5,0.012) or np.zeros(1))
add(EV["help"],pap(0.035)); 
for k,e in enumerate(("major","two","guns","bullets")): add(EV[e],pap(0.025))
mgun(EV["scatter"]-0.3,10,0.03); add(EV["jams"],lp(bp(noise(0.25),400,2500),3000)*np.exp(-T_(0.25)*15)*0.05); add(EV["jams"]+0.1,boom(0.04,180,20,0.2))
tt=T_(2.5); add(EV["truck"],lp(np.sin(2*np.pi*(55+8*np.sin(2*np.pi*3*tt))*tt)*0.5+rng.normal(0,1,len(tt))*0.2,500)*np.clip(tt/0.3,0,1)*np.clip((2.5-tt)/0.5,0,1)*0.05)
footsteps(EV["outrun"],EV["outrun"]+2.0,0.014,0.05); add(EV["kmh"],whoosh(0.6,0.03,600,3000))
add(EV["tanks"],boom(0.05,50,3,1.0))
mgun(EV["rounds"]-0.2,6,0.022,0.1)
for k in range(3): add(EV["three"]+k*0.35,pap(0.025)); add(EV["no"]+k*0.12,pap(0.035))
add(EV["won"],chime(D(2,0),0.016,2.0)); kookaburra(EV["won"]+0.3,0.012)
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
