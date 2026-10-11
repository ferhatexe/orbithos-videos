import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid40"); sys.path.insert(0,"/home/claude/toolkit")
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
def lyre(f,dur=2.2,amp=0.04):
    tt=T_(dur); s=sum(a_*np.sin(2*np.pi*f*(k+1)*tt)*np.exp(-tt*(1.6+k*1.3)) for k,a_ in enumerate([1,.55,.3,.15,.08]))
    return lp(s*amp*np.clip(tt/0.004,0,1),5000)
def aulos(f,dur,amp=0.02,att=0.15):
    tt=T_(dur); ph=2*np.pi*np.cumsum(f*(1+0.006*np.sin(2*np.pi*5.5*tt)))/SR
    s=sum(np.sin(ph*k)/k*(1 if k%2 else 0.5) for k in range(1,9))
    return lp(s*np.clip(tt/att,0,1)*np.clip((dur-tt)/0.25,0,1)*amp,2800)
def drum(amp=0.12):
    tt=T_(0.5); return (np.sin(2*np.pi*np.cumsum(90+60*np.exp(-tt*25))/SR)*np.exp(-tt*9)+lp(rng.normal(0,1,len(tt)),900)*np.exp(-tt*30)*0.4)*amp
def clink(amp=0.04,f=1300):
    tt=T_(0.6); return lp(sum(np.sin(2*np.pi*f*r*tt)*np.exp(-tt*d) for r,d in ((1,8),(2.4,14),(3.9,20)))*amp*np.clip(tt/0.002,0,1),4200)
DOR=[0,2,3,5,7,9,10,12,14,15]
def lyre_line(t0,t1,step,amp,pat,root=0,oct=1):
    x=t0;k=0
    while x<t1-0.3:
        add(x,lyre(D(oct,root+DOR[pat[k%len(pat)]]),1.8,amp)); x+=step; k+=1
def drums(t0,t1,amp=0.08,step=0.6,pat=(1,0,0.5,0)):
    x=t0;k=0
    while x<t1-0.2:
        if pat[k%len(pat)]>0: add(x,drum(amp*pat[k%len(pat)]))
        x+=step; k+=1
# ---------- music ----------
a,b=sec("hook"); add(a+0.2,aulos(D(0,0),b-a,0.014,1.0)); lyre_line(a+0.3,b,0.5,0.03,[0,2,4,2,1,0,1,2])
a,b=sec("fire"); lyre_line(a,b,0.4,0.03,[0,2,4,5,4,2,7,4]); drums(a+0.2,b,0.06,0.4,(1,0,0.6,0)); add(a,aulos(D(-1,0),b-a,0.010,1.0))
add(EV["stole"],aulos(D(1,7),2.0,0.016,0.1))
a,b=sec("punish"); add(a,drone(D(-2),b-a,0.035,1.0,1.0,280)); drums(a+0.2,EV["heracles"]-0.4,0.07,0.8,(1,0,0,0.5))
for x in np.arange(a+0.3,EV["heracles"]-0.4,1.6): add(x,lyre(D(0,[0,1,0,-2][int((x-a)/1.6)%4]),2.0,0.03))
for k,s_ in enumerate((0,4,7,12)): add(EV["free"]+k*0.15,lyre(D(1,s_),2.2,0.035))
a,b=sec("science"); 
for x in np.arange(a+0.2,b-0.3,0.3): add(x,lyre(D(1,[0,4,7,9,7,4][int((x-a)/0.3)%6]),1.2,0.018))
for s_ in (0,4,7): add(a,pad(D(-1,s_),b-a,0.010,1.5,1.0))
a,b=sec("knew"); lyre_line(a,b,0.55,0.026,[0,3,5,3,7,5,3,1],root=0)
add(a,aulos(D(0,3),b-a,0.010,1.0))
a,b=sec("end"); lyre_line(a,b-1.5,0.45,0.03,[0,2,4,7,4,2]); tf=Lx("Maybe the myth")[1]+0.6
for k,s_ in enumerate((0,7,12,16)): add(tf+k*0.12,lyre(D(0,s_),3.0,0.035))
add(tf,aulos(D(0,0),3.0,0.014,0.3)); add(tf,drum(0.15))
# ---------- sfx ----------
for s_ in SC[1:]:   # vase rotation: pottery clink + rotating swish
    b_=s_["s"]; add(b_-0.35,whoosh(0.7,0.05,300,1500)); add(b_,clink(0.035,1100))
