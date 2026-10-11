import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid42")
for p in ["/home/claude/vid42","/home/claude/vid3","/home/claude/ep1"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
from paper import *
from PIL import Image, ImageDraw
EV=ev.EV; Lx=ev.Lx
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
LOGO=E1.LOGO
# ================= palette (cyanotype blueprint) =================
WH=(0.93,0.96,1.0); GOLD=(1.0,0.80,0.34); CORAL=(1.0,0.46,0.36); CYAN=(0.62,0.94,1.0); PAPER=(0.93,0.91,0.85)
cB=(16,46,96); cW=(242,247,255); cG=(255,204,92); cC=(232,92,74); cP=(240,234,220)
def tag(d,s,x,y,fs=56,a=1.0,sc=1.0,ang=0,fg=cB,bg=cW,pad=(26,8)): card(d,s,x,y,fs=fs,a=a,fg=fg,bg=bg,fn="NationalPark-Bold",torn=False,ang=ang,sc=sc,pad=pad)
def gtag(d,s,x,y,fs=60,a=1.0,sc=1.0,ang=0,pad=(28,8)): tag(d,s,x,y,fs,a,sc,ang,fg=cB,bg=cG,pad=pad)
def ctag(d,s,x,y,fs=56,a=1.0,sc=1.0,ang=-4,pad=(26,8)): tag(d,s,x,y,fs,a,sc,ang,fg=cW,bg=cC,pad=pad)
def hand(d,s,x,y,fs=46,a=1.0,ang=-3,col=cW): card(d,s,x,y,fs=fs,a=a,fg=col,bg=None,fn="NothingYouCouldDo-Regular",torn=False,ang=ang,pad=(6,6))
def nu(d,s,x,y,fs=60,a=1.0,col=cG): card(d,s,x,y,fs=fs,a=a,fg=col,bg=None,fn="Jura-Medium",torn=False,pad=(4,4))
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= background =================
def _n1(n,scale,seed):
    r=np.random.default_rng(seed); a=r.normal(0,1,n//scale+3); return np.interp(np.arange(n),np.arange(len(a))*scale,a)
_L=18+5*_n1(h,40,1)+2*_n1(h,6,2); _R=w-18+5*_n1(h,40,3)+2*_n1(h,6,4)
_T=52+5*_n1(w,40,5)+2*_n1(w,6,6); _Bt=938+6*_n1(w,40,7)+2*_n1(w,6,8)
_D=np.minimum.reduce([xx-_L[:,None],_R[:,None]-xx,yy-_T[None,:],_Bt[None,:]-yy]).astype(np.float32)
_g=np.random.default_rng(42)
_st=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),sigmaX=10,sigmaY=0.7); _st/=_st.std()
_st2=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),sigmaX=0.7,sigmaY=10); _st2/=_st2.std()
_horiz=(np.minimum(yy-_T[None,:],_Bt[None,:]-yy)<np.minimum(xx-_L[:,None],_R[:,None]-xx))
P3=np.clip((_D+2.5*np.where(_horiz,_st,_st2))/5,0,1)[...,None].astype(np.float32)
_mot=cv2.resize(_g.normal(0,1,(20,12)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC); _mot/=_mot.std()
_mot2=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),2.5); _mot2/=_mot2.std()
CY=np.zeros((h,w,3),np.float32); grad(CY,[(0,(0.11,0.31,0.57)),(h*0.75,(0.07,0.22,0.46)),(h,(0.06,0.19,0.40))])
CY*=(1+0.07*_mot+0.025*_mot2)[...,None]
CY+=(np.clip(1-_D/26,0,1)*0.10)[...,None]*np.array((0.5,0.6,0.7),np.float32)
_gm=np.zeros((h,w),np.float32)
for x in range(0,w,30): _gm[:,x]=0.05 if x%150 else 0.10
for y in range(0,h,30): _gm[y,:]=np.maximum(_gm[y,:],0.05 if y%150 else 0.10)
CY+=(_gm[...,None])*(np.array(WH,np.float32)-CY)
PAP=np.zeros((h,w,3),np.float32); grad(PAP,[(0,PAPER),(h,(0.86,0.83,0.76))])
PAP*=(1+0.03*_mot)[...,None]
# ================= drawing helpers =================
def _bb(m):
    x0,y0=max(0,m.x0),max(0,m.y0); x1,y1=min(w,m.x1),min(h,m.y1); return x0,y0,x1,y1
def addm(buf,m,col,a=1.0):
    if m.x1<=m.x0: return
    x0,y0,x1,y1=_bb(m)
    if x1<=x0 or y1<=y0: return
    A=m.m[y0:y1,x0:x1].astype(np.float32)*(a/255)
    buf[y0:y1,x0:x1]+=A[...,None]*np.array(col,np.float32)
def ink(buf,m,a=1.0,col=WH): comp(buf,m,col,sh=0,rim=0,a=a)
def outl(buf,m,a=1.0,th=1,fill=0.10,col=WH,fcol=None):
    if m.x1<=m.x0 or a<=0: return
    x0,y0,x1,y1=_bb(m)
    if x1<=x0 or y1<=y0: return
    A=m.m[y0:y1,x0:x1].astype(np.float32)/255; k=2*th+1
    er=cv2.erode(A,np.ones((k,k),np.uint8)); e=np.clip(A-er,0,1)
    Bf=buf[y0:y1,x0:x1]; c=np.array(col,np.float32); fc=np.array(fcol if fcol else col,np.float32)
    Bf+=(fc-Bf)*(A*fill*a)[...,None]; Bf+=(c-Bf)*(e*a)[...,None]
def glow(buf,x,y,r,col,a=1.0):
    R=int(r*3)+1; x0,y0=max(0,int(x)-R),max(0,int(y)-R); x1,y1=min(w,int(x)+R),min(h,int(y)+R)
    if x1<=x0 or y1<=y0 or a<=0: return
    d2=((xx[y0:y1,x0:x1]-x)**2+(yy[y0:y1,x0:x1]-y)**2)/(r*r)
    buf[y0:y1,x0:x1]+=(np.exp(-d2)*a)[...,None]*np.array(col,np.float32)
def part(pts,u):
    """polyline truncated to fraction u of its length"""
    p=np.asarray(pts,np.float64)
    if u>=1: return p
    if u<=0 or len(p)<2: return p[:1]
    sl=np.hypot(*np.diff(p,axis=0).T); cs=np.concatenate([[0],np.cumsum(sl)]); L=cs[-1]*u
    k=np.searchsorted(cs,L)-1; k=min(max(k,0),len(sl)-1); f=(L-cs[k])/max(sl[k],1e-9)
    return np.vstack([p[:k+1],p[k]+(p[k+1]-p[k])*f])
def dl(m,pts,u=1.0,th=1.4):
    q=part(pts,u)
    if len(q)>=2: m.pline(q,th)
    return m
