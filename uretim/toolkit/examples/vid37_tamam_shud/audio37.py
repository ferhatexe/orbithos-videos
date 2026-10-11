import numpy as np, math, sys
sys.path.insert(0,"/home/claude/vid37"); sys.path.insert(0,"/home/claude/toolkit")
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
def tri(t_,f): return 2*np.abs(2*((t_*f)%1)-1)-1
def epiano(f,dur=2.4,amp=0.03):
    tt=T_(dur); s=np.sin(2*np.pi*f*tt)*np.exp(-tt*1.6)+0.3*np.sin(2*np.pi*f*2*tt)*np.exp(-tt*3)+0.12*np.sin(2*np.pi*f*7.0*tt)*np.exp(-tt*12)
    return lp(s*(1+0.12*np.sin(2*np.pi*5*tt))*amp*np.clip(tt/0.004,0,1),4200)
def bass(f,dur=0.7,amp=0.07):
    tt=T_(dur); s=np.sin(2*np.pi*f*tt)+0.4*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*6)+0.15*tri(tt,f)
    return lp(s*np.exp(-tt*3.2)*amp*np.clip(tt/0.01,0,1),900)
def brush(dur=0.35,amp=0.012):
    tt=T_(dur); return lp(bp(rng.normal(0,1,len(tt)),1500,4500),4500)*np.sin(np.pi*tt/dur)**1.5*amp
def click(amp=0.03):
    tt=T_(0.035); return lp(bp(rng.normal(0,1,len(tt)),700,2600),3000)*np.exp(-tt*160)*amp+np.sin(2*np.pi*220*tt)*np.exp(-tt*120)*amp*0.5
def typing(at,n,cps=28,amp=0.025):
    for i in range(n): add(at+i/cps+rng.uniform(-0.006,0.006),click(amp*rng.uniform(0.7,1.1)))
    add(at+n/cps+0.05,chime(1800,0.006,0.25))
def thud(amp=0.25): return boom(amp,95,7,0.6)+lp(bp(noise(0.6),150,900),1000)*np.exp(-T_(0.6)*18)*amp*0.6
Dm9=[0,3,7,10,14]; Gm9=[5,8,12,15,19]; A7b9=[7,11,14,17,20]; Bb9=[-4,0,3,7,10]
PROG=[Dm9,Gm9,Bb9,A7b9]; BEAT=0.714
def comp_piano(t0,t1,amp=0.02,prog=PROG,bar=4*BEAT,oct=0,sparse=False):
    x=t0;k=0
    while x<t1-0.4:
        ch=prog[k%len(prog)]
        for j,s_ in enumerate(ch): add(x+j*0.025,epiano(D(oct,s_),bar+0.6,amp*(0.8 if j else 1)))
        if not sparse: 
            for j,s_ in enumerate(ch[1:4]): add(x+2.5*BEAT+j*0.02,epiano(D(oct,s_),1.4,amp*0.6))
        x+=bar; k+=1
