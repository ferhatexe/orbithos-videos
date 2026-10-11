import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid59")
for p in ["/home/claude/vid59","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= cased daguerreotype =================
OX0,OX1,OY0,OY1=66,474,64,560          # opening in the brass mat
ARC_CY,ARC_AY=210,146
def _open_mask():
    m=M().rect(OX0,ARC_CY,OX1,OY1).ell((OX0+OX1)/2,ARC_CY,(OX1-OX0)/2,ARC_AY); return cv2.GaussianBlur(m.f(),(0,0),0.8)
OPEN=_open_mask()
_dist=cv2.distanceTransform((OPEN>0.5).astype(np.uint8),cv2.DIST_L2,5).astype(np.float32)
_g=np.random.default_rng(59)
_n1=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),30); _n1/=_n1.std()
_n2=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),3); _n2/=_n2.std()
ang=np.arctan2(yy-330,xx-270)
# tarnish halo: iridescent ring hugging the mat opening
_tk=np.exp(-_dist/11)*(0.75+0.25*_n1)*0.6
TARN=np.stack([0.5+0.5*np.sin(ang*2+_n1*1.5),0.5+0.5*np.sin(ang*2+2.1+_n1*1.5),0.5+0.5*np.sin(ang*2+4.2+_n1*1.5)],-1).astype(np.float32)
TARN=TARN*np.array((0.55,0.35,0.85),np.float32)+np.array((0.25,0.15,0.0),np.float32)
VIGP=np.clip(1-np.exp(-_dist/55)*0.55,0,1).astype(np.float32)
DUST=np.zeros((h,w),np.float32)
for _ in range(70): cv2.circle(DUST,(int(_g.uniform(OX0,OX1)),int(_g.uniform(OY0,OY1))),int(_g.choice([1,1,1,2])),float(_g.uniform(0.2,0.6)),-1,cv2.LINE_AA)
for _ in range(6):
    x0,y0=_g.uniform(OX0,OX1),_g.uniform(OY0,OY1); a=_g.uniform(0,math.pi); L=_g.uniform(20,90)
    cv2.line(DUST,(int(x0),int(y0)),(int(x0+math.cos(a)*L),int(y0+math.sin(a)*L)),float(_g.uniform(0.2,0.5)),1,cv2.LINE_AA)
DUST=cv2.GaussianBlur(DUST,(0,0),0.5)
def _case():
    """leather case + engraved brass mat; returns colour, alpha (1 = case covers plate)"""
    C=np.zeros((h,w,3),np.float32)
    leather=np.array((0.10,0.06,0.04),np.float32)*(1+0.10*_n2[...,None]+0.06*_n1[...,None])
    C[:]=leather
    mat=M().rect(36,30,504,668).f()
    br=(0.60,0.46,0.22); brass=np.array(br,np.float32)*(0.82+0.18*np.cos((xx*0.9+yy*0.4)*0.05)[...,None])*(1+0.05*_n2[...,None])
    C=C*(1-mat[...,None])+brass*mat[...,None]
    # engraved floral scroll lines on the mat
    eng=np.zeros((h,w),np.float32)
    for k in range(26):
        a0=k*2*math.pi/26; r1,r2=240,262
        cx,cy=270,330
        pts=[(cx+math.cos(a0+s*0.18)*(r1+(r2-r1)*abs(math.sin(s*3)))*0.95,cy+math.sin(a0+s*0.18)*(r1+(r2-r1)*abs(math.sin(s*3)))*1.25) for s in np.linspace(0,1,8)]
        cv2.polylines(eng,[np.round(np.array(pts)*16).astype(np.int32)],False,1.0,1,cv2.LINE_AA,4)
    eng*=mat*(1-cv2.GaussianBlur(OPEN,(0,0),6)*1.0)
    C*=(1-0.35*eng)[...,None]
    # bevelled edge round the opening
    _dout=cv2.distanceTransform((OPEN<0.5).astype(np.uint8),cv2.DIST_L2,5).astype(np.float32)
    edge=np.exp(-(_dout/3.0)**2)*mat; shade=np.exp(-(_dout/14.0))*mat
    C*=(1-0.35*shade)[...,None]; C+=(edge*0.30)[...,None]*np.array((1,0.9,0.6),np.float32)*(1-OPEN)[...,None]
    # nameplate cartouche on the mat foot
    np_=M().rect(120,582,420,652).f(); k=np.clip((yy-582)/70,0,1)[...,None]
    pl=np.array((0.93,0.80,0.52),np.float32)*(1-k)+np.array((0.78,0.62,0.34),np.float32)*k
    C=C*(1-np_[...,None])+pl*np_[...,None]
    cv2.rectangle(C,(120,582),(420,652),(0.30,0.20,0.08),2); cv2.rectangle(C,(126,588),(414,646),(0.45,0.32,0.12),1)
    # stamped gold border on the leather
    cv2.rectangle(C,(14,12),(526,948),(0.60,0.45,0.18),2); cv2.rectangle(C,(22,20),(518,940),(0.60,0.45,0.18),1)
    A=1-OPEN
    return C,A