def circ_pts(cx,cy,rx,ry=None,a0=0,a1=2*math.pi,n=72):
    ry=rx if ry is None else ry
    return [(cx+rx*math.cos(a0+(a1-a0)*i/n),cy+ry*math.sin(a0+(a1-a0)*i/n)) for i in range(n+1)]
def dashc(m,cx,cy,r,n=28,th=1.2,u=1.0,ry=None):
    ry=r if ry is None else ry
    for k in range(int(n*u)):
        if k%2==0: m.pline(circ_pts(cx,cy,r,ry,2*math.pi*k/n,2*math.pi*(k+1)/n,6),th)
    return m
def dim(m,p0,p1,th=1.2,u=1.0):
    p1=(p0[0]+(p1[0]-p0[0])*u,p0[1]+(p1[1]-p0[1])*u)
    m.line(p0,p1,th); dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)+1e-6; ux,uy=dx/L,dy/L; px,py=-uy,ux
    for (x,y),s in ((p0,1),(p1,-1)):
        m.line((x,y),(x+s*ux*9+px*4,y+s*uy*9+py*4),th); m.line((x,y),(x+s*ux*9-px*4,y+s*uy*9-py*4),th)
        m.line((x-px*7,y-py*7),(x+px*7,y+py*7),th)
    return m
def leader(buf,p0,p1,a=1.0):
    if a<=0: return
    m=M().line(p0,p1,1.3).circ(p1[0],p1[1],3); ink(buf,m,a)
def hatch(buf,m,a=0.5,step=7,col=WH):
    """diagonal hatching clipped to mask"""
    if m.x1<=m.x0: return
    x0,y0,x1,y1=_bb(m); A=m.m[y0:y1,x0:x1].astype(np.float32)/255
    pat=(((xx[y0:y1,x0:x1]+yy[y0:y1,x0:x1])%step)<1.3).astype(np.float32)
    Bf=buf[y0:y1,x0:x1]; Bf+=(np.array(col,np.float32)-Bf)*(A*pat*a)[...,None]
def streaks(buf,t,n,seed,a=1.0,ang=1.25,spread=0.22,spd=1.0,L=80,col=GOLD,box=(0,40,w,700),th=1.6,org=None):
    if a<=0 or n<=0: return
    g=np.random.default_rng(seed); ms=[M() for _ in range(4)]; heads=[]
    x0,y0,x1,y1=box; diag=math.hypot(x1-x0,y1-y0); cx,cy=(x0+x1)/2,(y0+y1)/2
    for k in range(n):
        an=ang+g.uniform(-spread,spread); per=g.uniform(0.8,1.5)/spd; ph=g.uniform(0,1); off=g.uniform(-0.55,0.55)*diag
        dx,dy=math.cos(an),math.sin(an)
        if org is None:
            px,py=-dy,dx; p=((t/per+ph)%1)*(diag+2*L)-diag/2-L; hx,hy=cx+px*off+dx*p,cy+py*off+dy*p
        else:
            p=((t/per+ph)%1)*(diag*0.8+L); hx,hy=org[0]+dx*p,org[1]+dy*p
        for j in range(4):
            a0,a1_=j*L/4,(j+1)*L/4
            if org is not None and a1_>p: a1_=p
            if a1_>a0: ms[j].line((hx-dx*a0,hy-dy*a0),(hx-dx*a1_,hy-dy*a1_),th)
        heads.append((hx,hy))
    for j,m in enumerate(ms): addm(buf,m,col,a*(0.95-j*0.22))
    for hx,hy in heads:
        if -6<hx<w+6 and -6<hy<h+6: glow(buf,hx,hy,3.2,col,0.75*a)
def titleblock(buf,d,n,name,a=1.0):
    if d is None:
        m=M().rect(330,64,512,66).rect(330,92,512,94).rect(330,64,332,94).rect(510,64,512,94).rect(392,64,394,94); ink(buf,m,0.55*a)
    else:
        card(d,f"{n}/7",726,158,fs=24,a=0.8*a,fg=cW,bg=None,fn="NationalPark-Bold",torn=False,pad=(2,2))
        card(d,name,904,158,fs=24,a=0.8*a,fg=cW,bg=None,fn="NationalPark-Bold",torn=False,pad=(2,2))
# ================= objects =================
def person_mask(cx,cy,s):
    m=M(); m.circ(cx,cy-270*s,22*s); m.rect(cx-8*s,cy-252*s,cx+8*s,cy-234*s)
    m.poly([(cx-48*s,cy-238*s),(cx+48*s,cy-238*s),(cx+36*s,cy-140*s),(cx+30*s,cy-118*s),(cx-30*s,cy-118*s),(cx-36*s,cy-140*s)])
    for sd in (-1,1):
        m.line((cx+sd*42*s,cy-228*s),(cx+sd*60*s,cy-150*s),15*s); m.line((cx+sd*60*s,cy-150*s),(cx+sd*66*s,cy-82*s),12*s)
        m.circ(cx+sd*66*s,cy-78*s,8*s)
        m.line((cx+sd*17*s,cy-124*s),(cx+sd*21*s,cy-60*s),19*s); m.line((cx+sd*21*s,cy-60*s),(cx+sd*23*s,cy-6*s),15*s)
        m.ell(cx+sd*28*s,cy-4*s,14*s,6*s)
    return m
def person(buf,cx,cy,s,a=1.0,bones=0.0):
    if a<=0: return
    outl(buf,person_mask(cx,cy,s),a=a,th=1,fill=0.10)
    if bones>0:
        b=M(); b.circ(cx,cy-272*s,13*s); b.line((cx,cy-252*s),(cx,cy-130*s),3*s)
        for k in range(5):
            yk=cy-(225-k*17)*s; b.pline(circ_pts(cx,yk+14*s,28*s*(1-k*0.06),14*s,math.pi*1.12,math.pi*1.88,14),2*s)
        b.ell(cx,cy-122*s,24*s,10*s)
        for sd in (-1,1): b.line((cx+sd*18*s,cy-118*s),(cx+sd*22*s,cy-10*s),3*s); b.line((cx+sd*44*s,cy-226*s),(cx+sd*64*s,cy-84*s),3*s)
        hole=M(); hole.circ(cx,cy-272*s,8*s); ink(buf,b,0.55*bones*a); ink(buf,hole,0.0)
