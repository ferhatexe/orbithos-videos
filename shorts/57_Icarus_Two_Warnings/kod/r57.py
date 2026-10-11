import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid57")
for p in ["/home/claude/vid57","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= shadow-puppet theatre =================
SX0,SX1,SY0,SY1=30,510,58,612          # backlit cloth screen
SCREEN=np.array((1.0,0.80,0.52),np.float32)
_g=np.random.default_rng(57)
_w1=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),sigmaX=0.6,sigmaY=5); _w2=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),sigmaX=5,sigmaY=0.6)
_bl=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),25)
CLOTH=(1+0.035*_w1/_w1.std()+0.035*_w2/_w2.std()+0.05*_bl/_bl.std()+0.03*np.sin(xx*math.pi/1.6)*np.sin(yy*math.pi/1.6))
CLOTH*=1-0.10*np.exp(-((xx-188)/1.6)**2)-0.10*np.exp(-((xx-352)/1.6)**2)   # seams
CLOTH=CLOTH.astype(np.float32)
def light(t):
    fl=1+0.025*math.sin(t*13.1)+0.017*math.sin(t*29.3+1)+0.01*math.sin(t*47)
    cx,cy=272+3*math.sin(t*3.1),330+3*math.sin(t*2.3)
    d2=((xx-cx)**2+(yy-cy)**2*0.85)/(2*255**2); edge=np.clip(np.minimum.reduce([xx-SX0,SX1-xx,yy-SY0,SY1-yy])/40,0,1)
    return ((0.22+0.95*np.exp(-d2))*fl*(0.55+0.45*edge)).astype(np.float32)
class Stage:
    def __init__(s): s.L=[]
    def sil(s,m,blur=0.8,a=1.0,holes=True): s.L.append((m,blur,None,a)); return s
    def col(s,m,c,blur=0.8,a=1.0): s.L.append((m,blur,np.array(c,np.float32),a)); return s
    def render(s,t,lit=1.0):
        Tr=np.ones((h,w,3),np.float32)
        for m,bl,c,a in s.L:
            A=m.f() if isinstance(m,M) else m
            if bl>0.3: A=cv2.GaussianBlur(A,(0,0),bl)
            A=A*a
            if c is None: Tr*=(1-0.93*A)[...,None]
            else:
                Tr*=(1-A)[...,None]+A[...,None]*c
                e=np.clip(A-cv2.erode(A,np.ones((5,5),np.uint8)),0,1); Tr*=(1-0.85*e)[...,None]
        return SCREEN*(light(t)*CLOTH*lit)[...,None]*Tr
# ---- proscenium: red valance + side curtains + carved wooden ledge ----
def _frame():
    F=np.zeros((h,w,3),np.float32); A=np.zeros((h,w),np.float32)
    red=np.array((0.46,0.06,0.06),np.float32)
    side=((xx<SX0)|(xx>SX1)).astype(np.float32)
    fold=(0.65+0.35*np.sin(xx*0.55))[...,None]
    F+=side[...,None]*red*fold; A=np.maximum(A,side)
    edge=SY0-10+12*np.abs(np.sin(math.pi*xx/90)); val=(yy<edge).astype(np.float32)
    F=F*(1-val[...,None])+val[...,None]*red*(0.75+0.25*np.sin(xx*0.21))[...,None]*(0.8+0.2*np.clip(yy/40,0,1))[...,None]
    A=np.maximum(A,val)
    fr=((yy>=edge)&(yy<edge+4)).astype(np.float32); F=F*(1-fr[...,None])+fr[...,None]*np.array((0.86,0.64,0.26),np.float32); A=np.maximum(A,fr)
    led=(yy>=SY1).astype(np.float32)
    gr=cv2.GaussianBlur(np.random.default_rng(9).normal(0,1,(h,w)).astype(np.float32),(0,0),sigmaX=30,sigmaY=0.8); gr/=gr.std()
    wood=np.array((0.20,0.11,0.06),np.float32)*(1+0.18*gr)[...,None]
    F=F*(1-led[...,None])+led[...,None]*wood; A=np.maximum(A,led)
    for y0,y1,c in ((SY1,SY1+6,(0.86,0.64,0.26)),(SY1+18,SY1+20,(0.55,0.38,0.16)),(h-26,h-24,(0.55,0.38,0.16))):
        b=((yy>=y0)&(yy<y1)).astype(np.float32); F=F*(1-b[...,None])+b[...,None]*np.array(c,np.float32)
    for x in [x for x in range(52,w-30,48) if not 140<x<400]:
        m=M().circ(x,h-46,7).f()-M().circ(x,h-46,4).f(); F+=np.clip(m,0,1)[...,None]*np.array((0.35,0.24,0.1),np.float32)
    sh=np.clip(1-np.minimum.reduce([np.abs(yy-SY1),np.abs(xx-SX0),np.abs(xx-SX1)])/10,0,1)*(1-A)*0.5
    return F,A,sh
