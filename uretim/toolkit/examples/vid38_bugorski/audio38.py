import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid38"); sys.path.insert(0,"/home/claude/toolkit")
from scipy.signal import butter, sosfilt
import scipy.io.wavfile as wf
import ev, master
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
SR=44100; N=int((TOTAL+0.5)*SR); t=np.arange(N)/SR; rng=np.random.default_rng(36)
def lp(x,f): return sosfilt(butter(2,f/(SR/2),'low',output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f/(SR/2),'high',output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a/(SR/2),b/(SR/2)],'band',output='sos'),x)
out=np.zeros(N)
def add(at,sig,g=1.0):
    i=int(at*SR)
    if i<0: sig=sig[-i:]; i=0
    L=min(len(sig),N-i)
    if L>0: out[i:i+L]+=sig[:L]*g
def T_(d): return np.arange(int(d*SR))/SR
def noise(d): return rng.normal(0,1,int(d*SR))
def boom(amp=1.0,f0=55,dec=1.6,dur=3.0):
    tt=T_(dur); f=f0*0.6+f0*0.8*np.exp(-tt*5)
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*dec)+lp(rng.normal(0,1,len(tt)),220)*np.exp(-tt*dec*1.5)*0.5)*amp*np.clip(tt/0.03,0,1)
def pad(f,dur,amp=0.03,att=0.8,rel=1.0):
    tt=T_(dur); s=np.sin(2*np.pi*f*tt)+0.35*np.sin(2*np.pi*f*2.002*tt+1)+0.12*np.sin(2*np.pi*f*3.003*tt)+0.25*np.sin(2*np.pi*f*0.998*tt)
    return lp(s*np.clip(tt/att,0,1)*np.clip((dur-tt)/rel,0,1)*amp,3500)
def kal(f,dur=1.6,amp=0.05):   # kalimba / marimba-like pluck
    tt=T_(dur); s=np.sin(2*np.pi*f*tt)*np.exp(-tt*3.2)+0.35*np.sin(2*np.pi*f*4.0*tt)*np.exp(-tt*14)+0.15*np.sin(2*np.pi*f*2.0*tt)*np.exp(-tt*6)
    return lp(s*amp*np.clip(tt/0.004,0,1),5000)
def plip(amp=0.06,f0=700,f1=1500):  # water-drop motif
    tt=T_(0.35); f=f0+(f1-f0)*np.clip(tt/0.05,0,1); s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*22)
    ring=np.sin(2*np.pi*f1*0.5*tt)*np.exp(-tt*9)*0.25
    return lp((s+ring)*amp*np.clip(tt/0.002,0,1),4500)
def whoosh(dur,amp,lo=300,hi=1800,sweep=True):
    L=int(dur*SR); tt=np.arange(L)/SR; x=rng.normal(0,1,L)
    if sweep:
        y=np.zeros(L); seg=int(SR*0.05)
        for i in range(0,L,seg):
            u=i/L; f=lo+(hi-lo)*u; y[i:i+seg]=bp(x[max(0,i-seg):i+seg],max(60,f*0.6),min(f*1.6,6000))[-len(x[i:i+seg]):]
        x=y
    else: x=bp(x,lo,hi)
    return lp(x,3000)*np.sin(np.pi*tt/dur)**2*amp
def pap(amp=0.05): tt=T_(0.09); return lp(bp(rng.normal(0,1,len(tt)),250,1600),1800)*np.exp(-tt*55)*amp+np.sin(2*np.pi*140*tt)*np.exp(-tt*40)*amp*0.6
def chime(f,amp=0.04,dur=2.5):
    tt=T_(dur); s=sum(a*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*d) for a,r,d in ((1,1,1.4),(0.4,2.76,3),(0.2,5.4,6)))
    return lp(s*amp*np.clip(tt/0.003,0,1),5000)
def chirp_bird(amp=0.02):
    tt=T_(0.18); f=1800+900*np.sin(np.pi*tt/0.18)+300*np.sin(2*np.pi*28*tt); return lp(np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*tt/0.18)**2*amp,4000)
def drone(f,dur,amp,att=1.5,rel=1.5,cut=600):
    tt=T_(dur); ph=2*np.pi*f*tt; s=sum(np.sin(ph*k)/k for k in range(1,7))*(1+0.15*np.sin(2*np.pi*0.2*tt))
    return lp(s*np.clip(tt/att,0,1)*np.clip((dur-tt)/rel,0,1)*amp,cut)
def amb(lo,hi,amp,t0,t1,fi=1.0,fo=1.0,mod=0.0,modf=0.3):
    d=t1-t0; tt=T_(d); x=lp(bp(rng.normal(0,1,len(tt)),lo,hi),hi*1.2)*np.clip(tt/fi,0,1)*np.clip((d-tt)/fo,0,1)*amp
    if mod: x*=1+mod*np.sin(2*np.pi*modf*tt+rng.uniform(0,6))
    add(t0,x)
