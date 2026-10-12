import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid69"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
A=lambda o,s=0:220*2**o*2**(s/12)
def lyre(f,dur=1.8,amp=0.011):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt)*np.exp(-tt*(2.0+k*1.0))/k**1.1 for k in range(1,7))
    return lp(s*amp*np.clip(tt/0.003,0,1),4200)
def aulos(f,dur,amp=0.004):
    tt=T_(dur); vib=1+0.005*np.sin(2*np.pi*5.5*tt); s=sum(np.sin(2*np.pi*np.cumsum(f*k*vib)/SR)/k**0.7 for k in range(1,9))
    return bp(s,300,3500)*np.clip(tt/0.15,0,1)*np.clip((dur-tt)/0.3,0,1)*amp
MODE=[0,1,3,5,7,8,10,12]
x=0.1;k=0;g=np.random.default_rng(3)
while x<TOTAL-0.2: add(x,lyre(A(0,MODE[[0,2,4,3,5,4,2,1][k%8]]),1.8,0.009)); x+=0.36;k+=1
add(0,drone(A(-2,0),TOTAL+0.4,0.016,0.4,0.8,280))
for t0,notes in ((1.0,[7,8,7,5,3]),(18.6,[0,3,5,7,8,7]),(35.2,[12,10,8,7])):
    for i,n in enumerate(notes): add(t0+i*0.7,aulos(A(0,n),0.85))
def flap(at,amp=0.010): tt=T_(0.28); add(at,lp(bp(noise(0.28),180,1400),1500)*np.sin(np.pi*tt/0.28)**2*amp)
def ripplefx(at): add(at,shimmer(0.007,1.0)); add(at,bell(A(1,0),0.006,1.5)); add(at+0.05,whoosh(0.7,0.006,800,3000))
SH=[S("gorgon")["s"],Lx("Perseus cut")[0]-0.3,S("birth")["s"],Lx("Pegasus later")[0]-0.3,S("after")["s"],Lx("In Ovid, he set")[0]-0.3,S("shield")["s"],Lx("Greeks painted")[0]-0.3,Lx("Ovid also")[0]-0.3,Lx("So the next")[0]-0.3]
for t_ in SH: ripplefx(t_-0.38)
ripplefx(TOTAL-0.66)
for i in range(4): flap(0.3+i*0.5)
add(EV["neck0"],bell(A(-1,0),0.014,2.5))
def hiss(at,dur=0.8,amp=0.006): tt=T_(dur); add(at,bp(noise(dur),4000,9000)*np.sin(np.pi*tt/dur)*amp)
hiss(EV["three"]); hiss(EV["onlydie"],0.6)
add(EV["immortal"],chime(A(2,7),0.010,2.0))
add(EV["blade"],lp(bp(noise(0.4),2000,8000),9000)*np.exp(-T_(0.4)*8)*0.014); add(EV["reflect"],shimmer(0.010,1.2))
add(EV["sprang"],boom(0.04,60,4,1.5)); add(EV["pegasus"],lyre(A(1,7),2.0,0.014))
for i in range(5): flap(EV["pegasus"]+0.2+i*0.45)
add(EV["thunder"],boom(0.08,40,1.6,3.0)); add(EV["thunder"],crack(0.03))
add(EV["gaze"],cello(A(-1,1),1.8,0.010,0.2,0.8)); add(EV["weapon"]-0.4,crack(0.03))
for i in range(8): add(EV["coral"]+i*0.08,click(0.008,3500,500))
add(EV["shield"],bell(A(0,0),0.016,3.0)); add(EV["evil"],aulos(A(0,1),1.2,0.005)); hiss(EV["cursed"],0.9)
add(EV["remember"],lyre(A(0,0),2.4,0.016))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.5
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
