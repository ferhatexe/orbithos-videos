import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid63"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sc_(n): s=S(n); return s["s"],s["e"]
C=lambda o,s=0:130.81*2**o*2**(s/12)
def ticks(t0,t1,amp=0.006):
    x=t0;k=0
    while x<t1: add(x,click(amp*(1.0 if k%2 else 0.65),2600 if k%2 else 1900,600)); x+=0.5;k+=1
def ratchet(at,dur=0.72,n=18):
    for k in range(n): add(at+dur*k/n,click(0.006,3500,900))
def celesta(f,amp=0.008): return chime(f,amp,1.6)
def cseq(t0,t1,notes,step=0.36,amp=0.0065):
    x=t0;k=0
    while x<t1-0.2: add(x,celesta(C(2,notes[k%len(notes)]),amp)); x+=step;k+=1
ticks(0.0,TOTAL)
add(0,drone(C(-2,0),TOTAL+0.4,0.014,0.4,0.8,280))
for (a,b),ch in ((sc_("hook"),[[0,4,7],[5,9,12]]),(sc_("rome"),[[0,4,7],[-3,0,4],[5,9,12]]),(sc_("swap"),[[-3,0,4],[2,5,9],[0,4,7],[-5,-1,2]]),(sc_("latin"),[[0,4,7],[5,9,12]])):
    t_=a;k=0
    while t_<b-0.3:
        for s_ in ch[k%len(ch)]: add(t_,pad(C(0,s_),min(3.4,b-t_+0.5),0.006,0.8,1.0))
        t_+=2.6;k+=1
cseq(0.1,S("rome")["e"],[0,4,7,12,7,4],0.36)
cseq(S("latin")["s"],TOTAL+0.1,[0,4,7,12,7,4],0.36)
NOTES=[0,2,4,5,7,9,11]
for i,k in enumerate(["sun","moon","mars","mercury","jupiter","venus","saturn"]): add(EV[k],bell(C(1,NOTES[i]),0.012,2.0))
add(EV["four"],bell(C(0,0),0.016,3.0))
for k0,kg,kd,nt in (("s_mars","tiw","tuesday",9),("s_merc","woden","wednesday",7),("s_jup","thor","thursday",4),("s_ven","frigg","friday",2)):
    ratchet(EV[k0]-0.3,0.4,10); add(EV[kg],cello(C(-1,nt),1.6,0.012,0.15,0.8)); add(EV[kd],bell(C(1,nt),0.012,1.8))
add(EV["thor"]+0.1,boom(0.035,70,4,1.2))
add(EV["s_sat"],bell(C(1,11),0.010,1.8))
for k in ("martes","mierc","jueves","viernes"): add(EV[k],celesta(C(3,7),0.008))
add(EV["thurs2"],bell(C(0,4),0.016,3.0)); add(EV["thurs2"]+0.05,boom(0.03,70,4,1.0))
SH=[S("rome")["s"],S("swap")["s"],S("latin")["s"]]
for t_ in SH: ratchet(t_-0.36)
ratchet(TOTAL-0.62,0.62,16)
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.65
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
