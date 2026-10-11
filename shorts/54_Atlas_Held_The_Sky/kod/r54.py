import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid54")
for p in ["/home/claude/vid54","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from drawkit import part, dl, circ_pts, rotp, dashl
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= palette (planetarium dome projection) =================
GOLDP=(1.0,0.84,0.52); ICE=(0.62,0.82,1.0); ROSEP=(1.0,0.56,0.52); WHITEP=(0.94,0.96,1.0)
cGold=(255,214,140); cIce=(160,210,255); cRose=(255,150,140); cWhite=(240,244,255)
CZ="/home/claude/vid54/Cinzel.ttf"
_PT={}
def ptxt(d,s,x,y,fs=90,a=1.0,sc=1.0,col=cGold,wt=700):
    """projected lettering: soft halo + crisp core"""
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); k=(s,n,col,wt)
    if k not in _PT:
        f=ImageFont.truetype(CZ,n); f.set_variation_by_axes([wt])
        while f.getlength(s)>980 and n>16: n-=4; f=ImageFont.truetype(CZ,n); f.set_variation_by_axes([wt])
        bb=ImageDraw.Draw(Image.new("L",(4,4))).textbbox((0,0),s,font=f); tw,th=bb[2]-bb[0],bb[3]-bb[1]; pad=int(n*0.5)
        base=Image.new("L",(tw+2*pad,th+2*pad),0); ImageDraw.Draw(base).text((pad-bb[0],pad-bb[1]),s,font=f,fill=255)
        A=np.array(base).astype(np.float32)/255; g=cv2.GaussianBlur(A,(0,0),n*0.18)
        c=np.array(col,np.float32)/255; alpha=np.clip(A+g*0.8,0,1)
        rgb=np.where(A[...,None]>0.05,np.clip(c*0.7+0.3,0,1)[None,None,:]*np.ones_like(A)[...,None],c[None,None,:]*np.ones_like(A)[...,None])
        _PT[k]=Image.fromarray(np.dstack([rgb*255,alpha*255]).astype(np.uint8),"RGBA")
    im=_PT[k]
    if a<0.99: ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); im=Image.fromarray(ar)
    paste(d,im,x-im.width/2,y-im.height/2)
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= dome =================
_g=np.random.default_rng(1595)
DOME=np.zeros((h,w,3),np.float32); grad(DOME,[(0,(0.02,0.03,0.08)),(500,(0.04,0.06,0.14)),(820,(0.07,0.09,0.18)),(960,(0.02,0.02,0.04))])
_mw=np.exp(-(((xx-yy*0.55-40)/70)**2))*(0.6+0.4*cv2.GaussianBlur(_g.random((h,w)).astype(np.float32),(0,0),14)*2)
DOME+=(np.clip(_mw,0,1)*0.06)[...,None]*np.array((0.7,0.75,1.0),np.float32)
STARS=np.zeros((h,w),np.float32)
for k in range(900):
    x,y=_g.uniform(0,w),_g.uniform(0,860); b=_g.random()**3
    cv2.circle(STARS,(int(x),int(y)),1 if b<0.6 else 2,float(0.25+0.75*b),-1)
STARS=cv2.GaussianBlur(STARS,(0,0),0.6)
DOME+=STARS[...,None]*np.array((0.85,0.9,1.0),np.float32)*0.8
# audience silhouettes under the dome
_au=M()
for k in range(14):
    x=k*42+_g.uniform(-6,6); _au.circ(x,905+_g.uniform(-4,4),22).rect(x-28,915,x+28,h)
