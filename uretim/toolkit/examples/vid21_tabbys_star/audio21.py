import numpy as np, math, subprocess, sys
sys.path.insert(0,"/home/claude/vid21")
from scipy.signal import fftconvolve, butter, sosfilt
import scipy.io.wavfile as wf
import ev
EV=ev.EV; LINES=ev.LINES; SC=ev.SC; TOTAL=ev.T["total"]; S=ev.S; Lx=ev.Lx
SR=44100; N=int((TOTAL+0.5)*SR); t=np.arange(N)/SR; rng=np.random.default_rng(51)
def lp(x,f): return sosfilt(butter(2,f/(SR/2),'low',output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f/(SR/2),'high',output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a/(SR/2),b/(SR/2)],'band',output='sos'),x)
out=np.zeros(N)
def add(at,sig,g=1.0):
    i=int(at*SR)
    if i<0: sig=sig[-i:]; i=0
    L=min(len(sig),N-i)
    if L>0: out[i:i+L]+=sig[:L]*g
def span(n): s=S(n); return s["s"],s["e"]
def env_(dur,att=0.02,rel=0.3):
    tt=np.arange(int(dur*SR))/SR; return np.clip(tt/att,0,1)*np.clip((dur-tt)/rel,0,1)
def lyre(f,dur=2.2,amp=0.05):
    tt=np.arange(int(dur*SR))/SR; s=sum(a*np.sin(2*np.pi*f*(k+1)*tt)*np.exp(-tt*(1.8+k*1.4)) for k,a in enumerate([1,0.5,0.25,0.12]))
    return s*amp*np.clip(tt/0.012,0,1)
def boom(amp=1.0,f0=55,dec=1.6,dur=3.0):
    tt=np.arange(int(dur*SR))/SR; f=f0*0.6+f0*0.8*np.exp(-tt*5)
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*dec)+lp(rng.normal(0,1,len(tt)),250)*np.exp(-tt*dec*1.5)*0.5)*amp*np.clip(tt/0.04,0,1)
def water_rush(dur,amp=0.3): L=int(dur*SR); tt=np.arange(L)/SR; return lp(bp(rng.normal(0,1,L),150,2500),3000)*np.sin(np.pi*tt/dur)*amp
# --- music: soft ambient pads + sparse plucks; minor until the public steps in (Kickstarter), then major ---
def gl(f,dur=3.2,amp=0.05,att=0.5):
    tt=np.arange(int(dur*SR))/SR
    s=np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*f*2.003*tt)+0.1*np.sin(2*np.pi*f*3.01*tt)
    return lp(s*np.clip(tt/att,0,1)*np.exp(-tt*0.5)*np.clip((dur-tt)/0.6,0,1)*amp,7000)
def pluck(f,dur=2.2,amp=0.05):
    tt=np.arange(int(dur*SR))/SR; s=sum(a_*np.sin(2*np.pi*f*(k+1)*tt)*np.exp(-tt*(2.2+k*1.6)) for k,a_ in enumerate([1,.45,.2,.1]))
    return lp(s*amp*np.clip(tt/0.012,0,1),6000)
def tick(f=2000,amp=0.04,dur=0.05):
    tt=np.arange(int(dur*SR))/SR; return lp(np.sin(2*np.pi*f*tt)*np.exp(-tt*70)*amp*np.clip(tt/0.003,0,1),5000)
def sweep(dur,f0,f1,amp=0.05):
    tt=np.arange(int(dur*SR))/SR; f=f0+(f1-f0)*(tt/dur)**2; return lp(np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*tt/dur)**2*amp,6000)
def rustle(dur,amp=0.08,lo=400,hi=3000):
    tt=np.arange(int(dur*SR))/SR; return lp(bp(rng.normal(0,1,len(tt)),lo,hi),hi)*np.sin(np.pi*tt/dur)**2*amp
