import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid61"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sc_(n): s=S(n); return s["s"],s["e"]
F=lambda o,s=0:174.61*2**o*2**(s/12)
def harp(f,dur=2.2,amp=0.009):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt)*np.exp(-tt*(1.6+k*1.2))/k**1.3 for k in range(1,6))
    return lp(s*amp*np.clip(tt/0.003,0,1),5000)
def harp_seq(t0,t1,chords,step=0.28,cl_=2.6,amp=0.008):
    x=t0;k=0
    while x<t1-0.2:
        ch=chords[int((x-t0)/cl_)%len(chords)]; n=ch[k%len(ch)]+(12 if (k//len(ch))%2 else 0); add(x,harp(F(1,n),2.0,amp)); x+=step;k+=1
def fpads(t0,t1,chords,cl=2.6,amp=0.007):
    x=t0;k=0
    while x<t1-0.3:
        for s_ in chords[k%len(chords)]: add(x,pad(F(-1,s_),min(cl+1.0,t1-x+0.5),amp,0.9,1.2))
        x+=cl;k+=1
def dropfx(at):
    add(at,plip(0.016,600,1400)); add(at+0.05,lp(bp(noise(0.9),400,3000),3200)*np.sin(np.pi*T_(0.9)/0.9)**2*0.006)
CH=[[0,4,7,11],[5,9,12,16],[2,5,9,12],[7,11,14,17]]
add(0,drone(F(-2,0),TOTAL+0.4,0.014,0.4,0.8,300))
fpads(0,TOTAL+0.3,CH,2.6,0.007); harp_seq(0.1,TOTAL+0.1,CH,0.30,2.6,0.0075)
a,b=sc_("earth"); add(EV["scatter"],shimmer(0.010,1.5)); add(EV["away"],whoosh(1.0,0.008,3000,800))
a,b=sc_("mars"); add(EV["less"],whoosh(1.4,0.006,200,600)); 
d=EV["grains"]-EV["dust"]+0.4; tt=T_(d); add(EV["dust"]-0.4,lp(bp(noise(d),200,1600),1800)*(0.6+0.4*np.sin(2*np.pi*0.25*tt))*np.clip(tt/0.6,0,1)*np.clip((d-tt)/0.6,0,1)*0.010)
add(EV["fwd"],shimmer(0.012,1.4)); add(EV["size"],harp(F(2,7),1.8,0.010))
add(EV["glow"],choir_(F(0,4),2.4,0.008)); add(EV["glow"],choir_(F(0,11),2.4,0.006))
add(EV["thirds"],chime(F(2,4),0.010,1.8)); add(EV["twilight"],drone(F(-2,5),3.5,0.012,0.6,1.5,400))
add(EV["curio"],beep(900,0.06,0.006)); add(EV["curio"]+0.12,beep(1200,0.06,0.006)); add(EV["y2015"],click(0.012,2000,300))
add(EV["remember"],harp(F(1,0),2.4,0.012))
SH=[S("earth")["s"],Lx("At sunset, sunlight")[0]-0.3,S("mars")["s"],Lx("Instead")[0]-0.3,Lx("But the grains")[0]-0.3,S("blue")["s"],Lx("The Sun looks")[0]-0.3,Lx("And high dust")[0]-0.3,Lx("So if you ever")[0]-0.3]
for t_ in SH: dropfx(t_-0.4)
dropfx(TOTAL-0.7)
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.4
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