def earth(buf,cx,cy,R,u=1.0,a=1.0,layers=True,night=0.0):
    if a<=0: return
    m=dl(M(),circ_pts(cx,cy,R,n=120),u,1.8); ink(buf,m,a)
    if layers:
        ly=M()
        for f in (0.86,0.55,0.19): dashc(ly,cx,cy,R*f,n=40,th=1.1,u=u)
        for k in range(-2,3): dl(ly,circ_pts(cx,cy,R*math.cos(k*0.45),R*0.18,0,math.pi*2,60),u*0.9,1.0) if False else None
        ink(buf,ly,0.45*a)
        mer=M()
        for k in (-0.6,-0.3,0.3,0.6):
            yk=cy+R*k; hw=math.sqrt(max(R*R-(R*k)**2,0)); mer.line((cx-hw*u,yk),(cx+hw*u,yk),1)
        ink(buf,mer,0.22*a)
    if night>0:
        nm=M().poly(circ_pts(cx,cy,R-2,a0=-math.pi/2,a1=math.pi/2,n=60)); hatch(buf,nm,0.45*night*a,step=6)
def nucleus(buf,cx,cy,s=1.0,a=1.0,u=1.0):
    g=np.random.default_rng(5); m=M()
    pts=[(0,0)]+[(math.cos(k*2.4)*r,math.sin(k*2.4)*r) for k,r in enumerate([16]*6+[30]*8)]
    fm=M()
    for k,(x,y) in enumerate(pts[:max(1,int(len(pts)*u))]):
        m.pline(circ_pts(cx+x*s,cy+y*s,12*s,n=24),1.3)
        if k%2==0: fm.circ(cx+x*s,cy+y*s,11*s)
    comp(buf,fm,WH,sh=0,rim=0,a=0.30*a); ink(buf,m,a)
def atom(buf,cx,cy,s,t,a=1.0):
    nucleus(buf,cx,cy,0.6*s,a)
    m=M()
    for k in range(3):
        an=k*math.pi/3; pts=[(cx+math.cos(q)*120*s*math.cos(an)-math.sin(q)*40*s*math.sin(an),cy+math.cos(q)*120*s*math.sin(an)+math.sin(q)*40*s*math.cos(an)) for q in np.linspace(0,2*math.pi,80)]
        m.pline(pts,1.3)
        q=t*2.2+k*2.1; ex,ey=cx+math.cos(q)*120*s*math.cos(an)-math.sin(q)*40*s*math.sin(an),cy+math.cos(q)*120*s*math.sin(an)+math.sin(q)*40*s*math.cos(an)
        e=M().circ(ex,ey,5*s); ink(buf,e,a)
    ink(buf,m,0.6*a)
# ---- PMT wall (precomputed) ----
PMTS=[]
for r_ in range(17):
    for c_ in range(15):
        x=36+c_*33+(16 if r_%2 else 0); y=84+r_*33
        if x<w-20: PMTS.append((x,y))
PMT_BASE=np.zeros((h,w,3),np.float32); PMT_A=np.zeros((h,w),np.float32)
_m=M(); [_m.circ(x,y,13) for x,y in PMTS]; PMT_A=_m.f()
_cen=M(); [_cen.circ(x+3,y+3,6) for x,y in PMTS]; _hi=M(); [_hi.circ(x-5,y-5,3) for x,y in PMTS]
PMT_BASE[:]=np.array((0.86,0.64,0.24),np.float32)
PMT_BASE*=(1-0.45*_cen.f())[...,None]; PMT_BASE+=(0.5*_hi.f())[...,None]
_rim=np.clip(PMT_A-cv2.erode(PMT_A,np.ones((3,3),np.uint8)),0,1); PMT_BASE*=(1-0.5*_rim)[...,None]
def pmt_wall(buf,a=1.0):
    buf*=(1-0.35*a); A=(PMT_A*a)[...,None]; buf[:]=buf*(1-A)+PMT_BASE*A
# ================= scenes =================
def s_hook(t,sc):
    buf=CY.copy(); hud=[]
    z=sm((t-EV["earth"]+0.2)/1.2)
    n=int(10+26*sm((t-EV["trillion"])/2.0))
    streaks(buf,t,n,1,a=1.0,ang=1.35,spread=0.12,spd=1.1)
    if z>0: earth(buf,270,430,215,u=sm((t-EV["earth"]+0.2)/1.0),a=1.0)
    s=1.55*(1-z)+0.13*z; fy=610*(1-z)+218*z
    person(buf,270,fy,s,a=1.0,bones=sm((t-EV["bones"]+0.1)/0.4)*(1-z))
    la=fa(t,EV["skin"]-0.1,EV["earth"]-0.1); lb=fa(t,EV["bones"]-0.1,EV["earth"]-0.1)
    leader(buf,(120,470),(158,415),la); leader(buf,(420,330),(278,330),lb)
    titleblock(buf,None,1,"")
    def hd(d,t=t,la=la,lb=lb):
        titleblock(buf,d,1,"THE GHOSTS")
        gtag(d,"100 TRILLION",540,290,84,a=ap(t,EV["trillion"],EV["earth"]),sc=pop(t,EV["trillion"]-0.1))
        tag(d,"EVERY SECOND",540,410,54,a=ap(t,EV["second"],EV["earth"]),sc=pop(t,EV["second"]-0.1))
        hand(d,"skin",175,985,58,a=la); hand(d,"bones",880,640,58,a=lb)
        tag(d,"THROUGH THE WHOLE EARTH",540,1250,48,a=ap(t,EV["earth"]+0.4,EV["neutrinos"]))
        gtag(d,"NEUTRINOS",540,290,100,a=ap(t,EV["neutrinos"],sc["e"]+1),sc=pop(t,EV["neutrinos"]-0.1))
        ctag(d,"UNCATCHABLE?",540,1250,62,a=ap(t,EV["catch1"],sc["e"]+1),sc=pop(t,EV["catch1"]-0.1))
    hud.append(hd); return buf,hud
LETTER_LINES=["Zürich, 4 Dec. 1930","","Dear Radioactive","Ladies and Gentlemen,"]
_LC={}
def letter_img(nch):
    if nch in _LC: return _LC[nch]
    im=Image.new("RGBA",(760,880),(0,0,0,0)); d=ImageDraw.Draw(im)
    sh=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(sh).rectangle((34,40,740,870),fill=(0,0,0,120)); sh=sh.filter(ImageFilter.GaussianBlur(10)); im.alpha_composite(sh)
    d.rectangle((20,20,724,850),fill=cP+(255,))
    f1=F("IBMPlexSerif-Italic",34); f2=F("IBMPlexSerif-Italic",58)
    d.text((690,70),LETTER_LINES[0],font=f1,fill=(60,56,50,255),anchor="ra")
    left=nch; y=190
    for ln in LETTER_LINES[2:]:
        s=ln[:max(0,left)]; left-=len(ln); d.text((70,y),s,font=f2,fill=(30,30,40,255)); y+=82
    for k in range(7):
        yy_=420+k*52; d.line((70,yy_,690-(k%3)*90,yy_),fill=(150,145,135,255),width=4)
    _LC[nch]=im; return im
