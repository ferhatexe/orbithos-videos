import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid54"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sec(n): s=S(n); return s["s"],s["e"]
def celesta(f,dur=1.6,amp=0.02):
    tt=T_(dur); s=(np.sin(2*np.pi*f*tt)+0.5*np.sin(2*np.pi*f*4.01*tt)*np.exp(-tt*8)+0.2*np.sin(2*np.pi*f*2*tt))*np.exp(-tt*2.5)
    return lp(s*amp*np.clip(tt/0.002,0,1),6000)
def cel_arp(t0,t1,chords,step=0.22,amp=0.010,cl=2.6):
    x=t0;k=0
    while x<t1-0.2:
        ch=chords[int((x-t0)/cl)%len(chords)]; s_=ch[k%len(ch)]+(12 if (k//len(ch))%2 else 0); add(x,celesta(D(1,s_),1.4,amp)); x+=step;k+=1
CH=[[0,4,7,11],[-3,0,4,7],[-7,-3,0,4],[-5,-1,2,7]]
a,b=sec("hook"); add(0,drone(D(-2,0),b+0.4,0.018,0.2,1.0,360)); pads(0,b,CH[:2],2.6,0.009); cel_arp(0,b,CH,0.22,0.010)
a,b=sec("myth"); pads(a,b,[[0,3,7],[-4,0,3],[-2,2,5],[-5,-1,2]],2.6,0.009); add(a,drone(D(-2,-4),b-a,0.018,0.6,0.6,360))
for k in range(0,int((b-a)/1.3)): add(a+k*1.3,choir_(D(0,[0,3,7,5,3,2,0,-2][k%8]),1.6,0.008))
a,b=sec("statue"); pads(a,b,CH,2.6,0.009); cel_arp(EV["look"],b,CH,0.18,0.010)
a,b=sec("name"); pads(a,TOTAL+0.2,CH,2.6,0.009); cel_arp(a,TOTAL+0.1,CH,0.22,0.010)
# ---------------- sfx ----------------
for s_ in SC[1:]: add(s_["s"]-0.4,whoosh(0.9,0.035,150,1200)); add(s_["s"]-0.2,shimmer(0.010,1.2))
add(TOTAL-0.7,whoosh(0.9,0.035,150,1200))
add(EV["earth"],chime(D(2,4),0.014,2.0)); add(EV["wrong"],boom(0.05,90,6,0.6)); add(EV["holding"],shimmer(0.016,1.6))
add(EV["zeus"],boom(0.08,50,2,2.0)); add(EV["zeus"],crack(0.04)); add(EV["sky"],shimmer(0.018,1.8)); add(EV["forever"],bell(D(-1,0),0.02,3.0))
add(EV["heavens"],chime(D(2,7),0.014,2.2)); add(EV["tricked"],pap(0.025)); add(EV["stone"],boom(0.08,45,1.6,2.4)); add(EV["stone"]+0.1,crack(0.04))
add(EV["farnese"],bell(D(-1,5),0.018,2.6)); add(EV["const"],shimmer(0.02,1.8))
for k in range(8): add(EV["const"]+0.1+k*0.09,celesta(D(2,[0,4,7,11,14,11,7,4][k]),1.0,0.008))
add(EV["y1595"],pap(0.03)); add(EV["titled"],chime(D(2,0),0.014,2.0)); add(EV["atlantic"],lp(bp(noise(2.2),120,800),900)*np.sin(np.pi*T_(2.2)/2.2)*0.04)
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.15
master.master(vo,bus,SR,"mix.wav",bus_gain=BG)