CASE,CASEA=_case()
def tone(G,neg=0.0,glare=0.0):
    """silver plate: neutral-cool positive, brown-blue negative when tilted, iridescent tarnish at the rim"""
    G=np.clip(G,0,1)
    pos=G[...,None]*np.array((0.90,0.91,0.93),np.float32)+0.04
    ng=(1-G)[...,None]*np.array((0.55,0.48,0.40),np.float32)+np.array((0.05,0.07,0.12),np.float32)
    img=pos*(1-neg)+ng*neg
    img=img*VIGP[...,None]
    img=img*(1-_tk[...,None]*0.75)+TARN*_tk[...,None]*0.75
    img+=(DUST*0.5)[...,None]
    img+=glare[...,None]*np.array((1.0,0.98,0.94),np.float32) if isinstance(glare,np.ndarray) else 0
    return img
# ================= painting in grey (photographic) =================
def gpaint(G,m,v,a=1.0,soft=0.0):
    A=m.f() if isinstance(m,M) else m
    if soft>0: A=cv2.GaussianBlur(A,(0,0),soft)
    G+=(v-G)*A*a
def ggrad(G,m,v0,v1,x0,y0,x1,y1,a=1.0):
    A=m.f() if isinstance(m,M) else m
    dx,dy=x1-x0,y1-y0; k=np.clip(((xx-x0)*dx+(yy-y0)*dy)/(dx*dx+dy*dy),0,1); v=v0*(1-k)+v1*k; G+=(v-G)*A*a
def backdrop(v0=0.62,v1=0.30):
    G=np.full((h,w),v1,np.float32); d=((xx-270)**2/1.2+(yy-300)**2)/(2*230**2); G+=(v0-v1)*np.exp(-d); G+=0.025*_n1; return G