def s_pauli(t,sc):
    buf=CY.copy(); hud=[]
    pL=sm((t-EV["letter"]+0.4)/0.5); pC=sm((t-EV["tiny"]+0.4)/0.5); pD=sm((t-EV["person"]+0.2)/0.5)
    dia=(1-0.75*pL*(1-pC))*(1-pD)
    streaks(buf,t,6,2,a=0.35)
    if dia>0:
        u=sm((t-sc["s"]+0.3)/0.9)
        nucleus(buf,140,330,1.4,a=dia,u=u)
        te=EV["decay"]
        if t>te-0.2:
            k=eout((t-te+0.2)/1.0); ex,ey=140-80*k,330+170*k
            ink(buf,dl(M(),[(130,350),(ex,ey)],1.0,1.3),0.6*dia); ink(buf,M().circ(ex,ey,9),dia)
        # energy bars
        bm=M(); bm.rect(330,240,372,560); outl(buf,bm,a=dia*u,th=1,fill=0.25)
        am=M(); am.rect(412,345,454,560); outl(buf,am,a=dia*u,th=1,fill=0.25)
        van=sm((t-EV["vanish"]+0.1)/0.5)
        miss=M(); dl(miss,[(412,240),(454,240),(454,345),(412,345),(412,240)],1.0,1.3)
        if van>0 and pC<=0:
            dm=M()
            for k in range(8): dm.line((412+(k%2)*42,240+k*13),(412+(k%2)*42,246+k*13),1.3)
            for k in range(4): dm.line((412+k*12,240),(418+k*12,240),1.3)
            ink(buf,dm,van*dia)
        if pC>0:
            fl=M().rect(412,345-105*pC,454,345); comp(buf,fl,GOLD,sh=0,rim=0,a=dia*0.9)
            k=eout((t-EV["invisible"]+0.2)/1.1)
            if t>EV["invisible"]-0.2:
                gx,gy=140+110*k,330-130*k; gm=dashc(M(),gx,gy,13,n=12,th=1.5); addm(buf,gm,GOLD,dia); glow(buf,gx,gy,10,GOLD,0.6*dia)
                ink(buf,dl(M(),[(150,315),(gx,gy)],1.0,1.0),0.25*dia)
    if pD>0:
        # ballroom
        cx=270; bufc=M()
        for k in range(7):
            an=math.pi*(0.1+0.8*k/6); bufc.pline([(cx,120),(cx+math.cos(an)*120,150+math.sin(an)*60)],1.3)
            bx,by=cx+math.cos(an)*120,150+math.sin(an)*60; bufc.circ(bx,by+8,4)
        bufc.line((cx,66),(cx,120),1.5); bufc.pline(circ_pts(cx,150,120,60,0,math.pi,40),1.4)
        ink(buf,bufc,pD)
        for k in range(7):
            an=math.pi*(0.1+0.8*k/6); glow(buf,cx+math.cos(an)*120,158+math.sin(an)*60,6,GOLD,0.5*pD*(0.7+0.3*math.sin(t*6+k)))
        sw=math.sin(t*2.6)*0.12
        for sd in (-1,1):
            x0=270+sd*36+math.sin(t*2.6)*20; m=M()
            m.circ(x0,330,16); m.poly([(x0-16,352),(x0+16,352),(x0+sd*8+40*sw,470),(x0-46+30*sw,560),(x0+46+30*sw,560)] if sd<0 else [(x0-16,352),(x0+16,352),(x0+20,470),(x0+18,560),(x0-18,560)])
            m.line((x0,370),(x0-sd*40,410),8)
            outl(buf,m,a=pD,th=1,fill=0.12)
        for k in range(4):
            nx=80+k*120+20*math.sin(t+k); ny=300-((t*40+k*70)%160); nm=M().circ(nx,ny,6).line((nx+5,ny),(nx+5,ny-24),2); ink(buf,nm,0.7*pD*sm(ny/300))
    titleblock(buf,None,2,"")
    def hd(d,t=t,pL=pL,pC=pC,pD=pD):
        titleblock(buf,d,2,"THE LETTER")
        tag(d,"1930",540,290,72,a=ap(t,EV["y1930"],EV["letter"]),sc=pop(t,EV["y1930"]-0.1))
        hand(d,"Wolfgang Pauli",540,410,64,a=ap(t,EV["pauli"],EV["letter"]))
        hand(d,"e⁻",170,1030,60,a=ap(t,EV["decay"]+0.6,EV["person"])*(1-pL*(1-pC)))
        hand(d,"before",700,1150,40,a=ap(t,EV["decay"],EV["letter"]),ang=0); hand(d,"after",866,1150,40,a=ap(t,EV["decay"],EV["letter"]),ang=0)
        hand(d,"?",866,580,90,a=ap(t,EV["vanish"],EV["letter"]),ang=0)
        ctag(d,"ENERGY VANISHES?",540,1260,52,a=ap(t,EV["vanish"],EV["letter"]),sc=pop(t,EV["vanish"]-0.1))
        if pL>0 and pD<1:
            nch=int(np.clip((t-EV["dear"]+0.1)/((Lx("So he wrote")[1]-EV["dear"])*0.9),0,1)*36)
            im=letter_img(nch); sc_=1-0.62*pC; im2=im.resize((int(im.width*sc_),int(im.height*sc_)),Image.BILINEAR)
            ar=np.array(im2); ar[...,3]=(ar[...,3]*pL*(1-pD)).astype(np.uint8); im2=Image.fromarray(ar)
            x=540-(290*pC); y=760+(1-pL)*500-(430*pC); paste(d,im2,x-im2.width/2,y-im2.height/2)
        nu(d,"ν",560,330,96,a=ap(t,EV["invisible"]+0.5,EV["person"]))
        gtag(d,"TINY · INVISIBLE",540,1100,56,a=ap(t,EV["invisible"],EV["desperate"]),sc=pop(t,EV["invisible"]-0.1))
        ctag(d,"“A DESPERATE REMEDY”",540,1250,58,a=ap(t,EV["desperate"],EV["person"]),sc=pop(t,EV["desperate"]-0.1))
        ctag(d,"SKIPPED THE MEETING",540,290,58,a=ap(t,EV["skipped"],sc["e"]+1),sc=pop(t,EV["skipped"]-0.1))
        gtag(d,"…FOR A BALL",540,1250,70,a=ap(t,EV["ball"],sc["e"]+1),sc=pop(t,EV["ball"]-0.1),ang=3)
    hud.append(hd); return buf,hud
