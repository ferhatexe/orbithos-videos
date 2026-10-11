"""Orbithos mastering chain v2.
master(vo, bus, SR, out) -> writes 48 kHz stereo wav at -14 LUFS / <= -1 dBTP and prints a QA report.
vo  : mono narration (float, unprocessed except trimming)
bus : mono or (N,2) music+sfx bus
"""
import numpy as np, subprocess
import pyloudnorm as pyln
from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, PeakFilter, HighShelfFilter, LowShelfFilter, Compressor, Reverb, Limiter, Gain
from scipy.signal import butter, sosfilt, sosfiltfilt, resample_poly
import scipy.io.wavfile as wf

def _f32(x): return np.ascontiguousarray(np.asarray(x,np.float32))
def _env(x,SR,att,rel):
    """one-pole envelope follower on |x| (attack/release in seconds)"""
    a=np.exp(-1/(att*SR)); r=np.exp(-1/(rel*SR)); y=np.abs(x).astype(np.float64)
    # vectorised approx: smooth with release then attack via two IIR passes
    from scipy.signal import lfilter
    e=lfilter([1-r],[1,-r],y)          # release smoothing
    e=np.maximum(e,lfilter([1-a],[1,-a],y))
    return e
def deess(v,SR,lo=5000,hi=9500,thr=0.035,ratio=4.0):
    sos=butter(4,[lo/(SR/2),min(hi,SR/2-100)/(SR/2)],'band',output='sos'); s=sosfiltfilt(sos,v)
    e=_env(s,SR,0.002,0.06); over=np.maximum(e/thr,1.0); g=over**(1/ratio-1)   # gain for sibilant band only
    return v-s*(1-g)
def voice_chain(vo,SR):
    pb=Pedalboard([HighpassFilter(80),LowShelfFilter(cutoff_frequency_hz=140,gain_db=1.0),
                   PeakFilter(cutoff_frequency_hz=300,gain_db=-2.5,q=1.0),
                   PeakFilter(cutoff_frequency_hz=3200,gain_db=2.0,q=0.8),
                   HighShelfFilter(cutoff_frequency_hz=9500,gain_db=-2.0),
                   Compressor(threshold_db=-21,ratio=2.6,attack_ms=6,release_ms=110),
                   Gain(3.0)])
    v=pb(_f32(vo)[None,:],SR)[0].astype(np.float64)
    v=deess(v,SR)
    rv=Pedalboard([Reverb(room_size=0.14,damping=0.75,wet_level=1.0,dry_level=0.0,width=0.5)])(_f32(v)[None,:],SR)[0]
    rv=sosfilt(butter(2,[250/(SR/2),5000/(SR/2)],'band',output='sos'),rv)
    return v+0.055*rv
def bus_chain(bus,SR):
    b=np.atleast_2d(bus.T if bus.ndim==2 else bus[None,:]).astype(np.float32)
    pb=Pedalboard([HighpassFilter(32),PeakFilter(cutoff_frequency_hz=2800,gain_db=-4.0,q=0.7),LowpassFilter(9000)])
    return pb(b,SR).astype(np.float64)
def limiter(x,SR,thr_db,la=0.005,rel=0.12):
    """lookahead brickwall limiter on (2,N) array, unity gain below threshold (no makeup)"""
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    from scipy.signal import lfilter
    thr=10**(thr_db/20); n=int(la*SR)
    pk=maximum_filter1d(np.abs(x).max(0),size=2*n+1)
    gr=1-np.minimum(1.0,thr/(pk+1e-12))
    r=np.exp(-1/(rel*SR)); gr=np.maximum(gr,lfilter([1-r],[1,-r],gr))
    gr=uniform_filter1d(gr,size=n+1); gr=maximum_filter1d(gr,size=n+1)
    return x*(1-gr)[None,:]
