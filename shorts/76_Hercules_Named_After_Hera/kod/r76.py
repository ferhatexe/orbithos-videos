import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid76"); sys.path.insert(0,"/home/claude/toolkit")
from pro import *
from PIL import Image, ImageDraw, ImageFont
T,LINES,SC,TOTAL=load("timeline.json")
CAP=Captions(LINES); WD=CAP.W
def wt(li,sub,o=0.0): return word_t(WD,li,sub,o)
def Ls(i): return LINES[i]["s"]
def sm_np(x): x=np.clip(x,0,1); return x*x*(3-2*x)
# ================= Hercules / Hera: marble-and-gold cinematic reliefs, Olympus clouds + god-rays, peacock-eye iris transitions =================
GOLD=np.array([1.0,0.72,0.28],np.float32); GOLDL=np.array([1.0,0.88,0.55],np.float32)
SERIF="/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
# ---------- static textures (cached) ----------
MH,MW=1500,900
def _marble():
    Y,X=np.mgrid[0:MH,0:MW].astype(np.float32)
    n1=fbm((MH,MW),761,6,3); n2=fbm((MH,MW),762,6,4); n3=fbm((MH,MW),763,4,2)
    v1=np.abs(np.sin((X*0.55+Y*0.85)/MW*5.0+n1*2.4+n2*0.6)); vein1=np.exp(-v1/0.05)
    v2=np.abs(np.sin((X*-0.75+Y*0.45)/MW*8.0+n2*2.8)); vein2=np.exp(-v2/0.025)*np.clip(n3*0.6+0.5,0,1)
    v3=np.abs(np.sin((X*0.25-Y*0.95)/MW*3.0+n1*3.6+n3)); gv=np.exp(-v3/0.012)*np.clip(n2*0.8-0.1,0,1)
    cloud=fbm((MH,MW),764,5,6)
    return np.stack([vein1,vein2,gv,cloud]).astype(np.float16)
CACHE="tex76.npz"
if os.path.exists(CACHE): _z=np.load(CACHE); VEIN=_z["v"].astype(np.float32); CLD=_z["c"]; RAYP=_z["r"]
else:
    VEIN=_marble().astype(np.float32)
    c=fbm((h,w*2),770,6,3,aspect=2); c2=fbm((h,w*2),771,6,5,aspect=2); CLD=np.stack([c,c2]).astype(np.float32)
    g=np.random.default_rng(772); r=np.zeros(2048,np.float32)
    for k in (8,17,33,61,120): vals=g.random(k); r+=np.interp(np.arange(2048),np.linspace(0,2048,k+1),np.r_[vals,vals[0]])*(1.0/(1+k/40))
    r[-1]=r[0]; RAYP=r
    np.savez(CACHE,v=VEIN.astype(np.float16),c=CLD,r=RAYP)
RAYP=(RAYP-RAYP.min())/(RAYP.max()-RAYP.min()+1e-6)
def marble_rgb(kind="white"):
    v1,v2,gv,cl=VEIN
    if kind=="white":
        base=np.array([0.93,0.91,0.87],np.float32)*(0.95+0.035*cl)[...,None]
        col=base*(1-0.30*v1[...,None])*(1-0.18*v2[...,None])
        col=col*(1-gv[...,None])+np.array([1.0,0.74,0.30],np.float32)*1.15*gv[...,None]
    else:  # dark "nero" marble with gold veins
        base=np.array([0.075,0.07,0.085],np.float32)*(0.9+0.12*cl)[...,None]
        col=base+np.array([0.30,0.29,0.31],np.float32)*(v1*0.45+v2*0.35)[...,None]
        col=col*(1-gv[...,None])+np.array([1.0,0.70,0.25],np.float32)*1.1*gv[...,None]
    return col.astype(np.float32)
MW_=marble_rgb("white"); MD_=marble_rgb("dark")
def mcrop(M,ox=0,oy=0):
    ox=int(ox)%(MW-w); oy=int(oy)%(MH-h); return M[oy:oy+h,ox:ox+w].copy()
LGRAD=(1.08-0.45*np.clip(((xx/w-0.25)**2*0.8+(yy/h-0.15)**2*0.6),0,1)).astype(np.float32)[...,None]
# ---------- relief shading ----------
def relief(b,m,L=(-0.55,-0.75),depth=5.0,alb=None,gold=False,amb=0.32,rim=(1.0,0.75,0.35),rim_a=0.35,shad=(9,13),shad_a=0.5,strength=9.0,glowa=0.0,tint=(0.62,0.52,0.48)):
    ys,xs=np.nonzero(m>0.02)
    if len(xs)==0: return
    pad=int(depth*3+max(abs(shad[0]),abs(shad[1]))+6)
    x0,x1=max(0,xs.min()-pad),min(w,xs.max()+pad+1); y0,y1=max(0,ys.min()-pad),min(h,ys.max()+pad+1)
    mm=m[y0:y1,x0:x1]; bb=b[y0:y1,x0:x1]
    R=depth*4.0; dist=cv2.distanceTransform((mm>0.45).astype(np.uint8),cv2.DIST_L2,5)
    hm=R*np.sqrt(np.clip(dist/R,0,1))*np.clip((mm-0.45)/0.55,0,1)**0.6
    hm=cv2.GaussianBlur(hm,(0,0),2.4)
    gx=cv2.Sobel(hm,cv2.CV_32F,1,0,ksize=3)*(strength/40); gy=cv2.Sobel(hm,cv2.CV_32F,0,1,ksize=3)*(strength/40)
    nz=1/np.sqrt(1+gx*gx+gy*gy); nx=-gx*nz; ny=-gy*nz
    lx,ly=L; lz=0.55; ln=math.sqrt(lx*lx+ly*ly+lz*lz); lx,ly,lz=lx/ln,ly/ln,lz/ln
    dif=np.clip(nx*lx+ny*ly+nz*lz,0,1)
    hx,hy,hz=lx,ly,lz+1; hn=math.sqrt(hx*hx+hy*hy+hz*hz); spec=np.clip((nx*hx+ny*hy+nz*hz)/hn,0,1)**30
    if shad_a>0:
        M_=np.float32([[1,0,shad[0]],[0,1,shad[1]]]); sh_=cv2.warpAffine(cv2.GaussianBlur(mm,(0,0),depth*1.6),M_,(mm.shape[1],mm.shape[0]))
        bb*=(1-shad_a*np.clip(sh_,0,1)*(1-mm))[...,None]
    if gold:
        col=GOLD*(0.18+1.05*dif)[...,None]+GOLDL*(spec*1.6)[...,None]
    else:
        a=alb[y0:y1,x0:x1] if alb is not None else np.full(mm.shape+(3,),0.9,np.float32)
        tt_=np.array(tint,np.float32); k=(amb+(1-amb)*1.18*dif)[...,None]
        col=a*(tt_*(1-k)+k*1.0)*k**0.8+spec[...,None]*0.25
    if rim_a>0:
        r=np.clip(-(nx*lx+ny*ly)*1.6,0,1)**1.4*np.clip((1-nz)*6,0,1)
        col=col+np.array(rim,np.float32)*(r*rim_a)[...,None]
    m3=np.clip(mm*1.0,0,1)[...,None]; bb[:]=bb*(1-m3)+col*m3
    if glowa>0:
        g=cv2.GaussianBlur(mm,(0,0),10)
        bb+=(g*glowa)[...,None]*np.array(rim,np.float32)
def newm(): return np.zeros((h,w),np.float32)
# ---------- figures (mask drawing, canvas coords) ----------
def _P(x,y,s,d,u,v): return (int(round(x+u*s*d)),int(round(y-v*s)))
def _poly(m,x,y,s,d,pts,val=1.0): cv2.fillPoly(m,[np.array([_P(x,y,s,d,u,v) for u,v in pts],np.int32)],val,cv2.LINE_AA)
def _lines(m,x,y,s,d,pts,th,val=1.0):
    q=[_P(x,y,s,d,u,v) for u,v in pts]
    for a,b_ in zip(q,q[1:]): cv2.line(m,a,b_,val,max(1,int(th*s)),cv2.LINE_AA)
    for p in q: cv2.circle(m,p,max(1,int(th*s*0.5)),val,-1,cv2.LINE_AA)
def _circ(m,x,y,s,d,u,v,r,val=1.0): cv2.circle(m,_P(x,y,s,d,u,v),max(1,int(r*s)),val,-1,cv2.LINE_AA)
PROF=[(-0.45,0.0),(-0.48,-0.25),(-0.35,-0.45),(-0.1,-0.55),(0.15,-0.52),(0.30,-0.40),(0.36,-0.18),(0.38,-0.12),(0.50,0.08),(0.40,0.12),(0.41,0.18),(0.37,0.22),(0.39,0.27),(0.33,0.31),(0.34,0.40),(0.25,0.47),(0.10,0.45),(0.08,0.75),(-0.22,0.75),(-0.25,0.35),(-0.40,0.22)]
BUN=[(-0.40,0.25),(-0.58,0.18),(-0.62,-0.02),(-0.50,-0.15),(-0.40,-0.10)]
DIAD=[(-0.20,-0.52),(0.24,-0.47),(0.30,-0.60),(0.02,-0.76),(-0.26,-0.66)]
BEARD=[(0.10,0.45),(0.25,0.47),(0.34,0.40),(0.33,0.31),(0.30,0.55),(0.12,0.68),(-0.05,0.55)]
def head(m,x,y,s,d,u=0.0,v=0.92,r=0.058,female=True,diadem=False,beard=False):
    H=r*2.3*s; cx,cy=_P(x,y,s,d,u,v+0.01)
    def Q(pts): return np.array([(cx+px*H*d,cy+py*H) for px,py in pts],np.int32)
    cv2.fillPoly(m,[Q(PROF)],1.0,cv2.LINE_AA)
    if female: cv2.fillPoly(m,[Q(BUN)],0.95,cv2.LINE_AA)
    if diadem: cv2.fillPoly(m,[Q(DIAD)],1.0,cv2.LINE_AA)
    if beard: cv2.fillPoly(m,[Q(BEARD)],0.95,cv2.LINE_AA)
    e=Q([(0.24,-0.06)])[0]; cv2.ellipse(m,(int(e[0]),int(e[1])),(max(1,int(H*0.06)),max(1,int(H*0.025))),0,0,360,0.78,-1,cv2.LINE_AA)
    for k in range(3):   # hair waves
        q=Q([(-0.30+k*0.12,-0.40),(-0.20+k*0.12,-0.20),(-0.32+k*0.1,0.05)]); cv2.polylines(m,[q],False,0.82,max(1,int(H*0.025)),cv2.LINE_AA)
