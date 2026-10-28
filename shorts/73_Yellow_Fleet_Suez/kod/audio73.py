import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid73"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import master
from sfxlib import *
import r73
LINES=r73.LINES; TOTAL=r73.TOTAL; wt=r73.wt; Ls=r73.Ls; SHOTS=r73.SHOTS
init(TOTAL)
# ---- music: warm desert adventure, D phrygian-dominant flavour, 92 bpm: oud-like plucks + frame drum + low pad ----
BEAT=60/92; D_=lambda o,s=0:146.83*2**o*2**(s/12)
SCL=[0,1,4,5,7,8,10,12]
def oud(f,dur=1.4,amp=0.010):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt+0.3*k)*np.exp(-tt*(3.0+k*1.4))/k**0.9 for k in range(1,8))
    return bp(s*amp*np.clip(tt/0.002,0,1),120,4500)
def drum(amp,low=True):
    tt=T_(0.4); f=(90 if low else 180)*(1+0.6*np.exp(-tt*25))
    return lp(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*(9 if low else 18))*amp+bp(noise(0.4),300,2500)*np.exp(-tt*35)*amp*0.25,3000)
MEL=[0,1,4,1,0,-2,0,4,5,4,1,0,7,5,4,1]
x=0.0;k=0
while x<TOTAL+0.2:
    add(x,oud(D_(0,MEL[k%16]),1.3,0.0085)); 
    if k%4==0: add(x,drum(0.05,True))
    elif k%4==2: add(x,drum(0.03,False))
    if k%8==7: add(x+BEAT/4,drum(0.02,False))
    x+=BEAT/2; k+=1
add(0,drone(D_(-2,0),TOTAL+0.4,0.018,0.5,0.8,350)); add(0,drone(D_(-1,7),TOTAL+0.4,0.006,0.5,0.8,500))
# ---- transitions ----
for st,fn,kind in SHOTS[1:]:
    if kind=="sand": add(st-0.3,whoosh(0.6,0.018,250,2500)); add(st-0.3,lp(bp(noise(0.6),1500,7000),8000)*np.sin(np.pi*T_(0.6)/0.6)*0.006)
    else: add(st,boom(0.025,70,8,0.4)); add(st,click(0.008,1500,150))
add(TOTAL-0.55,whoosh(0.6,0.018,250,2500))
# ---- scene sfx ----
amb(150,1500,0.008,0,Ls(1)-0.2,0.05,0.3,0.4,0.2)                      # desert wind
add(1.0,lp(np.sin(2*np.pi*72*T_(1.6))*np.clip(T_(1.6)/0.1,0,1)*np.clip((1.6-T_(1.6))/0.3,0,1),400)*0.05)   # ship horn
for k_,ft in enumerate((0.4,1.3,2.2,3.0)): add(Ls(1)+ft,boom(0.07,40,2.2,2.0))   # distant blasts
add(wt(1,"sealed"),stampfx(0.08)); add(wt(1,"ends"),stampfx(0.08))
for i in range(14): add(Ls(2)+0.2+i*0.12,click(0.006,2500,400))
add(Ls(3)+0.3,chime(D_(1,0),0.008,2.0))
amb(500,5000,0.010,Ls(4),Ls(5)-0.2,0.3,0.3,0.6,1.1)                   # sand hiss
for i in range(8): add(Ls(5)+0.3+i*0.12,pap(0.025))
add(wt(6,"Great"),chime(D_(1,4),0.008,2.2))
amb(200,1200,0.006,Ls(7),Ls(8)-0.2,0.3,0.3,0.3,0.4); add(wt(7,"church"),bell(D_(0,0),0.012,3.0))
add(wt(8,"Olympics"),chime(D_(2,0),0.010,1.8))
for sub in ("sailing","diving","archery"): add(wt(8,sub),pap(0.035))
add(Ls(9),boom(0.04,60,4,1.0)); add(Ls(9)+0.05,shimmer(0.008,1.2))
add(wt(10,"stamps"),pap(0.04)); add(wt(10,"letters")-0.1,stampfx(0.10))
add(wt(11,"1975"),bell(D_(-1,0),0.012,3.0))
add(wt(12,"Hamburg")-0.3,lp(np.sin(2*np.pi*65*T_(2.0))*np.clip(T_(2.0)/0.1,0,1)*np.clip((2.0-T_(2.0))/0.4,0,1),380)*0.07)
amb(300,3000,0.012,wt(12,"thousands")-0.2,Ls(13),0.4,0.4,0.5,3)        # crowd cheer (noise bed)
bus=lp(out(),9500); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.2
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