nt=lambda s:440*2**((s-9)/12)   # semitone index relative to C (0=C4? -> A4=9)
D=lambda o,s=0:146.83*2**(o)*2**(s/12)
def sec(name): s=S(name); return s["s"],s["e"]
def timp(f=73.4,amp=0.25,dur=2.2):
    tt=T_(dur); s=np.sin(2*np.pi*f*tt*(1+0.04*np.exp(-tt*8)))*np.exp(-tt*2.2)+lp(rng.normal(0,1,len(tt)),300)*np.exp(-tt*12)*0.3
    return s*amp*np.clip(tt/0.005,0,1)
def strings(f,dur,amp=0.02,att=1.2,rel=1.2):
    tt=T_(dur); s=sum(np.sign(np.sin(2*np.pi*f*d*tt))*0.3+np.sin(2*np.pi*f*d*tt) for d in (0.997,1.0,1.004))
    return lp(s*np.clip(tt/att,0,1)*np.clip((dur-tt)/rel,0,1)*amp*(1+0.05*np.sin(2*np.pi*5.5*tt)),1800)
def choir(f,dur,amp=0.02,att=1.0,rel=1.5):
    tt=T_(dur); src=sum(np.sin(2*np.pi*f*k*tt*(1+0.003*np.sin(2*np.pi*4.8*tt)))/k for k in range(1,12))
    s=bp(src,500,1100)*1.4+bp(src,200,450)*0.8
    return lp(s*np.clip(tt/att,0,1)*np.clip((dur-tt)/rel,0,1)*amp,3000)
def ostinato(t0,t1,root,amp=0.05,step=0.25,pat=(0,0,12,0,7,0,10,0)):
    x=t0;k=0
    while x<t1-0.2:
        tt=T_(0.24); f=D(-2,root+pat[k%len(pat)]); s=lp((np.sign(np.sin(2*np.pi*f*tt))*0.5+np.sin(2*np.pi*f*tt))*np.exp(-tt*9),700)
        add(x,s*amp); x+=step; k+=1
def geiger(t0,t1,rate,amp=0.02):
    x=t0
    while x<t1:
        add(x,lp(bp(noise(0.004),800,3000),3200)*amp); x+=rng.exponential(1/rate)
def clank(amp=0.06):
    tt=T_(0.8); s=sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*dd) for f,dd in ((180,5),(410,8),(970,12),(1530,18)))
    return lp(s*amp*np.clip(tt/0.002,0,1),3500)
# ---------- music ----------
a,b=sec("hook"); add(a,strings(D(-1,0),b-a+0.5,0.02,2,1)); add(a,strings(D(-1,7),b-a+0.5,0.014,2,1))
add(EV["y1978"],timp(73.4,0.3)); add(EV["protons"],timp(73.4,0.25)); add(EV["suns"]-0.4,choir(D(0,0),4.0,0.03,0.4,2.0)); add(EV["suns"]-0.4,choir(D(0,7),4.0,0.022,0.4,2.0))
add(EV["didnt"],timp(55,0.35,3.0)); add(EV["didnt"],choir(D(0,4),3.0,0.02,0.2,2.0))
a,b=sec("lab"); ostinato(a+0.2,b,0,0.045); add(a,choir(D(-1,0),b-a,0.015,1.5,1.0))
for x in np.arange(a+0.2,b,2.0): add(x,timp(73.4,0.12,1.2))
a,b=sec("accident"); ostinato(a,EV["path"]-0.2,1,0.04,0.2,(0,0,1,0,6,0,1,0)); add(a,strings(D(0,1),b-a,0.016,1.0,0.6)); add(a,strings(D(0,6),b-a,0.012,1.0,0.6))
a,b=sec("beam"); add(a,strings(D(-1,0),b-a,0.018,1.0,1.0))
for e in (EV["entered"],EV["five"],EV["two"],EV["three"]): add(e,timp(65,0.25,1.8))
for k,s_ in enumerate((0,3,7,10)): add(EV["yet"]+k*0.6,kal(D(1,s_),1.6,0.025))
a,b=sec("after"); add(a,strings(D(-1,0),b-a,0.02,1.5,1.0)); add(a,strings(D(-1,3),b-a,0.015,1.5,1.0)); add(a,strings(D(0,8),b-a,0.010,2,1.0))
a,b=sec("survive"); add(a-0.2,timp(73.4,0.4,3.0))
for s_ in (0,4,7,12): add(a,choir(D(0,s_),b-a+0.6,0.016,0.6,1.5))
for k,s_ in enumerate((0,4,7,12,16,19)): add(EV["narrow"]+k*0.25,kal(D(1,s_),1.5,0.022))
a,b=sec("cost"); 
for x,s_ in zip(np.arange(a+0.3,b,1.4),[0,3,7,3,-2,0,3,8,7,3,0,-2]): add(x,kal(D(0,s_),2.0,0.03))
add(a,strings(D(-1,0),b-a,0.014,1.5,1.0))
a,b=sec("mind"); 
for k in range(int((b-a)/0.3)): add(a+0.2+k*0.3,kal(D(1,[0,4,7,11,12,11,7,4][k%8]),1.0,0.022))
for s_ in (0,4,7): add(a,choir(D(0,s_),b-a+0.5,0.012,1.0,1.0))
a,b=sec("end"); tf=Lx("He saw a light")[1]+0.6
for s_ in (0,4,7,12): add(a,choir(D(0,s_),b-a+0.6,0.016,1.0,2.5))
add(EV["lightb"]-0.3,timp(73.4,0.3,3.0)); add(tf,timp(55,0.3,3.0))
for f in (D(1,0),D(1,7),D(2,4)): add(tf+0.05,chime(f,0.03,3.0))
# ---------- sfx ----------
for s_ in SC[1:]:   # constructivist band wipe: whoosh + metal clank
    b_=s_["s"]; add(b_-0.3,whoosh(0.6,0.06,300,1600)); add(b_,clank(0.05))