def hf_clamp(x,SR,f=6500,ceil_db=-19.0):
    """tame HF transient spikes (TTS clicks / crackle): lookahead-limit the >f band to ceil"""
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    from scipy.signal import lfilter
    sos=butter(4,f/(SR/2),'high',output='sos'); c=10**(ceil_db/20); y=x.copy(); n=int(0.0015*SR)
    for ch in range(x.shape[0]):
        h=sosfiltfilt(sos,x[ch]); hc=sosfilt(sos,x[ch]); pk=maximum_filter1d(np.maximum(np.abs(h),np.abs(hc)),size=2*n+1)
        gr=1-np.minimum(1.0,c/(pk+1e-12)); r=np.exp(-1/(0.03*SR)); gr=np.maximum(gr,lfilter([1-r],[1,-r],gr))
        gr=maximum_filter1d(uniform_filter1d(gr,size=n),size=n); y[ch]=x[ch]-h*gr
    return y
def true_peak(x,SR):
    up=resample_poly(x,4,1,axis=0); return 20*np.log10(np.abs(up).max()+1e-12)
def master(vo,bus,SR,out="mix.wav",duck_db=9.0,bus_gain=0.45,lufs=-14.0,tp=-1.0):
    N=len(vo); v=voice_chain(vo,SR)
    b=bus_chain(bus,SR)
    if b.shape[0]==1: b=np.vstack([b[0],b[0]])
    # smooth sidechain ducking (fast-ish attack, slow release so music breathes between lines)
    venv=_env(v,SR,0.04,0.45); venv=np.clip(venv/0.05,0,1)**0.8
    g=10**(-duck_db*venv/20)
    b=b*g[None,:]*bus_gain
    # gentle Haas width on bus
    d=int(0.006*SR); b[1]=np.concatenate([np.zeros(d),b[1][:-d]])*0.9+b[1]*0.1
    mix=np.vstack([v,v])+b
    glue=Pedalboard([Compressor(threshold_db=-16,ratio=1.6,attack_ms=25,release_ms=220)])
    mix=glue(_f32(mix),SR).astype(np.float64)
    meter=pyln.Meter(SR)
    for it in range(4):
        L=meter.integrated_loudness(mix.T); mix=mix*10**((lufs-L)/20)
        mix=hf_clamp(mix,SR); mix=limiter(mix,SR,tp-0.7)
        if true_peak(mix.T,SR)<=tp and abs(meter.integrated_loudness(mix.T)-lufs)<0.3: break
    mix=hf_clamp(mix,SR)
    pk=true_peak(mix.T,SR)
    if pk>tp: mix*=10**((tp-0.05-pk)/20)
    y=resample_poly(mix.T,160,147,axis=0) if SR==44100 else mix.T
    wf.write(out,48000 if SR==44100 else SR,(np.clip(y,-1,1)*32767).astype(np.int16))
    # ---- QA ----
    L=meter.integrated_loudness(mix.T); pk=true_peak(mix.T,SR)
    sp=venv>0.5; vr=20*np.log10(np.sqrt((v[sp]**2).mean())/(np.sqrt((b[:,sp]**2).mean())+1e-9)+1e-9)
    hf=sosfilt(butter(4,7000/(SR/2),'high',output='sos'),mix.mean(0)); bad=[]
    for s0 in range(int(N/SR)):
        seg=hf[s0*SR:(s0+1)*SR]; cr=np.abs(seg).max()/(np.sqrt((seg**2).mean())+1e-9); p=20*np.log10(np.abs(seg).max()+1e-9)
        if cr>25 and p>-15: bad.append(s0)
    from scipy.ndimage import uniform_filter1d
    bm=np.sqrt(np.maximum(uniform_filter1d((b**2).mean(0),size=int(0.4*SR)),0)); vavg=np.sqrt((v[sp]**2).mean())
    i=int(bm.argmax()); peakrel=20*np.log10(bm[i]/vavg+1e-9)
    print(f"loudest SFX/music moment: {peakrel:+.1f} dB vs average speech (at {i/SR:.1f}s)")
    print(f"LUFS {L:.2f} | true peak {pk:.2f} dBTP | voice-over-bus during speech {vr:.1f} dB | harsh seconds {bad}")
    return mix