def robe_fig(m,x,y,s,d,crown=False,scepter=False,arm="fwd",veil=False,cup=False,arm_t=0.0):
    head(m,x,y,s,d,diadem=crown)
    _poly(m,x,y,s,d,[(-0.115,0.835),(0.10,0.835),(0.125,0.70),(0.10,0.56),(0.12,0.40),(0.17,0.0),(-0.20,0.0),(-0.15,0.35),(-0.13,0.56)])
    for u in (-0.09,-0.045,0.0,0.045,0.09): _lines(m,x,y,s,d,[(u*0.8,0.50),(u*1.35+0.01,0.03)],0.008,0.72)
    _lines(m,x,y,s,d,[(-0.11,0.80),(0.08,0.56),(0.12,0.50)],0.012,0.75)   # himation diagonal fold
    if veil: _poly(m,x,y,s,d,[(-0.04,0.99),(-0.13,0.93),(-0.17,0.70),(-0.11,0.72),(-0.07,0.86)],0.92)
    _lines(m,x,y,s,d,[(-0.09,0.80),(-0.13,0.63),(-0.11,0.48)],0.045)
    if arm=="fwd": _lines(m,x,y,s,d,[(0.07,0.80),(0.15,0.66),(0.27,0.70)],0.045)
    elif arm=="up": _lines(m,x,y,s,d,[(0.07,0.80),(0.15,0.90+0.03*arm_t),(0.20,1.02+0.05*arm_t)],0.045)
    elif arm=="out": _lines(m,x,y,s,d,[(0.07,0.80),(0.20,0.74),(0.33,0.76)],0.045)
    if scepter: _lines(m,x,y,s,d,[(0.27,0.0),(0.27,1.08)],0.018); _circ(m,x,y,s,d,0.27,1.09,0.025)
    if cup: _poly(m,x,y,s,d,[(0.25,0.74),(0.33,0.74),(0.31,0.70),(0.27,0.70)]); _lines(m,x,y,s,d,[(0.29,0.70),(0.29,0.67)],0.012); _lines(m,x,y,s,d,[(0.27,0.665),(0.31,0.665)],0.012)
def hero_fig(m,x,y,s,d,pose="stand",club=True,lion=True,beard=False,himation=False,t=0.0):
    if pose=="kneel":
        if lion: _poly(m,x,y,s,d,[(0.02,0.60),(-0.16,0.56),(-0.26,0.16),(-0.12,0.26)],0.9)
        _poly(m,x,y,s,d,[(-0.09,0.58),(0.06,0.62),(0.13,0.56),(0.07,0.32),(-0.10,0.30)])
        _circ(m,x,y,s,d,0.15,0.555,0.06)
        _lines(m,x,y,s,d,[(0.0,0.31),(0.20,0.29),(0.21,0.02)],0.075); _lines(m,x,y,s,d,[(0.21,0.02),(0.28,0.0)],0.04)
        _lines(m,x,y,s,d,[(-0.06,0.30),(-0.07,0.03),(-0.26,0.0)],0.07)
        _lines(m,x,y,s,d,[(0.09,0.58),(0.24,0.52),(0.20,0.58)],0.045); _lines(m,x,y,s,d,[(-0.04,0.58),(0.08,0.46),(0.16,0.50)],0.045)
        return
    hv=0.92; head(m,x,y,s,d,0.0,hv,female=False,beard=beard)
    if lion:
        _circ(m,x,y,s,d,-0.012,hv+0.015,0.072,0.95); _circ(m,x,y,s,d,-0.05,hv+0.07,0.02,0.95)
        _poly(m,x,y,s,d,[(-0.03,hv+0.02),(-0.17,0.80),(-0.24,0.40),(-0.20,0.30),(-0.12,0.52),(-0.08,0.80)],0.9)
        _lines(m,x,y,s,d,[(0.07,0.82),(-0.07,0.66)],0.03,0.9)
    _poly(m,x,y,s,d,[(-0.135,0.825),(-0.10,0.848),(0.10,0.848),(0.135,0.825),(0.115,0.72),(0.085,0.60),(0.08,0.52),(-0.08,0.52),(-0.085,0.60),(-0.115,0.72)])
    cv2.ellipse(m,_P(x,y,s,d,0.045,0.74),(int(0.05*s),int(0.025*s)),0,0,180,0.8,max(1,int(0.006*s)),cv2.LINE_AA)
    cv2.ellipse(m,_P(x,y,s,d,-0.045,0.74),(int(0.05*s),int(0.025*s)),0,0,180,0.8,max(1,int(0.006*s)),cv2.LINE_AA)
    _poly(m,x,y,s,d,[(-0.09,0.53),(0.09,0.53),(0.10,0.45),(-0.10,0.45)])
    if himation: _poly(m,x,y,s,d,[(-0.11,0.56),(0.10,0.56),(0.16,0.0),(-0.19,0.0)])
    else:
        _lines(m,x,y,s,d,[(-0.05,0.47),(-0.08,0.25),(-0.12,0.02)],0.072); _lines(m,x,y,s,d,[(0.05,0.47),(0.12,0.25),(0.15,0.02)],0.072)
        _lines(m,x,y,s,d,[(-0.12,0.02),(-0.05,0.0)],0.04); _lines(m,x,y,s,d,[(0.15,0.02),(0.22,0.0)],0.04)
    if pose=="stand":
        _lines(m,x,y,s,d,[(0.105,0.81),(0.17,0.65),(0.19,0.52)],0.05)
        if club: _poly(m,x,y,s,d,[(0.175,0.55),(0.205,0.55),(0.27,0.05),(0.20,0.02)])
        _lines(m,x,y,s,d,[(-0.105,0.81),(-0.15,0.65),(-0.12,0.50)],0.05)
    elif pose=="raise":   # arm raised (zeus w/ thunderbolt, or triumph)
        _lines(m,x,y,s,d,[(0.105,0.81),(0.19,0.93),(0.21,1.05)],0.05)
        _lines(m,x,y,s,d,[(-0.105,0.81),(-0.15,0.65),(-0.12,0.50)],0.05)
    elif pose=="reach":
        _lines(m,x,y,s,d,[(0.105,0.81),(0.22,0.74),(0.34,0.76)],0.05)
        _lines(m,x,y,s,d,[(-0.105,0.81),(-0.15,0.65),(-0.12,0.50)],0.05)
        if club: _poly(m,x,y,s,d,[(-0.135,0.53),(-0.105,0.53),(-0.08,0.05),(-0.15,0.02)])
    elif pose=="grief":
        _lines(m,x,y,s,d,[(0.105,0.81),(0.20,0.90),(0.07,0.97)],0.05)
        _lines(m,x,y,s,d,[(-0.105,0.81),(-0.17,0.91),(-0.06,0.98)],0.05)
    elif pose=="ascend":
        _lines(m,x,y,s,d,[(0.105,0.81),(0.20,0.92),(0.27,1.04+0.02*math.sin(t*2))],0.05)
        _lines(m,x,y,s,d,[(-0.105,0.81),(-0.20,0.92),(-0.26,1.03)],0.05)
def baby_fig(m,x,y,s,arms=0.0):
    cv2.ellipse(m,(int(x),int(y-s*0.30)),(int(s*0.24),int(s*0.32)),0,0,360,1.0,-1,cv2.LINE_AA)
    cv2.circle(m,(int(x),int(y-s*0.80)),int(s*0.21),1.0,-1,cv2.LINE_AA)
    for sg in (-1,1):
        ex=x+sg*s*(0.30+0.14*arms); ey=y-s*(0.45+0.55*arms); elx=x+sg*s*(0.34+0.06*arms); ely=y-s*(0.48+0.12*arms)
        cv2.line(m,(int(x+sg*s*0.17),int(y-s*0.50)),(int(elx),int(ely)),1.0,max(2,int(s*0.13)),cv2.LINE_AA)
        cv2.line(m,(int(elx),int(ely)),(int(ex),int(ey)),1.0,max(2,int(s*0.12)),cv2.LINE_AA); cv2.circle(m,(int(ex),int(ey)),int(s*0.09),1.0,-1,cv2.LINE_AA)
        cv2.line(m,(int(x+sg*s*0.10),int(y-s*0.08)),(int(x+sg*s*0.20),int(y+s*0.05)),1.0,max(2,int(s*0.15)),cv2.LINE_AA)
