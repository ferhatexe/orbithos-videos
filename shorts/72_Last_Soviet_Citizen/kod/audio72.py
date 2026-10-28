import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid72"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import master
from sfxlib import *
import r72
LINES=r72.LINES; TOTAL=r72.TOTAL; wt=r72.wt; Ls=r72.Ls; SHOTS=r72.SHOTS
init(TOTAL)
# ---- music: melancholic A minor, 84 bpm: soft piano arpeggio + low strings + pulse ----
BEAT=60/84; A=lambda o,s=0:220*2**o*2**(s/12)
PROG=[[0,3,7],[-4,0,3],[-7,-4,0],[-5,-2,2]]  # Am F Dm Em(ish)
def piano(f,dur=2.0,amp=0.010):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt)*np.exp(-tt*(1.6+k*0.9))/k**1.3 for k in range(1,6))
    return lp(s*amp*np.clip(tt/0.004,0,1),3800)
x=0.0;k=0
while x<TOTAL+0.2:
    ch=PROG[int(x/(BEAT*4))%4]; n=ch[k%3]+(12 if (k//3)%2 else 0)
    add(x,piano(A(0,n),2.2,0.009)); x+=BEAT/2; k+=1
x=0.0
while x<TOTAL+0.2:
    ch=PROG[int(x/(BEAT*4))%4]
    for s_ in ch: add(x,cello(A(-2,s_),BEAT*4+0.5,0.006,0.6,0.7))
    add(x,cello(A(-3,ch[0]),BEAT*4+0.5,0.010,0.4,0.6)); x+=BEAT*4
for i in range(int(TOTAL/BEAT)+1): add(i*BEAT,lp(np.sin(2*np.pi*55*T_(0.3))*np.exp(-T_(0.3)*12),300)*0.05)
# ---- transitions: CRT channel switch = static burst + click; cuts = soft thump ----
for st,fn,kind in SHOTS[1:]:
    if kind=="tv": add(st-0.18,static(0.36,0.020)); add(st-0.02,click(0.012,1200,120)); add(st,beep(15700,0.25,0.0012))
    else: add(st,boom(0.025,70,8,0.4))
# ---- scene sfx ----
amb(80,600,0.010,0.0,Ls(1)-0.2,0.05,0.3,0.3,0.2)
add(Ls(2)+0.3,boom(0.12,35,0.6,4.5)); amb(40,900,0.03,Ls(2)+0.3,Ls(3)-0.3,0.4,0.4,0.3,6)   # launch roar
for i in range(6): add(Ls(4)+i*0.55,boom(0.02,48,6,0.5))                                     # tank treads
amb(60,500,0.015,Ls(4),Ls(5)-0.2,0.2,0.3,0.6,7)
add(wt(5,"Saint")-0.1,stampfx(0.07)); add(wt(5,"Saint")+0.08,click(0.02,900,80))
for k_,sub in enumerate(("Flights","seat")): add(wt(6,sub),pap(0.04))
add(wt(6,"replacement"),stampfx(0.09))
add(wt(7,"stay"),bell(A(-1,0),0.012,3.0))
amb(200,2500,0.010,Ls(8),wt(8,"while"),0.3,0.3,0.6,1.5)                                     # wind on the flag
add(wt(8,"dissolved"),bell(A(-2,0),0.016,4.0))
add(wt(9,"Kazakhstan"),stampfx(0.09))
amb(300,3000,0.010,Ls(10),Ls(11)-0.3,0.3,0.3,0.4,0.8)                                       # parachute wind
for i in range(12): add(wt(10,"311")+i*0.07,click(0.004,2800,400))
add(Ls(11)+0.1,boom(0.12,32,0.6,4.0)); amb(40,1200,0.03,Ls(11)+0.1,Ls(12)-0.3,0.3,0.4,0.3,7)
add(wt(12,"last"),chime(A(1,0),0.008,2.4))
bus=lp(out(),9500); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.45
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
