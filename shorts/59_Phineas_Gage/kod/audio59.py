import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid59"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sc_(n): s=S(n); return s["s"],s["e"]
G_=lambda o,s=0:196.0*2**o*2**(s/12)
def mbox(f,amp=0.008):
    tt=T_(1.4); s=np.sin(2*np.pi*f*tt)*np.exp(-tt*4)+0.5*np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt*9)+0.25*np.sin(2*np.pi*f*5.4*tt)*np.exp(-tt*14)
    return lp(s*amp*np.clip(tt/0.002,0,1),7000)
def harm(f,dur,amp=0.006):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt*(1+0.002*np.sin(2*np.pi*5*tt)))/k**1.4 for k in range(1,8))
    return lp(s*np.clip(tt/0.4,0,1)*np.clip((dur-tt)/0.6,0,1)*amp,2400)
MEL=[7,9,11,12,11,9,7,4,5,7,9,7,4,2,0,2]
def mbox_seq(t0,t1,step=0.30,amp=0.007,off=0):
    x=t0;k=off
    while x<t1-0.2: add(x,mbox(G_(1,MEL[k%len(MEL)]),amp)); x+=step;k+=1
def hpads(t0,t1,chords,cl=2.4,amp=0.005):
    x=t0;k=0
    while x<t1-0.3:
        for s_ in chords[k%len(chords)]: add(x,harm(G_(-1,s_),min(cl+0.8,t1-x+0.4),amp))
        x+=cl;k+=1
def tick(t0,t1,amp=0.004):
    x=t0;k=0
    while x<t1: add(x,click(amp*(1 if k%2 else 0.7),3000 if k%2 else 2200,500)); x+=0.5;k+=1
def hoof(at,amp=0.012,f=500): tt=T_(0.08); add(at,lp(bp(noise(0.08),f*0.6,f*3),f*3)*np.exp(-tt*60)*amp+np.sin(2*np.pi*f*0.4*tt)*np.exp(-tt*50)*amp*0.6)
def tiltfx(at):
    add(at,shimmer(0.008,1.0)); add(at+0.1,whoosh(0.6,0.008,1500,6000))
# ---- bed ----
tick(0.3,TOTAL)
a,b=sc_("hook"); hpads(0,b,[[0,4,7],[5,9,12]],2.5); mbox_seq(0.1,b,0.32,0.007)
a,b=sc_("blast"); hpads(a,EV["spark"],[[0,4,7],[-3,0,4],[5,9,12]],2.6); mbox_seq(a,EV["spark"]-0.2,0.30,0.006,4)
a,b=sc_("skull"); add(a,drone(G_(-2,0),b-a,0.016,0.3,1.0,300)); add(EV["six"],cello(G_(-1,3),3.0,0.010,0.4,1.0))
a,b=sc_("after"); hpads(a,b,[[-3,0,4],[0,4,7],[-5,-1,2]],2.4); mbox_seq(EV["nolonger"]-0.5,b,0.36,0.005,8)
a,b=sc_("chile"); hpads(a,b,[[0,4,7],[5,9,12],[7,11,14]],1.9); mbox_seq(a,b,0.24,0.006,2)
a,b=sc_("harvard"); hpads(a,TOTAL+0.3,[[0,4,7],[-3,0,4],[5,9,12],[0,4,7]],2.4); mbox_seq(EV["y2009"],TOTAL+0.1,0.32,0.007)
SH=[S("blast")["s"],S("skull")["s"],S("after")["s"],Lx("He survived")[0]-0.3,S("chile")["s"],S("harvard")["s"],Lx("For a century")[0]-0.3]
for t_ in SH: tiltfx(t_-0.36)
tiltfx(TOTAL-0.62)
# ---- events ----
add(EV["rod"],bell(G_(2,7),0.006,2.0)); add(EV["lived"],chime(G_(2,0),0.010,2.0))
for k in range(6): add(EV["blasting"]+k*0.25,lp(bp(noise(0.12),300,2500),2600)*np.exp(-T_(0.12)*30)*0.012)
for k in range(10): add(EV["tamping"]+k*0.11,lp(bp(noise(0.05),200,1500),1600)*np.exp(-T_(0.05)*80)*0.012)
add(EV["spark"]-0.05,crack(0.03)); add(EV["spark"],boom(0.10,45,2,2.5)); add(EV["spark"],lp(noise(1.5),2500)*np.exp(-T_(1.5)*3)*0.03)
add(EV["blast"]+0.1,whoosh(0.7,0.02,600,4000)); add(EV["bullet"],bell(G_(3,0),0.006,1.2))
add(EV["meters"]-0.6,whoosh(0.5,0.014,1500,500)); add(EV["meters"]-0.05,bell(G_(1,10),0.008,1.5)); add(EV["meters"]-0.05,boom(0.03,120,10,0.4))
for k in range(8): hoof(S("after")["s"]+0.3+k*0.45,0.010,300)
d=Lx("He survived")[0]-S("after")["s"]; tt=T_(d); add(S("after")["s"],lp(bp(noise(d),150,900),1000)*(0.5+0.5*np.sin(2*np.pi*0.9*tt))**4*0.010)
add(EV["doctor"],scribble(1.4,0.007)); add(EV["nolonger"],harm(G_(-1,1),2.0,0.008))
x=S("chile")["s"]+0.2
while x<S("chile")["e"]-0.2:
    for o in (0,0.09,0.2,0.29): hoof(x+o,0.010,520)
    x+=0.55
add(S("chile")["s"],lp(bp(noise(S("chile")["e"]-S("chile")["s"]),200,1200),1300)*0.004)
add(EV["hint"],chime(G_(2,4),0.010,1.8))
add(EV["harvard"],bell(G_(0,0),0.012,3.0)); add(EV["photo"],harm(G_(-1,-3),2.0,0.007))
add(EV["y2009"],shimmer(0.012,1.4)); add(EV["turned"],chime(G_(2,7),0.010,2.0))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 2.2
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
