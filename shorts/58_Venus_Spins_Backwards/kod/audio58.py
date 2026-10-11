import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid58"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sc_(n): s=S(n); return s["s"],s["e"]
E=lambda o,s=0:164.81*2**o*2**(s/12)
INS=[0,1,5,7,8,12,13,17]
def koto(f,dur=1.6,amp=0.012):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt*(1+0.0008*k))*np.exp(-tt*(3.0+k*1.6))/k**0.9 for k in range(1,8))
    s+=bp(noise(dur),f*2,min(f*6,15000))*np.exp(-tt*60)*0.3
    return lp(s*amp*np.clip(tt/0.002,0,1),5000)
def flute(f,dur,amp=0.006):
    tt=T_(dur); vib=1+0.006*np.sin(2*np.pi*5.2*tt)*np.clip((tt-0.3)/0.5,0,1)
    s=np.sin(2*np.pi*np.cumsum(f*vib)/SR)+0.18*np.sin(2*np.pi*np.cumsum(2*f*vib)/SR)+bp(noise(dur),f*0.8,f*2.5)*0.25
    return lp(s*np.clip(tt/0.35,0,1)*np.clip((dur-tt)/0.6,0,1)*amp,3500)
def taiko(amp=0.05):
    tt=T_(0.9); return (np.sin(2*np.pi*np.cumsum(70*(1+0.6*np.exp(-tt*25)))/SR)*np.exp(-tt*5)+lp(noise(0.9),500)*np.exp(-tt*20)*0.5)*amp
def koto_seq(t0,t1,step=0.36,amp=0.010,seed=0,oct_=0):
    g=np.random.default_rng(seed); x=t0
    while x<t1-0.2:
        add(x,koto(E(oct_,INS[g.integers(0,len(INS))]),1.6,amp)); x+=step*(1 if g.random()<0.75 else 2)
def mistfx(at):
    add(at,lp(bp(noise(0.8),400,2500),2600)*np.sin(np.pi*T_(0.8)/0.8)**2*0.010)
# ---- bed ----
add(0,drone(E(-2,0),TOTAL+0.4,0.016,0.3,0.6,300))
a,b=sc_("hook"); koto_seq(0.05,b,0.34,0.010,1); add(0.2,flute(E(1,7),2.6,0.006)); add(3.3,flute(E(1,5),2.6,0.006))
a,b=sc_("spin"); koto_seq(a,b,0.30,0.009,2)
a,b=sc_("twist"); koto_seq(a,b,0.30,0.009,3); add(EV["d117"],flute(E(1,0),3.0,0.006))
a,b=sc_("hell"); add(a,drone(E(-2,1),b-a,0.014,0.5,0.8,400)); koto_seq(a,EV["beneath"],0.22,0.008,4)
a,b=sc_("why"); koto_seq(a,Lx("So if you're")[0],0.4,0.008,5,0); koto_seq(Lx("So if you're")[0],TOTAL+0.1,0.34,0.010,6)
add(Lx("So if you're")[0],flute(E(1,7),3.0,0.006))
for s_ in SC: add(s_["s"]+0.02,taiko(0.045))
SH=[S("spin")["s"],S("twist")["s"],S("hell")["s"],S("why")["s"],Lx("So if you're")[0]-0.3]
for t_ in SH: mistfx(t_-0.38)
mistfx(TOTAL-0.66)
# ---- events ----
add(EV["west"],koto(E(1,12),1.8,0.014)); add(EV["months"],flute(E(0,7),2.0,0.005)); add(EV["back"],whoosh(0.9,0.010,1500,300))
t0=EV["turn"]-0.2; t1=EV["year"]-0.6
for k in range(26): add(t0+(t1-t0)*(k/26)**0.9,click(0.008,900,180))
add(EV["sunorb"]+1.2,koto(E(1,0),1.4,0.012)); add(EV["longer"],taiko(0.04)); add(EV["year"],koto(E(1,7),1.8,0.014))
add(EV["twist"],taiko(0.04)); t0=EV["sunrise"]-0.3; t1=EV["two"]+0.9
for k in range(30): add(t0+(t1-t0)*k/30,click(0.007,800,180))
for k in range(2): add(t0+(t1-t0)*(0.3+0.5*k),chime(E(2,7),0.010,1.6))
add(EV["clouds"],whoosh(2.0,0.014,300,2200)); add(EV["race"],whoosh(1.4,0.012,2200,400))
add(EV["beneath"],boom(0.04,55,3,2.0))
d=EV["lead"]+1.5-EV["beneath"]; tt=T_(d); add(EV["beneath"],lp(bp(noise(d),800,5000),6000)*(np.random.default_rng(1).random(len(tt))<0.004)*np.clip(tt/0.5,0,1)*0.10)
add(EV["lead"],whoosh(1.2,0.008,600,200))
add(EV["impact"]-0.6,whoosh(0.6,0.02,400,2600)); add(EV["impact"],boom(0.08,45,2,2.5)); add(EV["impact"],crack(0.03))
add(EV["tides"],whoosh(1.8,0.010,200,700)); add(EV["nobody"],koto(E(0,1),1.6,0.012))
add(EV["patient"],chime(E(1,7),0.012,2.2))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.2
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.78)