def portrait(G,cx,cy,s,t=0.0,rod=True):
    """seated man, scarred brow, left eye closed, holding the tamping iron (photo is mirror-reversed)"""
    body=M().poly([(cx-150*s,cy+330*s),(cx-118*s,cy+120*s),(cx-60*s,cy+70*s),(cx+60*s,cy+70*s),(cx+118*s,cy+120*s),(cx+150*s,cy+330*s)])
    ggrad(G,body,0.22,0.10,cx-150*s,cy,cx+150*s,cy)
    gpaint(G,M().poly([(cx-34*s,cy+72*s),(cx+34*s,cy+72*s),(cx,cy+170*s)]),0.86,soft=1)
    gpaint(G,M().poly([(cx-14*s,cy+80*s),(cx+14*s,cy+80*s),(cx+8*s,cy+150*s),(cx-8*s,cy+150*s)]),0.12)
    for sg in (-1,1): gpaint(G,M().line((cx+sg*34*s,cy+74*s),(cx+sg*20*s,cy+190*s),5*s),0.30,soft=1)
    gpaint(G,M().rect(cx-22*s,cy+20*s,cx+22*s,cy+80*s),0.55,soft=1)
    head=M().ell(cx,cy-30*s,62*s,80*s); ggrad(G,head,0.80,0.45,cx-60*s,cy-60*s,cx+70*s,cy+20*s)
    gpaint(G,M().ell(cx-64*s,cy-24*s,10*s,20*s),0.55,soft=1); gpaint(G,M().ell(cx+64*s,cy-24*s,10*s,20*s),0.40,soft=1)
    hair=M().poly([(cx-66*s,cy-40*s),(cx-60*s,cy-100*s),(cx-20*s,cy-122*s),(cx+30*s,cy-120*s),(cx+64*s,cy-90*s),(cx+66*s,cy-40*s),(cx+50*s,cy-80*s),(cx-10*s,cy-96*s),(cx-50*s,cy-80*s)])
    gpaint(G,hair,0.12,soft=1)
    gpaint(G,M().line((cx-38*s,cy-52*s),(cx-14*s,cy-56*s),4*s),0.18,soft=1); gpaint(G,M().line((cx+14*s,cy-56*s),(cx+38*s,cy-50*s),4*s),0.18,soft=1)
    gpaint(G,M().ell(cx-26*s,cy-38*s,9*s,5*s),0.10,soft=0.8); gpaint(G,M().circ(cx-24*s,cy-39*s,2*s),0.9)
    gpaint(G,M().line((cx+16*s,cy-36*s),(cx+36*s,cy-34*s),2.5*s),0.16,soft=0.8)          # closed eye
    gpaint(G,M().line((cx+10*s,cy-70*s),(cx+30*s,cy-100*s),3*s),0.92,0.7,soft=1.2)        # scar on the brow
    gpaint(G,M().poly([(cx-2*s,cy-30*s),(cx+6*s,cy+4*s),(cx-8*s,cy+6*s)]),0.55,soft=1)
    gpaint(G,M().line((cx-16*s,cy+26*s),(cx+16*s,cy+26*s),3*s),0.25,soft=1)
    gpaint(G,M().poly([(cx-50*s,cy+10*s),(cx-30*s,cy+46*s),(cx+30*s,cy+46*s),(cx+50*s,cy+10*s),(cx+40*s,cy+40*s),(cx,cy+60*s),(cx-40*s,cy+40*s)]),0.25,0.6,soft=2)  # beard shadow
    if rod:
        x0,y0,x1,y1=cx-40*s,cy+320*s,cx+150*s,cy-220*s
        gpaint(G,M().line((x0,y0),(x1,y1),11*s),0.30,soft=0.8)
        gpaint(G,M().line((x0+3*s,y0),(x1+2*s,y1+2*s),3*s),0.85,0.8,soft=0.8)
        gpaint(G,M().poly([(x1-5*s,y1+8*s),(x1+5*s,y1-2*s),(x1+18*s,y1-30*s)]),0.30)
    for q in ((0.18,),(0.48,)):
        hx,hy=cx-40*s+190*s*q[0],cy+320*s-540*s*q[0]
        gpaint(G,M().ell(hx,hy,26*s,18*s,-40),0.72,soft=1.2)
def finish(G,soft=0.9):
    if soft>0: G=cv2.GaussianBlur(G,(0,0),soft)
    return G+0.035*_n2*0.5
# ================= fonts / HUD =================
_IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(P.FD+n,s)
    return _IF[k]