_aA=cv2.GaussianBlur(_au.f(),(0,0),1.5)[...,None]
DOMEV=(1-0.45*np.clip(((xx/w-0.5)**2*1.4+((yy-430)/h)**2*1.6)*2.0,0,1))[...,None].astype(np.float32)
# ================= projected line art =================
class Proj:
    def __init__(s): s.L={}; s.F={}
    def line(s,m,col=GOLDP,a=1.0):
        if a<=0.01 or m.x1<=m.x0: return
        A=m.f()*a; s.L[col]=np.maximum(s.L[col],A) if col in s.L else A
    def fill(s,m,col=GOLDP,a=0.12):
        if a<=0.005 or m.x1<=m.x0: return
        A=m.f()*a; s.F[col]=np.maximum(s.F[col],A) if col in s.F else A
    def render(s,mult=1.0):
        out=np.zeros((h,w,3),np.float32)
        for col,A in s.F.items(): out+=cv2.GaussianBlur(A,(0,0),2)[...,None]*np.array(col,np.float32)
        for col,A in s.L.items():
            c=np.array(col,np.float32); out+=(cv2.GaussianBlur(A,(0,0),1.0)*0.95+cv2.GaussianBlur(A,(0,0),6)*0.55)[...,None]*c+(A*0.35)[...,None]
        return out*mult
def C(cx,cy,r,u=1.0,th=2.2,a0=-math.pi/2): return dl(M(),circ_pts(cx,cy,r,r,a0,a0+2*math.pi,max(30,int(r))),u,th)
def titan(pr,x,y,s,a=1.0,arms=1.0,col=GOLDP,kneel=1.0):
    """kneeling Titan bearing a sphere on his shoulders"""
    m=M()
    hx,hy=x,y-190*s
    dl(m,circ_pts(hx,hy,17*s,19*s,0,2*math.pi,30),1,2.2)
    m.pline([(x-30*s,y-170*s),(x-40*s,y-110*s),(x-30*s,y-60*s),(x+28*s,y-60*s),(x+40*s,y-110*s),(x+30*s,y-170*s),(x-30*s,y-170*s)],2.2)
    for sd in (-1,1):
        sh=(x+sd*30*s,y-168*s); el=(x+sd*62*s,y-200*s+30*s*(1-arms)); hd=(x+sd*50*s,y-245*s+60*s*(1-arms))
        m.pline([sh,el,hd],2.2)
    m.pline([(x-24*s,y-60*s),(x-60*s,y-20*s*kneel),(x-40*s,y+0)],2.2)
    m.pline([(x+20*s,y-60*s),(x+44*s,y-10*s),(x+30*s,y+50*s*kneel-50*s*(1-kneel)),(x+70*s,y+50*s*kneel-50*s*(1-kneel))],2.2)
    pr.line(m,col,a); pr.fill(M().poly([(x-30*s,y-170*s),(x+30*s,y-170*s),(x+28*s,y-60*s),(x-30*s,y-60*s)]),col,0.10*a)
    jm=M()
    for px,py in ((x-30*s,y-170*s),(x+30*s,y-170*s),(x-62*s,y-200*s+30*s*(1-arms)),(x+62*s,y-200*s+30*s*(1-arms)),(x-50*s,y-245*s+60*s*(1-arms)),(x+50*s,y-245*s+60*s*(1-arms)),(x-30*s,y-60*s),(x+28*s,y-60*s),(x-60*s,y-20*s*kneel),(x+44*s,y-10*s)):
        jm.circ(px,py,3.2)
    pr.line(jm,WHITEP,a)
