import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid52")
for p in ["/home/claude/vid52","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from drawkit import part, dl, circ_pts, rotp, dashl
from PIL import Image, ImageDraw, ImageFont, ImageFilter
EV=ev.EV; Lx=ev.Lx
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= palette (neon sign tubes on a dark brick wall) =================
PINK=(1.0,0.22,0.58); CYAN=(0.18,0.82,1.0); YEL=(1.0,0.82,0.28); GRN=(0.30,1.0,0.42); WHT=(0.92,0.94,1.0); RED=(1.0,0.22,0.14); PUR=(0.66,0.36,1.0)
cPink=(255,70,160); cCyan=(60,210,255); cYel=(255,210,80); cGrn=(90,255,120); cWht=(235,240,255); cPur=(170,100,255)
_IF={}
def _f(path,s):
    k=(path,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(path,s)
    return _IF[k]
FN=P.FD+"Outfit-Regular.ttf"; FS=P.FD+"NothingYouCouldDo-Regular.ttf"; FB=P.FD+"Outfit-Bold.ttf"
_NC={}
def neon(d,s,x,y,fs=90,a=1.0,sc=1.0,col=cPink,font=None):
    """neon lettering: blurred halo + saturated tube + hot white core"""
    if a<=0.01 or fs*sc<8: return
    font=font or FN; n=int(fs*sc)
    k=(s,n,col,font)
    if k not in _NC:
        f=_f(font,n)
        while f.getlength(s)>980 and n>16: n-=4; f=_f(font,n)
        bb=ImageDraw.Draw(Image.new("L",(4,4))).textbbox((0,0),s,font=f); tw,th=bb[2]-bb[0],bb[3]-bb[1]; pad=int(n*0.6)
        Wc,Hc=tw+2*pad,th+2*pad; base=Image.new("L",(Wc,Hc),0); ImageDraw.Draw(base).text((pad-bb[0],pad-bb[1]),s,font=f,fill=255)
        A=np.array(base).astype(np.float32)/255
        g1=cv2.GaussianBlur(A,(0,0),n*0.10); g2=cv2.GaussianBlur(A,(0,0),n*0.28)
        er=cv2.erode(A,np.ones((3,3),np.uint8))
        c=np.array(col,np.float32)/255
        rgb=np.clip(c[None,None,:]*(A[...,None]*0.9)+np.array((1,1,1),np.float32)*(er[...,None]*0.55),0,1)
        alpha=np.clip(A+g1*0.9+g2*0.7,0,1)
        glowc=c[None,None,:]*np.clip(g1*1.2+g2,0,1)[...,None]
        rgb=np.where(A[...,None]>0.05,rgb,glowc/np.maximum(alpha[...,None],1e-3))
        im=np.dstack([np.clip(rgb,0,1)*255,alpha*255]).astype(np.uint8); _NC[k]=Image.fromarray(im,"RGBA")
    im=_NC[k]
    if a<0.99: ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); im=Image.fromarray(ar)
    paste(d,im,x-im.width/2,y-im.height/2)
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= brick wall =================
_g=np.random.default_rng(1969)
WALL=np.zeros((h,w,3),np.float32)
bh_,bw_=22,52
row=(yy//bh_).astype(int); off=np.where(row%2==0,0,bw_/2)
bx=((xx+off)//bw_).astype(int)
bid=row*37+bx*101
tone=(np.sin(bid*12.9898)*43758.5453)%1.0
WALL[:]=np.array((0.075,0.06,0.07),np.float32)
WALL*=(0.75+0.5*tone)[...,None]
mort=(((yy%bh_)<2)|(((xx+off)%bw_)<2)).astype(np.float32)
WALL=WALL*(1-mort[...,None])+np.array((0.035,0.035,0.04),np.float32)*mort[...,None]
_n=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),1.0); WALL*=(1+0.12*_n/_n.std())[...,None]
WALL=np.clip(WALL,0,1)
# ================= neon layer accumulation =================
class Lay:
    def __init__(s): s.L={}
    def add(s,m,col,a=1.0):
        if a<=0.01 or m.x1<=m.x0: return
        A=m.f()*a
        if col in s.L: np.maximum(s.L[col],A,out=s.L[col])
        else: s.L[col]=A
    def light(s,mult=1.0):
        out=np.zeros((h,w,3),np.float32)
        for col,A in s.L.items():
            c=np.array(col,np.float32)
            g1=cv2.GaussianBlur(A,(0,0),2.2); g2=cv2.GaussianBlur(A,(0,0),9); g3=cv2.GaussianBlur(A,(0,0),26)
            out+=(g1*0.9+g2*0.75+g3*0.55)[...,None]*c+ (A*0.75)[...,None]*(0.55*c+0.45)
        return out*mult
def tube(m,pts,u=1.0,th=3.0): return dl(m,pts,u,th)
def circ(m,cx,cy,r,u=1.0,th=3.0,a0=-math.pi/2): return dl(m,circ_pts(cx,cy,r,r,a0,a0+2*math.pi,max(24,int(r))),u,th)
def arrowhead(m,p,ang,s=14,th=3.0):
    for d_ in (-0.5,0.5): m.line(p,(p[0]-math.cos(ang+d_)*s,p[1]-math.sin(ang+d_)*s),th)
    return m
def earth(ly,cx,cy,R,u=1.0,a=1.0,t=0.0):
    ly.add(circ(M(),cx,cy,R,u),CYAN,a)
    m=M()
    for k in range(3):
        an=t*0.5+k*2.1; px=cx+math.cos(an)*R*0.45
        if abs(px-cx)<R*0.7: m.pline([(px+R*0.12*math.sin(q*5+k),cy-R*0.5+q*R*(0.6+0.1*k)) for q in np.linspace(0,1,10)],2.5)
    ly.add(m,GRN,a*u)
def moon(ly,cx,cy,R,u=1.0,a=1.0):
    ly.add(circ(M(),cx,cy,R,u),WHT,a)
    m=M()
    for dx,dy,r in ((-0.3,-0.25,0.22),(0.3,0.1,0.16),(-0.05,0.4,0.12)): circ(m,cx+dx*R,cy+dy*R,r*R,u,2)
    ly.add(m,WHT,0.7*a)
def astronaut(ly,x,y,s,a=1.0):
    m=M(); circ(m,x,y-120*s,22*s,1,3); m.pline([(x-12*s,y-122*s),(x+12*s,y-122*s)],3)
    dl(m,[(x-24*s,y-96*s),(x+24*s,y-96*s),(x+28*s,y-40*s),(x-28*s,y-40*s),(x-24*s,y-96*s)],1,3)
    m.line((x-14*s,y-40*s),(x-16*s,y),3).line((x+14*s,y-40*s),(x+16*s,y),3).line((x+24*s,y-88*s),(x+50*s,y-56*s),3)
    ly.add(m,WHT,a)
def panel(ly,x,y,s,a=1.0):
    m=M(); dl(m,[(x-30*s,y),(x+30*s,y),(x+30*s,y-40*s),(x-30*s,y-40*s),(x-30*s,y)],1,3)
    for k in (1,2): m.line((x-30*s+k*20*s,y),(x-30*s+k*20*s,y-40*s),2)
    m.line((x-30*s,y-20*s),(x+30*s,y-20*s),2); ly.add(m,YEL,a)
# ================= scenes =================
def s_hook(t,sc):
    tt=max(t,-1.0); ly=Lay(); hud=[]
    ex,ey=150,560; d=230+18*math.sin(tt*0.0)+14*sm((tt-EV["cm"]+0.3)/0.6)
    mx,my=ex+d*math.cos(-0.75),ey+d*math.sin(-0.75)
    earth(ly,ex,ey,70,1.0,1.0,tt); moon(ly,mx+6*tt*0.6,my-5*tt*0.6,34,1.0,1.0)
    m=M(); a0=(ex+80*math.cos(-0.75),ey+80*math.sin(-0.75)); a1=(mx+6*tt*0.6-44*math.cos(-0.75),my-5*tt*0.6-44*math.sin(-0.75))
    dashl(m,a0,a1,10,8,2.5); arrowhead(m,a1,-0.75); ly.add(m,YEL,0.9)
    for k in range(3):
        q=((tt*0.7+k/3)%1); px=mx+6*tt*0.6+math.cos(-0.75)*(40+q*80); py=my-5*tt*0.6+math.sin(-0.75)*(40+q*80)
        ly.add(M().line((px,py),(px+math.cos(-0.75)*14,py+math.sin(-0.75)*14),2.5),PINK,1-q)
    def hd(d,t=t):
        k0=1.0 if t<0.4 else ap(t,-1,EV["cm"])
        neon(d,"THE MOON IS",540,200,92,a=k0,col=cWht); neon(d,"RUNNING AWAY",540,320,110,a=k0,col=cPink)
        neon(d,"+3.8 cm / year",540,230,96,a=ap(t,EV["cm"],sc["e"]+1),sc=pop(t,EV["cm"]-0.1),col=cYel)
        neon(d,"how do we know?",540,360,84,a=ap(t,EV["how"],sc["e"]+1),col=cCyan,font=FS)
    return ly,[hd]
def s_laser(t,sc):
    ly=Lay(); hud=[]
    pN=sm((t-EV["timing"]+0.3)/0.4)
    a1=1-pN
    if a1>0:
        # lunar surface + astronaut + panel (first), then Earth-Moon laser link
        pL=sm((t-EV["lasers"]+0.3)/0.4)
        b1=a1*(1-pL)
        if b1>0:
            ly.add(dl(M(),[(20,560)]+[(x,560-12*math.sin(x/50)) for x in range(20,540,20)],1.0,3),WHT,b1*0.8)
            circ_m=M(); circ(circ_m,120,600,30,1,2); circ(circ_m,420,590,22,1,2); ly.add(circ_m,WHT,0.5*b1)
            astronaut(ly,200,548,1.3,b1*sm((t-EV["apollo"]+0.4)/0.4))
            panel(ly,360,560,1.2,b1*sm((t-EV["mirrors"]+0.3)/0.4))
            ly.add(dl(M(),[(60,120),(110,90),(160,120)],1,3),CYAN,b1*0.0)
        b2=a1*pL
        if b2>0:
            ex,ey=130,560; mx,my=420,190
            earth(ly,ex,ey,80,1.0,b2,t); moon(ly,mx,my,40,1.0,b2)
            dome=M(); dl(dome,circ_pts(ex,ey-80,16,16,math.pi,2*math.pi,20),1,3); ly.add(dome,WHT,b2)
            beam=sm((t-EV["lasers"]+0.1)/0.5)
            ly.add(dl(M(),[(ex,ey-96),(mx-20,my+30)],beam,2.5),GRN,b2*0.8)
            per=2.5/1.6; ph=((t-EV["lasers"])/per)%1 if t>EV["lasers"] else -1
            if ph>=0:
                q=ph*2 if ph<0.5 else 2-ph*2
                px,py=ex+(mx-20-ex)*q,ey-96+(my+30-ey+96)*q
                ly.add(M().circ(px,py,7),GRN if ph<0.5 else YEL,b2)
            sw=sm((t-EV["trip"]+0.3)/0.4)
            if sw>0:
                cx_,cy_=410,520; m=M(); circ(m,cx_,cy_,50,1,3); m.line((cx_,cy_),(cx_+math.sin(t*2.6)*38,cy_-math.cos(t*2.6)*38),3); m.rect(cx_-8,cy_-64,cx_+8,cy_-56)
                ly.add(m,YEL,b2*sw)
    if pN>0:
        fx,fy=170,600
        m=M(); dl(m,[(fx-36,fy),(fx-36,fy-240)]+circ_pts(fx,fy-240,36,40,math.pi,2*math.pi,24)+[(fx+36,fy-240),(fx+36,fy)],1,3); ly.add(m,PINK,pN)
        nl=M(); dl(nl,[(fx-24,fy-250),(fx-24,fy-210),(fx+24,fy-210),(fx+24,fy-250)],1,3); ly.add(nl,WHT,pN)
        g=sm((t-EV["nails"]+0.2)/1.2); ly.add(M().line((fx-24,fy-210+0),(fx+24,fy-210),3),CYAN,pN*g)
        rl=M(); rl.line((300,620),(300,200),3)
        for k in range(15): rl.line((300,620-k*28),(300+(24 if k%5==0 else 12),620-k*28),2.5)
        ly.add(rl,YEL,pN)
        ly.add(dl(M(),[(360,600),(360,600-380*sm((t-EV["slipping"]+0.2)/1.4))],1.0,3),PINK,pN)
        ly.add(arrowhead(M(),(360,600-380*sm((t-EV["slipping"]+0.2)/1.4)),-math.pi/2),PINK,pN)
    def hd(d,t=t):
        neon(d,"1969 · APOLLO 11",540,200,84,a=ap(t,EV["y1969"],EV["lasers"]),sc=pop(t,EV["y1969"]-0.1),col=cWht)
        neon(d,"a panel of mirrors",540,1310,78,a=ap(t,EV["mirrors"],EV["lasers"]),col=cYel,font=FS)
        neon(d,"LASER",540,200,130,a=ap(t,EV["lasers"],EV["trip"]),sc=pop(t,EV["lasers"]-0.1),col=cGrn)
        neon(d,"…and back",540,1310,80,a=ap(t,EV["back"],EV["trip"]),col=cYel,font=FS)
        neon(d,"~2.5 SECONDS",540,200,100,a=ap(t,EV["secs"]-0.2,EV["timing"]),sc=pop(t,EV["secs"]-0.3),col=cYel)
        neon(d,"round trip",540,1310,80,a=ap(t,EV["trip"],EV["timing"]),col=cGrn,font=FS)
        neon(d,"SLIPPING AWAY",540,200,100,a=ap(t,EV["slipping"],sc["e"]+1),sc=pop(t,EV["slipping"]-0.1),col=cPink)
        neon(d,"as fast as fingernails grow",540,1310,64,a=ap(t,EV["nails"],sc["e"]+1),col=cCyan,font=FS)
    return ly,[hd]
def s_tides(t,sc):
    ly=Lay(); hud=[]
    ex,ey=200,470
    ang_m=-0.35+0.25*(t-sc["s"])/12
    r_orb=220+40*sm((t-EV["higher"]+0.3)/1.5)
    mx,my=ex+r_orb*math.cos(ang_m),ey+r_orb*math.sin(ang_m)
    lead=0.0 if t<EV["ahead"]-0.2 else 0.45*sm((t-EV["ahead"]+0.2)/0.8)
    bul=sm((t-EV["pulls"]+0.2)/0.6)
    earth(ly,ex,ey,72,1.0,1.0,t*(1.0-0.6*sm((t-EV["slows"]+0.2)/1.0)))
    if bul>0:
        ell=circ_pts(0,0,72+28*bul,72-6*bul,0,2*math.pi,60); pts=rotp([(ex+x,ey+y) for x,y in ell],ang_m+lead,ex,ey)
        ly.add(dl(M(),pts,1.0,2.5),CYAN,0.8*bul)
    moon(ly,mx,my,30,1.0,1.0)
    ly.add(dashl(M(),*[(ex+r_orb*math.cos(a_),ey+r_orb*math.sin(a_)) for a_ in (ang_m+0.25,)],(ex+r_orb*math.cos(ang_m+0.25),ey+r_orb*math.sin(ang_m+0.25)),4,4,2) if False else M(),WHT,0)
    om=M()
    for k in range(24):
        a0=k*2*math.pi/24; a1_=a0+math.pi/24; om.pline([(ex+r_orb*math.cos(q),ey+r_orb*math.sin(q)) for q in np.linspace(a0,a1_,4)],2)
    ly.add(om,WHT,0.45)
    sp=sm((t-EV["spins"]+0.2)/0.4)
    if sp>0:
        rot=M(); pts=circ_pts(ex,ey,100,100,math.pi*0.7,math.pi*1.25,20); dl(rot,pts,1,3); arrowhead(rot,pts[-1],math.pi*1.25+math.pi/2)
        ly.add(rot,YEL,sp)
    tg=sm((t-EV["tug"]+0.2)/0.4)
    if tg>0:
        bx,by=ex+(100)*math.cos(ang_m+lead),ey+(100)*math.sin(ang_m+lead)
        ly.add(dl(M(),[(bx,by),(mx-20*math.cos(ang_m),my-20*math.sin(ang_m))],tg,2.5),PINK,0.9)
        fm=M(); tgx,tgy=mx+50*math.cos(ang_m+math.pi/2),my+50*math.sin(ang_m+math.pi/2)
        dl(fm,[(mx,my),(tgx,tgy)],tg,3); arrowhead(fm,(tgx,tgy),ang_m+math.pi/2); ly.add(fm,PINK,tg)
    def hd(d,t=t):
        neon(d,"TIDES",540,200,140,a=ap(t,EV["tides"],EV["spins"]),sc=pop(t,EV["tides"]-0.1),col=cCyan)
        neon(d,"ocean bulges",540,1310,80,a=ap(t,EV["bulges"],EV["spins"]),col=cCyan,font=FS)
        neon(d,"EARTH SPINS FASTER",540,200,84,a=ap(t,EV["spins"],EV["tug"]),sc=pop(t,EV["spins"]-0.1),col=cYel)
        neon(d,"bulge runs ahead",540,1310,80,a=ap(t,EV["ahead"],EV["energy"]),col=cCyan,font=FS)
        neon(d,"…TUGS THE MOON",540,320,84,a=ap(t,EV["tug"],EV["energy"]),sc=pop(t,EV["tug"]-0.1),col=cPink)
        neon(d,"MOON CLIMBS HIGHER",540,200,84,a=ap(t,EV["energy"],sc["e"]+1),sc=pop(t,EV["energy"]-0.1),col=cWht)
        neon(d,"Earth's spin slows",540,1310,80,a=ap(t,EV["slows"],sc["e"]+1),col=cYel,font=FS)
    return ly,[hd]
def s_time(t,sc):
    ly=Lay(); hud=[]
    pE=sm((t-EV["future"]+0.3)/0.4); pR=sm((t-EV["allb"]+0.3)/0.4)
    a1=1-pE; a2=pE*(1-pR); a3=pR
    if a1>0:
        cx,cy=270,400; m=M(); circ(m,cx,cy,150,sm((t-sc["s"]+0.2)/0.6),3)
        for k in range(18):
            an=-math.pi/2+k*2*math.pi/18; m.line((cx+math.cos(an)*128,cy+math.sin(an)*128),(cx+math.cos(an)*144,cy+math.sin(an)*144),2.5)
        ly.add(m,PINK,a1)
        hnd=M(); an=-math.pi/2+(t*1.4)%(2*math.pi); hnd.line((cx,cy),(cx+math.cos(an)*110,cy+math.sin(an)*110),3).line((cx,cy),(cx+math.cos(an/12)*70,cy+math.sin(an/12)*70),4)
        ly.add(hnd,WHT,a1)
        mm=M(); circ(mm,cx+190,cy-150,26,1,3); ly.add(mm,WHT,a1*0.9)
    if a2>0:
        cx,cy=270,380; m=M(); circ(m,cx,cy,110,1,3)
        for k in range(16): an=k*math.pi/8+t*0.3; m.line((cx+math.cos(an)*126,cy+math.sin(an)*126),(cx+math.cos(an)*150,cy+math.sin(an)*150),3)
        ly.add(m,YEL,a2)
        k=sm((t-EV["small"]+0.6)/1.6); r=110*(1.0-0.25*k)
        mx=cx+(1-sm((t-EV["future"]+0.2)/1.2))*260
        mm=M(); circ(mm,mx,cy,r,1,3); ly.add(mm,WHT,a2)
        fill=M().circ(mx,cy,r-3); ly.add(fill,(0.02,0.02,0.04),0)  # (tubes only)
    if a3>0:
        ex,ey=150,560; d_=244; mx,my=ex+d_*math.cos(-0.75),ey+d_*math.sin(-0.75)
        earth(ly,ex,ey,70,1.0,a3,t-45.6); moon(ly,mx,my,34,1.0,a3)
    def hd(d,t=t,a1=a1):
        neon(d,"1.4 BILLION YEARS AGO",540,180,76,a=ap(t,EV["billion"],EV["future"]),sc=pop(t,EV["billion"]-0.1),col=cWht)
        neon(d,"18-HOUR DAYS",540,1310,96,a=ap(t,EV["eighteen"]-0.2,EV["future"]),sc=pop(t,EV["eighteen"]-0.3),col=cPink)
        neon(d,"FAR FUTURE",540,200,110,a=ap(t,EV["future"],EV["allb"]),sc=pop(t,EV["future"]-0.1),col=cYel)
        neon(d,"no more total eclipses",540,1310,74,a=ap(t,EV["eclipses"],EV["allb"]),col=cWht,font=FS)
        neon(d,"EVERY SINGLE YEAR",540,230,84,a=ap(t,EV["every"]-0.2,sc["e"]+1),col=cYel)
    return ly,[hd]
SCN=dict(hook=s_hook,laser=s_laser,tides=s_tides,time=s_time)
BAND=(1-0.30*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.40*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.010,(h,w,1)).astype(np.float32) for i in range(6)]
TR=0.34; TOTAL=B.TOTAL; LOOPD=0.6
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
def flick(u,seed,rising):
    """neon start-up/shut-down flicker: stuttering on/off with a buzz-like irregular rhythm"""
    g=np.random.default_rng(seed); x=u if rising else 1-u
    on=1.0 if g.random()<x*1.25 else 0.08
    return on*min(1,0.3+x)
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(sc,SC[i+1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SC[i-1],sc,t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(sc,SC[0],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    fr=int(round(t*30))
    if pair is None:
        ly,hud=render_scene(t,sc); light=ly.light(1+0.03*math.sin(t*37)*math.sin(t*5.3)); hk=1.0
    else:
        A_,B2,ta,tb,u=pair
        l1,h1=render_scene(ta,A_); l2,h2=render_scene(tb,B2)
        f1=flick(min(1,u*2),fr*7+1,False) if u<0.5 else 0.0
        f2=flick(max(0,u*2-1),fr*7+3,True) if u>=0.5 else 0.0
        light=(l1.light(f1) if f1>0 else 0)+(l2.light(f2) if f2>0 else 0)
        hud=h1 if u<0.5 else h2; hk=f1 if u<0.5 else f2
    buf=WALL*(1+0.0)+(light if not isinstance(light,int) else 0)
    buf=buf+(light*0.0 if isinstance(light,np.ndarray) else 0)
    buf=np.clip(buf,0,1.3)*VIG*BAND+GR[fr%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