def s_ghost(t,sc):
    buf=CY.copy(); hud=[]
    pB=sm((t-EV["sun"]+0.4)/0.5); pC=sm((t-EV["upearth"]+0.3)/0.5); pD=sm((t-EV["lifetime"]+0.3)/0.5)
    aA=1-pB; aB=pB*(1-pC); aC=pC*(1-pD); aD=pD
    if aA>0:
        streaks(buf,t,14,3,a=0.8*aA,ang=0.2,spread=0.6)
        u=sm((t-sc["s"]-0.2)/0.8); m=M()
        for r in (40,80,130): dashc(m,270,330,r,n=36,u=u)
        dl(m,[(100,330),(440,330)],u); dl(m,[(270,170),(270,490)],u); ink(buf,m,0.45*aA)
        glow(buf,270,330,22,GOLD,1.2*aA); ink(buf,M().circ(270,330,7),aA,col=(1,0.95,0.8))
        dim(m2:=M(),(150,560),(390,560),u=u); ink(buf,m2,0.5*aA)
    if aB>0:
        streaks(buf,t,22,4,a=aB,ang=0.0,spread=0.05,spd=1.3,box=(120,170,540,500))
        sunm=M().circ(40,330,170); outl(buf,sunm,a=aB,th=1,fill=0.15,col=WH,fcol=GOLD)
        core=dashc(M(),40,330,60,n=24); addm(buf,core,GOLD,aB); glow(buf,40,330,40,GOLD,0.7*aB)
        for k in range(12):
            an=k*math.pi/6+t*0.2; ink(buf,M().line((40+math.cos(an)*180,330+math.sin(an)*180),(40+math.cos(an)*200,330+math.sin(an)*200),1.5),0.6*aB)
        earth(buf,420,330,75,a=aB,night=sm((t-EV["night"]+0.1)/0.5))
    if aC>0:
        gr=M().rect(0,470,w,690); hatch(buf,gr,0.35*aC,step=8); ink(buf,M().rect(0,468,w,471),aC)
        for k in range(3): ink(buf,dl(M(),[(0,520+k*40+((k*37)%13)),(w,515+k*42)],1.0,1.0),0.3*aC)
        bed=M().rect(140,400,400,440).rect(140,370,152,468).rect(388,395,400,468).rect(150,385,230,402)
        outl(buf,bed,a=aC,th=1,fill=0.12)
        sl=M().ell(190,382,22,14).poly([(210,392),(380,388),(384,402),(210,404)]); outl(buf,sl,a=aC,th=1,fill=0.15)
        streaks(buf,t,20,5,a=aC,ang=-math.pi/2,spread=0.18,spd=1.2,box=(60,60,480,700))
        moon=M().circ(450,140,26); ink(buf,moon,0.85*aC); ink(buf,M().circ(462,132,22),0.0) if False else comp(buf,M().circ(462,132,22),(0.10,0.29,0.55),sh=0,rim=0,a=aC)
    if aD>0:
        streaks(buf,t,16,6,a=0.8*aD,ang=0.5,spread=0.4)
        atom(buf,270,340,1.25,t,a=aD)
        th=EV["atom"]
        if t>th-0.6:
            k=cl((t-th+0.6)/0.6); hx,hy=270-260*(1-k),340-180*(1-k)
            m=M().line((hx-80*0.82,hy-80*0.57),(hx,hy),2.5); addm(buf,m,GOLD,aD); glow(buf,hx,hy,6,GOLD,aD)
            if t>th: f=math.exp(-(t-th)*2.2); glow(buf,270,340,50*(1+(t-th)),(1,0.95,0.7),1.4*f*aD)
    titleblock(buf,None,3,"")
    def hd(d,t=t,aA=aA,aB=aB,aC=aC,aD=aD):
        titleblock(buf,d,3,"THE PARTICLE")
        gtag(d,"NEUTRINO",540,290,92,a=ap(t,EV["named"],EV["sun"]),sc=pop(t,EV["named"]-0.1))
        hand(d,"italian:",380,410,46,a=ap(t,EV["italian"],EV["sun"]))
        tag(d,"“LITTLE NEUTRAL ONE”",540,1000,52,a=ap(t,EV["little"],EV["charge"]),sc=pop(t,EV["little"]-0.1))
        tag(d,"CHARGE:  0",540,1000,58,a=ap(t,EV["charge"],EV["sun"]),sc=pop(t,EV["charge"]-0.1))
        tag(d,"MASS:  ≈ 0",540,1110,58,a=ap(t,EV["mass"],EV["sun"]),sc=pop(t,EV["mass"]-0.1))
        hand(d,"core of the Sun",250,1080,44,a=aB*fa(t,EV["sun"],1e9))
        hand(d,"Earth",840,880,44,a=aB*fa(t,EV["sun"]+0.5,1e9))
        tag(d,"AT NIGHT",540,290,64,a=ap(t,EV["night"],EV["lifetime"]),sc=pop(t,EV["night"]-0.1))
        gtag(d,"…THROUGH YOUR BED",540,410,54,a=ap(t,EV["bed"],EV["lifetime"]),sc=pop(t,EV["bed"]-0.1))
        tag(d,"YOUR WHOLE LIFE:",540,290,58,a=ap(t,EV["lifetime"],sc["e"]+1))
        gtag(d,"≈ 1 HIT",540,1180,86,a=ap(t,EV["onehit"],sc["e"]+1),sc=pop(t,EV["onehit"]-0.1))
    hud.append(hd); return buf,hud
