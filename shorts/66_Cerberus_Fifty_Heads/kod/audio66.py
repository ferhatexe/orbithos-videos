import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid66"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
Dm=lambda o,s=0:146.83*2**o*2**(s/12)
def pizz(f,amp=0.012):
    tt=T_(0.6); s=(np.sin(2*np.pi*f*tt)+0.4*np.sin(2*np.pi*2*f*tt)+0.2*np.sin(2*np.pi*3*f*tt))*np.exp(-tt*9)
    return lp(s*amp*np.clip(tt/0.002,0,1),3000)
def timp(amp=0.04,f=73.4): tt=T_(1.0); return (np.sin(2*np.pi*f*tt)*np.exp(-tt*3.5)+lp(noise(1.0),400)*np.exp(-tt*25)*0.4)*amp
def stab(ch,amp=0.006): return sum(saw(Dm(0,s_),0.35,amp,0.01,0.2,2200) for s_ in ch)
def growl(at,dur=1.0,amp=0.03):
    tt=T_(dur); x=lp(bp(noise(dur),60,500),600)*(0.6+0.4*np.sin(2*np.pi*22*tt))*np.sin(np.pi*tt/dur); add(at,x*amp)
mel=[0,3,7,5,3,2,0,-2]; beat=0.30; x=0.0;k=0
while x<TOTAL-0.2:
    add(x,pizz(Dm(0,mel[k%8]),0.010)); 
    if k%4==0: add(x,pizz(Dm(-1,[0,-4,-2,-5][(k//8)%4]),0.016))
    x+=beat;k+=1
add(0,drone(Dm(-2,0),TOTAL+0.4,0.012,0.4,0.8,250))
def slidefx(at): add(at,whoosh(0.5,0.016,600,4500)); add(at+0.3,timp(0.03))
SH=[S("heads")["s"],Lx("His brother")[0]-0.3,Lx("The poet Pindar")[0]-0.3,Lx("Artists")[0]-0.3,S("job")["s"],Lx("Heracles")[0]-0.3,Lx("Orpheus")[0]-0.3,S("sop")["s"],Lx("Beaten")[0]-0.3,Lx("That's the origin")[0]-0.3,Lx("So whenever")[0]-0.3]
for t_ in SH: slidefx(t_-0.34)
slidefx(TOTAL-0.6)
growl(EV["three"]-0.6,1.0); add(EV["fifty"]-0.2,stab([0,3,7])); add(EV["fifty"],timp(0.05))
add(EV["fiftyh"],stab([0,3,7])); add(EV["bronze"],bell(Dm(-1,0),0.016,2.0))
add(EV["orthrus"],pizz(Dm(1,7),0.014)); add(EV["hydra"],lp(bp(noise(0.8),2000,6000),6000)*np.exp(-T_(0.8)*3)*0.010)
add(EV["hundred"]-0.2,stab([0,4,7,12],0.008)); add(EV["hundred"],timp(0.05)); growl(EV["hundred"],1.2,0.035)
add(EV["two"],pizz(Dm(1,0),0.014)); add(EV["threex"],pizz(Dm(1,7),0.014))
add(EV["deadin"],chime(Dm(2,7),0.008,1.4)); add(EV["leave"],crack(0.04)); add(EV["leave"],timp(0.05,110))
add(EV["dragged"],whoosh(0.8,0.012,200,900)); add(EV["dragged"]+0.3,timp(0.04)); add(EV["labor"],stab([0,4,7]))
for i,n in enumerate([7,9,12,14,12]): add(EV["orpheus"]+0.3+i*0.28,kal(Dm(2,n),1.4,0.012))
tt=T_(1.4); add(EV["music"]+0.6,lp(saw(70,1.4,0.010,0.2,0.4,500)*(0.5+0.5*np.sin(2*np.pi*0.7*tt)),600))
add(EV["cake"]-0.5,whoosh(0.6,0.012,800,3000)); add(EV["cake"]+0.2,plip(0.02,500,900))
for i,k_ in enumerate(("strength","music2","snack")): add(EV[k_],stab([[0,3,7],[2,5,9],[3,7,10]][i],0.006)); add(EV[k_],timp(0.03))
add(EV["sop"],chime(Dm(2,0),0.010,2.0)); add(EV["remember"],timp(0.05)); growl(EV["picture"],0.9,0.025)
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.9
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