FR,FA,FSH=_frame()
# ================= fonts / HUD =================
FD=P.FD; _IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(FD+n,s)
    return _IF[k]
cGD=(240,200,115); cINK=(58,28,12)
def ttl(d,s,y=1300,fs=82,a=1.0,sc=1.0,col=cGD):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f("Gloock-Regular.ttf",n)
    while f.getlength(s)>960 and n>20: n-=4; f=_f("Gloock-Regular.ttf",n)
    d.text((W/2+4,y+5),s,font=f,fill=(10,4,2,int(200*a)),anchor="mm")
    d.text((W/2,y),s,font=f,fill=col+(int(255*a),),anchor="mm",stroke_width=2,stroke_fill=(40,18,8,int(255*a)))
def lab(d,s,x,y,fs=50,a=1.0,sc=1.0):
    """hand-painted caption on the cloth"""
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f("Gloock-Regular.ttf",n)
    d.text((x,y),s,font=f,fill=cINK+(int(235*a),),anchor="mm")
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= puppets (all profile, facing f=+1 right / -1 left) =================
def rod(st,x,y,dx=30):
    st.sil(M().line((x,y),(x+dx,SY1+40),2.4),blur=2.2,a=0.55)
def person(x,y,s,f=1,beard=False,crown=False,staff=False,arm=0.3,kid=False,bow=0.0,crook=False):
    m=M(); H=(120 if kid else 170)*s
    hx,hy=x+f*(4+bow*14)*s,y-H+14*s+bow*12*s
    m.circ(hx,hy,(12 if kid else 14)*s); m.poly([(hx+f*12*s,hy-2*s),(hx+f*20*s,hy+4*s),(hx+f*11*s,hy+6*s)])
    if beard: m.poly([(hx-f*4*s,hy+6*s),(hx+f*12*s,hy+6*s),(hx+f*2*s,hy+30*s)])
    if crown: m.poly([(hx-12*s,hy-10*s),(hx-12*s,hy-28*s),(hx-6*s,hy-18*s),(hx,hy-30*s),(hx+6*s,hy-18*s),(hx+12*s,hy-28*s),(hx+12*s,hy-10*s)])
    ty=y-H+30*s; m.rect(hx-5*s,hy+8*s,hx+5*s,ty+4*s)
    m.poly([(x-15*s+f*bow*10*s,ty),(x+15*s+f*bow*10*s,ty),(x+25*s,y-H*0.40),(x-25*s,y-H*0.40)])
    hip=y-H*0.42
    m.line((x-7*s,hip),(x-9*s,y),8*s); m.line((x+7*s,hip),(x+9*s,y),8*s)
    m.ell(x-9*s+f*7*s,y,10*s,4*s); m.ell(x+9*s+f*7*s,y,10*s,4*s)
    sx,sy=x+f*(6+bow*10)*s,ty+8*s; ex,ey=sx+f*math.sin(arm)*52*s,sy+math.cos(arm)*52*s; m.line((sx,sy),(ex,ey),7*s)
    if staff: m.line((ex,ey-70*s),(ex,y),5*s); m.circ(ex,ey-74*s,7*s)
    if crook:
        m.line((ex,ey-60*s),(ex,y),4*s); cv2.ellipse(m.m,(int((ex+f*9*s)*16),int((ey-60*s)*16)),(int(9*s*16),int(9*s*16)),0,180,360,255,int(4*s),cv2.LINE_AA,4)
    for k in range(4): m.circ(x-15*s+k*10*s,y-H*0.47,2.2*s,0)     # punched decoration
    m.circ(x+f*bow*6*s,ty+18*s,3*s,0)
    return m,(x,hip)