TELE=["THANKS FOR MESSAGE.","EVERYTHING COMES TO HIM","WHO KNOWS HOW TO WAIT.","— PAULI"]
def s_catch(t,sc):
    buf=CY.copy(); hud=[]
    pB=sm((t-EV["y1956"]+0.4)/0.5); pC=sm((t-EV["telegram"]+0.3)/0.6)
    aA=1-pB; aB=pB*(1-0.7*pC)
    if aA>0:
        u=sm((t-EV["trap"]+0.3)/1.0)
        m=M(); box=[(150,300),(330,240),(430,290),(250,350),(150,300)]
        dl(m,box,u); dl(m,[(150,300),(150,540),(250,590),(430,540),(430,290)],u); dl(m,[(250,350),(250,590)],u)
        ink(buf,m,aA); dim(m2:=M(),(130,310),(130,550),u=u); ink(buf,m2,0.5*aA)
        streaks(buf,t,10,7,a=0.7*aA,ang=0.9,spread=0.3)
        ink(buf,dashc(M(),270,215,40,n=16,u=sm((t-EV["catchg"]+0.2)/0.6)),0.6*aA); glow(buf,270,215,10,GOLD,0.8*aA*sm((t-EV["catchg"])/0.4))
    if aB>0:
        gr=M().rect(26,560,w,690); hatch(buf,gr,0.3*aB,step=9); ink(buf,M().rect(26,558,w,561),aB)
        rb=M().rect(50,420,230,560).poly(circ_pts(140,420,90,70,math.pi,2*math.pi,40)); outl(buf,rb,a=aB*sm((t-EV["reactor"]+0.2)/0.5+0.6),th=1,fill=0.12)
        ch=M().poly([(190,560),(200,250),(222,250),(232,560)]); outl(buf,ch,a=aB,th=1,fill=0.10)
        dm=M()
        for k in range(3):
            y0=380+k*60; dm.rect(330,y0,470,y0+50)
        outl(buf,dm,a=aB*sm((t-EV["detector"]+0.2)/0.5),th=1,fill=0.14)
        streaks(buf,t,18,8,a=aB,ang=0.02,spread=0.5,org=(140,420),spd=1.4,L=60)
        tc=EV["caught"]
        if t>tc-0.1:
            f=math.exp(-(t-tc)*1.6); glow(buf,400,465,60,(1,0.95,0.7),1.5*f*aB); comp(buf,M().rect(330,440,470,490),GOLD,sh=0,rim=0,a=0.5*aB*(0.4+0.6*f))
    titleblock(buf,None,4,"")
    def hd(d,t=t,aA=aA,aB=aB,pC=pC):
        titleblock(buf,d,4,"THE TRAP")
        hand(d,"how do you catch a ghost?",540,290,52,a=ap(t,EV["catchg"],EV["y1956"]))
        gtag(d,"A GIANT TRAP",540,1250,66,a=ap(t,EV["trap"],EV["y1956"]),sc=pop(t,EV["trap"]-0.1))
        tag(d,"1956",540,290,72,a=ap(t,EV["y1956"],EV["telegram"]),sc=pop(t,EV["y1956"]-0.1))
        hand(d,"C. Cowan & F. Reines",540,400,54,a=ap(t,EV["cowan"],EV["telegram"]))
        tag(d,"NUCLEAR REACTOR",280,1180,40,a=ap(t,EV["reactor"],EV["telegram"])*(1-pC))
        tag(d,"DETECTOR",800,1180,40,a=ap(t,EV["detector"],EV["telegram"])*(1-pC))
        hand(d,"South Carolina",540,1265,48,a=ap(t,EV["carolina"],EV["caught"]))
        gtag(d,"CAUGHT!",800,700,76,a=ap(t,EV["caught"],EV["telegram"]),sc=pop(t,EV["caught"]-0.1),ang=-5)
        if pC>0:
            tag(d,"TELEGRAM → PAULI",540,300,50,a=pC)
            if t>EV["replied"]-0.2:
                tot=sum(len(x) for x in TELE); n=int(np.clip((t-EV["replied"]+0.2)/max(0.5,(EV["wait"]-EV["replied"]+0.6)),0,1)*tot)
                rows=[];left=n
                for ln in TELE: rows.append(ln[:max(0,left)]); left-=len(ln)
                s="\n".join(r if r else " " for r in rows)
                card(d,s,540,760,fs=50,a=sm((t-EV["replied"]+0.2)/0.3),fg=(30,30,36),bg=cP,fn="IBMPlexMono-Bold",torn=True,pad=(40,30),lsp=1.35) if False else _tele(d,rows,sm((t-EV["replied"]+0.2)/0.3))
    hud.append(hd); return buf,hud
def _tele(d,rows,a):
    im=Image.new("RGBA",(900,460),(0,0,0,0)); dd=ImageDraw.Draw(im)
    sh=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(sh).rectangle((30,36,890,450),fill=(0,0,0,120)); sh=sh.filter(ImageFilter.GaussianBlur(9)); im.alpha_composite(sh)
    dd.rectangle((14,14,880,440),fill=cP+(255,)); dd.rectangle((14,14,880,70),fill=(210,196,160,255))
    dd.text((40,26),"WESTERN UNION · 1956",font=F("IBMPlexMono-Bold",30),fill=(60,50,40,255))
    f=F("IBMPlexMono-Bold",44)
    for k,r in enumerate(rows): dd.text((44,104+k*78),r,font=f,fill=(30,30,36,255))
    ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); paste(d,Image.fromarray(ar),540-450,760-230)
def s_superk(t,sc):
    buf=CY.copy(); hud=[]
    pB=sm((t-EV["walls"]+0.4)/0.6); aA=1-pB
    if aA>0:
        u=sm((t-sc["s"]-0.1)/1.0)
        mt=[(26,300),(110,230),(200,130),(260,160),(330,110),(420,210),(514,260)]
        mm=M().poly(mt+[(514,680),(26,680)]); hatch(buf,mm,0.28*aA*u,step=9)
        ink(buf,dl(M(),mt,u,1.8),aA)
        tk=M().rect(180,420,360,620); comp(buf,tk,(0.08,0.24,0.48),sh=0,rim=0,a=aA*sm((t-EV["tank"]+0.2)/0.5))
        fill=sm((t-EV["water"]+0.6)/1.2)
        if fill>0: comp(buf,M().rect(182,620-198*fill,358,620),(0.30,0.62,0.85),sh=0,rim=0,a=0.55*aA)
        tm=M(); dl(tm,[(180,420),(180,620),(360,620),(360,420),(180,420)],sm((t-EV["tank"]+0.2)/0.7),1.8); ink(buf,tm,aA)
        ink(buf,dim(M(),(470,215),(470,420),u=sm((t-EV["mountain"]+0.1)/0.6)),0.7*aA)
        streaks(buf,t,8,9,a=0.6*aA,ang=1.4,spread=0.2)
    if pB>0:
        pmt_wall(buf,pB)
        rr=sm((t-EV["ring"]+0.2)/0.4); y01=EV["y2001"]
        if rr>0 and t<y01+0.6:
            rr*=1-sm((t-y01+0.1)/0.6)
            hits=[]
            for (x,y) in PMTS:
                e=math.hypot((x-270)/140,(y-300)/120); v=math.exp(-((e-1)/0.11)**2)*rr
                if v>0.15: hits.append((x,y,v))
            for x,y,v in hits: glow(buf,x,y,16,CYAN,0.9*v*pB)
            tr=EV["hits"]
            if t>tr-0.5:
                k=cl((t-tr+0.5)/0.5); hx,hy=270-200*(1-k),300-250*(1-k); m=M().line((hx-50,hy-62),(hx,hy),2); addm(buf,m,GOLD,pB*(1-rr*0.5))
        if t>y01-0.3:
            ox,oy=270,640; t0=EV["imploded"]; v=150.0
            sh=M()
            if t>t0:
                for k in range(4):
                    r=(t-t0-k*0.35)*v
                    if 0<r<900: sh.pline(circ_pts(ox,oy,r,r*0.85,math.pi,2*math.pi,60),1.5)
                addm(buf,sh,WH,0.5*pB)
            br=M(); cr=M()
            for (x,y) in PMTS:
                tt=t0+math.hypot(x-ox,(y-oy)/0.85)/v
                if t>tt:
                    br.circ(x,y,13)
                    cr.line((x-9,y-6),(x+2,y+1),1).line((x+2,y+1),(x+8,y-9),1).line((x+2,y+1),(x-2,y+10),1)
                    if t-tt<0.25: glow(buf,x,y,14,(1,0.9,0.7),1.0*(1-(t-tt)/0.25)*pB)
            comp(buf,br,(0.05,0.10,0.18),sh=0,rim=0,a=0.85*pB); ink(buf,cr,0.6*pB,col=(0.8,0.85,0.9))
            if t<t0 and t>EV["cracked"]-0.1:
                x,y=min(PMTS,key=lambda p:math.hypot(p[0]-ox,p[1]-oy)); glow(buf,x,y,18,CORAL,0.8*(0.5+0.5*math.sin(t*30)))
    titleblock(buf,None,5,"")
    def hd(d,t=t,pB=pB):
        titleblock(buf,d,5,"SUPER-K")
        hand(d,"Japan",300,290,56,a=ap(t,EV["japan"],EV["superk"]))
        tag(d,"SUPER-KAMIOKANDE",540,290,64,a=ap(t,EV["superk"],EV["walls"]),sc=pop(t,EV["superk"]-0.1))
        hand(d,"≈1 km of rock",770,640,40,a=ap(t,EV["mountain"],EV["walls"]),ang=-80) if False else hand(d,"deep inside",820,600,40,a=ap(t,EV["mountain"],EV["walls"]),ang=-4)
        gtag(d,"50,000 TONS OF WATER",540,1270,52,a=ap(t,EV["tons"],EV["walls"]),sc=pop(t,EV["tons"]-0.1))
        gtag(d,"≈ 11,000 SENSORS",540,290,64,a=ap(t,EV["eleven"],EV["hits"]),sc=pop(t,EV["eleven"]-0.1))
        tag(d,"RING OF BLUE LIGHT",540,1250,54,a=ap(t,EV["ring"],EV["y2001"]),sc=pop(t,EV["ring"]-0.1))
        ctag(d,"NOV 2001",540,290,70,a=ap(t,EV["y2001"],sc["e"]+1),sc=pop(t,EV["y2001"]-0.1))
        tag(d,"CHAIN REACTION",540,410,54,a=ap(t,EV["chain"],sc["e"]+1),sc=pop(t,EV["chain"]-0.1))
        ctag(d,"6,000+ SENSORS LOST",540,1250,56,a=ap(t,EV["thousands"],sc["e"]+1),sc=pop(t,EV["thousands"]-0.1))
    hud.append(hd); return buf,hud