def cel_sphere(pr,cx,cy,R,t,a=1.0,detail=1.0,col=GOLDP):
    pr.line(C(cx,cy,R,1,2.4),col,a); pr.fill(M().circ(cx,cy,R),col,0.07*a)
    m=M()
    for k in range(-2,3):
        ry=R*0.9*abs(math.cos(k*0.5)); yy_=cy+R*math.sin(k*0.5)
        if k!=0: m.pline(circ_pts(cx,yy_,R*math.cos(k*0.5),R*0.12,0,2*math.pi,40),1.2)
    m.pline(circ_pts(cx,cy,R,R*0.25,0,2*math.pi,60),1.6)
    for k in range(3):
        rx=R*abs(math.cos(t*0.4+k*1.05)); m.pline(circ_pts(cx,cy,rx,R,-math.pi/2,math.pi/2,30) if math.cos(t*0.4+k*1.05)>0 else circ_pts(cx,cy,rx,R,math.pi/2,1.5*math.pi,30),1.0)
    pr.line(m,col,0.55*a)
    eb=rotp(circ_pts(cx,cy,R*0.98,R*0.32,0,2*math.pi,60),0.4,cx,cy); pr.line(dl(M(),eb,1,1.8),ROSEP,0.7*a)
    if detail>0:
        g=np.random.default_rng(7); cm=M(); sm_=M()
        for k in range(9):
            an=g.uniform(0,2*math.pi); rr=g.uniform(0.15,0.8)*R; ox,oy=cx+math.cos(an+t*0.15)*rr,cy+math.sin(an+t*0.15)*rr*0.9
            pts=[(ox+g.normal(0,10*R/120),oy+g.normal(0,10*R/120)) for _ in range(4)]
            cm.pline(pts,1.0)
            for p in pts: sm_.circ(p[0],p[1],1.8*R/120)
        pr.line(cm,ICE,0.8*a*detail); pr.line(sm_,WHITEP,a*detail)
def earthglobe(pr,cx,cy,R,a=1.0,t=0.0):
    pr.line(C(cx,cy,R,1,2.4),ICE,a)
    m=M()
    g=np.random.default_rng(3)
    for k,(dx,dy,rr) in enumerate(((-0.32,-0.15,0.32),(0.3,0.15,0.28),(0.05,-0.55,0.16))):
        ph=g.uniform(0,6,5); pts=[]
        for q in np.linspace(0,2*math.pi,40):
            r=rr*R*(1+0.25*math.sin(3*q+ph[0])+0.15*math.sin(5*q+ph[1])); pts.append((cx+dx*R+math.cos(q)*r*0.8,cy+dy*R+math.sin(q)*r))
        m.pline(pts,1.6)
    m.pline(circ_pts(cx,cy,R*0.45,R,-math.pi/2,math.pi/2,30),1.0)
    pr.line(m,ICE,0.8*a)
def bolt(pr,x,y,s,a=1.0):
    pr.line(dl(M(),[(x,y),(x-20*s,y+60*s),(x+10*s,y+60*s),(x-14*s,y+130*s)],1,2.6),WHITEP,a)
def flatworld(pr,cx,cy,R,a=1.0,t=0.0):
    pr.line(dl(M(),circ_pts(cx,cy,R,R*0.18,0,2*math.pi,80),1,2),ICE,a)
    m=M()
    for k in range(10):
        x=cx-R+k*R*0.04; m.line((x,cy+4),(x+2,cy+60+((t*80+k*13)%40)),1.2)
    pr.line(m,ICE,0.6*a)
def mountains_line(pr,x0,x1,y,h_,a=1.0,u=1.0,col=GOLDP):
    pts=[]
    for k in range(25):
        f=k/24; pts.append((x0+(x1-x0)*f,y-h_*(0.5+0.5*math.sin(f*9.3))*abs(math.sin(f*math.pi))**0.6))
    pr.line(dl(M(),pts,u,2.2),col,a)
def statue(pr,x,y,s,a=1.0):
    pr.line(dl(M(),[(x-80*s,y),(x+80*s,y),(x+70*s,y-40*s),(x-70*s,y-40*s),(x-80*s,y)],1,2.2),WHITEP,a)
    titan(pr,x,y-40*s,s,a,1.0,WHITEP)
def book(pr,x,y,s,a=1.0):
    m=M(); dl(m,[(x-120*s,y),(x,y-14*s),(x+120*s,y),(x+120*s,y-150*s),(x,y-164*s),(x-120*s,y-150*s),(x-120*s,y)],1,2.2); m.line((x,y-14*s),(x,y-164*s),2)
    pr.line(m,GOLDP,a)
    lm=M()
    for k in range(5): lm.line((x-100*s,y-130*s+k*22*s),(x-14*s,y-140*s+k*22*s),1); lm.line((x+14*s,y-140*s+k*22*s),(x+100*s,y-130*s+k*22*s),1)
    pr.line(lm,GOLDP,0.4*a)
