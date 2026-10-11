import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid42"); sys.path.insert(0,"/home/claude/toolkit")
from scipy.signal import butter, sosfilt
import scipy.io.wavfile as wf
import ev, master
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
SR=44100; N=int((TOTAL+0.5)*SR); t=np.arange(N)/SR; rng=np.random.default_rng(42)
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
LYD=[[0,4,7],[2,6,9],[-3,2,6],[-5,-1,2]]
# ---------------- music ----------------
a,b=sec("hook"); add(a,drone(D(-2,0),b-a+0.4,0.030,2.0,1.0,500)); pads(a+0.4,b,LYD[:2],3.4,0.006)
arp(EV["neutrinos"]-0.1,b,LYD,0.19,0.009)
a,b=sec("pauli"); bal=EV["skipped"]-0.2
add(a,cello(D(-2,0),bal-a,0.016,1.0,1.0)); arp(a+0.2,bal,[[0,4,7],[-3,0,4],[-5,-1,2],[2,5,9]],0.32,0.010,1,2.6)
add(EV["vanish"],pad(D(0,1),2.5,0.010,0.2,1.2)); add(EV["desperate"],cello(D(-1,-1),2.2,0.012,0.3,1.0))
x=bal; k=0
while x<b+0.2:   # waltz at the ball
    ch=[[0,4,7],[-5,-1,2]][(k//3)%2]
    if k%3==0: add(x,kal(D(-1,ch[0]),0.9,0.030))
    else:
        for s_ in ch: add(x,kal(D(1,s_),0.5,0.010))
    x+=0.36; k+=1
a,b=sec("ghost"); pads(a,b,LYD,2.6,0.008); arp(a+0.3,b,LYD,0.21,0.008,1,2.6); add(a,drone(D(-2,0),b-a,0.018,1.5,1.5,450))
a,b=sec("catch"); add(a,drone(D(-2,-1),b-a,0.022,1.0,1.2,500)); pads(a,EV["telegram"],[[-1,3,6],[0,3,7]],3.0,0.008)
for x in np.arange(EV["y1956"],EV["caught"],0.8): add(x,boom(0.05,60,7,0.6))
pads(EV["telegram"],b,[[0,4,7],[5,9,12]],2.5,0.009)
a,b=sec("superk"); add(a,drone(D(-2,0),b-a,0.026,1.5,1.0,380)); pads(a,EV["y2001"]-0.3,[[0,4,7],[2,6,9],[-3,2,6],[0,4,9]],3.0,0.008)
arp(EV["walls"],EV["y2001"]-0.3,LYD,0.17,0.007,1,2.6)
add(EV["y2001"]-0.2,pad(D(-1,1),b-EV["y2001"]+0.6,0.012,0.4,1.0)); add(EV["y2001"]-0.2,pad(D(-1,7),b-EV["y2001"]+0.6,0.009,0.4,1.0))
a,b=sec("nova"); add(a,drone(D(-2,0),b-a,0.020,1.0,1.5,450))
tt=T_(EV["exploded"]-a+0.2); add(a,lp(noise(len(tt)/SR),900)*np.clip(tt/(len(tt)/SR),0,1)**3*0.04)
pads(EV["arrived"]-0.3,b,[[0,4,7],[2,6,9],[4,7,11]],2.4,0.010); arp(EV["arrived"],b,[[0,4,7],[2,6,9],[4,7,11]],0.15,0.009,1,2.4)
a,b=sec("end"); pads(a,EV["watched"],[[-3,0,4],[-5,-1,2]],3.0,0.008); add(a,drone(D(-2,-3),EV["watched"]-a+0.5,0.022,1.0,1.0,350))
pads(EV["watched"]-0.2,b,LYD[:2]+[[0,4,7]],2.6,0.010); arp(EV["watched"],b-1.5,LYD,0.19,0.009)
tf=Lx("So while you")[1]+0.4; add(tf,bell(D(-1,0),0.05,5.0)); add(tf,pad(D(0,0),4.5,0.012,0.2,2.5)); add(tf,pad(D(0,7),4.5,0.009,0.2,2.5))
# ---------------- sfx ----------------
for s_ in SC[1:]:   # Cherenkov ring transition: rising shimmer + soft air
    b_=s_["s"]; add(b_-0.30,whoosh(0.7,0.025,600,3000)); add(b_-0.25,shimmer(0.014,1.4))
a,b=sec("hook"); amb(200,1200,0.010,a,b,1.5,1.0,0.3,0.25)
add(EV["trillion"],chime(D(2,4),0.018,2.0)); add(EV["second"],pap(0.03))
add(EV["bones"],lp(bp(noise(0.6),800,3000),3200)*np.sin(np.pi*T_(0.6)/0.6)*0.012)
add(EV["earth"],boom(0.12,45,1.2,3.0)); add(EV["neutrinos"],chime(D(2,0),0.022,2.5)); add(EV["neutrinos"]+0.08,chime(D(2,7),0.016,2.5))
add(EV["catch1"],boom(0.06,80,6,0.6))
a,b=sec("pauli"); add(EV["y1930"],pap(0.03)); add(EV["decay"],plip(0.03,500,1400))
add(EV["vanish"],whoosh(0.8,0.02,2000,400))
for x in np.arange(EV["dear"],Lx("So he wrote")[1],0.11): add(x+rng.uniform(0,0.03),lp(bp(noise(0.02),900,3500),3800)*np.exp(-T_(0.02)*180)*0.018)
add(EV["invisible"],plip(0.03,900,1800)); add(EV["desperate"],boom(0.08,90,6,0.6))
add(EV["ball"],chime(D(2,4),0.02,2.0))
a,b=sec("ghost"); amb(300,1500,0.008,a,b,1.0,1.0)
add(EV["named"],chime(D(2,0),0.02,2.2)); add(EV["charge"],pap(0.03)); add(EV["mass"],pap(0.03))
add(EV["sun"],boom(0.08,50,1.5,2.5)); add(EV["night"],chime(D(1,9),0.015,2.5))
add(EV["atom"],plip(0.04,1200,2400)); add(EV["atom"]+0.05,chime(D(2,7),0.02,2.5))
a,b=sec("catch"); add(EV["trap"],boom(0.07,70,5,0.8)); add(EV["reactor"],lp(noise(2.0),300)*np.sin(np.pi*T_(2.0)/2.0)*0.05)
add(EV["caught"],plip(0.05,800,2000)); add(EV["caught"]+0.03,chime(D(2,0),0.02,2.5))
g=np.random.default_rng(5); x=EV["telegram"]
while x<EV["replied"]+0.2:
    d=0.06 if g.uniform()<0.6 else 0.18; add(x,beep(760,d,0.012)); x+=d+0.07
add(EV["wait"]+0.4,chime(D(2,4),0.018,2.0))
a,b=sec("superk"); amb(80,500,0.022,a,b,1.5,1.0,0.3,0.15)
add(EV["mountain"],boom(0.08,40,1.2,3.0)); 
for k in range(6): add(EV["water"]-0.3+k*0.18,plip(0.012,400+k*60,900))
add(EV["sensors"],chime(D(2,9),0.012,2.0))
add(EV["hits"],plip(0.03,1500,2500)); 
for k,sv in enumerate((0,4,7,11,14)): add(EV["ring"]+k*0.05,chime(D(2,sv),0.012,2.5))
add(EV["cracked"],crack(0.04)); add(EV["imploded"],boom(0.18,60,3,1.2)); add(EV["imploded"],crack(0.05))
import math as _m
tm=[EV["imploded"]+_m.hypot(x_-270,(y_-640)/0.85)/150.0 for (x_,y_) in [(36+c*33+(16 if r%2 else 0),84+r*33) for r in range(17) for c in range(15)]]
tm=sorted(tm)[::4]
for x in tm:
    if x<b+0.2: add(x+g.uniform(0,0.03),crack(0.012*g.uniform(0.6,1.0)))
for k in range(4): add(EV["imploded"]+k*0.35,boom(0.05,50,4,0.8))
a,b=sec("nova"); add(EV["y1987"],pap(0.03)); add(EV["exploded"],boom(0.22,38,0.9,4.0)); add(EV["exploded"],whoosh(1.4,0.04,200,1500))
for k in range(25): add(EV["detectors"]+k*(max(0.4,EV["n25"]-EV["detectors"]+0.5)/25),plip(0.010,1400,2200))
add(EV["hours"],chime(D(2,4),0.018,2.0)); add(EV["later"],whoosh(1.2,0.035,300,2500)); add(EV["later"]+0.2,boom(0.08,60,2,2.0))
a,b=sec("end"); tt=T_(EV["watched"]-a+0.5); add(a,lp(bp(rng.normal(0,1,len(tt)),60,400),450)*(0.7+0.3*np.sin(2*np.pi*0.12*tt))*np.clip(tt/1,0,1)*np.clip((len(tt)/SR-tt)/0.8,0,1)*0.06)
add(EV["powerful"]-0.8,whoosh(1.6,0.05,200,2200)); add(EV["powerful"],boom(0.20,42,1.2,3.0))
for k,sv in enumerate((0,7,12,16)): add(EV["powerful"]+0.1+k*0.07,chime(D(2,sv),0.014,2.5))
add(EV["nobody"],boom(0.05,90,6,0.6))
add(EV["quad"],shimmer(0.018,1.6)); add(EV["never"],chime(D(2,0),0.015,2.5))
# ======================== MASTER ========================
bus=lp(out,9000)
vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
