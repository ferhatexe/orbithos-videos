import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid39"); sys.path.insert(0,"/home/claude/toolkit")
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
def mbira(f,amp=0.035,dur=1.8):
    tt=T_(dur); s=np.sin(2*np.pi*f*tt)*np.exp(-tt*3.5)+0.25*np.sin(2*np.pi*f*5.4*tt)*np.exp(-tt*16)+0.12*np.sin(2*np.pi*f*2.01*tt)*np.exp(-tt*6)
    buzz=lp(rng.normal(0,1,len(tt)),2500)*np.exp(-tt*9)*0.04
    return lp((s+buzz)*amp*np.clip(tt/0.003,0,1),4500)
PENT=[0,3,5,7,10,12,15,17]
def mbira_line(t0,t1,step,amp,maj=False,seed=1):
    g=np.random.default_rng(seed); x=t0; k=0; sc_=[0,2,4,7,9,12,14,16] if maj else PENT
    pat=[0,2,4,2,5,4,2,1]
    while x<t1-0.3:
        s_=sc_[pat[k%8]+ (1 if k%16>=8 else 0)]; add(x,mbira(D(1,s_),amp)); 
        if k%4==0: add(x,mbira(D(0,sc_[0] if (k//8)%2==0 else sc_[3]),amp*0.8))
        x+=step; k+=1
def bubbles(t0,dur,rate,amp=0.02,f0=500,f1=1400):
    x=t0
    while x<t0+dur:
        f=rng.uniform(f0,f1); add(x,plip(amp*rng.uniform(0.5,1),f*0.6,f)); x+=rng.exponential(1/rate)
def crickets(t0,t1,amp=0.004):
    d=t1-t0; tt=T_(d); env=(np.sin(2*np.pi*14*tt)>0.2)*(np.sin(2*np.pi*0.7*tt)>-0.3)
    add(t0,lp(np.sin(2*np.pi*3100*tt)*env*np.clip(tt/1,0,1)*np.clip((d-tt)/1,0,1),3600)*amp)
def frog(at,amp=0.03):
    tt=T_(0.25); add(at,lp(np.sign(np.sin(2*np.pi*95*tt))*np.sin(np.pi*tt/0.25)*(0.6+0.4*np.sin(2*np.pi*22*tt)),700)*amp)
# ---------- music ----------
a,b=sec("hook"); add(a,pad(D(-1,0),EV["nosound"]-a,0.018,1.5,0.15)); add(a,pad(D(-1,3),EV["nosound"]-a,0.012,1.5,0.15))
mbira_line(a+0.4,EV["noexp"]-0.2,0.42,0.026)
add(EV["killed"],boom(0.3,55,1.5,2.5))
add(EV["morning"],pad(D(-1,0),b-EV["morning"]+0.5,0.016,1.0,1.0)); add(EV["morning"],pad(D(0,1),b-EV["morning"]+0.5,0.010,1.0,1.0))
a,b=sec("lake"); add(a,pad(D(-1,0),b-a,0.016,1.0,1.0)); add(a,pad(D(-1,7),b-a,0.012,1.0,1.0)); mbira_line(a+0.2,b-0.4,0.36,0.022,seed=2)
add(a,drone(D(-2),b-a,0.03,1.5,1.0,250))
a,b=sec("night"); add(a,drone(D(-2,1),b-a,0.04,1.0,0.5,280)); add(a,pad(D(0,1),b-a,0.012,1.0,0.5)); add(a,pad(D(0,6),b-a,0.010,1.0,0.5))
for x in np.arange(a+0.3,EV["rose"],0.5): add(x,mbira(D(0,[0,1][int(x*2)%2]),0.02,1.0))
a,b=sec("erupt"); add(a,drone(D(-2),b-a+0.5,0.05,0.3,1.0,300))
for s_ in (0,1,7): add(EV["invisible"]-0.3,pad(D(0,s_),b-EV["invisible"]+1.0,0.014,1.5,1.0))
a,b=sec("cloud"); add(a,pad(D(-1,0),b-a,0.016,1.5,1.0)); add(a,pad(D(-1,3),b-a,0.012,1.5,1.0)); add(a,pad(D(0,8),b-a,0.008,2,1.0))
for x in np.arange(EV["villages"],b-0.3,0.8): add(x,mbira(D(1,[0,3,7,3][int((x-a)/0.8)%4]),0.018,2.0))
a,b=sec("dawn"); add(a,pad(D(-1,0),b-a,0.018,2.0,1.0)); add(a,pad(D(-1,7),b-a,0.012,2.0,1.0))
for x,s_ in zip(np.arange(a+0.5,b,1.5),[12,10,7,5,3,0,-2,0,3,5,3,0]): add(x,mbira(D(0,s_),0.022,2.4))
a,b=sec("why"); add(a,drone(D(-2,0),b-a,0.03,1,1,250))
for x in np.arange(a+0.2,EV["before"]-0.3,0.67): add(x,lp(np.sin(2*np.pi*660*T_(0.6))*np.exp(-T_(0.6)*5),1500)*0.02)
a,b=sec("fix"); mbira_line(a+0.3,b-0.3,0.3,0.024,maj=True,seed=4)
for s_ in (0,4,7): add(a,pad(D(-1,s_),b-a,0.012,1.5,1.0))
a,b=sec("end"); add(a,drone(D(-2),b-a+1,0.035,1.0,2.0,260)); add(a,pad(D(0,1),b-a,0.012,1.5,1.5))
tf=Lx("The quietest")[1]+0.6
for s_ in (0,3,7,10): add(EV["quiet"]-0.2,pad(D(0,s_),tf-EV["quiet"]+3.5,0.014,0.8,2.5))
add(tf,mbira(D(1,0),0.04,3.0)); add(tf+0.3,mbira(D(1,7),0.03,3.0)); add(tf+0.6,mbira(D(2,3),0.025,3.0))
# ---------- sfx ----------
for s_ in SC[1:]:   # gas-fog wipe: soft hiss swell + low bloom
    b_=s_["s"]; add(b_-0.35,lp(bp(noise(0.7),300,2200),2400)*np.sin(np.pi*T_(0.7)/0.7)**2*0.05); add(b_,boom(0.10,60,4,0.9))
a,b=sec("hook"); crickets(a,EV["nosound"]); 
for x in np.arange(a+1,EV["nosound"],1.3): frog(x+rng.uniform(0,0.4),0.02)
for e in (EV["noexp"],EV["nofire"],EV["nosound"]): add(e,pap(0.04))
add(EV["silent"],chime(D(1,0),0.025,3.0))
a,b=sec("lake"); bubbles(EV["magma"],b-EV["magma"],3,0.012)
add(EV["soda"],lp(bp(noise(1.0),800,3000),3200)*np.sin(np.pi*T_(1.0))*0.012); bubbles(EV["fizzier"],2.0,14,0.012,700,1700)
a,b=sec("night")
add(EV["landslide"],boom(0.25,70,3,1.5)); add(EV["landslide"]+0.2,lp(bp(noise(1.0),150,900),1000)*np.exp(-T_(1.0)*3)*0.06)
amb(400,2200,0.03,EV["rain"]-0.1,EV["quake"]-0.1,0.3,0.4)
add(EV["quake"],lp(noise(1.2),120)*np.sin(np.pi*T_(1.2)/1.2)*0.5); add(EV["quake"],boom(0.3,40,2,1.5))
add(EV["rose"],whoosh(1.5,0.05,150,900)); add(EV["dropped"],lp(np.sin(2*np.pi*np.cumsum(900-600*T_(0.6))/SR)*np.exp(-T_(0.6)*3),2000)*0.02)
bubbles(EV["allonce"]-0.1,1.6,40,0.02,400,1300); add(EV["allonce"],boom(0.45,45,1.5,3.0))
a,b=sec("erupt"); tt=T_(3.5); add(EV["fountain"]-0.1,lp(bp(rng.normal(0,1,len(tt)),120,1600),1800)*np.clip(tt/0.2,0,1)*np.exp(-tt*0.6)*0.10)
add(EV["wave"],whoosh(1.4,0.06,150,1000))
tt=T_(b-EV["cloudw"]+1); add(EV["cloudw"]-0.2,lp(bp(rng.normal(0,1,len(tt)),200,1200),1400)*np.clip(tt/1.5,0,1)*0.035)
a,b=sec("cloud"); tt=T_(b-a); add(a,lp(bp(rng.normal(0,1,len(tt)),150,900),1000)*np.clip(tt/1,0,1)*np.clip((b-a-tt)/1,0,1)*0.03)
add(EV["heavier"],lp(np.sin(2*np.pi*np.cumsum(500-300*T_(0.8))/SR)*np.exp(-T_(0.8)*2.5),1500)*0.03)
for e in (EV["vnyos"],EV["kam"],EV["cha"],EV["subum"]): add(e,pap(0.035))
add(EV["km25"],boom(0.2,60,3,1.5))
a,b=sec("dawn"); amb(150,800,0.012,a,b,2,1)
add(EV["never"],chime(D(0,0),0.03,4.0)); add(EV["red"],boom(0.2,50,1.5,2.5))
a,b=sec("why"); add(EV["limnic"],boom(0.25,55,2,2.0)); add(EV["monoun"],pap(0.04)); add(EV["k37"],chime(D(1,0),0.025,2.5))
a,b=sec("fix"); add(EV["pipe"]-0.2,lp(bp(noise(1.4),300,1500),1600)*np.sin(np.pi*T_(1.4)/1.4)*0.03)
tt=T_(b-EV["pushed"]); add(EV["pushed"],lp(bp(rng.normal(0,1,len(tt)),300,2200),2400)*np.clip(tt/0.5,0,1)*np.clip((b-EV["pushed"]-tt)/1.0,0,1)*0.03)
bubbles(EV["pushed"],b-EV["pushed"]-0.5,4,0.010)
add(EV["y2011"],pap(0.04)); add(EV["less"],chime(D(2,4),0.03))
a,b=sec("end"); crickets(a,b,0.003); add(EV["kivu"],boom(0.25,48,1.5,2.5)); bubbles(EV["full"],3.0,5,0.012)
# ======================== MASTER ========================
# true silence after "No sound": duck the whole bus for a beat
sil0=EV["nosound"]+0.25; sil1=EV["morning"]-0.3
g_=np.ones(N); i0,i1=int(sil0*SR),int(sil1*SR); ramp=int(0.15*SR)
g_[i0:i1]=0.08; g_[i0-ramp:i0]=np.linspace(1,0.08,ramp); g_[i1:i1+ramp]=np.linspace(0.08,1,ramp)
bus=lp(out,9000)*g_
vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
master.master(vo,bus,SR,"mix.wav",bus_gain=0.7)
