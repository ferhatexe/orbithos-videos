import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid69")
for p in ["/home/claude/vid69","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= engraved Etruscan bronze mirror on museum velvet =================
CX,CY,RD=270,320,236
_g=np.random.default_rng(69)
def _nz(s): n=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),s); return n/n.std()
_a,_b,_c,_d=_nz(0.8),_nz(3),_nz(12),_nz(40)
R2=np.sqrt((xx-CX)**2+(yy-CY)**2)
DISC=np.clip((RD-R2)/1.5,0,1).astype(np.float32)
def _bronze():
    base=np.array((0.70,0.52,0.28),np.float32)
    sheen=np.clip(1.0+0.35*np.exp(-(((xx-CX+80)**2+(yy-CY+90)**2)/(2*120**2)))-0.25*(R2/RD)**2,0.5,1.5)
    img=base*(sheen*(1+0.04*_a+0.05*_b))[...,None]
    pat=np.clip((_c*0.7+_d*0.6-0.9)*1.5,0,1)*np.clip(0.4+R2/RD,0,1.2)
    img=img*(1-pat[...,None]*0.75)+np.array((0.30,0.52,0.42),np.float32)*pat[...,None]*0.75*(0.9+0.1*_a[...,None])
    pits=(_g.random((h,w))<0.004).astype(np.float32); img*=(1-cv2.GaussianBlur(pits,(0,0),0.8)*1.5)[...,None]
    return img.astype(np.float32)
BRONZE=_bronze()
def _velvet():
    b=np.empty((h,w,3),np.float32); b[:]=(0.04,0.07,0.08); b*=(1+0.08*_c+0.05*_a)[...,None]
    b+=np.exp(-(((xx-CX)**2+(yy-CY)**2)/(2*300**2)))[...,None]*np.array((0.10,0.12,0.12),np.float32)
    return b
VELVET=_velvet()
def engrave(buf,m,a=1.0,col=None,fillcol=None,fa_=0.0):
    """an incised line: dark groove, a lit lower lip, optional inlay/fill"""
    A=(m.f() if isinstance(m,M) else m)*a
    if A.max()<0.01: return
    if fillcol is not None:
        buf+=(np.array(fillcol,np.float32)-buf)*(A*fa_)[...,None]; return
    sh=np.roll(np.roll(A,1,0),1,1)
    buf+=(np.array((1.0,0.88,0.6),np.float32)-buf)*(np.clip(sh-A,0,1)*0.55)[...,None]
    c=np.array(col if col else (0.16,0.10,0.05),np.float32); buf+=(c-buf)*(A*0.92)[...,None]
def line(pts,th=2.0): return M().pline(pts,th)
def mirror():
    b=VELVET.copy()
    hm=M().poly([(CX-26,CY+RD-10),(CX+26,CY+RD-10),(CX+14,CY+RD+120),(CX-14,CY+RD+120)])
    fill_=hm.f(); b=b*(1-fill_[...,None])+BRONZE*fill_[...,None]*0.85
    b=b*(1-DISC[...,None])+BRONZE*DISC[...,None]
    rim=np.clip(DISC-np.clip((RD-6-R2)/1.5,0,1),0,1); b+=rim[...,None]*np.array((0.25,0.20,0.10),np.float32)
    # engraved ivy border
    ring=M(); ring.pline([(CX+math.cos(a)*(RD-22),CY+math.sin(a)*(RD-22)) for a in np.linspace(0,2*math.pi,120)],2)
    for k in range(36):
        a=k*2*math.pi/36; x,y=CX+math.cos(a)*(RD-12),CY+math.sin(a)*(RD-12)
        ring.ell(x,y,6,3,math.degrees(a)+90)
    engrave(b,ring)
    return b
