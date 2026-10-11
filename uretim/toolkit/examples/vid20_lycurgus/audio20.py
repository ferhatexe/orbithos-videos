import numpy as np, math, subprocess, sys
sys.path.insert(0,"/home/claude/vid20")
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
# --- music: glass-harmonica pads + sparse plucks; minor -> major when "modern" begins ---
def gl(f,dur=3.2,amp=0.05,att=0.5):
    tt=np.arange(int(dur*SR))/SR
    s=np.sin(2*np.pi*f*tt)+0.35*np.sin(2*np.pi*f*2.003*tt)+0.12*np.sin(2*np.pi*f*3.01*tt)+0.05*np.sin(2*np.pi*f*1.002*tt*(1+0.002*np.sin(2*np.pi*5*tt)))
    e=np.clip(tt/att,0,1)*np.exp(-tt*0.55)*np.clip((dur-tt)/0.6,0,1)
    return lp(s*e*amp,7000)
def pluck(f,dur=2.2,amp=0.05):
    tt=np.arange(int(dur*SR))/SR; s=sum(a_*np.sin(2*np.pi*f*(k+1)*tt)*np.exp(-tt*(2.0+k*1.6)) for k,a_ in enumerate([1,.5,.25,.12]))
    return lp(s*amp*np.clip(tt/0.012,0,1),6000)
def tick(f=2400,amp=0.05,dur=0.05):
    tt=np.arange(int(dur*SR))/SR; return lp(np.sin(2*np.pi*f*tt)*np.exp(-tt*70)*amp*np.clip(tt/0.003,0,1),5000)
def sweep(dur,f0,f1,amp=0.05):
    tt=np.arange(int(dur*SR))/SR; f=f0+(f1-f0)*(tt/dur)**2
    return lp(np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*tt/dur)**2*amp,6000)
def rustle(dur,amp=0.08,lo=400,hi=3000):
    tt=np.arange(int(dur*SR))/SR; return lp(bp(rng.normal(0,1,len(tt)),lo,hi),hi)*np.sin(np.pi*tt/dur)**2*amp
env=np.interp(t,[0,0.3,1.5,S("myth")["s"],S("secret")["s"],S("light")["s"],S("debate")["s"],S("modern")["s"],S("end")["s"],TOTAL-2,TOTAL],[0,0,0.55,0.6,0.55,0.75,0.5,0.8,0.85,0.7,0])
root=146.83; tmod=S("modern")["s"]
for ci in range(int(TOTAL/3.5)+1):
    s0=ci*3.5; ch=([0,3,7],[-2,2,5],[-4,0,3],[-5,-1,2]) if s0<tmod else ([0,4,7],[-3,0,4],[5,9,12],[7,11,14])
    for sm_ in ch[ci%4]: add(s0,gl(root*2**(sm_/12),4.4,0.022,1.2),float(np.interp(s0,t[::441],env[::441])))
pen=[0,3,7,10,12,10,7,3] if True else []
x=1.6; k=0
while x<TOTAL-3:
    semi=([0,3,7,10,12,10,7,3] if x<tmod else [0,4,7,9,12,9,7,4])[k%8]
    add(x,pluck(root*2*2**(semi/12),2.2,0.04),float(np.interp(x,t[::441],env[::441]))); x+=0.75; k+=1
out+=np.sin(2*np.pi*73.4*t)*0.02*env
# --- unique intro: the museum lamp switches on, hums, then the cup turns blood red ---
add(0.3,lp(rng.normal(0,1,int(0.05*SR)),900)*np.exp(-np.arange(int(0.05*SR))/SR*60)*0.5); add(0.3,tick(1800,0.04))
add(0.35,sweep(1.2,180,420,0.05))
add(EV["green"],gl(783.99,2.5,0.05,0.3))
add(EV["light"]-0.1,rustle(2.4,0.09,200,1800)); add(EV["through"],sweep(1.9,90,240,0.08))
add(EV["turns"]-0.1,sweep(0.9,300,1400,0.06))
add(EV["blood"]-0.05,boom(1.3,38,1.0,3.5)); 
for f in (146.83,174.6,220,293.7): add(EV["blood"],gl(f,3.2,0.05,0.15))
add(EV["sixteen"],pluck(392,2.2,0.05)); add(EV["nobody"],gl(196,2.6,0.04,0.3))
# --- light-sweep transitions (one per scene boundary, synced to the wipe) ---
for s_ in SC[1:]:
    add(s_["s"]-0.44,sweep(0.88,300,3000,0.05)); add(s_["s"]-0.05,gl(1568,1.6,0.045,0.006)); add(s_["s"]+0.02,boom(0.22,70,5,0.8))
