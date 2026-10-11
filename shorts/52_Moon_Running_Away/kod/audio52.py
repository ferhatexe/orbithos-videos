import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid52"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
def hum(t0,t1,amp=0.006):
    d=t1-t0; tt=T_(d); x=(np.sin(2*np.pi*120*tt)+0.4*np.sin(2*np.pi*240*tt)+0.2*np.sin(2*np.pi*360*tt))*(1+0.2*np.sin(2*np.pi*0.7*tt))
    add(t0,x*np.clip(tt/0.5,0,1)*np.clip((d-tt)/0.5,0,1)*amp)
def buzzflick(at,dur=0.6,amp=0.02):
    g=np.random.default_rng(int(at*100)); tt=T_(dur); env=(g.random(len(tt)//800+1)>0.45).repeat(800)[:len(tt)].astype(float)
    x=(np.sign(np.sin(2*np.pi*120*tt))*0.5+bp(rng.normal(0,1,len(tt)),2000,6000)*0.4)*env
    add(at,lp(x,6000)*amp)
def synthbass(t0,t1,roots,step=0.25,amp=0.03):
    x=t0;k=0
    while x<t1-0.1:
        r=roots[(k//16)%len(roots)]; f=D(-2,r+(12 if k%4==2 else 0)); tt=T_(step*0.9)
        add(x,lp(saw(f,step*0.9,1.0,0.005,0.08,600)*np.exp(-tt*4),900)*amp*1.5); x+=step;k+=1
def arpsyn(t0,t1,chords,step=0.125,amp=0.008,cl=2.0):
    x=t0;k=0
    while x<t1-0.1:
        ch=chords[int((x-t0)/cl)%len(chords)]; s_=ch[k%len(ch)]+(12 if (k//len(ch))%2 else 0)
        tt=T_(0.2); add(x,saw(D(1,s_),0.2,amp,0.003,0.15,2600)*np.exp(-tt*10)); x+=step;k+=1
CH=[[0,3,7],[-4,0,3],[-2,2,5],[-5,-1,2]]
hum(0,TOTAL+0.4,0.004)
a,b=sec("hook"); synthbass(0,b,[0],0.25,0.025); arpsyn(0,b,CH,0.125,0.006,2.0); pads(0,b,[[0,7,15]],3.0,0.007)
a,b=sec("laser"); synthbass(a,b,[0,-4,-2,-5],0.25,0.025); arpsyn(a,b,CH,0.125,0.006,2.0); pads(a,b,CH,2.0,0.006)
a,b=sec("tides"); synthbass(a,b,[-4,-2],0.25,0.022); pads(a,b,[[-4,0,3,7],[-2,2,5,9]],2.4,0.008); arpsyn(a,b,[[-4,0,3],[-2,2,5]],0.25,0.006,2.4)
a,b=sec("time"); pads(a,EV["allb"],[[0,3,7,10],[-4,0,3,7]],2.4,0.008); add(a,drone(D(-2,0),EV["allb"]-a,0.02,0.5,0.5,360)); synthbass(EV["allb"]-0.1,TOTAL+0.1,[0],0.25,0.025); arpsyn(EV["allb"],TOTAL+0.1,CH,0.125,0.006,2.0)
# ---------------- sfx ----------------
for s_ in SC[1:]: buzzflick(s_["s"]-0.34,0.68,0.018)
buzzflick(TOTAL-0.6,0.6,0.018)
add(EV["running"],whoosh(0.8,0.02,600,2400)); add(EV["cm"],beep(880,0.08,0.012)); add(EV["how"],chime(D(2,3),0.012,1.6))
add(EV["y1969"],beep(660,0.1,0.012)); add(EV["apollo"],lp(bp(noise(0.4),800,3000),3500)*np.exp(-T_(0.4)*6)*0.02)
add(EV["mirrors"],chime(D(2,7),0.012,1.6))
def pew(at,amp=0.03):
    tt=T_(0.35); f=2400*np.exp(-tt*9)+300; add(at,np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*8)*amp)
per=2.5/1.6; x=EV["lasers"]
while x<EV["timing"]: pew(x,0.02); add(x+per/2,beep(1400,0.04,0.008)); x+=per
x=EV["trip"]
while x<EV["timing"]-0.2: add(x,click(0.02,3000,300)); x+=0.5
add(EV["slipping"],whoosh(1.2,0.02,1500,500)); add(EV["nails"],chime(D(2,4),0.010,1.4))
add(EV["tides"],lp(bp(noise(2.0),100,700),800)*np.sin(np.pi*T_(2.0)/2.0)*0.04)
add(EV["tug"],boom(0.05,70,4,0.8)); add(EV["higher"],shimmer(0.014,1.4)); add(EV["slows"],cello(D(-2,0),1.6,0.014,0.1,1.0))
add(EV["billion"],bell(D(-1,0),0.018,2.6)); 
for k in range(6): add(EV["eighteen"]+k*0.12,click(0.02,2500,280))
add(EV["future"],shimmer(0.014,1.6)); add(EV["eclipses"],cello(D(-1,-4),1.8,0.014,0.2,1.0)); add(EV["every"],chime(D(2,0),0.012,1.6))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
