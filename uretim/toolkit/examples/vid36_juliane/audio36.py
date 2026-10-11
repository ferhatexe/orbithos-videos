import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid36"); sys.path.insert(0,"/home/claude/toolkit")
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
# ======================== MUSIC ========================
# chord progression per section (semitones from D3); minor for danger, major for home/rescue
MIN=[[0,3,7],[-4,0,3],[-7,-3,0],[-2,2,5]]      # Dm  Bb  G  C
MAJ=[[0,4,7],[-5,-1,2],[-3,0,4],[-7,-3,0]]     # D  A  Bm  G
def sec(name): s=S(name); return s["s"],s["e"]
def chords(t0,t1,prog,step=3.5,amp=0.022,oct=0):
    x=t0; k=0
    while x<t1-0.5:
        dd=min(step+1.2,t1-x+0.6)
        for s in prog[k%len(prog)]: add(x,pad(D(oct,s),dd,amp,0.9,1.0))
        x+=step; k+=1
def arp(t0,t1,prog,step=0.42,amp=0.035,pat=(0,1,2,1),oct=1,step_chord=3.5):
    x=t0; k=0
    while x<t1-0.3:
        ch=prog[int((x-t0)//step_chord)%len(prog)]; s=ch[pat[k%len(pat)]]+(12 if k%8==7 else 0)
        add(x,kal(D(oct,s),1.4,amp)); x+=step; k+=1
a,b=sec("hook"); chords(a+0.3,b,MIN,4.0,0.018); add(a,drone(D(-1),b-a+1,0.025,2,1.5))
a,b=sec("lima"); chords(a,b,MAJ,3.6,0.018); arp(a+0.4,b-1.2,MAJ,0.45,0.03,(0,2,1,2),1,3.6)
a,b=sec("storm"); add(a,drone(D(-2),b-a,0.05,3,0.5,300));
for x in np.arange(a+1.5,EV["mother"]-0.6,0.5): add(x,kal(D(0,0 if int(x*2)%4 else 1),0.6,0.02))
for s_ in (0,3,8): add(EV["mother"]-0.3,pad(D(0,s_),EV["struck"]-EV["mother"]+0.6,0.022,0.6,0.4))
a,b=sec("fall"); add(a,pad(D(1,0),EV["black"]-a+0.5,0.012,1.0,1.0)); add(a,pad(D(1,1),EV["black"]-a+0.5,0.008,1.0,1.0))
a,b=sec("wake"); add(EV["woke"],pad(D(0,0),b-EV["woke"],0.012,2.0,1.0)); add(EV["woke"],pad(D(0,7),b-EV["woke"],0.009,2.0,1.0))
for x,s_ in zip(np.arange(EV["collar"],EV["called"],1.6),[0,3,7,10,7,3,0,-2,0,3,7,3,0]): add(x,kal(D(1,s_),1.8,0.025))
a,b=sec("rule"); chords(a,b,[[0,3,7],[3,7,10],[5,8,12],[7,10,14]],3.5,0.016); arp(EV["lost"],b-0.5,[[0,3,7],[3,7,10]],0.36,0.028,(0,1,2,1),1,3.5)
a,b=sec("walk"); chords(a,b,MIN,4.0,0.016);
for x in np.arange(a+0.3,b-0.5,0.571):
    md=1-0.8*(EV["day4"]-0.4<x<EV["cut"]-0.3); add(x,kal(D(0,[0,7,3,7][int((x-a)/0.571)%4]),0.9,0.026*md))
a,b=sec("river"); chords(a,b,[[0,3,7],[-2,2,5],[-4,0,3],[-5,-2,2]],3.2,0.016); arp(a+0.2,EV["saw"]-0.4,[[0,3,7],[-2,2,5],[-4,0,3],[-5,-2,2]],0.27,0.026,(0,1,2,3%3),2,3.2)
add(EV["saw"],chime(D(2,7),0.035)); add(EV["saw"]+0.12,chime(D(2,12),0.03))
a,b=sec("hut"); add(a,pad(D(0,0),b-a,0.012,1.0,1.0)); add(a,pad(D(0,3),b-a,0.008,1.0,1.0))
a,b=sec("rescue"); chords(a,EV["of92"]-0.4,MAJ,3.6,0.018); arp(EV["cleaned"]-0.3,EV["of92"]-0.6,MAJ,0.4,0.03,(0,1,2,1),1,3.6)
for s_ in (0,4,7): add(EV["of92"]-0.4,pad(D(0,s_-12+12),b-EV["of92"]+1.4,0.014,1.5,1.5))
a,b=sec("today"); chords(a,b,MAJ,3.0,0.02); arp(a+0.2,b,MAJ,0.3,0.03,(0,1,2,1,2,1),1,3.0)
a,b=sec("end");
for s_ in (0,4,7,11): add(a,pad(D(0,s_),b-a+0.5,0.017,1.2,2.5))
for k,s_ in enumerate((0,4,7,12,7,4)): add(a+0.5+k*0.55,kal(D(1,s_),1.8,0.026))
out+=np.sin(2*np.pi*D(-2)*t)*0.008*np.clip(np.interp(t,[0,2,TOTAL-3,TOTAL],[0,1,1,0]),0,1)
# ======================== SFX ========================
# transitions: paper tear swoosh + soft thump (unique to this video)
for s_ in SC[1:]:
    b_=s_["s"]; add(b_-0.32,whoosh(0.64,0.07,350,1900)); add(b_-0.05,pap(0.06)); add(b_,boom(0.12,90,6,0.6))
# hook: falling wind, rustle into canopy, sunrise birds, card taps
add(0.2,whoosh(EV["landed"]+1.5,0.05,200,900,False)); add(EV["twomiles"],boom(0.35,60,2.2,2.0)); add(EV["twomiles"],pap(0.05))
add(EV["landed"]+1.3,lp(bp(noise(1.6),300,2200),2500)*np.exp(-T_(1.6)*2.2)*0.10)
add(EV["alone"],pap(0.05)); add(EV["alone"],pad(D(0,0),2.8,0.02,0.05,1.5))
for k in range(6): add(EV["eleven"]+0.5+k*0.42,chirp_bird(0.02))
add(EV["alive"],chime(D(1,7),0.04)); add(EV["alive"]+0.08,chime(D(1,11),0.03)); add(EV["alive"],pap(0.05))
# lima
add(EV["name"],pap(0.05)); add(EV["grad"],whoosh(0.5,0.05,600,2400));
for k in range(10): add(EV["grad"]+0.15+k*0.07,chime(D(3,[0,4,7,12][k%4]),0.008,0.8))
add(EV["lima"],pap(0.04)); add(EV["parents"],pap(0.04)); add(EV["parents"]+0.25,pap(0.04)); add(EV["station"],pap(0.04))
tt=T_(EV["flight"]-EV["flying"]); add(EV["flying"],lp(np.sin(2*np.pi*110*tt+3*np.sin(2*np.pi*55*tt)),600)*np.sin(np.pi*tt/tt[-1])*0.018)
add(EV["flight"]-0.3,whoosh(0.4,0.05,500,2000)); add(EV["n92"],boom(0.35,75,5,1.0)); add(EV["n92"],pap(0.08))
# storm: rain, engines, thunder, turbulence, presents, lightning strike, break-up
a,b=sec("storm"); amb(400,2600,0.035,a,EV["broke"]+1.5,1.5,1.0,0.2,0.4)
tt=T_(EV["broke"]-a); eng=lp(np.sin(2*np.pi*np.cumsum(95+3*np.sin(2*np.pi*0.3*tt))/SR)*0.6+np.sin(2*np.pi*190*tt)*0.2+lp(rng.normal(0,1,len(tt)),300)*0.3,500)*np.clip(tt/1.0,0,1)*0.04; add(a,eng)
for e in (EV["wall"]+0.3,EV["flash"],EV["again"]): add(e,boom(0.55,45,0.9,3.5)); add(e+0.05,lp(bp(noise(1.2),200,1500),1600)*np.exp(-T_(1.2)*3)*0.12)
for x in np.arange(EV["shook"],EV["mother"]-0.4,0.23): add(x+rng.uniform(0,0.1),boom(0.10,110+rng.uniform(-20,20),9,0.4))
for k in range(9): add(EV["bags"]+k*0.33+rng.uniform(0,0.1),boom(0.12,150,10,0.3)); add(EV["bags"]+k*0.33,pap(0.03))
add(EV["theend"],pad(D(-1,0),3,0.02,0.3,1.5))
add(EV["struck"],boom(0.6,38,0.7,4.5)); add(EV["struck"],lp(bp(noise(0.5),300,2500),2800)*np.exp(-T_(0.5)*9)*0.35)
add(EV["broke"],boom(0.5,32,0.6,4.0)); add(EV["broke"],whoosh(3.0,0.10,150,900,False))
# fall: wind roar building, then silence at "black"
a,b=sec("fall"); d=EV["black"]-a+0.6; tt=T_(d); x=lp(bp(rng.normal(0,1,len(tt)),150,1300),1500)*(0.6+0.4*np.clip(tt/d*1.5,0,1))*np.clip(tt/0.4,0,1)*np.clip((d-tt)/0.7,0,1)*0.09
x*=1+0.25*np.sin(2*np.pi*0.9*tt); add(a,x)
for k in range(6): add(a+0.6+k*1.6,whoosh(0.9,0.05,250,1100))
add(EV["m3000"],pap(0.04)); add(EV["forest"],whoosh(1.4,0.05,400,1500))
# wake: forest ambience, insects, birds, drips; echoing silence after "Nobody answered"
a,b=sec("wake"); amb(1800,3200,0.006,EV["woke"],b+0.4,2,1.0,0.6,6.0); amb(200,900,0.012,EV["woke"],b+0.4,2,1)
for x in np.arange(EV["woke"]+0.8,b,2.3): add(x+rng.uniform(0,1),chirp_bird(0.012))
for x in np.arange(EV["woke"]+1.5,b,1.9): add(x,plip(0.02,900,1700))
for e in (EV["collar"],EV["cuts"],EV["conc"],EV["eye"],EV["glasses"],EV["shoe"]): add(e,pap(0.035))
add(EV["spinseats"],whoosh(0.6,0.04,500,1500)); add(EV["trees"],lp(bp(noise(0.7),300,2000),2200)*np.exp(-T_(0.7)*5)*0.05)
for k in range(3): add(EV["mom"]+k*0.45,pad(D(1,7-k*2),1.2,0.012*(1-0.3*k),0.05,0.9))
# rule: pencil scribbles + water drip motif
a,b=sec("rule"); add(EV["father"]-0.2,whoosh(0.4,0.03,800,2000))
for e,dd in ((EV["water"],0.6),(EV["downhill"],1.4),(EV["rivers"],1.0)): add(e,lp(bp(noise(dd),900,2600),2800)*(0.5+0.5*np.abs(np.sin(2*np.pi*7*T_(dd))))*0.012)
add(EV["water"],plip(0.07)); add(EV["rivers"],plip(0.05,500,1100)); add(EV["people"],chime(D(2,4),0.03)); add(EV["creek"],plip(0.06,800,1600)); add(EV["lost"],pap(0.04))
# walk: flowing creek, wading steps, insects; muted at day 4; flies
a,b=sec("walk"); amb(250,1600,0.022,a,b+0.4,1,1,0.15,0.2); amb(1900,3000,0.004,a,b,1,1,0.7,5)
for x in np.arange(a+0.2,b,0.571):
    st=lp(bp(noise(0.16),180,1400),1500)*np.exp(-T_(0.16)*25)*0.05; add(x,st*(1-0.6*(EV["day4"]-0.4<x<EV["cut"]-0.3)))
add(EV["sweets"],pap(0.04));
for k in range(5): add(EV["sweets"]+0.2+k*0.1,chime(D(3,[0,4,7,9,12][k]),0.008,0.7))
add(EV["day4"],pad(D(-1,0),EV["cut"]-EV["day4"],0.02,0.5,1.0)); add(EV["notamong"],chime(D(1,0),0.025,3.0))
tt=T_(b-EV["flies"]); fly=lp(np.sign(np.sin(2*np.pi*np.cumsum(185+15*np.sin(2*np.pi*3*tt))/SR)),900)*0.006*(0.6+0.4*np.sin(2*np.pi*0.7*tt))*np.clip(tt/0.3,0,1)*np.clip((tt[-1]-tt)/0.3,0,1); add(EV["flies"],fly)
add(EV["worse"],pap(0.05)); add(EV["worse"],boom(0.2,70,4,1.0))
# river: water grows; drips on each stage; current; arrival chime
a,b=sec("river"); d=b-a; tt=T_(d); x=lp(bp(rng.normal(0,1,len(tt)),150,1800),2000)*np.clip(0.3+0.7*tt/d,0,1)*np.clip(tt/1,0,1)*np.clip((d-tt)/1,0,1)*0.045; add(a,x)
for e,(f0,f1) in ((EV["creekb"],(900,1800)),(EV["stream"],(700,1400)),(EV["riverw"],(500,1000))): add(e,plip(0.06,f0,f1)); add(e,pap(0.04))
for e in (EV["boat"],EV["path"],EV["shelter"]): add(e,pap(0.05))
# hut: wood creaks, can clank, tally ticks, rain + crickets at dusk
a,b=sec("hut"); tt=T_(0.6); clank=sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*dd) for f,dd in ((420,9),(1130,14),(1870,20)))*0.03; add(EV["gas"],lp(clank,3500)); add(EV["gas"],pap(0.04))
add(EV["remem"],pad(D(1,7),3.5,0.012,0.6,1.5)); add(EV["remem"],whoosh(0.6,0.03,600,1800))
n0=EV["thirty"]-0.3; n1=EV["onebyone"]+1.3
for i in range(30): add(n0+(n1-n0)*i/30,lp(bp(noise(0.03),500,2200),2400)*np.exp(-T_(0.03)*120)*0.035)
add(EV["thirty"],pap(0.05))
amb(500,2600,0.02,EV["lay"]-0.3,b+0.4,1.5,1,0.2,0.3)
for x in np.arange(EV["lay"],b,0.38): add(x,lp(np.sin(2*np.pi*2600*T_(0.05))*np.exp(-T_(0.05)*60),3200)*0.006)
# rescue: river, birds, voices as soft murmur, water-spirit shimmer, paddles, the one golden dot, the falling flower
a,b=sec("rescue"); amb(200,1500,0.02,a,EV["of92"]-0.2,1,1.2)
for x in np.arange(a+0.5,EV["of92"]-1,2.1): add(x,chirp_bird(0.012))
for k in range(3): add(EV["voices"]+k*0.3,lp(bp(noise(0.35),180,700),800)*np.sin(np.pi*T_(0.35)/0.35)*0.02)
for k,s_ in enumerate((7,11,14,19)): add(EV["spirit"]-0.1+k*0.08,chime(D(2,s_),0.014,2.2))
for x in np.arange(EV["cleaned"],EV["of92"]-0.4,0.9): add(x,lp(bp(noise(0.3),200,1300),1500)*np.exp(-T_(0.3)*10)*0.05)
add(EV["only"],chime(D(2,7),0.045,3.5)); add(EV["mother2"],chime(D(1,0),0.03,4.0))
# today: bright birds + chimes
a,b=sec("today"); amb(250,1500,0.012,a,b+0.4,1,1)
for x in np.arange(a+0.3,b,1.1): add(x+rng.uniform(0,0.4),chirp_bird(0.014))
add(EV["pang"],chime(D(2,0),0.04)); add(EV["pang"]+0.1,chime(D(2,4),0.03)); add(EV["biology"],pap(0.04)); add(EV["protect"],pap(0.04))
# end: water, the final drip motif on "Follow the water", logo chime
a,b=sec("end"); amb(200,1600,0.02,a,b,1,2)
add(EV["follow"]-0.05,plip(0.09,700,1500)); add(EV["follow"]+0.5,plip(0.05,900,1800)); add(EV["follow"],boom(0.25,55,1.5,2.5))
tf=Lx("Follow the water")[1]+0.6; add(tf,chime(D(1,0),0.04,3.0)); add(tf+0.1,chime(D(1,7),0.03,3.0)); add(tf+0.2,chime(D(2,4),0.025,3.0))
# ======================== MASTER ========================
bus=lp(out,9000)
vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
master.master(vo,bus,SR,"mix.wav",bus_gain=0.42)