MIRROR=mirror()
# ---- engraved figures ----
def medusa(m,cx,cy,s,t=0.0,tongue=True):
    pts=[(cx+math.cos(a)*40*s,cy+math.sin(a)*44*s) for a in np.linspace(0,2*math.pi,40)]; m.pline(pts,2)
    for sx in (-1,1): m.pline([(cx+sx*16*s+math.cos(a)*8*s,cy-8*s+math.sin(a)*8*s) for a in np.linspace(0,2*math.pi,16)],2); m.circ(cx+sx*16*s,cy-8*s,2.5*s)
    m.pline([(cx,cy-4*s),(cx-4*s,cy+10*s),(cx+4*s,cy+10*s)],1.6)
    m.pline([(cx-20*s,cy+18*s),(cx-8*s,cy+22*s),(cx+8*s,cy+22*s),(cx+20*s,cy+18*s)],2)
    for sx in (-1,1): m.pline([(cx+sx*12*s,cy+21*s),(cx+sx*10*s,cy+30*s),(cx+sx*7*s,cy+21*s)],1.4)
    if tongue: m.pline([(cx-4*s,cy+22*s),(cx,cy+36*s),(cx+4*s,cy+22*s)],1.6)
    for k in range(11):
        a=-math.pi+k*math.pi/10; r0=44*s
        pts=[(cx+math.cos(a)*(r0+q*30*s)+math.sin(q*9+t*3+k)*4*s*q,cy+math.sin(a)*(r0+q*30*s)) for q in np.linspace(0,1,10)]
        m.pline(pts,1.8); m.circ(pts[-1][0],pts[-1][1],3*s)
def horse(m,x,y,s,f=1,wing=0.0,t=0.0):
    X=lambda dx:x+f*dx*s
    m.pline([(X(-60),y-10*s),(X(-30),y-26*s),(X(30),y-26*s),(X(56),y-46*s),(X(70),y-74*s),(X(92),y-70*s),(X(96),y-58*s),(X(76),y-48*s),(X(62),y-14*s),(X(40),y+4*s),(X(-40),y+4*s),(X(-60),y-10*s)],2)
    for dx,ph in ((-46,0),(-32,1),(34,2),(48,3)):
        sw=math.sin(t*5+ph)*8*s; m.pline([(X(dx),y+2*s),(X(dx)+sw,y+30*s),(X(dx)+sw*1.2,y+52*s)],2)
    m.pline([(X(-60),y-8*s),(X(-84),y+10*s),(X(-90),y+30*s)],2)
    m.pline([(X(80),y-72*s),(X(84),y-84*s)],1.6); m.circ(X(84),y-64*s,2*s)
    if wing>0:
        for k in range(6):
            a=-1.9-k*0.18+0.25*math.sin(t*4); L=(60+k*10)*s*wing
            m.pline([(X(0),y-24*s),(X(0)+f*math.cos(a)*L*0.6,y-24*s+math.sin(a)*L*0.6),(X(0)+f*math.cos(a+0.15)*L,y-24*s+math.sin(a+0.15)*L)],1.8)
def person(m,x,y,s,f=1,helm=False,winged_cap=False,arm=0.0,dress=False):
    X=lambda dx:x+f*dx*s
    m.pline([(X(0)+math.cos(a)*14*s,y-150*s+math.sin(a)*16*s) for a in np.linspace(0,2*math.pi,24)],2)
    m.pline([(X(14),y-152*s),(X(20),y-148*s),(X(13),y-144*s)],1.6)
    if helm: m.pline([(X(-16),y-158*s),(X(-6),y-176*s),(X(14),y-170*s),(X(16),y-158*s)],2); m.pline([(X(-6),y-176*s),(X(-30),y-186*s),(X(-40),y-170*s)],2)
    if winged_cap:
        m.pline([(X(-14),y-160*s),(X(0),y-170*s),(X(14),y-160*s)],2)
        for k in range(3): m.pline([(X(-12),y-162*s),(X(-30-k*8),y-180*s+k*6*s)],1.6)
    m.pline([(X(-16),y-132*s),(X(16),y-132*s),(X(26 if dress else 22),y-(4 if dress else 60)*s),(X(-26 if dress else -22),y-(4 if dress else 60)*s),(X(-16),y-132*s)],2)
    if not dress:
        m.pline([(X(-10),y-60*s),(X(-14),y)],2); m.pline([(X(10),y-60*s),(X(16),y)],2)
    for k in range(4): m.pline([(X(-12+k*7),y-120*s),(X(-16+k*9),y-(10 if dress else 66)*s)],1.0)
    ex,ey=X(14)+f*math.cos(arm)*60*s,y-120*s-math.sin(arm)*60*s; m.pline([(X(14),y-124*s),(ex,ey)],2)
    return ex,ey
