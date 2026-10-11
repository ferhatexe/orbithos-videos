import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid49")
for p in ["/home/claude/vid49","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
import drawkit as K
from drawkit import part, dl, circ_pts, rotp, dashl
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= palette (Song-dynasty ink wash on rice paper, cinnabar seals) =================
RICE=(0.93,0.90,0.81); INKC=(0.09,0.09,0.11); CINN=(0.78,0.16,0.10); GOLDW=(0.95,0.72,0.28); AZURE=(0.30,0.48,0.62); OCHRE=(0.72,0.46,0.26)
cInk=(24,22,26); cCin=(196,40,26); cRice=(246,238,218)
CJK="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
_IF={}
def _f(path,s):
    k=(path,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(path,s)
    return _IF[k]
FT=P.FD+"CrimsonPro-Bold.ttf"; FTI=P.FD+"CrimsonPro-Italic.ttf"
def ttl(d,s,x,y,fs=110,a=1.0,sc=1.0,col=cInk,font=None):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f(font or FT,n)
    while f.getlength(s)>1000 and n>20: n-=6; f=_f(font or FT,n)
    d.text((x,y),s,font=f,fill=col+(int(235*a),),anchor="mm")
_SC={}
def seal(d,txt,x,y,fs=70,a=1.0,sc=1.0,ang=0):
    """cinnabar seal: CJK characters reversed-out of a red square"""
    if a<=0.01: return
    k=(txt,fs,ang)
    if k not in _SC:
        f=_f(CJK,fs); n=len(txt); cols=1 if n<=2 else 2; rows=math.ceil(n/cols)
        cw=int(fs*1.08); pad=int(fs*0.22); W_=cols*cw+2*pad; H_=rows*cw+2*pad
        im=Image.new("RGBA",(W_+20,H_+20),(0,0,0,0)); dd=ImageDraw.Draw(im)
        dd.rounded_rectangle((10,10,10+W_,10+H_),radius=int(fs*0.12),fill=cCin+(255,))
        for i,ch in enumerate(txt):
            c_=i//rows; r_=i%rows; cx=10+pad+(cols-1-c_)*cw+cw/2; cy=10+pad+r_*cw+cw/2
            dd.text((cx,cy),ch,font=f,fill=cRice+(255,),anchor="mm")
        ar=np.array(im).astype(np.float32); g=np.random.default_rng(len(txt)*7+fs)
        nz=cv2.GaussianBlur(g.random(ar.shape[:2]).astype(np.float32),(0,0),1.3); nz=(nz-nz.min())/(nz.max()-nz.min()+1e-6)
        ar[...,3]*=np.clip(0.62+nz*0.6,0,1)
        im=Image.fromarray(ar.astype(np.uint8))
        if ang: im=im.rotate(ang,resample=Image.BICUBIC,expand=True)
        _SC[k]=im
    im=_SC[k]
    if abs(sc-1)>0.01: q=max(0.05,round(sc*20)/20); im=im.resize((max(1,int(im.width*q)),max(1,int(im.height*q))),Image.BILINEAR)
    if a<0.99: ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); im=Image.fromarray(ar)
    paste(d,im,x-im.width/2,y-im.height/2)
def label(d,s,x,y,fs=46,a=1.0,sc=1.0,ang=0,red=False):
    card(d,s,x,y,fs=fs,a=a,fg=cRice if red else cInk,bg=cCin if red else (238,228,204),fn="CrimsonPro-Bold",torn=True,ang=ang,sc=sc,pad=(24,10))
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= rice paper =================
_g=np.random.default_rng(1054)
PAPERR=np.zeros((h,w,3),np.float32); PAPERR[:]=RICE
_bl=cv2.resize(_g.normal(0,1,(10,6)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC); _bl/=_bl.std()
PAPERR*=(1-0.03*_bl)[...,None]
_fm=M()
for k in range(160):
    x,y=_g.uniform(0,w),_g.uniform(0,h); an=_g.uniform(0,6.28); L=_g.uniform(8,30)
    _fm.pline([(x+math.cos(an+0.4*math.sin(q*3))*L*q,y+math.sin(an+0.4*math.sin(q*3))*L*q) for q in np.linspace(0,1,8)],1)
_fa=_fm.f()[...,None]*0.10; PAPERR=PAPERR*(1-_fa)+np.array((0.75,0.70,0.60),np.float32)*_fa
FIB=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),2.5); FIB/=FIB.std()
# ================= ink helpers =================
def inkA(m,soft=1.5,grain=0.10):
    A=cv2.GaussianBlur(m.f() if isinstance(m,M) else m,(0,0),soft) if soft>0 else (m.f() if isinstance(m,M) else m)
    return np.clip(A*(1+grain*FIB),0,1)