def theremin(f,dur,amp=0.04):
    tt=np.arange(int(dur*SR))/SR; return lp(np.sin(2*np.pi*np.cumsum(f*(1+0.012*np.sin(2*np.pi*5.2*tt)))/SR)*np.sin(np.pi*tt/dur)**1.5*amp,4000)
tk=S("kickstarter")["s"]
env=np.interp(t,[0,0.3,1.5,S("kepler")["s"],S("star")["s"],S("aliens")["s"],tk,S("result")["s"],S("end")["s"],TOTAL-2,TOTAL],[0,0,0.5,0.5,0.5,0.45,0.6,0.7,0.75,0.65,0])
root=110.0
for ci in range(int(TOTAL/3.5)+1):
    s0=ci*3.5; ch=([0,3,7],[-2,2,5],[-4,0,3],[-5,-1,2]) if s0<tk else ([0,4,7],[-3,0,4],[5,9,12],[7,11,14])
    for sm_ in ch[ci%4]: add(s0,gl(root*2**(sm_/12),4.4,0.02,1.2),float(np.interp(s0,t[::441],env[::441])))
x=1.6; k=0
while x<TOTAL-3:
    semi=([0,3,7,10,12,10,7,3] if x<tk else [0,4,7,9,12,9,7,4])[k%8]; add(x,pluck(root*4*2**(semi/12),2.2,0.032),float(np.interp(x,t[::441],env[::441]))); x+=0.9; k+=1
out+=np.sin(2*np.pi*55*t)*0.015*env
# --- unique identity: the light curve is SONIFIED: pitch follows the star's brightness, so the dip is heard as a fall ---
H0=0.3; HE=EV["giant"]+2.6; tt=np.arange(int((HE-H0)*SR))/SR; bb=np.array([ev.hook_b(H0+u) for u in tt[::441]]); b_=np.interp(tt,tt[::441],bb)
f_=190+620*(b_-0.75); son=np.sin(2*np.pi*np.cumsum(f_)/SR)*np.clip(tt/1.0,0,1)*np.clip((len(tt)/SR-tt)/0.8,0,1)
add(H0,lp(son,3000)*0.05)
add(0.3,sweep(1.0,150,520,0.05)); add(EV["flicker"],rustle(1.6,0.05,1500,4500)); add(EV["dropped"]-0.1,boom(1.1,42,1.0,3.0)); add(EV["dropped"],sweep(1.4,700,110,0.06))
add(EV["pct"],gl(233,2.6,0.05,0.1)); add(EV["pct"],gl(247,2.6,0.04,0.1)); add(EV["days"],tick(1500,0.05)); add(EV["planet"],tick(1900,0.05)); add(EV["giant"],pluck(392,2.0,0.05))
# --- dip transitions (audio dims with the picture) ---
for s_ in SC[1:]:
    add(s_["s"]-0.5,sweep(0.5,900,140,0.05)); add(s_["s"]-0.02,boom(0.35,60,4,1.0)); add(s_["s"]+0.02,sweep(0.6,140,760,0.04))