def coasts(pr,a=1.0,t=0.0):
    L=[(120+20*math.sin(y/40)+15*math.sin(y/17),y) for y in range(150,700,10)]
    R=[(420-25*math.sin(y/50)-12*math.sin(y/23)+(30 if y>420 else 0),y) for y in range(150,700,10)]
    pr.line(dl(M(),L,1,2.4),ICE,a); pr.line(dl(M(),R,1,2.4),ICE,a)
    m=M()
    for k in range(9):
        y=180+k*55; m.pline([(170+x*2,y+5*math.sin(x/8+t*2+k)) for x in range(0,110)],1.2)
    pr.line(m,ICE,0.5*a)
# ================= scenes =================
def s_hook(t,sc):
    tt=max(t,-1.0); pr=Proj()
    titan(pr,270,540,1.15,1.0,1.0,GOLDP)
    eg=1-sm((tt-EV["holding"]+0.3)/0.5)
    if eg>0: earthglobe(pr,270,540-245*1.15-74,82,eg,tt)
    if eg<1: cel_sphere(pr,270,540-245*1.15-74,82,tt,1-eg,1.0)
    xk=sm((tt-EV["wrong"]+0.1)/0.3)*eg
    if xk>0: pr.line(dl(M(),[(190,85),(350,245)],xk,3).line((350,85),(190,245),3) if xk>0.5 else dl(M(),[(190,85),(350,245)],xk,3),ROSEP,1.0)
    def hd(d,t=t):
        k0=1.0 if t<0.4 else ap(t,-1,EV["logos"])
        ptxt(d,"ATLAS NEVER CARRIED",540,1250,64,a=k0,col=cWhite); ptxt(d,"THE EARTH",540,1330,104,a=k0,col=cRose)
        ptxt(d,"STATUES & LOGOS: WRONG",540,1260,60,a=ap(t,EV["logos"],EV["what"]),col=cRose)
        ptxt(d,"SO WHAT WAS IT?",540,1260,80,a=ap(t,EV["what"],sc["e"]+1),sc=pop(t,EV["what"]-0.1),col=cGold)
    return pr,[hd]
