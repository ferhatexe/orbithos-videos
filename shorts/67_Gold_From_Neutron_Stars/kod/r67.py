import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid67")
for p in ["/home/claude/vid67","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial import cKDTree
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= pointillism: the frame is painted, then re-laid as pure dots of colour =================
_g=np.random.default_rng(67)
_cache="dots_cache.npz"
if os.path.exists(_cache):
    z=np.load(_cache); DP=z["DP"]; LF=z["LF"]; IN=z["IN"]; RAD=z["RAD"]
else:
    pts=[]
    for j in range(int(h/4.2)+2):
        for i in range(int(w/4.2)+2): pts.append((i*4.2+(2.1 if j%2 else 0)+_g.uniform(-1.4,1.4),j*4.2+_g.uniform(-1.4,1.4)))
    DP=np.array(pts,np.float32); RAD=_g.uniform(1.6,2.5,len(DP)).astype(np.float32)
    tr=cKDTree(DP); YF,XF=np.mgrid[0:H,0:W].astype(np.float32); q=np.stack([(XF.ravel()+0.5)/2,(YF.ravel()+0.5)/2],-1)
    dd,ii=tr.query(q); LF=ii.reshape(H,W).astype(np.int32); IN=np.clip((RAD[ii]-dd)/0.45,0,1).reshape(H,W).astype(np.float16)
    np.savez(_cache,DP=DP,LF=LF,IN=IN,RAD=RAD)
K=len(DP); LFr=LF.ravel(); INf=IN.astype(np.float32)[...,None]
HUE=_g.normal(0,1,(K,3)).astype(np.float32)
# Seurat-like chromatic jitter: each dot leans toward a neighbouring pure hue
JIT=(HUE*np.array((0.11,0.10,0.12),np.float32))
GROUND=np.array((0.93,0.90,0.82),np.float32)
def sample(img,px,py):
    xi=np.clip(px.astype(np.int32),0,w-1); yi=np.clip(py.astype(np.int32),0,h-1); return img[yi,xi]
def pointil(img,px=None,py=None):
    if px is None: px,py=DP[:,0],DP[:,1]
    c=sample(img,px,py); lum=c.mean(1,keepdims=True)
    c=np.clip(c+JIT*(0.4+lum)+(c-lum)*0.25,0,1)                 # boost saturation a touch
    full=c[LFr].reshape(H,W,3)
    bgr=cv2.resize(img,(W,H),interpolation=cv2.INTER_LINEAR)
    ground=GROUND*0.12+bgr*0.42
    return full*INf+ground*(1-INf)
# ---- base painting helpers (smooth colour image at 540x960) ----
def fill(buf,m,col,a=1.0):
    A=(m.f() if isinstance(m,M) else m)*a; buf+=(np.array(col,np.float32)-buf)*A[...,None]
def glow(buf,x,y,r,col,a=1.0):
    d2=((xx-x)**2+(yy-y)**2)/(r*r); buf+=(np.exp(-d2)*a)[...,None]*np.array(col,np.float32)
def sky(top=(0.04,0.06,0.20),bot=(0.12,0.10,0.30)):
    k=np.clip(yy/h,0,1)[...,None]; b=np.array(top,np.float32)*(1-k)+np.array(bot,np.float32)*k
    return b.astype(np.float32)+0*xx[...,None]
STARS=[(_g.uniform(0,w),_g.uniform(0,670),_g.uniform(0.6,1.6)) for _ in range(90)]
def stars(b,a=1.0):
    for x,y,r in STARS: glow(b,x,y,r*2.2,(1.0,0.95,0.85),0.8*a)
def ring(b,cx,cy,s,t,a=1.0):
    outer=M().ell(cx,cy,110*s,46*s); inner=M().ell(cx,cy+4*s,82*s,28*s)
    R=np.clip(outer.f()-inner.f(),0,1)
    sh=np.clip(0.55+0.45*np.cos((xx-cx)/(110*s)*2.2+t*0.6),0,1)
    col=np.array((1.0,0.80,0.25),np.float32)[None,None,:]*(0.6+0.6*sh[...,None])
    b+=(col-b)*(R*a)[...,None]; glow(b,cx-40*s,cy-30*s,26*s,(1.0,0.95,0.7),0.8*a)
def nstar(b,x,y,r,a=1.0):
    glow(b,x,y,r*4,(0.45,0.65,1.0),0.6*a); glow(b,x,y,r*1.4,(0.95,0.98,1.0),1.2*a)
def label(d,s,x,y,fs=60,a=1.0,col=(255,250,235),sc=1.0):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f("CrimsonPro-Bold.ttf",n)
    d.text((x,y),s,font=f,fill=col+(int(255*a),),anchor="mm",stroke_width=5,stroke_fill=(20,16,40,int(230*a)))
_IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(P.FD+n,s)
    return _IF[k]
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.3,0.28,0.25)
# ================= shots =================
def s_hook(t,end=False):
    b=sky(); stars(b)
    an=t*1.6; r=90-25*sm((t-EV["dead"]+0.5)/1.5) if not end else 90
    for k in (0,1): nstar(b,270+math.cos(an+k*math.pi)*r,230+math.sin(an+k*math.pi)*r*0.45,10)
    if not end and t>EV["smash"]-0.2: glow(b,270,230,90*sm((t-EV["smash"]+0.2)/0.6),(1.0,0.7,0.4),1.4)
    ring(b,270,500,1.2,t)
    def hd(d,t=t):
        if not end:
            label(d,"GOLD",540,300,96,ap(t,EV["gold0"]-0.2,EV["dead"]),sc=pop(t,EV["gold0"]-0.3))
            label(d,"forged by dead stars",540,300,66,ap(t,EV["dead"]-0.1,99),sc=pop(t,EV["dead"]-0.2))
        else: label(d,"remember",540,300,90,ap(t,EV["remember"]-0.2,99),sc=pop(t,EV["remember"]-0.3))
    return b,[hd]
