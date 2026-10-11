import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid44"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
def piano(f,dur=1.8,amp=0.03):
    tt=T_(dur); s=sum(a_*np.sin(2*np.pi*f*k*tt*(1+0.0005*k*k))*np.exp(-tt*(1.8+k*0.9)) for k,a_ in ((1,1),(2,0.45),(3,0.25),(4,0.12),(5,0.06)))
    return lp(s*amp*np.clip(tt/0.003,0,1),4500)
def rag(t0,t1,amp=0.022,minor=False,step=0.24):
    """1910s parlour piano: oom-pah bass + broken chords"""
    prog=[[0,4,7],[5,9,12],[7,11,14],[0,4,7]] if not minor else [[0,3,7],[-4,0,3],[-5,-1,2],[0,3,7]]
    x=t0;k=0
    while x<t1-0.2:
        ch=prog[(k//8)%4]
        if k%2==0: add(x,piano(D(-1,ch[0]-12*((k//2)%2==1)*0),1.2,amp*0.9))
        else:
            for s_ in ch: add(x,piano(D(0,s_),0.9,amp*0.45))
        if k%4==3: add(x+step*0.5,piano(D(1,ch[k%3]),0.6,amp*0.35))
        x+=step;k+=1
def creak(amp=0.03,dur=0.8):
    tt=T_(dur); f=90+40*np.sin(2*np.pi*1.3*tt); s=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-((tt-dur/2)/(dur/3))**2)
    return lp(bp(s,200,1500),1600)*amp
def glug(amp=0.04):
    tt=T_(0.25); f=180+260*np.exp(-tt*14); return lp(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*9)*amp,1200)
def rumble(dur,amp):
    tt=T_(dur); return lp(rng.normal(0,1,len(tt)),140)*np.clip(tt/0.4,0,1)*np.clip((dur-tt)/0.6,0,1)*amp*6
# ---------------- music ----------------
a,b=sec("hook"); add(0,drone(D(-2,0),b+0.4,0.024,0.2,1.0,380)); rag(0.0,b,0.016,True,0.24)
a,b=sec("tank"); rag(a,EV["warm"],0.020,False,0.25); add(EV["warm"],drone(D(-2,-5),EV["burst"]-EV["warm"]+0.3,0.022,0.6,0.3,420))
x=EV["sound"]
while x<EV["burst"]:   # nervous ticking
    add(x,piano(D(1,1),0.4,0.010)); x+=0.25
a,b=sec("wave"); add(a,rumble(b-a+0.4,0.05)); add(a,drone(D(-2,-5),b-a,0.028,0.3,0.8,420)); add(a,cello(D(-2,-5),b-a,0.016,0.4,0.8))
a,b=sec("stuck"); add(a,drone(D(-2,-3),b-a,0.022,0.6,1.0,380)); 
for k,s_ in enumerate((0,-1,-3,-5,-7,-8)): add(a+0.2+k*1.4,piano(D(0,s_),2.5,0.016))
add(EV["cooled"],pad(D(-1,3),b-EV["cooled"],0.010,1.0,1.0))
a,b=sec("end"); rag(a,EV["locals"],0.014,True,0.3); rag(EV["locals"],TOTAL+0.2,0.016,False,0.24); add(EV["locals"],pad(D(-1,0),TOTAL-EV["locals"]+0.4,0.008,0.8,0.3))
# ---------------- sfx ----------------
for s_ in SC[1:]: add(s_["s"]-0.32,whoosh(0.7,0.03,200,1200)); add(s_["s"]-0.1,glug(0.03))
add(TOTAL-0.6,whoosh(0.7,0.03,200,1200)); add(TOTAL-0.35,glug(0.03))
add(0,rumble(3.5,0.035)); add(EV["n21"],boom(0.10,60,3,1.4)); add(EV["syrup"]-0.3,plip(0.04,500,900)); add(EV["kill"],boom(0.05,90,6,0.6))
add(EV["jan"],pap(0.03)); add(EV["gallons"],glug(0.035)); add(EV["gallons"]+0.25,glug(0.03)); add(EV["meant"],pap(0.025))
add(EV["alcohol"],plip(0.03,600,1200)); add(EV["explosives"],boom(0.08,70,4,1.0))
add(EV["warm"],chime(D(2,4),0.012,2.0)); add(EV["sound"]-0.2,creak(0.03,1.0))
g=np.random.default_rng(3); x=EV["gun"]-0.1
while x<EV["burst"]:
    add(x,crack(0.035*g.uniform(0.6,1.0))); x+=g.uniform(0.07,0.16)
add(EV["burst"],boom(0.14,40,1.2,3.5)); add(EV["burst"],crack(0.07)); add(EV["burst"]+0.1,whoosh(1.5,0.05,150,1200)); add(EV["burst"],rumble(2.5,0.035))
add(EV["brown"],whoosh(1.2,0.04,150,900)); add(EV["ft25"],boom(0.06,60,4,0.8)); add(EV["mph"],whoosh(0.9,0.04,300,1800))
add(EV["crush"],crack(0.06)); add(EV["buildings"],boom(0.14,50,2.4,1.8))
for k in range(5): add(EV["buildings"]+0.15+k*0.18,crack(0.03))
add(EV["bends"],creak(0.05,1.2)); add(EV["railway"],boom(0.08,80,3,1.0))
add(EV["real"],boom(0.08,45,1.8,2.2)); add(EV["thick"],glug(0.03)); add(EV["glue"],glug(0.025))
add(EV["half"],boom(0.06,55,3,1.2)); add(EV["cleanup"],lp(bp(noise(1.8),800,3500),3800)*np.sin(np.pi*T_(1.8)/1.8)*0.02)
add(EV["anarch"],boom(0.06,90,5,0.7)); add(EV["court"],pap(0.03)); add(EV["weak"],gavel(0.20)); add(EV["weak"]+0.35,gavel(0.12))
add(EV["sweet"],chime(D(2,4),0.014,2.2)); add(EV["harbor"],amb(200,900,0.0,0,0.1) if False else lp(bp(noise(3.0),150,700),800)*np.sin(np.pi*T_(3.0)/3.0)*0.03)
add(EV["y1919"],bell(D(-1,0),0.025,2.5))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
