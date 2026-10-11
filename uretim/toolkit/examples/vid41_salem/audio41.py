import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid41"); sys.path.insert(0,"/home/claude/toolkit")
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
MIN=[[0,3,7],[-4,0,3],[-2,2,5],[-5,-1,2]]
a,b=sec("hook"); add(a,cello(D(-2,0),b-a,0.03,1.5,1.0)); hymn(a+0.5,EV["scientist"]-0.3,MIN,3.0,0.010)
add(EV["hanged"],bell(98,0.05)); add(EV["fungus"]-0.2,pad(D(0,1),3.5,0.014,0.3,1.5)); add(EV["fungus"]-0.2,pad(D(0,6),3.5,0.010,0.3,1.5))
a,b=sec("start"); add(a,cello(D(-2,0),b-a,0.022,1.0,1.0)); add(a,cello(D(-2,7),b-a,0.014,1.0,1.0))
for x in np.arange(EV["fits"],b-0.5,0.5): add(x,lp(np.sin(2*np.pi*D(1,[0,1,0,-1][int((x-a)*2)%4])*T_(0.45))*np.exp(-T_(0.45)*6),2500)*0.016)
a,b=sec("accused"); hymn(a,b,MIN,2.6,0.012); add(a,cello(D(-2,0),b-a,0.02,1.0,1.0))
a,b=sec("trials"); add(a,cello(D(-2,1),b-a,0.025,1.0,1.0))
for x in np.arange(a+0.3,EV["burned"]-0.3,0.85): add(x,boom(0.10,55,6,0.5)); add(x+0.25,boom(0.07,55,6,0.5))
for s_ in (0,3,7): add(EV["burned"]-0.2,choir_(D(0,s_),b-EV["burned"]+0.6,0.012))
a,b=sec("ergot")
tt=T_(b-a); warble=sum(np.sin(2*np.pi*D(0,s_)*tt*(1+0.01*np.sin(2*np.pi*0.3*tt+s_))) for s_ in (0,1,6,7))
add(a,lp(warble*np.clip(tt/1.5,0,1)*np.clip((b-a-tt)/1,0,1),2500)*0.008)
for x in np.arange(a+0.3,b-0.3,0.4): add(x,lp(np.sin(2*np.pi*D(1,[0,3,6,3,1,6][int((x-a)/0.4)%6])*T_(0.35))*np.exp(-T_(0.35)*7),2500)*0.014)
a,b=sec("doubt"); add(a,cello(D(-2,0),b-a,0.02,1.0,1.0)); hymn(a+0.3,b,[[0,3,7],[0,5,8],[-2,2,5],[0,3,7]],3.2,0.010)
a,b=sec("end"); hymn(a,b-2,[[0,3,7],[-4,0,3],[-2,2,5],[0,4,7]],3.0,0.012); add(a,cello(D(-2,0),b-a+0.5,0.02,1.0,2.0))
tf=Lx("Maybe the scariest")[1]+0.6; add(tf,bell(98,0.06,5.0))
# ---------- sfx ----------
for s_ in SC[1:]:   # ink-blot transition: wet drop + low swell
    b_=s_["s"]; add(b_-0.38,lp(bp(noise(0.76),150,900),1000)*np.sin(np.pi*T_(0.76)/0.76)**2*0.05); add(b_-0.05,plip(0.04,250,600))
a,b=sec("hook"); amb(150,900,0.025,a,b,1.5,1.0,0.4,0.2)
for e in (EV["scream"],EV["shake"],EV["twist"]): add(e,lp(bp(noise(0.3),400,1800),2000)*np.sin(np.pi*T_(0.3)/0.3)*0.02)
a,b=sec("start"); tt=T_(b-a); add(a,lp(bp(rng.normal(0,1,len(tt)),100,700),800)*(0.6+0.4*np.sin(2*np.pi*0.7*tt))*np.clip(tt/1,0,1)*np.clip((b-a-tt)/1,0,1)*0.03)
for x in np.arange(a,b,0.7): add(x+rng.uniform(0,0.5),lp(bp(noise(0.03),300,1500),1700)*np.exp(-T_(0.03)*120)*0.02)
add(EV["threw"]+0.6,boom(0.12,180,10,0.4)); add(EV["wc"],gavel(0.18)); add(EV["names"],pap(0.04))
a,b=sec("accused"); amb(200,900,0.02,a,b,1,1,0.5,0.6)
for e in (EV["tituba"],EV["good"],EV["osborne"]): add(e,pap(0.035))
add(EV["confessed"],gavel(0.15)); add(EV["devil"],boom(0.25,45,1.5,2.5)); add(EV["panic"],lp(bp(noise(1.5),200,1500),1700)*np.sin(np.pi*T_(1.5)/1.5)*0.05)
a,b=sec("trials"); add(EV["court"],gavel(0.2)); add(EV["court"]+0.35,gavel(0.15)); add(EV["spectral"],chime(D(2,1),0.02,2.5)); add(EV["proof"],gavel(0.18))
for x in np.arange(EV["k200"],EV["burned"]-0.3,0.06): add(x,lp(bp(noise(0.02),600,2000),2200)*np.exp(-T_(0.02)*150)*0.010)
add(EV["n19"],bell(98,0.05,4.0)); 
for k in range(5): add(EV["stones"]+k*0.2,boom(0.12,70,8,0.5))
a,b=sec("ergot"); add(EV["journal"],pap(0.04)); add(EV["ergotw"],chime(D(1,6),0.02,2.5))
for e in (EV["spasms"],EV["conv"],EV["crawl"],EV["hallu"]): add(e,whoosh(0.5,0.025,500,1800))
add(EV["lsd"],lp(np.sin(2*np.pi*np.cumsum(300+200*np.sin(2*np.pi*1.5*T_(2.0)))/SR)*np.sin(np.pi*T_(2.0)/2.0),2000)*0.02)
add(EV["poisoned"],boom(0.2,55,2,2.0))
a,b=sec("doubt"); add(EV["no"],gavel(0.15)); add(EV["andover"],pap(0.04)); add(EV["sport"],chime(D(1,0),0.025,2.5))
for e in (EV["fear"],EV["rival"],EV["dreams"]): add(e,boom(0.08,90,8,0.5))
a,b=sec("end"); add(EV["unlawful"],boom(0.15,120,10,0.5)); add(EV["y2022"],chime(D(2,0),0.03)); add(EV["y2022"]+0.1,chime(D(2,4),0.025))
amb(150,700,0.012,a,b,1,2)
# ======================== MASTER ========================
bus=lp(out,9000)
vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
master.master(vo,bus,SR,"mix.wav",bus_gain=1.15)