def plate_title(d,s,a=1.0,sc=1.0,fs=58):
    """engraved into the brass nameplate"""
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f("LibreBaskerville-Regular.ttf",n)
    while f.getlength(s)>520 and n>18: n-=2; f=_f("LibreBaskerville-Regular.ttf",n)
    A=int(255*a); y=1232
    d.text((W/2+2,y+2),s,font=f,fill=(255,230,170,int(150*a)),anchor="mm")
    d.text((W/2,y),s,font=f,fill=(48,30,10,A),anchor="mm")
def slip(d,s,x,y,fs=36,a=1.0,sc=1.0,rot=0):
    """archival paper slip, handwritten in iron-gall ink"""
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f("CrimsonPro-Italic.ttf",n); tw=f.getlength(s); px,py=n*0.55,n*0.35
    d.rectangle((x-tw/2-px+5,y-n*0.55-py+6,x+tw/2+px+5,y+n*0.55+py+6),fill=(10,6,4,int(110*a)))
    d.rectangle((x-tw/2-px,y-n*0.55-py,x+tw/2+px,y+n*0.55+py),fill=(236,226,200,int(245*a)),outline=(120,90,60,int(200*a)),width=2)
    d.text((x,y),s,font=f,fill=(60,38,22,int(255*a)),anchor="mm")
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= shots (each returns a grey plate image) =================
def s_hook(t):
    G=backdrop(); z=1+0.01*t
    portrait(G,270,300,1.0*z,t); G=finish(G)
    def hd(d,t=t):
        slip(d,"the tamping iron",770,350,38,a=ap(t,EV["rod"],EV["lived"]),sc=pop(t,EV["rod"]-0.1))
        plate_title(d,"PHINEAS GAGE",a=ap(t,EV["holding"]-0.2,EV["lived"]-0.1),sc=pop(t,EV["holding"]-0.3))
        plate_title(d,"1848 – 1860",a=ap(t,EV["lived"],99),sc=pop(t,EV["lived"]-0.1))
    return G,[hd]
def worker(G,x,y,s,bend=0.0,v=0.16,arm=None):
    gpaint(G,M().circ(x+bend*24*s,y-150*s+bend*30*s,13*s),v)
    gpaint(G,M().poly([(x-18*s+bend*18*s,y-136*s+bend*30*s),(x+18*s+bend*24*s,y-136*s+bend*30*s),(x+16*s,y-60*s),(x-16*s,y-60*s)]),v)
    gpaint(G,M().line((x-8*s,y-62*s),(x-12*s,y),9*s),v); gpaint(G,M().line((x+8*s,y-62*s),(x+12*s,y),9*s),v)
    gpaint(G,M().ell(x+bend*24*s,y-162*s+bend*30*s,20*s,5*s),v)
    if arm: gpaint(G,M().line(arm[0],arm[1],6*s),v)