def wash(buf,A,col=INKC,a=1.0):
    if a<=0: return
    buf+=(np.array(col,np.float32)-buf)*(A*a)[...,None]
def inkm(buf,m,a=1.0,soft=1.2,col=INKC,grain=0.10):
    if a<=0 or (isinstance(m,M) and m.x1<=m.x0): return
    wash(buf,inkA(m,soft,grain),col,a)
def brush(buf,pts,w0,w1,a=1.0,col=INKC,u=1.0,soft=0.8):
    """tapered brush stroke along a polyline"""
    q=part(pts,u)
    if len(q)<2 or a<=0: return
    L=len(q); left=[];right=[]
    for i in range(L):
        p=q[i]; p2=q[min(i+1,L-1)]; p1=q[max(i-1,0)]; dx,dy=p2[0]-p1[0],p2[1]-p1[1]; n=math.hypot(dx,dy)+1e-6
        f=i/(L-1); wd=(w0*(1-f)+w1*f)*(0.8+0.4*math.sin(f*math.pi))
        left.append((p[0]-dy/n*wd/2,p[1]+dx/n*wd/2)); right.append((p[0]+dy/n*wd/2,p[1]-dx/n*wd/2))
    inkm(buf,M().poly(left+right[::-1]),a,soft,col)
def mountains(buf,y0,amp,seed,a=1.0,depth=180,tone=0.85):
    pts=ridge(w,y0,amp,seed,step=14)
    A=M().poly(pts).f()
    ry=np.interp(np.arange(w),[p[0] for p in pts[1:-1]],[p[1] for p in pts[1:-1]])
    fall=np.clip(1-(yy-ry[None,:])/depth,0.12,1)
    wash(buf,cv2.GaussianBlur(A,(0,0),1.2)*fall*(1+0.12*FIB),INKC,a*tone)
def mist(buf,y,hh,a=0.7):
    k=np.exp(-((yy-y)/hh)**2)*a; wash(buf,k*(1+0.2*_bl),RICE,1.0)
def glowg(buf,x,y,r,a=1.0,col=GOLDW):
    d2=((xx-x)**2+(yy-y)**2)/(r*r); wash(buf,np.exp(-d2)*0.9,col,a)
def gstar(buf,x,y,r,t,a=1.0,rays=1.0):
    glowg(buf,x,y,r*3.2,a*0.7); glowg(buf,x,y,r*1.4,a,(1.0,0.86,0.5))
    if rays>0:
        for k in range(8):
            an=k*math.pi/4+0.15*math.sin(t*2+k); L=r*(3+1.2*math.sin(t*5+k*1.7))*rays
            brush(buf,[(x+math.cos(an)*r*1.1,y+math.sin(an)*r*1.1),(x+math.cos(an)*(r+L),y+math.sin(an)*(r+L))],2.4,0.3,0.8*a,CINN)
    inkm(buf,M().circ(x,y,r*0.55),a,0.8,(1.0,0.95,0.8),0.0)
def redsun(buf,x,y,r,a=1.0): inkm(buf,M().circ(x,y,r),a*0.9,1.5,CINN,0.15)
def scholar(buf,x,y,s,a=1.0,point=0.0):
    m=M().poly([(x-26*s,y),(x-18*s,y-90*s),(x+18*s,y-90*s),(x+30*s,y)]).circ(x,y-104*s,13*s)
    m.poly([(x-22*s,y-114*s),(x+22*s,y-114*s),(x+14*s,y-126*s),(x-14*s,y-126*s)]).rect(x-30*s,y-118*s,x+30*s,y-112*s)
    an=-0.9-0.5*point; m.line((x+14*s,y-80*s),(x+14*s+math.cos(an)*50*s,y-80*s+math.sin(an)*50*s),7*s)
    inkm(buf,m,a,1.0)