def s_myth(t,sc):
    pr=Proj()
    pP=sm((t-EV["perseus"]+0.3)/0.4); pH=sm((t-EV["heracles"]+0.3)/0.4)*(1-pP); pM=(1-sm((t-EV["heracles"]+0.3)/0.4))
    if pM>0:
        a=pM
        if t<EV["punish"]-0.1:
            titan(pr,200,540,1.1,a,0.3,GOLDP,1.0); bolt(pr,380,150,1.3,a*sm((t-EV["zeus"]+0.3)/0.3)); pr.line(C(380,140,18),WHITEP,0.0)
        else:
            flatworld(pr,240,580,230,a,t)
            titan(pr,430,570,0.85,a,1.0,GOLDP)
            sk=sm((t-EV["sky"]+0.4)/0.6)
            if sk>0:
                arc=circ_pts(270,580,420,440,math.pi*1.08,math.pi*1.92,60); pr.line(dl(M(),arc,sk,2.4),GOLDP,a); pr.fill(M().poly(arc+[(690,580),(-150,580)]),GOLDP,0.05*a*sk)
            hv=sm((t-EV["heavens"]+0.2)/0.4)
            if hv>0: cel_sphere(pr,430,570-245*0.85-50,60,t,a*hv,0.6)
            pl=sm((t-EV["planet"]+0.2)/0.3)*(1-hv)
            if pl>0: earthglobe(pr,430,570-245*0.85-50,60,a*pl,t)
    if pH>0:
        a=pH
        titan(pr,170,540,1.0,a,1.0,ICE); cel_sphere(pr,170,540-245-40,60,t,a,0.4)
        titan(pr,380,540,1.0,a,0.2,GOLDP,0.0)
        am=M()
        for k in range(3): am.circ(420+k*24,380,10)
        pr.line(am,ROSEP,a); pr.fill(M().circ(420,380,10).circ(444,380,10).circ(468,380,10),ROSEP,0.3*a)
    if pP>0:
        a=pP; st=sm((t-EV["stone"]+0.2)/0.8)
        pr.line(dl(M(),[(90,540),(100,420),(70,370),(110,340),(150,370)],1,2.2),WHITEP,a*(1-st*0.3))
        pr.line(C(130,320,24,1,2.2),WHITEP,a); m=M()
        for k in range(7): an=-math.pi+k*0.5; m.pline([(130+math.cos(an)*24+math.cos(an)*q*20+4*math.sin(q*9+t*4),320+math.sin(an)*24+math.sin(an)*q*20) for q in np.linspace(0,1,10)],1.4)
        pr.line(m,ROSEP,a)
        titan(pr,360,540,1.0,a*(1-st),1.0,GOLDP)
        mountains_line(pr,200,540,550,300,a*st,st,GOLDP)
    def hd(d,t=t):
        ptxt(d,"A TITAN",540,1250,90,a=ap(t,EV["titan"],EV["punish"]),sc=pop(t,EV["titan"]-0.1))
        ptxt(d,"VS. ZEUS — AND LOST",540,1335,56,a=ap(t,EV["zeus"],EV["punish"]),col=cRose)
        ptxt(d,"THE WESTERN EDGE OF THE WORLD",540,180,48,a=ap(t,EV["west"],EV["planet"]),col=cIce)
        ptxt(d,"HOLD UP THE SKY",540,1250,84,a=ap(t,EV["sky"],EV["planet"]),sc=pop(t,EV["sky"]-0.1))
        ptxt(d,"FOREVER",540,1335,70,a=ap(t,EV["forever"],EV["planet"]),col=cRose)
        ptxt(d,"NOT THE PLANET",540,1250,80,a=ap(t,EV["planet"],EV["heracles"]),col=cIce)
        ptxt(d,"THE HEAVENS",540,1335,96,a=ap(t,EV["heavens"],EV["heracles"]),sc=pop(t,EV["heavens"]-0.1))
        ptxt(d,"HERACLES’ TRICK",540,1260,84,a=ap(t,EV["heracles"],EV["perseus"]),sc=pop(t,EV["heracles"]-0.1),col=cIce)
        ptxt(d,"PERSEUS + MEDUSA",540,180,66,a=ap(t,EV["perseus"],sc["e"]+1),col=cRose)
        ptxt(d,"THE ATLAS MOUNTAINS",540,1260,74,a=ap(t,EV["mountains"],sc["e"]+1),sc=pop(t,EV["mountains"]-0.1))
    return pr,[hd]
def s_statue(t,sc):
    pr=Proj()
    z=sm((t-EV["look"]+0.3)/0.8)
    a1=1-z
    if a1>0:
        statue(pr,270,580,1.0,a1*sm((t-sc["s"]+0.2)/0.6))
        cel_sphere(pr,270,580-40-245-66,72,t,a1,0.3,WHITEP)
    if z>0:
        cel_sphere(pr,270,380,210,t,z,1.0,GOLDP)
        hl=sm((t-EV["const"]+0.2)/0.5)
        if hl>0:
            m=M(); o=[(200,330),(230,300),(260,320),(250,370),(215,380),(200,330)]; dl(m,o,hl,2.4)
            o2=[(300,450),(330,430),(360,450),(345,490),(310,500)]; dl(m,o2,hl,2.4); pr.line(m,ROSEP,z)
    def hd(d,t=t):
        ptxt(d,"THE FARNESE ATLAS",540,170,76,a=ap(t,EV["farnese"],EV["look"]),sc=pop(t,EV["farnese"]-0.1))
        ptxt(d,"ROMAN MARBLE · ~1,900 YEARS OLD",540,260,44,a=ap(t,EV["roman"],EV["look"]),col=cIce)
        ptxt(d,"LOOK CLOSELY…",540,170,80,a=ap(t,EV["look"],EV["const"]),col=cIce)
        ptxt(d,"CONSTELLATIONS",540,170,96,a=ap(t,EV["const"],sc["e"]+1),sc=pop(t,EV["const"]-0.1),col=cGold)
        ptxt(d,"ONE OF THE OLDEST SKY MAPS",540,1330,56,a=ap(t,EV["oldest"],sc["e"]+1),col=cRose)
    return pr,[hd]