def harpe(m,x,y,s):
    m.pline([(x,y),(x,y-60*s)],2.5); m.pline([(x+18*s*math.cos(a),y-60*s-18*s*math.sin(a)) for a in np.linspace(math.pi,0,14)],2.5)
def round_shield(m,x,y,r,gorg=True,t=0.0):
    m.pline([(x+math.cos(a)*r,y+math.sin(a)*r) for a in np.linspace(0,2*math.pi,50)],2.4)
    m.pline([(x+math.cos(a)*(r-8),y+math.sin(a)*(r-8)) for a in np.linspace(0,2*math.pi,50)],1.4)
    if gorg: medusa(m,x,y,r/95,t)
def bolt(m,x,y,s): m.pline([(x,y),(x-14*s,y+30*s),(x+6*s,y+30*s),(x-10*s,y+64*s)],2.4)
_IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(P.FD+n,s)
    return _IF[k]
def ttl(d,s,y=1250,fs=80,a=1.0,sc=1.0,col=(236,206,150)):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f("Lora-BoldItalic.ttf",n)
    while f.getlength(s)>980 and n>20: n-=4; f=_f("Lora-BoldItalic.ttf",n)
    d.text((W/2,y),s,font=f,fill=col+(int(255*a),),anchor="mm",stroke_width=3,stroke_fill=(10,16,18,int(220*a)))
def tag(d,s,x,y,fs=40,a=1.0):
    if a<=0.01: return
    d.text((x,y),s,font=_f("Lora-Bold.ttf",fs),fill=(255,236,190,int(255*a)),anchor="mm",stroke_width=4,stroke_fill=(30,20,8,int(230*a)))
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.3,0.28,0.25)
def wk(t,e,d=0.8): return cl((t-e)/d)
def draw(b,m,k=1.0,col=None):
    """engraving appears as if being cut: reveal from the top down"""
    A=m.f()
    if k<1: A=A*np.clip(((CY-RD)+(2*RD)*k-yy)/12,0,1)
    engrave(b,A,1.0,col)
# ================= shots =================
def s_hook(t,end=False):
    b=MIRROR.copy(); m=M(); medusa(m,CX,CY+130,0.9,t); draw(b,m)
    k=sm((t+0.3)/1.4) if not end else 1.0
    m2=M(); horse(m2,CX-20,CY-10-40*k,1.15,1,wing=k,t=t); draw(b,m2,k)
    glow=fa(t,EV["neck0"]-0.3,99,0.3,0.3) if not end else 0.0
    if glow>0: b+=(np.exp(-((xx-CX)**2+(yy-CY-80)**2)/(2*40**2))*0.35*glow)[...,None]*np.array((1,0.9,0.6),np.float32)
    def hd(d,t=t):
        if not end:
            ttl(d,"PEGASUS",1250,96,ap(t,EV["peg0"]-0.2,EV["neck0"]-0.2),pop(t,EV["peg0"]-0.3))
            ttl(d,"born from Medusa's neck",1250,74,ap(t,EV["born"]-0.2,99),pop(t,EV["born"]-0.3))
        else: ttl(d,"remember",1250,90,ap(t,EV["remember"]-0.2,99),pop(t,EV["remember"]-0.3))
    return b,[hd]