def cradle(m,x,y,s):
    cv2.ellipse(m,(int(x),int(y)),(int(s*0.62),int(s*0.30)),0,0,180,1.0,-1,cv2.LINE_AA)
    cv2.rectangle(m,(int(x-s*0.66),int(y-s*0.04)),(int(x+s*0.66),int(y+s*0.03)),1.0,-1,cv2.LINE_AA)
    for sg in (-1,1): cv2.line(m,(int(x+sg*s*0.45),int(y+s*0.2)),(int(x+sg*s*0.55),int(y+s*0.48)),1.0,max(2,int(s*0.06)),cv2.LINE_AA)
    for k in range(-4,5): cv2.line(m,(int(x+k*s*0.12),int(y+s*0.02)),(int(x+k*s*0.10),int(y+s*0.26)),0.72,max(1,int(s*0.012)),cv2.LINE_AA)
def column(m,x,y0,y1,r):
    cv2.rectangle(m,(int(x-r),int(y0)),(int(x+r),int(y1)),1.0,-1)
    for k in (-0.6,-0.2,0.2,0.6): cv2.line(m,(int(x+k*r),int(y0+r*0.6)),(int(x+k*r),int(y1-r*0.4)),0.7,max(1,int(r*0.14)),cv2.LINE_AA)
    cv2.rectangle(m,(int(x-r*1.45),int(y0-r*0.55)),(int(x+r*1.45),int(y0)),1.0,-1); cv2.rectangle(m,(int(x-r*1.3),int(y1)),(int(x+r*1.3),int(y1+r*0.4)),1.0,-1)
def temple(m,cx,base,width,colh,n=6):
    r=width/(n*3.2); xs=[cx-width/2+r*1.6+i*(width-r*3.2)/(n-1) for i in range(n)]
    for x in xs: column(m,x,base-colh,base,r)
    cv2.rectangle(m,(int(cx-width/2-r),int(base-colh-r*2.4)),(int(cx+width/2+r),int(base-colh-r*0.55)),1.0,-1)
    cv2.line(m,(int(cx-width/2-r),int(base-colh-r*1.5)),(int(cx+width/2+r),int(base-colh-r*1.5)),0.7,2,cv2.LINE_AA)
    cv2.fillPoly(m,[np.array([(cx-width/2-r*1.5,base-colh-r*2.4),(cx+width/2+r*1.5,base-colh-r*2.4),(cx,base-colh-r*2.4-width*0.2)],np.int32)],1.0,cv2.LINE_AA)
    cv2.fillPoly(m,[np.array([(cx-width/2+r*1.5,base-colh-r*2.9),(cx+width/2-r*1.5,base-colh-r*2.9),(cx,base-colh-r*2.4-width*0.17)],np.int32)],0.75,cv2.LINE_AA)
    for k in range(3): cv2.rectangle(m,(int(cx-width/2-r*(2+k)),int(base+r*0.4+k*r*0.5)),(int(cx+width/2+r*(2+k)),int(base+r*0.4+(k+1)*r*0.5)),1.0-0.05*k,-1)
def tripod(m,x,y,s):
    for u in (-0.3,0.0,0.3): cv2.line(m,(int(x+u*s*0.3),int(y-s*0.62)),(int(x+u*s),int(y)),1.0,max(2,int(s*0.04)),cv2.LINE_AA)
    cv2.ellipse(m,(int(x),int(y-s*0.70)),(int(s*0.36),int(s*0.14)),0,0,180,1.0,-1,cv2.LINE_AA)
    cv2.rectangle(m,(int(x-s*0.38),int(y-s*0.73)),(int(x+s*0.38),int(y-s*0.68)),1.0,-1)
    for sg in (-1,1): cv2.ellipse(m,(int(x+sg*s*0.30),int(y-s*0.80)),(int(s*0.07),int(s*0.07)),0,0,360,1.0,max(1,int(s*0.025)),cv2.LINE_AA)
# ---------- carved text ----------
_TX={}
def text_mask(txt,size,font=SERIF,track=0):
    k=(txt,size,font,track)
    if k in _TX: return _TX[k]
    f=ImageFont.truetype(font,int(size)); widths=[f.getlength(c) for c in txt]; tw=int(sum(widths)+track*(len(txt)-1))+20
    im=Image.new("L",(tw,int(size*1.4)),0); d=ImageDraw.Draw(im); x=10
    for c,cw in zip(txt,widths): d.text((x,size*1.1),c,font=f,fill=255,anchor="ls"); x+=cw+track
    a=np.asarray(im).astype(np.float32)/255; _TX[k]=a; return a
def put(m,a,cx,cy,sc=1.0,val=1.0):
    if sc!=1: a=cv2.resize(a,(max(1,int(a.shape[1]*sc)),max(1,int(a.shape[0]*sc))),interpolation=cv2.INTER_AREA if sc<1 else cv2.INTER_LINEAR)
    x0=int(cx-a.shape[1]/2); y0=int(cy-a.shape[0]/2); X0,Y0=max(0,x0),max(0,y0); X1,Y1=min(w,x0+a.shape[1]),min(h,y0+a.shape[0])
    if X1<=X0 or Y1<=Y0: return
    m[Y0:Y1,X0:X1]=np.maximum(m[Y0:Y1,X0:X1],a[Y0-y0:Y1-y0,X0-x0:X1-x0]*val)
# ---------- peacock feather sprite ----------
SW_,SH_=240,560; EYE=(120,150)
def _feather():
    rgb=np.zeros((SH_,SW_,3),np.float32); al=np.zeros((SH_,SW_),np.float32)
    g=np.random.default_rng(780)
    for k in range(260):
        v=-40+k*1.8; y0=EYE[1]+v; side=1 if k%2 else -1
        ang=math.radians(g.uniform(32,52)); wid=max(10,105*math.sin(math.pi*np.clip((v+120)/560,0,1))**0.7)*g.uniform(0.85,1.1)
        x1=EYE[0]+side*wid*math.cos(ang); y1=y0-wid*math.sin(ang)*1.15
        tone=np.clip(1-abs(v)/420,0,1); col=(0.25+0.55*tone,0.55+0.2*tone,0.18+0.05*tone)
        cv2.line(rgb,(EYE[0],int(y0)),(int(x1),int(y1)),col,1,cv2.LINE_AA); cv2.line(al,(EYE[0],int(y0)),(int(x1),int(y1)),0.75*(0.45+0.55*tone),1,cv2.LINE_AA)
    for k in range(40):  # crown barbs around eye top
        a=math.radians(-160+k*3.5); r0=55; r1=95+g.uniform(-8,8)
        p0=(int(EYE[0]+math.cos(a)*r0*0.9),int(EYE[1]+math.sin(a)*r0)); p1=(int(EYE[0]+math.cos(a)*r1*0.9),int(EYE[1]+math.sin(a)*r1))
        cv2.line(rgb,p0,p1,(0.55,0.62,0.18),1,cv2.LINE_AA); cv2.line(al,p0,p1,0.6,1,cv2.LINE_AA)
    rgb=cv2.GaussianBlur(rgb,(0,0),0.6); al=cv2.GaussianBlur(al,(0,0),0.6)
    Y,X=np.mgrid[0:SH_,0:SW_].astype(np.float32); u=X-EYE[0]; v=Y-EYE[1]
    d=np.sqrt((u/46)**2+(v/60)**2); din=np.sqrt((u/21)**2+((v+5)/29)**2)
    rings=[(1.45,(0.30,0.50,0.14)),(1.22,(0.80,0.62,0.18)),(1.0,(0.42,0.24,0.08)),(0.80,(0.05,0.50,0.52))]
    for r_,c in rings:
        mk=sm_np((r_-d)/0.10); rgb=rgb*(1-mk[...,None])+np.array(c,np.float32)*mk[...,None]; al=np.maximum(al,mk*(0.55 if r_>1.3 else 0.97))
    mk=sm_np((1-din)/0.08); core=np.array([0.03,0.07,0.42],np.float32)+np.array([0.08,0.20,0.45],np.float32)*np.clip(1-din,0,1)[...,None]
    rgb=rgb*(1-mk[...,None])+core*mk[...,None]
    cv2.line(rgb,(EYE[0],EYE[1]+60),(EYE[0],SH_-4),(0.95,0.85,0.55),2,cv2.LINE_AA); cv2.line(al,(EYE[0],EYE[1]+60),(EYE[0],SH_-4),0.9,2,cv2.LINE_AA)
    shine=np.exp(-((u+10)**2/180+(v+20)**2/300))*0.5; rgb+=shine[...,None]*np.array([0.6,0.8,1.0],np.float32)
    return rgb,al
FRGB,FAL=_feather()
def feather(b,x,y,sc=1.0,ang=0.0,a=1.0,glint=0.0):
    R=int(470*sc)+4; x0,x1=max(0,int(x-R)),min(w,int(x+R)); y0,y1=max(0,int(y-R)),min(h,int(y+R))
    if x0>=x1 or y0>=y1 or a<=0.01: return
    M=cv2.getRotationMatrix2D(EYE,-ang,sc); M[0,2]+=x-EYE[0]-x0; M[1,2]+=y-EYE[1]-y0
    rg=cv2.warpAffine(FRGB,M,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR); al=cv2.warpAffine(FAL,M,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR)*a
    if glint: rg=rg*(1+glint)
    bb=b[y0:y1,x0:x1]; bb[:]=bb*(1-al[...,None])+rg*al[...,None]
