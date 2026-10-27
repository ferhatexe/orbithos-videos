import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid70"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf, json
import master
from sfxlib import *
import r70
LINES=r70.LINES; TOTAL=r70.TOTAL; wt=r70.wt; Ls=r70.Ls; SHOTS=r70.SHOTS
init(TOTAL)
# ---- music: dark cinematic pulse, D minor, 100 bpm 8ths ----
BEAT=0.6; E8=BEAT/2
def sub(f,dur,amp): tt=T_(dur); return lp(np.sin(2*np.pi*f*tt)*np.exp(-tt*5)*np.clip(tt/0.004,0,1)*amp+np.sin(2*np.pi*f*2*tt)*np.exp(-tt*9)*amp*0.25,400)
PROG=[0,0,-4,-2]  # Dm, Dm, Bb, C (roots rel. D)
x=0.0;k=0
while x<TOTAL+0.2:
    bar=int(x/(BEAT*4)); r=PROG[bar%4]; f=D(-2,r)
    add(x,sub(f,E8*0.95,0.11 if k%2==0 else 0.07)); x+=E8; k+=1
CH={0:[0,3,7],-4:[-4,0,3],-2:[-2,2,5]}
x=0.0
while x<TOTAL+0.2:
    bar=int(x/(BEAT*4)); r=PROG[bar%4]
    for s_ in CH[r]: add(x,pad(D(-1,s_),BEAT*4+0.8,0.006,0.5,0.8))
    x+=BEAT*4
arp(0.0,TOTAL+0.2,[[0,3,7,12],[0,3,7,12],[-4,0,3,8],[-2,2,5,10]],step=E8/2,amp=0.0045,oct_=1,cl=BEAT*4)
for i in range(int(TOTAL/BEAT)+1):
    if i%2==1: add(i*BEAT,lp(bp(noise(0.08),3000,9000),10000)*np.exp(-T_(0.08)*60)*0.010)
# ---- transitions ----
def riser(at,dur=0.5,amp=0.012): add(at-dur,whoosh(dur,amp,400,4000))
for st,fn,kind in SHOTS[1:]:
    if kind=="whip":
        riser(st,0.45,0.014); add(st-0.05,whoosh(0.4,0.016,600,3000)); add(st,boom(0.05,48,3.0,1.6))
    else:
        add(st,boom(0.028,70,7,0.5)); add(st,click(0.010,1800,160))
riser(TOTAL,0.42,0.014)
# ---- word-synced sfx ----
def tinkle(at,n=6,amp=0.006):
    g=np.random.default_rng(int(at*100))
    for i in range(n): add(at+i*0.05+g.uniform(0,0.03),chime(g.uniform(2500,4200),amp,0.8))
tinkle(wt(0,"glass"),8,0.007); tinkle(wt(5,"glass"),7,0.006); tinkle(wt(6,"drops"),6,0.006)
add(wt(0,"Sideways"),whoosh(0.7,0.02,500,3500)); add(wt(0,"Sideways"),boom(0.06,42,2.5,2.0))
add(wt(1,"marble"),chime(D(2,0),0.006,2.0)); add(wt(2,"water"),boom(0.04,55,4,1.0))
for i in range(12): add(wt(3,"year")+i*0.13,click(0.006,3000,400))
add(wt(4,"1,000"),saw(D(-1,0),1.4,0.006,0.6,0.3,900))
for i in range(10): add(wt(4,"1,000")+i*0.06,click(0.005,2600,400))
amb(150,1800,0.010,Ls(6)-0.15,Ls(7)-0.2,0.3,0.3,0.5,1.3)
for i in range(10): add(wt(6,"4,500")+i*0.05,click(0.005,2600,400))
add(wt(7,"Webb"),beep(1320,0.12,0.010)); add(wt(7,"Webb")+0.18,beep(1760,0.16,0.008))
add(Ls(8),chime(D(1,7),0.010,1.6)); add(Ls(8),boom(0.04,60,5,0.8))
add(wt(8,"rotten"),crack(0.03)); add(wt(8,"stink")-0.05,lp(bp(noise(0.5),200,900),1000)*np.sin(np.pi*T_(0.5)/0.5)*0.010)
add(wt(9,"right"),shimmer(0.006,1.4))
bus=lp(out(),9500); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 0.75
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
