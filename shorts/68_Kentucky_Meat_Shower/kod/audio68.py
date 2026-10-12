import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid68"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
E=lambda o,s=0:164.81*2**o*2**(s/12)
def bass(f,amp=0.024): tt=T_(0.5); return lp((np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt))*np.exp(-tt*5)*amp*np.clip(tt/0.01,0,1),900)
def brush(at,amp=0.004): tt=T_(0.16); add(at,bp(noise(0.16),3000,9000)*np.exp(-tt*18)*amp)
def vib(f,amp=0.006): tt=T_(1.2); return lp((np.sin(2*np.pi*f*tt))*np.exp(-tt*2.5)*(1+0.3*np.sin(2*np.pi*5*tt))*amp,5000)
WALK=[0,3,5,6,7,5,3,2]; beat=60/88; x=0.0;k=0
while x<TOTAL-0.2:
    add(x,bass(E(-2,WALK[k%8]))); brush(x+beat*0.66); brush(x,0.005 if k%2 else 0.0025)
    if k%4==0: add(x+beat*0.5,vib(E(1,[0,3,7,10,7,3][(k//4)%6])))
    if k%8==0:
        for s_ in (0,3,7,10): add(x,pad(E(-1,s_),beat*8,0.004,0.4,0.8))
    x+=beat;k+=1
def flashfx(at):
    add(at,click(0.03,3500,250)); tt=T_(0.5); add(at+0.02,np.sin(2*np.pi*np.cumsum(2000+3000*tt)/SR)*np.exp(-tt*6)*0.004)
def pinfx(at): add(at,click(0.014,1800,500))
def rustle(at,dur=0.3): tt=T_(dur); add(at,bp(noise(dur),1500,6000)*np.sin(np.pi*tt/dur)*0.006)
def splat(at,amp=0.014): tt=T_(0.15); add(at,lp(noise(0.15),900)*np.exp(-tt*30)*amp)
def caw(at,amp=0.010):
    tt=T_(0.35); f=900-300*tt/0.35; s=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*0.5+bp(noise(0.35),800,2500); add(at,bp(s,600,2600)*np.sin(np.pi*tt/0.35)*amp)
SH=[S("scene")["s"],Lx("The pieces")[0]-0.3,Lx("The New York")[0]-0.3,S("clues")["s"],Lx("Scientists who")[0]-0.3,Lx("One early")[0]-0.3,S("answer")["s"],Lx("Vultures really")[0]-0.3,Lx("So if it ever")[0]-0.3]
for t_ in SH: flashfx(t_)
flashfx(TOTAL-0.28)
g=np.random.default_rng(1)
for i in range(10): splat(EV["meat"]+i*0.11+g.uniform(0,0.04),0.012)
for key in ("date","meat","bath","woman","soap","pieces","inches","bigger","nyt","sciam","tasted","mutton","venison","scient","lung","vultures","really"): pinfx(EV[key]-0.15); rustle(EV[key]-0.25)
for i in range(7): add(EV["scient"]+0.3+i*0.09,click(0.010,2500,600))
add(EV["norain"],boom(0.05,90,12,0.4)); add(EV["norain"],crack(0.02))
caw(EV["vultures"]+0.1); caw(EV["vultures"]+0.6,0.008); caw(EV["midair"],0.008)
for i in range(6): splat(EV["midair"]+0.3+i*0.12,0.010)
add(EV["remember"],vib(E(1,7),0.010))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 2.7
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
