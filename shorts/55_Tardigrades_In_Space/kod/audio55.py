import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid55"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
def labhum(t0,t1,amp=0.006):
    d=t1-t0; tt=T_(d); x=(np.sin(2*np.pi*100*tt)+0.3*np.sin(2*np.pi*300*tt))*(1+0.1*np.sin(2*np.pi*0.3*tt))+bp(rng.normal(0,1,len(tt)),2000,5000)*0.15
    add(t0,x*np.clip(tt/0.4,0,1)*np.clip((d-tt)/0.4,0,1)*amp)
def bloop(at,f=500,amp=0.02):
    tt=T_(0.3); add(at,np.sin(2*np.pi*np.cumsum(f*(1+0.8*np.exp(-tt*20)))/SR)*np.exp(-tt*9)*amp)
def pluck_seq(t0,t1,notes,step=0.3,amp=0.012,oct_=1):
    x=t0;k=0
    while x<t1-0.2: add(x,kal(D(oct_,notes[k%len(notes)]),1.2,amp)); x+=step;k+=1
labhum(0,TOTAL+0.4,0.005)
a,b=sec("hook"); pads(0,b,[[0,4,7,11],[2,5,9,12]],2.6,0.008); pluck_seq(0.0,b,[0,7,4,11,7,2],0.3,0.010)
a,b=sec("meet"); pads(a,b,[[0,4,7,11],[5,9,12,16],[-3,0,4,7]],2.6,0.008); pluck_seq(a,EV["bad"],[0,4,7,9,7,4],0.26,0.011)
add(EV["bad"],drone(D(-2,-1),b-EV["bad"],0.018,0.5,0.6,360))
a,b=sec("space"); add(a,drone(D(-3,0),EV["back"]-a,0.03,0.5,0.5,260)); pads(a,EV["back"],[[0,3,7],[-2,3,7]],3.0,0.007)
pads(EV["back"],b,[[0,4,7,11],[5,9,12,16]],2.4,0.009); pluck_seq(EV["woke"],b,[0,4,7,12,16,12,7,4],0.18,0.010)
a,b=sec("moon"); add(a,drone(D(-3,0),EV["whyis"]-a,0.028,0.5,0.5,260)); pads(a,EV["whyis"],[[0,3,7],[-4,0,3]],2.8,0.008)
pads(EV["whyis"]-0.2,TOTAL+0.2,[[0,4,7,11]],2.6,0.008); pluck_seq(EV["whyis"],TOTAL+0.1,[0,7,4,11,7,2],0.3,0.010)
# ---------------- sfx ----------------
for s_ in SC[1:]: add(s_["s"]-0.34,whoosh(0.7,0.03,300,3000)); bloop(s_["s"],800,0.012)
add(TOTAL-0.6,whoosh(0.7,0.03,300,3000))
add(EV["naked"],boom(0.04,90,6,0.6)); add(EV["suit"],beep(700,0.07,0.012)); add(EV["ship"],beep(820,0.07,0.012)); add(EV["half"],bloop(EV["half"],600,0.015) or np.zeros(1)); add(EV["how"],chime(D(2,4),0.012,1.8))
add(EV["tardi"],bloop(EV["tardi"],400,0.02) or np.zeros(1))
for k in range(8): add(EV["legs"]+k*0.08,lp(bp(noise(0.05),600,2500),3000)*np.exp(-T_(0.05)*60)*0.02)
add(EV["dries"],whoosh(1.0,0.02,3000,600)); add(EV["tun"],bloop(EV["tun"],300,0.025) or np.zeros(1)); add(EV["shuts"],cello(D(-2,0),1.6,0.012,0.1,1.0))
add(EV["y2007"],pap(0.025)); add(EV["opened"],whoosh(1.2,0.03,2500,200))
for k in range(12): add(EV["cosmic"]+k*0.15,click(0.012,4000,400))
add(EV["water"],plip(0.04,500,1200)); add(EV["water"]+0.15,plip(0.03,700,1500)); add(EV["woke"],shimmer(0.018,1.6))
for k in range(5): bloop(EV["eggs"]+k*0.1,900+k*80,0.010)
add(EV["y2019"],pap(0.025)); add(EV["crashed"]-0.6,whoosh(0.8,0.04,300,2500)); add(EV["crashed"],boom(0.13,40,1.4,3.0)); add(EV["crashed"],crack(0.05))
add(EV["thousands"],shimmer(0.012,1.4)); add(EV["nobody"],cello(D(-1,1),1.4,0.012,0.1,0.8)); add(EV["without"],plip(0.02,400,700))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