def s_sisters(t):
    b=MIRROR.copy()
    for i,(x,y) in enumerate(((CX-140,CY),(CX,CY-30),(CX+140,CY))):
        k=wk(t,EV["three"]-0.6+i*0.15,0.6); m=M(); medusa(m,x,y,0.75,t+i); draw(b,m,k)
    hl=fa(t,EV["onlydie"]-0.2,EV["sisters"],0.2,0.3)
    if hl>0: b+=(np.exp(-((xx-CX)**2+(yy-CY+30)**2)/(2*60**2))*0.3*hl)[...,None]*np.array((1,0.4,0.3),np.float32)
    def hd(d,t=t):
        ttl(d,"THREE GORGONS",1250,84,ap(t,EV["hesiod"]-0.2,EV["onlydie"]-0.1),pop(t,EV["hesiod"]-0.3))
        tag(d,"MORTAL",CX*2,(CY+60)*2,44,ap(t,EV["onlydie"]-0.2,99))
        tag(d,"STHENO",(CX-140)*2,(CY+80)*2,38,ap(t,EV["stheno"]-0.2,99)); tag(d,"EURYALE",(CX+140)*2,(CY+80)*2,38,ap(t,EV["eury"]-0.2,99))
        ttl(d,"only Medusa could die",1250,72,ap(t,EV["onlydie"]-0.1,EV["immortal"]-0.1),pop(t,EV["onlydie"]-0.2))
        ttl(d,"her sisters: immortal",1250,72,ap(t,EV["immortal"]-0.1,99),pop(t,EV["immortal"]-0.2))
    return b,[hd]
def s_perseus(t):
    b=MIRROR.copy(); m=M()
    ex,ey=person(m,CX-80,CY+170,1.1,1,winged_cap=True,arm=1.1)
    harpe(m,ex,ey+20,1.0) if t>EV["blade"]-0.3 else None
    round_shield(m,CX+90,CY-20,70,gorg=t>EV["reflect"]-0.4,t=t)
    m.pline([(CX-74,CY+10),(CX+40,CY-20)],1.2)
    draw(b,m,wk(t,Lx("Perseus cut")[0]-0.3,0.9))
    if t>EV["athena1"]-0.3:
        m3=M(); m3.pline([(CX+200,CY-160),(CX+120,CY-110),(CX+40,CY-60)],2); m3.pline([(CX+36,CY-64),(CX+44,CY-50)],2); draw(b,m3,wk(t,EV["athena1"]-0.3,0.6))
    def hd(d,t=t):
        ttl(d,"PERSEUS",1250,92,ap(t,EV["perseus"]-0.2,EV["reflect"]-0.1),pop(t,EV["perseus"]-0.3))
        ttl(d,"only in a reflection",1250,74,ap(t,EV["reflect"]-0.1,EV["hermes"]),pop(t,EV["reflect"]-0.2))
        ttl(d,"Hermes' blade · Athena's guidance",1250,58,ap(t,EV["blade"]-0.2,99),pop(t,EV["blade"]-0.3))
    return b,[hd]
def s_birth(t):
    b=MIRROR.copy(); m=M(); medusa(m,CX-40,CY+150,0.7,t); draw(b,m)
    k=sm((t-EV["sprang"]+0.2)/1.2); m2=M(); horse(m2,CX+20,CY-20-50*k,0.9,1,wing=k,t=t); draw(b,m2,k)
    kc=sm((t-EV["chrysaor"]+0.3)/0.6)
    if kc>0: m3=M(); person(m3,CX-150,CY+60,0.75,1,helm=True,arm=1.3); draw(b,m3,kc)
    gl=fa(t,EV["sprang"]-0.2,99,0.3,0.3); b+=(np.exp(-((xx-CX+20)**2+(yy-CY-100)**2)/(2*60**2))*0.3*gl)[...,None]*np.array((1,0.9,0.6),np.float32)
    def hd(d,t=t):
        ttl(d,"sons of Poseidon",1250,78,ap(t,EV["poseidon"]-0.4,EV["pegasus"]-0.1),pop(t,EV["poseidon"]-0.5))
        tag(d,"PEGASUS",(CX+40)*2,(CY-150)*2,44,ap(t,EV["pegasus"]-0.2,99))
        tag(d,"CHRYSAOR",(CX-150)*2,(CY+100)*2,40,ap(t,EV["chrysaor"]-0.2,99))
    return b,[hd]
