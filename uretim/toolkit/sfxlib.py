"""Shared Orbithos sound generators (from vid42 audio) + init/add bus. Usage:
from sfxlib import *; init(TOTAL); ... add(t,sig,g) ...; bus=lp(out(),9000)"""
import numpy as np, math
from scipy.signal import butter, sosfilt
SR=44100; rng=np.random.default_rng(42); _O={}
def init(total):
    global N; N=int((total+0.5)*SR); _O["o"]=np.zeros(N)
def out(): return _O["o"]
def lp(x,f): return sosfilt(butter(2,f/(SR/2),'low',output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f/(SR/2),'high',output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a/(SR/2),b/(SR/2)],'band',output='sos'),x)
def add(at,sig,g=1.0):
    o=_O["o"]; i=int(at*SR)
    if i<0: sig=sig[-i:]; i=0
    L=min(len(sig),len(o)-i)
    if L>0: o[i:i+L]+=sig[:L]*g
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
def cello(f,dur,amp=0.025,att=0.4,rel=0.6):
    tt=T_(dur); ph=2*np.pi*np.cumsum(f*(1+0.004*np.sin(2*np.pi*5*tt)))/SR
    s=sum(np.sin(ph*k)/k**1.2 for k in range(1,10))
    return lp(s*np.clip(tt/att,0,1)*np.clip((dur-tt)/rel,0,1)*amp,1800)
def hymn(t0,t1,prog,step,amp=0.012):
    x=t0;k=0
    while x<t1-0.5:
        for s_ in prog[k%len(prog)]: add(x,choir_(D(0,s_),step+0.6,amp))
        x+=step; k+=1
def choir_(f,dur,amp):
    tt=T_(dur); src=sum(np.sin(2*np.pi*f*k*tt*(1+0.003*np.sin(2*np.pi*4.5*tt)))/k for k in range(1,10))
    return lp((bp(src,450,1100)*1.3+bp(src,200,420)*0.7)*np.clip(tt/0.5,0,1)*np.clip((dur-tt)/0.6,0,1)*amp,2800)
def bell(f=110,amp=0.05,dur=4.0):
    tt=T_(dur); return lp(sum(a_*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*d) for a_,r,d in ((1,1,0.8),(0.6,2.0,1.2),(0.4,2.4,1.6),(0.25,3.0,2.2),(0.15,4.2,3)))*amp*np.clip(tt/0.003,0,1),3500)
def gavel(amp=0.2):
    x=boom(amp,140,12,0.4); n=lp(bp(noise(0.4),300,1800),2000)*np.exp(-T_(0.4)*60)*amp*0.6; return x+n

def arp(t0,t1,chords,step=0.19,amp=0.010,oct_=1,cl=2.6):
    x=t0;k=0
    while x<t1-0.2:
        ch=chords[int((x-t0)/cl)%len(chords)]; s_=ch[k%len(ch)]+(12 if (k//len(ch))%2 else 0)
        add(x,kal(D(oct_,s_),1.2,amp)); x+=step; k+=1
def pads(t0,t1,chords,cl=2.6,amp=0.010,oct_=0):
    x=t0;k=0
    while x<t1-0.3:
        for s_ in chords[k%len(chords)]: add(x,pad(D(oct_,s_),min(cl+1.0,t1-x+0.5),amp,0.7,1.0))
        x+=cl;k+=1
def beep(f=760,d=0.08,amp=0.02): tt=T_(d); return np.sin(2*np.pi*f*tt)*np.clip(tt/0.004,0,1)*np.clip((d-tt)/0.006,0,1)*amp
def crack(amp=0.03):
    tt=T_(0.25); n=bp(noise(0.25),1200,4500)*np.exp(-tt*45); th=np.sin(2*np.pi*90*tt)*np.exp(-tt*25)
    return lp(n*0.6+th,5200)*amp
def shimmer(amp=0.02,dur=1.2,up=True):
    tt=T_(dur); s=np.zeros(len(tt))
    for k,sv in enumerate((0,7,12,16,19)):
        f=D(2,sv); env=np.exp(-((tt-(k*0.08 if up else 0.3-k*0.06))/0.25)**2) if True else 1
        s+=np.sin(2*np.pi*f*tt)*np.clip(tt-k*0.06,0,None)**0.01*np.exp(-np.clip(tt-k*0.06,0,None)*2.5)*(tt>k*0.06)
    return lp(s*amp,6000)
def saw(f,dur,amp=0.02,att=0.05,rel=0.3,cut=1800,det=0.004):
    tt=T_(dur); s=0
    for dd in (1-det,1,1+det):
        ph=(f*dd*tt)%1.0; s=s+(2*ph-1)
    return lp(lp(s/3*np.clip(tt/att,0,1)*np.clip((dur-tt)/rel,0,1)*amp,cut),cut*1.5)
def click(amp=0.03,f=2500,dec=300):
    tt=T_(0.02); return bp(rng.normal(0,1,len(tt)),f*0.5,min(f*1.8,15000))*np.exp(-tt*dec)*amp
def printer(dur,amp=0.02,rate=38):
    """dot-matrix printer chatter"""
    o=np.zeros(int(dur*SR)+SR//10); x=0.0
    while x<dur:
        s=click(amp*rng.uniform(0.6,1.0),rng.uniform(1800,3200),rng.uniform(180,320)); i=int(x*SR); o[i:i+len(s)]+=s[:len(o)-i]
        x+=1/rate*rng.uniform(0.6,1.4)
    tt=np.arange(len(o))/SR; o+=lp(rng.normal(0,1,len(o)),400)*amp*0.15*(tt<dur)
    return o
def feed(amp=0.05,dur=0.55):
    """tractor-feed paper advance: ratchet clicks + paper swish"""
    o=np.zeros(int(dur*SR)); n=10
    for k in range(n):
        s=click(amp*0.8,1400,220); i=int(dur*SR*(0.5*(1-math.cos(math.pi*k/n))))
        o[i:i+len(s)]+=s[:len(o)-i]
    tt=T_(dur); o+=bp(rng.normal(0,1,len(tt)),900,4500)*np.sin(np.pi*tt/dur)**2*amp*0.5
    return o
def stampfx(amp=0.12):
    x=boom(amp,120,14,0.35); n=lp(bp(noise(0.12),200,1500),1600)*np.exp(-T_(0.12)*45)*amp*0.7; x[:len(n)]+=n; return x
def scribble(dur,amp=0.012):
    tt=T_(dur); x=bp(rng.normal(0,1,len(tt)),2500,7000)*(0.5+0.5*np.abs(np.sin(2*np.pi*5.5*tt)))
    return x*np.clip(tt/0.05,0,1)*np.clip((dur-tt)/0.08,0,1)*amp
def static(dur,amp=0.01):
    tt=T_(dur); x=bp(rng.normal(0,1,len(tt)),400,5000)*(1+0.4*rng.normal(0,1,len(tt)).clip(-1,1)*0)
    return x*np.clip(tt/0.3,0,1)*np.clip((dur-tt)/0.3,0,1)*amp