_gs=np.random.default_rng(12); GAL=[(110+_gs.normal(0,38),210+_gs.normal(0,16),_gs.uniform(0.5,1.6)) for _ in range(160)]
def s_nova(t,sc):
    buf=CY.copy(); hud=[]
    pB=sm((t-EV["arrived"]+0.3)/0.5); aA=1-pB
    if aA>0:
        m=M()
        for x,y,r in GAL: m.circ(x,y,r)
        ink(buf,m,0.8*aA); ink(buf,dashc(M(),110,210,95,ry=40,n=30),0.35*aA)
        te=EV["exploded"]
        if t>te-0.15:
            f=sm((t-te+0.15)/0.3); glow(buf,130,205,14+30*f,(1,0.97,0.85),1.6*aA)
            for k in range(8):
                an=k*math.pi/4+0.2; ink(buf,M().line((130+math.cos(an)*12,205+math.sin(an)*12),(130+math.cos(an)*(20+30*f),205+math.sin(an)*(20+30*f)),1.5),0.8*aA)
        earth(buf,430,540,48,a=aA,layers=False)
        ink(buf,dim(M(),(150,250),(400,510),u=sm((t-EV["ly"]+0.2)/0.6)),0.6*aA)
        if t>te:
            k=cl((t-te)/max(0.5,EV["detectors"]-te)); px,py=130+300*k,205+335*k
            for j in range(6):
                q=max(0,k-j*0.02); glow(buf,130+300*q,205+335*q,5,GOLD,0.7*aA*(1-j/6))
            if k>=1: glow(buf,430,540,60,GOLD,0.6*aA*math.exp(-(t-EV["detectors"])*1.2))
    if pB>0:
        u=1; R=170; cx,cy=270,320
        sm_=M().circ(cx,cy,R); outl(buf,sm_,a=pB,th=1,fill=0.10)
        for f in (0.75,0.5): ink(buf,dashc(M(),cx,cy,R*f,n=40),0.35*pB)
        core=M().circ(cx,cy,20); comp(buf,core,GOLD,sh=0,rim=0,a=pB); glow(buf,cx,cy,28,GOLD,0.9*pB)
        streaks(buf,t,26,10,a=pB,ang=0,spread=math.pi,org=(cx,cy),spd=1.6,L=50)
        lt=EV["later"]; ks=sm((t-EV["escaped"]+0.6)/(lt-EV["escaped"]+0.6))
        sr=20+(R-20)*ks; ink(buf,M().pline(circ_pts(cx,cy,sr,n=90),2.2),0.9*pB)
        if t>lt-0.1:
            f=sm((t-lt+0.1)/0.6); glow(buf,cx,cy,R*1.25,(1,0.98,0.92),0.9*f*pB)
        # race bars
        y1,y2=560,612; ink(buf,M().rect(60,y1,480,y1+2).rect(60,y2,480,y2+2),0.4*pB)
        kn=sm((t-EV["arrived"]+0.2)/1.4); kl=sm((t-lt)/2.5)*0.75
        comp(buf,M().rect(60,y1-16,60+420*kn,y1-4),GOLD,sh=0,rim=0,a=pB)
        comp(buf,M().rect(60,y2-16,60+420*kl,y2-4),WH,sh=0,rim=0,a=pB)
    titleblock(buf,None,6,"")
    def hd(d,t=t,aA=aA,pB=pB):
        titleblock(buf,d,6,"SUPERNOVA")
        ctag(d,"FEB 1987",540,290,72,a=ap(t,EV["y1987"],EV["arrived"]),sc=pop(t,EV["y1987"]-0.1))
        hand(d,"Large Magellanic Cloud",300,570,38,a=ap(t,EV["exploded"],EV["arrived"]),ang=-2)
        tag(d,"168,000 LIGHT-YEARS",620,820,46,a=ap(t,EV["ly"],EV["arrived"]),ang=-34,sc=pop(t,EV["ly"]-0.1))
        n=int(np.clip((t-EV["detectors"])/max(0.4,EV["n25"]-EV["detectors"]+0.5),0,1)*25)
        gtag(d,f"{n} NEUTRINOS",540,1250,66,a=ap(t,EV["detectors"]+0.2,EV["arrived"]))
        nu(d,"ν",100,1102,46,a=pB); hand(d,"light",110,1205,40,a=pB,ang=0)
        gtag(d,"HOURS BEFORE THE LIGHT",540,290,56,a=ap(t,EV["hours"],sc["e"]+1),sc=pop(t,EV["hours"]-0.1))
        hand(d,"neutrinos escape first…",540,1040,48,a=ap(t,EV["escaped"],EV["later"]))
        hand(d,"…light breaks out later",540,1040,48,a=ap(t,EV["later"],sc["e"]+1))
    hud.append(hd); return buf,hud
