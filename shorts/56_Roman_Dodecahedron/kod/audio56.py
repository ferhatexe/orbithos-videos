import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid56"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sc_(n): s=S(n); return s["s"],s["e"]
def lyre(f,dur=1.8,amp=0.012):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt)*np.exp(-tt*(2.2+k*1.1))/k**1.1 for k in range(1,7))
    return lp(s*amp*np.clip(tt/0.003,0,1),4200)
def drum(amp=0.05,f=78):
    tt=T_(0.7); x=np.sin(2*np.pi*np.cumsum(f*(1+0.5*np.exp(-tt*30)))/SR)*np.exp(-tt*7)+lp(noise(0.7),400)*np.exp(-tt*18)*0.4
    return x*amp
def lyre_seq(t0,t1,notes,step=0.34,amp=0.010,oct_=1):
    x=t0;k=0
    while x<t1-0.2: add(x,lyre(D(oct_,notes[k%len(notes)]),1.8,amp)); x+=step;k+=1
def tiles_fx(at,dur=0.72,n=46,amp=0.010):
    g=np.random.default_rng(int(at*100))
    for k in range(n):
        x=at+dur*(k/n)**0.9+g.uniform(-0.01,0.01)
        add(x,click(amp*g.uniform(0.6,1.2),g.uniform(1800,4200),g.uniform(450,800)))
        if k%6==0: add(x,pap(amp*0.5))
# ---------------- music bed (D dorian) ----------------
add(0,drone(D(-2,0),TOTAL+0.4,0.020,0.3,0.6,320))
a,b=sc_("hook"); pads(0,b,[[0,3,7],[-2,2,5]],2.5,0.007); lyre_seq(0.05,b,[0,7,3,10,7,2],0.34,0.010)
a,b=sc_("map"); pads(a,b,[[0,3,7],[5,9,12],[-2,2,5]],2.6,0.007); lyre_seq(a,b,[0,3,7,12,10,7],0.28,0.009)
a,b=sc_("clues"); pads(a,b,[[0,3,7],[-2,2,5],[3,7,10],[0,3,7]],2.8,0.007); lyre_seq(a,EV["text"]-0.4,[0,7,3,10,5,2],0.32,0.009)
add(EV["text"]-0.4,cello(D(-2,0),3.2,0.010,0.4,1.0))
a,b=sc_("guess"); pads(a,b,[[5,9,12],[-2,2,5]],2.6,0.007); lyre_seq(a,b,[0,5,9,12,9,5],0.25,0.009)
a,b=sc_("find"); pads(a,EV["solve"],[[5,9,12],[0,4,7],[-2,2,5]],2.6,0.008); lyre_seq(a,EV["solve"],[0,4,7,12,7,4],0.27,0.009)
pads(EV["solve"]-0.2,TOTAL+0.3,[[0,3,7],[-2,2,5]],2.6,0.007); lyre_seq(EV["eighteen"],TOTAL+0.1,[0,7,3,10,7,2],0.34,0.010)
for s_ in SC: add(s_["s"]+0.02,drum(0.045))
# ---------------- tile flips ----------------
SH=[S("map")["s"],S("clues")["s"],EV["graves"]-0.55,Lx("But no surviving")[0]-0.35,S("guess")["s"],S("find")["s"],Lx("Eighteen")[0]-0.3]
for t_ in SH: tiles_fx(t_-0.36)
tiles_fx(TOTAL-0.62,0.62)
# ---------------- events ----------------
for i in range(12): add(EV["twelve"]-0.1+i*0.07,lyre(D(2,[0,2,3,5,7,9,10,12,14,15,17,19][i]),0.8,0.006))
add(EV["hole"],drum(0.03,140)); add(EV["nobody"],cello(D(-1,0),2.0,0.011,0.3,1.0))
add(EV["roman"],bell(D(0,0),0.020,3.0))
g=np.random.default_rng(5)
for k in range(57): add(EV["hundred"]+2.2*(k/57)**0.8,click(0.007,g.uniform(900,1600),250))
add(EV["england"],chime(D(2,7),0.012,1.6)); add(EV["hungary"],chime(D(2,10),0.012,1.6)); add(EV["second"],bell(D(-1,0),0.02,3.0))
for k in range(3): add(EV["every"]+0.2+k*0.25,lyre(D(1,[0,3,7][k]),1.2,0.010))
add(EV["holes"],whoosh(0.9,0.012,300,900))
for k in range(20): add(EV["corner"]+k*0.035,click(0.008,3200,700))
add(EV["graves"],drum(0.05,60)); add(EV["graves"],choir_(D(0,0),1.8,0.010))
for k in range(14): add(EV["hoards"]+0.05+k*0.085+g.uniform(0,0.03),chime(g.uniform(2400,3600),0.006,0.5))
add(EV["treasure"],shimmer(0.012,1.4))
add(EV["text"],scribble(1.0,0.008)); add(EV["mentions"]+0.1,gavel(0.10))
for kk in ("candle","die","tool","charm"): add(EV[kk],lyre(D(1,7),1.0,0.010)); add(EV[kk],click(0.012,2500,500))
add(EV["candle"],whoosh(0.6,0.008,400,1500)); add(EV["pile"],drum(0.04,90))
add(EV["y2023"],drum(0.05,70))
for k in range(5): add(EV["diggers"]+k*0.42,lp(bp(noise(0.25),250,1800),2000)*np.exp(-T_(0.25)*14)*0.012)
add(EV["found"],shimmer(0.014,1.5)); add(EV["found"]+0.1,bell(D(1,0),0.014,2.5))
add(EV["solve"],cello(D(-1,0),2.2,0.012,0.3,1.0)); add(EV["eighteen"],bell(D(-1,0),0.018,3.5))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.2
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