def fan(b,px,py,R,n=11,spread=150,sc=0.8,open_=1.0,a=1.0,t=0.0,rot=0.0):
    for i in range(n):
        f=(i/(n-1)-0.5)*spread*open_+rot; rr=math.radians(f)
        feather(b,px+math.sin(rr)*R,py-math.cos(rr)*R,sc,f,a,0.15*math.sin(t*2+i))
# ---------- sky / clouds / rays ----------
def sky(top,bot,k0=0.0,k1=1.0):
    k=np.clip((yy/h-k0)/(k1-k0),0,1)[...,None]; return (np.array(top,np.float32)*(1-k)+np.array(bot,np.float32)*k).astype(np.float32)
def rays(b,cx,cy,t,a=0.5,col=(1.0,0.82,0.5),fall=700):
    ang=(np.arctan2(yy-cy,xx-cx)/(2*np.pi)+0.5+t*0.004)%1.0
    p=RAYP[(ang*2047).astype(np.int32)]; r=np.sqrt((xx-cx)**2+(yy-cy)**2)
    I=np.clip(p-0.35,0,1)**1.5*np.exp(-r/fall)*np.clip(r/60,0,1)
    b+=(I*a)[...,None]*np.array(col,np.float32)
def clouds(b,t,y0,y1,speed=12,layer=0,a=1.0,lit=(1.05,0.95,0.85),shd=(0.55,0.50,0.62),dens=1.0,thr=0.15):
    off=int(t*speed)%w; c=CLD[layer][:,off:off+w]
    band=sm_np((yy-y0)/80)*(1-sm_np((yy-y1)/80))
    d=np.clip((c-thr)*0.9*dens,0,1)*band
    sh_=np.clip(d-np.roll(d,10,0),0,1)
    li=np.clip(1-np.clip(np.roll(d,-14,0)-d,0,1)*3.5,0,1)
    col=np.array(shd,np.float32)*(1-li[...,None])+np.array(lit,np.float32)*li[...,None]
    dd=(np.clip(d*1.6,0,1)*a)[...,None]; b[:]=b*(1-dd)+col*dd
def olympus_bg(t,sun=(0.5,0.2),top=(0.10,0.12,0.30),bot=(1.0,0.72,0.42),ra=0.55,cl=True):
    b=sky(top,bot,0.0,0.85); sx,sy=w*sun[0],h*sun[1]
    glow(b,sx,sy,60,(2.0,1.6,1.0),1.0); glow(b,sx,sy,260,(0.9,0.6,0.3),0.6)
    rays(b,sx,sy,t,ra)
    if cl:
        clouds(b,t,h*0.05,h*0.40,5,1,0.55,thr=0.4)
        clouds(b,t,h*0.70,h*1.1,14,0,0.95,dens=1.3,thr=0.0)
    return b
# ---------- gold frieze bands (static) ----------
def _meander(hh=26,period=40):
    m=np.zeros((hh,w),np.float32)
    for x0 in range(-period,w+period,period):
        pts=[(x0,hh-4),(x0,4),(x0+period*0.75,4),(x0+period*0.75,hh-10),(x0+period*0.3,hh-10),(x0+period*0.3,10),(x0+period*0.5,10)]
        cv2.polylines(m,[np.array(pts,np.int32)],False,1.0,3,cv2.LINE_AA)
    cv2.line(m,(0,1),(w,1),1.0,2); cv2.line(m,(0,hh-2),(w,hh-2),1.0,2); return m
MEAND=_meander()
def bands(b,tops=(52,1060)):
    for y0 in tops:
        m=newm(); m[y0:y0+MEAND.shape[0]]=MEAND
        b[y0-8:y0+MEAND.shape[0]+8]*=0.72
        relief(b,m,gold=True,depth=1.2,shad=(2,3),shad_a=0.4,strength=5,rim_a=0.0)
def spot(cx,cy,rx,ry,lo=0.30):
    return (lo+(1-lo)*np.exp(-(((xx-cx)/rx)**2+((yy-cy)/ry)**2)))[...,None].astype(np.float32)
def panel(t,kind="white",ox=0,oy=0,light=1.0,band=True,sp=(0.42,0.45,430,640),lo=0.30,tone=(0.62,0.62,0.70)):
    b=mcrop(MW_ if kind=="white" else MD_,ox+t*4,oy+t*6)*LGRAD*light*np.array(tone,np.float32)
    if sp is not None and kind=="white": b*=spot(w*sp[0],h*sp[1],sp[2],sp[3],lo)
    if band: bands(b)
    return b
