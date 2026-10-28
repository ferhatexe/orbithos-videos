import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid76"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import master
from sfxlib import *
import r76
LINES=r76.LINES; TOTAL=r76.TOTAL; wt=r76.wt; Ls=r76.Ls; SHOTS=r76.SHOTS
init(TOTAL)
# ---- music: mythic epic, D dorian, 84 bpm: lyre (kithara) plucks + cello ostinato + frame drum + choir on Olympus ----
BEAT=60/84; D_=lambda o,s=0:146.83*2**o*2**(s/12)
def lyre(f,dur=1.8,amp=0.010):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt+0.2*k)*np.exp(-tt*(2.2+k*1.1))/k**1.1 for k in range(1,7))
    return bp(s*amp*np.clip(tt/0.0015,0,1),150,5000)
def drum(amp,low=True):
    tt=T_(0.45); f=(80 if low else 170)*(1+0.5*np.exp(-tt*22))
    return lp(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*(8 if low else 16))*amp+bp(noise(0.45),250,2200)*np.exp(-tt*30)*amp*0.3,2800)
PROG=[[0,3,7],[-2,2,5],[-4,0,3],[-5,-1,2]]          # Dm  C  Bb  A(ish) in semitones from D
CL=BEAT*4
x=0.0;k=0
while x<TOTAL+0.2:
    ch=PROG[int(x/CL)%4]; arp_=[ch[0],ch[1],ch[2],ch[1]+12,ch[2],ch[1]]
    add(x,lyre(D_(0,arp_[k%6]),1.6,0.0075))
    if k%4==0: add(x,drum(0.045,True))
    elif k%4==2: add(x,drum(0.022,False))
    x+=BEAT/2; k+=1
x=0.0
while x<TOTAL:
    ch=PROG[int(x/CL)%4]; add(x,cello(D_(-1,ch[0]),CL+0.3,0.020,0.5,0.6)); x+=CL
add(0,drone(D_(-2,0),TOTAL+0.4,0.014,0.5,0.8,300))
# madness: dissonant low swell; olympus/hebe: choir
add(Ls(9)-0.2,cello(D_(-1,1),3.2,0.03,0.8,0.8)); add(Ls(9)-0.2,cello(D_(-1,7),3.2,0.02,0.8,0.8))
for s_ in (0,3,7): add(Ls(11)-0.3,choir_(D_(0,s_),4.0,0.012)); add(wt(12,"married")-0.2,choir_(D_(0,s_+(-2 if s_==0 else 0)),3.5,0.010))
# ---- transitions ----
def flutter(amp=0.02,dur=0.55):
    tt=T_(dur); n=bp(noise(dur),900,6000)*(0.55+0.45*np.abs(np.sin(2*np.pi*18*tt)))
    return n*np.sin(np.pi*tt/dur)**2*amp
for st,fn,kind in SHOTS[1:]:
    if kind=="iris": add(st-0.3,flutter(0.022)); add(st-0.3,whoosh(0.6,0.012,300,2600)); add(st,shimmer(0.006,1.0))
    else: add(st,boom(0.022,70,8,0.4)); add(st,click(0.007,1500,150))
# ---- scene sfx ----
amb(150,1200,0.006,0,Ls(1)-0.2,0.05,0.3,0.4,0.2)                       # wind on Olympus
add(wt(0,"tried"),boom(0.05,50,3,1.5))
for i in range(2): add(wt(0,"kill")-0.2+i*0.1,lp(bp(noise(0.8),3000,9000),9500)*np.exp(-T_(0.8)*3)*0.010)  # hiss
for i in range(7): add(Ls(1)+0.1+i*0.11,click(0.010,3500,260))          # chisel letters
add(wt(1,"glory"),chime(D_(2,0),0.010,2.0))
add(Ls(2)+0.1,boom(0.05,45,2.0,2.0)); add(Ls(2)+0.1,crack(0.03))         # thunderbolt
add(wt(2,"mortal"),bell(D_(1,3),0.008,2.5))
add(wt(3,"delays"),lp(np.sin(2*np.pi*D_(1,7)*T_(1.5))*np.exp(-T_(1.5)*1.5),3000)*0.012)
add(wt(3,"throne")-0.1,chime(D_(1,5),0.010,2.0))
amb(2500,8000,0.006,Ls(4),Ls(5)+0.5,0.6,0.3,0.6,1.5)                     # serpents hissing
add(wt(4,"serpents"),lp(bp(noise(1.0),3000,9000),9500)*np.exp(-T_(1.0)*2.5)*0.014)
add(Ls(5),boom(0.09,48,3,1.8)); add(Ls(5)+0.05,shimmer(0.009,1.2))
for i in range(6): add(Ls(6)+0.2+i*0.12,click(0.012,3200,240))         # chisel ALCIDES
add(wt(6,"Alcaeus"),pap(0.03))
amb(300,2500,0.010,wt(7,"people")-0.2,wt(7,"serpents"),0.4,0.4,0.4,2.5)   # crowd
add(wt(7,"glory"),chime(D_(2,3),0.010,2.2))
amb(200,1500,0.008,Ls(8),Ls(9)-0.1,0.3,0.3,0.4,0.8)                       # Delphi vapour
add(Ls(9),boom(0.06,40,1.5,2.5))
for i in range(12): add(wt(10,"Twelve")+i*0.09,click(0.010,2200+i*80,200))  # medallions
add(wt(10,"famous"),bell(D_(0,0),0.010,3.0))
add(wt(11,"god"),shimmer(0.010,1.5)); add(wt(11,"peace"),chime(D_(2,7),0.010,2.0))
add(wt(12,"adopted"),bell(D_(1,0),0.009,2.5)); add(wt(12,"Hebe"),chime(D_(2,0),0.010,2.5))
for i in range(8): add(Ls(13)+0.1+i*0.1,click(0.010,3300,250))
add(TOTAL-0.55,whoosh(0.6,0.014,250,2500))
bus=lp(out(),9500); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.1
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