# --- kepler ---
add(EV["kepler"],pluck(330,2.2,0.05)); 
for k in range(4): add(EV["four"]+k*0.22,tick(1300+k*150,0.04))
for u in np.arange(EV["four"],EV["stars150"]+0.8,0.045): add(u,tick(1800+(u*913)%1800,0.02,0.03))
add(EV["stars150"],gl(659.3,2.4,0.045,0.2)); add(EV["dips"],pluck(1046.5,2.0,0.04)); add(EV["passes"]-0.3,sweep(0.9,200,900,0.05))
add(EV["passes"],sweep(EV["jupiter"]-EV["passes"]+0.6,520,505,0.03)); add(EV["dims"],tick(700,0.05,0.1)); add(EV["jupiter"],gl(523.3,2.4,0.045,0.2)); add(EV["onepct"],tick(1200,0.05))
# --- volunteers ---
for i_ in range(30): add(S("volunteers")["s"]+i_*0.05,tick(1200+(i_*137)%1000,0.025,0.04))
add(EV["ph"],pluck(587.3,2.2,0.05)); add(EV["flagged"],tick(1760,0.06,0.12)); add(EV["flagged"]+0.15,tick(1318,0.06,0.12)); add(EV["flagged"]+0.3,boom(0.4,80,3,1.0))
# --- the star ---
add(EV["kic"],gl(880,2.4,0.04,0.2)); add(EV["tabby"],pluck(440,2.2,0.05)); add(EV["boy"],pluck(554,2.0,0.04)); add(EV["wtf"],tick(700,0.06,0.12)); add(EV["wtf"]+0.14,tick(520,0.06,0.12)); add(EV["flux"],pluck(392,2.2,0.05))
add(EV["ly"]-0.1,sweep(2.0,200,900,0.04)); add(EV["cyg"],tick(1600,0.04)); add(EV["nopat"],gl(233,2.6,0.04,0.2))
for u in np.arange(EV["nopat"],S("star")["e"]-1.0,0.11): add(u,tick(700+(u*577)%900,0.018,0.03))
# --- theories & aliens ---
for e_,f in ((EV["comets"],523.3),(EV["torn"],466.2),(EV["dust"],392)): add(e_,pluck(f,2.0,0.05))
add(EV["wright"],pluck(293.7,2.2,0.05)); add(EV["alien"]-0.3,theremin(330,3.6,0.05)); add(EV["structure"],gl(196,3.0,0.045,0.3)); add(EV["collect"],sweep(1.6,120,480,0.04))
for j_ in range(3):
    for u in range(10): add(EV["headlines"]+j_*0.5+u*0.035,lp(bp(rng.normal(0,1,int(0.03*SR)),1200,4000),4000)*np.exp(-np.arange(int(0.03*SR))/SR*80)*0.07)
add(EV["longshot"],boom(0.6,70,2.5,1.4)); add(EV["longshot"],tick(320,0.08,0.1)); add(EV["testing"],gl(392,2.2,0.045,0.2)); add(EV["testing"]+0.05,gl(494,2.2,0.035,0.2))
# --- crowdfunding: the counter ticks up, the bar fills, then a bright chime ---
add(EV["unusual"],pluck(392,2.2,0.05)); add(EV["y2016"],pluck(494,2.2,0.04)); add(EV["help"],gl(587.3,2.6,0.045,0.2))
d0=EV["people"]; d1=EV["dollars"]+1.3
for u in np.arange(d0,d1,0.03): add(u,tick(900+700*(u-d0)/(d1-d0),0.02,0.03))
add(d1,gl(1046.5,2.8,0.05,0.02)); add(d1,gl(1318.5,2.4,0.035,0.02)); add(EV["telescope"],pluck(659.3,2.0,0.045))
for k in range(8): add(EV["telescope"]+0.3+k*0.28,tick(1000+k*140,0.03,0.05))
# --- the test: three tones per panel, blue leads ---
for e_,pan in ((EV["solid"],0),(EV["grains"],1)):
    add(e_,pluck(294 if pan==0 else 330,2.0,0.045))
    for j_,f in enumerate((330,440,660)): add(e_+0.4+j_*0.15,gl(f*(1 if pan==0 else [1,1,1.0][j_]),1.6,0.03+0.02*(1 if pan==1 and j_==2 else 0),0.05))