def s_blast(t):
    G=np.full((h,w),0.80,np.float32); ggrad(G,M().rect(0,0,w,h),0.86,0.70,0,60,0,330)
    gpaint(G,M().poly([(0,300),(120,260),(220,290),(330,240),(470,270),(w,250),(w,h),(0,h)]),0.52,soft=2)
    rock=M().poly([(0,360),(90,330),(160,350),(200,420),(210,560),(0,560)]); ggrad(G,rock,0.40,0.22,0,330,200,560)
    rock2=M().poly([(w,330),(420,320),(350,360),(330,430),(320,560),(w,560)]); ggrad(G,rock2,0.30,0.48,320,330,w,560)
    for k in range(6): gpaint(G,M().line((20+k*30,370+k*20),(120+k*15,420+k*24),2),0.18,0.6)
    gpaint(G,M().poly([(200,560),(260,470),(280,470),(320,560)]),0.62)
    for k in range(9): y=480+k*10; gpaint(G,M().line((262-k*7,y),(280+k*5,y),3),0.25)
    gpaint(G,M().line((262,470),(208,560),3),0.20); gpaint(G,M().line((280,470),(318,560),3),0.20)
    worker(G,110,520,0.9); worker(G,420,520,0.85)
    k=sm((t-EV["tamping"]+0.4)/0.4); bob=math.sin(t*9)*5*fa(t,EV["tamping"],EV["spark"],0.2,0.2)
    gx,gy=255,545
    worker(G,gx,gy,1.0,bend=0.5,v=0.12,arm=((gx+18,gy-110),(gx+40,gy-60+bob)))
    rx,ry=gx+42,gy-60+bob
    if t<EV["spark"]: gpaint(G,M().line((rx,ry-90),(rx,ry+18),5),0.30); gpaint(G,M().circ(rx,gy+12,6),0.08)
    fl=fa(t,EV["spark"],EV["spark"]+0.6,0.05,0.5)
    if fl>0:
        G+=(cv2.GaussianBlur(M().circ(rx,gy,90).f(),(0,0),40)*1.4*fl)
        for i in range(14):
            a=-math.pi/2+(i-7)*0.16; r=40+300*cl(t-EV["spark"]); gpaint(G,M().circ(rx+math.cos(a)*r,gy+math.sin(a)*r,4),0.95,fl)
    G=finish(G)
    def hd(d,t=t):
        plate_title(d,"VERMONT, 1848",a=ap(t,S("blast")["s"]+0.2,EV["tamping"]),sc=pop(t,S("blast")["s"]+0.1))
        slip(d,"railroad foreman",540,300,40,a=ap(t,EV["railroad"],EV["tamping"]))
        plate_title(d,"GUNPOWDER",a=ap(t,EV["tamping"]+0.2,EV["spark"]+0.15),sc=pop(t,EV["tamping"]+0.1))
        plate_title(d,"A SPARK",a=ap(t,EV["spark"],99),sc=pop(t,EV["spark"]-0.1))
    return G,[hd]
def skull_shape(G,cx,cy,s,v=0.80):
    cran=M().ell(cx+10*s,cy-30*s,150*s,130*s); face=M().poly([(cx-150*s,cy-10*s),(cx-160*s,cy+40*s),(cx-140*s,cy+90*s),(cx-120*s,cy+140*s),(cx-60*s,cy+170*s),(cx+10*s,cy+150*s),(cx+40*s,cy+80*s),(cx+100*s,cy+40*s)])
    m=np.maximum(cran.f(),face.f()); ggrad(G,m,v,v-0.35,cx-120*s,cy-120*s,cx+140*s,cy+120*s)
    gpaint(G,M().ell(cx-95*s,cy+10*s,30*s,26*s),0.12,soft=1)            # orbit
    gpaint(G,M().poly([(cx-150*s,cy+52*s),(cx-130*s,cy+44*s),(cx-140*s,cy+80*s)]),0.12,soft=1)
    gpaint(G,M().ell(cx+50*s,cy+30*s,20*s,26*s),0.25,soft=1.5)
    gpaint(G,M().poly([(cx-120*s,cy+100*s),(cx-50*s,cy+108*s),(cx-50*s,cy+118*s),(cx-120*s,cy+112*s)]),0.30,soft=1)
    for k in range(7): gpaint(G,M().line((cx-118*s+k*10*s,cy+102*s),(cx-118*s+k*10*s,cy+116*s),1.5*s),0.2)
    for a in np.linspace(-2.2,-0.5,5): gpaint(G,M().line((cx+10*s+math.cos(a)*120*s,cy-30*s+math.sin(a)*110*s),(cx+10*s+math.cos(a+0.15)*126*s,cy-30*s+math.sin(a+0.15)*116*s),1.5),0.45,0.6)