LAYERS=[("H",(0.95,0.75,0.35)),("He",(0.95,0.55,0.30)),("C",(0.85,0.35,0.30)),("O",(0.60,0.30,0.55)),("Si",(0.35,0.35,0.70)),("Fe",(0.55,0.55,0.60))]
def s_onion(t):
    b=sky((0.08,0.04,0.10),(0.12,0.06,0.14)); stars(b,0.5)
    cx,cy=270,340
    for i,(nm,col) in enumerate(LAYERS):
        r=230-i*36; k=sm((t-EV["forge"]+0.3-i*0.12)/0.4); fill(b,M().circ(cx,cy,r),col,k)
    fe=fa(t,EV["iron"]-0.2,99,0.2,0.3); glow(b,cx,cy,40,(1,1,1),0.5*fe)
    def hd(d,t=t):
        for i,(nm,col) in enumerate(LAYERS):
            r=230-i*36; label(d,nm,(cx+r-18)*2 if i<5 else cx*2,cy*2,44 if i<5 else 60,ap(t,EV["forge"]+0.1+i*0.12,99))
        label(d,"up to iron",540,1180,74,ap(t,EV["iron"]-0.2,EV["beyond"]),sc=pop(t,EV["iron"]-0.3))
        label(d,"then fusion stops paying",540,1180,58,ap(t,EV["beyond"],99),sc=pop(t,EV["beyond"]-0.1),col=(255,200,140))
    return b,[hd]
def s_flood(t):
    b=sky((0.03,0.05,0.10),(0.06,0.08,0.16))
    cx,cy=270,340; n=int(12+30*sm((t-EV["flood"]+0.3)/2.0))
    g=np.random.default_rng(3)
    for i in range(n):
        a=g.uniform(0,2*math.pi); r=g.uniform(0,1)**0.5*52
        fill(b,M().circ(cx+math.cos(a)*r,cy+math.sin(a)*r,11),(0.9,0.35,0.30) if i%2 else (0.55,0.62,0.75))
    for i in range(26):
        a=i*2.4+t*0.7; ph=((t*1.6+i*0.13)%1); r=300*(1-ph)+60
        glow(b,cx+math.cos(a)*r,cy+math.sin(a)*r,9,(0.7,0.85,1.0),0.9*cl((t-EV["flood"]+0.5)/0.4))
    def hd(d,t=t):
        label(d,"a flood of neutrons",540,1180,68,ap(t,EV["flood"]-0.2,99),sc=pop(t,EV["flood"]-0.3))
        label(d,"faster than decay",540,1260,52,ap(t,EV["decay"]-0.3,99),col=(190,215,255))
    return b,[hd]