def s_thunder(t):
    b=MIRROR.copy(); m=M(); horse(m,CX,CY+40,1.25,1,wing=1.0,t=t); draw(b,m)
    k=wk(t,EV["thunder"]-0.3,0.5)
    if k>0:
        m2=M(); bolt(m2,CX-30,CY-170,1.4); bolt(m2,CX+60,CY-180,1.2); draw(b,m2,1.0,(0.45,0.12,0.05))
    def hd(d,t=t):
        ttl(d,"Zeus's thunderbolt carrier",1250,68,ap(t,EV["thunder"]-0.3,99),pop(t,EV["thunder"]-0.4))
    return b,[hd]
def s_gaze(t):
    b=MIRROR.copy(); m=M(); ex,ey=person(m,CX-110,CY+170,1.0,1,winged_cap=True,arm=1.4); medusa(m,ex+10,ey-30,0.55,t); draw(b,m)
    k=wk(t,EV["gaze"]-0.2,1.0)
    if k>0:
        m2=M(); person(m2,CX+120,CY+170,1.0,-1,arm=-0.4); A=m2.f()
        engrave(b,A); b+=(A*k*0.5)[...,None]*np.array((0.25,0.25,0.25),np.float32)
        for q in range(4): m3=M(); m3.pline([(ex+30,ey-30+q*8),(ex+30+150*k,ey-30+q*30)],1.2); draw(b,m3)
    def hd(d,t=t):
        ttl(d,"her gaze still worked",1250,74,ap(t,EV["dead"]-0.3,99),pop(t,EV["dead"]-0.4))
        tag(d,"STONE",(CX+120)*2,(CY+20)*2,44,ap(t,EV["weapon"]-0.6,99))
    return b,[hd]
def s_coral(t):
    b=MIRROR.copy(); m=M(); medusa(m,CX,CY+40,0.8,t);
    k=sm((t-EV["coral"]+0.6)/1.0)
    for i in range(7):
        x0=CX-180+i*60; pts=[(x0+10*math.sin(q*6+i),CY+200-q*120) for q in np.linspace(0,1,12)]; M_=M(); M_.pline(pts,2)
        if k<0.5: engrave(b,M_.f(),1.0,(0.20,0.35,0.18))
        else:
            M2=M(); M2.pline(pts,3)
            for j in range(3): yb=CY+200-(j+1)*30; M2.pline([(x0,yb),(x0+(-1)**j*22,yb-26)],2.2)
            engrave(b,M2.f(),1.0,(0.70,0.15,0.12))
    draw(b,m)
    def hd(d,t=t):
        ttl(d,"OVID",1250,92,ap(t,EV["ovid1"]-0.2,EV["seaweed"]),pop(t,EV["ovid1"]-0.3))
        ttl(d,"seaweed",1250,84,ap(t,EV["seaweed"]-0.1,EV["coral"]-0.3),pop(t,EV["seaweed"]-0.2),(170,220,150))
        ttl(d,"turned to coral",1250,84,ap(t,EV["coral"]-0.3,99),pop(t,EV["coral"]-0.4),(250,140,120))
    return b,[hd]
def s_aegis(t):
    b=MIRROR.copy(); m=M(); person(m,CX-90,CY+190,1.15,1,helm=True,arm=0.4,dress=True); round_shield(m,CX+60,CY+40,95,True,t)
    m.pline([(CX-66,CY+60),(CX-66,CY-160)],2.4)
    draw(b,m,wk(t,S("shield")["s"],0.8))
    def hd(d,t=t):
        ttl(d,"ATHENA'S SHIELD",1250,86,ap(t,EV["athena2"]-0.3,99),pop(t,EV["athena2"]-0.4))
    return b,[hd]