def pavilion(buf,x,y,s,a=1.0):
    m=M().poly([(x-90*s,y-60*s),(x,y-100*s),(x+90*s,y-60*s),(x+70*s,y-52*s),(x-70*s,y-52*s)]).rect(x-60*s,y-52*s,x-50*s,y).rect(x+50*s,y-52*s,x+60*s,y).rect(x-70*s,y,x+70*s,y+8*s)
    inkm(buf,m,a,1.0)
# ================= scenes =================
def s_hook(t,sc):
    tt=max(t,-1.0)
    buf=PAPERR.copy(); hud=[]
    mountains(buf,560,90,3,1.0,220,0.55); mist(buf,600,40,0.6); mountains(buf,640,60,8,1.0,200,0.85)
    redsun(buf,150,230,40)
    gstar(buf,360,250,16+3*math.sin(tt*3),tt,1.0,1.0)
    pv=sm((tt-EV["spinning"]+0.3)/0.4)
    if pv>0:
        cx,cy=360,250; an=tt*2.4
        for k in (0,1):
            a0=an+k*math.pi; tri=[(cx,cy),(cx+math.cos(a0-0.12)*240,cy+math.sin(a0-0.12)*240),(cx+math.cos(a0+0.12)*240,cy+math.sin(a0+0.12)*240)]
            wash(buf,inkA(M().poly(tri),4,0.1),GOLDW,0.45*pv)
    def hd(d,t=t):
        k0=1.0 if t<0.4 else ap(t,-1,EV["faded"])
        ttl(d,"A STAR IN",540,780,96,a=k0); ttl(d,"BROAD DAYLIGHT",540,890,96,a=k0,col=cCin)
        seal(d,"客星",900,190,64,a=1.0 if t<0.4 else ap(t,-1,sc["e"]+1))
        ttl(d,"IT FADED…",540,840,104,a=ap(t,EV["faded"],EV["spinning"]),sc=pop(t,EV["faded"]-0.1))
        label(d,"STILL SPINNING · 30× A SECOND",540,860,50,a=ap(t,EV["spinning"],sc["e"]+1),sc=pop(t,EV["spinning"]-0.1),red=True)
    hud.append(hd); return buf,hud