def s_pair(t):
    b=sky(); stars(b)
    an=t*2.2; r=110-40*sm((t-EV["collide"]+0.4)/1.4)
    for k in (0,1): nstar(b,270+math.cos(an+k*math.pi)*r,300+math.sin(an+k*math.pi)*r*0.5,14)
    ck=sm((t-EV["city"]+0.4)/0.6)
    if ck>0:
        for i in range(14):
            bx=40+i*34; hh=40+((i*37)%70)
            fill(b,M().rect(bx,600-hh,bx+26,600),(0.18,0.20,0.30),ck)
        fill(b,M().rect(30,600,510,610),(0.12,0.12,0.2),ck)
    def hd(d,t=t):
        label(d,"two neutron stars",540,180,70,ap(t,EV["nstars"]-0.3,EV["city"]-0.1),sc=pop(t,EV["nstars"]-0.4))
        label(d,"city-sized · heavier than the Sun",540,180,50,ap(t,EV["city"]-0.1,99),sc=pop(t,EV["city"]-0.2))
    return b,[hd]
def s_waves(t):
    b=sky((0.02,0.04,0.12),(0.05,0.08,0.20)); stars(b,0.6)
    ex,ey=360,470
    k=cl((t-EV["waves"]+0.6)/2.5)
    for i in range(7):
        r=(i*55+t*90)%420
        R=np.clip(1-np.abs(np.sqrt((xx-120)**2+(yy-220)**2)-r)/3.5,0,1); b+=(R*0.35*k)[...,None]*np.array((0.6,0.8,1.0),np.float32)
    fill(b,M().circ(ex,ey,90),(0.20,0.40,0.80)); fill(b,M().ell(ex-20,ey-20,50,36,20),(0.25,0.60,0.35)); glow(b,ex-30,ey-35,40,(1,1,1),0.25)
    fill(b,M().rect(ex-4,ey-110,ex+4,ey-60),(0.9,0.9,0.95)); fill(b,M().rect(ex-4,ey-64,ex+46,ey-56),(0.9,0.9,0.95))
    nstar(b,120,220,6,0.9)
    def hd(d,t=t):
        label(d,"2017",540,180,110,ap(t,EV["y2017"]-0.2,EV["detect"]),sc=pop(t,EV["y2017"]-0.3))
        label(d,"gravitational waves",540,180,64,ap(t,EV["detect"],EV["dist"]-0.1),sc=pop(t,EV["detect"]-0.1))
        label(d,"~130 million light-years",540,180,56,ap(t,EV["dist"]-0.1,99),sc=pop(t,EV["dist"]-0.2))
    return b,[hd]
def s_kilonova(t):
    b=sky((0.02,0.02,0.06),(0.04,0.03,0.08)); stars(b,0.5)
    k=sm((t-EV["debris"]+0.8)/1.6)
    glow(b,270,330,60+200*k,(1.0,0.35,0.15),0.9); glow(b,270,330,30+80*k,(1.0,0.75,0.4),1.0); glow(b,270,330,14,(1,1,1),1.2)
    def hd(d,t=t):
        label(d,"a kilonova",540,1180,90,ap(t,EV["kilonova"]-0.3,99),sc=pop(t,EV["kilonova"]-0.4),col=(255,190,140))
    return b,[hd]