FEATH=[(30,0.0),(40,0.13),(50,0.26),(60,0.39),(70,0.52),(80,0.65),(90,0.78),(98,0.91),(104,1.04)]
def wing_into(m,px,py,s,f,ang,lost=0,feath=9,grow=1.0):
    """fan of feathers laid short to long, rooted on the arm"""
    for i,(L,da) in enumerate(FEATH[:feath]):
        if i>=9-lost: continue
        a=ang-f*da; L=L*s*(grow if i==feath-1 else 1)
        cx,cy=px+math.cos(a)*L*0.55*f,py+math.sin(a)*L*0.55
        m.ell(cx,cy,L*0.55,5.5*s,math.degrees(math.atan2(math.sin(a),math.cos(a)*f)))
    m.line((px,py),(px+math.cos(ang)*60*s*f,py+math.sin(ang)*60*s),5*s)
def flyer(x,y,s,t,f=1,beard=False,flap=1.0,lost=0,tilt=0.0,ph=0.0):
    m=M(); c,sn=math.cos(tilt),math.sin(tilt)
    def R(dx,dy): return (x+f*(dx*c-dy*sn),y+dx*sn+dy*c)
    hx,hy=R(48*s,-8*s)
    m.ell(*R(0,0),40*s,11*s,math.degrees(tilt)*f); m.circ(hx,hy,11*s); m.poly([R(57*s,-10*s),R(64*s,-5*s),R(56*s,-3*s)])
    if beard: m.poly([R(42*s,0),R(58*s,0),R(46*s,16*s)])
    m.line(R(-30*s,2*s),R(-82*s,8*s),6*s); m.line(R(-30*s,-2*s),R(-80*s,-6*s),6*s)
    fl=math.sin(t*5.5+ph)*0.45*flap
    px,py=R(6*s,-8*s); wing_into(m,px,py,s,f,-math.pi*0.62+tilt*f-fl,lost)
    m.circ(*R(-6*s,0),2.4*s,0); m.circ(*R(4*s,0),2.4*s,0); m.circ(*R(14*s,0),2.4*s,0)
    return m
def sun(st,x,y,r,t,a=1.0):
    m=M().circ(x,y,r)
    for k in range(14):
        an=k*2*math.pi/14+t*0.25; m.poly([(x+math.cos(an-0.12)*r*0.95,y+math.sin(an-0.12)*r*0.95),(x+math.cos(an)*r*1.55,y+math.sin(an)*r*1.55),(x+math.cos(an+0.12)*r*0.95,y+math.sin(an+0.12)*r*0.95)])
    for k in range(10): an=k*2*math.pi/10-t*0.2; m.circ(x+math.cos(an)*r*0.62,y+math.sin(an)*r*0.62,r*0.07,0)
    m.circ(x,y,r*0.22,0)
    st.col(m,(1.0,0.40,0.10),0.7,a); rod(st,x,y+r,20)
def sea(st,t,y0=540,a=1.0,amp=7):
    pts=[(x,y0+amp*math.sin(x/34+t*2.2)+3*math.sin(x/13-t*3)) for x in range(SX0-10,SX1+20,8)]
    st.col(M().poly(pts+[(SX1+20,SY1+10),(SX0-10,SY1+10)]),(0.20,0.62,0.66),0.8,a)
    for k in range(3):
        yy0=y0+18+k*18; pts=[(x,yy0+4*math.sin(x/24+t*1.8+k)) for x in range(SX0,SX1,10)]
        st.sil(M().pline(pts,2.5),0.8,0.5*a)