def s_record(t,sc):
    buf=PAPERR.copy(); hud=[]
    pR=sm((t-EV["southwest"]+0.35)/0.45); a=1-pR
    if a>0:
        mountains(buf,600,70,12,a,200,0.6); mist(buf,640,40,0.5*a)
        pavilion(buf,150,640,1.1,a); scholar(buf,300,640,1.15,a,point=sm((t-EV["guest"]+0.3)/0.4))
        day=sm((t-EV["venus"]+0.2)/0.4)*(1-sm((t-EV["night"]+0.2)/0.4))
        nt=sm((t-EV["night"]+0.2)/0.4)
        if nt>0: wash(buf,np.clip(1-yy/700,0,1)*0.75,(0.12,0.14,0.22),nt*a)
        if day>0: redsun(buf,110,170,34,day*a)
        fade=1-sm((t-EV["disappears"]+0.1)/0.6)
        gstar(buf,400,200,15,t,a*sm((t-EV["guest"]+0.3)/0.4)*fade,1.0)
        if day>0.01:
            v=M().circ(470,330,5); inkm(buf,v,day*a,0.8,(1,0.95,0.8)); glowg(buf,470,330,14,day*a*0.6)
        n=int(cl((t-EV["days23"]+0.1)/1.2)*23)
        if n>0 and t<EV["night"]+0.2:
            tm=M()
            for k in range(n):
                gx=k//5; gi=k%5; x0=80+gx*58
                if gi<4: tm.line((x0+gi*10,290),(x0+gi*10+2,332),3.5)
                else: tm.line((x0-6,320),(x0+42,302),3.5)
            inkm(buf,tm,a*day,0.7)
    if pR>0:
        rock=M().poly([(30,180),(510,160),(530,640),(10,660)]); wash(buf,inkA(rock,6,0.12),OCHRE,0.55*pR); inkm(buf,M().pline([(30,180),(510,160),(530,640),(10,660),(30,180)],3),0.4*pR,2)
        hd_=M().ell(200,420,34,44)
        for k,(an,L) in enumerate(((-2.2,70),(-1.85,84),(-1.55,88),(-1.25,80),(-0.6,56))):
            hd_.line((200+math.cos(an)*20,420+math.sin(an)*26),(200+math.cos(an)*L,420+math.sin(an)*L),16)
        inkm(buf,hd_,pR*sm((t-EV["painted"]+0.3)/0.4),1.6,(0.62,0.20,0.10))
        cm=M().circ(370,300,44); cm2=M().circ(392,286,40); A=np.clip(inkA(cm,1.4)-inkA(cm2,1.4)*1.2,0,1); wash(buf,A,(0.62,0.20,0.10),pR*sm((t-EV["painted"])/0.4))
        st=M().poly([(420,410),(428,388),(436,410),(458,410),(440,422),(446,444),(428,430),(410,444),(416,422),(398,410)])
        inkm(buf,st,pR*sm((t-EV["rock"]+0.2)/0.4),1.2,(0.62,0.20,0.10))
    def hd(d,t=t,pR=pR):
        seal(d,"一〇五四",920,210,50,a=ap(t,EV["july"],EV["southwest"]),sc=pop(t,EV["july"]-0.1))
        ttl(d,"JULY 4, 1054",540,840,100,a=ap(t,EV["july"],EV["guest"]),sc=pop(t,EV["july"]-0.1))
        ttl(d,"A “GUEST STAR”",540,840,96,a=ap(t,EV["guest"],EV["venus"]),sc=pop(t,EV["guest"]-0.1),col=cCin)
        label(d,"CHINESE COURT ASTRONOMERS",540,950,40,a=ap(t,EV["china"],EV["venus"]))
        ttl(d,"AS BRIGHT AS VENUS",540,840,84,a=ap(t,EV["venus"],EV["days23"]),sc=pop(t,EV["venus"]-0.1))
        ttl(d,"23 DAYS IN DAYLIGHT",540,840,84,a=ap(t,EV["days23"],EV["night"]),sc=pop(t,EV["days23"]-0.1),col=cCin)
        ttl(d,"~2 YEARS AT NIGHT",540,840,90,a=ap(t,EV["twoyears"]-0.3,EV["disappears"]),sc=pop(t,EV["twoyears"]-0.4))
        ttl(d,"GONE",540,840,140,a=ap(t,EV["disappears"],EV["southwest"]),sc=pop(t,EV["disappears"]-0.1),col=cCin)
        label(d,"AMERICAN SOUTHWEST",540,840,52,a=ap(t,EV["southwest"],sc["e"]+1),sc=pop(t,EV["southwest"]-0.1),red=True)
        label(d,"MAYBE PAINTED ON A ROCK",540,950,42,a=ap(t,EV["painted"],sc["e"]+1))
    hud.append(hd); return buf,hud