a,b=sec("hook")
for k in range(4): add(EV["eagle"]-0.3+k*0.28,lp(bp(noise(0.18),200,1500),1600)*np.sin(np.pi*T_(0.18)/0.18)*0.05)
add(EV["liver"],drum(0.12)); add(EV["night"],pad(D(1,7),1.5,0.012,0.1,1.0)); add(EV["grew"],chime(D(2,0),0.025,2.0)); add(EV["prom"],drum(0.15))
a,b=sec("fire"); add(EV["zeus"],boom(0.35,45,1.2,3.0)); add(EV["zeus"]+0.05,lp(bp(noise(1.2),200,1600),1800)*np.exp(-T_(1.2)*3)*0.06)
tt=T_(EV["withfire"]-EV["stole"]+0.3); add(EV["stole"],lp(bp(rng.normal(0,1,len(tt)),150,900),1000)*np.clip(tt/0.4,0,1)*0.02)
tt=T_(b-EV["withfire"]+0.3); add(EV["withfire"]-0.2,lp(bp(rng.normal(0,1,len(tt)),120,1000),1100)*np.clip(tt/0.4,0,1)*np.clip((b-EV["withfire"]-tt)/0.5,0,1)*0.035)
add(EV["cook"],pap(0.04)); 
for k in range(3): add(EV["forge"]+k*0.22,clink(0.03,900+k*40))
a,b=sec("punish")
for k in range(6): add(EV["chained"]+k*0.09,clink(0.018,1500+k*70))
for k in range(5): add(EV["eagle2"]-0.2+k*0.28,lp(bp(noise(0.18),200,1500),1600)*np.sin(np.pi*T_(0.18)/0.18)*0.05)
for x in np.arange(EV["immortal"]-0.2,EV["ages"]-0.3,1.5): add(x,whoosh(1.4,0.02,150,700))
add(EV["arrow"]-0.1,whoosh(0.35,0.05,800,2500)); add(EV["arrow"]+0.2,drum(0.14)); add(EV["free"],chime(D(2,4),0.03))
for k in range(6): add(EV["free"]+0.05+k*0.07,clink(0.015,1700-k*60))
a,b=sec("science"); add(EV["best"],chime(D(2,0),0.03)); add(EV["twothirds"],lp(bp(noise(0.5),600,2200),2400)*np.sin(np.pi*T_(0.5)/0.5)*0.03)
tt=T_(2.5); add(EV["months"],lp(np.sin(2*np.pi*np.cumsum(200+300*tt/2.5)/SR)*np.sin(np.pi*tt/2.5),1500)*0.02)
add(EV["both"],chime(D(2,4),0.025)); add(EV["both"]+0.15,chime(D(2,7),0.022))
for x in np.arange(EV["divide"],EV["stop"],0.18): add(x+rng.uniform(0,0.05),lp(np.sin(2*np.pi*rng.uniform(600,1100)*T_(0.07))*np.exp(-T_(0.07)*50),2500)*0.02)
add(EV["stop"],drum(0.10))
a,b=sec("knew"); add(EV["know"],drum(0.15)); add(EV["omens"],chime(D(1,10),0.025,2.5)); add(EV["wounds"],clink(0.04,700))
add(EV["guess"],pap(0.04)); add(EV["tityus"],boom(0.25,50,1.5,2.5))
for k in range(4): add(EV["vultures"]+k*0.3,lp(bp(noise(0.18),200,1500),1600)*np.sin(np.pi*T_(0.18)/0.18)*0.04)
add(EV["too"],chime(D(2,0),0.025))
a,b=sec("end"); add(EV["sfire"],lp(bp(noise(1.2),150,900),1000)*np.sin(np.pi*T_(1.2)/1.2)*0.03); add(EV["refuses"],drum(0.12))
# ======================== MASTER ========================
bus=lp(out,9000)
vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
master.master(vo,bus,SR,"mix.wav",bus_gain=0.85)
