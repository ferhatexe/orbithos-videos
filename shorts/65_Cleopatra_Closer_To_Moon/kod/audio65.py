import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid65"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
F=lambda o,s=0:174.61*2**o*2**(s/12)
def vib(f,dur=1.4,amp=0.008):
    tt=T_(dur); s=(np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*6))*np.exp(-tt*2.2)*(1+0.25*np.sin(2*np.pi*5.5*tt))
    return lp(s*amp*np.clip(tt/0.003,0,1),6000)
def bass(f,dur=0.5,amp=0.022):
    tt=T_(dur); s=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt))*np.exp(-tt*5)
    return lp(s*amp*np.clip(tt/0.01,0,1),900)
def brush(at,amp=0.004): tt=T_(0.18); add(at,bp(noise(0.18),3000,9000)*np.exp(-tt*16)*amp)
CH=[[0,4,7,11,14],[5,9,12,16,19],[2,5,9,12,16],[7,11,14,17,21]]
ROOT=[0,5,2,7]
beat=60/96; x=0.0; k=0
while x<TOTAL-0.2:
    bar=int(x/(beat*4))%4; ch=CH[bar]; r=ROOT[bar]
    add(x,bass(F(-2,r+[0,7,12,7][k%4])))
    brush(x+beat*0.66); brush(x,0.006 if k%2 else 0.003)
    if k%2==0: add(x+(beat*0.66 if k%4==2 else 0),vib(F(1,ch[(k//2)%5]),1.4,0.007))
    if k%4==0:
        for s_ in ch[:4]: add(x,pad(F(-1,s_),beat*4+0.3,0.0045,0.3,0.6))
    x+=beat; k+=1
def fanfx(at):
    add(at,whoosh(0.7,0.010,500,3000)); add(at+0.36,shimmer(0.007,0.8))
SH=[S("pyramid")["s"],Lx("Cleopatra was born")[0]-0.3,Lx("And about two")[0]-0.3,Lx("To her")[0]-0.3,S("mammoth")["s"],Lx("A last small")[0]-0.3,S("oxford")["s"],Lx("History isn't")[0]-0.3,Lx("So the next")[0]-0.3]
for t_ in SH: fanfx(t_-0.36)
fanfx(TOTAL-0.62)
for k_ in ("y2560","born","armstrong"): add(EV[k_],bell(F(1,0),0.012,2.5))
add(EV["moon0"],chime(F(2,7),0.010,2.0)); add(EV["ancient"],cello(F(-1,0),1.8,0.010,0.2,0.8))
tt=T_(1.2); f=F(0,7)*(1+0.3*np.sin(np.pi*tt/1.2)); add(EV["mammoths"],lp(np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*tt/1.2)**2*0.014+bp(noise(1.2),500,2000)*np.sin(np.pi*tt/1.2)**2*0.006,3000))
add(EV["y4000"],bell(F(0,7),0.012,2.5)); add(EV["teaching"],bell(F(1,4),0.010,2.0)); add(EV["tenoch"],bell(F(0,11),0.010,2.0))
add(EV["overlaps"],shimmer(0.010,1.4)); add(EV["remember"],bell(F(0,0),0.014,3.0))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 2.3
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
