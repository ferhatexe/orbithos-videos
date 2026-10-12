import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid67"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
A=lambda o,s=0:220*2**o*2**(s/12)
CH=[[0,3,7,10],[-4,0,3,7],[-2,2,5,9],[-5,-1,2,5]]
t_=0;k=0
while t_<TOTAL:
    for s_ in CH[k%4]: add(t_,pad(A(-1,s_),3.6,0.0055,1.0,1.2))
    t_+=2.8;k+=1
add(0,drone(A(-2,0),TOTAL+0.4,0.012,0.4,0.8,280))
x=0.2;k=0; notes=[12,15,19,22,19,15,14,10]
while x<TOTAL-0.3: add(x,chime(A(1,notes[k%8]),0.0045,1.6)); x+=0.42;k+=1
def chirp(at,dur=1.6,amp=0.02):
    tt=T_(dur); f=40+260*(tt/dur)**3.5; env=(tt/dur)**1.5*np.clip((dur-tt)/0.05,0,1)
    add(at,np.sin(2*np.pi*np.cumsum(f)/SR)*env*amp)
def swirlfx(at): add(at,shimmer(0.007,1.0)); add(at,whoosh(0.8,0.008,1200,5000))
SH=[S("forge")["s"],Lx("Heavier atoms")[0]-0.3,Lx("One place")[0]-0.3,S("crash")["s"],Lx("Telescopes")[0]-0.3,Lx("In its light")[0]-0.3,S("earth")["s"],Lx("So the next")[0]-0.3]
for t_ in SH: swirlfx(t_-0.4)
swirlfx(TOTAL-0.7)
add(EV["ring"],chime(A(2,7),0.012,2.2)); chirp(EV["dead"]-0.6,1.4,0.016); add(EV["smash"],boom(0.07,45,2,2.5))
for i in range(6): add(EV["forge"]+0.1+i*0.12,kal(A(1,[0,3,7,10,12,15][i]),1.2,0.009))
add(EV["iron"],bell(A(-1,0),0.014,2.5)); add(EV["beyond"],cello(A(-1,1),1.6,0.010,0.2,0.8))
for i in range(14): add(EV["flood"]+i*0.12,click(0.008,3000,500))
chirp(EV["collide"]-1.0,1.4,0.018); add(EV["collide"]+0.4,boom(0.05,50,3,1.5))
chirp(EV["waves"]-0.4,1.8,0.022); add(EV["y2017"],bell(A(0,0),0.012,2.5))
add(EV["debris"]-0.6,boom(0.06,40,1.5,3.0)); add(EV["kilonova"],shimmer(0.012,1.6))
add(EV["fresh"],shimmer(0.010,1.4)); add(EV["five"],bell(A(1,7),0.010,2.0))
for k_,n in (("gold2",12),("plat",16),("uran",19)): add(EV[k_],chime(A(2,n),0.010,2.0))
add(EV["born"],choir_(A(0,7),2.4,0.008)); add(EV["remember"],chime(A(2,7),0.012,2.4))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.65
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
