import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid45"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
def choir(t0,t1,prog,step,amp=0.010,oct_=0):
    x=t0;k=0
    while x<t1-0.4:
        for s_ in prog[k%len(prog)]: add(x,choir_(D(oct_,s_),min(step+0.8,t1-x+0.6),amp))
        x+=step;k+=1
def glassrun(at,amp=0.010,n=9,up=True):
    sc_=[0,2,4,7,9,12,14,16,19,21,24]
    for k in range(n): add(at+k*0.035,chime(D(2,sc_[k if up else n-1-k]),amp*(0.6+0.4*rng.random()),1.6))
def lyre(t0,t1,chords,step=0.28,amp=0.014,cl=2.2):
    x=t0;k=0
    while x<t1-0.2:
        ch=chords[int((x-t0)/cl)%len(chords)]; s_=ch[k%len(ch)]+(12 if (k//len(ch))%2 else 0)
        add(x,kal(D(0,s_),1.6,amp)); x+=step; k+=1
DOR=[[0,3,7],[-2,2,5],[-4,0,3],[-2,2,7]]
# ---------------- music ----------------
a,b=sec("hook"); add(0,drone(D(-2,0),b+0.5,0.020,0.2,1.0,380)); choir(0.0,b,DOR,2.8,0.008); lyre(0.0,b,DOR,0.24,0.010,2.8)
a,b=sec("greece"); choir(a,b,DOR,2.6,0.008); lyre(a,b,DOR,0.26,0.014,2.6); add(a,drone(D(-2,-2),b-a,0.016,1.0,1.0,380))
a,b=sec("aus"); add(a,drone(D(-3,0),b-a,0.050,0.8,1.0,260)); choir(a,b,[[0,7],[-2,5]],3.0,0.006)
x=EV["orion2"]
while x<b-0.2:
    add(x,click(0.05,1800,180)); add(x+0.26,click(0.035,1500,180)); x+=0.52
a,b=sec("sky"); add(a,drone(D(-2,0),b-a+0.4,0.018,0.8,0.3,380)); choir(a,EV["backward"],[[0,4,7],[-3,0,4]],2.8,0.007)
choir(EV["hundred"],TOTAL+0.2,[[0,3,7],[-2,2,5],[-4,0,3]],2.6,0.009); lyre(EV["hypo"],TOTAL+0.1,DOR,0.24,0.010,2.6)
# ---------------- sfx ----------------
for s_ in SC[1:]: glassrun(s_["s"]-0.3,0.010); add(s_["s"]-0.32,whoosh(0.6,0.02,800,4000))
glassrun(TOTAL-0.6,0.010); add(TOTAL-0.62,whoosh(0.6,0.02,800,4000))
add(EV["same"],bell(D(-1,0),0.02,3.0)); add(EV["seven"],shimmer(0.016,1.4)); add(EV["hunter"],boom(0.05,70,4,0.8))
add(EV["missing"],whoosh(0.8,0.02,3000,600)); add(EV["missing"]+0.05,chime(D(2,-1),0.014,2.0))
add(EV["how"],boom(0.05,60,4,1.0)); add(EV["samestar"],chime(D(2,3),0.014,2.4))
add(EV["pleiades"],shimmer(0.014,1.4)); add(EV["atlas"],boom(0.07,45,1.5,2.0))
add(EV["orion"],boom(0.05,80,5,0.7)); add(EV["gods"],shimmer(0.02,1.8))
for k in range(7): add(EV["madestars"]+k*0.07,chime(D(2,[0,3,7,10,12,15,19][k]),0.010,1.8))
add(EV["merope"],bell(D(0,3),0.016,2.5)); add(EV["mortal"],chime(D(1,7),0.012,2.0)); add(EV["faint"],whoosh(1.0,0.018,2500,500))
add(EV["aus"],boom(0.06,50,2,1.6)); add(EV["chasing"],whoosh(0.9,0.02,500,2200)); add(EV["hiding"],whoosh(0.7,0.018,2000,500)); add(EV["six"],bell(D(-1,0),0.02,2.5))
add(EV["look"],shimmer(0.012,1.2)); add(EV["see6"],chime(D(2,0),0.014,2.2)); add(EV["y2021"],pap(0.025))
tt=T_(1.6); add(EV["backward"],lp(np.sin(2*np.pi*np.cumsum(1200-900*tt/1.6)/SR)*np.sin(np.pi*tt/1.6)*0.012,3000)); add(EV["backward"],whoosh(1.6,0.03,2500,300))
x=EV["backward"]
while x<EV["apart"]+0.8: add(x,click(0.02,3000,300)); x+=0.09
add(EV["apart"],shimmer(0.018,1.6)); add(EV["seven2"],bell(D(0,0),0.022,3.0)); add(EV["seven2"],chime(D(2,7),0.014,2.5))
add(EV["hypo"],boom(0.04,70,4,0.8)); add(EV["oldest"],bell(D(-1,0),0.02,3.0))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.8)