def hill(pts,y0,amp,seed):
    g=np.random.default_rng(seed); out=[]
    for x,yy_ in pts: out.append((x,yy_))
    return M().poly(out)
def tower(m,x,y,s):
    m.rect(x-38*s,y-190*s,x+38*s,y);
    for k in range(5): m.rect(x-38*s+k*17*s,y-206*s,x-38*s+k*17*s+10*s,y-190*s)
    m.rect(x-12*s,y-150*s,x+12*s,y-120*s,0); m.rect(x-12*s,y-80*s,x+12*s,y-50*s,0)
    m.rect(x-34*s,y-110*s,x+34*s,y-106*s,0)
def boat(m,x,y,s,t):
    yb=y+3*math.sin(t*2.2)
    m.poly([(x-60*s,yb-10*s),(x+60*s,yb-10*s),(x+48*s,yb+12*s),(x-48*s,yb+12*s)]); m.poly([(x+60*s,yb-10*s),(x+72*s,yb-26*s),(x+64*s,yb-8*s)])
    for k in range(5): m.circ(x-40*s+k*20*s,yb,3*s,0)
    return yb
def sheep(m,x,y,s):
    for dx,dy in ((-14,0),(0,-6),(14,0),(-6,6),(8,6)): m.circ(x+dx*s,y-22*s+dy*s,12*s)
    m.ell(x+26*s,y-26*s,9*s,6*s,20); m.line((x-12*s,y-12*s),(x-12*s,y),4*s); m.line((x+12*s,y-12*s),(x+12*s,y),4*s)
def cypress(m,x,y,s): m.ell(x,y-70*s,12*s,70*s); m.rect(x-2*s,y-6*s,x+2*s,y)
def feather(m,x,y,s,ang): m.ell(x,y,30*s,5*s,math.degrees(ang)); m.line((x-math.cos(ang)*34*s,y-math.sin(ang)*34*s),(x+math.cos(ang)*30*s,y+math.sin(ang)*30*s),1.6*s)
def panpipe(m,x,y,s):
    for k in range(7): m.rect(x+k*12*s,y-(90-k*10)*s,x+k*12*s+9*s,y)
    m.rect(x-3*s,y-30*s,x+85*s,y-22*s)
# ================= shots =================
def s_hook(t,lit=1.0):
    st=Stage(); sea(st,t,560); sun(st,380,165,58,t)
    k=(t+0.6)/5.4; x,y=110+170*k,470-200*k
    m=flyer(x,y,1.0,t,1,tilt=-0.35); st.sil(m,0.8); rod(st,x-20,y+10,-10)
    def hd(d,t=t):
        ttl(d,"TWO WARNINGS",1300,90,a=ap(t,EV["two"]-0.1,99),sc=pop(t,EV["two"]-0.2))
    return st.render(t,lit),[hd]
def s_crete(t,lit=1.0):
    st=Stage(); sea(st,t,575,amp=5)
    st.sil(M().poly([(SX0-10,600),(60,520),(150,470),(240,455),(330,430),(420,470),(SX1+10,520),(SX1+10,620),(SX0-10,620)]),0.8)
    tm=M(); tower(tm,360,445,1.0)
    tm.circ(350,232,6); tm.rect(345,238,355,262); tm.circ(370,236,5); tm.rect(366,241,374,262); st.sil(tm,0.8)
    mm,_=person(150,470,1.25,f=1,crown=True,staff=True,arm=0.5); st.sil(mm,1.0); rod(st,150,400,40)
    def hd(d,t=t):
        ttl(d,"DAEDALUS",1300,92,a=ap(t,EV["daed"],EV["crete"]-0.2),sc=pop(t,EV["daed"]-0.1))
        lab(d,"Daedalus & son",720,400,52,a=ap(t,EV["genius"],99))
        ttl(d,"TRAPPED ON CRETE",1300,84,a=ap(t,EV["crete"]-0.2,99),sc=pop(t,EV["crete"]-0.3))
        lab(d,"King Minos",300,390,54,a=ap(t,EV["minos"],99),sc=pop(t,EV["minos"]-0.1))
    return st.render(t,lit),[hd]