_gb=np.random.default_rng(7)
SPL=[( _gb.uniform(0,2*math.pi), _gb.uniform(60,260), _gb.uniform(2,9)) for _ in range(70)]
def s_boom(t,sc):
    buf=PAPERR.copy(); hud=[]
    pG=sm((t-EV["weeks"]+0.35)/0.45); pL=sm((t-EV["light"]+0.35)/0.45)
    a1=1-pG; a2=pG*(1-pL); a3=pL
    cx,cy=270,380
    if a1>0:
        k=eout(cl((t-EV["exploding"]+0.4)/1.4))
        if t<EV["exploding"]-0.4:
            r=60+6*math.sin(t*5); inkm(buf,M().circ(cx,cy,r),a1,3,(0.85,0.40,0.18)); inkm(buf,M().circ(cx,cy,r*0.7),a1*0.6,3,CINN)
        else:
            inkm(buf,M().circ(cx,cy,20+30*(1-k)),a1,2,INKC)
            m=M()
            for an,L,r in SPL:
                d=L*k; m.circ(cx+math.cos(an)*d,cy+math.sin(an)*d,r*(0.5+k))
                m.line((cx+math.cos(an)*d*0.5,cy+math.sin(an)*d*0.5),(cx+math.cos(an)*d,cy+math.sin(an)*d),r*0.6)
            inkm(buf,m,a1,1.2)
            m2=M()
            for an,L,r in SPL[::3]: d=L*k*0.7; m2.circ(cx+math.cos(an)*d,cy+math.sin(an)*d,r)
            inkm(buf,m2,a1,1.5,CINN)
            glowg(buf,cx,cy,90*k,a1*(1-k*0.5))
    if a2>0:
        for arm in (0,1):
            pts=[(cx+math.cos(q+arm*math.pi+t*0.2)*q*36,cy+math.sin(q+arm*math.pi+t*0.2)*q*22) for q in np.linspace(0.3,5.2,60)]
            brush(buf,pts,14,2,a2*0.75)
        inkm(buf,M().ell(cx,cy,40,26),a2*0.8,4)
        sx,sy=cx+120,cy-40; gstar(buf,sx,sy,10+14*sm((t-EV["outshine"]+0.2)/0.6),t,a2,1.0)
    if a3>0:
        sx,sy=80,200; gstar(buf,sx,sy,14,t,a3,0.6)
        u=sm((t-EV["light"]+0.1)/2.2); ex,ey=440,560
        brush(buf,[(sx+(ex-sx)*q,sy+(ey-sy)*q+30*math.sin(q*math.pi)) for q in np.linspace(0,1,40)],5,1.5,a3*0.7,GOLDW,u)
        inkm(buf,M().circ(ex,ey,40),a3*sm((t-EV["earth"]+0.4)/0.4),1.2,AZURE); inkm(buf,M().pline(circ_pts(ex,ey,40,n=60),3),a3*sm((t-EV["earth"]+0.4)/0.4),1)
    def hd(d,t=t):
        ttl(d,"SUPERNOVA",540,1130,140,a=ap(t,EV["supernova"],EV["weeks"]),sc=pop(t,EV["supernova"]-0.1),col=cCin)
        label(d,"A GIANT STAR DIES",540,1240,48,a=ap(t,EV["giant"],EV["weeks"]))
        seal(d,"超新星",910,200,56,a=ap(t,EV["supernova"],EV["weeks"]))
        ttl(d,"BRIGHTER THAN",540,1100,84,a=ap(t,EV["outshine"]-0.3,EV["light"]))
        ttl(d,"A WHOLE GALAXY",540,1200,96,a=ap(t,EV["galaxy"]-0.2,EV["light"]),sc=pop(t,EV["galaxy"]-0.3),col=cCin)
        ttl(d,"~6,500 YEARS",540,1130,120,a=ap(t,EV["years"],sc["e"]+1),sc=pop(t,EV["years"]-0.1),col=cCin)
        label(d,"FOR ITS LIGHT TO REACH EARTH",540,1240,44,a=ap(t,EV["years"]+0.3,sc["e"]+1))
    hud.append(hd); return buf,hud
_gc=np.random.default_rng(31)
FIL=[(_gc.uniform(0,2*math.pi),_gc.uniform(0.4,1.0),_gc.uniform(-0.4,0.4)) for _ in range(46)]
def nebula(buf,cx,cy,R,t,a=1.0):
    wash(buf,inkA(M().ell(cx,cy,R*0.9,R*0.65),R*0.25,0.4),AZURE,0.5*a)
    for an,L,bend in FIL:
        pts=[(cx+math.cos(an+bend*q)*R*L*q*1.1,cy+math.sin(an+bend*q)*R*L*q*0.8) for q in np.linspace(0.25,1,14)]
        brush(buf,pts,3.5,1.0,0.75*a,CINN if (int(an*10)%3) else INKC)