add(EV["blue"],gl(660,2.4,0.05,0.1))
# --- result ---
add(EV["y2017"],pluck(392,2.2,0.05)); add(EV["dipped"],sweep(1.2,600,140,0.05)); add(EV["deeper"],gl(523.3,2.6,0.045,0.2)); add(EV["deeper"]+0.05,gl(784,2.6,0.035,0.2))
add(EV["itdust"],boom(0.9,50,1.4,3.0)); 
for f in (146.83,184.99,220,293.7): add(EV["itdust"],gl(f,3.4,0.04,0.2))
add(EV["notsolid"],tick(500,0.06,0.1)); add(EV["notalien"],tick(400,0.06,0.12))
# --- open questions ---
add(EV["notover"],gl(196,3.0,0.05,0.3)); add(EV["where"],rustle(EV["photos"]-EV["where"],0.05,300,2200)); add(EV["shattered"],tick(300,0.07,0.09)); add(EV["shattered"]+0.1,tick(260,0.06,0.09))
for u in range(14): add(EV["storm"]+u*0.06,tick(1000+(u*211)%900,0.03,0.04))
for u in np.arange(EV["photos"],EV["nobody"],0.25): add(u,lp(bp(rng.normal(0,1,int(0.03*SR)),400,2500),2500)*np.exp(-np.arange(int(0.03*SR))/SR*90)*0.09)
add(EV["fading"],sweep(3.0,700,180,0.035)); add(EV["nobody"],gl(146.83,3.4,0.05,0.2))
# --- end ---
add(EV["message"],gl(293.7,3.0,0.05,0.3)); add(EV["wasnt"],pluck(392,2.4,0.05))
for f in (146.83,184.99,220,293.7): add(EV["wasnt"],gl(f,3.4,0.04,0.2))
tf=Lx("next strange star")[1]+0.6; tt=np.arange(int(3.5*SR))/SR
add(tf,(np.sin(2*np.pi*293.7*tt)+0.6*np.sin(2*np.pi*440*tt)+0.4*np.sin(2*np.pi*587.3*tt))*np.exp(-tt*1.0)*0.045*np.clip(tt/0.05,0,1))
# --- clean master: gentle lowpass on sfx/music, smooth reverb, voice ducking, peak control ---
out=lp(out,8000)
ir_t=np.arange(int(2.2*SR))/SR; ir=rng.normal(0,1,len(ir_t))*np.exp(-ir_t*2.8); ir=lp(ir,4000); ir/=np.abs(ir).sum()**0.5*8
wet=fftconvolve(out,ir)[:N]; bus=out*0.85+wet*0.45
vo=np.zeros(N)
for ln in LINES:
    sr,d=wf.read(f"vo/vo_{ln['i']:02d}.wav"); d=d.astype(np.float64)/32768; i=int(ln["s"]*SR); d=d[:N-i]; vo[i:i+len(d)]+=d
vo=vo-0.6*hp(vo,5500); vo=vo+fftconvolve(vo,ir*0.5)[:N]*0.04
venv=np.convolve(np.abs(vo),np.ones(8820)/8820,mode="same"); venv=np.clip(venv/0.04,0,1)
vo=np.tanh(vo*1.15)/np.tanh(1.15); vo=vo-0.55*hp(vo,5200); bus=bus*(1-0.7*venv); mix=vo*1.15+bus*0.5
st=np.stack([mix+0.02*np.roll(wet,300),mix+0.02*np.roll(wet,-300)],1); st/=np.abs(st).max()*1.05
wf.write("mix_raw.wav",SR,(st*32767).astype(np.int16))
subprocess.run(["ffmpeg","-y","-v","error","-i","mix_raw.wav","-af","loudnorm=I=-14:TP=-1.0:LRA=11","-ar","48000","mix.wav"],check=True)
# --- QA: detect crackle / harsh transients ---
sr,x=wf.read("mix.wav"); x=x.astype(np.float64).mean(1)/32768
hf=sosfilt(butter(4,7000/(sr/2),'high',output='sos'),x)
worst=[]
for s0 in range(0,int(len(x)/sr)):
    seg=hf[s0*sr:(s0+1)*sr]; full=x[s0*sr:(s0+1)*sr]
    r=np.sqrt((seg**2).mean())/(np.sqrt((full**2).mean())+1e-9); cr=np.abs(seg).max()/(np.sqrt((seg**2).mean())+1e-9)
    worst.append((r,cr,s0))
print("max HF ratio",round(max(w[0] for w in worst),3),"at",max(worst)[2],"s | max HF crest",round(max(w[1] for w in worst),1))
print("peak dBFS",round(20*np.log10(np.abs(x).max()),2))
