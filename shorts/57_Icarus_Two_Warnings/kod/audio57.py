import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid57"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sc_(n): s=S(n); return s["s"],s["e"]
A=lambda o,s=0:220*2**o*2**(s/12)
def lyre(f,dur=1.8,amp=0.012):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt)*np.exp(-tt*(2.0+k*1.0))/k**1.1 for k in range(1,7))
    return lp(s*amp*np.clip(tt/0.003,0,1),4200)
def lyre_seq(t0,t1,notes,step=0.34,amp=0.010,oct_=0):
    x=t0;k=0
    while x<t1-0.2: add(x,lyre(A(oct_,notes[k%len(notes)]),1.8,amp)); x+=step;k+=1
def apads(t0,t1,chords,cl=2.6,amp=0.007):
    x=t0;k=0
    while x<t1-0.3:
        for s_ in chords[k%len(chords)]: add(x,pad(A(-1,s_),min(cl+1.0,t1-x+0.5),amp,0.7,1.0))
        x+=cl;k+=1
def flap(at,amp=0.010):
    tt=T_(0.28); add(at,lp(bp(noise(0.28),180,1400),1500)*np.sin(np.pi*tt/0.28)**2*amp)
def flaps(t0,t1,rate=1.15,amp=0.010):
    x=t0
    while x<t1: flap(x,amp); x+=1/rate
def waves(t0,t1,amp=0.006):
    d=t1-t0; tt=T_(d); x=lp(bp(noise(d),150,1500),1600)*(0.6+0.4*np.sin(2*np.pi*0.28*tt))*np.clip(tt/0.6,0,1)*np.clip((d-tt)/0.6,0,1)*amp; add(t0,x)
def lampfx(at):
    tt=T_(0.75); g=lp(noise(0.75),300)*np.exp(-((tt-0.3)/0.12)**2)*0.6+bp(noise(0.75),1500,5000)*(np.random.default_rng(int(at*10)).random(len(tt))<0.0009)*2.0
    add(at,g*0.03); add(at+0.36,whoosh(0.4,0.010,200,900))
# ---- music bed: A phrygian-dorian lyre ----
add(0,drone(A(-2,0),TOTAL+0.4,0.018,0.3,0.6,320))
a,b=sc_("hook"); apads(0,b,[[0,3,7],[1,5,8]],2.4); lyre_seq(0.05,b,[0,7,3,12,8,7],0.30,0.010)
a,b=sc_("crete"); apads(a,b,[[0,3,7],[-2,1,5],[1,5,8],[0,3,7]],2.8); lyre_seq(a,b,[0,3,7,8,7,3],0.34,0.009)
a,b=sc_("warn"); apads(a,b,[[0,3,7],[5,8,12],[3,7,10]],2.8); lyre_seq(a,b,[0,7,12,7,3,7],0.30,0.009)
a,b=sc_("fall"); apads(a,EV["fell"],[[0,3,7],[1,5,8],[3,7,10],[5,8,12]],2.4); lyre_seq(a,EV["fell"],[0,3,7,12,15,12,7,3],0.20,0.009)
apads(EV["fell"],b,[[0,3,7],[-2,1,5]],2.6,0.008); add(EV["fell"]+0.3,cello(A(-2,0),3.2,0.011,0.3,1.2))
lyre_seq(EV["buried"],b,[0,3,7,3],0.6,0.008)
a,b=sc_("moral"); apads(a,TOTAL+0.3,[[0,3,7],[1,5,8]],2.5); lyre_seq(a,TOTAL+0.1,[0,7,3,12,8,7],0.30,0.009)
# ---- lamp transitions ----
SH=[S("crete")["s"],Lx("So he built")[0]-0.35,S("warn")["s"],S("fall")["s"],Lx("But Icarus")[0]-0.3,Lx("His father")[0]-0.3,S("moral")["s"]]
for t_ in SH: lampfx(t_-0.36)
lampfx(TOTAL-0.62)
# ---- events ----
flaps(0.2,S("hook")["e"]-0.3); waves(0,S("hook")["e"]); add(EV["two"],lyre(A(1,7),1.6,0.014)); add(EV["two"]+0.15,lyre(A(1,12),1.6,0.012))
add(EV["daed"],bell(A(-1,0),0.016,2.5)); add(EV["minos"],cello(A(-2,1),1.6,0.012,0.2,0.8)); add(EV["crete"],drone(A(-2,0),2.0,0.012,0.2,1.0,240))
for k in range(9): add(EV["feathers"]+k*(EV["long"]-EV["feathers"]+0.4)/9,whoosh(0.18,0.004,1200,3000))
add(EV["pipes"],sum(pad(A(1,s_),1.4,0.004,0.1,0.6) for s_ in (0,3,7)))
add(EV["thread"],whoosh(0.5,0.006,2000,5000)); add(EV["wax"],plip(0.02,400,700))
add(EV["high"],shimmer(0.010,1.2)); add(EV["melt"],whoosh(0.8,0.008,800,300))
waves(EV["low"]-0.3,S("warn")["e"],0.007); add(EV["drag"],boom(0.04,60,4,1.2)); add(EV["middle"],chime(A(1,7),0.012,2.0))
flaps(S("warn")["s"]+0.2,S("warn")["e"]-0.2,1.0,0.007)
waves(S("fall")["s"],EV["climb"]-0.5,0.006); add(EV["gods"],choir_(A(0,7),1.8,0.010)); add(EV["gods"],choir_(A(0,0),1.8,0.008))
flaps(EV["climb"]-0.8,EV["soft"],1.6,0.010); add(EV["soft"],whoosh(1.0,0.008,600,250))
for k in range(9): add(EV["soft"]+k*0.12,whoosh(0.3,0.004,1500,600))
tf=EV["fell"]-0.4; add(tf,whoosh(0.9,0.022,2500,300)); add(tf+0.9,boom(0.05,70,6,1.0)); add(tf+0.9,lp(bp(noise(1.2),300,4000),4500)*np.exp(-T_(1.2)*4)*0.03)
waves(tf+0.9,S("fall")["e"],0.008)
add(EV["icarian"],bell(A(-1,7),0.014,2.5)); add(EV["buried"],bell(A(-2,0),0.018,3.5))
waves(S("moral")["s"],TOTAL,0.005); flaps(S("moral")["s"]+0.3,TOTAL-0.7,1.0,0.006)
add(EV["deadly"],boom(0.035,60,5,1.0))
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.2
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.75)