def walk(t0,t1,amp=0.06,prog=PROG):
    x=t0;k=0
    while x<t1-0.3:
        ch=prog[int((x-t0)//(4*BEAT))%len(prog)]; r=ch[0]; seq=[r,r+7,r+5,r+3 if k%2 else r-2]
        add(x,bass(D(-2,seq[k%4]),0.75,amp)); x+=BEAT; k+=1
def brushes(t0,t1,amp=0.010):
    x=t0;k=0
    while x<t1-0.3:
        add(x,brush(0.30,amp*(1.3 if k%2 else 0.7))); x+=BEAT; k+=1
def sec(name): s=S(name); return s["s"],s["e"]
# ======================== MUSIC (noir jazz trio) ========================
a,b=sec("hook"); comp_piano(a+0.3,b,0.016,sparse=True); add(a+0.3,bass(D(-2,0),2.5,0.08)); add(EV["y74"],bass(D(-2,0),2.5,0.08))
a,b=sec("beach"); comp_piano(a,b,0.014,sparse=True); 
a,b=sec("pockets"); walk(a,b,0.055); brushes(a,b); comp_piano(a,b,0.013)
a,b=sec("autopsy"); add(a,drone(D(-2),b-a,0.035,1.5,1.0,250)); 
for x in np.arange(a+0.5,b-0.5,2*BEAT): add(x,epiano(D(1,[1,0][int(x)%2]),1.4,0.012))
a,b=sec("suitcase"); walk(a,b,0.055,[Gm9,Dm9,A7b9,Dm9]); brushes(a,b); comp_piano(a,b,0.012,[Gm9,Dm9,A7b9,Dm9])
a,b=sec("scrap")
for k,s_ in enumerate([14,12,10,7,10,5,3,2,3,7,10,12,14,15,14,10,7,5,3,2,0,3,7,10,14,12,10,7]): add(a+0.5+k*0.7,chime(D(2,s_),0.010,1.6))
add(a,pad(D(0,0),b-a,0.012,1.5,1.5)); add(a,pad(D(0,3),b-a,0.009,1.5,1.5))
a,b=sec("book"); walk(a,b,0.05); brushes(a,b,0.008); comp_piano(a,b,0.012,sparse=True)
a,b=sec("code"); add(a,drone(D(-2,1),b-a,0.03,1.0,1.0,300))
for x in np.arange(a,EV["nurse"]-0.3,BEAT/2): add(x,bass(D(-2,0),0.3,0.035))
for s_ in (0,1,6): add(EV["shaken"]-0.2,pad(D(0,s_),3.0,0.012,0.4,1.5))
a,b=sec("years")
for x in np.arange(a,b,0.5): add(x,click(0.02))
comp_piano(a,b,0.012,[Dm9,Bb9],sparse=True)
a,b=sec("dna"); 
MOD=[[0,4,7,11,14],[5,9,12,16,19],[-3,0,4,7,11],[2,5,9,12,16]]
for x in np.arange(EV["abbott"]-0.3,b,0.18):
    k=int((x-EV["abbott"])/0.18); ch=MOD[int((x-EV["abbott"])//(8*0.36))%4]; add(x,kal(D(1,ch[k%5]),0.8,0.018))
for k,ch in enumerate(MOD*4):
    x=EV["abbott"]-0.3+k*8*0.36
    if x<b-1:
        for s_ in ch[:3]: add(x,pad(D(0,s_),8*0.36+0.8,0.010,0.6,0.8))
a,b=sec("end"); comp_piano(a,b-2,0.016,[Dm9,Bb9],sparse=True); tf=Lx("Tamam Shud. It is")[1]+0.6
for j,s_ in enumerate(Dm9): add(tf+j*0.04,epiano(D(0,s_),4.0,0.02))
add(tf,bass(D(-2,0),3.0,0.08))
# ======================== SFX ========================
for s_ in SC[1:]:   # flashbulb pop: click + soft rising whine + low thump
    b_=s_["s"]; add(b_-0.02,click(0.06)); tt=T_(0.5); add(b_,lp(np.sin(2*np.pi*np.cumsum(900+1400*tt)/SR)*np.exp(-tt*7)*0.012,3500)); add(b_,boom(0.10,80,8,0.5))
# typing for typed cards: (event, chars)
TY=[(0.3,15),(0.9,32),(EV["labels"],15),(EV["secret"],25),(EV["who"],19),(EV["somerton"],24),(EV["dawn"],8),(EV["suit"],9),(EV["shoes"],15),(EV["crossed"],12),(EV["cig"],21),(EV["evening"],19),
    (EV["train"],12),(EV["bus"],10),(EV["gum"],3),(EV["matches"],7),(EV["combs"],7),(EV["pack"],10),(EV["cut"],24),(S("autopsy")["s"]+0.3,20),(EV["liver"],16),(EV["poison"],7),(EV["rare"],28),
    (EV["station"],24),(EV["daybefore"],22),(EV["mend"],25),(EV["april"],10),(EV["tiny"],19),(EV["finished"],25),(EV["final"],21),(EV["july"],9),(EV["car"],29),(EV["naval"],18),(EV["amateurs"],21),
    (EV["nurse"],21),(EV["castf"],12),(EV["y2021"],14),(EV["abbott"],34),(EV["hairs"],34),(EV["y2022"],9),(EV["engineer"],19),(EV["melb"],21),(EV["noname2"],8),(EV["secret2"],16),(EV["poetry"],20)]
for e,n in TY: typing(e,n,28,0.02)
for e in (EV["wallet"],EV["noname"],EV["noviol"],EV["nomoney"],EV["noid"],EV["again"],EV["nokeane"],EV["matched"]+0.6,EV["cracked"],EV["notconf"]): add(e,thud(0.22))
for k in range(5): add(EV["clean"]+k*0.12,thud(0.10))
# waves / wind
for nm in ("hook","beach","end"):
    a,b=sec(nm); d=b-a+0.5; tt=T_(d); x=lp(bp(rng.normal(0,1,len(tt)),120,1400),1500)*(0.55+0.45*np.sin(2*np.pi*0.12*tt)**2)*np.clip(tt/1.2,0,1)*np.clip((d-tt)/1.0,0,1)*0.05; add(a,x)
add(EV["tamam"],chime(D(2,0),0.03,3)); add(EV["tamam"]+0.1,chime(D(2,3),0.025,3)); add(EV["y74"],thud(0.25))
for k in range(8): add(EV["swim"]+0.3+k*0.4,lp(bp(noise(0.12),200,1200),1300)*np.exp(-T_(0.12)*30)*0.03)
add(EV["cig"],whoosh(1.5,0.02,300,1200)); add(EV["raised"],whoosh(0.6,0.02,400,1200)); add(EV["drop"],thud(0.06))
tt=T_(EV["asleep"]+1.5-EV["evening"]); add(EV["evening"],lp(np.sin(2*np.pi*600*tt)*(0.5+0.5*np.sin(2*np.pi*31*tt)),900)*0.003*np.clip(tt/1,0,1))
# pockets
for e in (EV["train"],EV["bus"],EV["gum"],EV["matches"],EV["combs"],EV["pack"]): add(e,pap(0.04))
for k in range(3): add(EV["matches"]+0.05+k*0.05,click(0.02))
add(EV["brand"],whoosh(0.4,0.025,500,1800))
for k in range(4): add(EV["cut"]-0.4+k*0.22,lp(bp(noise(0.06),1200,3000),3200)*np.exp(-T_(0.06)*60)*0.05)
# autopsy
for k in range(5): add(EV["poison"]+0.2+k*0.15,chime(2200+k*90,0.008,0.6))
add(EV["wrote"]-0.3,lp(bp(noise(2.0),900,2800),3000)*(0.5+0.5*np.abs(np.sin(2*np.pi*5*T_(2.0))))*0.010)
# station
a,b=sec("suitcase"); amb(200,900,0.02,a,b,1,1,0.4,0.7)
tt=T_(1.6); add(a+1.0,lp((np.sin(2*np.pi*620*tt)+0.6*np.sin(2*np.pi*740*tt))*np.clip(tt/0.2,0,1)*np.clip((1.6-tt)/0.4,0,1),2000)*0.012)
for x in np.arange(a,b,1.0): add(x,click(0.012))
add(EV["again"]-0.4,click(0.06)); add(EV["again"]-0.3,click(0.06)); add(EV["again"]-0.2,lp(bp(noise(0.6),300,1200),1300)*np.sin(np.pi*T_(0.6)/0.6)*0.04)
add(EV["thread"],chime(D(2,7),0.03)); 
for k in range(3): add(EV["items"]+k*0.2,pap(0.035))
# scrap / book
add(EV["tiny"],whoosh(0.4,0.02,600,1600)); add(EV["rolled"],lp(bp(noise(1.0),500,2500),2800)*np.sin(np.pi*T_(1.0))*0.03); add(EV["twowords2"],lp(bp(noise(0.8),400,2200),2400)*np.sin(np.pi*T_(0.8)/0.8)*0.03)
add(EV["final"]-0.4,thud(0.12)); add(EV["final"],whoosh(0.6,0.03,300,1400))
add(EV["car"],thud(0.12)); add(EV["matched"],pap(0.05))
for k in range(5): add(EV["five"]+k*0.3,lp(bp(noise(0.25),900,2600),2800)*np.sin(np.pi*T_(0.25)/0.25)*0.012)
# code: UV hum, shuffle ticks
a,b=sec("code"); tt=T_(EV["nurse"]-a); add(a,lp(np.sign(np.sin(2*np.pi*100*tt))*0.3+np.sin(2*np.pi*100*tt),600)*0.010*np.clip(tt/0.5,0,1))
for x in np.arange(EV["naval"],EV["nobody"],0.083): add(x,click(0.012))
add(EV["castf"],pad(D(1,0),2.5,0.012,0.3,1.2))
# years: grave bell
a,b=sec("years"); add(a+0.3,chime(D(-1,0),0.05,4.0)); 
for e in (EV["spy"],EV["suicide"],EV["lover"]): add(e,pap(0.05))
# dna
for k in range(4): add(EV["exhumed"]+k*0.35,thud(0.09))
for x in np.arange(EV["abbott"],EV["tree"],0.9): add(x,lp(np.sin(2*np.pi*1200*T_(0.06))*np.exp(-T_(0.06)*40),2500)*0.012)
gt0=EV["tree"]; 
for k in range(40): add(gt0+k*0.065,lp(np.sin(2*np.pi*(500+k*25)*T_(0.05))*np.exp(-T_(0.05)*60),3000)*0.010)
add(EV["announced"],whoosh(0.8,0.03,300,1500)); add(EV["webb"]-0.1,boom(0.12,60,2,2.0))
for j,s_ in enumerate((0,4,7,11,14)): add(EV["webb"]+j*0.03,epiano(D(1,s_),3.0,0.018))
# end: scrap flutter
a,b=sec("end"); add(a+0.5,whoosh(4.0,0.03,300,1200,False))
add(EV["tamam3"],chime(D(2,0),0.03,3)); add(EV["mystery"],bass(D(-2,1),2.0,0.06))
# ======================== MASTER ========================
bus=lp(out,9000)
vo=np.zeros(N)
for ln in LINES:
    sr,dd=wf.read(f"vo/vo_{ln['i']:02d}.wav"); dd=dd.astype(np.float64)/32768; i=int(ln["s"]*SR); dd=dd[:N-i]; vo[i:i+len(dd)]+=dd
master.master(vo,bus,SR,"mix.wav",bus_gain=1.0)