def s_skull(t):
    G=backdrop(0.70,0.36); cx,cy=290,330; s=1.0
    skull_shape(G,cx,cy,s)
    p0=(cx-95*s,cy+150*s); p1=(cx-40*s,cy-150*s); dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy); ux,uy=dx/L,dy/L
    tf=EV["blast"]-0.2; k=cl((t-tf)/(EV["flew"]-tf+0.4))
    if t>EV["meters"]-0.6: off=(t-(EV["meters"]-0.6))*900
    else: off=0
    head=L*(-0.6+1.6*k)+off; tail=head-1.25*L
    a_=(p0[0]+ux*tail,p0[1]+uy*tail); b_=(p0[0]+ux*head,p0[1]+uy*head)
    gpaint(G,M().line(a_,b_,14),0.26,soft=0.6); gpaint(G,M().line((a_[0]+3,a_[1]),(b_[0]+3,b_[1]),3),0.80,0.7)
    gpaint(G,M().poly([(b_[0]-7,b_[1]+6),(b_[0]+7,b_[1]+6),(b_[0]+ux*30,b_[1]+uy*30)]),0.26)
    if k>0.55:
        gpaint(G,M().circ(p0[0]+ux*L*0.82,p0[1]+uy*L*0.82,16),0.10,soft=1)       # exit wound on the crown
    G=finish(G)
    def hd(d,t=t):
        plate_title(d,"THE SHOT",a=ap(t,EV["blast"]-0.1,EV["six"]),sc=pop(t,EV["blast"]-0.2))
        slip(d,"6 kg · 1.1 m",780,260,40,a=ap(t,EV["six"],EV["landed"]),sc=pop(t,EV["six"]-0.1))
        slip(d,"in: under the cheekbone",340,1080,34,a=ap(t,EV["cheek"],EV["landed"]))
        slip(d,"out: top of the skull",400,190,34,a=ap(t,EV["top"],EV["landed"]+0.6))
        plate_title(d,"THROUGH THE SKULL",a=ap(t,EV["six"]+0.1,EV["landed"]),sc=pop(t,EV["six"]))
        plate_title(d,"IT LANDED METERS AWAY",fs=44,a=ap(t,EV["landed"],99),sc=pop(t,EV["landed"]-0.1))
    return G,[hd]