def s_crab(t,sc):
    buf=PAPERR.copy(); hud=[]
    pC=sm((t-EV["heart"]+0.35)/0.45); pS=sm((t-EV["first"]+0.35)/0.45)
    a1=1-pC; a2=pC*(1-pS); a3=pS
    cx,cy=270,380
    if a1>0:
        R=150*(1+0.04*(t-sc["s"])); nebula(buf,cx,cy,R*sm((t-sc["s"]+0.2)/0.6+0.3),t,a1)
    if a2>0:
        nebula(buf,cx,cy,170,t,a2*0.35)
        an=t*2*math.pi*0.9 if t>EV["spins"]-0.2 else 0.4
        for k in (0,1):
            a0=an+k*math.pi; tri=[(cx,cy),(cx+math.cos(a0-0.10)*360,cy+math.sin(a0-0.10)*360),(cx+math.cos(a0+0.10)*360,cy+math.sin(a0+0.10)*360)]
            wash(buf,inkA(M().poly(tri),3,0.1),GOLDW,0.55*a2*sm((t-EV["spins"]+0.4)/0.4))
        inkm(buf,M().circ(cx,cy,14),a2,0.8,INKC); glowg(buf,cx,cy,22,a2*0.5)
        ct=sm((t-EV["city"]+0.3)/0.4)
        if ct>0:
            m=M(); x=110
            for k,(wd,ht) in enumerate(((30,60),(22,90),(40,120),(26,70),(34,150),(24,80),(40,100),(28,64),(30,110),(22,72))):
                m.rect(x,640-ht,x+wd,640); x+=wd+4
            inkm(buf,m,a2*ct*0.85,1.0)
            inkm(buf,dl(M(),[(110,662),(110+x-110,662)],1.0,2),a2*ct,0.6)
    if a3>0:
        mountains(buf,560,90,3,a3,220,0.55); mist(buf,600,40,0.6*a3); mountains(buf,640,60,8,a3,200,0.85)
        redsun(buf,150,230,40,a3); gstar(buf,360,250,14,t,a3,0.6)
    def hd(d,t=t,a2=a2):
        label(d,"TODAY",540,290,56,a=ap(t,EV["today"],EV["crab"]),red=True)
        ttl(d,"THE CRAB NEBULA",540,290,104,a=ap(t,EV["crab"],EV["heart"]),sc=pop(t,EV["crab"]-0.1))
        label(d,"STILL EXPANDING",540,400,46,a=ap(t,EV["expanding"],EV["heart"]))
        seal(d,"蟹狀星雲",920,200,46,a=ap(t,EV["crab"],sc["e"]+1))
        ttl(d,"NEUTRON STAR",540,290,120,a=ap(t,EV["neutron"],EV["spins"]),sc=pop(t,EV["neutron"]-0.1),col=cCin)
        label(d,"≈ 20 KM WIDE · A CITY",540,400,46,a=ap(t,EV["city"],EV["spins"]))
        ttl(d,"30 SPINS / SECOND",540,290,96,a=ap(t,EV["thirty2"],EV["first"]),sc=pop(t,EV["thirty2"]-0.1))
        label(d,"A COSMIC LIGHTHOUSE",540,400,46,a=ap(t,EV["lighthouse"],EV["first"]),red=True)
        ttl(d,"~1,000 YEARS AGO…",540,800,90,a=ap(t,EV["thousand"]-0.3,sc["e"]+1),col=cInk)
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,record=s_record,boom=s_boom,crab=s_crab)
BAND=(1-0.40*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.20*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.008,(h,w,1)).astype(np.float32) for i in range(6)]
TR=0.32; TOTAL=B.TOTAL; LOOPD=0.6
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
def scroll(b1,b2,u):
    """hanging-scroll unroll: a wooden roller travels down, revealing the new painting above it"""
    yr=int(sm(u)*(h+60))-30
    out=b1.copy()
    if yr>0: out[:min(yr,h)]=b2[:min(yr,h)]
    y0=max(0,yr-8); y1=min(h,yr+30)
    if y1>y0:
        sh=np.clip((yy[y0:y1,:1]-yr)/30,0,1)[...,None]; out[y0:y1]*=(1-0.35*(1-sh))
    m=M().rect(0,yr-9,w,yr+9).circ(6,yr,13).circ(w-6,yr,13)
    comp(out,m,(0.30,0.18,0.10),sh=0.4,dx=0,dy=6,blur=5,rim=0.15)
    comp(out,M().rect(0,yr-9,w,yr-5),(0.52,0.34,0.18),sh=0,rim=0)
    return out
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(sc,SC[i+1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SC[i-1],sc,t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(sc,SC[0],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None:
        buf,hud=render_scene(t,sc); hk=1.0
    else:
        A_,B2,ta,tb,u=pair
        b1,h1=render_scene(ta,A_); b2,h2=render_scene(tb,B2)
        buf=scroll(b1,b2,u); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    buf=np.clip(buf,0,1.2)*PT*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