# --- cup / myth / cage ---
for e_,f in ((EV["name"],392),(EV["rome"],440),(EV["museum"],523.3)): add(e_,pluck(f,2.2,0.05))
add(S("cup")["s"]+2.5,tick(1500,0.04))
for e_,f in ((EV["myth"],293.7),(EV["lyc"],220),(EV["dio"],329.6)): add(e_,pluck(f,2.4,0.06))
add(EV["amb"],gl(659.3,2.2,0.045,0.2)); add(EV["vine"],rustle(EV["traps"]-EV["vine"]+0.6,0.10,300,2600))
for k in range(4): add(EV["vine"]+0.4+k*0.55,lp(np.sin(2*np.pi*(120+30*np.sin(np.arange(int(0.5*SR))/SR*9))*np.arange(int(0.5*SR))/SR),900)*np.sin(np.pi*np.arange(int(0.5*SR))/SR/0.5)*0.05)
add(EV["traps"],boom(0.8,48,1.6,2.4)); 
for f in (155.6,164.8): add(EV["traps"],gl(f,2.6,0.04,0.05))
add(EV["deep"]-0.3,rustle(1.6,0.08,150,1400)); add(EV["floatw"],gl(587.3,2.4,0.04,0.3))
for k in range(7): add(EV["bridges"]+0.05+k*0.07,tick(2100+k*90,0.06))
add(EV["bridges"]+0.6,pluck(659.3,2.0,0.05))
# --- secret / particles ---
add(EV["secret"],gl(196,3.0,0.05,0.3)); add(EV["inside"],gl(880,2.4,0.04,0.2)); add(EV["y1990"],boom(0.5,70,3,1.4))
tt_=np.arange(int((S("secret")["e"]-EV["em"]+0.5)*SR))/SR; add(EV["em"]-0.2,np.sin(2*np.pi*120*tt_)*np.clip(tt_/0.8,0,1)*0.02+lp(rng.normal(0,1,len(tt_)),500)*0.02)
add(EV["em"],sweep(1.0,400,1100,0.05))
for k in range(9): add(EV["em"]+1.0+k*1.1,tick(1900,0.03))
for k in range(24): add(EV["gold"]+k*0.09,tick(1800+(k*173)%1600,0.03))
add(EV["nm"],pluck(587.3,2.0,0.05)); add(EV["nm"]+0.5,pluck(740,2.0,0.05))
for k in range(14): add(EV["thousand"]-0.2+k*0.06,tick(700+k*110,0.05))
add(EV["hair"],boom(0.4,85,4,1.0)); add(EV["hair"]+0.05,gl(220,2.4,0.04,0.2))
# --- light physics ---
def photon_times(t0,t1,mode):
    outl=[]; T=2.4
    for j in range(8):
        k=0
        while True:
            tt2=t0+((0.4-j/8.0)%1.0)*T+k*T; k+=1
            if tt2>t1: break
            if tt2>=t0: outl.append((tt2,j))
    return outl
for tt2,j in photon_times(S("light")["s"],EV["back"]-0.2,"A"): add(tt2,(pluck(1318.5,0.7,0.025) if j%2==0 else pluck(523.3,0.7,0.025)))
for tt2,j in photon_times(EV["back"],EV["nano"]-0.4,"B"):
    if j%2==0: add(tt2,rustle(0.25,0.035,900,3000))
    else: add(tt2+0.36,pluck(523.3,0.8,0.03))