def s_gorgoneion(t):
    b=MIRROR.copy(); m=M()
    m.pline([(CX-180,CY+160),(CX-180,CY-40),(CX,CY-150),(CX+180,CY-40),(CX+180,CY+160)],2.4)
    for k in range(4): m.pline([(CX-150+k*100,CY-30),(CX-150+k*100,CY+160)],2)
    medusa(m,CX,CY-50,0.55,t); round_shield(m,CX-110,CY+90,46,True,t); round_shield(m,CX+110,CY+90,46,True,t)
    draw(b,m,wk(t,Lx("Greeks painted")[0]-0.2,0.8))
    def hd(d,t=t):
        ttl(d,"to scare evil away",1250,80,ap(t,EV["evil"]-0.4,99),pop(t,EV["evil"]-0.5))
        ttl(d,"on shields & buildings",1250,70,ap(t,EV["greeks"]-0.1,EV["evil"]-0.3),pop(t,EV["greeks"]-0.2))
    return b,[hd]
def s_ovid2(t):
    b=MIRROR.copy(); m=M()
    m.pline([(CX+math.cos(a)*44,CY-40+math.sin(a)*54) for a in np.linspace(0,2*math.pi,40)],2)
    m.pline([(CX+44,CY-40),(CX+56,CY-30),(CX+42,CY-22)],1.6); m.circ(CX+18,CY-52,3)
    k=sm((t-EV["cursed"]+0.3)/0.8)
    for i in range(9):
        a=-2.6+i*0.28; pts=[(CX-10+math.cos(a)*(40+q*130),CY-40+math.sin(a)*(40+q*80)+q*140+math.sin(q*8+i+t*2)*12*k) for q in np.linspace(0,1,14)]
        m.pline(pts,2)
        if k>0.5: m.circ(pts[-1][0],pts[-1][1],5)
    m.pline([(CX-30,CY+14),(CX-60,CY+140),(CX+60,CY+140),(CX+30,CY+14)],2)
    draw(b,m,wk(t,Lx("Ovid also")[0]-0.2,0.8))
    def hd(d,t=t):
        ttl(d,"Ovid's version",1250,84,ap(t,EV["ovid2"]-0.2,EV["cursed"]-0.1),pop(t,EV["ovid2"]-0.3))
        ttl(d,"a beauty, cursed by Athena",1250,70,ap(t,EV["cursed"]-0.1,99),pop(t,EV["cursed"]-0.2))
    return b,[hd]
def s_end(t): return s_hook(t,end=True)
TR=0.38; TOTAL=B.TOTAL; LOOPD=0.66
SHOTS=[(0.0,s_hook),(S("gorgon")["s"],s_sisters),(Lx("Perseus cut")[0]-0.3,s_perseus),(S("birth")["s"],s_birth),(Lx("Pegasus later")[0]-0.3,s_thunder),
       (S("after")["s"],s_gaze),(Lx("In Ovid, he set")[0]-0.3,s_coral),(S("shield")["s"],s_aegis),(Lx("Greeks painted")[0]-0.3,s_gorgoneion),(Lx("Ovid also")[0]-0.3,s_ovid2),(Lx("So the next")[0]-0.3,s_end)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
_ANG=np.arctan2(yy-CY,xx-CX)
def ripple(b1,b2,u):
    """the bronze surface turns liquid: concentric ripples blur the old engraving into the new one"""
    k=math.sin(math.pi*u)
    disp=(np.sin(R2/9-u*14)*7*k).astype(np.float32)
    mx=(xx+np.cos(_ANG)*disp).astype(np.float32); my=(yy+np.sin(_ANG)*disp).astype(np.float32)
    w1=cv2.remap(b1,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT); w2=cv2.remap(b2,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    mix=sm((u-0.3)/0.4); out=w1*(1-mix)+w2*mix
    out+=(np.clip(np.sin(R2/9-u*14),0,1)**8*0.25*k*DISC)[...,None]*np.array((1,0.9,0.7),np.float32)
    return out
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None: buf,hud=SHOTS[i][1](t); hk=1.0
    else:
        fa_,fb_,ta,tb,u=pair; b1,h1=fa_(ta); b2,h2=fb_(tb)
        buf=ripple(b1,b2,u); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