amb(40,200,0.02,0,S("accident")["e"],2,1)   # accelerator hum bed
tt=T_(S("accident")["e"]); add(0,lp(np.sin(2*np.pi*50*tt)+0.4*np.sin(2*np.pi*100*tt),300)*0.012)
add(EV["protons"]-0.3,whoosh(1.2,0.06,300,2400)); add(EV["flash"],lp(bp(noise(2.5),200,3000),3200)*np.exp(-T_(2.5)*1.6)*0.10); add(EV["flash"],boom(0.4,45,1.2,3.0))
for e in (EV["y1978"],EV["light"],EV["nopain"],EV["expected"]): add(e,clank(0.03))
a,b=sec("lab")
for k in range(10): 
    x=EV["u70"]+k*0.6; add(x,whoosh(0.6,0.025,500+k*80,1500+k*120))
geiger(EV["push"],b,6,0.025)
a,b=sec("accident")
for e in (EV["failed"],EV["failed"]+0.25,EV["failed"]+0.5): add(e,lp(np.sin(2*np.pi*300*T_(0.25))*np.exp(-T_(0.25)*6),900)*0.05); add(e,clank(0.04))
geiger(EV["running"],b+0.5,15,0.025)
tt=T_(1.8); kl=lp(np.sign(np.sin(2*np.pi*np.where((tt*2.5)%1<0.5,440,350)*tt)),1400)*0.025*np.clip((1.8-tt)/0.3,0,1); add(EV["path"]-0.05,kl)
a,b=sec("beam"); geiger(a,EV["five"],25,0.02)
add(EV["entered"],whoosh(1.6,0.06,300,2200)); add(EV["back"],boom(0.25,60,4,1.2)); add(EV["nose"],boom(0.25,70,4,1.2))
for e in (EV["two"],EV["three"]): add(e,whoosh(1.0,0.04,200,1200))
tt=T_(3.0); add(EV["yet"],lp(np.sign(np.sin(2*np.pi*2*tt))*np.exp(-((tt*2)%1)*60),2000)*0.02)
a,b=sec("after"); 
for x in np.arange(EV["obs"],b+0.3,0.5): add(x,lp(np.sin(2*np.pi*1000*T_(0.08))*np.exp(-T_(0.08)*25),2500)*0.010)
add(EV["peeled"],lp(bp(noise(2.0),400,2000),2200)*np.sin(np.pi*T_(2.0)/2.0)*0.025)
a,b=sec("survive"); add(EV["butnot"]-0.1,lp(bp(noise(1.5),200,2500),2800)*np.exp(-T_(1.5)*2)*0.06)
add(EV["thin"],whoosh(0.8,0.03,800,2500))
a,b=sec("cost")
for e in (EV["ear"],EV["paral"],EV["seiz"],EV["tired"]): add(e,clank(0.04))
tt=T_(2.0); add(EV["ear"]+0.3,np.sin(2*np.pi*3200*tt)*np.clip(tt/0.3,0,1)*np.clip((2-tt)/0.8,0,1)*0.003)
add(EV["seiz"],lp(bp(noise(0.6),200,1500),1600)*np.exp(-T_(0.6)*5)*0.06)
tt=T_(1.0); add(EV["tired"],lp(np.sin(2*np.pi*np.cumsum(400-250*tt)/SR)*np.exp(-tt*2),1500)*0.025)
a,b=sec("mind"); add(EV["intact"],chime(D(2,0),0.04)); add(EV["phd"],chime(D(2,7),0.04)); add(EV["s77"],chime(D(2,12),0.035))
for k in range(6): add(EV["back2"]+0.1+k*0.1,clank(0.012))
a,b=sec("end"); add(EV["only"],clank(0.04)); add(EV["lightb"]-0.2,lp(bp(noise(2.5),300,3000),3200)*np.sin(np.pi*T_(2.5)/2.5)*0.05)
# ======================== MASTER ========================
bus=lp(out,9000)
vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
master.master(vo,bus,SR,"mix.wav",bus_gain=0.55)
