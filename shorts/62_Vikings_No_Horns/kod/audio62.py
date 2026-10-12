import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid62"); sys.path.insert(0,"/home/claude/toolkit")
import scipy.io.wavfile as wf
import ev, master
from sfxlib import *
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
init(TOTAL)
def sc_(n): s=S(n); return s["s"],s["e"]
Dm=lambda o,s=0:146.83*2**o*2**(s/12)
def drum(amp=0.05,f=60):
    tt=T_(0.8); return (np.sin(2*np.pi*np.cumsum(f*(1+0.7*np.exp(-tt*22)))/SR)*np.exp(-tt*6)+lp(noise(0.8),300)*np.exp(-tt*16)*0.5)*amp
def lur(f,dur,amp=0.008):
    tt=T_(dur); s=sum(np.sin(2*np.pi*f*k*tt*(1+0.002*np.sin(2*np.pi*4*tt)))/k**0.9 for k in range(1,9))
    return lp(s*np.clip(tt/0.25,0,1)*np.clip((dur-tt)/0.5,0,1)*amp,2200)
def chisel(at,n=6,amp=0.010):
    g=np.random.default_rng(int(at*100))
    for k in range(n): tt=T_(0.06); add(at+k*0.07+g.uniform(0,0.02),bp(noise(0.06),1800,6000)*np.exp(-tt*80)*amp*g.uniform(0.6,1))
def grind(at,dur=0.72):
    tt=T_(dur); add(at,lp(bp(noise(dur),60,500),600)*np.sin(np.pi*tt/dur)**1.5*0.03)
def clang(at,amp=0.02): add(at,bell(Dm(2,6),amp*0.6,1.5)); add(at,crack(amp))
add(0,drone(Dm(-2,0),TOTAL+0.4,0.020,0.3,0.8,260)); add(0,drone(Dm(-1,7),TOTAL+0.4,0.007,0.5,0.8,380))
x=0.0
while x<TOTAL-0.3:
    add(x,drum(0.030,58)); add(x+0.75,drum(0.018,70)); x+=1.5
for (a,b),ch in ((sc_("hook"),[0,3,7]),(sc_("helmet"),[0,3,7]),(sc_("opera"),[5,8,12]),(sc_("bronze"),[-2,2,5])):
    t_=a
    while t_<b-0.5:
        for s_ in ch: add(t_,cello(Dm(-1,s_),2.8,0.006,0.6,1.0))
        t_+=2.6
a,b=sc_("hook"); add(EV["never"],clang(EV["never"]) or np.zeros(1)); chisel(EV["image"])
chisel(EV["onlyone"]); chisel(EV["norway"]); chisel(EV["gjer"])
chisel(EV["rounded"]); add(EV["nohorns"],drum(0.04,50))
add(EV["blade"]-0.2,whoosh(0.5,0.02,600,4000)); clang(EV["catch"],0.03)
chisel(EV["c19"]); add(EV["painters"],scribble(1.2,0.006))
add(EV["y1876"],choir_(Dm(1,7),2.4,0.010)); add(EV["y1876"],choir_(Dm(1,3),2.4,0.007)); chisel(EV["doepler"])
add(EV["sensation"],lp(bp(noise(1.6),400,3000),3200)*np.sin(np.pi*T_(1.6)/1.6)*0.010)   # applause wash
add(EV["bronze"]-0.2,lur(Dm(-1,0),2.6,0.010)); add(EV["y1700"],lur(Dm(-1,7),2.2,0.008)); chisel(EV["cerem"])
add(EV["remember"],drum(0.05,48))
SH=[S("helmet")["s"],Lx("It's a rounded")[0]-0.3,S("opera")["s"],Lx("Then in 1876")[0]-0.3,Lx("The opera was")[0]-0.3,S("bronze")["s"],Lx("So next time")[0]-0.3]
for t_ in SH: grind(t_-0.36)
grind(TOTAL-0.62,0.62)
bus=lp(out(),9000); N=len(out()); vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
BG=float(sys.argv[1]) if len(sys.argv)>1 else 1.2
master.master(vo,bus,SR,"mix.wav",bus_gain=BG,lufs=-13.95)
