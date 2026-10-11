import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid56")
for p in ["/home/claude/vid56","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial import cKDTree
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= Roman mosaic (opus tessellatum) =================
# palette of stone / glass tesserae
PAL=np.array([
 (0.10,0.09,0.08),(0.24,0.23,0.24),(0.46,0.47,0.50),(0.70,0.69,0.66),(0.92,0.88,0.79),(0.97,0.95,0.90),
 (0.42,0.27,0.15),(0.60,0.42,0.22),(0.78,0.60,0.33),(0.93,0.80,0.48),
 (0.68,0.33,0.20),(0.47,0.16,0.12),(0.86,0.62,0.52),
 (0.30,0.46,0.60),(0.52,0.66,0.74),(0.18,0.30,0.42),
 (0.46,0.55,0.36),(0.25,0.35,0.23),(0.98,0.70,0.25)],np.float32)
CREAM=(0.92,0.88,0.79); WHITE=(0.97,0.95,0.90); BLACK=(0.10,0.09,0.08); RED=(0.68,0.33,0.20); DRED=(0.47,0.16,0.12)
OCHRE=(0.78,0.60,0.33); SEA=(0.30,0.46,0.60); SEAL=(0.52,0.66,0.74); SAGE=(0.46,0.55,0.36); DGREEN=(0.25,0.35,0.23)
GOLD=(0.93,0.80,0.48); FLAME=(0.98,0.70,0.25); GREY=(0.46,0.47,0.50); LGREY=(0.70,0.69,0.66); BRN=(0.42,0.27,0.15)
PITCH=6.4
_cache="mos_cache.npz"
if os.path.exists(_cache):
    z=np.load(_cache); PTS=z["PTS"]; LC=z["LC"]; LF=z["LF"]; GAP=z["GAP"]; OFX=z["OFX"]; OFY=z["OFY"]
else:
    rg=np.random.default_rng(56); pts=[]
    for j in range(int(h/PITCH)+3):
        off=PITCH*0.5*(j%2)
        for i in range(-1,int(w/PITCH)+3): pts.append((i*PITCH+off+rg.uniform(-1.2,1.2),j*PITCH+rg.uniform(-1.0,1.0)-PITCH*0.5))
    PTS=np.array(pts,np.float32); tr=cKDTree(PTS)
    q=np.stack([xx.ravel()+0.5,yy.ravel()+0.5],-1); _,LC=tr.query(q); LC=LC.reshape(h,w).astype(np.int32)
    YF,XF=np.mgrid[0:H,0:W].astype(np.float32); q=np.stack([(XF.ravel()+0.5)/2,(YF.ravel()+0.5)/2],-1)
    dd,ii=tr.query(q,k=2); LF=ii[:,0].reshape(H,W).astype(np.int32); GAP=(dd[:,1]-dd[:,0]).reshape(H,W).astype(np.float32)
    OFX=(q[:,0]-PTS[ii[:,0],0]).reshape(H,W).astype(np.float32); OFY=(q[:,1]-PTS[ii[:,0],1]).reshape(H,W).astype(np.float32)
    np.savez(_cache,PTS=PTS,LC=LC,LF=LF,GAP=GAP,OFX=OFX,OFY=OFY)
K=len(PTS); LCr=LC.ravel(); CNT=np.maximum(np.bincount(LCr,minlength=K),1).astype(np.float32); LFr=LF.ravel()
_rt=np.random.default_rng(7); TVAR=(_rt.uniform(0.92,1.05,(K,1))*(1+_rt.normal(0,0.015,(K,3)))).astype(np.float32)
_gin=np.clip((GAP-0.30)/0.45,0,1); _gin=_gin*_gin*(3-2*_gin)
_bev=1-0.085*(OFX+OFY)/PITCH-0.20*np.exp(-GAP/0.55)
_sn=cv2.GaussianBlur(np.random.default_rng(3).normal(0,1,(H,W)).astype(np.float32),(0,0),1.0); _sn/=_sn.std()
_ly,_lx=np.mgrid[0:H,0:W].astype(np.float32)
_light=(1.04-0.10*((_lx/W-0.3)**2+(_ly/H-0.35)**2))
SHADE=((_bev*(1+0.035*_sn))*_light*_gin)[...,None].astype(np.float32)
GROUT=((1-_gin)*_light*(0.40+0.03*_sn))[...,None]*np.array((1.0,0.95,0.86),np.float32)
TCX=PTS[:,0]; TCY=PTS[:,1]
def tiles(buf):
    """average the base painting per tessera, snap to the stone palette"""
    f=buf.reshape(-1,3)
    c=np.stack([np.bincount(LCr,weights=f[:,k],minlength=K) for k in range(3)],-1).astype(np.float32)/CNT[:,None]
    d=((c[:,None,:]-PAL[None,:,:])**2).sum(-1); return PAL[np.argmin(d,1)]
def paint(cols):
    img=(cols*TVAR)[LFr].reshape(H,W,3)*SHADE+GROUT
    return np.clip(img,0,1)
_rd=np.random.default_rng(12).uniform(0,1,K).astype(np.float32)
DLY=np.clip((TCX/w*0.35+TCY/h*0.65)*0.72+_rd*0.28,0,1)
def flip(c1,c2,u):
    """every tessera turns over one by one (diagonal sweep) to reveal the next picture"""
    ut=np.clip((u-DLY*0.62)/0.38,0,1)[:,None]
    c=np.where(ut<0.5,c1,c2); br=0.30+0.70*np.abs(np.cos(math.pi*ut)); gl=np.sin(math.pi*ut)*0.35
    return c*br+np.array(GOLD,np.float32)*gl*(1-br)
# ================= fonts / HUD =================
_IF={}
def _f(s,var="Bold"):
    k=(s,var)
    if k not in _IF:
        f=ImageFont.truetype("/home/claude/vid56/Cinzel.ttf",s); f.set_variation_by_name(var); _IF[k]=f
    return _IF[k]
cCR=(244,234,212); cDR=(122,34,24); cGD=(236,196,110)
def plaque(d,s,x,y,fs=78,a=1.0,sc=1.0):
    """tabula ansata: Roman inscription plaque with dovetail handles"""
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f(n,"Black")
    while f.getlength(s)>820*sc and n>20: n-=4; f=_f(n,"Black")
    bb=d.textbbox((0,0),s,font=f,anchor="lt"); tw=f.getlength(s); th=n*0.78
    px,py=n*0.55,n*0.42; x0,x1=x-tw/2-px,x+tw/2+px; y0,y1=y-th/2-py,y+th/2+py; e=(y1-y0)*0.55
    A=int(255*a)
    for dx,dy,al in ((10,12,90),):
        d.polygon([(x0+dx,y0+dy),(x1+dx,y0+dy),(x1+e+dx,y0+dy-6),(x1+e+dx,y1+dy+6),(x1+dx,y1+dy),(x0+dx,y1+dy),(x0-e+dx,y1+dy+6),(x0-e+dx,y0+dy-6)],fill=(20,12,8,int(al*a)))
    poly=[(x0,y0),(x1,y0),(x1+e,y0-6),(x1+e*0.25,(y0+y1)/2),(x1+e,y1+6),(x1,y1),(x0,y1),(x0-e,y1+6),(x0-e*0.25,(y0+y1)/2),(x0-e,y0-6)]
    d.polygon(poly,fill=(240,230,208,A),outline=cDR+(A,),width=5)
    d.rectangle((x0+9,y0+9,x1-9,y1-9),outline=cDR+(int(150*a),),width=2)
    d.text((x,y+n*0.04),s,font=f,fill=cDR+(A,),anchor="mm")
def tag(d,s,x,y,fs=38,a=1.0,sc=1.0,bg=(122,34,24),fg=cCR):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f(n,"Bold"); tw=f.getlength(s); px,py=n*0.55,n*0.40
    d.rectangle((x-tw/2-px+6,y-n*0.5-py+8,x+tw/2+px+6,y+n*0.5+py+8),fill=(20,12,8,int(90*a)))
    d.rectangle((x-tw/2-px,y-n*0.5-py,x+tw/2+px,y+n*0.5+py),fill=bg+(int(235*a),),outline=fg+(int(220*a),),width=3)
    d.text((x,y),s,font=f,fill=fg+(int(255*a),),anchor="mm")
def lab(d,s,x,y,fs=34,a=1.0,col=cCR):
    if a<=0.01: return
    d.text((x,y),s,font=_f(fs,"Bold"),fill=col+(int(255*a),),anchor="mm",stroke_width=4,stroke_fill=(30,18,10,int(230*a)))
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= painting helpers (base image, before tessellation) =================
def fill(buf,m,col,a=1.0): comp(buf,m,col,sh=0,rim=0,a=a)
def border(buf):
    """classic mosaic frame: black edge, chequer band, red fillet"""
    m=M().rect(0,0,w,14); m.rect(0,h-14,w,h); m.rect(0,0,14,h); m.rect(w-14,0,w,h); fill(buf,m,BLACK)
    m=M(); cs=14
    for k in range(int(w/cs)+1):
        if k%2==0: m.rect(14+k*cs,14,14+k*cs+cs,28); m.rect(14+k*cs,h-28,14+k*cs+cs,h-14)
    for k in range(int(h/cs)+1):
        if k%2==0: m.rect(14,14+k*cs,28,14+k*cs+cs); m.rect(w-28,14+k*cs,w-14,14+k*cs+cs)
    fill(buf,m,BLACK)
    m=M().rect(34,34,w-34,40); m.rect(34,h-40,w-34,h-34); m.rect(34,34,40,h-34); m.rect(w-40,34,w-34,h-34); fill(buf,m,RED)
    subband(buf)
def subband(buf):
    """dark inscription register behind the subtitles"""
    fill(buf,M().rect(40,676,w-40,h-40),(0.18,0.16,0.16)); fill(buf,M().rect(40,670,w-40,676),RED)
    for x in range(64,w-50,34): fill(buf,M().poly([(x,846),(x+8,838),(x+16,846),(x+8,854)]),(0.47,0.16,0.12))
def bg(col=CREAM):
    b=np.empty((h,w,3),np.float32); b[:]=col; return b
# ---- 3-D dodecahedron ----
PHI=(1+5**0.5)/2
VERT=[(x,y,z) for x in (-1,1) for y in (-1,1) for z in (-1,1)]
for a_ in (-1,1):
    for b_ in (-1,1): VERT+=[(0,a_/PHI,b_*PHI),(a_/PHI,b_*PHI,0),(a_*PHI,0,b_/PHI)]
VERT=np.array(VERT,np.float32)
from scipy.spatial import ConvexHull
_hull=ConvexHull(VERT); FACES=[]; _seen=[]
for eq in _hull.equations:
    n=eq[:3].astype(np.float32); n/=np.linalg.norm(n)
    if any(abs(float(n@m)-1)<1e-4 for m in _seen): continue
    _seen.append(n); idx=[i for i in range(20) if abs(float(VERT[i]@n)+eq[3])<1e-4]
    c=VERT[idx].mean(0); u=VERT[idx[0]]-c; u/=np.linalg.norm(u); v=np.cross(n,u)
    an=[math.atan2((VERT[i]-c)@v,(VERT[i]-c)@u) for i in idx]; FACES.append((n,[idx[k] for k in np.argsort(an)]))
assert len(FACES)==12 and all(len(f[1])==5 for f in FACES), len(FACES)
HOLE=[0.20,0.46,0.30,0.38,0.24,0.52,0.34,0.27,0.44,0.22,0.36,0.30]
LDIR=np.array((-0.45,-0.62,0.64),np.float32); LDIR/=np.linalg.norm(LDIR)
def rotm(yaw,pitch,roll=0.0):
    cy,sy=math.cos(yaw),math.sin(yaw); cp,sp=math.cos(pitch),math.sin(pitch); cr,sr=math.cos(roll),math.sin(roll)
    Ry=np.array(((cy,0,sy),(0,1,0),(-sy,0,cy)),np.float32); Rx=np.array(((1,0,0),(0,cp,-sp),(0,sp,cp)),np.float32); Rz=np.array(((cr,-sr,0),(sr,cr,0),(0,0,1)),np.float32)
    return Rz@Rx@Ry
def dodeca(buf,cx,cy,sz,yaw,pitch,roll=0.0,hl_face=0.0,hl_hole=0.0,hl_knob=0.0,t=0.0,shadow=True,glow=0.0):
    """bronze Roman dodecahedron: 12 pentagon faces, a different-sized hole in each, a knob on every corner"""
    R=rotm(yaw,pitch,roll); V=VERT@R.T; s=sz/1.75
    P2=lambda p:(cx+p[0]*s,cy+p[1]*s)
    if shadow: fill(buf,M().ell(cx+sz*0.10,cy+sz*1.30,sz*1.05,sz*0.20),(0.70,0.65,0.56),0.9)
    if glow>0: fill(buf,M().circ(cx,cy,sz*1.45),GOLD,0.35*glow)
    def knob(p,front):
        k=0.18*s; q=p*1.07; x,y=P2(q); fill(buf,M().circ(x,y,k),(0.36,0.24,0.12) if not front else (0.52,0.36,0.18))
        if front:
            fill(buf,M().circ(x-k*0.25,y-k*0.30,k*0.55),(0.74,0.55,0.30))
            if hl_knob>0: fill(buf,M().circ(x,y,k*1.05),GOLD,hl_knob)
    for i in range(20):
        if V[i,2]<0: knob(V[i],False)
    order=sorted(range(12),key=lambda i:(R@FACES[i][0])[2])
    for fi in order:
        n=R@FACES[fi][0]
        if n[2]<=0.02: continue
        ids=FACES[fi][1]; pts=[P2(V[i]) for i in ids]
        l=max(0.0,float(n@LDIR)); col=lerpc((0.36,0.24,0.12),(0.80,0.60,0.33),0.15+0.85*l)
        if l>0.93: col=lerpc(col,GOLD,0.6)
        hk=cl((t-(hl_face+fi*0.07))/0.12)*(1-cl((t-(hl_face+fi*0.07)-0.35)/0.2)) if hl_face>0 else 0.0
        if hk>0: col=lerpc(col,GOLD,hk)
        m=M().poly(pts); fill(buf,m,col)
        c=V[ids].mean(0); u=V[ids[0]]-c; u/=np.linalg.norm(u); v=np.cross(n,u)
        r=HOLE[fi]*0.85; ring=[P2(c+r*(math.cos(a)*u+math.sin(a)*v)) for a in np.linspace(0,2*math.pi,28,endpoint=False)]
        fill(buf,M().poly(ring),(0.40,0.28,0.15) if hl_hole<=0 else lerpc((0.40,0.28,0.15),GOLD,hl_hole))
        inner=[P2(c+r*0.8*(math.cos(a)*u+math.sin(a)*v)-n*0.10) for a in np.linspace(0,2*math.pi,28,endpoint=False)]
        fill(buf,M().poly(inner),(0.12,0.08,0.06))
        cv2.polylines(buf,[np.round(np.array(pts)*16).astype(np.int32)],True,(0.20,0.13,0.07),3,cv2.LINE_AA,4)
    for i in range(20):
        if V[i,2]>=0: knob(V[i],True)
# ---- map ----
MX0,MX1,MY0,MY1=40,500,140,560
def LL(lon,lat): return (MX0+(lon+11)*(MX1-MX0)/34.0, MY0+(58-lat)*(MY1-MY0)/16.0)
def lp_(pts): return [LL(*p) for p in pts]
CONT=[(-9.3,43.2),(-8,43.7),(-5.5,43.5),(-1.8,43.4),(-1.2,46.0),(-2.2,47.2),(-4.7,48.4),(-3.0,48.8),(-1.6,48.7),(-1.3,49.7),(0.2,49.5),(1.6,50.2),(1.6,50.9),(2.5,51.1),(3.6,51.4),(4.2,51.9),(4.8,53.0),(6.0,53.45),(7.0,53.6),(8.6,53.9),(8.6,55.0),(8.1,56.8),(10.5,57.7),(10.6,56.5),(10.2,55.6),(9.8,55.0),(10.9,54.0),(12.4,54.3),(14.0,54.0),(18.5,54.8),(19.9,54.5),(21.2,55.2),(21.0,56.8),(21.6,57.6),(24,57.4),(24,40),(-9.5,40)]
SWE=[(12.5,56.2),(12.9,55.4),(14.3,55.5),(16.0,56.2),(16.6,57.9),(16.5,59),(11.2,59),(11.8,57.6)]
GB=[(-5.7,50.0),(-3.5,50.3),(1.4,51.2),(1.7,52.6),(0.2,53.5),(-0.5,54.5),(-1.6,55.6),(-2.0,56.0),(-1.8,57.6),(-3.0,58.6),(-5.0,58.6),(-6.2,57.5),(-5.6,56.3),(-4.9,55.0),(-3.0,54.9),(-3.4,54.3),(-3.0,53.4),(-4.6,53.3),(-4.2,52.3),(-5.3,51.8),(-3.0,51.4),(-4.2,51.2)]
IRL=[(-6.0,52.2),(-6.2,53.5),(-5.9,54.6),(-7.3,55.3),(-8.5,54.5),(-10.0,54.0),(-9.8,52.2),(-10.3,51.6),(-8.0,51.6)]
MED=[(3.0,40),(3.2,43.3),(4.0,43.5),(4.8,43.4),(6.0,43.1),(7.0,43.6),(8.8,44.4),(10.2,43.9),(10.5,42.9),(11.5,42.3),(12.5,41.5),(13.5,40)]
ADR=[(14.6,41.0),(14.0,41.9),(13.6,43.5),(12.4,44.2),(12.3,45.4),(13.8,45.7),(14.5,45.2),(15.2,44.3),(15.9,43.5),(17.5,43.0),(19.4,41.9),(19.6,41.0)]
COR=[(9.4,43.0),(9.6,42.5),(9.5,41.4),(8.6,41.8),(8.7,42.6)]
BARB=[(4.1,51.9),(6.1,51.85),(6.8,51.4),(6.95,50.94),(7.6,50.36),(8.3,50.3),(8.8,50.45),(9.5,49.8),(9.6,49.0),(10.5,49.0),(12.1,49.0),(13.5,48.6),(14.3,48.3),(16.4,48.2),(17.1,48.1),(18.9,47.8),(19.04,47.5),(18.9,46.0),(19.5,45.3),(21.0,44.8),(24,44.6),(24,60),(4.0,60)]
SCOT=[(-8,55.2),(-2.5,55.2),(-1.5,55.4),(0,56),(0,60),(-8,60)]
RHINE=[(4.1,51.9),(6.1,51.85),(6.8,51.4),(6.95,50.94),(7.6,50.36),(8.27,50.0),(8.4,49.0),(7.75,48.6),(7.6,47.6),(9.0,47.65)]
DANUBE=[(8.5,48.0),(10.0,48.4),(12.1,49.0),(13.5,48.6),(14.3,48.3),(16.4,48.2),(17.1,48.1),(18.9,47.8),(19.04,47.5),(18.9,46.0),(19.5,45.3),(21.0,44.8),(23,44.6)]
FINDS=[(-1.6,54.9),(-1.1,53.96),(-2.2,53.0),(-1.5,52.0),(0.9,51.9),(-0.1,51.5),(-2.4,51.4),(-3.0,51.6),(-1.3,51.0),(0.1,52.2),(-2.7,53.8),(-0.67,53.12),
 (2.3,48.9),(3.0,50.6),(4.8,50.5),(5.6,50.6),(6.1,49.6),(6.6,49.75),(4.0,49.3),(2.8,49.4),(1.1,49.4),(-0.4,49.2),(3.1,45.8),(4.8,45.75),(5.0,47.3),(6.0,47.2),(1.9,47.9),(0.7,47.4),(-1.5,47.2),(3.9,43.6),(4.4,44.0),(6.2,48.7),(7.75,48.6),(5.0,51.9),(5.9,51.8),(4.3,52.0),(3.7,51.1),
 (6.95,50.94),(7.6,50.36),(8.27,50.0),(8.5,49.5),(6.1,50.8),(7.1,50.7),(9.0,48.8),(10.9,48.4),(12.1,49.0),(7.4,46.9),(8.5,47.4),(7.7,47.5),(6.6,46.5),(14.3,48.3),(16.9,48.1),(15.6,47.1),(19.04,47.5),(18.6,47.0),(17.6,47.7),(16.6,47.2)]
_gf=np.random.default_rng(130); FORD=_gf.permutation(len(FINDS))
_MAPBASE=None
def mapbase():
    global _MAPBASE
    if _MAPBASE is None:
        b=bg(SEA)
        for k in range(0,h,13): cv2.line(b,(0,k),(w,k+6),SEAL,2,cv2.LINE_AA)
        land=M().poly(lp_(CONT)).poly(lp_(SWE)).poly(lp_(GB)).poly(lp_(IRL)); sea=M().poly(lp_(MED)).poly(lp_(ADR)); cor=M().poly(lp_(COR))
        L=np.clip(land.f()-sea.f(),0,1); L=np.maximum(L,cor.f())
        bar=np.maximum(M().poly(lp_(BARB)).f(),M().poly(lp_(SCOT)).f()); irl=M().poly(lp_(IRL)).f(); bar=np.maximum(bar,irl)
        fill(b,L,OCHRE); fill(b,L*bar,SAGE)
        for pl in (RHINE,DANUBE): cv2.polylines(b,[np.round(np.array(lp_(pl))*16).astype(np.int32)],False,SEA,4,cv2.LINE_AA,4)
        o=bg(CREAM); o[MY0:MY1,MX0:MX1]=b[MY0:MY1,MX0:MX1]
        cv2.rectangle(o,(MX0-6,MY0-6),(MX1+6,MY1+6),BLACK,6); border(o); _MAPBASE=o
    return _MAPBASE.copy()
# ================= shots =================
def spin(t): return 0.42*t+0.6, 0.48+0.10*math.sin(t*0.7)
def s_hook(t):
    b=bg(); border(b); yw,pt=spin(t)
    dodeca(b,270,390,175,yw,pt,hl_face=EV["twelve"]-0.1,hl_hole=0.8*fa(t,EV["hole"],EV["nobody"]-0.2,0.2,0.3),t=t)
    def hd(d,t=t):
        tag(d,"XII FACES",300,250,40,a=ap(t,EV["twelve"],EV["nobody"]+0.4),sc=pop(t,EV["twelve"]-0.1))
        tag(d,"XII HOLES",780,250,40,a=ap(t,EV["hole"],EV["nobody"]+0.4),sc=pop(t,EV["hole"]-0.1))
        plaque(d,"WHAT IS IT?",540,1265,88,a=ap(t,EV["nobody"],99),sc=pop(t,EV["nobody"]-0.1))
    return b,[hd]
def s_map(t):
    b=mapbase(); n=int(len(FINDS)*cl((t-EV["hundred"])/(EV["england"]-EV["hundred"]+0.6)))
    for k in range(n):
        x,y=LL(*FINDS[FORD[k]]); fill(b,M().circ(x,y,4.6),DRED); fill(b,M().circ(x-1,y-1,2.0),RED)
    for key,(lo,la) in (("england",(-1.6,54.9)),("hungary",(19.04,47.5))):
        k=fa(t,EV[key],99,0.25,0.3)
        if k>0: x,y=LL(lo,la); c=M().circ(x,y,17); c2=M().circ(x,y,11); fill(b,np.clip(c.f()-c2.f(),0,1),GOLD,k)
    nm=EV["hundred"]
    def hd(d,t=t):
        a=fa(t,EV["call"]+0.3,99)
        for s,lo,la in (("BRITANNIA",-3.2,52.4),("GALLIA",1.8,47.0),("GERMANIA",10.0,51.6),("PANNONIA",18.0,46.4)):
            x,y=LL(lo,la); lab(d,s,x*2,y*2,30,a*0.95)
        tag(d,"N. ENGLAND",LL(-1.6,54.9)[0]*2+30,LL(-1.6,54.9)[1]*2-62,32,a=ap(t,EV["england"],99),sc=pop(t,EV["england"]-0.1))
        tag(d,"HUNGARY",LL(19.04,47.5)[0]*2-60,LL(19.04,47.5)[1]*2-62,32,a=ap(t,EV["hungary"],99),sc=pop(t,EV["hungary"]-0.1))
        plaque(d,"ROMAN DODECAHEDRON",540,1265,70,a=ap(t,EV["roman"],EV["hundred"]+0.2),sc=pop(t,EV["roman"]-0.1))
        cnt=int(round(130*eout((t-nm)/1.6)))
        plaque(d,f"~{cnt} FOUND",540,1265,80,a=ap(t,EV["hundred"]+0.1,EV["second"]),sc=pop(t,EV["hundred"]))
        plaque(d,"II – IV CENTURY AD",540,1265,70,a=ap(t,EV["second"],99),sc=pop(t,EV["second"]-0.1))
    return b,[hd]
def s_sizes(t):
    b=bg(); border(b); yw,pt=spin(t); k=sm((t-EV["holes"]+0.4)/0.9)
    sz=[(105,330,42),(240,330,64),(408,330,90)]
    if k<1:
        for i,(x,y,s) in enumerate(sz):
            if i==1: continue
            dodeca(b,x+(270-x)*k*0.0,y,s*(1-k),yw+i,pt,t=t,shadow=k<0.3)
    x,y,s=sz[1]; dodeca(b,270+(x-270)*(1-k),y+(390-y)*k,s+(170-s)*k,yw+1,pt,hl_hole=0.85*fa(t,EV["holes"]+0.3,EV["corner"],0.25,0.3),hl_knob=0.9*fa(t,EV["corner"],EV["graves"],0.25,0.3),t=t)
    def hd(d,t=t):
        a=ap(t,EV["every"],EV["holes"]+0.2)
        for (x,y,s),lb in zip(sz,("4 CM","7 CM","11 CM")): tag(d,lb,x*2,(y+s*1.55)*2,34,a=a,sc=pop(t,EV["every"]+0.1))
        plaque(d,"ALL DIFFERENT",540,1265,80,a=ap(t,EV["every"]+0.2,EV["holes"]),sc=pop(t,EV["every"]+0.1))
        plaque(d,"HOLES: 6–40 MM",540,1265,76,a=ap(t,EV["sizes"]-0.3,EV["corner"]),sc=pop(t,EV["sizes"]-0.4))
        plaque(d,"A KNOB ON EVERY CORNER",540,1265,64,a=ap(t,EV["knob"]-0.3,99),sc=pop(t,EV["knob"]-0.4))
    return b,[hd]
def stele(b,x,y,s):
    fill(b,M().rect(x-70*s,y-110*s,x+70*s,y+120*s),LGREY); fill(b,M().poly([(x-82*s,y-110*s),(x,y-160*s),(x+82*s,y-110*s)]),GREY)
    fill(b,M().rect(x-56*s,y-92*s,x+56*s,y+100*s),WHITE); fill(b,M().rect(x-80*s,y+120*s,x+80*s,y+138*s),GREY)
    for k in range(4): fill(b,M().rect(x-42*s,y-14*s+k*24*s,x+42*s,y-6*s+k*24*s),GREY)
    mm=np.zeros((h,w),np.uint8); cv2.putText(mm,"D M",(int(x-44*s),int(y-40*s)),cv2.FONT_HERSHEY_TRIPLEX,1.5*s,255,max(2,int(5*s)),cv2.LINE_AA); fill(b,mm.astype(np.float32)/255,DRED)
def hoard(b,x,y,s,t,k):
    fill(b,M().ell(x,y+30*s,72*s,78*s),RED); fill(b,M().rect(x-40*s,y-70*s,x+40*s,y-38*s),RED); fill(b,M().ell(x,y-70*s,46*s,12*s),DRED)
    fill(b,M().ell(x,y+30*s,72*s,78*s).f()*np.clip((xx-(x+20*s))/(50*s),0,1),DRED,0.7)
    for i in range(int(14*k)):
        a_=i*2.4; r=30+i*4.5; cx,cy=x+70*s+math.cos(a_)*r*0.9*s,y+95*s+math.sin(a_)*r*0.25*s
        fill(b,M().circ(cx,cy,9*s),GOLD); fill(b,M().circ(cx,cy,5*s),OCHRE)
def s_burial(t):
    b=bg(); border(b)
    k1=sm((t-EV["graves"]+0.5)/0.5); k2=sm((t-EV["hoards"]+0.4)/0.5)
    stele(b,150,330,1.0); dodeca(b,150,535,58,spin(t)[0],0.5,t=t,shadow=False)
    if k2>0: hoard(b,385,330,1.0*k2,t,cl((t-EV["hoards"])/1.2)); dodeca(b,385,535,58*k2,spin(t)[0]+1,0.5,t=t,shadow=False)
    def hd(d,t=t):
        tag(d,"GRAVES",300,1180,40,a=ap(t,EV["graves"],99),sc=pop(t,EV["graves"]-0.1))
        tag(d,"COIN HOARDS",770,1180,40,a=ap(t,EV["hoards"],99),sc=pop(t,EV["hoards"]-0.1))
        plaque(d,"BURIED LIKE TREASURE",540,1320,66,a=ap(t,EV["treasure"]-0.1,99),sc=pop(t,EV["treasure"]-0.2))
    return b,[hd]
def s_silence(t):
    b=bg(); border(b)
    # scroll (volumen) with columns of writing
    fill(b,M().rect(70,170,330,520),WHITE); fill(b,M().rect(56,160,80,530),BRN); fill(b,M().rect(320,160,344,530),BRN)
    for c in range(2):
        for r_ in range(9): fill(b,M().rect(98+c*115,200+r_*36,98+c*115+(90 if (r_*7+c*3)%5 else 58),212+r_*36),GREY)
    # empty painted panel (picture)
    fill(b,M().rect(370,210,490,360),BRN); fill(b,M().rect(382,222,478,348),CREAM)
    sc_=fa(t,EV["text"],99,0.3,0.3); k=sm((t-EV["mentions"]+0.2)/0.4)
    if sc_>0:
        y=196+((t-EV["text"])*90)%300; fill(b,M().rect(90,y,320,y+10),GOLD,0.8*sc_*(1-k))
    if k>0:
        for (x0,y0,x1,y1) in ((60,160,340,530),(370,210,490,360)):
            m=M().line((x0,y0),(x1,y1),16).line((x1,y0),(x0,y1),16); fill(b,m,DRED,k)
    def hd(d,t=t):
        tag(d,"TEXTS",400,1120,38,a=ap(t,EV["text"],99),sc=pop(t,EV["text"]-0.1))
        tag(d,"PICTURES",860,800,38,a=ap(t,EV["picture"],99),sc=pop(t,EV["picture"]-0.1))
        plaque(d,"NEVER MENTIONED",540,1265,80,a=ap(t,EV["mentions"],99),sc=pop(t,EV["mentions"]-0.1))
    return b,[hd]
PAN=[(40,150,262,372),(278,150,500,372),(40,410,262,632),(278,410,500,632)]
def panel(b,i):
    x0,y0,x1,y1=PAN[i]; fill(b,M().rect(x0,y0,x1,y1),BLACK); fill(b,M().rect(x0+8,y0+8,x1-8,y1-8),WHITE); return (x0+x1)/2,(y0+y1)/2
def s_guess(t):
    b=bg(); border(b); keys=["candle","die","tool","charm"]; yw,pt=spin(t)
    for i,kk in enumerate(keys):
        k=sm((t-EV[kk]+0.25)/0.35)
        if k<=0: continue
        cx,cy=panel(b,i)
        if i==0:
            dodeca(b,cx,cy+28,66*k,yw,pt,t=t,shadow=False)
            fill(b,M().rect(cx-15,cy-78,cx+15,cy-30),GREY); fill(b,M().rect(cx-11,cy-74,cx+11,cy-30),WHITE)
            fl=1+0.12*math.sin(t*23)+0.08*math.sin(t*37); fill(b,M().ell(cx,cy-98,14*k,26*fl*k),FLAME); fill(b,M().ell(cx,cy-90,6*k,11*k),WHITE)
        elif i==1:
            s=58*k; fill(b,M().poly([(cx-s,cy-s*0.6),(cx,cy-s*1.1),(cx+s,cy-s*0.6),(cx,cy-s*0.1)]),WHITE)
            fill(b,M().poly([(cx-s,cy-s*0.6),(cx,cy-s*0.1),(cx,cy+s*1.0),(cx-s,cy+s*0.5)]),LGREY)
            fill(b,M().poly([(cx+s,cy-s*0.6),(cx,cy-s*0.1),(cx,cy+s*1.0),(cx+s,cy+s*0.5)]),GREY)
            cv2.polylines(b,[np.round(np.array([(cx-s,cy-s*0.6),(cx,cy-s*1.1),(cx+s,cy-s*0.6),(cx+s,cy+s*0.5),(cx,cy+s*1.0),(cx-s,cy+s*0.5)])*16).astype(np.int32)],True,BLACK,3,cv2.LINE_AA,4)
            for px,py in ((0,-0.6),(-0.5,0.0),(-0.5,0.5),(0.5,0.2)): fill(b,M().circ(cx+px*s,cy+py*s,7*k),BLACK)
        elif i==2:
            dodeca(b,cx-50,cy+40,40*k,yw,pt,t=t,shadow=False)
            fill(b,M().rect(cx+48,cy-70,cx+80,cy+60),GREY); fill(b,M().poly([(cx+42,cy-70),(cx+64,cy-92),(cx+86,cy-70)]),DRED)
            for a in (-0.35,0.0):
                m=M().line((cx-50,cy+40),(cx-50+150*math.cos(a-0.5),cy+40+150*math.sin(a-0.5)),3); fill(b,m,DRED,k)
        else:
            for a in np.linspace(0,2*math.pi,10,endpoint=False):
                m=M().line((cx+math.cos(a+t*0.6)*58,cy+10+math.sin(a+t*0.6)*58),(cx+math.cos(a+t*0.6)*86,cy+10+math.sin(a+t*0.6)*86),6); fill(b,m,GOLD,k)
            fill(b,M().line((cx,cy-95),(cx,cy-40),3),BLACK,k); dodeca(b,cx,cy+10,52*k,yw,pt,t=t,shadow=False,glow=0.6*k)
    def hd(d,t=t):
        plaque(d,"THE GUESSES",540,190,66,a=ap(t,EV["pile"],99),sc=pop(t,EV["pile"]-0.1))
        for i,(kk,s) in enumerate(zip(keys,("CANDLE HOLDER?","GAMING DIE?","MEASURING TOOL?","RELIGIOUS CHARM?"))):
            x0,y0,x1,y1=PAN[i]; tag(d,s,(x0+x1),y1*2+4,30,a=ap(t,EV[kk],99),sc=pop(t,EV[kk]-0.1))
    return b,[hd]
_FLD=None
def fieldbase():
    global _FLD
    if _FLD is None:
        b=bg((0.86,0.90,0.90))
        fill(b,M().poly([(0,250)]+[(x,250-14*math.sin(x/60)-10*math.sin(x/23)) for x in range(0,w+20,20)]+[(w,960),(0,960)]),DGREEN)
        fld=M().poly([(0,290)]+[(x,284-8*math.sin(x/90)) for x in range(0,w+20,20)]+[(w,960),(0,960)]); fill(b,fld,SAGE)
        F=fld.f()
        for k in range(-20,40):
            m=M().line((270+k*30*0.2,290),(270+k*60,960),5); fill(b,m.f()*F,DGREEN,0.8)
        fill(b,M().circ(440,120,34),WHITE); fill(b,M().circ(440,120,26),GOLD)
        for x in (60,150,470): fill(b,M().circ(x,236,24),DGREEN); fill(b,M().circ(x+20,226,20),DGREEN)
        fill(b,M().poly([(140,470),(400,470),(430,600),(110,600)]),BRN); fill(b,M().poly([(160,482),(380,482),(402,590),(132,590)]),(0.60,0.42,0.22))
        border(b); _FLD=b
    return _FLD.copy()
def digger(b,x,y,s,t,ph):
    fill(b,M().circ(x,y-62*s,12*s),BLACK); fill(b,M().poly([(x-14*s,y-48*s),(x+14*s,y-48*s),(x+18*s,y),(x-18*s,y)]),DRED)
    a=0.6+0.35*math.sin(t*4+ph); fill(b,M().line((x+10*s,y-40*s),(x+10*s+34*s*math.cos(a),y-40*s+34*s*math.sin(a)),6*s),BLACK)
    fill(b,M().rect(x-16*s,y,x-4*s,y+36*s),BLACK); fill(b,M().rect(x+4*s,y,x+16*s,y+36*s),BLACK)
def s_find(t):
    b=fieldbase()
    for x,y,ph in ((110,430,0),(440,440,2),(468,590,4)): digger(b,x,y,1.0,t,ph)
    k=sm((t-EV["found"]+0.3)/1.0); yw,pt=spin(t)
    dodeca(b,270,560-60*k,40+30*k,yw,pt,t=t,shadow=False,glow=fa(t,EV["found"],EV["solve"],0.3,0.4)*0.8)
    if k>0:
        for i in range(8):
            a=i*math.pi/4+t*0.5; r=60+8*math.sin(t*6+i); fill(b,M().line((270+math.cos(a)*r*0.8,500+math.sin(a)*r*0.8),(270+math.cos(a)*r*1.15,500+math.sin(a)*r*1.15),3),GOLD,k*0.7*fa(t,EV['found'],EV['solve']+0.6,0.3,0.4))
    def hd(d,t=t):
        plaque(d,"MMXXIII · 2023",540,190,66,a=ap(t,EV["y2023"],EV["norton"]),sc=pop(t,EV["y2023"]-0.1))
        tag(d,"NORTON DISNEY · LINCOLNSHIRE",540,190,36,a=ap(t,EV["norton"],EV["solve"]),sc=pop(t,EV["norton"]-0.1))
        tag(d,"VOLUNTEERS",540,1265,34,a=ap(t,EV["diggers"],EV["found"]),sc=pop(t,EV["diggers"]-0.1),bg=(60,80,50))
        plaque(d,"ALMOST INTACT",540,1265,74,a=ap(t,EV["intact"]-0.2,EV["solve"]),sc=pop(t,EV["intact"]-0.3))
        plaque(d,"STILL UNSOLVED",540,1265,78,a=ap(t,EV["solve"],99),sc=pop(t,EV["solve"]-0.1))
    return b,[hd]
def s_final(t):
    b=bg(); border(b); yw,pt=spin(t-ev.T["total"])
    dodeca(b,270,390,175,yw,pt,t=t)
    def hd(d,t=t):
        plaque(d,"XVIII CENTURIES LATER",540,1265,64,a=ap(t,EV["eighteen"],EV["this"]+0.3),sc=pop(t,EV["eighteen"]-0.1))
    return b,[hd]
TR=0.36; TOTAL=B.TOTAL; LOOPD=0.62
SHOTS=[(0.0,s_hook),(S("map")["s"],s_map),(S("clues")["s"],s_sizes),(EV["graves"]-0.55,s_burial),(Lx("But no surviving")[0]-0.35,s_silence),
       (S("guess")["s"],s_guess),(S("find")["s"],s_find),(Lx("Eighteen")[0]-0.3,s_final)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None:
        buf,hud=SHOTS[i][1](t); cols=tiles(buf); hk=1.0
    else:
        fa_,fb_,ta,tb,u=pair; b1,h1=fa_(ta); b2,h2=fb_(tb)
        cols=flip(tiles(b1),tiles(b2),u); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    img=Image.fromarray((paint(cols)*255).astype(np.uint8)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
