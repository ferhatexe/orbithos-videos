import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid74"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import master
from sfxlib import *
import r74
LINES=r74.LINES; TOTAL=r74.TOTAL; wt=r74.wt; Ls=r74.Ls; SHOTS=r74.SHOTS
init(TOTAL)
# ---- music: storm thriller in D minor (pulsing cello ostinato + low drone + taiko-ish hits), resolves to D major after "SCE to Aux" ----
BPM=100; BEAT=60/BPM; Dn=lambda o,s=0:73.42*2**o*2**(s/12)
T_FIX=r74.wt(9,"flipped"); T_MOON=Ls(10)-0.25; T_END=Ls(13)-0.3
def pluckc(f,dur=0.32,amp=0.02):
    tt=T_(dur); ph=2*np.pi*f*tt; s=sum(np.sin(ph*k)/k**1.1 for k in range(1,9))
    return lp(s*np.exp(-tt*7)*np.clip(tt/0.006,0,1)*amp,1500)
def taiko(amp):
    tt=T_(0.7); f=58*(1+0.8*np.exp(-tt*30))
    return lp(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*6)*amp+lp(noise(0.7),600)*np.exp(-tt*25)*amp*0.4,1200)
OST=[0,0,12,0,10,0,7,0, 0,0,12,0,8,0,7,5]
x=0.0;k=0
while x<T_FIX:
    sec=1.0 if x>Ls(2)-0.3 else 0.75
    add(x,pluckc(Dn(1,OST[k%16]),0.30,0.016*sec))
    if k%8==0: add(x,taiko(0.07*sec))
    if k%8==6 and x>Ls(4): add(x,taiko(0.04))
    x+=BEAT/2; k+=1
# chord pads (Dm - Bb - Gm - A) during tension
pads(0,T_FIX+0.3,[(0,3,7),(-2,2,5),(-7,-4,0),(-5,-1,2)],cl=BEAT*8,amp=0.006,oct_=0)
add(0,drone(Dn(0,0),T_FIX+0.6,0.020,0.5,0.8,260))
# release: D major warm pads + kalimba arp from the fix to the end of the chutes
pads(T_FIX,T_END+0.3,[(0,4,7),(-2,2,5),(5,9,12),(7,11,14)],cl=BEAT*6,amp=0.008,oct_=1)
arp(T_MOON,T_END,[(0,4,7,11),(5,9,12,16),(-2,2,5,9),(7,11,14,19)],step=BEAT/2,amp=0.010,oct_=2,cl=BEAT*6)
add(T_FIX,drone(Dn(0,0),T_END-T_FIX+0.6,0.012,1.0,1.0,300))
add(T_FIX+0.05,shimmer(0.012,1.6))
# loop tail: tension returns for the seamless restart
add(T_END-0.2,drone(Dn(0,0),TOTAL-T_END+0.7,0.020,0.3,0.1,260))
for kk in range(4): add(T_END+kk*BEAT/2,pluckc(Dn(1,OST[kk]),0.30,0.016))
# ---- lightning-strike transitions ----
def thunder(amp=0.08,dur=2.6):
    tt=T_(dur); n=lp(noise(dur),180)*(np.exp(-tt*1.3)*(1+0.6*np.sin(2*np.pi*3.1*tt)**2))
    return n*amp*np.clip(tt/0.04,0,1)
def zapfx(amp=0.05):
    tt=T_(0.5); n=hp(noise(0.5),1800)*np.exp(-tt*14)*amp; buzz=np.sign(np.sin(2*np.pi*90*tt))*np.exp(-tt*10)*amp*0.25
    return lp(n+buzz,8000)
for st,fn,kind in SHOTS[1:]:
    if kind=="zap": add(st-0.02,crack(0.10)); add(st-0.02,zapfx(0.05)); add(st,thunder(0.10,2.0)); add(st-0.3,whoosh(0.3,0.012,400,3000))
    else: add(st,click(0.006,1800,200)); add(st,boom(0.012,70,10,0.3))
# ---- lightning strikes on the rocket ----
for s_ in r74.STRIKES:
    add(s_,crack(0.16)); add(s_+0.09,crack(0.08)); add(s_,zapfx(0.06)); add(s_+0.05,thunder(0.16,3.0))