def s_name(t,sc):
    pr=Proj()
    pA=sm((t-EV["atlantic"]+0.3)/0.4); pR=sm((t-EV["nomatter"]+0.3)/0.4)
    a1=1-pA; a2=pA*(1-pR); a3=pR
    if a1>0:
        book(pr,270,520,1.4,a1*sm((t-EV["mercator"]+0.4)/0.5))
        titan(pr,270,340,0.5,a1*sm((t-EV["titled"]+0.3)/0.4)); cel_sphere(pr,270,340-122-24,26,t,a1*sm((t-EV["titled"]+0.3)/0.4),0)
    if a2>0: coasts(pr,a2,t)
    if a3>0:
        titan(pr,270,540,1.15,a3,1.0,GOLDP); cel_sphere(pr,270,540-245*1.15-74,82,t,a3,1.0)
    def hd(d,t=t):
        ptxt(d,"1595",540,170,120,a=ap(t,EV["y1595"],EV["atlantic"]),sc=pop(t,EV["y1595"]-0.1))
        ptxt(d,"MERCATOR’S MAPS",540,1260,70,a=ap(t,EV["mercator"],EV["titled"]),col=cIce)
        ptxt(d,"“ATLAS”",540,1260,110,a=ap(t,EV["titled"],EV["atlantic"]),sc=pop(t,EV["titled"]-0.1),col=cGold)
        ptxt(d,"THE NAME STUCK",540,1340,56,a=ap(t,EV["stuck"],EV["atlantic"]),col=cRose)
        ptxt(d,"ATLANTIC",540,170,110,a=ap(t,EV["atlantic"],EV["nomatter"]),sc=pop(t,EV["atlantic"]-0.1),col=cIce)
        ptxt(d,"= THE SEA OF ATLAS",540,1260,70,a=ap(t,EV["sea"]-0.2,EV["nomatter"]),sc=pop(t,EV["sea"]-0.3))
    return pr,[hd]
SCN=dict(hook=s_hook,myth=s_myth,statue=s_statue,name=s_name)
BAND=(1-0.30*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.012,(h,w,1)).astype(np.float32) for i in range(6)]
TR=0.36; TOTAL=B.TOTAL; LOOPD=0.7
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
PIV=(270,1150)
def rot(img,ang):
    Mx=cv2.getRotationMatrix2D(PIV,math.degrees(ang),1.0); return cv2.warpAffine(img,Mx,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(sc,SC[i+1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SC[i-1],sc,t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(sc,SC[0],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    drift=0.004*math.sin(t*0.3)
    if pair is None:
        pr,hud=render_scene(t,sc); sky=rot(pr.render(),drift); hk=1.0
    else:
        A_,B2,ta,tb,u=pair
        p1,h1=render_scene(ta,A_); p2,h2=render_scene(tb,B2); k=sm(u)
        # the whole dome sky wheels around the pole: old projection rotates away, new one rotates in
        sky=rot(p1.render(1-k),-0.55*k+drift)+rot(p2.render(k),0.55*(1-k)+drift)
        hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    stars_rot=rot(DOME,(0 if pair is None else (-0.55*sm(pair[4]) if pair[4]<0.5 else 0.55*(1-sm(pair[4]))))*0.4+drift)
    buf=stars_rot+sky
    buf=buf*(1-_aA)+np.array((0.01,0.01,0.02),np.float32)*_aA
    buf=np.clip(buf,0,1.3)*DOMEV*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