SPEC=[(0.55,0.2,0.75),(0.25,0.35,0.95),(0.2,0.75,0.9),(0.3,0.85,0.35),(0.95,0.9,0.25),(0.98,0.55,0.15),(0.9,0.2,0.15)]
def s_spectrum(t):
    b=sky((0.03,0.03,0.07),(0.05,0.05,0.10))
    k=sm((t-EV["light"]+0.2)/0.8)
    for i in range(len(SPEC)-1):
        x0=40+i*(460/6); fill(b,M().rect(x0,200,x0+460/6+1,300).f()*1,SPEC[i],k)
    gk=sm((t-EV["fresh"]+0.3)/0.6)
    for x in (130,160,250,330,400): fill(b,M().rect(x,200,x+5,300),(0.02,0.02,0.04),gk)
    sk=sm((t-EV["five"]+0.4)/1.0)
    for i in range(5):
        if sk*5>i: ex=95+i*88; fill(b,M().circ(ex,470,34),(0.20,0.40,0.80)); fill(b,M().ell(ex-8,462,18,12,20),(0.25,0.60,0.35))
    def hd(d,t=t):
        label(d,"freshly made heavy elements",540,700,52,ap(t,EV["fresh"]-0.2,EV["est"]),sc=pop(t,EV["fresh"]-0.3))
        label(d,"~5 Earths of strontium",540,700,62,ap(t,EV["five"]-0.3,99),sc=pop(t,EV["five"]-0.4),col=(255,220,140))
        label(d,"Sr",620,630,60,ap(t,EV["sr"]-0.3,99))
    return b,[hd]
def s_metals(t):
    b=sky((0.05,0.04,0.10),(0.10,0.08,0.18)); stars(b,0.6)
    for i,(key,col,x) in enumerate((("gold2",(1.0,0.78,0.22),120),("plat",(0.85,0.86,0.90),270),("uran",(0.45,0.85,0.35),420))):
        k=sm((t-EV[key]+0.2)/0.5)
        if k>0: fill(b,M().circ(x,330,58*k+0.5),col); glow(b,x-18,312,18,(1,1,1),0.6*k)
    bk=sm((t-EV["born"]+0.5)/1.2)
    if bk>0: glow(b,270,540,60*bk,(1.0,0.85,0.4),1.2)
    def hd(d,t=t):
        for i,(key,s,x) in enumerate((("gold2","Au",120),("plat","Pt",270),("uran","U",420))): label(d,s,x*2,800,70,ap(t,EV[key]-0.1,99))
        label(d,"same violent birth",540,180,70,ap(t,EV["violent"]-0.3,EV["born"]),sc=pop(t,EV["violent"]-0.4))
        label(d,"before our Sun was born",540,180,62,ap(t,EV["born"]-0.2,99),sc=pop(t,EV["born"]-0.3))
    return b,[hd]
def s_end(t): return s_hook(t,end=True)
TR=0.40; TOTAL=B.TOTAL; LOOPD=0.70
SHOTS=[(0.0,s_hook),(S("forge")["s"],s_onion),(Lx("Heavier atoms")[0]-0.3,s_flood),(Lx("One place")[0]-0.3,s_pair),(S("crash")["s"],s_waves),
       (Lx("Telescopes")[0]-0.3,s_kilonova),(Lx("In its light")[0]-0.3,s_spectrum),(S("earth")["s"],s_metals),(Lx("So the next")[0]-0.3,s_end)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
_ANG=_g.uniform(0,2*math.pi,K).astype(np.float32); _MAG=_g.uniform(20,120,K).astype(np.float32)
def swirl(b1,b2,u):
    """every dot of paint lifts off, swirls, and lands where the next picture needs it"""
    k=math.sin(math.pi*u)
    a=_ANG+u*3.0; px=DP[:,0]+np.cos(a)*_MAG*k; py=DP[:,1]+np.sin(a)*_MAG*k
    src=b1 if u<0.5 else b2
    return pointil(src,px,py)
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None: base,hud=SHOTS[i][1](t); hk=1.0; img=pointil(np.clip(base,0,1))
    else:
        fa_,fb_,ta,tb,u=pair
        if u<0.5: base,hud=fa_(ta)
        else: base,hud=fb_(tb)
        img=swirl(np.clip(base,0,1),np.clip(base,0,1),u); hk=cl(abs(u-0.5)*2.4)
    band=np.zeros((H,W,1),np.float32); band[1352:]=1
    img=img*(1-band)+band*np.array((0.06,0.05,0.12),np.float32)
    pil=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    pil.alpha_composite(ov); pil.alpha_composite(o2); return pil.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