def s_work(t,lit=1.0):
    st=Stage()
    st.sil(M().rect(SX0-10,560,SX1+10,SY1+10),0.8)   # workbench
    dm,_=person(100,560,1.05,f=1,beard=True,arm=1.2); st.sil(dm,1.0); rod(st,100,480,30)
    nf=int(cl((t-EV["feathers"]+0.2)/(EV["long"]-EV["feathers"]+0.4))*9)
    wm=M(); px,py=170,470
    if nf>0:
        for i,(L,da) in enumerate(FEATH[:nf]):
            a=-0.10-da*0.62; L=L*2.2; cx,cy=px+math.cos(a)*L*0.55,py+math.sin(a)*L*0.55
            wm.ell(cx,cy,L*0.55,9,math.degrees(a))
            for q in range(5): wm.circ(px+math.cos(a)*L*(0.25+q*0.13),py+math.sin(a)*L*(0.25+q*0.13),1.8,0)
    st.sil(wm,0.7)
    th=cl((t-EV["thread"]+0.2)/0.6)
    if th>0:
        pts=[(px+math.cos(-0.10-da*0.62)*L*2.2*0.5,py+math.sin(-0.10-da*0.62)*L*2.2*0.5) for L,da in FEATH]
        n=max(2,int(len(pts)*th)); st.sil(M().pline(pts[:n],3),0.6)
    wx=sm((t-EV["wax"]+0.2)/0.6)
    if wx>0:
        wmk=M().ell(px+10,py-8,42*wx,26*wx,-20)
        for k in range(3): wmk.ell(px+20+k*14,py+18+8*k*wx,5,9*wx)
        st.col(wmk,(1.0,0.82,0.25),0.8)
    pp=sm((t-EV["pipes"]+0.3)/0.5)
    if pp>0: pm=M(); panpipe(pm,400,210,1.0*pp+0.01); st.sil(pm,0.8); rod(st,440,210,20)
    def hd(d,t=t):
        ttl(d,"HE BUILT WINGS",1300,90,a=ap(t,EV["built"]-0.1,EV["thread"]-0.2),sc=pop(t,EV["built"]-0.2))
        lab(d,"short  to  long",640,1060,54,a=ap(t,EV["short"],EV["thread"]))
        lab(d,"like panpipes",860,470,50,a=ap(t,EV["pipes"],99))
        ttl(d,"THREAD & WAX",1300,92,a=ap(t,EV["thread"],99),sc=pop(t,EV["thread"]-0.1))
    return st.render(t,lit),[hd]
def zones(st,t,ahigh,alow,amid):
    if ahigh>0: st.col(M().rect(SX0,SY0,SX1,215),(1.0,0.55,0.25),2.5,0.55*ahigh)
    if alow>0:
        for k in range(14):
            g=np.random.default_rng(k); x=g.uniform(60,480); ph=(t*0.7+g.uniform(0,1))%1
            st.col(M().circ(x,540-ph*120,4+3*(1-ph)),(0.25,0.65,0.70),0.6,alow*(1-ph))
    if amid>0:
        pts=[(x,330+6*math.sin(x/40)) for x in range(SX0+10,int(SX0+10+(SX1-SX0-20)*amid),6)]
        for i in range(0,len(pts)-2,4): st.sil(M().line(pts[i],pts[i+2],4),0.6,0.8)