add(EV["nano"],gl(587.3,3.0,0.05,0.2)); add(EV["nano"]-0.1,sweep(0.8,300,1500,0.05)); add(EV["word"],gl(1174.7,2.6,0.04,0.3))
# --- debate ---
add(EV["q"],gl(174.6,3.0,0.05,0.3))
tg=EV["precise"]-0.4; g_=0.0
for k in range(44): add(tg+g_,tick(1500+k*20,0.02)); g_+=max(0.02,0.11-k*0.002)
add(EV["less"],gl(1568,2.6,0.05,0.05)); add(EV["less"]+0.05,gl(2093,2.2,0.035,0.05))
for k in range(9): add(EV["luck"]+k*0.075,lp(bp(rng.normal(0,1,int(0.05*SR)),700,2800),2800)*np.exp(-np.arange(int(0.05*SR))/SR*50)*0.12*(1-k/11))
add(EV["luck"]+0.7,tick(900,0.06,0.09)); add(EV["recipe"]-0.05,rustle(0.7,0.09,600,3000)); add(EV["recipe"]+0.2,pluck(392,2.2,0.05))
add(EV["noone"],boom(0.5,52,2.0,2.0)); add(EV["noone"],gl(146.83,3.2,0.05,0.2))
# --- cracked ---
tk=EV["cracked"]; ck=np.zeros(int(1.4*SR))
for i_ in range(9):
    o=int(i_*0.09*SR); L_=int(0.05*SR); ck[o:o+L_]+=lp(rng.normal(0,1,L_),2600)*np.exp(-np.arange(L_)/SR*90)*np.clip(np.arange(L_)/SR/0.004,0,1)*(1-i_/12)
add(tk,ck*0.32); add(tk,boom(0.45,70,3,1.2)); add(tk+0.05,gl(1975,1.8,0.03,0.005))
add(EV["rim"],gl(1046.5,2.6,0.04,0.2))
# --- modern ---
add(EV["borrow"]-0.1,gl(587.3,2.6,0.045,0.2)); add(EV["borrow"]+0.1,gl(740,2.6,0.035,0.2)); add(EV["illinois"],pluck(440,2.2,0.05))
add(EV["stamp"]-0.05,rustle(0.5,0.08,800,3500)); 
for k in range(117): add(EV["billion"]-0.2+k*0.0078,tick(1200+(k*97)%1400,0.012,0.03))
add(EV["sprayed"],rustle(1.0,0.05,1500,4500)); add(EV["mini"],pluck(659.3,2.2,0.05))
add(EV["changes"],sweep(EV["hundred"]-EV["changes"],260,720,0.025))
for k in range(3):
    e_=EV["liquid"]+k*1.2; tt_=np.arange(int(0.18*SR))/SR; add(e_+0.7,np.sin(2*np.pi*np.cumsum(1300-800*tt_/0.18)/SR)*np.exp(-tt_*18)*0.06*np.clip(tt_/0.006,0,1)); add(e_+0.85,tick(880,0.04,0.09))
add(EV["hundred"],boom(0.6,60,2.0,2.0)); add(EV["hundred"],gl(880,2.6,0.05,0.1))
add(EV["diseases"],gl(1108,3.0,0.04,0.3)); add(EV["diseases"]+0.4,gl(880,3.0,0.04,0.3))
# --- end ---
add(EV["sixteenc"],pluck(293.7,2.4,0.05)); add(EV["unknown"],pluck(370,2.4,0.05))
add(EV["trapped"]-0.8,sweep(0.8,300,1800,0.06)); add(EV["trapped"],boom(1.0,45,1.2,3.0))
for f in (146.83,184.99,220,293.7): add(EV["trapped"],gl(f,3.6,0.05,0.2))
tf=Lx("And we are only")[1]+0.6; tt=np.arange(int(3.5*SR))/SR
add(tf,(np.sin(2*np.pi*293.7*tt)+0.6*np.sin(2*np.pi*440*tt)+0.4*np.sin(2*np.pi*587.3*tt))*np.exp(-tt*1.0)*0.045)
# --- clean master: gentle lowpass on sfx/music, smooth reverb, voice ducking, peak control ---
out=lp(out,8000)
ir_t=np.arange(int(2.2*SR))/SR; ir=rng.normal(0,1,len(ir_t))*np.exp(-ir_t*2.8); ir=lp(ir,4000); ir/=np.abs(ir).sum()**0.5*8
wet=fftconvolve(out,ir)[:N]; bus=out*0.85+wet*0.45
vo=np.zeros(N)
for ln in LINES:
    sr,d=wf.read(f"vo/vo_{ln['i']:02d}.wav"); d=d.astype(np.float64)/32768; i=int(ln["s"]*SR); d=d[:N-i]; vo[i:i+len(d)]+=d
vo=vo-0.6*hp(vo,5500); vo=vo+fftconvolve(vo,ir*0.5)[:N]*0.1
venv=np.convolve(np.abs(vo),np.ones(8820)/8820,mode="same"); venv=np.clip(venv/0.04,0,1)
bus=bus*(1-0.5*venv); mix=vo*1.05+bus*0.8
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