# ---------- extra props ----------
DARKA=np.full((h,w,3),0.05,np.float32); BRONZE=np.full((h,w,3),0.0,np.float32)+np.array([0.55,0.40,0.25],np.float32)
def serpent(b,pts,th,glow_a=0.7,eyes=True,a=1.0):
    m=newm(); n=len(pts)
    for i in range(n-1):
        f=i/(n-1); tk=th*(0.22+0.78*math.sin(math.pi*min(1.0,f*1.25+0.05))**0.6)
        cv2.line(m,(int(pts[i][0]),int(pts[i][1])),(int(pts[i+1][0]),int(pts[i+1][1])),1.0 if (i//2)%2 else 0.86,max(2,int(tk)),cv2.LINE_AA)
    hx,hy=pts[-1]; px,py=pts[-3]; ang=math.degrees(math.atan2(hy-py,hx-px))
    cv2.ellipse(m,(int(hx),int(hy)),(int(th*0.95),int(th*0.62)),ang,0,360,1.0,-1,cv2.LINE_AA)
    if a<1: m*=a
    relief(b,m,gold=True,depth=max(1.5,th*0.18),strength=8,shad=(5,8),shad_a=0.45,rim_a=0.0)
    if glow_a>0:
        g=cv2.GaussianBlur(cv2.resize(m,(w//4,h//4),interpolation=cv2.INTER_AREA),(0,0),4); b+=cv2.resize(g,(w,h))[...,None]*np.array([1.0,0.6,0.15],np.float32)*glow_a
    if eyes and a>0.5:
        ca,sa=math.cos(math.radians(ang)),math.sin(math.radians(ang))
        for sg in (-1,1): glow(b,hx+ca*th*0.35-sa*th*0.32*sg,hy+sa*th*0.35+ca*th*0.32*sg,max(2,th*0.12),(2.5,0.3,0.1),1.0)
def spath(x0,y0,x1,y1,t,amp=30,waves=2.0,n=40,ph=0.0):
    L=math.hypot(x1-x0,y1-y0)+1e-6; ux,uy=(x1-x0)/L,(y1-y0)/L; out=[]
    for i in range(n):
        f=i/(n-1); o=amp*math.sin(f*waves*2*math.pi-t*7+ph)*(0.3+0.7*(1-f)) 
        out.append((x0+ux*L*f-uy*o,y0+uy*L*f+ux*o))
    return out
def wreath(m,cx,cy,r,n=13,lw=0.30,val=1.0):
    for side in (-1,1):
        for i in range(n):
            a=math.radians(100+i*(150/n))*1.0; ax=cx+side*math.cos(a-math.pi/2+math.pi/2)*0  # placeholder
            th=math.radians(250-i*(155/(n-1))) if side<0 else math.radians(-70+i*(155/(n-1)))
            x=cx+math.cos(th)*r; y=cy-math.sin(th)*r
            tang=math.degrees(-th)+(90 if side<0 else -90)
            for o in (-1,1):
                cv2.ellipse(m,(int(x+o*math.cos(th)*r*0.09),int(y-o*math.sin(th)*r*0.09)),(int(r*lw*0.5),int(r*lw*0.18)),tang+o*35*side,0,360,val,-1,cv2.LINE_AA)
    cv2.ellipse(m,(int(cx),int(cy)),(int(r),int(r)),0,25,155,val,max(2,int(r*0.03)),cv2.LINE_AA)
def hourglass(m,cx,cy,s,sand):
    cv2.rectangle(m,(int(cx-s*0.42),int(cy-s*0.62)),(int(cx+s*0.42),int(cy-s*0.54)),1.0,-1); cv2.rectangle(m,(int(cx-s*0.42),int(cy+s*0.54)),(int(cx+s*0.42),int(cy+s*0.62)),1.0,-1)
    for sg in (-1,1): cv2.line(m,(int(cx+sg*s*0.36),int(cy-s*0.56)),(int(cx+sg*s*0.36),int(cy+s*0.56)),1.0,max(2,int(s*0.05)),cv2.LINE_AA)
    g=np.array([(cx-s*0.28,cy-s*0.54),(cx+s*0.28,cy-s*0.54),(cx+s*0.04,cy),(cx+s*0.28,cy+s*0.54),(cx-s*0.28,cy+s*0.54),(cx-s*0.04,cy)],np.int32)
    cv2.polylines(m,[g],True,0.8,max(1,int(s*0.02)),cv2.LINE_AA)
def crown(m,cx,cy,s,val=1.0):
    pts=[(-0.5,0.3),(-0.5,-0.25),(-0.3,0.05),(-0.15,-0.4),(0,0.0),(0.15,-0.4),(0.3,0.05),(0.5,-0.25),(0.5,0.3)]
    cv2.fillPoly(m,[np.array([(cx+u*s,cy+v*s) for u,v in pts],np.int32)],val,cv2.LINE_AA)
    for u in (-0.5,-0.15,0.15,0.5): cv2.circle(m,(int(cx+u*s),int(cy-(0.25 if abs(u)==0.5 else 0.4)*s)),max(2,int(s*0.07)),val,-1,cv2.LINE_AA)
def bolt(b,x,y,s,t):
    m=newm(); pts=[(0,-0.5),(0.12,-0.12),(-0.04,-0.08),(0.10,0.30),(-0.10,-0.02),(0.04,-0.06),(-0.06,-0.5)]
    cv2.fillPoly(m,[np.array([(x+u*s,y+v*s) for u,v in pts],np.int32)],1.0,cv2.LINE_AA)
    relief(b,m,gold=True,depth=1.5,strength=8,shad_a=0.3,rim_a=0.0); fl=0.8+0.2*math.sin(t*23)+0.15*math.sin(t*41)
    glow(b,x,y,s*0.35,(1.6,1.2,0.6),0.7*fl); glow(b,x,y,s*1.0,(0.6,0.4,0.2),0.35*fl)
_DUST=np.random.default_rng(790).random((70,4)).astype(np.float32)
def dust(b,t,a=0.6,col=(1.0,0.8,0.45)):
    lay=np.zeros((h//2,w//2),np.float32)
    for x,y,s,p in _DUST:
        X=(x*w+12*math.sin(t*0.5+p*9)+t*6)%w; Y=(y*h-t*(10+18*s))%h
        cv2.circle(lay,(int(X/2),int(Y/2)),1,float(0.4+0.6*s),-1,cv2.LINE_AA)
    lay=cv2.GaussianBlur(lay,(0,0),1.0); b+=cv2.resize(lay,(w,h))[...,None]*np.array(col,np.float32)*a
def statue_light(t): return (-0.55+0.12*math.sin(t*0.6),-0.75)
# ================= shots =================
def sh_hook(t,close=False,end=False):
    tt=t-TOTAL if end else t
    b=olympus_bg(tt,sun=(0.5,0.21),top=(0.03,0.03,0.12),bot=(0.55,0.28,0.22),ra=0.6)
    b*=(0.45+0.55*np.clip(1-np.abs(xx-360)/380,0,1))[...,None]
    fan(b,360,800,285,n=11,spread=170,sc=0.70,t=tt,rot=2*math.sin(tt*0.8))
    m=newm(); robe_fig(m,360,1340,850,1,crown=True,veil=False,arm="out",scepter=True)
    relief(b,m,alb=MW_*0.42,L=(-0.85,-0.25),strength=12,rim=(1.0,0.70,0.30),rim_a=1.3,shad_a=0.0,glowa=0.12,amb=0.25)
    if close:
        k=t-wt(0,"kill")+0.25
        if k>0:
            e=eout(k/0.8)
            for sg in (-1,1):
                x0=360+sg*420; x1=360+sg*(230-60*e); y1=1150-430*e
                serpent(b,spath(x0,1290,x1,y1,t,30,1.6,ph=sg),30,0.9)
            glow(b,360+0.03*850,1340-0.925*850,7,(2.4,1.5,0.5),e)
    clouds(b,tt,h*0.88,h*1.2,22,0,0.9,dens=1.4,thr=0.0)
    dust(b,tt,0.5)
    return b,None,(1.02+0.025*sm((tt+0.2)/4)) if not close else 1.22+0.03*(t-wt(0,"goddess"))
def sh_name(t,phase=0):
    b=panel(t,sp=(0.5,0.42,420,600)); u=t-(Ls(1) if phase==0 else wt(1,"glory"))
    if phase==0:
        m=newm(); hero_fig(m,360,1060,520,1); relief(b,m,alb=MW_*0.95,L=statue_light(t),strength=10)
        tm=text_mask("ΗΡΑΚΛΗΣ",112,track=6); m=newm(); put(m,tm,360,445)
        rev=np.clip((xx-(-200+u*1100))/-80,0,1); m*=rev
        relief(b,m,gold=True,depth=2.2,strength=7,shad=(3,5),shad_a=0.5,rim_a=0.0)
        g=cv2.GaussianBlur(m,(0,0),8); b+=g[...,None]*np.array([0.5,0.32,0.1],np.float32)*0.6
        sx=-200+u*1100
        if 120<sx<620: glow(b,sx,445,30,(2.0,1.5,0.8),0.8)
    else:
        e=eout(u/0.45)
        m=newm(); put(m,text_mask("ΗΡΑ",96,track=4),lerp(290,165,e),445); put(m,text_mask("ΚΛΕΟΣ",96,track=4),lerp(455,480,e),445)
        relief(b,m,gold=True,depth=2.2,strength=7,shad=(3,5),shad_a=0.5,rim_a=0.0)
        g=cv2.GaussianBlur(m,(0,0),8); b+=g[...,None]*np.array([0.5,0.32,0.1],np.float32)*0.6
        a=sm((u-0.1)/0.4)
        m=newm(); robe_fig(m,190,1060,500,1,crown=True,veil=True,arm="out"); relief(b,m,alb=MW_*0.95,L=statue_light(t),strength=10)
        m=newm(); wreath(m,530,760,150); relief(b,m*a,gold=True,depth=1.6,strength=7,shad=(4,6),rim_a=0.0)
        glow(b,530,760,90,(1.0,0.75,0.35),0.5*a); rays(b,530,760,t,0.35*a,fall=260)
        feather(b,360,640,0.42,0,a*0.9)
    dust(b,t,0.4)
    def hud(img):
        if phase==0: label(img,"IN GREEK:",540,300,84,WHITE,a=fa(t,Ls(1)+0.05,99,0.15,0.2))
        else:
            label(img,"HERA + KLEOS",540,300,110,WHITE,a=fa(t,wt(1,"glory")-0.05,99,0.12,0.2))
            label(img,"KLEOS = GLORY, FAME",540,420,62,ORANGE,a=fa(t,wt(1,"glory")+0.3,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.02*u
def sh_zeus(t):
    u=t-Ls(2); b=panel(t,ox=200,sp=(0.5,0.48,430,620))
    fan(b,500,610,190,n=9,spread=150,sc=0.42,t=t,open_=0.6+0.4*eout(u/0.8))
    m=newm(); robe_fig(m,500,1060,540,-1,crown=True,scepter=True,veil=True,arm="fwd"); relief(b,m,alb=MW_*0.95,L=statue_light(t),strength=10)
    m=newm(); hero_fig(m,220,1060,560,1,pose="raise",club=False,lion=False,beard=True,himation=True); relief(b,m,alb=MW_*0.95,L=statue_light(t),strength=10)
    bolt(b,220+0.21*560,1060-1.05*560-30,90,t)
    dust(b,t,0.4)
    def hud(img):
        label(img,"KING & QUEEN",540,290,104,WHITE,a=fa(t,Ls(2)+0.05,99,0.15,0.2)); label(img,"OF THE GODS",540,400,76,ORANGE,a=fa(t,Ls(2)+0.25,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.025*u
def sh_alcmene(t):
    u=t-wt(2,"Heracles"); b=panel(t,ox=420,oy=200,sp=(0.5,0.55,400,560),tone=(0.66,0.60,0.62))
    feather(b,360,560,0.95,0,0.85*sm(u/0.6),0.25*math.sin(t*3))
    glow(b,360,640,120,(1.0,0.7,0.35),0.35+0.1*math.sin(t*3))
    m=newm(); hero_fig(m,215,1060,560,1,pose="reach",club=False,lion=False,beard=True,himation=True); relief(b,m,alb=MW_*0.95,L=statue_light(t),strength=10)
    m=newm(); robe_fig(m,505,1060,520,-1,arm="fwd",veil=True); relief(b,m,alb=MW_*np.array([1.0,0.93,0.86],np.float32),L=statue_light(t),strength=10)
    dust(b,t,0.4)
    def hud(img):
        label(img,"ALCMENE",540,290,118,WHITE,a=fa(t,wt(2,"mortal")-0.1,99,0.15,0.2)); label(img,"A MORTAL QUEEN",540,410,70,ORANGE,a=fa(t,wt(2,"mortal")+0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
def sh_iliad(t):
    u=t-Ls(3); b=panel(t,"dark",oy=300); glow(b,w*0.5,h*0.5,330,(0.35,0.25,0.15),0.6)
    m=newm(); robe_fig(m,230,1080,560,1,crown=True,veil=True,arm="out"); relief(b,m,alb=MW_*0.9,L=statue_light(t),strength=10,rim_a=0.6)
    stop=sm((t-wt(3,"delays"))/0.3)
    hx,hy,hs=505,720,300; m=newm(); hourglass(m,hx,hy,hs,0); relief(b,m,gold=True,depth=2,strength=7,shad=(5,7),rim_a=0.0)
    fl=1-stop; top=0.5+0.25*sm(u/2)*0; lay=newm()
    cv2.fillPoly(lay,[np.array([(hx-hs*0.22,hy-hs*0.30),(hx+hs*0.22,hy-hs*0.30),(hx+hs*0.04,hy-hs*0.03),(hx-hs*0.04,hy-hs*0.03)],np.int32)],1.0,cv2.LINE_AA)
    cv2.fillPoly(lay,[np.array([(hx-hs*0.26,hy+hs*0.53),(hx+hs*0.26,hy+hs*0.53),(hx,hy+hs*0.36)],np.int32)],1.0,cv2.LINE_AA)
    if fl>0.02: cv2.line(lay,(hx,int(hy)),(hx,int(hy+hs*0.5)),fl,3,cv2.LINE_AA)
    b+=lay[...,None]*np.array([1.0,0.72,0.32],np.float32)*0.9; glow(b,hx,hy+hs*0.2,40,(1.2,0.8,0.3),0.4*fl+0.1)
    if stop>0: glow(b,hx,hy,60,(0.6,0.7,1.2),0.5*stop*(1-sm((t-wt(3,"delays")-0.4)/0.6)))
    def hud(img):
        label(img,"THE ILIAD",540,290,118,WHITE,a=fa(t,Ls(3)+0.05,99,0.15,0.2)); label(img,"BIRTH HELD BACK",540,410,70,ORANGE,a=fa(t,wt(3,"delays")-0.05,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.025*u
def sh_rival(t):
    u=t-wt(3,"rival"); b=panel(t,ox=100,oy=500,sp=(0.32,0.6,330,520),tone=(0.60,0.60,0.68))
    for cx,act in ((190,1),(530,0)):
        m=newm(); cradle(m,cx,860,215)
        if act: baby_fig(m,cx,840,95,0.2)
        relief(b,m,alb=MW_*(0.95 if act else 0.6),L=statue_light(t),strength=10)
    glow(b,190,760,140,(1.0,0.7,0.3),0.45)
    e=eout((u-0.1)/0.8); m=newm(); crown(m,190,lerp(300,650,e),100); relief(b,m,gold=True,depth=2,strength=8,shad=(4,8),rim_a=0.0); glow(b,190,lerp(300,650,e),70,(1.2,0.8,0.3),0.5)
    def hud(img):
        label(img,"EURYSTHEUS",540,290,110,WHITE,a=fa(t,wt(3,"rival")-0.05,99,0.15,0.2)); label(img,"BORN AT 7 MONTHS",540,410,68,ORANGE,a=fa(t,wt(3,"born")-0.05,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
def night_bg(t,win_=True):
    b=panel(t,"dark",ox=300,oy=100,band=True); b*=np.array([0.7,0.8,1.15],np.float32)
    # moonlit window
    win=newm()
    if win_: cv2.rectangle(win,(300,440),(420,580),1.0,-1); cv2.circle(win,(360,440),60,1.0,-1); win=cv2.GaussianBlur(win,(0,0),6)
    b+=win[...,None]*np.array([0.18,0.26,0.5],np.float32)
    shaft=np.clip(1-np.abs((xx-360-(yy-500)*0.10)/(70+np.clip(yy-500,0,None)*0.25)),0,1)*np.clip((yy-480)/200,0,1)*np.exp(-np.clip(yy-500,0,None)/900)
    b+=shaft[...,None]*np.array([0.20,0.28,0.5],np.float32)*0.5
    return b
def sh_snakes(t,close=False):
    u=t-Ls(4); b=night_bg(t)
    m=newm(); cradle(m,360,860,420); baby_fig(m,360,815,130,0.0); relief(b,m,alb=MW_*np.array([0.75,0.82,1.0],np.float32),L=(-0.2,-0.9),strength=10,rim=(0.6,0.75,1.2),rim_a=0.5)
    e=sm((u+0.4)/3.2)
    for sg in (-1,1):
        x1=360+sg*lerp(420,125,e); y1=lerp(1000,790,e)
        serpent(b,spath(360+sg*560,1180,x1,y1,t,38,1.6,ph=sg*1.3),34,1.0)
    def hud(img):
        label(img,"8 MONTHS OLD",540,300,118,WHITE,a=fa(t,wt(4,"eight")-0.05,99,0.15,0.2))
        if close: label(img,"SENT BY HERA",540,420,76,ORANGE,a=fa(t,wt(4,"serpents")+0.1,99,0.15,0.2),stroke=6)
    return b,hud,(1.0+0.03*u) if not close else 1.28+0.05*(t-wt(4,"serpents"))
def sh_strangle(t):
    u=t-Ls(5); b=night_bg(t,False); fl=np.exp(-max(u,0)/0.25)
    rays(b,360,640,t,0.9*(0.5+0.5*fl),col=(1.0,0.75,0.35),fall=420); glow(b,360,640,200,(1.0,0.7,0.3),0.4+fl)
    m=newm(); baby_fig(m,360,900,330,1.0); relief(b,m,alb=MW_*0.95,L=(-0.3,-0.85),strength=10,rim=(1.0,0.75,0.35),rim_a=0.8)
    dec=math.exp(-max(u,0)*1.3)
    for sg in (-1,1):
        hx=360+sg*330*(0.30+0.22); hy=900-330*(0.45+0.45)
        pts=[(hx+sg*(10+i*9)+math.sin(i*0.5-t*8)*30*dec,hy-30+i*16) for i in range(40)][::-1]
        serpent(b,pts,30,0.6,eyes=dec>0.3)
    b+=fl*0.35
    def hud(img): label(img,"BARE HANDS",540,300,124,WHITE,a=fa(t,Ls(5)+0.1,99,0.15,0.2))
    return b,hud,1.0+0.03*u
def sh_alcides(t,phase=0):
    u=t-(Ls(6) if phase==0 else wt(6,"Alcaeus")); b=panel(t,ox=50,oy=700,sp=(0.5,0.5,420,640),tone=(0.72,0.70,0.72))
    m=newm(); cv2.rectangle(m,(70,450),(650,1000),1.0,-1); cv2.rectangle(m,(100,480),(620,970),0.8,-1)
    relief(b,m,alb=MW_*0.95,L=statue_light(t),strength=6,depth=3)
    if phase==0:
        tm=text_mask("ALCIDES",96,track=6); m=newm(); put(m,tm,360,600)
        front=-100+u*900; m*=np.clip((front-xx)/40,0,1)
        if 60<front<660:
            for k in range(6): glow(b,front+np.sin(t*50+k)*14,600+np.cos(t*37+k*2)*40,4,(2.0,1.4,0.6),0.8)
        relief(b,m,gold=True,depth=2.2,strength=7,shad=(3,5),shad_a=0.5,rim_a=0.0)
        m=newm(); put(m,text_mask("ΗΡΑΚΛΗΣ",58,track=4),360,470); relief(b,m*0.6,alb=MW_*0.7,depth=1.5,strength=6,shad_a=0.2)
        cv2.line(b,(200,470),(200+int(320*sm((t-wt(6,"wasn't"))/0.4)),470),(0.6,0.15,0.1),5,cv2.LINE_AA)
    else:
        m=newm(); put(m,text_mask("ALCIDES",70,track=5),360,500); put(m,text_mask("ALCAEUS",92,track=5),360,680)
        m[620:760]*=sm(u/0.35)
        relief(b,m,gold=True,depth=2.2,strength=7,shad=(3,5),shad_a=0.5,rim_a=0.0)
        m=newm(); put(m,text_mask("OR",48),360,590); relief(b,m,alb=MW_*0.7,depth=1.2,strength=5,shad_a=0.2)
    dust(b,t,0.35)
    def hud(img):
        label(img,"HIS BIRTH NAME",540,300,104,WHITE,a=fa(t,Ls(6)+0.05,99,0.15,0.2))
        if phase==1: label(img,"FROM HIS GRANDFATHER",540,415,62,ORANGE,a=fa(t,wt(6,"Alcaeus")+0.15,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.025*u
def crowd_mask(m,t,y0,n=26,seed=5):
    g=np.random.default_rng(seed)
    for i in range(n):
        x=g.uniform(-20,w+20); s=g.uniform(170,240); yb=y0+g.uniform(0,90)
        hero_fig(m,x,yb+s*0.05,s,1 if g.random()<0.5 else -1,pose="ascend" if g.random()<0.65 else "stand",club=False,lion=False,himation=True,t=t+i)
def sh_argos(t):
    u=t-Ls(7); b=olympus_bg(t,sun=(0.5,0.52),top=(0.16,0.14,0.34),bot=(1.0,0.62,0.32),ra=0.65,cl=False)
    clouds(b,t,h*0.08,h*0.35,6,1,0.5,thr=0.35)
    hill=np.array([(0,720),(120,640),(250,560),(470,540),(600,600),(w,660),(w,h),(0,h)],np.int32)
    m=newm(); cv2.fillPoly(m,[hill],1.0,cv2.LINE_AA); temple(m,360,560,250,120,6)
    relief(b,m,alb=MW_*np.array([0.42,0.36,0.38],np.float32),L=(0.0,0.9),strength=6,rim=(1.0,0.65,0.3),rim_a=1.2,shad_a=0.0)
    m=newm(); crowd_mask(m,t,1040); relief(b,m,alb=DARKA,L=(0.0,0.9),strength=8,rim=(1.0,0.6,0.25),rim_a=1.5,shad_a=0.0)
    dust(b,t,0.5)
    def hud(img):
        label(img,"VERSION 1",540,290,118,WHITE,a=fa(t,Ls(7)+0.05,99,0.15,0.2)); label(img,"ARGOS · DIODORUS",540,410,66,ORANGE,a=fa(t,wt(7,"Argos")-0.05,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
def sh_glory(t):
    u=t-wt(7,"serpents"); b=panel(t,"dark",ox=500,oy=200); rays(b,360,600,t,0.8,fall=420); glow(b,360,600,160,(1.0,0.7,0.3),0.5)
    m=newm(); wreath(m,360,600,190); relief(b,m,gold=True,depth=1.8,strength=8,shad=(5,8),rim_a=0.0)
    m=newm(); put(m,text_mask("ΚΛΕΟΣ",92,track=6),360,620); relief(b,m,gold=True,depth=2,strength=7,shad=(3,5),rim_a=0.0)
    for sg in (-1,1):
        pts=[(360+sg*(40+i*8),930+math.sin(i*0.35+sg)*22) for i in range(40)]
        serpent(b,pts,20,0.25,eyes=False)
    dust(b,t,0.6)
    def hud(img): label(img,"HER ATTACK",540,290,112,WHITE,a=fa(t,wt(7,"glory")-0.1,99,0.15,0.2)); label(img,"BECAME HIS FAME",540,410,74,ORANGE,a=fa(t,wt(7,"Hera")-0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
def sh_delphi(t):
    u=t-Ls(8); b=olympus_bg(t,sun=(0.75,0.40),top=(0.10,0.07,0.22),bot=(0.95,0.45,0.30),ra=0.45,cl=False)
    m=newm(); temple(m,430,700,420,230,6); cv2.rectangle(m,(0,760),(w,h),1.0,-1)
    relief(b,m,alb=MW_*np.array([0.55,0.45,0.48],np.float32),L=(0.6,-0.3),strength=6,rim=(1.0,0.6,0.3),rim_a=0.9,shad_a=0.0)
    # vapour from tripod
    off=int(t*40)%h; c=np.roll(CLD[1][:, :w],-off,0)
    col_=np.exp(-((xx-(250+np.sin(yy/90+t)*30))/(60+np.clip(900-yy,0,None)*0.25))**2)*np.clip((900-yy)/500,0,1)
    vap=np.clip(c*0.4+0.5,0,1)*col_; b+=vap[...,None]*np.array([0.45,0.55,0.45],np.float32)*0.55
    m=newm(); tripod(m,250,1010,280); relief(b,m,gold=True,depth=1.8,strength=8,shad=(4,6),rim_a=0.0)
    m=newm(); robe_fig(m,450,1050,470,-1,veil=True,arm="out"); relief(b,m,alb=MW_*0.85,L=(0.6,-0.6),strength=10,rim=(1.0,0.6,0.3),rim_a=0.7)
    glow(b,250,700,90,(0.6,0.9,0.6),0.25)
    dust(b,t,0.4)
    def hud(img):
        label(img,"VERSION 2",540,290,118,WHITE,a=fa(t,Ls(8)+0.05,99,0.15,0.2)); label(img,"THE PYTHIA AT DELPHI",540,410,64,ORANGE,a=fa(t,wt(8,"oracle")-0.05,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
CRACKS=[]
_g=np.random.default_rng(795)
for k in range(9):
    x,y=_g.uniform(80,640),_g.uniform(500,1150); a=_g.uniform(0,6.28); pts=[(x,y)]
    for i in range(14): a+=_g.normal(0,0.5); x+=math.cos(a)*28; y+=math.sin(a)*28; pts.append((x,y))
    CRACKS.append(np.array(pts,np.int32))
def sh_madness(t):
    u=t-Ls(9); b=panel(t,"dark",ox=600,oy=400,band=True)*np.array([1.0,0.75,0.9],np.float32)
    b+=sky((0.05,0.0,0.06),(0.25,0.04,0.10),0,1)*0.6
    pul=0.6+0.4*math.sin(t*5)
    lay=newm()
    for c in CRACKS: cv2.polylines(lay,[c],False,1.0,2,cv2.LINE_AA)
    lay*=sm(u/0.6); b+=(lay+cv2.GaussianBlur(lay,(0,0),5)*2.5)[...,None]*np.array([1.0,0.25,0.12],np.float32)*pul*0.8
    feather(b,360,370,1.05,0,0.9*sm(u/0.5),0.3*math.sin(t*4))
    glow(b,360,365,60,(0.3,0.5,1.5),0.6*pul)
    m=newm(); hero_fig(m,360,1150,520,1,pose="grief",club=False); relief(b,m,alb=MW_*np.array([0.85,0.75,0.8],np.float32),L=(0.0,-0.9),strength=10,rim=(1.0,0.25,0.15),rim_a=1.0)
    def hud(img): label(img,"THE DARKEST CHAPTER",540,290,76,WHITE,a=fa(t,Ls(9)+0.05,99,0.15,0.2))
    return b,hud,1.0+0.035*u
NUM=["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII"]
def sh_labours(t,close=False):
    u=t-Ls(10); b=panel(t,ox=700,oy=50,sp=(0.5,0.52,420,600)); rot=t*0.15
    m=newm(); hero_fig(m,360,1050,540,1); relief(b,m,alb=MW_*0.95,L=statue_light(t),strength=10)
    n_on=int(np.clip((t-wt(10,"Twelve"))/0.09,0,12))
    m=newm()
    for i in range(12):
        if i>=n_on: continue
        a=rot+i*2*math.pi/12; x=360+math.cos(a)*285; y=720+math.sin(a)*330
        cv2.circle(m,(int(x),int(y)),44,1.0,-1,cv2.LINE_AA); cv2.circle(m,(int(x),int(y)),36,0.85,2,cv2.LINE_AA)
        tm=text_mask(NUM[i],34); mm=newm(); put(mm,tm,x,y+2); m=np.where(mm>0.3,0.8,m)
    relief(b,m,gold=True,depth=2,strength=8,shad=(4,7),rim_a=0.0)
    dust(b,t,0.45)
    def hud(img):
        if not close:
            label(img,"12 YEARS",540,290,124,WHITE,a=fa(t,wt(10,"Twelve")-0.05,99,0.15,0.2)); label(img,"SERVING HIS RIVAL",540,410,70,ORANGE,a=fa(t,wt(10,"service")-0.05,99,0.15,0.2),stroke=6)
        else: label(img,"THE 12 LABOURS",540,300,110,WHITE,a=fa(t,wt(10,"famous")-0.05,99,0.15,0.2))
    return b,hud,(1.0+0.02*u) if not close else 1.10+0.04*(t-wt(10,"famous"))
def sh_olympus(t):
    u=t-Ls(11); b=olympus_bg(t,sun=(0.5,0.33),top=(0.10,0.12,0.32),bot=(0.80,0.50,0.40),ra=0.7)
    m=newm(); temple(m,360,560,330,150,6); relief(b,m,alb=MW_*0.95,L=(0,-0.9),strength=7,rim=(1.0,0.8,0.4),rim_a=0.9,shad_a=0.0); glow(b,360,470,150,(1.0,0.8,0.4),0.35)
    clouds(b,t,h*0.44,h*0.56,10,1,0.85,dens=1.4,thr=0.0)
    y=lerp(1300,1100,eout(u/3)); m=newm(); hero_fig(m,360,y,470,1,pose="ascend",t=t)
    relief(b,m,alb=DARKA*2.2,L=(-0.6,-0.5),strength=12,rim=(1.0,0.75,0.35),rim_a=2.2,glowa=0.6,shad_a=0.0,amb=0.4)
    clouds(b,t,h*0.80,h*1.2,20,0,0.95,dens=1.5,thr=-0.1)
    dust(b,t,0.6)
    def hud(img): label(img,"MOUNT OLYMPUS",540,290,104,WHITE,a=fa(t,wt(11,"Olympus")-0.1,99,0.15,0.2)); label(img,"NOW A GOD",540,410,80,ORANGE,a=fa(t,wt(11,"god")-0.05,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
def sh_peace(t):
    u=t-wt(11,"Hera"); b=olympus_bg(t,sun=(0.5,0.45),top=(0.14,0.12,0.34),bot=(1.0,0.70,0.45),ra=0.7)
    fan(b,500,640,220,n=11,spread=170,sc=0.5,t=t,open_=0.3+0.7*eout(u/0.9))
    m=newm(); robe_fig(m,500,1080,540,-1,crown=True,veil=True,arm="out"); relief(b,m,alb=MW_*0.95,L=(-0.2,-0.6),strength=10,rim=(1.0,0.72,0.35),rim_a=1.0,shad_a=0.0)
    m=newm(); hero_fig(m,225,1080,560,1,pose="reach"); relief(b,m,alb=MW_*0.95,L=(0.2,-0.6),strength=10,rim=(1.0,0.72,0.35),rim_a=1.0,shad_a=0.0)
    glow(b,365,660,40,(2.0,1.5,0.8),0.7+0.2*math.sin(t*4)); glow(b,365,660,140,(0.8,0.5,0.2),0.4)
    clouds(b,t,h*0.86,h*1.2,20,0,0.95,dens=1.5,thr=-0.1)
    dust(b,t,0.6)
    def hud(img): label(img,"ENEMIES NO MORE",540,300,96,WHITE,a=fa(t,wt(11,"peace")-0.15,99,0.15,0.2))
    return b,hud,1.0+0.03*u
def sh_adopt(t):
    u=t-Ls(12); b=panel(t,ox=350,oy=600,sp=(0.48,0.5,420,600),tone=(0.66,0.62,0.66))
    fan(b,300,640,230,n=9,spread=150,sc=0.5,t=t,a=0.85)
    m=newm(); robe_fig(m,300,1080,640,1,crown=True,veil=True,arm="out"); relief(b,m,alb=MW_*0.95,L=statue_light(t),strength=10)
    m=newm(); hero_fig(m,440,1090,500,-1,pose="stand",club=False); relief(b,m,alb=MW_*np.array([1.0,0.96,0.9],np.float32),L=statue_light(t),strength=10,shad=(10,14),shad_a=0.6)
    glow(b,380,700,200,(1.0,0.7,0.35),0.3+0.15*sm(u/1.5))
    dust(b,t,0.5)
    def hud(img): label(img,"ADOPTED BY HERA",540,290,96,WHITE,a=fa(t,wt(12,"adopted")-0.1,99,0.15,0.2)); label(img,"DIODORUS, BOOK 4",540,410,62,ORANGE,a=fa(t,wt(12,"adopted")+0.2,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
def sh_hebe(t):
    u=t-wt(12,"married"); b=olympus_bg(t,sun=(0.5,0.38),top=(0.16,0.12,0.30),bot=(1.0,0.75,0.50),ra=0.8)
    fan(b,360,560,260,n=13,spread=200,sc=0.45,t=t,a=0.85)
    m=newm(); wreath(m,360,470,95); relief(b,m,gold=True,depth=1.5,strength=8,shad_a=0.0,rim_a=0.0); glow(b,360,470,70,(1.0,0.75,0.35),0.5)
    m=newm(); hero_fig(m,220,1080,560,1,pose="reach",club=False); relief(b,m,alb=MW_*0.95,L=(0.2,-0.6),strength=10,rim=(1.0,0.72,0.35),rim_a=1.0,shad_a=0.0)
    m=newm(); robe_fig(m,500,1080,500,-1,cup=True,veil=True,arm="out"); relief(b,m,alb=MW_*np.array([1.0,0.95,0.92],np.float32),L=(-0.2,-0.6),strength=10,rim=(1.0,0.72,0.35),rim_a=1.0,shad_a=0.0)
    clouds(b,t,h*0.86,h*1.2,20,0,0.95,dens=1.5,thr=-0.1)
    dust(b,t,0.9)
    def hud(img): label(img,"HEBE",540,290,124,WHITE,a=fa(t,wt(12,"Hebe")-0.1,99,0.15,0.2)); label(img,"GODDESS OF YOUTH",540,410,70,ORANGE,a=fa(t,wt(12,"Hebe")+0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
def sh_rome(t):
    u=t-Ls(13); b=panel(t,ox=150,oy=900,sp=(0.5,0.5,420,600),tone=(0.74,0.72,0.74))
    m=newm(); wreath(m,360,580,215,n=15); relief(b,m,alb=MW_*0.9,depth=1.8,strength=8,shad=(4,6))
    m=newm(); put(m,text_mask("ΗΡΑΚΛΗΣ",52,track=6),360,335); relief(b,m*(1-0.5*sm(u/1.0)),alb=MW_*0.7,depth=1.5,strength=6,shad_a=0.2)
    m=newm(); put(m,text_mask("HERCVLES",76,font="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",track=4),360,585); m*=np.clip((-60+u*900-xx)/50,0,1)
    relief(b,m,gold=True,depth=2.2,strength=7,shad=(3,5),shad_a=0.5,rim_a=0.0)
    g=cv2.GaussianBlur(m,(0,0),8); b+=g[...,None]*np.array([0.5,0.32,0.1],np.float32)*0.6
    dust(b,t,0.4)
    def hud(img): label(img,"IN LATIN:",540,300,96,WHITE,a=fa(t,Ls(13)+0.05,99,0.15,0.2)); label(img,"HERCULES",540,415,80,ORANGE,a=fa(t,wt(13,"Hercules")-0.05,TOTAL-0.75,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
def sh_end(t): return sh_hook(t,end=True)
def Z(fn,zf,*a):
    def f(t):
        b,hud,z=fn(t,*a); return b,hud,z*zf
    return f
SHOTS=[(0.0,sh_hook,"cut"),(wt(0,"goddess")-0.05,lambda t:sh_hook(t,close=True),"cut"),
 (Ls(1)-0.25,lambda t:sh_name(t,0),"iris"),(wt(1,"glory")-0.1,lambda t:sh_name(t,1),"cut"),
 (Ls(2)-0.15,sh_zeus,"cut"),(wt(2,"Heracles")-0.1,sh_alcmene,"cut"),(wt(2,"Alcmene")-0.1,Z(sh_alcmene,1.2),"cut"),
 (Ls(3)-0.15,sh_iliad,"cut"),(wt(3,"rival")-0.1,sh_rival,"cut"),
 (Ls(4)-0.25,sh_snakes,"iris"),(wt(4,"serpents")-0.1,lambda t:sh_snakes(t,True),"cut"),(Ls(5)-0.1,sh_strangle,"cut"),
 (Ls(6)-0.25,lambda t:sh_alcides(t,0),"iris"),(wt(6,"Alcides")-0.1,Z(sh_alcides,1.12,0),"cut"),(wt(6,"Alcaeus")-0.1,lambda t:sh_alcides(t,1),"cut"),
 (Ls(7)-0.15,sh_argos,"cut"),(wt(7,"renamed")-0.1,Z(sh_argos,1.22),"cut"),(wt(7,"serpents")-0.1,sh_glory,"cut"),
 (Ls(8)-0.25,sh_delphi,"iris"),(Ls(9)-0.1,sh_madness,"cut"),(wt(9,"cost")-0.1,Z(sh_madness,1.2),"cut"),
 (Ls(10)-0.15,sh_labours,"cut"),(wt(10,"famous")-0.1,lambda t:sh_labours(t,True),"cut"),
 (Ls(11)-0.25,sh_olympus,"iris"),(wt(11,"Hera")-0.1,sh_peace,"cut"),
 (Ls(12)-0.15,sh_adopt,"cut"),(wt(12,"married")-0.1,sh_hebe,"cut"),
 (Ls(13)-0.15,sh_rome,"cut"),(TOTAL-0.95,sh_end,"iris")]
TR=0.25
def shot_at(t):
    i=0
    for k,s in enumerate(SHOTS):
        if t>=s[0]: i=k
    return i
def render_shot(i,t):
    b,hud,z=SHOTS[i][1](t); st=SHOTS[i][0]
    z*=punch(t,[st] if i>0 and SHOTS[i][2]=="cut" else [],0.06,0.32)
    dx,dy=shake(t,Ls(5),9,0.45); d2=shake(t,Ls(9),5,0.6); dx+=d2[0]; dy+=d2[1]
    dx+=3*math.sin(t*0.7); dy+=2*math.cos(t*0.5)
    cy=0.40 if SHOTS[i][1] is not None and z>1.15 else 0.47
    return camera(b,z,0.5,cy,dx,dy),hud
# ---- peacock-eye iris transition ----
ICX,ICY=w*0.5,h*0.47
IDN=np.sqrt(((xx-ICX))**2+((yy-ICY)/1.3)**2).astype(np.float32); IANG=np.arctan2(yy-ICY,xx-ICX).astype(np.float32)
IRMAX=float(IDN.max())*1.08
RINGS=[(0.0,np.array([0.04,0.10,0.48],np.float32)*1.3),(0.28,np.array([0.04,0.42,0.44],np.float32)*1.15),(0.54,np.array([0.50,0.30,0.09],np.float32)),(0.74,np.array([1.0,0.76,0.32],np.float32)*1.25),(1.0,None)]
BARB=((0.5+0.5*np.sin(IANG*140))**6).astype(np.float32)
def peacock_iris(b1,b2,u):
    e=sm(u)**1.3; R=e*IRMAX; W_=14+0.13*R
    de=IDN-R*(1+0.012*np.sin(IANG*26+u*3)+0.015*np.sin(IANG*7-u*5))
    x=de/W_
    out=np.where((de<0)[...,None],b2,b1)
    band=np.zeros_like(b1); ba=np.zeros((h,w),np.float32)
    for (x0,c),(x1,_) in zip(RINGS,RINGS[1:]):
        k=sm_np((x-x0)/0.06)*(1-sm_np((x-x1)/0.06)); band+=k[...,None]*c; ba+=k
    ba=np.clip(ba,0,1)*(de>=0)
    out=out*(1-ba[...,None]*0.95)+band*0.95
    barb=BARB*np.exp(-np.clip(x-1,0,None)*3.0)*(x>0.9)*0.35
    out+=barb[...,None]*np.array([0.8,0.75,0.3],np.float32)
    rimg=np.exp(-((de)/6)**2)*0.9; out+=rimg[...,None]*np.array([1.0,0.85,0.5],np.float32)
    return out
def compose(t,fi=None):
    if fi is None: fi=int(round(t*30))
    i=shot_at(max(t,0)); nxt=SHOTS[i+1] if i+1<len(SHOTS) else None; huds=[]
    if nxt and nxt[2]=="iris" and t>nxt[0]-TR:
        u=(t-(nxt[0]-TR))/(2*TR); b1,h1=render_shot(i,t); b2,h2=render_shot(i+1,t); b=peacock_iris(b1,b2,u); huds=[h1] if u<0.3 else []
    elif SHOTS[i][2]=="iris" and t<SHOTS[i][0]+TR and i>0:
        u=(t-(SHOTS[i][0]-TR))/(2*TR); b1,h1=render_shot(i-1,t); b2,h2=render_shot(i,t); b=peacock_iris(b1,b2,u); huds=[h2] if u>0.75 else []
    else:
        b,h1=render_shot(i,t); huds=[h1]
    b=post(b,bloom=0.5,thr=0.70,tint=(1.03,1.0,0.95))
    img=to_img(b,fi)
    for hf in huds:
        if hf: hf(img)
    ha=1-sm((t-(Ls(1)-0.45))/0.25) if t<Ls(1) else sm((t-(TOTAL-0.55))/0.3)
    if ha>0.01:
        hook_title(img,[("NAMED AFTER",WHITE)],a=ha,y=250,size=124)
        s2=wt(0,"tried")-0.05
        if t>=s2 or t>TOTAL-0.55:
            a2=ha*(sm((t-s2)/0.08) if t<Ls(1) else 1.0); sc=0.7+0.3*spring((t-s2)/0.22) if t<Ls(1) else 1.0
            hook_title(img,[("HIS ENEMY",ORANGE)],a=a2,y=390,size=150,sc=sc)
    return finish(img,CAP,t)
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
