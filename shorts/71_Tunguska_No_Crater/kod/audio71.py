import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid71"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import master
from sfxlib import *
import r71
LINES=r71.LINES; TOTAL=r71.TOTAL; wt=r71.wt; Ls=r71.Ls; SHOTS=r71.SHOTS
init(TOTAL)
# ---- music: dark documentary pulse (E minor, 96 bpm), low strings + taiko-ish pulses ----
BEAT=0.625; E=lambda o,s=0:164.81*2**o*2**(s/12)
PROG=[0,0,-4,-2]; CH={0:[0,3,7],-4:[-4,0,3],-2:[-2,1,5]}
def tom(amp): tt=T_(0.5); f=70+40*np.exp(-tt*18); return lp(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*7)*amp+bp(noise(0.5),80,400)*np.exp(-tt*20)*amp*0.3,600)
x=0.0;k=0
while x<TOTAL+0.2:
    bar=int(x/(BEAT*4)); r=PROG[bar%4]
    if k%4 in (0,3): add(x,tom(0.10 if k%4==0 else 0.06))
    add(x,cello(E(-2,r),BEAT*0.9,0.012,0.05,0.2)); x+=BEAT; k+=1
x=0.0
while x<TOTAL+0.2:
    bar=int(x/(BEAT*4)); r=PROG[bar%4]
    for s_ in CH[r]: add(x,cello(E(-1,s_),BEAT*4+0.4,0.0045,0.6,0.6))
    x+=BEAT*4
add(0,drone(E(-3,0),TOTAL+0.4,0.02,0.3,0.6,200))
# ---- transitions ----
for st,fn,kind in SHOTS[1:]:
    if kind=="blast": add(st-0.35,whoosh(0.45,0.016,300,2500)); add(st,boom(0.09,40,2.2,2.5)); add(st,crack(0.02))
    else: add(st,boom(0.025,75,8,0.4)); add(st,click(0.008,1500,150))
add(TOTAL-0.4,whoosh(0.45,0.016,300,2500))
# ---- scene sfx ----
amb(150,1200,0.012,0.0,Ls(1)-0.2,0.05,0.3,0.4,0.25)        # wind over the dead forest
for i in range(14): add(0.3+i*0.31,click(0.004,g_:=np.random.default_rng(i).uniform(800,2000),90))  # crackle embers
add(wt(0,"flattened"),boom(0.05,45,3,2.0))
add(wt(0,"crater"),bell(E(-1,0),0.012,2.5))
amb(400,6000,0.006,Ls(1),Ls(2),0.8,0.3,0.0)                 # rising heat hiss
add(wt(1,"heat"),whoosh(1.2,0.012,200,3000))
add(wt(2,"blast"),boom(0.22,32,1.2,3.5)); add(wt(2,"blast"),crack(0.06)); amb(60,900,0.03,wt(2,"blast"),wt(2,"blast")+1.6,0.05,1.0,0.3,3)
add(wt(2,"threw"),pap(0.05))
add(wt(3,"glowed"),shimmer(0.006,1.6)); add(wt(3,"midnight"),bell(E(1,0),0.010,2.4))
for i in range(12): add(wt(3,"midnight")+i*0.08,click(0.003,3500,500))  # clock ticks
amb(500,4000,0.004,Ls(4)-0.3,Ls(5)-0.1,0.2,0.2,0.0)          # film projector hiss
for i in range(int((Ls(5)-Ls(4))/0.0417)): add(Ls(4)-0.3+i*0.0417,click(0.0025,2200,700))
add(wt(5,"giant"),boom(0.04,55,4,1.2)); add(wt(5,"pointing"),whoosh(0.6,0.010,800,4000))
add(wt(6,"standing"),chime(E(1,7),0.008,2.0)); amb(100,800,0.008,Ls(6),Ls(7)-0.3,0.4,0.3,0.4,0.2)
add(Ls(7)-0.2,whoosh(1.4,0.014,200,1600))
add(wt(7,"exploded"),boom(0.25,30,1.0,4.0)); add(wt(7,"exploded"),crack(0.05))
add(wt(7,"hundreds"),boom(0.08,38,1.6,2.5))
add(wt(8,"ground"),bell(E(-1,0),0.010,3.0))
bus=lp(out(),9500); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 0.8
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