_gd=np.random.default_rng(21)
def s_end(t,sc):
    buf=CY.copy(); hud=[]
    pB=sm((t-EV["watched"]+0.4)/0.6); aA=1-pB
    if aA>0:
        sea=M().poly([(26,140)]+[(x,140+6*math.sin(x/30+t*1.5)) for x in range(26,520,10)]+[(514,680),(26,680)])
        comp(buf,sea,(0.05,0.17,0.36),sh=0,rim=0,a=0.6*aA)
        ink(buf,M().pline([(x,140+6*math.sin(x/30+t*1.5)) for x in range(26,520,6)],1.8),aA)
        bed=M().poly([(26,600),(140,590),(260,605),(400,588),(514,598),(514,680),(26,680)]); hatch(buf,bed,0.4*aA,step=8)
        tp=EV["powerful"]; lit=[]
        sm_=M(); bd=M()
        for k in range(8):
            x=70+k*52; base=598-((k*13)%9); sm_.line((x,base),(x,300),1)
            for j in range(12):
                y=base-12-j*24; bd.circ(x,y,4.5)
                if t>tp:
                    dd_=abs((x-60)*0.6-(y-150)*0.8+0)/1.0; d0=abs(0.8*(x-60)-0.6*(y-150)) if False else abs((y-150)-(x-60)*1.05)/1.45
                    tt=tp+d0/600
                    if t>tt and d0<140: lit.append((x,y,math.exp(-(t-tt)*0.8)*(1-d0/140)))
        ink(buf,sm_,0.55*aA); outl(buf,bd,a=aA,th=1,fill=0.3)
        for x,y,v in lit: glow(buf,x,y,10,CYAN,v*aA)
        if t>tp-0.8:
            k=cl((t-tp+0.8)/1.6); x0,y0=-40,45; hx,hy=x0+620*k,y0+650*k
            m=M().line((x0+(hx-x0)*max(0,k-0.3)/max(k,1e-3),y0+(hy-y0)*max(0,k-0.3)/max(k,1e-3)),(hx,hy),4); addm(buf,m,GOLD,1.1*aA); glow(buf,hx,hy,9,GOLD,1.2*aA)
        ink(buf,dim(M(),(495,150),(495,595),u=sm((t-EV["med"]+0.2)/0.6)),0.55*aA)
        streaks(buf,t,6,11,a=0.4*aA,ang=1.2)
    if pB>0:
        streaks(buf,t,46,12,a=pB,ang=1.35,spread=0.12,spd=1.2)
        person(buf,270,610,1.55,a=pB)
    titleblock(buf,None,7,"")
    tf=Lx("So while you")[1]+0.4
    def hd(d,t=t,tf=tf):
        titleblock(buf,d,7,"STILL HERE")
        tag(d,"2023 · MEDITERRANEAN SEA",540,300,46,a=ap(t,EV["y2023"],EV["nobody"]),sc=pop(t,EV["y2023"]-0.1))
        hand(d,"3,450 m",955,700,40,a=ap(t,EV["med"],EV["watched"]),ang=-80)
        gtag(d,"MOST POWERFUL EVER SEEN",540,1250,52,a=ap(t,EV["powerful"],EV["nobody"]),sc=pop(t,EV["powerful"]-0.1))
        ctag(d,"SOURCE: UNKNOWN",540,1250,60,a=ap(t,EV["nobody"],EV["watched"]),sc=pop(t,EV["nobody"]-0.1))
        tag(d,"WHILE YOU WATCHED:",540,290,52,a=ap(t,EV["watched"],tf+0.2))
        gtag(d,"10,000,000,000,000,000+",540,410,62,a=ap(t,EV["quad"],tf+0.2),sc=pop(t,EV["quad"]-0.1))
        hand(d,"you never felt a thing",540,1250,54,a=ap(t,EV["never"],tf+0.2))
        if t>tf:
            kk=t-tf; a=sm((kk-0.2)/0.6); lg=LOGO.resize((int(LOGO.width*0.5),int(LOGO.height*0.5)),Image.LANCZOS); al=np.array(lg); al[:,:,3]=(al[:,:,3]*a).astype(np.uint8)
            d._image.alpha_composite(Image.fromarray(al),(W//2-lg.width//2,640-lg.height//2)); B.txt(d,(W//2,1000),"ORBITHOS",B.CZ(72,600),(255,215,140,int(255*a)),anchor="mm",stroke=2)
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,pauli=s_pauli,ghost=s_ghost,catch=s_catch,superk=s_superk,nova=s_nova,end=s_end)
BAND=(1-0.55*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.26*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.011,(h,w,1)).astype(np.float32) for i in range(6)]
CEN=[(270,330),(130,330),(270,330),(140,420),(270,520),(130,205),(270,330)]
TR=0.30
TF=Lx("So while you")[1]+0.4
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(sc,SC[i+1],nb,i+1)
    elif t<pb+TR: pair=(SC[i-1],sc,pb,i)
    if pair is None:
        buf,hud=render_scene(t,sc); hk=1.0
    else:
        A_,B2,bnd,j=pair; u=cl((t-(bnd-TR))/(2*TR))
        b1,h1=render_scene(t,A_); b2,h2=render_scene(t,B2)
        cx,cy=CEN[j]; RM=max(math.hypot(px-cx,(py-cy)/0.9) for px in (0,w) for py in (0,h))+12; R=(0.55*sm(u)+0.45*u)*RM
        d=np.sqrt((xx-cx)**2+((yy-cy)/0.9)**2)
        m=np.clip((R-d)/3,0,1)[...,None]; buf=b1*(1-m)+b2*m
        ang=np.arctan2(yy-cy,xx-cx); dots=(np.cos(ang*56)>0.55).astype(np.float32)
        edge=np.exp(-((d-R)/4.5)**2)*(0.55+0.9*dots)*(1-0.5*u)
        halo=np.exp(-((d-R)/22)**2)*0.35*(1-u)
        buf=buf+(edge+halo)[...,None]*np.array(CYAN,np.float32)
        hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.2)
    buf=buf*P3+PAP*(1-P3)
    buf=np.clip(buf,0,1.4)*PT*VIG*BAND+GR[int(t*30)%6]
    if t>TF: buf*=max(0.10,1-(t-TF)*0.9)
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
TOTAL=B.TOTAL
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
