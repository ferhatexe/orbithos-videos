import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid50"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
def tabor(amp=0.05):
    tt=T_(0.25); return lp(np.sin(2*np.pi*(90+60*np.exp(-tt*30))*tt)*np.exp(-tt*14)*amp+bp(rng.normal(0,1,len(tt)),800,3000)*np.exp(-tt*35)*amp*0.4,4000)
def recorder(f,dur,amp=0.012):
    tt=T_(dur); vib=1+0.004*np.sin(2*np.pi*5.5*tt)
    s=np.sin(2*np.pi*np.cumsum(f*vib)/SR)+0.15*np.sin(4*np.pi*np.cumsum(f*vib)/SR)+bp(rng.normal(0,1,len(tt)),f,f*2.5)*0.06
    return lp(s*np.clip(tt/0.03,0,1)*np.clip((dur-tt)/0.05,0,1)*amp,5000)
def gurdy(f,dur,amp=0.02):
    tt=T_(dur); ph=2*np.pi*f*tt; s=sum(np.sin(ph*k)/k**0.9 for k in range(1,9))*(1+0.06*np.sin(2*np.pi*7*tt))
    return lp(s*np.clip(tt/0.3,0,1)*np.clip((dur-tt)/0.4,0,1)*amp,2200)
MEL=[0,2,3,5,7,5,3,2, 0,3,7,10,7,5,3,2]
def dance(t0,t1,beat=0.2,amp=1.0,mel=True):
    add(t0,gurdy(D(-1,0),t1-t0+0.3,0.014*amp)); add(t0,gurdy(D(-1,7),t1-t0+0.3,0.008*amp))
    x=t0;k=0
    while x<t1-0.1:
        if k%3==0: add(x,tabor(0.05*amp))
        elif k%3==2: add(x,tabor(0.025*amp))
        if mel and k%2==0: add(x,recorder(D(1,MEL[(k//2)%len(MEL)]),beat*1.9,0.010*amp))
        x+=beat;k+=1
def chant(t0,t1,amp=0.010):
    x=t0;k=0; notes=[0,2,0,-2,0,3,2,0]
    while x<t1-0.5:
        add(x,choir_(D(0,notes[k%len(notes)]),1.3,amp)); add(x,choir_(D(-1,notes[k%len(notes)]),1.3,amp*0.7)); x+=1.1;k+=1
a,b=sec("hook"); dance(0.0,b,0.21,0.8)
a,b=sec("start"); dance(a,b,0.20,0.9)
a,b=sec("cure"); add(a,drone(D(-2,0),EV["guild"]-a,0.016,0.4,0.4,360)); dance(EV["guild"],b,0.17,1.0); 
x=EV["worse"]
while x<b-0.2: add(x,tabor(0.03)); x+=0.17
a,b=sec("shrine"); chant(a,EV["similar"],0.010); add(a,drone(D(-2,0),b-a,0.016,0.5,0.6,360)); dance(EV["similar"],b,0.24,0.45,mel=False)
a,b=sec("why"); add(a,drone(D(-2,-1),EV["began"]-a,0.02,0.4,0.4,360)); pads(a,EV["began"],[[-1,3,6],[0,3,7]],2.6,0.008)
x=EV["fear"]
while x<EV["began"]: add(x,tabor(0.022+0.02*(x-EV["fear"])/3)); x+=0.33-0.15*(x-EV["fear"])/3.5
dance(EV["began"]-0.1,TOTAL+0.2,0.21,0.8)
# ---------------- sfx ----------------
def pagef(at,amp=0.04):
    tt=T_(0.5); add(at,bp(rng.normal(0,1,len(tt)),900,5000)*np.sin(np.pi*tt/0.5)**1.5*amp)
for s_ in SC[1:]: pagef(s_["s"]-0.32)
pagef(TOTAL-0.6)
add(EV["hundreds"],lp(bp(noise(1.5),300,2500),3000)*np.sin(np.pi*T_(1.5)/1.5)*0.02)
add(EV["july"],bell(D(0,0),0.012,2.0)); add(EV["four"],boom(0.05,70,4,0.8))
add(EV["hot"],whoosh(0.6,0.02,800,2500)); add(EV["more"],chime(D(2,0),0.012,1.6))
add(EV["collapsed"],boom(0.06,90,8,0.5))
for k in range(3): add(EV["shrine"]+k*0.9,bell(D(-1,[0,-5,-3][k]),0.03,3.0))
add(EV["redshoes"],chime(D(2,4),0.014,2.0)); add(EV["stops"]+0.3,bell(D(-1,0),0.025,3.5))
add(EV["hysteria"],boom(0.05,60,3,1.2)); add(EV["strasbourg"],bell(D(-1,0),0.025,3.0))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.8)
