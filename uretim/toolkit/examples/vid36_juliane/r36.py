import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid36")
for p in ["/home/claude/vid36","/home/claude/vid3","/home/claude/ep1"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
from paper import *
from PIL import Image, ImageDraw
EV=ev.EV; Lx=ev.Lx; SS=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
LOGO=E1.LOGO
SKIN=(0.87,0.66,0.52); HAIR=(0.30,0.17,0.10); DRESS=(0.98,0.80,0.32); SEAT=(0.20,0.45,0.66); SEATD=(0.12,0.29,0.46); FRAME=(0.55,0.58,0.62)
GD=(0.04,0.17,0.15); G1=(0.06,0.27,0.20); G2=(0.10,0.40,0.26); G3=(0.25,0.57,0.30); G4=(0.55,0.77,0.32)
WATER=(0.32,0.74,0.84); WATERD=(0.14,0.48,0.60); CREAM=(250,245,232); INK=(28,30,36)
ORANGE=(240,120,50); RED=(205,60,55); BLUE=(40,90,160); GOLD=(250,190,60)
# ================= shared shape builders =================
P=1080; JW=P+w
def ridgeP(y0,amp,seed,step=12):
    g=np.random.default_rng(seed); xs=np.arange(0,JW+step,step).astype(np.float64); y=np.zeros(len(xs))
    for k,am in ((2,1.0),(5,0.5),(11,0.25),(23,0.12)):
        y+=am*np.sin(xs*2*np.pi*k/P+g.uniform(0,6.283))
    return [(0,h+60)]+list(zip(xs,y0+y*amp))+[(JW,h+60)]
def per(fn,x,*a,**k):
    fn(x,*a,**k)
    if x<w+120: fn(x+P,*a,**k)
    if x>P-120: fn(x-P,*a,**k)
def _jungle(seed):
    g=np.random.default_rng(seed); L=[]
    m=M(JW,h).poly(ridgeP(420,38,seed)); L.append(m)                      # far hills
    m=M(JW,h); m.poly(ridgeP(470,22,seed+1))
    for i in range(16): per(lambda x,r=g.uniform(30,50),y=g.uniform(430,470),s=g.integers(999): blob(m,x,y,r,s,6),g.uniform(0,P))
    L.append(m)                                                              # far canopy
    m=M(JW,h); m.poly(ridgeP(560,18,seed+2))
    for i in range(9):
        x=g.uniform(0,P); r=g.uniform(45,75); y=g.uniform(330,420); s=int(g.integers(999)); tw=g.uniform(9,15)
        per(lambda x,y=y,r=r,s=s,tw=tw:(m.poly([(x-tw,h),(x-tw*0.6,y),(x+tw*0.6,y),(x+tw,h)]),blob(m,x,y,r,s,8)),x)
    L.append(m)                                                              # mid trees
    m=M(JW,h); m.poly(ridgeP(640,14,seed+3))
    for i in range(70):
        x=g.uniform(0,P); a=g.uniform(-2.6,-0.5); Ll=g.uniform(50,110)
        per(lambda x,a=a,Ll=Ll:leaf(m,x,g.uniform(630,700) if False else 660,Ll,Ll*0.22,a,curl=0.1),x)
    L.append(m)                                                              # near bank ferns
    m=M(JW,h)
    for i in range(26):
        x=g.uniform(0,P); a=g.uniform(1.0,2.1); Ll=g.uniform(70,150)
        per(lambda x,a=a,Ll=Ll:leaf(m,x,-10,Ll,Ll*0.24,a,curl=-0.1),x)
    for i in range(10):
        x=g.uniform(0,P); ln=g.uniform(80,260)
        per(lambda x,ln=ln:(m.line((x,0),(x+6,ln),3),leaf(m,x+6,ln,26,8,1.9)),x)
    L.append(m)                                                              # hanging leaves/vines (top)
    return L
JUNG=_jungle(7)
def jungle(buf,t,cam,pal,water=None,oy=0,flow=0.0,skip=()):
    """pal: list of 5 colors (far hills, far canopy, mid trees, bank ferns, hanging). cam: camera x (scroll)."""
    pars=(0.15,0.3,0.55,1.0,1.25)
    for k,m in enumerate(JUNG):
        if k in skip: continue
        ox=-int((cam*pars[k])%P)
        if k==3 and water is not None: waterband(buf,t,water,flow,cam)
        comp(buf,m,pal[k],sh=0.32 if k>1 else 0.18,ox=ox,oy=oy if k<4 else 0)
def waterband(buf,t,wb,flow,cam):
    y0,y1,col,col2=wb; y0=int(y0); y1=int(y1)
    if y1<=y0: return
    m=M().rect(-5,y0,w+5,y1); comp(buf,m,col,sh=0.0,rim=0.0)
    hl=M(); g=np.random.default_rng(3)
    for i in range(40):
        yy_=g.uniform(y0+4,y1-2); L=g.uniform(14,40); x=(g.uniform(0,w+60)+t*flow*(0.6+0.8*(yy_-y0)/max(1,y1-y0))+cam*0.9)%(w+60)-30
        hl.line((x,yy_),(x+L,yy_),1.6)
    comp(buf,hl,col2,sh=0.0,rim=0.0,a=0.7)
def girl(buf,x,y,s=1.0,ph=0.0,walk=0.0,face=1,wade=None):
    H_=70*s; sw=math.sin(ph)*0.45*walk
    hip=(x,y-0.42*H_); sh_=(x,y-0.78*H_)
    lg=M()
    for sg in (1,-1):
        a=sg*sw; lg.line(hip,(x+math.sin(a)*0.42*H_*face,y-0.42*H_+math.cos(a)*0.42*H_),0.07*H_)
    comp(buf,lg,(SKIN[0]*0.85,SKIN[1]*0.85,SKIN[2]*0.85),sh=0.25)
    ar=M(); a=-sw*0.8; ar.line((x,sh_[1]+0.04*H_),(x+math.sin(a)*0.32*H_*face,sh_[1]+0.04*H_+math.cos(a)*0.32*H_),0.06*H_); comp(buf,ar,(SKIN[0]*0.8,SKIN[1]*0.8,SKIN[2]*0.8),sh=0.2)
    dr=M().poly([(x-0.10*H_,sh_[1]),(x+0.10*H_,sh_[1]),(x+0.18*H_,y-0.38*H_),(x-0.18*H_,y-0.38*H_)]); comp(buf,dr,DRESS,sh=0.3)
    ar=M(); a=sw*0.8; ar.line((x,sh_[1]+0.04*H_),(x+math.sin(a)*0.32*H_*face,sh_[1]+0.04*H_+math.cos(a)*0.32*H_),0.06*H_); comp(buf,ar,SKIN,sh=0.2)
    hx,hy=x+0.02*H_*face,y-0.90*H_
    hr=M().circ(hx-0.03*H_*face,hy+0.01*H_,0.105*H_).poly([(hx-0.11*H_*face,hy),(hx+0.0*face,hy),(hx-0.04*H_*face,hy+0.24*H_),(hx-0.13*H_*face,hy+0.22*H_)]); comp(buf,hr,HAIR,sh=0.2)
    hd=M().circ(hx+0.02*H_*face,hy+0.02*H_,0.085*H_); comp(buf,hd,SKIN,sh=0.15)
    hr=M().ell(hx-0.01*H_*face,hy-0.05*H_,0.10*H_,0.05*H_,-15*face); comp(buf,hr,HAIR,sh=0.1)
    if wade is not None:
        comp(buf,M().rect(x-0.35*H_,wade,x+0.35*H_,y+4),WATER,sh=0.0,rim=0.0,a=0.85)
        rp=M(); rp.ell(x,wade,0.32*H_,0.04*H_); comp(buf,rp,(0.85,0.95,1.0),sh=0,a=0.5)
def seats(buf,cx,cy,s=1.0,ang=0.0,sq=1.0,girl_in=True,col=SEAT,cold=SEATD,a=1.0):
    def T(pts): return rot(pts,ang,cx,cy,sq*s,s)
    fr=M(); fr.poly(T([(-60,22),(60,22),(60,28),(-60,28)]))
    for lx in (-50,0,50): fr.poly(T([(lx-3,26),(lx+3,26),(lx+5,48),(lx-5,48)]))
    comp(buf,fr,FRAME,a=a)
    bk=M(); cs=M()
    for k in (-40,0,40):
        bk.poly(T([(k-17,-46),(k+17,-46),(k+18,-40),(k+18,10),(k-18,10),(k-18,-40)]))
        cs.poly(T([(k-19,6),(k+19,6),(k+19,24),(k-19,24)]))
    comp(buf,bk,col,a=a); comp(buf,cs,cold,a=a)
    if girl_in:
        k=-40; d=M().poly(T([(k-14,-14),(k+14,-14),(k+16,14),(k-16,14)])); comp(buf,d,DRESS,a=a)
        hr=M().poly(T([(k-13,-40),(k+13,-40),(k+12,-14),(k-12,-14)])).circ(*T([(k,-36)])[0],13*s); comp(buf,hr,HAIR,a=a)
        hd=M().circ(*T([(k,-30)])[0],10.5*s*max(0.4,sq)); comp(buf,hd,SKIN,a=a,sh=0.1)
        bl=M().line(T([(k-18,12)])[0],T([(k+18,12)])[0],2.5*s); comp(buf,bl,(0.85,0.85,0.8),sh=0,a=a)
def plane_masks(T):
    body=M(); st=M(); win=M(); eng=M(); prop=M()
    body.poly(T([(-150,-14),(118,-14),(135,-11),(150,-4),(153,2),(146,9),(130,15),(-120,15),(-150,6),(-168,-2),(-150,-14)]))
    body.poly(T([(-150,-12),(-176,-58),(-160,-60),(-118,-12)]))
    body.poly(T([(-175,-8),(-128,-8),(-128,-2),(-178,-2)]))
    st.poly(T([(-150,-4),(150,-4),(152,0),(-160,0)]))
    for i in range(16): win.circ(*T([(-110+i*14,-8)])[0],2.4)
    win.poly(T([(130,-11),(144,-6),(140,-3),(128,-6)]))
    wing=T([(-30,8),(60,8),(64,14),(-36,14)]); eng.poly(wing)
    for ex in (30,-10):
        eng.poly(T([(ex-6,0),(ex+36,0),(ex+40,6),(ex+36,13),(ex-6,13)]))
    for ex in (30,-10): prop.ell(*T([(ex+42,6)])[0],2.5,22,0)
    return [(body,(0.95,0.95,0.97)),(st,(0.85,0.22,0.22)),(win,(0.18,0.28,0.42)),(eng,(0.78,0.80,0.84)),(prop,(0.6,0.62,0.66))]
def bolt(buf,x0,y0,x1,y1,seed,a=1.0,th=3.0):
    g=np.random.default_rng(seed); n=12; pts=[(x0,y0)]
    for i in range(1,n):
        u=i/n; pts.append((x0+(x1-x0)*u+g.uniform(-22,22),y0+(y1-y0)*u+g.uniform(-8,8)))
    pts.append((x1,y1)); m=M().pline(pts,th)
    for j in range(3):
        k=int(g.integers(2,n-2)); bx,by=pts[k]; m.pline([(bx,by),(bx+g.uniform(-50,50),by+g.uniform(20,60)),(bx+g.uniform(-70,70),by+g.uniform(50,100))],th*0.6)
    f=m.f(); gl=cv2.GaussianBlur(f,(0,0),10)
    buf+=(gl*a*1.6)[...,None]*np.array([0.7,0.75,1.0],np.float32); buf+=(f*a)[...,None]*(np.array([1,1,1],np.float32)-buf)
def gift(m_box,m_rib,x,y,s,ang):
    m_box.poly(rot([(-s,-s),(s,-s),(s,s),(-s,s)],ang,x,y)); m_rib.poly(rot([(-s,-s*0.18),(s,-s*0.18),(s,s*0.18),(-s,s*0.18)],ang,x,y)); m_rib.poly(rot([(-s*0.18,-s),(s*0.18,-s),(s*0.18,s),(-s*0.18,s)],ang,x,y))
# --- clouds (periodic) ---
def _clouds(seed,n,yr,rr):
    g=np.random.default_rng(seed); m=M(2*w,h)
    for i in range(n):
        x=g.uniform(0,w); y=g.uniform(*yr); r=g.uniform(*rr); s=int(g.integers(999)); cloud(m,x,y,r,s); cloud(m,x+w,y,r,s)
    return m
CLS=[_clouds(1,6,(80,700),(40,70)),_clouds(2,6,(60,760),(55,90)),_clouds(3,5,(100,820),(70,110))]
SCL=[_clouds(11,7,(40,900),(50,80)),_clouds(12,6,(40,900),(70,110)),_clouds(13,5,(60,900),(90,140))]  # storm
# --- top-down forest texture ---
def _forest(N=1100,seed=4):
    g=np.random.default_rng(seed); img=np.zeros((N,N,3),np.float32); img[:]=GD
    pal=[G1,G2,G3,(0.18,0.50,0.28),(0.35,0.62,0.30),(0.10,0.35,0.30),G4]
    for i in range(1900):
        x,y=g.uniform(0,N,2); r=g.uniform(10,34); c=np.array(pal[int(g.integers(len(pal)))],np.float32)*g.uniform(0.85,1.1)
        cv2.circle(img,(int(x+3),int(y+4)),int(r),tuple(float(v) for v in np.array(GD)*0.7),-1,cv2.LINE_AA)
        cv2.circle(img,(int(x),int(y)),int(r),tuple(float(v) for v in c),-1,cv2.LINE_AA)
        cv2.circle(img,(int(x-r*0.25),int(y-r*0.25)),int(r*0.55),tuple(float(v) for v in np.clip(c*1.18,0,1)),-1,cv2.LINE_AA)
    return cv2.GaussianBlur(img,(0,0),0.7)
if os.path.exists("forest.npy"): FOREST=np.load("forest.npy")
else: FOREST=_forest(); np.save("forest.npy",FOREST)
def forest_view(cx,cy,sc,ang):
    Mx=cv2.getRotationMatrix2D((cx,cy),ang,sc); Mx[0,2]+=w/2-cx; Mx[1,2]+=h/2-cy
    return cv2.warpAffine(FOREST,Mx,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
# rays
RAYS=np.zeros((h,w),np.float32)
for k,(x0,wd) in enumerate([(120,26),(230,14),(330,34),(450,18),(520,24)]):
    d=(xx-(x0-0.45*yy)); RAYS+=np.exp(-(d/wd)**2)*(0.7+0.3*(k%2))
RAYS*=np.clip(1-yy/850,0,1)
def birds(buf,t,n,col=(0.15,0.12,0.18),seed=5,y0=150,a=1.0):
    g=np.random.default_rng(seed); m=M()
    for i in range(n):
        x=(g.uniform(0,w)+t*g.uniform(18,34))%(w+40)-20; y=y0+g.uniform(-60,60)+math.sin(t*0.8+i)*6; f=math.sin(t*9+i*2)*5; s=g.uniform(6,10)
        m.pline([(x-s,y-f),(x,y),(x+s,y-f)],1.8)
    comp(buf,m,col,sh=0,a=a,rim=0)
def butterfly(buf,x,y,s,t,col):
    f=abs(math.sin(t*12))*0.8+0.2; m=M(); m.ell(x-6*s*f,y,7*s*f,10*s,20); m.ell(x+6*s*f,y,7*s*f,10*s,-20); comp(buf,m,col,sh=0.25)
    comp(buf,M().ell(x,y,1.6*s,7*s),(0.1,0.1,0.1),sh=0)
def hut(m_wall,m_roof,m_dark,x,y,s=1.0,stilts=False):
    b=y-(26*s if stilts else 0)
    if stilts:
        for sx in (-34,-12,12,34): m_dark.rect(x+sx*s-2*s,b,x+sx*s+2*s,y)
    m_wall.rect(x-40*s,b-44*s,x+40*s,b); m_dark.rect(x-10*s,b-30*s,x+10*s,b)
    m_roof.poly([(x-58*s,b-40*s),(x,b-86*s),(x+58*s,b-40*s),(x+50*s,b-34*s),(x-50*s,b-34*s)])
def boat(m,x,y,s=1.0,ang=0.0): m.poly(rot([(-60,-6),(60,-10),(48,8),(-48,8)],ang,x,y,s,s))
def dayc(d,n,a,x=200,y=230):
    card(d,f"DAY {n}",x,y,fs=46,a=a,fg=(30,30,30),bg=(255,212,80),fn="BigShoulders-Bold",ang=-3,pad=(28,8))
# ================= scenes =================
def s_hook(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    cd=sm((t-EV["landed"]+0.4)/2.8); sr=sm((t-EV["eleven"]+0.4)/1.6)
    top=lerpc((0.10,0.09,0.30),(0.36,0.56,0.84),sr); mid=lerpc((0.58,0.24,0.48),(0.98,0.72,0.55),sr); low=lerpc((1.0,0.60,0.34),(1.0,0.90,0.62),sr)
    grad(buf,[(0,top),(520-cd*260,mid),(860-cd*330,low)])
    rgrad(buf,420,640-cd*300-sr*120,150,(1.0,0.75,0.45),0.35+0.35*sr)
    for k,(m,col) in enumerate(zip(CLS,[lerpc((0.75,0.45,0.62),(1.0,0.88,0.80),sr),lerpc((0.85,0.55,0.65),(1.0,0.93,0.86),sr),lerpc((0.95,0.70,0.70),(1.0,0.97,0.92),sr)])):
        comp(buf,m,col,sh=0.15,ox=-int((t*(6+6*k))%w),oy=int(-cd*(160+120*k)),a=0.9)
    if sr>0: buf+=(RAYS*0.35*sr)[...,None]*np.array([1.0,0.9,0.6],np.float32)
    fy=80+460*sm(t/(EV["landed"]+1.9))**1.15
    if t<EV["landed"]+2.6: seats(buf,370,fy,0.95,0.35*math.sin(t*0.9),max(0.2,abs(math.cos(t*2.6))))
    pal=[lerpc((0.20,0.35,0.42),(0.40,0.62,0.55),sr),lerpc(G1,G2,sr),lerpc(GD,G2,sr*0.6),G1,GD]
    jungle(buf,t,t*10,pal,oy=int(470-cd*420),skip=(3,4))
    if sr>0: birds(buf,t,6,a=sr,y0=230)
    def hd(d,t=t):
        a=fa(t,0.3,EV["landed"]-0.3); card(d,"DECEMBER 24, 1971",290,210,fs=34,a=a,ang=-3)
        a2=fa(t,EV["twomiles"]-0.1,EV["landed"]-0.3); card(d,"2 MILES",290,360,fs=112,a=a2,fn="Gloock-Regular",fg=(255,255,255),bg=(225,85,60),ang=2,sc=spring((t-EV["twomiles"]+0.1)/0.6))
        card(d,"≈ 3,000 m  ·  10,000 ft",290,480,fs=30,a=a2*sm((t-EV["twomiles"]-0.3)/0.3),ang=2)
        a=fa(t,EV["landed"]-0.1,EV["eleven"]-0.4); card(d,"THE AMAZON RAINFOREST",540,230,fs=40,a=a,fg=(255,255,255),bg=(30,110,70),ang=-2)
        card(d,"ALONE.",540,390,fs=120,a=fa(t,EV["alone"]-0.05,EV["eleven"]-0.4),fn="Gloock-Regular",ang=1,sc=spring((t-EV["alone"]+0.05)/0.6))
        a=fa(t,EV["eleven"]-0.1,SS("hook")["e"]+1); card(d,"11 DAYS LATER",540,240,fs=44,a=a,bg=(255,212,80),ang=-2)
        card(d,"SHE WALKED OUT\nALIVE",540,430,fs=92,a=fa(t,EV["alive"]-0.15,SS("hook")["e"]+1),fn="Gloock-Regular",ang=1,sc=spring((t-EV["alive"]+0.15)/0.6))
    hud.append(hd); return buf,hud
def bust(buf,x,y,s=1.0,a=1.0):
    comp(buf,M().ell(x,y+20*s,78*s,104*s),HAIR,a=a)
    comp(buf,M().ell(x,y+150*s,120*s,70*s).rect(x-120*s,y+150*s,x+120*s,y+240*s),(0.30,0.55,0.75),a=a)
    comp(buf,M().rect(x-18*s,y+40*s,x+18*s,y+100*s),(SKIN[0]*0.88,SKIN[1]*0.88,SKIN[2]*0.88),a=a)
    comp(buf,M().ell(x,y,50*s,64*s),SKIN,a=a)
    comp(buf,M().ell(x-8*s,y-46*s,58*s,30*s,-8),HAIR,a=a,sh=0.15)
    ey=M().circ(x-18*s,y+2*s,4.2*s).circ(x+18*s,y+2*s,4.2*s); comp(buf,ey,(0.18,0.12,0.10),a=a,sh=0,rim=0)
    ck=M().circ(x-28*s,y+20*s,9*s).circ(x+28*s,y+20*s,9*s); comp(buf,ck,(0.95,0.55,0.50),a=a*0.45,sh=0,rim=0)
    sm_=M().pline([(x-12*s+24*s*u,y+28*s+7*s*math.sin(math.pi*u)) for u in np.linspace(0,1,9)],2.6*s); comp(buf,sm_,(0.45,0.20,0.18),a=a,sh=0,rim=0)
    comp(buf,M().poly([(x-50*s,y+80*s),(x,y+140*s),(x+50*s,y+80*s),(x+70*s,y+110*s),(x,y+190*s),(x-70*s,y+110*s)]),(0.96,0.95,0.92),a=a,sh=0.15)
def s_lima(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    grad(buf,[(0,(0.99,0.92,0.78)),(600,(0.98,0.80,0.62)),(960,(0.95,0.70,0.55))])
    comp(buf,M().circ(430,160,58),(1.0,0.72,0.38),sh=0.1)
    pm=fa(t,EV["flying"]-0.5,SS("lima")["e"]+1,0.5,0.3); pa=1-pm
    # pastel colonial skyline
    g=np.random.default_rng(2); cols=[(0.96,0.55,0.45),(0.55,0.80,0.70),(0.98,0.80,0.40),(0.60,0.70,0.90),(0.95,0.65,0.70)]
    for row,(yb,sc_) in enumerate(((800,1.0),(860,1.2))):
        x=-20+row*30; i=0
        while x<w+20:
            bw=g.uniform(60,95)*sc_; bh=g.uniform(120,200)*sc_; m=M().rect(x,yb-bh,x+bw,h+10)
            if g.uniform()<0.4: m.poly([(x-4,yb-bh),(x+bw/2,yb-bh-30*sc_),(x+bw+4,yb-bh)])
            comp(buf,m,cols[(i+row*2)%5],a=pa)
            win=M()
            for yy_ in np.arange(yb-bh+22,yb-20,38*sc_):
                for xx_ in np.arange(x+12,x+bw-14,22*sc_): win.rect(xx_,yy_,xx_+10*sc_,yy_+18*sc_)
            comp(buf,win,(0.35,0.30,0.32),sh=0.1,rim=0,a=pa*0.8); x+=bw+4; i+=1
    pb=sm((t-EV["parents"]+0.6)/0.6)
    bx=270-120*pb; by=380+20*pb; bs=1.0-0.22*pb
    if pa>0.01: bust(buf,bx,by,bs,pa*sm((t-sc["s"])/0.5))
    gt=t-EV["grad"]
    if -0.2<gt<6 and pa>0.01:
        cy=by-70*bs-160*eout(gt/0.9)+60*max(0,gt-1.6)**2*0 ; ang=gt*5.0 if gt<0.9 else 4.5+0.2*math.sin(gt*3)
        cy=by-70*bs-150*sm(gt/0.8)+150*sm((gt-1.8)/0.7)
        cap=M().poly(rot([(-46,0),(0,-16),(46,0),(0,16)],0.2*math.sin(gt*4),bx,cy)); comp(buf,cap,(0.12,0.12,0.16),a=pa)
        tas=M().line((bx+20,cy+2),(bx+28,cy+30),2.5); comp(buf,tas,(1.0,0.8,0.2),a=pa,sh=0.1)
        if gt>0:
            cf=M(); g2=np.random.default_rng(9); cc=[(0.95,0.3,0.3),(0.3,0.6,0.95),(1.0,0.8,0.2),(0.4,0.8,0.4)]
            for j in range(4):
                cf=M()
                for k in range(18):
                    vx=g2.uniform(-160,160); vy=g2.uniform(-260,-80); px=bx+vx*gt; py=by-80+vy*gt+190*gt*gt
                    cf.poly(rot([(-4,-2),(4,-2),(4,2),(-4,2)],gt*g2.uniform(3,9),px,py))
                comp(buf,cf,cc[j],sh=0.15,a=pa*(1-sm((gt-2.5)/1.0)),rim=0)
    if pb>0.01 and pa>0.01:
        for k,(ix,iy,e) in enumerate(((380,250,EV["parents"]),(450,370,EV["parents"]+0.25),(380,480,EV["station"]))):
            s_=spring((t-e)/0.6)*pa
            if s_<0.02: continue
            if k==0: butterfly(buf,ix,iy,2.2*s_,t,(0.25,0.55,0.95))
            elif k==1:
                comp(buf,M().circ(ix-8,iy-8,26*s_),(0.85,0.92,0.98)); comp(buf,M().line((ix+10,iy+10),(ix+36*s_,iy+36*s_),9),(0.45,0.30,0.20))
                ring=M().circ(ix-8,iy-8,26*s_); ring.m=np.clip(ring.m.astype(np.int16)-M().circ(ix-8,iy-8,20*s_).m.astype(np.int16),0,255).astype(np.uint8); comp(buf,ring,(0.3,0.3,0.35))
            else:
                mw,mr,md=M(),M(),M(); hut(mw,mr,md,ix,iy+40,0.8*s_,True); comp(buf,M().ell(ix,iy+46,90*s_,14*s_),G2); comp(buf,md,(0.35,0.22,0.14)); comp(buf,mw,(0.80,0.62,0.40)); comp(buf,mr,(0.62,0.48,0.22))
    if pm>0.01:
        mp=sm((t-EV["flying"]+0.5)/0.6); y0=int(150+(1-mp)*700)
        comp(buf,M().rect(36,y0,504,y0+470),(0.55,0.78,0.90),sh=0.4)
        land=M().poly([(170,y0),(504,y0),(504,y0+470),(260,y0+470),(225,y0+380),(180,y0+260),(150,y0+120)]); comp(buf,land,(0.93,0.86,0.68),sh=0.2)
        jg=M().poly([(330,y0),(504,y0),(504,y0+470),(360,y0+470),(340,y0+300),(320,y0+150)]); comp(buf,jg,(0.35,0.62,0.35),sh=0.15)
        mt=M()
        for k in range(9):
            mx=205+k*14+ (k%2)*10; my=y0+70+k*42; mt.poly([(mx-26,my+30),(mx,my-18),(mx+26,my+30)])
        comp(buf,mt,(0.60,0.45,0.32)); sn=M()
        for k in range(9):
            mx=205+k*14+(k%2)*10; my=y0+70+k*42; sn.poly([(mx-8,my-3),(mx,my-18),(mx+8,my-3)])
        comp(buf,sn,(1,1,1),sh=0)
        L_=(180,y0+330); Pc=(420,y0+170); u=sm((t-EV["flying"])/2.6)
        rt=M(); n=24
        for i in range(n):
            if i/n>u: break
            if i%2==0:
                a0=i/n; a1=min(u,(i+1)/n); p0=(L_[0]+(Pc[0]-L_[0])*a0,L_[1]+(Pc[1]-L_[1])*a0-60*math.sin(math.pi*a0)); p1=(L_[0]+(Pc[0]-L_[0])*a1,L_[1]+(Pc[1]-L_[1])*a1-60*math.sin(math.pi*a1)); rt.line(p0,p1,3.2)
        comp(buf,rt,(0.85,0.25,0.25),sh=0.1)
        for p in (L_,Pc): comp(buf,M().circ(p[0],p[1],8),(0.15,0.15,0.2))
        px=L_[0]+(Pc[0]-L_[0])*u; py=L_[1]+(Pc[1]-L_[1])*u-60*math.sin(math.pi*u); ang=math.atan2((Pc[1]-L_[1])-60*math.pi*math.cos(math.pi*u),(Pc[0]-L_[0]))
        pl=M().poly(rot([(32,0),(24,-5),(-26,-5),(-26,5),(24,5)],ang,px,py)).poly(rot([(6,-20),(12,-20),(2,20),(-4,20)],ang,px,py)).poly(rot([(-24,-12),(-18,-12),(-20,12),(-26,12)],ang,px,py)); comp(buf,pl,(1,1,1),sh=0.35)
    def hd(d,t=t,pa=pa,pm=pm,y0m=150):
        card(d,"JULIANE KOEPCKE · 17",540,200,fs=46,a=fa(t,EV["name"]-0.1,EV["parents"]-0.7)*pa,ang=-2)
        card(d,"GRADUATED · DEC 23, 1971",540,1180,fs=36,a=fa(t,EV["grad"]-0.1,EV["parents"]-0.7)*pa,bg=(255,212,80),ang=2)
        card(d,"LIMA, PERU",880,290,fs=34,a=fa(t,EV["lima"]-0.1,EV["parents"]-0.7)*pa,fg=(255,255,255),bg=(205,60,55),ang=4)
        card(d,"PARENTS: BIOLOGISTS",540,200,fs=46,a=fa(t,EV["parents"]-0.1,EV["flying"]-0.6)*pa,ang=-2)
        card(d,"A RESEARCH STATION\nIN THE RAINFOREST",770,1150,fs=32,a=fa(t,EV["station"],EV["flying"]-0.6)*pa,bg=(255,212,80),ang=2)
        if pm>0.01:
            mp=sm((t-EV["flying"]+0.5)/0.6)*(1-sm((t-EV["flight"]+0.5)/0.4)); yo=(1-mp)*1400
            card(d,"LIMA",300,300+660+yo,fs=34,a=mp,ang=-3); card(d,"PUCALLPA",840,300+250+yo,fs=34,a=mp*sm((t-EV["flying"]-1.8)/0.4),ang=3)
            card(d,"THE ANDES",500,300+120+yo,fs=28,a=mp*sm((t-EV["andes"])/0.3),fg=(255,255,255),bg=(120,90,60),ang=-2,torn=False)
            card(d,"HOME FOR CHRISTMAS",540,1210+yo,fs=36,a=mp*sm((t-EV["christmas"])/0.3),fg=(255,255,255),bg=(30,110,70),ang=-1)
        bp=fa(t,EV["flight"]-0.3,SS("lima")["e"]+1,0.5);
        if bp>0.01:
            s_=spring((t-EV["flight"]+0.3)/0.7); yb=620
            card(d,"  LANSA  ·  FLIGHT 508  ",540,yb-150,fs=46,a=bp,fg=(255,255,255),bg=(30,70,140),torn=False,sc=s_)
            card(d,"LIMA   →   PUCALLPA\n24 DEC 1971  ·  ELECTRA L-188",540,yb,fs=40,a=bp,fn="WorkSans-Bold",torn=False,sc=s_,pad=(40,26))
            card(d,"92 ON BOARD",540,yb+170,fs=60,a=bp*sm((t-EV["n92"]+0.1)/0.3),fn="BigShoulders-Bold",fg=(255,255,255),bg=(205,60,55),ang=-4,sc=spring((t-EV["n92"]+0.1)/0.5))
    hud.append(hd)
    if t>EV["flight"]-0.3: buf*=1-0.25*sm((t-EV["flight"]+0.3)/0.5)
    return buf,hud
def s_storm(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    grad(buf,[(0,(0.10,0.08,0.22)),(500,(0.22,0.16,0.38)),(960,(0.12,0.10,0.25))])
    st=t-sc["s"]; sk=sm((t-EV["shook"]+0.3)/0.6)*(1-sm((t-EV["mother"]+0.6)/0.6))+sm((t-EV["struck"])/0.2)
    shx=math.sin(t*37)*5*sk+math.sin(t*23)*3*sk; shy=math.cos(t*31)*5*sk
    fl=0.0
    for e in (EV["wall"]+0.3,EV["flash"],EV["flash"]+0.35,EV["again"],EV["again"]+0.25,EV["struck"]):
        if t>=e: fl=max(fl,math.exp(-(t-e)*6))
    for k,(m,col) in enumerate(zip(SCL,[(0.26,0.20,0.42),(0.34,0.26,0.50),(0.42,0.33,0.58)])):
        comp(buf,m,lerpc(col,(0.9,0.9,1.0),fl*0.5),sh=0.25,ox=-int((t*(40+50*k))%w)+int(shx),oy=int(shy*(k+1)/2))
    if t>=EV["flash"] and t<EV["mother"]-0.3:
        for i,e in enumerate((EV["flash"],EV["again"])):
            if 0<t-e<0.18: bolt(buf,80+i*300,0,140+i*260,420,i+3,a=1-(t-e)/0.18)
    dm=fa(t,EV["mother"]-0.4,EV["struck"]-0.25,0.5,0.25)
    px=270+shx; py=320+shy+math.sin(st*1.3)*8; pang=math.sin(st*0.9)*0.04+sk*0.05*math.sin(t*11)
    br=t-EV["broke"]
    rg=np.random.default_rng(int(t*24))
    for i in range(70):
        x=rg.uniform(0,w); y=rg.uniform(0,h); cv2.line(buf,(int(x),int(y)),(int(x-6),int(y+22)),(0.55,0.55,0.75),1,cv2.LINE_AA)
    if br<0:
        T=lambda pts:rot(pts,pang,px,py,1.35,1.35)
        for m,col in plane_masks(T): comp(buf,m,col,a=1-0.55*dm,sh=0.35)
    else:
        u=eout(br/2.5)
        for side,(dx,dy,da) in ((1,(60,40,0.5)),(-1,(-70,90,-0.7))):
            T=lambda pts,dx=dx,dy=dy,da=da:rot(pts,pang+da*u,px+dx*u,py+dy*u+120*u*u,1.35,1.35)
            cut=M().poly(T([(-300,-200),(5,-200),(-5,-10),(12,0),(-2,15),(8,200),(-300,200)] if side==-1 else [(300,-200),(5,-200),(-5,-10),(12,0),(-2,15),(8,200),(300,200)]))
            cf=cut.f()
            for m,col in plane_masks(T): comp(buf,m.f()*cf,col,sh=0.35,a=1-sm((br-1.2)/0.8))
        g=np.random.default_rng(4); db=M()
        for i in range(26):
            vx,vy=g.uniform(-160,160),g.uniform(-120,60); x=px+vx*br; y=py+vy*br+100*br*br; s=g.uniform(2,6)
            db.poly(rot([(-s,-s*0.5),(s,-s*0.4),(s*0.6,s*0.6),(-s*0.7,s*0.5)],br*g.uniform(2,8),x,y))
        comp(buf,db,(0.85,0.85,0.9),a=1-sm((br-1.3)/0.8))
    gt=t-EV["bags"]
    if 0<gt<4:
        mb,mr=M(),M(); g=np.random.default_rng(8); cols=[(0.85,0.22,0.25),(0.20,0.55,0.35),(0.95,0.75,0.20)]
        for j in range(3):
            mb,mr=M(),M()
            for k in range(3):
                x=g.uniform(-60,200)+gt*g.uniform(120,220); y=g.uniform(420,640)-gt*g.uniform(10,60)+40*gt*gt*0.3; gift(mb,mr,x,y,g.uniform(10,18),gt*g.uniform(-4,4))
            comp(buf,mb,cols[j],sh=0.35,a=1-sm((gt-3)/0.8)); comp(buf,mr,(1,0.95,0.85),sh=0,a=1-sm((gt-3)/0.8))
    if t>=EV["struck"]-0.05 and t<EV["struck"]+0.25: bolt(buf,330,0,px+40,py+12,9,a=1-(t-EV["struck"])/0.3,th=5)
    buf*=(1-0.6*dm)
    buf+=fl*0.35
    def hd(d,t=t,dm=dm):
        card(d,"+25 MIN",540,220,fs=50,a=fa(t,EV["mins"]-0.1,EV["shook"]-0.2),fn="BigShoulders-Bold",bg=(255,212,80),ang=-3)
        card(d,"A WALL OF STORM CLOUDS",540,1150,fs=38,a=fa(t,EV["wall"],EV["shook"]-0.2),fg=(255,255,255),bg=(70,50,120),ang=2)
        card(d,"HER MOTHER",540,420,fs=30,a=dm,fg=(255,255,255),bg=(70,50,120),torn=False)
        card(d,"“That's the end.\nIt's all over.”",540,620,fs=76,a=dm*sm((t-EV["theend"]+0.1)/0.5),fn="InstrumentSerif-Italic",pad=(50,30))
        card(d,"LIGHTNING STRIKE",540,230,fs=56,a=fa(t,EV["struck"],EV["broke"]+1.8),fn="BigShoulders-Bold",fg=(30,30,30),bg=(255,230,90),ang=-3,sc=spring((t-EV["struck"])/0.5))
    hud.append(hd); return buf,hud
def s_fall(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; st=t-sc["s"]
    k=sm(st/5.0); grad(buf,[(0,lerpc((0.16,0.12,0.32),(0.28,0.50,0.85),k)),(960,lerpc((0.40,0.30,0.55),(0.75,0.88,0.98),k))])
    fz=sm((t-EV["forest"]+0.6)/1.6)
    for kk,(m,col) in enumerate(zip(CLS,[(0.85,0.82,0.95),(0.92,0.92,0.98),(1,1,1)])):
        comp(buf,m,col,sh=0.15,ox=-int(kk*90),oy=-int((st*(260+180*kk))%960)+0,a=0.8*(1-fz))
        comp(buf,m,col,sh=0.15,ox=-int(kk*90),oy=-int((st*(260+180*kk))%960)+960,a=0.8*(1-fz))
    if fz>0:
        fv=forest_view(550,550,0.35+0.9*sm((t-EV["forest"])/3.5)**1.5,(t-EV["forest"])*25)
        buf[:]=buf*(1-fz)+fv*fz
    wl=M(); g=np.random.default_rng(int(t*30))
    for i in range(16):
        x=g.uniform(0,w); y=g.uniform(0,h); wl.line((x,y),(x,y-g.uniform(40,90)),1.4)
    comp(buf,wl,(1,1,1),sh=0,a=0.35*(1-fz*0.5),rim=0)
    s_=1.25-0.25*fz
    seats(buf,270+math.sin(st*1.7)*12,330+math.sin(st*2.3)*10,s_,0.25*math.sin(st*1.1),max(0.15,abs(math.cos(st*3.0))))
    bk=sm((t-EV["black"])/0.9); buf*=(1-bk)
    def hd(d,t=t,st=st):
        alt=int(3000*(1-sm((t-EV["m3000"]+0.3)/(EV["black"]-EV["m3000"]+0.6))*0.97)//10*10)
        a=fa(t,sc["s"]+0.6,EV["black"]-0.2)
        card(d,"STILL STRAPPED TO A\nROW OF THREE SEATS",540,1180,fs=36,a=fa(t,EV["row"]-0.1,EV["m3000"]-0.2),ang=-2)
        if t>EV["m3000"]-0.3:
            card(d,f"{alt:,} m",800,220,fs=70,a=a,fn="BigShoulders-Bold",fg=(255,255,255),bg=(205,60,55),torn=False)
            card(d,f"{int(alt*3.281)//10*10:,} ft",800,330,fs=36,a=a*sm((t-EV["ft"])/0.3),fn="BigShoulders-Bold",torn=False)
    hud.append(hd); return buf,hud
def s_wake(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; st=t-sc["s"]
    dk=sm((t-EV["called"]+0.3)/1.0)*0.35
    grad(buf,[(0,(0.20,0.42,0.36)),(700,(0.10,0.28,0.22)),(960,(0.06,0.18,0.14))])
    buf+=(RAYS*0.32)[...,None]*np.array([1.0,0.95,0.7],np.float32)*(1-dk)
    pal=[(0.22,0.42,0.38),(0.16,0.36,0.30),(0.08,0.26,0.20),(0.10,0.34,0.20),(0.06,0.22,0.14)]
    jungle(buf,t,200+st*3,pal,skip=(4,))
    gm=M().rect(-5,640,w+5,h); comp(buf,gm,(0.20,0.30,0.18),sh=0.2)
    seats(buf,330,600,1.0,1.35,1.0,girl_in=False,col=(0.18,0.38,0.52),cold=(0.11,0.25,0.36))
    girl(buf,190,690,1.4,face=1)
    comp(buf,JUNG[4],(0.04,0.16,0.10),ox=-int(200*1.25)%P,sh=0.3)
    lv=M()
    for (x,y,L_,a) in ((-10,960,170,-1.1),(40,980,150,-1.4),(520,970,180,-2.0),(560,940,150,-2.3),(480,990,120,-1.7)): leaf(lv,x,y,L_,L_*0.25,a)
    comp(buf,lv,(0.05,0.20,0.12),sh=0.35)
    buf*=(1-dk)
    ey=sm((t-EV["woke"]+0.4)/1.4)
    if ey<1:
        lid=(1-ey)*(h/2+40); m=np.clip(np.minimum(yy-lid,(h-lid)-yy)/30,0,1)*(0.3+0.7*ey) if ey>0 else np.zeros_like(yy)
        buf*=m[...,None]
    def hd(d,t=t):
        items=[("BROKEN COLLARBONE",EV["collar"]),("DEEP CUTS",EV["cuts"]),("CONCUSSION",EV["conc"]),("ONE EYE SWOLLEN",EV["eye"]),("NO GLASSES",EV["glasses"]),("ONE SHOE",EV["shoe"])]
        pe=EV["nobody"]-0.4
        pa=fa(t,EV["collar"]-0.4,pe)
        if pa>0.01:
            card(d,"FIELD NOTES",540,180,fs=34,a=pa,fg=(255,255,255),bg=(205,60,55),torn=False,ang=-2)
            for i,(s,e) in enumerate(items):
                card(d,("✕  " if False else "")+s,540,270+i*82,fs=40,a=pa*sm((t-e+0.05)/0.25),ang=(i%2-0.5)*3,sc=0.9+0.1*spring((t-e)/0.4))
        a=fa(t,EV["nobody"]-0.1,EV["called"]-0.4)
        card(d,"NOBODY KNOWS EXACTLY HOW",540,200,fs=40,a=a,bg=(255,212,80),ang=-2)
        card(d,"SPINNING\nSEATS?",320,400,fs=50,a=a*sm((t-EV["spinseats"])/0.3),fn="Gloock-Regular",ang=-3,sc=spring((t-EV["spinseats"])/0.5))
        card(d,"THICK\nTREES?",760,430,fs=50,a=a*sm((t-EV["trees"])/0.3),fn="Gloock-Regular",ang=3,sc=spring((t-EV["trees"])/0.5))
        for k,(x,y,s) in enumerate(((560,330,120),(300,500,92),(800,600,70))):
            e=EV["mom"]+k*0.45; aa=sm((t-e)/0.3)*(1-sm((t-e-0.9)/0.6))*(1-0.3*k)
            if aa>0.01: txt_hand(d,"Mom...?",x,y,s,(255,250,235),aa)
    hud.append(hd); return buf,hud
def txt_hand(d,s,x,y,fs,col,a): B.txt(d,(x,y),s,F("NothingYouCouldDo-Regular",fs),col+(int(255*a),),anchor="mm",stroke=2)
def s_rule(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; st=t-sc["s"]
    zm=sm((t-EV["creek"]+0.3)/2.2); s_=1+2.2*zm; cx,cy=270+0*zm,330
    buf[:]=(0.98,0.95,0.86)
    def X(p): return ((p[0]-cx)*s_+cx,(p[1]-cy)*s_+cy+zm*120)
    ln=M()
    for y in range(90,960,34): ln.line(X((0,y)),X((w,y)),1.0)
    comp(buf,ln,(0.62,0.75,0.88),sh=0,rim=0,a=0.8)
    comp(buf,M().line(X((62,0)),X((62,h)),1.6),(0.88,0.45,0.45),sh=0,rim=0)
    ink=(0.10,0.18,0.42)
    def drawp(pts,u,th,col=ink):
        n=len(pts); k=max(2,int(n*cl(u)))
        if u>0.01: comp(buf,M().pline([X(p) for p in pts[:k]],th*s_),col,sh=0,rim=0)
    u1=sm((t-EV["water"]+0.2)/0.6)
    if u1>0:
        dp=M().poly([X(p) for p in [(270,150),(256,180),(258,196),(270,204),(282,196),(284,180)]]); comp(buf,dp,(0.35,0.62,0.90),sh=0.0,a=u1); drawp([(270,150),(256,180),(258,196),(270,204),(282,196),(284,180),(270,150)],u1,2.2)
    stream=[(270+math.sin(i/6)*26+i*0.6,215+i*5) for i in range(60)]
    drawp(stream,sm((t-EV["downhill"])/1.4),2.6,(0.25,0.50,0.85))
    riv=[(306+math.sin(i/5)*30,515+i*3) for i in range(1)]
    ur=sm((t-EV["rivers"])/1.0)
    if ur>0:
        rp=[(300+math.sin(i/7)*30,515+i*4.0) for i in range(int(18*ur)+2)]
        comp(buf,M().pline([X(p) for p in rp],12*s_),(0.30,0.58,0.88),sh=0,rim=0)
    up=spring((t-EV["people"])/0.6)
    if up>0.02:
        mw,mr,md=M(),M(),M()
        for k,(hx,hy) in enumerate(((420,575),(465,588))): hut(mw,mr,md,*X((hx,hy)),0.42*up*s_)
        comp(buf,mw,(0.95,0.85,0.65),sh=0.15); comp(buf,mr,(0.80,0.35,0.25),sh=0.1); comp(buf,md,ink,sh=0)
    if t>EV["walk"]-0.3:
        k_=sm((t-EV["walk"]+0.3)/1.5); p=stream[min(59,int(5+k_*20))]; girl(buf,*X((p[0]+8,p[1])),0.3*s_,ph=t*8,walk=1.0)
    def hd(d,t=t,X=X,s_=s_,zm=zm):
        a=1-zm
        txt_hand(d,"Dad's rule:",540,200,84,(26,46,107),fa(t,EV["father"]-0.2,99)*a)
        for (s,x,y,e,fs) in (("find water",780,370,EV["water"],58),("follow it downhill",790,640,EV["downhill"],52),("streams become\nrivers",290,1000,EV["rivers"],52),("rivers lead to people!",700,1270,EV["people"],50)):
            px,py=X((x/2,y/2)); aa=sm((t-e)/0.3)*a
            if aa>0.01: txt_hand(d,s,px*2,py*2,int(fs*s_),(26,46,107),aa)
        card(d,"IF YOU ARE LOST:",300,290,fs=34,a=fa(t,EV["lost"]-0.2,EV["creek"]-0.3),fg=(255,255,255),bg=(205,60,55),ang=-4,torn=False)
    hud.append(hd); return buf,hud
def s_walk(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; st=t-sc["s"]
    md=fa(t,EV["day4"]-0.4,EV["cut"]-0.4,0.6,0.6)
    grad(buf,[(0,(0.62,0.85,0.80)),(500,(0.42,0.72,0.62)),(960,(0.20,0.45,0.35))])
    buf+=(RAYS*0.25)[...,None]*np.array([1.0,0.95,0.7],np.float32)
    cam=st*38
    pal=[(0.35,0.62,0.58),(0.20,0.50,0.40),(0.10,0.38,0.26),(0.08,0.30,0.16),(0.05,0.20,0.12)]
    wb=(640,760,(0.30,0.66,0.74),(0.80,0.95,1.0))
    for k,m in enumerate(JUNG[:3]): comp(buf,m,pal[k],sh=0.3 if k>1 else 0.15,ox=-int((cam*(0.15,0.3,0.55)[k])%P))
    if md>0.01:
        sx=420-(t-EV["day4"]+0.4)*20
        seats(buf,sx,600,0.8,0.25,1.0,girl_in=False,col=(0.45,0.50,0.55),cold=(0.35,0.38,0.42),a=md*0.9)
        fl=M();
        for k in range(5): fl.ell(sx+math.cos(k*1.256)*6,560+math.sin(k*1.256)*6,6,3.5,k*72)
        comp(buf,fl,(1,1,1),a=md*sm((t-EV["notamong"])/0.6)); comp(buf,M().circ(sx,560,2.5),(1,0.85,0.3),a=md*sm((t-EV["notamong"])/0.6),sh=0)
    waterband(buf,t,wb,-30,cam)
    girl(buf,230,720,1.5,ph=t*5.5,walk=0.9,wade=700)
    comp(buf,JUNG[3],pal[3],sh=0.3,ox=-int(cam%P),oy=110)
    comp(buf,JUNG[4],pal[4],sh=0.3,ox=-int((cam*1.25)%P))
    if md>0:
        gy=buf.mean(2,keepdims=True); buf[:]=buf*(1-0.45*md)+gy*0.45*md; buf*=1-0.18*md
    ft=t-EV["flies"]
    if ft>0:
        for k in range(2):
            fx=262+math.cos(ft*7+k*3)*22; fy=640+math.sin(ft*9+k)*14
            comp(buf,M().circ(fx,fy,2.6),(0.1,0.1,0.1),sh=0); comp(buf,M().ell(fx-2,fy-3,3,1.6,30),(0.9,0.95,1),sh=0,a=0.8)
    def hd(d,t=t):
        e4=EV["day4"]; s0=sc["s"]
        n=1+int(3*cl((t-s0)/(e4-s0))) if t<e4 else (4 if t<EV["cut"] else 5+int(2*cl((t-EV["cut"])/3)))
        dayc(d,n,fa(t,s0+0.3,sc["e"]+1))
        a=fa(t,EV["sweets"]-0.1,EV["day4"]-0.5)
        if a>0.01:
            card(d,"ONLY FOOD:\nA BAG OF SWEETS",620,300,fs=40,a=a,ang=2,sc=spring((t-EV["sweets"]+0.1)/0.5))
            for k,c in enumerate([(230,70,70),(60,140,220),(250,190,40),(80,180,90),(200,90,200)]):
                x=440+k*90; y=470+(k%2)*24; aa=a*sm((t-EV["sweets"]-0.2-k*0.1)/0.2)
                if aa>0.01: d.ellipse([x-24,y-18,x+24,y+18],fill=c+(int(255*aa),)); d.polygon([(x-24,y),(x-44,y-14),(x-44,y+14)],fill=c+(int(255*aa),)); d.polygon([(x+24,y),(x+44,y-14),(x+44,y+14)],fill=c+(int(255*aa),))
        card(d,"INFECTED",780,330,fs=54,a=fa(t,EV["worse"]-0.1,sc["e"]+1),fn="BigShoulders-Bold",fg=(255,255,255),bg=(205,60,55),ang=4,sc=spring((t-EV["worse"]+0.1)/0.5))
    hud.append(hd); return buf,hud
def river_path(y,ph=0.0): return 270+110*math.sin(y/150+ph)+40*math.sin(y/61+ph*1.7)
def s_river(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; st=t-sc["s"]
    sv=sm((t-EV["saw"]+0.5)/0.6)
    if sv<1:
        zo=sm(st/9.0); scl=1.25-0.75*zo
        fv=forest_view(550,550+st*12,scl,0); buf[:]=fv
        wd=4+10*sm((t-EV["creekb"])/0.8)+16*sm((t-EV["stream"])/1.0)+30*sm((t-EV["riverw"])/1.2)+16*sm((t-EV["day10"])/2)
        wd*=scl/0.9
        pts=[(river_path(y/scl+st*12+0),y) for y in range(-20,h+40,10)]
        sh_=M().pline([(x+4,y+6) for x,y in pts],wd+6); comp(buf,sh_,(0.02,0.10,0.08),sh=0,rim=0,a=0.6)
        rv=M().pline(pts,wd); comp(buf,rv,WATER,sh=0,rim=0)
        hl=M(); g=np.random.default_rng(2)
        for i in range(30):
            y=(g.uniform(0,h)+st*60)%h; x=river_path(y/scl+st*12)+g.uniform(-0.3,0.3)*wd; hl.line((x,y),(x,y+g.uniform(8,20)),1.4)
        comp(buf,hl,(0.9,0.98,1.0),sh=0,rim=0,a=0.7)
        gy=520; gx=river_path(gy/scl+st*12)
        comp(buf,M().circ(gx,gy,5),DRESS,sh=0.4); comp(buf,M().circ(gx+1,gy-6,3.4),HAIR,sh=0.2)
        buf*=1-0.25*sm((t-EV["day10"])/1.5)
    if sv>0:
        b2=np.zeros_like(buf); grad(b2,[(0,(0.95,0.82,0.62)),(520,(0.80,0.78,0.62)),(960,(0.30,0.50,0.45))])
        rgrad(b2,400,300,180,(1.0,0.8,0.5),0.3)
        pal=[(0.55,0.62,0.55),(0.32,0.50,0.40),(0.18,0.40,0.28),(0.10,0.32,0.18),(0.06,0.22,0.12)]
        cam=(t-EV["saw"])*12
        for k,m in enumerate(JUNG[:3]): comp(b2,m,pal[k],sh=0.25,ox=-int((cam*(0.15,0.3,0.55)[k])%P),oy=40)
        waterband(b2,t,(560,h,(0.38,0.70,0.76),(0.85,0.97,1.0)),-20,cam)
        bank=M().poly([(300,h+5),(370,610),(420,570),(w+5,555),(w+5,h+5)]); comp(b2,bank,(0.30,0.48,0.24),sh=0.35)
        comp(b2,M().poly([(300,h+5),(370,610),(420,570),(440,572),(395,615),(330,h+5)]),(0.55,0.42,0.28),sh=0.1)
        u=spring((t-EV["path"])/0.6)
        if u>0.02: comp(b2,M().pline([(360,620),(410,600),(470,590),(540,575)],10*u),(0.82,0.70,0.48),sh=0.1)
        u=spring((t-EV["shelter"])/0.6)
        if u>0.02:
            mw,mr,md_=M(),M(),M(); hut(mw,mr,md_,470,585,0.75*u,True); comp(b2,md_,(0.30,0.20,0.12)); comp(b2,mw,(0.80,0.62,0.40)); comp(b2,mr,(0.60,0.50,0.25))
        u=spring((t-EV["boat"])/0.6)
        if u>0.02: bm=M(); boat(bm,330,600+math.sin(t*2)*2,0.9*u,0.03); comp(b2,bm,(0.50,0.30,0.18),sh=0.35)
        girl(b2,130,700+math.sin(t*1.6)*3,1.2,wade=680)
        b2*=0.85+0.15*sv
        buf[:]=buf*(1-sv)+b2*sv
    def hd(d,t=t,sv=sv):
        n=7+int(3*cl((t-sc["s"])/(EV["day10"]-sc["s"]))) if t<EV["day10"] else 10
        dayc(d,n,fa(t,sc["s"]+0.2,sc["e"]+1))
        for s,e,e2,x,y in (("CREEK",EV["creekb"],EV["stream"],760,520),("STREAM",EV["stream"],EV["riverw"],760,520),("RIVER",EV["riverw"],EV["day10"]-0.2,760,520)):
            card(d,s,x,y,fs=56,a=fa(t,e-0.1,e2-0.15,0.2,0.2),fn="BigShoulders-Bold",fg=(255,255,255),bg=(30,110,140),ang=3,sc=spring((t-e+0.1)/0.4))
        a=fa(t,EV["day10"],EV["saw"]-0.5); card(d,"LETTING THE CURRENT\nCARRY HER",540,1150,fs=36,a=a,ang=-2)
        for s,e,x,y in (("A BOAT",EV["boat"],330,1040),("A PATH",EV["path"],720,1000),("A SHELTER",EV["shelter"],880,880)):
            card(d,s,x,y,fs=34,a=sm((t-e)/0.3),fg=(255,255,255) if s!="A PATH" else (30,30,30),bg=(205,60,55) if s!="A PATH" else (255,212,80),ang=(-3 if x<500 else 3))
    hud.append(hd); return buf,hud
def s_hut(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; st=t-sc["s"]
    dusk=sm((t-EV["lay"]+0.3)/1.5)
    for i in range(0,w,54):
        c=(0.55,0.36,0.20) if (i//54)%2==0 else (0.50,0.32,0.18); buf[:,i:i+54]=c
    comp(buf,M().rect(330,120,500,330),lerpc((0.75,0.92,0.80),(0.30,0.30,0.50),dusk),sh=0.4)
    comp(buf,M().rect(410,120,418,330).rect(330,222,500,230),(0.40,0.26,0.14),sh=0.2)
    rgrad(buf,415,225,180,(1.0,0.85,0.55),0.35*(1-dusk))
    fl=M().rect(-5,700,w+5,h); comp(buf,fl,(0.42,0.28,0.16),sh=0.4)
    if dusk>0:
        rg=np.random.default_rng(int(t*20))
        for i in range(20):
            x=rg.uniform(334,496); y=rg.uniform(124,320); cv2.line(buf,(int(x),int(y)),(int(x-2),int(y+10)),(0.7,0.75,0.9),1,cv2.LINE_AA)
    cm=1-sm((t-EV["dog"]+0.3)/0.5)*0.0
    u=spring((t-EV["gas"]+0.2)/0.6)
    if u>0.02:
        cx,cy=180,560; s_=u*1.15
        can=M().poly([(cx-50*s_,cy-70*s_),(cx+30*s_,cy-70*s_),(cx+50*s_,cy-50*s_),(cx+50*s_,cy+80*s_),(cx-50*s_,cy+80*s_)]); comp(buf,can,(0.82,0.16,0.14),sh=0.45)
        comp(buf,M().rect(cx-34*s_,cy-96*s_,cx-10*s_,cy-70*s_),(0.25,0.25,0.25)); comp(buf,M().rect(cx-20*s_,cy-40*s_,cx+30*s_,cy+40*s_),(0.95,0.88,0.40),sh=0.1)
    fb=fa(t,EV["remem"]-0.2,EV["poured"]-0.3,0.4,0.4)
    if fb>0.01:
        cxm,cym,R=215,300,112; circ=M().circ(cxm,cym,R); comp(buf,circ,(0.92,0.84,0.66),sh=0.45,a=fb)
        sil=M(); sil.circ(cxm-40,cym-60,16).poly([(cxm-62,cym-40),(cxm-18,cym-40),(cxm-12,cym+50),(cxm-68,cym+50)])
        sil.ell(cxm+40,cym+30,40,18).circ(cxm+80,cym+12,14).poly([(cxm+84,cym+2),(cxm+96,cym-10),(cxm+92,cym+10)])
        for lx in (cxm+14,cxm+60): sil.rect(lx,cym+40,lx+7,cym+70)
        sil.line((cxm+2,cym+18),(cxm-30,cym-8),4)
        circf=circ.f(); comp(buf,sil.f()*circf,(0.45,0.32,0.20),sh=0,a=fb,rim=0)
    girl(buf,400,700,2.2,face=-1)
    buf*=1-0.45*dusk
    if dusk>0:
        g=np.random.default_rng(3)
        for i in range(10):
            x=g.uniform(40,500)+math.sin(t*0.7+i)*20; y=g.uniform(300,700)+math.cos(t*0.9+i*2)*15; aa=dusk*(0.5+0.5*math.sin(t*3+i*1.7))
            rgrad(buf,x,y,6,(1.0,0.95,0.5),0.5*aa)
    def hd(d,t=t):
        card(d,"GASOLINE",360,800,fs=46,a=fa(t,EV["gas"],EV["remem"]-0.3),fn="BigShoulders-Bold",fg=(255,255,255),bg=(205,60,55),ang=-3)
        card(d,"WHAT HER FATHER DID\nFOR AN INJURED DOG",430,880,fs=32,a=fa(t,EV["remem"]-0.1,EV["poured"]-0.4),ang=2)
        a=fa(t,EV["poured"]-0.1,EV["lay"]-0.4)
        if a>0.01:
            n=int(30*cl((t-EV["thirty"]+0.3)/(EV["onebyone"]-EV["thirty"]+1.6)))
            card(d,"≈ 30",760,520,fs=110,a=a*sm((t-EV["thirty"])/0.3),fn="BigShoulders-Bold",bg=(255,212,80),ang=3)
            card(d,"MAGGOTS REMOVED",760,700,fs=34,a=a*sm((t-EV["thirty"])/0.3),ang=3)
            for i in range(n):
                gx=600+(i%10)*34+((i%10)//5)*26; gy=820+(i//10)*86
                d.line([(gx,gy),(gx+6,gy+62)],fill=(250,240,220,int(240*a)),width=7)
                if i%5==4: d.line([(gx-138,gy+50),(gx+12,gy+10)],fill=(255,200,70,int(240*a)),width=7)
        card(d,"…AND WAITED",540,300,fs=60,a=fa(t,EV["waited"]-0.1,sc["e"]+1),fn="Gloock-Regular",ang=-2)
    hud.append(hd); return buf,hud
def s_rescue(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; st=t-sc["s"]
    m92=sm((t-EV["of92"]+0.4)/0.7); bt=fa(t,EV["cleaned"]-0.4,EV["of92"]-0.3,0.5,0.4)
    grad(buf,[(0,(0.86,0.92,0.95)),(500,(0.72,0.86,0.82)),(960,(0.30,0.50,0.42))])
    rgrad(buf,120,200,200,(1.0,0.95,0.8),0.35)
    cam=st*(6 if bt<0.5 else 30)
    pal=[(0.62,0.74,0.72),(0.40,0.60,0.52),(0.22,0.46,0.34),(0.12,0.36,0.22),(0.07,0.24,0.14)]
    for k,m in enumerate(JUNG[:3]): comp(buf,m,pal[k],sh=0.25,ox=-int((cam*(0.15,0.3,0.55)[k])%P),oy=30)
    waterband(buf,t,(600,h,(0.40,0.72,0.78),(0.88,0.98,1.0)),-20 if bt<0.5 else -60,cam)
    if bt<0.99:
        a=1-bt
        bank=M().poly([(260,h+5),(320,650),(370,612),(w+5,598),(w+5,h+5)]); comp(buf,bank,(0.30,0.48,0.24),sh=0.35,a=a)
        comp(buf,M().poly([(260,h+5),(320,650),(370,612),(390,614),(345,655),(290,h+5)]),(0.55,0.42,0.28),sh=0.1,a=a)
        mw,mr,md_=M(),M(),M(); hut(mw,mr,md_,440,625,0.8,True); comp(buf,md_,(0.30,0.20,0.12),a=a); comp(buf,mw,(0.80,0.62,0.40),a=a); comp(buf,mr,(0.60,0.50,0.25),a=a)
        sp=sm((t-EV["spirit"]+0.2)/0.5)*(1-sm((t-EV["cleaned"]+0.6)/0.5))
        if sp>0:
            rgrad(buf,380,640,60,(0.4,0.8,1.0),0.6*sp*(0.8+0.2*math.sin(t*6)))
            for k in range(3):
                r=((t*30+k*25)%75)+10; ring=M().ell(380,690,r*1.4,r*0.35); inner=M().ell(380,690,r*1.4-3,r*0.35-1.5); ring.m=np.clip(ring.m.astype(np.int16)-inner.m,0,255).astype(np.uint8); comp(buf,ring,(0.8,0.95,1.0),sh=0,a=sp*(1-r/85),rim=0)
        girl(buf,380,690,1.2,face=-1)
        wk=sm((t-EV["workers"]+0.2)/2.5)
        for k in range(3):
            x=-60+wk*(150+k*45)-k*40; y=690+k*6
            if x>-40:
                girl(buf,x,y,1.5,ph=t*5+k,walk=1.0*(1-sm((t-EV["workers"]-2.3)/0.4)))
                comp(buf,M().ell(x+2,y-1.5*70*0.97,15,5).circ(x+2,y-1.5*70*1.0,8),(0.80,0.70,0.40),sh=0.2)
    if bt>0.01:
        bx=150+(t-EV["cleaned"])*18; by=640+math.sin(t*2)*3
        bm=M(); boat(bm,bx,by,1.6,0.0)
        for k in range(4):
            x=bx-60+k*38; girl(buf,x,by-2,1.0 if k!=2 else 0.85,face=1)
        comp(buf,bm,(0.50,0.30,0.18),sh=0.35,a=bt)
    gx=int((-cam*1.25)%P)
    comp(buf,JUNG[4],pal[4],sh=0.3,ox=-int((cam*1.25)%P))
    if m92>0:
        b2=np.zeros_like(buf); grad(b2,[(0,(0.12,0.16,0.30)),(960,(0.20,0.26,0.40))])
        dm=M(); gm=M()
        for i in range(92):
            r_,c_=divmod(i,10); x=90+c_*40; y=170+r_*46
            if i==62: gm.circ(x,y,13)
            else: dm.circ(x,y,13)
        comp(b2,dm,(0.55,0.58,0.66),sh=0.3,a=sm((t-EV["of92"]+0.2)/0.6))
        rgrad(b2,90+2*40,170+6*46,36,(1.0,0.8,0.3),0.8*sm((t-EV["only"])/0.4))
        comp(b2,gm,(1.0,0.78,0.25),sh=0.3,a=sm((t-EV["of92"]+0.2)/0.6))
        mt=t-EV["mother2"]
        if mt>-0.5:
            fy=-30+min(mt+0.5,4)*90; fx=300+math.sin(mt*1.2)*30; fl=M()
            for k in range(5): fl.ell(fx+math.cos(k*1.256+mt)*9,fy+math.sin(k*1.256+mt)*9,10,6,math.degrees(k*1.256+mt))
            comp(b2,fl,(1,1,1),sh=0.3); comp(b2,M().circ(fx,fy,4),(1,0.85,0.3),sh=0)
        buf[:]=buf*(1-m92)+b2*m92
    def hd(d,t=t,m92=m92,bt=bt):
        a=fa(t,EV["voices"]-0.1,EV["fright"]-0.3)*(1-m92)
        if a>0.01:
            for k in range(3):
                aa=a*sm((t-EV["voices"]-k*0.3)/0.3); x=150+k*120; y=820-k*60
                card(d,"...",x,y,fs=40,a=aa,torn=False,ang=(k-1)*5)
        card(d,"LOCAL WORKERS",540,250,fs=44,a=fa(t,EV["workers"]-0.1,EV["spirit"]-0.4)*(1-m92),bg=(255,212,80),ang=-2)
        card(d,"“A WATER SPIRIT?”",540,300,fs=64,a=fa(t,EV["spirit"]-0.1,EV["cleaned"]-0.5),fn="Gloock-Regular",fg=(255,255,255),bg=(30,110,140),ang=2,sc=spring((t-EV["spirit"]+0.1)/0.5))
        card(d,"BY BOAT TO A DOCTOR",540,280,fs=44,a=bt*sm((t-EV["byboat"])/0.3),ang=-2)
        card(d,"1 OF 92",540,1255,fs=96,a=m92*sm((t-EV["only"])/0.3),fn="BigShoulders-Bold",fg=(30,30,30),bg=(255,212,80),ang=-2,sc=spring((t-EV["only"])/0.5))
    hud.append(hd); return buf,hud
def s_today(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; st=t-sc["s"]
    grad(buf,[(0,(0.45,0.78,0.95)),(520,(0.80,0.93,0.92)),(960,(0.30,0.60,0.40))])
    comp(buf,M().circ(110,150,50),(1.0,0.85,0.35),sh=0.1); rgrad(buf,110,150,160,(1,0.9,0.5),0.3)
    buf+=(RAYS*0.25)[...,None]*np.array([1.0,0.95,0.7],np.float32)
    cam=st*14
    pal=[(0.40,0.70,0.62),(0.20,0.60,0.40),(0.12,0.50,0.30),(0.10,0.42,0.22),(0.06,0.30,0.16)]
    for k,m in enumerate(JUNG[:3]): comp(buf,m,pal[k],sh=0.25,ox=-int((cam*(0.15,0.3,0.55)[k])%P),oy=40)
    u=spring((t-EV["pang"]+0.3)/0.7)
    mw,mr,md_=M(),M(),M(); hut(mw,mr,md_,300,640,1.3,True); comp(buf,md_,(0.30,0.20,0.12)); comp(buf,mw,(0.88,0.70,0.45)); comp(buf,mr,(0.70,0.55,0.25))
    comp(buf,M().rect(-5,630,w+5,h),(0.22,0.45,0.22),sh=0.3)
    comp(buf,JUNG[3],pal[3],sh=0.3,ox=-int(cam%P),oy=40)
    comp(buf,JUNG[4],pal[4],sh=0.3,ox=-int((cam*1.25)%P))
    for k,(c,ph) in enumerate((((0.20,0.50,0.98),0),((0.98,0.55,0.15),2),((0.20,0.50,0.98),4))):
        x=(100+k*160+st*(20+k*6))%(w+40)-20; y=330+k*60+math.sin(t*1.3+ph)*30; butterfly(buf,x,y,1.4,t+ph,c)
    birds(buf,t,4,col=(0.85,0.20,0.15),y0=200)
    def hd(d,t=t):
        card(d,"STUDIED BIOLOGY",540,230,fs=46,a=fa(t,EV["biology"]-0.1,EV["leads"]-0.3),bg=(255,212,80),ang=-2)
        card(d,"PANGUANA",540,230,fs=76,a=fa(t,EV["pang"]-0.2,sc["e"]+1),fn="Gloock-Regular",fg=(255,255,255),bg=(30,110,70),ang=-2,sc=spring((t-EV["pang"]+0.2)/0.6))
        card(d,"RESEARCH STATION · PERU",540,340,fs=30,a=fa(t,EV["pang"]+0.2,sc["e"]+1),ang=1)
        card(d,"PROTECTING THE FOREST\nTHAT SAVED HER",540,1160,fs=40,a=fa(t,EV["protect"]-0.1,sc["e"]+1),ang=1)
    hud.append(hd); return buf,hud
def s_end(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; st=t-sc["s"]
    scl=0.95-0.45*sm(st/7.0)
    fv=forest_view(550,500,scl,8*math.sin(st*0.1)); buf[:]=fv
    pts=[(river_path(y/scl+300,1.3)+0,y) for y in range(-20,h+40,10)]; wd=26*scl/0.6
    comp(buf,M().pline([(x+4,y+6) for x,y in pts],wd+6),(0.02,0.10,0.08),sh=0,rim=0,a=0.6)
    comp(buf,M().pline(pts,wd),(0.55,0.85,0.95),sh=0,rim=0)
    gl=sm((t-EV["follow"]+0.2)/0.8); ph=(st*0.9)%1.0
    hl=M()
    for y in range(0,h,8):
        if (y/h-ph)%0.25<0.04: hl.circ(river_path(y/scl+300,1.3),y,wd*0.35)
    comp(buf,hl,(1.0,0.95,0.70),sh=0,rim=0,a=0.4+0.5*gl)
    rgrad(buf,270,300,400,(1.0,0.75,0.40),0.25)
    tf=Lx("Follow the water")[1]+0.4
    if t>tf: buf*=max(0.12,1-(t-tf)*0.9)
    def hd(d,t=t,tf=tf):
        card(d,"2 MILES DOWN.\n11 DAYS ALONE.",540,300,fs=56,a=fa(t,EV["fellb"]-0.1,EV["follow"]-0.4),fn="Gloock-Regular",ang=-2)
        card(d,"FOLLOW\nTHE WATER.",540,560,fs=120,a=fa(t,EV["follow"]-0.15,tf+0.2,0.3,0.4),fn="Gloock-Regular",fg=(255,255,255),bg=(30,110,140),ang=-2,sc=spring((t-EV["follow"]+0.15)/0.6))
        if t>tf:
            kk=t-tf; a=sm((kk-0.2)/0.6); lg=LOGO.resize((int(LOGO.width*0.5),int(LOGO.height*0.5)),Image.LANCZOS); al=np.array(lg); al[:,:,3]=(al[:,:,3]*a).astype(np.uint8)
            d._image.alpha_composite(Image.fromarray(al),(W//2-lg.width//2,640-lg.height//2)); B.txt(d,(W//2,1000),"ORBITHOS",B.CZ(72,600),(255,215,140,int(255*a)),anchor="mm",stroke=2)
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,lima=s_lima,storm=s_storm,fall=s_fall,wake=s_wake,rule=s_rule,walk=s_walk,river=s_river,hut=s_hut,rescue=s_rescue,today=s_today,end=s_end)
BAND=(1-0.62*np.exp(-((yy-728)/78)**2))[...,None].astype(np.float32)
VIG=(1-0.28*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.010,(h,w,1)).astype(np.float32) for i in range(6)]
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
def tear_edge(p,seed):
    g=np.random.default_rng(seed); xs=np.arange(w); j=np.cumsum(g.normal(0,2.2,w)); j-=np.linspace(j[0],j[-1],w); j+=8*np.sin(xs/37+seed)
    return (-60+p*(h+140))+j+(xs-w/2)*0.22   # tear line y(x), slight diagonal
TR=0.32
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    buf,hud=render_scene(t,sc)
    tr=None
    if t>nb-TR: tr=(i,i+1,(t-(nb-TR))/(2*TR))
    elif t<pb+TR: tr=(i-1,i,(t-(pb-TR))/(2*TR))
    hk=1.0
    if tr:
        a_,b_,p=tr; p=sm(p)
        if b_==i: bufA,_=render_scene(t,SC[a_]); bufB=buf
        else: bufA=buf; bufB,_=render_scene(t,SC[b_])
        ey=tear_edge(p,a_+3)[None,:]
        mB=np.clip((ey-yy)/1.5,0,1)        # new scene above the tear line
        edge=np.clip(1-np.abs(yy-ey-2.5)/4.0,0,1)*(1-abs(2*p-1)*0.2)
        shadow=np.clip((yy-ey)/14,0,1); shadow=np.exp(-shadow*2.5)*(yy>ey)
        # old paper slides down & tilts slightly as it is ripped away
        dy=int(p*40); bufA=np.roll(bufA,dy,0)
        out=bufB*mB[...,None]+bufA*(1-mB[...,None])*(1-0.45*shadow[...,None])
        out+=edge[...,None]*(np.array([0.97,0.95,0.90],np.float32)-out)*0.95
        buf=out; hk=abs(2*p-1)
    buf=np.clip(buf,0,1.2)
    buf=buf*PT*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*hk).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
TOTAL=B.TOTAL
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