def s_warn(t,lit=1.0):
    st=Stage(); sea(st,t,545); sun(st,410,130,46,t)
    ah=fa(t,EV["high"]-0.2,99); al=fa(t,EV["low"]-0.2,99); am=sm((t-EV["middle"]+0.2)/0.8)
    zones(st,t,ah,al,am)
    k=(t-S("warn")["s"])/(S("warn")["e"]-S("warn")["s"]); x=150+120*k
    st.sil(flyer(x,330,0.8,t,1,beard=True),0.8); st.sil(flyer(x-110,345,0.62,t,1,ph=1.3),0.8)
    if ah>0: st.sil(flyer(250,175,0.55,t,1,ph=0.5,lost=int(3*cl((t-EV["melt"])/0.8))),1.2,0.35*ah)
    if al>0: st.sil(flyer(250,505,0.55,t,1,ph=2.1,tilt=0.25),1.2,0.35*al)
    def hd(d,t=t):
        lab(d,"too high",230,330,62,a=ah)
        lab(d,"too low",760,960,62,a=al)
        ttl(d,"NOT TOO HIGH",1300,90,a=ap(t,EV["high"],EV["low"]-0.3),sc=pop(t,EV["high"]-0.1))
        ttl(d,"NOT TOO LOW",1300,90,a=ap(t,EV["low"],EV["middle"]-0.2),sc=pop(t,EV["low"]-0.1))
        ttl(d,"FLY THE MIDDLE PATH",1300,80,a=ap(t,EV["middle"]-0.1,99),sc=pop(t,EV["middle"]-0.2))
    return st.render(t,lit),[hd]
def s_witness(t,lit=1.0):
    st=Stage(); sea(st,t,520)
    st.sil(M().poly([(SX0-10,470),(90,452),(170,470),(215,520),(232,SY1+10),(SX0-10,SY1+10)]),0.8)
    sm_,_=person(110,458,0.75,f=1,crook=True,arm=0.25,bow=-0.3); st.sil(sm_,0.9); sh=M(); sheep(sh,175,476,0.7); st.sil(sh,0.9)
    bm=M(); yb=boat(bm,380,535,1.0,t); fm,_=person(370,yb-8,0.55,f=-1,arm=2.4,bow=-0.4); st.sil(bm,0.8); st.sil(fm,0.8)
    st.sil(M().line((350,yb-58),(300,yb-110),2.5),0.6); st.sil(M().line((300,yb-110),(298,yb+10),1.2),0.6)
    k=(t-S("fall")["s"])/4.0; st.sil(flyer(150+160*k,190,0.55,t,1,beard=True),0.9); st.sil(flyer(80+160*k,210,0.45,t,1,ph=1.0),0.9)
    def hd(d,t=t):
        lab(d,"a fisherman",800,520,52,a=ap(t,EV["fisher"],99))
        lab(d,"a shepherd",240,590,52,a=ap(t,EV["shepherd"],99))
        ttl(d,"“GODS!”",1300,100,a=ap(t,EV["gods"]-0.1,99),sc=pop(t,EV["gods"]-0.2))
    return st.render(t,lit),[hd]
def s_climb(t,lit=1.0):
    st=Stage(); sea(st,t,560); sun(st,400,140,64,t)
    t0=Lx("But Icarus")[0]; tf=EV["fell"]-0.4
    lost=int(9*cl((t-EV["soft"])/(EV["slip"]+0.5-EV["soft"])))
    if t<tf:
        k=sm((t-t0)/(EV["soft"]-t0+0.4)); x,y=150+170*k,470-290*k
        st.sil(flyer(x,y,0.8,t,1,tilt=-0.5*(1-cl((t-EV["soft"])/0.6)),lost=lost,flap=1+cl((t-EV["soft"])/0.5)),0.8); rod(st,x,y,-30)
    else:
        k=ein((t-tf)/0.9); x,y=320+40*k,180+380*k
        if k<1: st.sil(flyer(x,y,0.8,t,1,tilt=0.8+k*1.2,lost=9,flap=1.6),0.8+k)
        if t>tf+0.9:
            u=(t-tf-0.9)
            for i in range(9):
                an=-math.pi/2+(i-4)*0.22; r=110*u*(1.2-u*0.5); st.col(M().circ(360+math.cos(an)*r,560+math.sin(an)*r*1.4+160*u*u,7),(0.25,0.65,0.70),0.6,cl(1-u/1.4))
    if t>EV["soft"]:
        for i in range(lost):
            g=np.random.default_rng(i); u=t-EV["soft"]-i*0.12
            if u<0: continue
            fm=M(); feather(fm,330+g.uniform(-40,40)+30*math.sin(u*2+i),200+u*70+g.uniform(0,30),0.7,u*1.5+i); st.sil(fm,1.0)
    def hd(d,t=t):
        ttl(d,"HIGHER AND HIGHER",1300,84,a=ap(t,EV["climb"],EV["soft"]-0.1),sc=pop(t,EV["climb"]-0.1))
        ttl(d,"THE WAX MELTED",1300,90,a=ap(t,EV["soft"]-0.1,EV["icarian"]-0.3),sc=pop(t,EV["soft"]-0.2))
        ttl(d,"THE ICARIAN SEA",1300,88,a=ap(t,EV["icarian"]-0.2,99),sc=pop(t,EV["icarian"]-0.3))
    return st.render(t,lit),[hd]
