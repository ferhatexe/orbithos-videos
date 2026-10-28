import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid75"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import master
from sfxlib import *
import r75
LINES=r75.LINES; TOTAL=r75.TOTAL; wt=r75.wt; Ls=r75.Ls; SHOTS=r75.SHOTS
init(TOTAL)
# ---- music: dark Anatolian underground — D phrygian-dominant, 76 bpm: low drone, oud plucks, frame drum heartbeat, cello lines ----
BEAT=60/76; D_=lambda o,s=0:146.83*2**o*2**(s/12)
def oud(f,dur=1.6,amp=0.010):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt+0.3*k)*np.exp(-tt*(2.6+k*1.3))/k**0.9 for k in range(1,8))
    return bp(s*amp*np.clip(tt/0.002,0,1),110,4200)
def drum(amp,low=True):
    tt=T_(0.5); f=(70 if low else 150)*(1+0.6*np.exp(-tt*22))
    return lp(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*(7 if low else 16))*amp+bp(noise(0.5),250,2200)*np.exp(-tt*30)*amp*0.25,2500)
def rumble(dur,amp,rate=7.0):
    tt=T_(dur); x=lp(noise(dur),180)*(0.6+0.4*np.abs(np.sin(np.pi*rate*tt)))+lp(bp(noise(dur),300,1400),1600)*0.25*(0.5+0.5*np.sin(2*np.pi*rate*tt))
    return x*np.sin(np.pi*tt/dur)**0.7*amp
def crackle(t0,t1,rate=6,amp=0.010):
    x=t0
    while x<t1:
        add(x,click(amp*rng.uniform(0.4,1.0),rng.uniform(1500,4000),rng.uniform(200,500))); x+=rng.exponential(1/rate)
def fft_out(amp=0.02):
    tt=T_(0.35); return bp(noise(0.35),400,3000)*np.exp(-tt*9)*amp
MEL=[0,1,4,1,0,None,-2,0,4,5,4,1,0,None,7,5]
x=0.6;k=0
while x<TOTAL-1.0:
    n=MEL[k%16]
    if n is not None and not (Ls(12)<x<Ls(13)): add(x,oud(D_(0,n),1.6,0.0075))
    if k%4==0: add(x,drum(0.05,True))
    if k%4==2 and x>Ls(1): add(x,drum(0.022,False))
    x+=BEAT/2; k+=1
add(0,drone(D_(-2,0),TOTAL+0.4,0.020,0.5,0.8,320)); add(0,drone(D_(-1,7),TOTAL+0.4,0.006,0.5,0.8,450))
for (t0,s_,d_) in ((Ls(2),0,3.6),(Ls(4),-2,3.0),(Ls(4)+3.0,1,3.0),(Ls(10),0,4.0),(Ls(11),-2,4.4)):
    add(t0,cello(D_(-1,s_),d_,0.012,0.5,0.8))
# ---- transitions ----
for st,fn,kind in SHOTS[1:]:
    if kind=="stone": add(st-0.30,rumble(0.62,0.05,9.0)); add(st-0.30,whoosh(0.6,0.012,150,1200)); add(st+0.25,boom(0.03,55,7,0.6))
    else: add(st,boom(0.020,70,9,0.4)); add(st,click(0.006,1400,160))
add(TOTAL-0.55,whoosh(0.6,0.012,150,1200))
# ---- scene sfx ----
amb(150,1500,0.008,0,1.0,0.05,0.3,0.4,0.2)                                   # surface wind
for k,sub in enumerate(("knocked","down","wall")):
    t0=wt(0,sub)+0.02; add(t0,gavel(0.10+0.04*k)); add(t0,crack(0.05+0.02*k))
    add(t0+0.03,lp(bp(noise(0.6),200,2500),3000)*np.exp(-T_(0.6)*6)*0.03*(k+1))  # rubble
add(wt(0,"found"),boom(0.07,45,1.8,2.5)); add(wt(0,"found")+0.05,shimmer(0.008,1.4))
add(wt(0,"city"),chime(D_(1,0),0.010,2.2))
add(wt(1,"1963"),bell(D_(-1,0),0.014,3.0))
amb(80,600,0.010,wt(1,"dark")-0.1,Ls(2)-0.2,0.2,0.3,0.3,0.5)                 # tunnel air
for i in range(5): add(wt(1,"dark")+i*0.36,pap(0.02))                         # footsteps
for k in range(8): e=Ls(2)-0.10+k*0.42; add(e,lp(noise(0.25),900)*np.exp(-T_(0.25)*12)*0.04); add(e,boom(0.012,90,10,0.3))  # torches ignite
crackle(Ls(2),Ls(5)-0.3,5,0.006)
add(wt(2,"carved"),scribble(0.5,0.006)); add(wt(2,"hand"),click(0.02,3000,250))
for i in range(9): add(wt(3,"85")+i*0.1,click(0.006,2200,400))
add(wt(3,"eight"),chime(D_(1,4),0.008,2.0)); add(wt(3,"maybe"),drone(D_(-2,1),2.0,0.02,0.4,1.0,250))
add(wt(4,"Stables"),pap(0.03)); add(wt(4,"kitchens"),lp(noise(0.6),1500)*np.exp(-T_(0.6)*4)*0.012)
add(wt(4,"wine"),pap(0.03)); add(wt(4,"churches"),bell(D_(0,0),0.012,3.0))
add(wt(4,"estimated")-0.2,choir_(D_(0,0),2.6,0.010)); add(wt(4,"estimated")-0.2,choir_(D_(0,7),2.6,0.007))
amb(1500,7000,0.010,Ls(5)-0.2,Ls(6),0.4,0.4,0.5,1.5); add(Ls(5),shimmer(0.007,1.6))   # air shaft
for i in range(5): add(Ls(6)+0.2+i*0.7,plip(0.03,600,1300))
add(wt(6,"poison"),drone(D_(-1,1),1.2,0.015,0.1,0.6,500))
add(wt(7,"raiders"),drum(0.07,True)); add(wt(7,"raiders")+0.33,drum(0.05,True)); add(wt(7,"raiders")+0.66,drum(0.06,True))
add(wt(7,"rolling")-0.05,rumble(1.05,0.10,6.0)); add(wt(7,"rolling")+0.9,boom(0.11,45,3.5,1.5)); add(wt(7,"rolling")+0.92,crack(0.03))
add(Ls(8)+0.2,gavel(0.06)); add(wt(8,"moved"),rumble(0.5,0.05,10))
for i in range(12): add(Ls(9)+0.3+i*0.14,click(0.004,1800,300))
add(Ls(9)+1.9,chime(D_(1,7),0.008,2.0)); add(wt(9,"reach")-0.1,whoosh(1.2,0.02,200,2000))
add(Ls(10)+0.05,chime(D_(1,1),0.007,2.5)); add(wt(10,"Phrygians"),bell(D_(-1,0),0.010,3.0))
hymn(Ls(11),Ls(11)+2.4,[(0,4,7),(1,5,8)],1.2,0.006); add(wt(11,"1923"),bell(D_(-1,-2),0.014,3.5))
for k in range(8): add(Ls(12)+0.15+k*0.16,fft_out(0.025))
for i in range(14): add(wt(12,"forgotten")-0.1+i*0.09,click(0.005,2500,400))
add(Ls(13)-0.3,boom(0.04,40,2,2.0))
bus=lp(out(),9500); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.2
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