def s_cart(t):
    G=np.full((h,w),0.78,np.float32); ggrad(G,M().rect(0,0,w,h),0.86,0.66,0,60,0,400)
    gpaint(G,M().poly([(0,400),(w,380),(w,h),(0,h)]),0.55,soft=3)
    for k in range(5): gpaint(G,M().line((0,430+k*28),(w,420+k*30),2),0.45,0.6)
    x=150+12*(t-S("after")["s"])
    G0=G
    for dx in (0,70):
        ox=x+dx; gpaint(G,M().ell(ox,430,46,26),0.20); gpaint(G,M().ell(ox-50,410,16,14),0.18)
        for lx in (-28,-10,18,32): gpaint(G,M().line((ox+lx,450),(ox+lx,492),6),0.18)
        gpaint(G,M().line((ox-56,400),(ox-70,388),3),0.6)
    cx=x+190; worker(G,cx+10,452,0.55,v=0.10); gpaint(G,M().rect(cx+6,366,cx+24,373),0.95)
    gpaint(G,M().rect(cx-70,410,cx+70,450),0.30); gpaint(G,M().line((x+40,420),(cx-70,430),4),0.25)
    gpaint(G,M().circ(cx-40,465,30),0.14); gpaint(G,M().circ(cx-40,465,22),0.55); gpaint(G,M().circ(cx-40,465,5),0.14)
    for a in np.linspace(0,math.pi,4,endpoint=False): gpaint(G,M().line((cx-40+math.cos(a+t)*22,465+math.sin(a+t)*22),(cx-40-math.cos(a+t)*22,465-math.sin(a+t)*22),2.5),0.14)
   # bandage
    worker(G,cx-140,500,0.7,v=0.20)
    Mz=cv2.getRotationMatrix2D((330,440),0,1.55); G=cv2.warpAffine(G,Mz,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    G=finish(G)
    def hd(d,t=t):
        plate_title(d,"SITTING UP, TALKING",fs=50,a=ap(t,EV["sitting"]-0.2,99),sc=pop(t,EV["sitting"]-0.3))
        slip(d,"ox cart",640,640,38,a=ap(t,EV["cart"],99))
    return G,[hd]
def s_note(t):
    G=np.full((h,w),0.40,np.float32)
    pm=M().poly([(90,120),(450,100),(470,540),(110,560)]); ggrad(G,pm,0.88,0.72,90,100,470,560)
    rg=np.random.default_rng(5)
    for k in range(13):
        y=150+k*30; x0=124+k*1.4; ww=rg.uniform(220,310)
        if k==7: continue
        pts=[(x,y+2*math.sin(x/9+k)+(x-x0)*-0.04) for x in np.arange(x0,x0+ww,4)]; gpaint(G,M().pline(pts,2.4),0.30,0.85)
    hk=cl((t-EV["nolonger"]+0.2)/0.6)
    if hk>0: gpaint(G,M().poly([(130,352),(130+300*hk,345),(130+300*hk,375),(130,380)]),0.97,0.6)
    G=finish(G,0.7)
    def hd(d,t=t):
        slip(d,"Dr. John Harlow",760,180,38,a=ap(t,EV["doctor"],99))
        if hk>0: d.text((560,726),"“no longer Gage”",font=_f("CrimsonPro-Italic.ttf",int(64)),fill=(40,22,10,int(255*hk)),anchor="mm")
        plate_title(d,"“NO LONGER GAGE”",a=ap(t,EV["nolonger"],99),sc=pop(t,EV["nolonger"]-0.1))
        plate_title(d,"HE SURVIVED",a=ap(t,EV["survived"]-0.2,EV["nolonger"]-0.1),sc=pop(t,EV["survived"]-0.3))
    return G,[hd]
def s_chile(t):
    G=np.full((h,w),0.82,np.float32); ggrad(G,M().rect(0,0,w,h),0.90,0.74,0,60,0,320)
    gpaint(G,M().poly([(0,330),(80,200),(150,260),(250,150),(330,240),(420,170),(w,260),(w,h),(0,h)]),0.58,soft=2)
    gpaint(G,M().poly([(220,170),(250,150),(280,172),(262,168),(250,160),(238,170)]),0.92)
    gpaint(G,M().poly([(0,400),(150,370),(320,390),(w,360),(w,h),(0,h)]),0.40,soft=2)
    road=M().poly([(0,520),(w,470),(w,500),(0,560)]); gpaint(G,road,0.66,soft=1)
    x=-160+(t-S("chile")["s"])*95; yb=500-(x+100)*0.09
    for dx in (0,58):
        hx=x+250+dx; hy=yb-4; gpaint(G,M().ell(hx,hy-30,34,16),0.16); gpaint(G,M().line((hx+26,hy-40),(hx+44,hy-62),9),0.16); gpaint(G,M().ell(hx+50,hy-62,13,7,30),0.16)
        ph=t*10+dx
        for i,lx in enumerate((-22,-12,18,26)): gpaint(G,M().line((hx+lx,hy-20),(hx+lx+8*math.sin(ph+i*1.6),hy+12),4),0.16)
    gpaint(G,M().rect(x+40,yb-110,x+200,yb-30),0.20); gpaint(G,M().rect(x+60,yb-100,x+110,yb-70),0.55); gpaint(G,M().rect(x+130,yb-100,x+180,yb-70),0.55)
    gpaint(G,M().rect(x+30,yb-124,x+214,yb-110),0.12)
    for wx in (x+75,x+175):
        gpaint(G,M().circ(wx,yb-20,26),0.12); gpaint(G,M().circ(wx,yb-20,19),0.62); gpaint(G,M().circ(wx,yb-20,4),0.12)
    worker(G,x+214,yb-108,0.42,v=0.10)
    G=finish(G)
    def hd(d,t=t):
        plate_title(d,"STAGECOACH DRIVER",fs=52,a=ap(t,S("chile")["s"]+0.25,EV["hint"]-0.2),sc=pop(t,S("chile")["s"]+0.15))
        slip(d,"Santiago – Valparaíso",540,780,40,a=ap(t,EV["chile"],99),sc=pop(t,EV["chile"]-0.1))
        plate_title(d,"A HIDDEN RECOVERY?",fs=52,a=ap(t,EV["hint"]-0.1,99),sc=pop(t,EV["hint"]-0.2))
    return G,[hd]
def s_museum(t):
    G=backdrop(0.55,0.22)
    gpaint(G,M().rect(80,140,460,560),0.32); gpaint(G,M().rect(92,152,448,548),0.48)
    ggrad(G,M().poly([(92,152),(200,152),(92,330)]),0.80,0.48,92,152,200,330,0.6)
    gpaint(G,M().rect(110,480,430,500),0.28)
    skull_shape(G,250,350,0.55,0.86)
    gpaint(G,M().line((140,470),(420,180),9),0.30); gpaint(G,M().line((143,470),(422,182),2.5),0.85,0.7)
    G=finish(G)
    def hd(d,t=t):
        slip(d,"Warren Anatomical Museum",540,1060,36,a=ap(t,EV["hskull"],99),sc=pop(t,EV["hskull"]-0.1))
        plate_title(d,"HARVARD",fs=62,a=ap(t,S("harvard")["s"]+0.25,99),sc=pop(t,S("harvard")["s"]+0.15))
    return G,[hd]
def s_found(t):
    G=np.full((h,w),0.30,np.float32)+0.03*_n1
    k=sm((t-EV["turned"]+0.3)/1.4)
    s=0.45+0.55*k; cx,cy=270,300
    inner=np.zeros((h,w),np.float32); portrait(inner_g:=np.full((h,w),0.45,np.float32),cx,cy,s,t)
    frame=M().rect(cx-200*s,cy-250*s,cx+200*s,cy+260*s); gpaint(G,frame,0.62)
    win=M().ell(cx,cy+5*s,165*s,215*s).f(); G=G*(1-win)+inner_g*win
    if t<EV["y2009"]-0.2:
        q=fa(t,EV["century"],EV["y2009"]-0.2,0.3,0.3); G=G*(1-0.8*q)+0.30*0.8*q
    G=finish(G)
    def hd(d,t=t):
        plate_title(d,"NO KNOWN PHOTO",fs=54,a=ap(t,EV["century"]-0.3,EV["y2009"]-0.1),sc=pop(t,EV["century"]-0.4))
        plate_title(d,"FOUND IN 2009",fs=58,a=ap(t,EV["y2009"]-0.1,99),sc=pop(t,EV["y2009"]-0.2))
    return G,[hd]
TR=0.36; TOTAL=B.TOTAL; LOOPD=0.62
SHOTS=[(0.0,s_hook),(S("blast")["s"],s_blast),(S("skull")["s"],s_skull),(S("after")["s"],s_cart),(Lx("He survived")[0]-0.3,s_note),
       (S("chile")["s"],s_chile),(S("harvard")["s"],s_museum),(Lx("For a century")[0]-0.3,s_found)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None:
        G,hud=SHOTS[i][1](t); img=tone(G); hk=1.0
    else:
        fa_,fb_,ta,tb,u=pair
        G,hud=(fa_(ta) if u<0.5 else fb_(tb))
        k=math.sin(math.pi*u)          # the plate tilts: positive turns negative under the glare
        c=-250+1100*u; band=np.exp(-(((xx+yy*0.45)-c)/70)**2)*k*0.9
        img=tone(G,neg=k*0.92,glare=band.astype(np.float32)); hk=cl(abs(u-0.5)*2.4)
    buf=img*(1-CASEA[...,None])+CASE*CASEA[...,None]
    pil=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    pil.alpha_composite(ov); pil.alpha_composite(o2); return pil.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
