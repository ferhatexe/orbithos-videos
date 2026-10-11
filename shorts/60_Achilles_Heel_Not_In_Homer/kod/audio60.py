import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid60"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sc_(n): s=S(n); return s["s"],s["e"]
Dn=lambda o,s=0:146.83*2**o*2**(s/12)
DOR=[0,2,3,5,7,9,10,12,14,15]
def lute(f,dur=1.5,amp=0.011):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt)*np.exp(-tt*(2.6+k*1.4))/k**1.0 for k in range(1,8))
    return lp(s*amp*np.clip(tt/0.002,0,1),3800)
def recorder(f,dur,amp=0.005):
    tt=T_(dur); vib=1+0.004*np.sin(2*np.pi*5*tt)
    s=np.sin(2*np.pi*np.cumsum(f*vib)/SR)+0.08*np.sin(2*np.pi*np.cumsum(3*f*vib)/SR)+bp(noise(dur),f,f*3)*0.12
    return lp(s*np.clip(tt/0.12,0,1)*np.clip((dur-tt)/0.3,0,1)*amp,4000)
def tabor(amp=0.04): tt=T_(0.5); return (np.sin(2*np.pi*np.cumsum(110*(1+0.3*np.exp(-tt*30)))/SR)*np.exp(-tt*9)+bp(noise(0.5),800,4000)*np.exp(-tt*25)*0.4)*amp
def lute_seq(t0,t1,step=0.33,amp=0.010,seed=0):
    g=np.random.default_rng(seed); x=t0; k=0; base=[0,4,2,5,4,7,5,3]
    while x<t1-0.2:
        n=DOR[(base[k%len(base)]+g.integers(0,2))%len(DOR)]; add(x,lute(Dn(0,n),1.5,amp)); x+=step; k+=1
def rec_line(t0,notes,step=0.6,amp=0.005):
    for i,n in enumerate(notes): add(t0+i*step,recorder(Dn(1,n),step+0.15,amp))
def stitchfx(at,dur=0.76):
    g=np.random.default_rng(int(at*100)); n=10
    for k in range(n):
        x=at+dur*k/n; tt=T_(0.07); add(x,bp(noise(0.07),2500,7000)*np.sin(np.pi*tt/0.07)**2*0.010)
        add(x+0.035,click(0.006,g.uniform(3000,5000),700))
# ---- bed ----
add(0,drone(Dn(-2,0),TOTAL+0.4,0.016,0.3,0.6,280)); add(0,drone(Dn(-1,7),TOTAL+0.4,0.006,0.3,0.6,400))
lute_seq(0.05,TOTAL+0.1,0.33,0.010,1)
rec_line(0.3,[7,5,3,2,0],0.8)
rec_line(S("statius")["s"]+0.2,[0,2,3,5,7,5],0.75)
rec_line(S("later")["s"]+0.2,[3,2,0,-2,0],0.8)
for s_ in SC: add(s_["s"]+0.02,tabor(0.04))
SH=[S("iliad")["s"],Lx("And the poem")[0]-0.3,S("statius")["s"],Lx("His mother")[0]-0.3,Lx("In later")[0]-0.3,Lx("An older")[0]-0.3,S("later")["s"],Lx("And Achilles' heel as")[0]-0.3,Lx("So when")[0]-0.3]
for t_ in SH: stitchfx(t_-0.38)
stitchfx(TOTAL-0.66,0.66)
# ---- events ----
add(0.0,whoosh(0.6,0.016,600,3500)); add(0.6,tabor(0.05)); add(0.6,crack(0.02))
add(EV["homer"],lute(Dn(-1,0),2.0,0.016))
add(EV["spear"]-0.3,whoosh(0.6,0.014,500,3000)); add(EV["graze"],crack(0.02)); add(EV["blood"],lute(Dn(0,1),1.5,0.012))
add(EV["ends"],whoosh(0.8,0.008,2000,600)); add(EV["paris"]+0.2,lp(bp(noise(0.8),300,1200),1300)*np.linspace(0,1,int(0.8*SR))*0.010)
tt=T_(0.4); add(EV["arrow"],np.sin(2*np.pi*np.cumsum(220*(1+0.2*np.exp(-tt*20)))/SR)*np.exp(-tt*8)*0.018); add(EV["arrow"]+0.05,whoosh(0.5,0.016,800,4000)); add(EV["arrow"]+0.5,tabor(0.04))
add(EV["roman"],scribble(1.5,0.006))
add(EV["dipped"]+0.4,lp(bp(noise(0.9),300,3000),3500)*np.exp(-T_(0.9)*5)*0.03); add(EV["dipped"]+0.4,plip(0.02,400,900))
d=Lx("In later")[0]-EV["dipped"]; tt=T_(d); add(EV["dipped"],lp(bp(noise(d),200,1500),1600)*(0.6+0.4*np.sin(2*np.pi*0.3*tt))*0.005)
add(EV["dry"],chime(Dn(2,7),0.010,2.0))
add(EV["arrow2"]-0.4,whoosh(0.5,0.018,800,4000)); add(EV["arrow2"]+0.15,tabor(0.05)); add(EV["arrow2"]+0.15,crack(0.02))
d=S("later")["s"]-EV["older"]+0.3; tt=T_(d); add(EV["older"]-0.3,lp(bp(noise(d),600,5000),6000)*(np.random.default_rng(2).random(len(tt))<0.003)*0.08+lp(noise(d),400)*0.010)
add(EV["tendon"],scribble(1.2,0.006)); add(EV["y1693"],bell(Dn(0,0),0.012,2.5))
add(EV["word"],chime(Dn(2,0),0.010,2.0)); add(EV["c1800"],tabor(0.035))
add(EV["remember"],lute(Dn(-1,0),2.2,0.016))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.6
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