add(0.0,crack(0.07)); add(0.05,thunder(0.08,2.0))      # distant bolt on the first frame
# ---- scene beds ----
amb(700,6000,0.010,0,Ls(4)-0.1,0.05,0.4,0.2,0.3)                       # rain
amb(30,180,0.05,0,Ls(1)-0.25,0.05,0.2,0.3,7)                           # rocket rumble (hook)
amb(30,200,0.05,wt(1,"lifted")-0.1,Ls(4)-0.2,0.6,0.4,0.3,6)            # liftoff + climb rumble
amb(200,1200,0.004,wt(1,"President")-0.2,Ls(2)-0.2,0.3,0.3,0.4,0.5)    # crowd murmur
amb(30,120,0.03,T_END-0.2,TOTAL+0.3,0.2,0.1,0.3,7)                     # loop rumble
# caution & warning: master alarm + fuel cell beeps
tA=wt(4,"warning")-0.15
for i in range(int((Ls(5)-0.2-tA)/0.5)):
    add(tA+i*0.5,beep(1000,0.22,0.010)); add(tA+i*0.5+0.25,beep(750,0.22,0.008))
for i,sub in enumerate(("three","fuel","cells")): add(wt(4,sub),beep(1400,0.07,0.012))
add(tA,boom(0.04,60,6,0.6))
# Conrad radio: quindar tones + static
def quindar(f): tt=T_(0.25); return np.sin(2*np.pi*f*tt)*np.clip(tt/0.005,0,1)*np.clip((0.25-tt)/0.005,0,1)*0.010
add(Ls(5)-0.3,quindar(2525)); add(LINES[5]["e"]+0.05,quindar(2475))
add(Ls(5)-0.1,static(LINES[5]["e"]-Ls(5)+0.3,0.006))
# Mission Control: hum, chatter, garbage glitches
amb(100,140,0.010,Ls(6)-0.25,Ls(9)-0.2,0.3,0.3)
amb(300,2500,0.003,Ls(6)-0.25,Ls(9)-0.2,0.3,0.3,0.6,1.3)
tg=wt(6,"data")
for i in range(14): add(tg+i*0.13+np.random.default_rng(i).uniform(0,0.05),hp(noise(0.06),1500)*np.exp(-T_(0.06)*40)*0.03)
add(tg,static(2.5,0.010))
for i in range(10): add(Ls(7)+0.2+i*0.32,click(0.004,2600,350))
add(wt(7,"pattern"),chime(Dn(3,0),0.010,1.5))
for i in range(6): add(wt(8,"baffled")+i*0.07,pap(0.010))
ts=wt(8,"SCE")-0.05
for i in range(9): add(ts+i*0.05,click(0.016,2600,260))
add(ts+0.5,beep(1200,0.08,0.010))
# switch flip
add(wt(9,"found"),chime(Dn(3,7),0.010,1.2))
add(T_FIX,click(0.06,1600,120)); add(T_FIX,boom(0.05,140,18,0.25))
for i,f in enumerate((880,1175,1480)): add(wt(9,"data")+i*0.09,beep(f,0.07,0.010))
# orbit / moon / reentry / chutes
add(Ls(10)+0.1,whoosh(1.4,0.010,200,1600))
add(wt(10,"Moon"),chime(Dn(3,4),0.012,2.4))
add(wt(11,"landed"),boom(0.03,50,3,1.2)); add(wt(11,"Surveyor"),chime(Dn(3,11),0.010,2.0))
amb(60,900,0.025,Ls(12)-0.15,wt(12,"never")-0.1,0.4,0.3,0.4,9)          # plasma roar
amb(300,2500,0.008,wt(12,"never")-0.15,T_END,0.3,0.4,0.3,0.4)          # wind while falling
to=wt(12,"opened")-0.25
add(to,boom(0.06,90,10,0.5)); add(to,pap(0.05)); add(to+0.08,pap(0.04)); add(to+0.16,pap(0.04))
add(T_END-0.5,whoosh(0.6,0.016,250,2500))
bus=lp(out(),9500); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.1
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
