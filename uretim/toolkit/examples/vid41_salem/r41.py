import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid41")
for p in ["/home/claude/vid41","/home/claude/vid3","/home/claude/ep1"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
from paper import *
from PIL import Image, ImageDraw
EV=ev.EV; Lx=ev.Lx; SS=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
LOGO=E1.LOGO
PARCH=(0.94,0.89,0.76); INK=(0.08,0.06,0.05); RED=(0.62,0.10,0.08); PURP=(0.32,0.12,0.36); CANDLE=(1.0,0.78,0.40)
cI=(24,18,14); cP=(236,224,196); cR=(160,30,24); cPu=(96,40,110)
def plaque(d,s,x,y,fs,a=1.0,fg=cI,bg=cP,sc=1.0,ang=0,fn="CrimsonPro-Bold",pad=(28,10)): card(d,s,x,y,fs=fs,a=a,fg=fg,bg=bg,fn=fn,torn=True,ang=ang,sc=sc,pad=pad)
def seal(d,s,x,y,fs,a=1.0,sc=1.0,ang=-6): card(d,s,x,y,fs=fs,a=a,fg=(250,236,220),bg=cR,fn="BigShoulders-Bold",torn=False,ang=ang,sc=sc,pad=(26,6))
def pop(t,e): return spring((t-e)/0.5)
# ---- woodcut helpers ----
HAT=((((xx+yy)%7)<2.2).astype(np.float32))
HAT2=((((xx-yy)%7)<2.2).astype(np.float32))
HATH=(((yy%6)<1.8).astype(np.float32))
def wc(buf,m,tone=0.5,a=1.0,outline=2.0,col=INK):
    """woodcut fill: tone 0=white,1=solid; hatched in between, plus outline"""
    f=m.f() if isinstance(m,M) else m
    if tone>=0.95: pat=np.ones_like(f)
    elif tone>0.6: pat=np.clip(HAT+HAT2,0,1)
    elif tone>0.25: pat=HAT
    elif tone>0.05: pat=HATH*0.8
    else: pat=np.zeros_like(f)
    fill=f*pat
    if outline>0:
        er=cv2.erode((f>0.5).astype(np.uint8),np.ones((int(outline*2)+1,int(outline*2)+1),np.uint8)).astype(np.float32)
        edge=np.clip(f-er,0,1); fill=np.maximum(fill,edge)
    if tone<0.95 and tone>0: buf+=(np.array(PARCH,np.float32)*1.02-buf)*(f*0.7*a)[...,None]
    buf+=(np.array(col,np.float32)-buf)*(fill*a)[...,None]
def parchment(buf,dark=0.0):
    grad(buf,[(0,lerpc(PARCH,(0.55,0.48,0.38),dark)),(h,lerpc((0.86,0.78,0.62),(0.45,0.38,0.30),dark))])
    g=np.random.default_rng(4)
    for k in range(7): rgrad(buf,g.uniform(0,w),g.uniform(0,h),g.uniform(60,160),(-0.08,-0.09,-0.10),0.6)
    edge=np.clip(np.minimum(np.minimum(xx,w-xx),np.minimum(yy,h-yy))/60,0,1)
    buf*=(0.72+0.28*edge)[...,None]
def frame(buf):
    m=M().rect(20,60,w-20,66).rect(20,654,w-20,660).rect(20,60,26,660).rect(w-26,60,w-20,660)
    wc(buf,m,1.0,outline=0)
def puritan(buf,x,y,s,tone=0.95,face=1,woman=False,a=1.0,arm=0.0,twist=0.0):
    def P(px,py): return (x+px*s*face,y+py*s)
    if woman:
        dr=M().poly([P(-34,0),P(34,0),P(18,-80),P(14,-100),P(-14,-100),P(-18,-80)]); wc(buf,dr,tone,a=a)
        ap=M().poly([P(-14,-10),P(14,-10),P(10,-78),P(-10,-78)]); wc(buf,ap,0.0,a=a,outline=1.4)
        cp=M().poly([P(-22,-70),P(22,-70),P(16,-104),P(-16,-104)]); wc(buf,cp,min(1,tone+0.3),a=a)
        hd=M().circ(*P(2,-116),13*s); wc(buf,hd,0.0,a=a,outline=1.5)
        bon=M().poly([P(-16,-104),P(16,-120),P(10,-134),P(-8,-132),P(-18,-118)]); wc(buf,bon,0.0,a=a,outline=1.6)
    else:
        lg=M().rect(*P(-12,-50),*P(-4,0)).rect(*P(4,-50),*P(12,0)); wc(buf,lg,1.0,a=a,outline=0)
        sh=M().rect(*P(-16,-6),*P(-2,0)).rect(*P(2,-6),*P(18,0)); wc(buf,sh,1.0,a=a,outline=0)
        cl=M().poly([P(-30,-40),P(30,-40),P(20,-100),P(-20,-100)]); wc(buf,cl,tone,a=a)
        col=M().poly([P(-16,-100),P(16,-100),P(10,-88),P(-10,-88)]); wc(buf,col,0.0,a=a,outline=1.2)
        hd=M().circ(*P(2,-114),13*s); wc(buf,hd,0.0,a=a,outline=1.5)
        hat=M().rect(*P(-12,-156),*P(14,-124)).rect(*P(-26,-127),*P(28,-121)); wc(buf,hat,1.0,a=a,outline=0)
        bk=M().rect(*P(-3,-133),*P(5,-127)); comp(buf,bk,(0.85,0.7,0.3),sh=0,rim=0,a=a)
    if arm:
        ar=M().line(P(14,-92),P(44,-124-30*arm),6*s); wc(buf,ar,1.0,a=a,outline=0)
def pines(buf,y,n,seed,tone=0.95,h0=90,a=1.0):
    g=np.random.default_rng(seed); m=M()
    for k in range(n):
        x=g.uniform(-20,w+20); hh=g.uniform(0.6,1.2)*h0
        for j in range(3): m.poly([(x-hh*0.35*(1-j*0.2),y-j*hh*0.28),(x,y-hh*(0.45+j*0.28)),(x+hh*0.35*(1-j*0.2),y-j*hh*0.28)])
        m.rect(x-3,y,x+3,y+12)
    wc(buf,m,tone,a=a,outline=1.0)
def house(buf,x,y,s,a=1.0,lit=0.0):
    m=M().rect(x-50*s,y-60*s,x+50*s,y).poly([(x-58*s,y-60*s),(x-10*s,y-110*s),(x+58*s,y-60*s)]); wc(buf,m,0.3,a=a)
    wc(buf,M().rect(x+20*s,y-120*s,x+34*s,y-80*s),1.0,a=a,outline=0)
    win=M().rect(x-30*s,y-42*s,x-12*s,y-24*s).rect(x+12*s,y-42*s,x+30*s,y-24*s)
    if lit>0: comp(buf,win,CANDLE,sh=0,rim=0,a=a*lit); rgrad(buf,x,y-33*s,40*s,(0.6,0.4,0.1),0.25*lit*a)
    else: wc(buf,win,1.0,a=a,outline=0)
def nightsky(buf,y1,t,a=1.0):
    m=M().rect(26,66,w-26,y1); wc(buf,m,0.7,a=a,outline=0)
    mo=M().circ(420,140,34); comp(buf,mo,(0.97,0.93,0.82),sh=0,rim=0,a=a)
    cut=M().circ(434,132,30); wc(buf,cut,0.7,a=a,outline=0)
    rays=M()
    for k in range(10):
        ang=k*0.63; rays.line((420+44*math.cos(ang),140+44*math.sin(ang)),(420+62*math.cos(ang),140+62*math.sin(ang)),2)
    comp(buf,rays,(0.97,0.93,0.82),sh=0,rim=0,a=a)
def girl(buf,x,y,s,t,fit=0.0,a=1.0,face=1):
    tw=fit*0.5*math.sin(t*9+x)
    def P(px,py): return rot([(px*s*face,py*s)],tw*(-py/120),x,y)[0]
    dr=M().poly([P(-28,0),P(28,0),P(12,-66),P(-12,-66)]); wc(buf,dr,0.5,a=a)
    ap=M().poly([P(-10,-6),P(10,-6),P(7,-60),P(-7,-60)]); wc(buf,ap,0.0,a=a,outline=1.2)
    a1=fit*math.sin(t*11+x)*1.2; m=M()
    m.line(P(8,-60),(P(8,-60)[0]+30*s*math.cos(-1.0+a1),P(8,-60)[1]+30*s*math.sin(-1.0+a1)),4.5*s)
    m.line(P(-8,-60),(P(-8,-60)[0]-30*s*math.cos(-1.0-a1),P(-8,-60)[1]+30*s*math.sin(-1.0-a1)),4.5*s)
    wc(buf,m,1.0,a=a,outline=0)
    hd=M().circ(*P(0,-80),11*s); wc(buf,hd,0.0,a=a,outline=1.4)
    bon=M().ell(*P(-3,-84),14*s,12*s); wc(buf,bon,0.0,a=a,outline=1.4)
def meeting_house(buf,x,y,s,a=1.0):
    m=M().rect(x-90*s,y-110*s,x+90*s,y).poly([(x-100*s,y-110*s),(x,y-170*s),(x+100*s,y-110*s)])
    wc(buf,m,0.3,a=a); st=M().rect(x-14*s,y-230*s,x+14*s,y-160*s).poly([(x-18*s,y-230*s),(x,y-280*s),(x+18*s,y-230*s)]); wc(buf,st,0.6,a=a)
    win=M()
    for k in (-50,0,50): win.rect(x+k*s-10*s,y-80*s,x+k*s+10*s,y-40*s)
    wc(buf,win,1.0,a=a,outline=0)
def candle(buf,x,y,t,a=1.0):
    wc(buf,M().rect(x-8,y-60,x+8,y),0.1,a=a); rgrad(buf,x,y-72,70,(0.5,0.35,0.1),0.35*a)
    fl=M().ell(x+math.sin(t*7)*1.5,y-72,5,12); comp(buf,fl,CANDLE,sh=0,rim=0,a=a)
def rye(buf,x,y,s,t,ergot=0.0,a=1.0):
    st=M().pline([(x+3*math.sin(u*2+t),y-u*260*s) for u in np.linspace(0,1,12)],2.5*s); wc(buf,st,1.0,a=a,outline=0)
    gr=M()
    for k in range(12):
        yy_=y-140*s-k*10*s; sd=1 if k%2 else -1; gr.ell(x+sd*8*s,yy_,6*s,10*s,sd*25)
    wc(buf,gr,0.3,a=a,outline=1.2)
    if ergot>0:
        eg=M()
        for k in (2,5,8):
            yy_=y-140*s-k*10*s; sd=1 if k%2 else -1; eg.poly(rot([(-4,-2),(4,-2),(3,22),(-3,22)],sd*0.4,x+sd*12*s,yy_-10*s,s*ergot,s*ergot))
        comp(buf,eg,PURP,sh=0.2,rim=0,a=a)
def stones(buf,cx,cy,n,a=1.0):
    g=np.random.default_rng(2); m=M()
    for k in range(n): m.ell(cx+g.uniform(-70,70),cy-k*9+g.uniform(-4,4),g.uniform(18,30),g.uniform(10,14),g.uniform(-20,20))
    wc(buf,m,0.6,a=a)
# ================= scenes =================
def s_hook(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    parchment(buf,0.1); nightsky(buf,420,t); frame(buf)
    pines(buf,430,14,3,0.95,110)
    house(buf,90,520,0.9,lit=1.0); house(buf,450,515,0.85,lit=1.0)
    meeting_house(buf,270,520,1.1)
    hl=M(); hl.poly([(26,560),(150,530),(390,540),(w-26,560),(w-26,654),(26,654)]); wc(buf,hl,0.3)
    fit=sm((t-EV["scream"]+0.2)/0.5)
    for k,(x,f) in enumerate(((170,1),(370,-1))): girl(buf,x,640,1.7,t,fit=fit*(1 if t<EV["scientist"]-0.4 else 0.3),face=f)
    if t>EV["fungus"]-0.3:
        u=sm((t-EV["fungus"]+0.3)/0.6); rye(buf,270,640,1.2*u+0.01,t,ergot=u)
    def hd(d,t=t):
        plaque(d,"SALEM · 1692",540,200,70,a=fa(t,EV["y1692"]-0.1,EV["girls"]-0.3),sc=pop(t,EV["y1692"]-0.1))
        seal(d,"19 HANGED",540,330,64,a=fa(t,EV["hanged"]-0.05,EV["girls"]-0.3),sc=pop(t,EV["hanged"]-0.05))
        plaque(d,"TWO GIRLS",540,200,62,a=fa(t,EV["girls"]-0.1,EV["scientist"]-0.3))
        plaque(d,"A FUNGUS?",540,200,90,a=fa(t,EV["fungus"]-0.1,sc["e"]+1),fg=(250,236,220),bg=cPu,sc=pop(t,EV["fungus"]-0.1))
    hud.append(hd); return buf,hud
def s_start(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    parchment(buf,0.15); frame(buf)
    wall=M().rect(26,66,w-26,560); wc(buf,wall,0.0,outline=0)
    for x in range(26,w-26,46): wc(buf,M().rect(x,66,x+2,560),0.9,outline=0)
    hearth=M().rect(170,330,370,560); wc(buf,hearth,1.0); inner=M().rect(195,380,345,560); comp(buf,inner,(0.15,0.08,0.05),sh=0,rim=0)
    for k in range(3): comp(buf,M().ell(240+k*30,540-8*math.sin(t*6+k),14,26+6*math.sin(t*5+k)),(1.0,0.55+0.1*k,0.2),sh=0,rim=0)
    rgrad(buf,270,520,170,(0.6,0.3,0.08),0.35)
    fl=M().rect(26,560,w-26,654); wc(buf,fl,0.6)
    for x in range(26,w-26,60): wc(buf,M().rect(x,566,x+2,654),1.0,outline=0)
    fit=sm((t-EV["fits"]+0.3)/0.6)
    girl(buf,130,630,1.9,t,fit=fit,face=1); girl(buf,420,630,1.9,t+1.3,fit=fit*sm((t-EV["abigail"])/0.5),face=-1)
    if t>EV["threw"]-0.2:
        u=sm((t-EV["threw"]+0.2)/0.8); cup=M().ell(260+120*u,520-200*u+250*u*u,10,7,u*400); wc(buf,cup,0.3)
    if t>EV["doctor"]-0.3: puritan(buf,300,640,1.6,face=-1,a=sm((t-EV["doctor"]+0.3)/0.4))
    if t>EV["more"]-0.3:
        a=sm((t-EV["more"]+0.3)/0.5)
        for k in range(3): girl(buf,70+k*45,610,0.9,t+k,fit=a,a=a)
    def hd(d,t=t):
        plaque(d,"SALEM VILLAGE · WINTER 1692",540,200,48,a=fa(t,EV["salem"]-0.1,EV["betty"]-0.3))
        plaque(d,"BETTY PARRIS, 9",320,200,44,a=fa(t,EV["betty"]-0.1,EV["screamed"]-0.3),ang=-2)
        plaque(d,"ABIGAIL WILLIAMS, 11",760,290,44,a=fa(t,EV["abigail"]-0.1,EV["screamed"]-0.3),ang=2)
        seal(d,"“WITCHCRAFT”",540,240,80,a=fa(t,EV["wc"]-0.1,EV["more"]-0.3),sc=pop(t,EV["wc"]-0.1))
        plaque(d,"…AND THEY NAMED NAMES",540,200,50,a=fa(t,EV["names"]-0.2,sc["e"]+1))
    hud.append(hd); return buf,hud
def s_accused(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    parchment(buf,0.1); frame(buf)
    pines(buf,300,12,7,0.6,80); house(buf,80,330,0.7); house(buf,460,320,0.7)
    wc(buf,M().rect(40,480,500,500),0.95)
    for x in range(60,500,60): wc(buf,M().rect(x,500,x+8,560),1.0,outline=0)
    for k,(e,x) in enumerate(((EV["tituba"],130),(EV["good"],270),(EV["osborne"],410))):
        a=sm((t-e+0.2)/0.4)
        if a>0.01: puritan(buf,x,480,1.45,tone=0.6 if k else 0.95,woman=True,a=a)
    cr=M()
    for k in range(9): x=40+k*58; cr.circ(x,610,22).poly([(x-30,654),(x+30,654),(x+22,620),(x-22,620)]); cr.rect(x-14,570,x+14,590).rect(x-24,588,x+24,594)
    wc(buf,cr,1.0,outline=0)
    if t>EV["devil"]-0.3:
        u=sm((t-EV["devil"]+0.3)/0.6); m=M()
        for k in range(14):
            ang=k/14*2*math.pi+t*0.5; r=200+30*math.sin(t*3+k); m.poly(rot([(0,-6),(60,0),(0,6)],ang,270,360,u,u))
        wc(buf,m,1.0,a=u*0.85,outline=0)
    if t>EV["panic"]-0.2:
        g=np.random.default_rng(int(t*10)); u=sm((t-EV["panic"]+0.2)/0.6)
        for k in range(int(12*u)): puritan(buf,g.uniform(40,500),g.uniform(380,640),g.uniform(0.4,0.7),tone=0.95,a=0.6)
    def hd(d,t=t):
        plaque(d,"THE FIRST ACCUSED",540,200,60,a=fa(t,EV["first"]-0.1,EV["confessed"]-0.3))
        for k,(s,e,x) in enumerate((("TITUBA",EV["tituba"],220),("SARAH GOOD",EV["good"],540),("SARAH OSBORNE",EV["osborne"],860))):
            plaque(d,s,x,1220 if k!=1 else 1260,34,a=fa(t,e,EV["confessed"]-0.3),ang=(k-1)*2)
        seal(d,"SHE CONFESSED",540,220,70,a=fa(t,EV["confessed"]-0.1,EV["panic"]-0.3),sc=pop(t,EV["confessed"]-0.1))
        plaque(d,"PANIC",540,240,120,a=fa(t,EV["panic"]-0.1,sc["e"]+1),fg=(250,236,220),bg=cI,sc=pop(t,EV["panic"]-0.1))
    hud.append(hd); return buf,hud
def s_trials(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    parchment(buf,0.35); frame(buf)
    ph=sm((t-EV["burned"]+0.3)/0.5)
    if ph<1:
        a=1-ph
        wall=M().rect(26,66,w-26,560); wc(buf,wall,0.0,a=a,outline=0)
        for k in range(3): wc(buf,M().rect(90+k*150,90,150+k*150,220).poly([(90+k*150,90),(120+k*150,70),(150+k*150,90)]),0.0,a=a,outline=2)
        for k in range(3): puritan(buf,160+k*110,300,1.0,face=1,a=a)
        wc(buf,M().rect(60,250,480,330),0.6,a=a)
        wc(buf,M().rect(60,330,480,350),1.0,a=a,outline=0)
        girl(buf,140,620,1.2,t,fit=0.6,a=a); puritan(buf,400,620,1.2,woman=True,tone=0.6,face=-1,a=a)
        sp=fa(t,EV["spectral"]-0.1,EV["k200"]-0.3)
        if sp>0:
            gh=M().circ(270,430,22).poly([(248,440),(292,440),(310,560),(230,560)]); comp(buf,gh,(1,1,1),sh=0,rim=0,a=0.55*sp*a)
            dots=M()
            for u in np.linspace(0,2*math.pi,40): dots.circ(270+60*math.cos(u),500+80*math.sin(u),1.6)
            wc(buf,dots,1.0,a=sp*a,outline=0)
        if t>EV["k200"]-0.3:
            u=sm((t-EV["k200"]+0.3)/1.2); g=np.random.default_rng(1)
            for k in range(int(60*u)): wc(buf,M().circ(g.uniform(40,500),g.uniform(380,640),5),1.0,a=0.8*a,outline=0)
    if ph>0:
        b2=np.zeros_like(buf); parchment(b2,0.2)
        sk=M().rect(26,66,w-26,420); comp(b2,sk,(0.62,0.20,0.14),sh=0,rim=0,a=0.55); frame(b2)
        pines(b2,520,10,9,0.95,90)
        hill=M().poly([(-10,654),(120,500),(300,470),(w+10,560),(w+10,654)]); wc(b2,hill,0.3)
        tr=M().line((330,480),(340,300),10).line((338,350),(400,300),5).line((336,330),(280,280),5); wc(b2,tr,1.0,outline=0)
        tal=M()
        for k in range(int(19*sm((t-EV["n19"]+0.1)/1.5))):
            x=80+(k%10)*40+(k//10)*10; y=180+(k//10)*70; tal.line((x,y),(x+4,y+50),4)
        wc(b2,tal,1.0,outline=0)
        if t>EV["stones"]-0.4: stones(b2,150,600,int(9*sm((t-EV["stones"]+0.4)/1.0))+1)
        buf[:]=buf*(1-ph)+b2*ph
    def hd(d,t=t,ph=ph):
        plaque(d,"A SPECIAL COURT",540,200,60,a=fa(t,EV["court"]-0.1,EV["spectral"]-0.3))
        plaque(d,"SPECTRAL EVIDENCE",540,200,56,a=fa(t,EV["spectral"]-0.1,EV["proof"]-0.1),fg=(250,236,220),bg=cI)
        seal(d,"A DREAM = PROOF",540,200,62,a=fa(t,EV["proof"]-0.2,EV["k200"]-0.3),sc=pop(t,EV["proof"]-0.2))
        plaque(d,"200+ ACCUSED",540,200,80,a=fa(t,EV["k200"]-0.1,EV["burned"]-0.3),sc=pop(t,EV["k200"]-0.1))
        plaque(d,"NO ONE WAS BURNED",540,560,52,a=ph*fa(t,EV["burned"]-0.1,EV["n19"]-0.1),fg=(250,236,220),bg=cI)
        seal(d,"19 HANGED",780,640,62,a=ph*sm((t-EV["n19"])/0.3))
        plaque(d,"GILES COREY",300,1250,44,a=ph*fa(t,EV["corey"]-0.1,sc["e"]+1),ang=-2)
    hud.append(hd); return buf,hud
def s_ergot(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    parchment(buf,0.15); frame(buf)
    ph2=sm((t-EV["rye"]+0.3)/0.5); ph3=sm((t-EV["bread"]+0.3)/0.5); ph5=sm((t-EV["poisoned"]+0.3)/0.5)
    if ph2<1:
        a=1-ph2
        bk=M().rect(150,220,390,560); wc(buf,bk,0.0,a=a); wc(buf,M().rect(150,220,390,300),1.0,a=a,outline=0)
        for k in range(8): wc(buf,M().rect(180,340+k*24,360,343+k*24),1.0,a=a,outline=0)
    if ph2>0 and ph3<1:
        a=ph2*(1-ph3)
        for k in range(5): rye(buf,90+k*90,640,1.5,t+k,ergot=sm((t-EV["ergotw"]+0.2)/0.6),a=a)
        if t>EV["ergotw"]:
            z=sm((t-EV["ergotw"])/0.6); cx,cy=380,250
            ring=M().circ(cx,cy,95*z); wc(buf,ring,0.0,a=a,outline=3)
            eg=M().poly(rot([(-14,-60),(14,-60),(10,60),(-10,60)],0.35,cx,cy,z,z)); comp(buf,eg,PURP,sh=0.2,rim=0,a=a)
    if ph3>0 and ph5<1:
        a=ph3*(1-ph5)
        lf=M().ell(270,520,140,60); wc(buf,lf,0.3,a=a)
        for k in range(4): wc(buf,M().line((170+k*60,490),(200+k*60,540),3),1.0,a=a,outline=0)
        for k in range(6): comp(buf,M().circ(190+k*30,505+(k%2)*20,5),PURP,sh=0,rim=0,a=a)
        g=np.random.default_rng(int(t*3)); sym=[EV["spasms"],EV["conv"],EV["crawl"],EV["hallu"]]
        for k,e in enumerate(sym):
            if t>e-0.1:
                x=110+k*110; y=300
                girl(buf,x,380,0.9,t+k,fit=0.8,a=a*sm((t-e+0.1)/0.3))
        if t>EV["hallu"]:
            for k in range(6):
                ang=t*0.8+k; comp(buf,M().ell(270+150*math.cos(ang),200+40*math.sin(ang*1.3),18,9),PURP,sh=0,rim=0,a=0.5*a)
        if t>EV["lsd"]-0.3:
            u=sm((t-EV["lsd"]+0.3)/0.5); mol=M()
            pts=[(270+50*math.cos(k*math.pi/3),250+50*math.sin(k*math.pi/3)) for k in range(7)]
            mol.pline(pts,3); mol.pline([(320,250),(380,220),(430,250)],3); mol.pline([(220,250),(170,280)],3)
            wc(buf,mol,1.0,a=a*u,outline=0)
    if ph5>0:
        b2=np.zeros_like(buf); parchment(b2,0.4); frame(b2)
        lf=M().ell(270,430,150,70); wc(b2,lf,0.3)
        for k in range(8): comp(b2,M().circ(180+k*26,410+(k%3)*18,5),PURP,sh=0,rim=0)
        q=M().circ(270,250,60); inn=M().circ(270,250,48); q.m=np.clip(q.m.astype(np.int16)-inn.m,0,255).astype(np.uint8); q.rect(256,280,284,330).rect(256,345,284,370); wc(b2,q,1.0,outline=0)
        buf[:]=buf*(1-ph5)+b2*ph5
    def hd(d,t=t):
        plaque(d,"1976 · LINNDA CAPORAEL",540,200,50,a=fa(t,EV["y1976"]-0.1,EV["rye"]-0.3))
        plaque(d,"PUBLISHED IN “SCIENCE”",540,300,40,a=fa(t,EV["journal"]-0.1,EV["rye"]-0.3),fg=(250,236,220),bg=cI)
        plaque(d,"RYE",250,200,70,a=fa(t,EV["rye"]-0.1,EV["bread"]-0.3))
        plaque(d,"ERGOT FUNGUS",540,1250,52,a=fa(t,EV["ergotw"]-0.1,EV["bread"]-0.3),fg=(250,236,220),bg=cPu,sc=pop(t,EV["ergotw"]-0.1))
        plaque(d,"ERGOTISM",540,200,74,a=fa(t,EV["ergotism"]-0.1,EV["lsd"]-0.3),fg=(250,236,220),bg=cPu)
        for k,(s,e) in enumerate((("SPASMS",EV["spasms"]),("CONVULSIONS",EV["conv"]),("CRAWLING SKIN",EV["crawl"]),("HALLUCINATIONS",EV["hallu"]))):
            plaque(d,s,540,1150+((k%2)*80) if False else 1100+k*0,30,a=0)
            plaque(d,s,220+(k%2)*640,1060+(k//2)*90,34,a=fa(t,e-0.05,EV["lsd"]-0.3),ang=(k%2-0.5)*4)
        seal(d,"LSD WAS FIRST MADE FROM ERGOT",540,200,46,a=fa(t,EV["lsd"]-0.1,EV["poisoned"]-0.3))
        plaque(d,"POISONED BY BREAD?",540,640,74,a=fa(t,EV["poisoned"]-0.1,sc["e"]+1),fg=(250,236,220),bg=cI,sc=pop(t,EV["poisoned"]-0.1))
    hud.append(hd); return buf,hud
def s_doubt(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    parchment(buf,0.08); frame(buf)
    ph2=sm((t-EV["families"]+0.3)/0.5); ph3=sm((t-EV["andover"]+0.3)/0.5); ph4=sm((t-EV["witness"]+0.3)/0.5)
    if ph2>0 and ph3<1:
        a=ph2*(1-ph3)
        hs=M().rect(80,300,460,600).poly([(60,300),(270,170),(480,300)]); wc(buf,hs,0.2,a=a)
        for k in range(8):
            x=120+(k%4)*90; y=440+(k//4)*150; sick=k in (1,6)
            if sick: girl(buf,x,y+10,1.1,t+k,fit=0.8,a=a)
            else: puritan(buf,x,y+10,0.85,tone=0.6,woman=k%2==0,a=a)
    if ph3>0 and ph4<1:
        a=ph3*(1-ph4)
        mp=M().poly([(60,180),(480,160),(500,620),(40,640)]); wc(buf,mp,0.0,a=a)
        for (x,y,r,nm) in ((330,470,24,"S"),(200,260,52,"A")): wc(buf,M().circ(x,y,r),0.95,a=a)
        wc(buf,M().pline([(330,470),(270,370),(200,260)],2),1.0,a=a,outline=0)
    if ph4>0:
        a=ph4
        qt=M().rect(80,200,460,480); wc(buf,qt,0.0,a=a)
        candle(buf,90,620,t,a=a)
        fr=sm((t-EV["fear"]+0.3)/0.5)
        if fr>0:
            for k in range(3): puritan(buf,180+k*90,640,1.0,tone=0.95,face=1 if k<2 else -1,a=fr)
    def hd(d,t=t):
        plaque(d,"MANY HISTORIANS SAY NO",540,560,58,a=fa(t,EV["no"]-0.1,EV["families"]-0.3),fg=(250,236,220),bg=cI,sc=pop(t,EV["no"]-0.1))
        plaque(d,"SAME BREAD — ONLY 1 OR 2 SICK",540,200,44,a=fa(t,EV["oneortwo"]-0.3,EV["andover"]-0.3))
        plaque(d,"ANDOVER",400,520,52,a=fa(t,EV["andover"]-0.1,EV["witness"]-0.3),fg=(250,236,220),bg=cR)
        plaque(d,"SALEM",660,940,40,a=fa(t,EV["andover"]-0.1,EV["witness"]-0.3))
        plaque(d,"MOST ACCUSATIONS",540,200,52,a=fa(t,EV["andover"]-0.1,EV["witness"]-0.3))
        card(d,"“She did it\nfor sport.”",540,680,fs=80,a=fa(t,EV["sport"]-0.3,EV["fear"]-0.3),fn="InstrumentSerif-Italic",fg=cI,bg=cP,pad=(50,26))
        for k,(s,e) in enumerate((("FEAR",EV["fear"]),("RIVALRIES",EV["rival"]),("DREAMS",EV["dreams"]))):
            seal(d,s,230+k*300,300,52,a=fa(t,e-0.1,sc["e"]+1),ang=(k-1)*5,sc=pop(t,e-0.1))
    hud.append(hd); return buf,hud
def s_end(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    parchment(buf,0.1); frame(buf)
    doc=M().rect(110,160,430,560); wc(buf,doc,0.0)
    for k in range(10): wc(buf,M().rect(140,200+k*28,400-(k%3)*30,203+k*28),1.0,outline=0)
    if t>EV["unlawful"]-0.2:
        s_=pop(t,EV["unlawful"]-0.2); comp(buf,M().circ(360,500,40*s_),RED,sh=0.3,rim=0)
    candle(buf,480,620,t)
    tf=Lx("Maybe the scariest")[1]+0.4
    if t>tf: buf*=max(0.12,1-(t-tf)*0.9)
    def hd(d,t=t,tf=tf):
        plaque(d,"DECLARED UNLAWFUL",540,200,60,a=fa(t,EV["unlawful"]-0.1,EV["last"]-0.3))
        plaque(d,"ELIZABETH JOHNSON JR.",540,200,52,a=fa(t,EV["johnson"]-0.1,EV["scariest"]-0.3),fg=(250,236,220),bg=cI)
        seal(d,"CLEARED IN 2022",540,320,70,a=fa(t,EV["y2022"]-0.1,EV["scariest"]-0.3),sc=pop(t,EV["y2022"]-0.1))
        plaque(d,"330 YEARS LATER",540,1250,52,a=fa(t,EV["y330"]-0.1,EV["scariest"]-0.3))
        plaque(d,"NOT WITCHES…\nBUT FRIGHTENED PEOPLE",540,560,62,a=fa(t,EV["notw"]-0.1,tf+0.2,0.3,0.4),fg=(250,236,220),bg=cI,pad=(36,16))
        if t>tf:
            kk=t-tf; a=sm((kk-0.2)/0.6); lg=LOGO.resize((int(LOGO.width*0.5),int(LOGO.height*0.5)),Image.LANCZOS); al=np.array(lg); al[:,:,3]=(al[:,:,3]*a).astype(np.uint8)
            d._image.alpha_composite(Image.fromarray(al),(W//2-lg.width//2,640-lg.height//2)); B.txt(d,(W//2,1000),"ORBITHOS",B.CZ(72,600),(255,215,140,int(255*a)),anchor="mm",stroke=2)
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,start=s_start,accused=s_accused,trials=s_trials,ergot=s_ergot,doubt=s_doubt,end=s_end)
BAND=(1-0.62*np.exp(-((yy-728)/78)**2))[...,None].astype(np.float32)
VIG=(1-0.30*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.012,(h,w,1)).astype(np.float32) for i in range(6)]
INKN=cv2.resize(np.random.default_rng(9).uniform(0,1,(24,14)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC)
DIST=np.sqrt((xx-w/2)**2+(yy-h*0.42)**2)/math.hypot(w/2,h*0.6)
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    buf,hud=render_scene(t,sc); hk=1.0; TRW=0.38
    ink=0.0
    if t>nb-TRW: ink=sm((t-(nb-TRW))/TRW)
    elif t<pb+TRW: ink=1-sm((t-pb)/TRW)
    if ink>0:
        r=ink*1.35
        m=np.clip((r-(DIST+0.35*INKN))/0.03,0,1)
        buf=buf*(1-m[...,None])+np.array(INK,np.float32)*m[...,None]
        hk=1-ink
    buf=np.clip(buf,0,1.3)
    buf=buf*PT*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
TOTAL=B.TOTAL
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
