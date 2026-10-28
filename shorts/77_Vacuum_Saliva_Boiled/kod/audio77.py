import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid77"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import master
from sfxlib import *
import r77
LINES=r77.LINES; TOTAL=r77.TOTAL; wt=r77.wt; Ls=r77.Ls; SHOTS=r77.SHOTS
init(TOTAL)
# ---- music: tense 60s-lab thriller: low pulse, ticking hi-hat, minor synth pad, heartbeat ----
BEAT=60/100; E=lambda o,s=0:164.81*2**o*2**(s/12)
PROG=[[0,3,7],[0,3,8],[-2,2,5],[-4,0,3]]
x=0.0;k=0
while x<TOTAL+0.2:
    ch=PROG[int(x/(BEAT*4))%4]
    add(x,lp(np.sin(2*np.pi*E(-2,ch[0])*T_(BEAT*0.9))*np.exp(-T_(BEAT*0.9)*4)*0.07,500))
    if k%2==1: add(x,click(0.006,6000,200))
    x+=BEAT/2 if False else BEAT; k+=1
x=0.0
while x<TOTAL+0.2:
    ch=PROG[int(x/(BEAT*4))%4]
    for s_ in ch: add(x,pad(E(-1,s_),BEAT*4+0.6,0.006,0.6,0.8))
    x+=BEAT*4
arp(0.0,TOTAL+0.2,[[0,3,7,12],[0,3,8,12],[-2,2,5,10],[-4,0,3,8]],step=BEAT/2,amp=0.0035,oct_=1,cl=BEAT*4)
add(0,drone(E(-3,0),TOTAL+0.4,0.015,0.4,0.8,250))
def heartbeat(at,amp=0.05): add(at,boom(amp,55,14,0.25)); add(at+0.18,boom(amp*0.7,50,14,0.25))
# ---- transitions: airlock iris = pneumatic hiss + metal clunk ----
for st,fn,kind in SHOTS[1:]:
    if kind=="iris": add(st-0.22,lp(bp(noise(0.3),2000,9000),10000)*np.sin(np.pi*T_(0.3)/0.3)*0.010); add(st-0.02,boom(0.05,90,12,0.35)); add(st-0.02,click(0.012,1200,90))
    else: add(st,boom(0.022,70,8,0.4))
# ---- scene sfx ----
amb(80,400,0.010,0,TOTAL,0.5,0.5,0.2,0.1)                          # chamber hum
for i in range(5): add(0.2+i*0.75,lp(bp(noise(0.12),1500,6000),7000)*np.exp(-T_(0.12)*30)*0.004)   # bubbling
add(wt(0,"black"),boom(0.08,40,2.0,2.0))
for i in range(int((Ls(1)-0.4)/0.8)): add(0.3+i*0.8,beep(880,0.12,0.004))   # warning beeps under hook
add(wt(2,"pumped"),lp(bp(noise(2.0),300,2500),3000)*np.clip(T_(2.0)/0.3,0,1)*np.clip((2.0-T_(2.0))/0.6,0,1)*0.010)
add(wt(3,"loose"),crack(0.05)); add(wt(3,"loose"),lp(bp(noise(2.5),1500,9000),10000)*np.exp(-T_(2.5)*1.2)*0.022)
for i in range(6): add(Ls(4)+i*0.5,beep(1000,0.15,0.006))
for i in range(8): add(Ls(5)+i*0.11,click(0.004,2500,500))
add(wt(6,"Armstrong"),bell(E(0,0),0.010,2.5))
for i in range(8): heartbeat(Ls(7)+i*0.62,0.05*(1-i/10))
add(wt(7,"collapsed"),boom(0.08,45,3,1.5))
for i in range(12): add(Ls(8)+i*0.22,lp(bp(noise(0.06),300,1500),1600)*np.exp(-T_(0.06)*50)*0.02)   # running steps
add(Ls(9),lp(bp(noise(2.0),200,4000),5000)*np.clip(T_(2.0)/0.2,0,1)*np.clip((2.0-T_(2.0))/0.6,0,1)*0.03)   # air rush
add(Ls(10)+0.2,lp(np.sin(2*np.pi*E(1,0)*T_(0.5))*np.exp(-T_(0.5)*3),3000)*0.01); heartbeat(Ls(10)+0.6,0.04); heartbeat(Ls(10)+1.4,0.04)
add(wt(10,"earache"),chime(E(1,7),0.007,1.8))
add(Ls(11)+0.2,pap(0.03))
bus=lp(out(),9500); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.05
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