def s_island(t,lit=1.0):
    st=Stage(); sea(st,t,520)
    im=M().poly([(80,560),(140,470),(230,430),(330,440),(420,480),(470,560)]);
    for x,s in ((160,1.0),(190,0.8),(400,0.9)): cypress(im,x,470 if x<300 else 480,s)
    im.ell(330,436,40,16); im.rect(318,392,342,436); im.poly([(314,394),(330,378),(346,394)]); im.circ(330,410,3,0)
    st.sil(im,0.8)
    dm,_=person(255,452,0.75,f=1,beard=True,arm=0.1,bow=0.8); st.sil(dm,0.9); rod(st,250,380,30)
    def hd(d,t=t):
        ttl(d,"ICARIA",1300,100,a=ap(t,EV["island"],99),sc=pop(t,EV["island"]-0.1))
        lab(d,"his grave",690,700,48,a=ap(t,EV["buried"],99))
    return st.render(t,lit),[hd]
def s_moral(t,lit=1.0):
    st=Stage(); sea(st,t,545); sun(st,410,130,46,t)
    ah=fa(t,EV["warning"]-0.2,99); al=fa(t,EV["toolow"]-0.3,99)
    zones(st,t,ah,al,0.0)
    st.sil(flyer(250,175,0.6,t,1,ph=0.5,lost=3),1.0,0.9*ah); st.sil(flyer(250,505,0.6,t,1,ph=2.1,tilt=0.25),1.0,0.9*al)
    st.sil(flyer(270,335,0.75,t,1,beard=True),0.8)
    def hd(d,t=t):
        lab(d,"too high",230,330,62,a=ah)
        lab(d,"too low",760,960,62,a=al)
        ttl(d,"“DON'T FLY TOO HIGH”",1300,80,a=ap(t,EV["warning"],EV["ovid"]-0.2),sc=pop(t,EV["warning"]-0.1))
        ttl(d,"TOO LOW: JUST AS DEADLY",1300,76,a=ap(t,EV["ovid"],99),sc=pop(t,EV["ovid"]-0.1))
    return st.render(t,lit),[hd]
TR=0.36; TOTAL=B.TOTAL; LOOPD=0.62
SHOTS=[(0.0,s_hook),(S("crete")["s"],s_crete),(Lx("So he built")[0]-0.35,s_work),(S("warn")["s"],s_warn),(S("fall")["s"],s_witness),
       (Lx("But Icarus")[0]-0.3,s_climb),(Lx("His father")[0]-0.3,s_island),(S("moral")["s"],s_moral)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
def lampf(u,seed):
    """lamp gutters out then flares back"""
    g=np.random.default_rng(seed); fl=1+0.25*math.sin(u*90+seed)*(1-abs(u-0.5)*2)
    k=abs(u-0.5)*2; return max(0.05,(k**1.6)*fl)
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None:
        buf,hud=SHOTS[i][1](t); hk=1.0
    else:
        fa_,fb_,ta,tb,u=pair; lf=lampf(u,i)
        if u<0.5: buf,hud=fa_(ta,lf)
        else: buf,hud=fb_(tb,lf)
        hk=cl(abs(u-0.5)*2.4)
    buf=buf*(1-FA[...,None])*(1-FSH[...,None])+FR*FA[...,None]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
