import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid40")
for p in ["/home/claude/vid40","/home/claude/vid3","/home/claude/ep1"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
from paper import *
from PIL import Image, ImageDraw
EV=ev.EV; Lx=ev.Lx; SS=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
LOGO=E1.LOGO
CLAY=(0.80,0.45,0.22); CLAYD=(0.62,0.31,0.14); BLK=(0.07,0.05,0.04); ARED=(0.48,0.11,0.09); AWH=(0.95,0.90,0.80); FIRE=(1.0,0.78,0.30)
cK=(22,16,12); cCl=(214,128,70); cW=(244,232,210); cR=(140,35,28)
CZN="../../../../../home/claude/vid40/Cinzel"
def tab(d,s,x,y,fs,a=1.0,fg=cK,bg=cCl,sc=1.0,ang=0,pad=(30,10)): card(d,s,x,y,fs=fs,a=a,fg=fg,bg=bg,fn=CZN,torn=False,ang=ang,sc=sc,pad=pad)
def big(d,s,x,y,fs,a=1.0,fg=cW,bg=cK,sc=1.0,pad=(30,10)): card(d,s,x,y,fs=fs,a=a,fg=fg,bg=bg,fn="BigShoulders-Bold",torn=False,sc=sc,pad=pad)
def pop(t,e): return spring((t-e)/0.5)
def K(buf,m,col=BLK,a=1.0,sh=0.10): comp(buf,m,col,sh=sh,rim=0,a=a)
def inc(buf,m,a=1.0): comp(buf,m,CLAY,sh=0,rim=0,a=a)        # incised line (shows clay through black)
PY0,PY1=150,640   # figure panel (terracotta frieze)
def meander(m,y,x0=0,x1=w,s=14):
    for x in range(int(x0),int(x1),s*2):
        m.pline([(x,y+s),(x,y),(x+s*1.5,y),(x+s*1.5,y+s*0.66),(x+s*0.5,y+s*0.66),(x+s*0.5,y+s*0.33)],2.2)
        m.line((x,y+s),(x+s*2,y+s),2.2)
def vase_bg(buf,t,night=0.0):
    sh=np.clip(1-((xx-w*0.38)/(w*0.75))**2,0,1)
    buf[:]=np.array(BLK,np.float32)*(0.6+0.7*sh)[...,None]
    rgrad(buf,150,400,120,(0.25,0.20,0.16),0.25)
    pan=lerpc(CLAY,(0.42,0.24,0.14),night)
    m=M().rect(0,PY0,w,PY1); comp(buf,m,pan,sh=0,rim=0)
    buf[PY0:PY1]*=(0.75+0.35*sh[PY0:PY1])[...,None]
    bd=M(); meander(bd,PY0-26); meander(bd,PY1+8); comp(buf,bd,lerpc(CLAY,(0.5,0.3,0.18),0.3),sh=0,rim=0)
    comp(buf,M().rect(0,PY0-4,w,PY0).rect(0,PY1,w,PY1+4),CLAYD,sh=0,rim=0)
    tg=M()
    for x in range(10,w,26): tg.poly([(x,PY1+40),(x+13,PY1+40),(x+6.5,PY1+80)])
    comp(buf,tg,CLAY,sh=0,rim=0,a=0.85)
def limb(m,p0,p1,w0,w1):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)+1e-6; nx,ny=-dy/L,dx/L
    m.poly([(p0[0]+nx*w0/2,p0[1]+ny*w0/2),(p1[0]+nx*w1/2,p1[1]+ny*w1/2),(p1[0]-nx*w1/2,p1[1]-ny*w1/2),(p0[0]-nx*w0/2,p0[1]-ny*w0/2)])
    m.circ(p1[0],p1[1],w1/2); m.circ(p0[0],p0[1],w0/2)
def man(buf,x,y,s=1.0,face=1,beard=True,pose="stand",arm=0.0,a=1.0,col=BLK,kneel=False,arms_up=False):
    """black-figure male in profile; (x,y)=feet; returns front hand point"""
    f=face
    def P(px,py): return (x+px*s*f,y+py*s)
    m=M()
    hip=P(0,-88)
    if kneel:
        limb(m,hip,P(34,-52),24*s,15*s); limb(m,P(34,-52),P(30,0),15*s,10*s)          # front leg (knee up)
        limb(m,hip,P(-18,-14),24*s,14*s); limb(m,P(-18,-14),P(-58,-6),14*s,9*s)      # back leg (knee down)
        m.poly([P(28,-4),P(46,-4),P(46,0),P(26,0)])
    else:
        limb(m,hip,P(14,-46),24*s,15*s); limb(m,P(14,-46),P(22,0),15*s,9*s); m.poly([P(18,-5),P(38,-4),P(38,0),P(16,0)])
        limb(m,hip,P(-12,-46),24*s,15*s); limb(m,P(-12,-46),P(-22,0),15*s,9*s); m.poly([P(-26,-5),P(-6,-4),P(-6,0),P(-28,0)])
    m.poly([P(-15,-92),P(15,-92),P(22,-120),P(30,-150),P(26,-162),P(-24,-162),P(-26,-140),P(-18,-118)])
    limb(m,P(0,-160),P(4,-172),12*s,12*s)
    hc=P(6,-186); m.circ(hc[0],hc[1],15*s)
    m.poly([P(18,-190),P(26,-180),P(19,-178)])
    if beard: m.poly([P(8,-176),P(24,-174),P(14,-154),P(0,-162)])
    ang=-0.35-2.1*arm; sx,sy=P(18,-152); L_=34*s
    ex,ey=sx+math.cos(ang)*L_*f,sy+math.sin(ang)*L_; ang2=ang-0.5*arm
    hx,hy=ex+math.cos(ang2)*L_*f,ey+math.sin(ang2)*L_
    limb(m,(sx,sy),(ex,ey),12*s,9*s); limb(m,(ex,ey),(hx,hy),9*s,7*s)
    bsx,bsy=P(-16,-150)
    if arms_up: limb(m,(bsx,bsy),P(-40,-200),12*s,8*s)
    else: limb(m,(bsx,bsy),P(-30,-118),12*s,9*s); limb(m,P(-30,-118),P(-22,-92),9*s,7*s)
    K(buf,m,col,a=a)
    ic=M(); ic.circ(*P(12,-189),2.0*s)
    ic.pline([P(-14,-128),P(2,-134),P(18,-128)],1.3*s); ic.pline([P(-16,-108),P(0,-112),P(14,-106)],1.2*s)
    ic.pline([P(-8,-200),P(4,-202),P(16,-196)],1.2*s)
    if beard: ic.line(P(10,-168),P(14,-160),1.1).line(P(4,-166),P(6,-158),1.1)
    inc(buf,ic,a=a)
    return (hx,hy)
def eagle(buf,cx,cy,s,t,flap=1.0,a=1.0,col=BLK):
    fl=math.sin(t*9)*0.5*flap
    m=M().ell(cx,cy,34*s,16*s)
    for sg in (1,-1):
        tip=(cx+sg*120*s,cy-60*s*(0.4+fl*sg*0+fl))
        m.poly([(cx+sg*10*s,cy-8*s),tip,(cx+sg*110*s,cy-30*s*(0.2+fl)),(cx+sg*90*s,cy-10*s),(cx+sg*70*s,cy+4*s)])
    m.circ(cx+40*s,cy-14*s,10*s).poly([(cx+48*s,cy-18*s),(cx+64*s,cy-10*s),(cx+48*s,cy-8*s)])
    m.poly([(cx-30*s,cy),(cx-62*s,cy-6*s),(cx-62*s,cy+10*s)])
    K(buf,m,col,a=a)
    ic=M()
    for sg in (1,-1):
        for k in range(4): ic.line((cx+sg*(30+k*18)*s,cy-6*s),(cx+sg*(40+k*20)*s,cy-26*s*(0.6+fl)),1.3)
    ic.circ(cx+42*s,cy-16*s,1.8)
    inc(buf,ic,a=a)
def rock(buf,x0,x1,ytop,col=BLK,a=1.0):
    m=M().poly([(x0,PY1),(x0+20,ytop+40),(x0+60,ytop+10),(x0+120,ytop),(x1-40,ytop+30),(x1,PY1)]); K(buf,m,col,a=a)
    ic=M().pline([(x0+40,ytop+60),(x0+70,ytop+110),(x0+60,ytop+160)],1.4).pline([(x1-60,ytop+50),(x1-80,ytop+120)],1.4); inc(buf,ic,a=a)
def flame(buf,x,y,s,t,a=1.0):
    for k,(c,sc_) in enumerate(((FIRE,1.0),((1.0,0.95,0.7),0.55))):
        pts=[]
        for i in range(25):
            u=i/24; ang=u*2*math.pi; r=(14*s*sc_)*(1-0.6*abs(math.sin(ang/2))**0.5)
            hgt=1.0+0.8*max(0,-math.cos(ang))
            pts.append((x+r*math.sin(ang)+2*math.sin(t*14+i),y-r*math.cos(ang)*hgt*1.6-6*s*sc_))
        comp(buf,M().poly(pts),c,sh=0,rim=0,a=a)
    rgrad(buf,x,y-10*s,40*s,(1.0,0.6,0.2),0.35*a)
def liver(buf,cx,cy,s,col=ARED,a=1.0,cut=None,keep="left"):
    pts=[(-90,-10),(-70,-40),(-20,-52),(40,-48),(85,-30),(95,-5),(60,15),(10,30),(-40,32),(-80,20)]
    P=[(cx+px*s,cy+py*s) for px,py in pts]
    m=M().poly(P)
    if cut is not None:
        cx2=cx+cut*s; cm=M().rect(cx-200*s,cy-100*s,cx2,cy+100*s) if keep=="left" else M().rect(cx2,cy-100*s,cx+200*s,cy+100*s)
        f=m.f()*cm.f(); comp(buf,f,col,sh=0.15,rim=0,a=a)
        ic=M().line((cx-50*s,cy-20*s),(cx-10*s,cy+10*s),1.4); inc(buf,ic.f()*cm.f(),a=a); return
    K(buf,m,col,a=a,sh=0.15)
    ic=M().pline([(cx-5*s,cy-50*s),(cx+5*s,cy-10*s),(cx-10*s,cy+28*s)],1.6).line((cx-50*s,cy-20*s),(cx-20*s,cy+10*s),1.3).line((cx+40*s,cy-30*s),(cx+60*s,cy),1.3)
    inc(buf,ic,a=a)
def daynight(buf,t,ph):
    """ph: 0=day sun, 1=night moon, at panel top"""
    x=60+420*((ph%1.0))
    if ph%2<1: comp(buf,M().circ(x,PY0+50,26),ARED,sh=0,rim=0)
    else:
        mm=M().circ(x,PY0+50,24); cut=M().circ(x+10,PY0+44,22); mm.m=np.clip(mm.m.astype(np.int16)-cut.m,0,255).astype(np.uint8); comp(buf,mm,AWH,sh=0,rim=0)
# ================= scenes =================
def s_hook(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    nt=sm((t-EV["night"]+0.2)/0.6)*(1-sm((t-EV["punish"]+0.3)/0.6))
    vase_bg(buf,t,nt*0.7)
    rock(buf,-20,150,280)
    hx,hy=man(buf,230,PY1-10,1.2,face=1,kneel=True,arms_up=True)
    ch=M()
    for k in range(7): ch.ell(150+k*10,PY1-232+k*2,4,3)
    comp(buf,ch,AWH,sh=0,rim=0)
    ea=sm((t-EV["eagle"]+0.3)/0.8)*(1-0.8*nt)
    eagle(buf,420-120*ea,260+150*ea,1.0,t,a=max(0.15,ea))
    lv=1.0 if t<EV["liver"] else (0.4 if t<EV["grew"] else 0.4+0.6*sm((t-EV["grew"])/0.8))
    liver(buf,250,PY1-140,0.20*lv+0.02,ARED)
    if nt>0: comp(buf,M().circ(430,PY0+50,22),AWH,sh=0,rim=0,a=nt)
    else: comp(buf,M().circ(80,PY0+50,24),ARED,sh=0,rim=0)
    def hd(d,t=t):
        tab(d,"EVERY DAY",300,1200,54,a=fa(t,0.6,EV["night"]-0.2),sc=pop(t,0.6))
        tab(d,"EVERY NIGHT",780,1200,54,a=fa(t,EV["night"]-0.05,EV["punish"]-0.3),fg=cW,bg=cK,sc=pop(t,EV["night"]-0.05))
        tab(d,"PROMETHEUS",540,200,78,a=fa(t,EV["prom"]-0.1,sc["e"]+1),fg=cW,bg=cK,sc=pop(t,EV["prom"]-0.1))
        big(d,"…AND IT'S REAL SCIENCE",540,1200,50,a=fa(t,EV["true"]-0.1,sc["e"]+1),fg=cK,bg=cCl)
    hud.append(hd); return buf,hud
def s_fire(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    vase_bg(buf,t)
    ph2=sm((t-EV["zeus"]+0.3)/0.5); ph4=sm((t-EV["withfire"]+0.3)/0.5)
    if ph4<1:
        a=1-ph4
        hx,hy=man(buf,200,PY1-10,1.25,face=1,arm=0.3+0.5*sm((t-EV["fennel"]+0.3)/0.6),a=a)
        if t>EV["zeus"]-0.3:
            zx,zy=man(buf,430,PY1-10,1.3,face=-1,arm=0.9,a=a*ph2)
            zb=M().pline([(zx-10,zy-30),(zx+6,zy-10),(zx-6,zy+2),(zx+10,zy+28)],5); comp(buf,zb,AWH,sh=0,rim=0,a=a*ph2)
        if t>EV["stole"]-0.2 or t>EV["spark"]-0.3:
            st=M().line((hx,hy+50),(hx+6,hy-40),4); K(buf,st,BLK,a=a)
            flame(buf,hx+6,hy-42,0.8+0.3*sm((t-EV["fennel"])/0.5),t,a=a*sm((t-EV["stole"]+0.2)/0.4))
        if t<EV["zeus"]:
            for k in range(4): man(buf,300+k*55,PY1-10,0.55,face=-1,beard=False,a=a*sm((t-EV["friend"]+0.2)/0.5))
    if ph4>0:
        b2=np.zeros_like(buf); vase_bg(b2,t)
        flame(b2,270,PY1-60,2.2,t)
        K(b2,M().rect(230,PY1-40,310,PY1-20),BLK)
        for k,(x,face) in enumerate(((120,1),(420,-1),(180,1),(360,-1))):
            man(b2,x,PY1-10,0.75,face=face,beard=k%2==0,arm=0.3)
        if t>EV["cook"]-0.2: K(b2,M().ell(270,PY1-90,34,22).rect(250,PY1-112,290,PY1-104),BLK); inc(b2,M().pline([(244,PY1-92),(296,PY1-92)],1.4))
        if t>EV["forge"]-0.2: K(b2,M().poly([(440,PY1-70),(500,PY1-70),(490,PY1-55),(450,PY1-55)]).rect(460,PY1-55,480,PY1-10),BLK)
        buf[:]=buf*(1-ph4)+b2*ph4
    def hd(d,t=t):
        tab(d,"A TITAN",540,200,64,a=fa(t,EV["titan"]-0.1,EV["fore"]-0.2),fg=cW,bg=cK)
        tab(d,"PRO-METHEUS = “FORETHOUGHT”",540,200,46,a=fa(t,EV["fore"]-0.1,EV["zeus"]-0.3))
        tab(d,"ZEUS",820,1200,60,a=fa(t,EV["zeus"]-0.1,EV["spark"]-0.3),fg=cW,bg=cK)
        tab(d,"STOLEN FIRE",540,200,66,a=fa(t,EV["stole"]-0.1,EV["fennel"]-0.3),sc=pop(t,EV["stole"]-0.1))
        tab(d,"HIDDEN IN A FENNEL STALK",540,200,46,a=fa(t,EV["fennel"]-0.1,EV["withfire"]-0.3),fg=cW,bg=cK)
        for k,(s,e) in enumerate((("COOK",EV["cook"]),("FORGE",EV["forge"]),("SURVIVE",EV["cold"]))):
            tab(d,s,250+k*290,1200,48,a=sm((t-e+0.1)/0.3),sc=pop(t,e-0.1))
    hud.append(hd); return buf,hud
def s_punish(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    st=t-sc["s"]
    cyc=0.0
    if t>EV["immortal"]-0.2: cyc=(t-EV["immortal"]+0.2)/1.5
    nt=0.5-0.5*math.cos(math.pi*cyc) if cyc>0 and t<EV["ages"]-0.3 else 0.0
    vase_bg(buf,t,nt*0.7)
    if cyc>0 and t<EV["ages"]-0.3: daynight(buf,t,cyc)
    rock(buf,-20,150,280)
    man(buf,230,PY1-10,1.2,face=1,kneel=True,arms_up=t<EV["free"]+0.3)
    ch=M()
    for k in range(7): ch.ell(150+k*10,PY1-232+k*2,4,3)
    comp(buf,ch,AWH,sh=0,rim=0,a=sm((t-EV["chained"])/0.4))
    fr=sm((t-EV["free"])/0.6)
    if fr>0: comp(buf,M().rect(120,PY1-170,240,PY1-60),lerpc(CLAY,(0.42,0.24,0.14),nt),sh=0,rim=0,a=0.0)
    ea=sm((t-EV["eagle2"]+0.2)/0.8)
    ex,ey=430-150*ea+20*math.sin(st*2),200+120*ea
    if t>EV["arrow"]:
        u=sm((t-EV["arrow"])/0.6); ex+=100*u; ey+=200*u
    if ea>0 and not (cyc>0 and nt>0.5 and t<EV["ages"]-0.3): eagle(buf,ex,ey,1.0,t,a=ea*(1-sm((t-EV["arrow"]-0.6)/0.4)))
    lvlt=0.22
    if cyc>0 and t<EV["ages"]: lvlt=0.10+0.12*nt
    liver(buf,250,PY1-140,lvlt,ARED)
    if t>EV["heracles"]-0.3:
        hx,hy=man(buf,470,PY1-10,1.2,face=-1,arm=0.55,a=sm((t-EV["heracles"]+0.3)/0.5))
        bow=M().pline([(hx-6+18*math.sin(u),hy-40+40*u) for u in np.linspace(0,2,15)],3); K(buf,bow,BLK)
        if t>EV["arrow"]-0.1:
            u=sm((t-EV["arrow"]+0.1)/0.3); ax=hx-(hx-ex)*u; ay=hy-(hy-ey)*u
            comp(buf,M().line((ax,ay),(ax+30,ay+6),3),AWH,sh=0,rim=0)
    if fr>0: comp(buf,M().rect(120,PY1-175,250,PY1-55),lerpc(CLAY,(0.42,0.24,0.14),nt),sh=0,rim=0,a=0)
    def hd(d,t=t):
        tab(d,"CHAINED TO A ROCK",540,200,56,a=fa(t,EV["chained"]-0.1,EV["everyday"]-0.3),fg=cW,bg=cK)
        tab(d,"EVERY DAY: THE EAGLE",540,200,52,a=fa(t,EV["everyday"]-0.1,EV["immortal"]-0.3),sc=pop(t,EV["everyday"]-0.1))
        tab(d,"IMMORTAL",540,200,70,a=fa(t,EV["immortal"]-0.1,EV["ages"]-0.3),fg=cW,bg=cK)
        tab(d,"THE LIVER GROWS BACK",540,1200,50,a=fa(t,EV["regrow"]-0.1,EV["ages"]-0.3),fg=cW,bg=cR)
        tab(d,"HERACLES",540,200,70,a=fa(t,EV["heracles"]-0.1,sc["e"]+1),sc=pop(t,EV["heracles"]-0.1))
        tab(d,"FREE",780,1200,60,a=fa(t,EV["free"]-0.1,sc["e"]+1),fg=cW,bg=cK)
    hud.append(hd); return buf,hud
def cells(buf,cx,cy,t,k,a=1.0):
    g=np.random.default_rng(3); m=M(); n=M()
    for i in range(18):
        x=cx+g.uniform(-170,170); y=cy+g.uniform(-110,110); r=14
        sp=k*sm((t*0.8+g.uniform(0,1))%1.0*2-0.3)*14 if k>0 else 0
        for sg in ((1,-1) if sp>1 else (0,)):
            m.circ(x+sg*sp,y,r); n.circ(x+sg*sp,y,4.5)
    K(buf,m,BLK,a=a,sh=0.08); comp(buf,n,ARED,sh=0,rim=0,a=a)
def s_science(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    vase_bg(buf,t)
    p_s=sm((t-EV["surgeons"]+0.3)/0.4); p_d=sm((t-EV["donor"]+0.3)/0.4); p_c=sm((t-EV["cells"]+0.3)/0.4)
    if p_s<1:
        a=1-p_s
        g_=1+0.15*math.sin(t*2)*sm((t-EV["best"])/0.4)
        liver(buf,270,400,1.8*g_,ARED,a=a)
        if t>EV["chose"]-0.2:
            rgrad(buf,270,400,200,(1,0.7,0.4),0.15*a*sm((t-EV["chose"])/0.4))
    if p_s>0 and p_d<1:
        a=p_s*(1-p_d)
        cut=sm((t-EV["twothirds"]+0.1)/0.6); gr=sm((t-EV["months"])/2.5)
        cx=270
        if cut<1: liver(buf,cx,400,1.8,ARED,a=a*(1-cut))
        if cut>0:
            liver(buf,cx-30*cut,400,1.8,ARED,a=a,cut=-30+0*gr,keep="left")
            if gr<1:
                comp(buf,M().rect(cx-30,240,cx+200,560),CLAY,sh=0,rim=0,a=0)
            if gr>0:
                g2=0.35+0.65*gr
                liver(buf,cx-30*cut+(1-g2)*-40,400,1.8*g2,ARED,a=a*gr)
        if cut>0 and gr<0.5:
            off=60*cut; liver(buf,cx+off*2,400-40*cut,1.8,(0.30,0.08,0.06),a=a*cut*(1-sm((t-EV["months"])/0.5)),cut=-30,keep="right")
    if p_d>0 and p_c<1:
        a=p_d*(1-p_c); g=sm((t-EV["both"])/2.0)
        liver(buf,150,330,(0.6+0.5*g),ARED,a=a); liver(buf,390,470,(0.9+0.2*g),ARED,a=a)
        man(buf,90,PY1-10,0.8,face=1,a=a*0.8); man(buf,470,PY1-10,0.8,face=-1,a=a*0.8)
    if p_c>0:
        cells(buf,270,400,t,sm((t-EV["divide"])/0.4)*(1-sm((t-EV["stop"])/0.5)),a=p_c)
    def hd(d,t=t):
        tab(d,"WHY THE LIVER?",540,200,62,a=fa(t,EV["organs"]-0.2,EV["best"]-0.3),fg=cW,bg=cK)
        big(d,"IT CAN GROW BACK",540,200,72,a=fa(t,EV["growing"]-0.3,EV["surgeons"]-0.3),fg=cK,bg=cCl,sc=pop(t,EV["growing"]-0.3))
        big(d,"UP TO ~2/3 REMOVED",540,200,60,a=fa(t,EV["twothirds"]-0.1,EV["months"]-0.2),fg=cW,bg=cR)
        big(d,"REGROWS IN MONTHS",540,200,60,a=fa(t,EV["months"]-0.1,EV["donor"]-0.3),fg=cK,bg=cCl,sc=pop(t,EV["months"]-0.1))
        big(d,"LIVING DONORS",540,200,62,a=fa(t,EV["donor"]-0.1,EV["both"]-0.2),fg=cW,bg=cK)
        big(d,"BOTH PIECES GROW",540,200,62,a=fa(t,EV["both"]-0.1,EV["cells"]-0.3),fg=cK,bg=cCl,sc=pop(t,EV["both"]-0.1))
        big(d,"CELLS WAKE UP & DIVIDE",540,200,56,a=fa(t,EV["divide"]-0.3,EV["stop"]-0.2),fg=cW,bg=cK)
        big(d,"…THEN THEY STOP",540,200,60,a=fa(t,EV["stop"]-0.1,sc["e"]+1),fg=cK,bg=cCl)
    hud.append(hd); return buf,hud
def s_knew(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    vase_bg(buf,t)
    p1=sm((t-EV["priests"]+0.3)/0.4); p2=sm((t-EV["another"]+0.3)/0.5)
    if p1<1:
        a=1-p1
        for k in range(3):
            x=150+k*120; y=380; comp(buf,M().circ(x,y,40+6*math.sin(t*3+k)),AWH if k!=1 else ARED,sh=0,rim=0,a=a*0.0)
        tab_a=a
        comp(buf,M().poly([(220,PY1-40),(320,PY1-40),(300,PY0+150),(240,PY0+150)]),BLK,sh=0.1,a=0)
    if p1>0 and p2<1:
        a=p1*(1-p2)
        hx,hy=man(buf,160,PY1-10,1.15,face=1,arm=0.45,a=a)
        liver(buf,hx+30,hy-10,0.35,ARED,a=a*sm((t-EV["omens"]+0.4)/0.4))
        K(buf,M().rect(100,PY1-60,130,PY1-10),BLK,a=a)
        if t>EV["doctors"]-0.3:
            ad=a*sm((t-EV["doctors"]+0.3)/0.4)
            sx,sy=man(buf,410,PY1-10,1.1,face=-1,arm=0.2,a=ad)
            K(buf,M().circ(370,PY1-115,42),BLK,a=ad); inc(buf,M().circ(370,PY1-115,30).circ(370,PY1-115,26),a=0)
            ring=M().circ(370,PY1-115,32); ii=M().circ(370,PY1-115,29); ring.m=np.clip(ring.m.astype(np.int16)-ii.m,0,255).astype(np.uint8); inc(buf,ring,a=ad)
            comp(buf,M().line((420,PY1-260),(470,PY1-20),4),BLK,sh=0,rim=0,a=ad)
        if t>EV["guess"]-0.2:
            q=sm((t-EV["guess"]+0.2)/0.4)
    if p2>0:
        b2=np.zeros_like(buf); vase_bg(b2,t,0.6)
        gm=M().poly([(80,PY1-30),(470,PY1-40),(480,PY1-90),(120,PY1-100),(60,PY1-70)]).circ(470,PY1-110,34); K(b2,gm,BLK)
        inc(b2,M().pline([(150,PY1-70),(250,PY1-80),(350,PY1-72)],1.5).circ(478,PY1-116,2.5))
        for k in range(2):
            vx=230+k*130+30*math.sin(t*2+k); vy=PY1-240+20*math.sin(t*3+k)
            eagle(b2,vx,vy,0.7,t+k,a=sm((t-EV["vultures"]+0.3)/0.5))
        lv=0.5+0.5*sm((t-EV["too"])/0.8); liver(b2,300,PY1-75,0.22*lv,ARED,a=sm((t-EV["tityus"])/0.4))
        buf[:]=buf*(1-p2)+b2*p2
    def hd(d,t=t,p1=p1,p2=p2):
        big(d,"DID THEY KNOW?",540,640,110,a=(1-p1)*sm((t-EV["know"]+0.2)/0.3),fg=cW,bg=cK,sc=pop(t,EV["know"]-0.2))
        tab(d,"READING OMENS IN LIVERS",540,200,46,a=fa(t,EV["omens"]-0.1,EV["doctors"]-0.3),fg=cW,bg=cK)
        tab(d,"BATTLE WOUNDS",540,200,58,a=fa(t,EV["wounds"]-0.2,EV["guess"]-0.3))
        big(d,"…OR A LUCKY GUESS?",540,200,60,a=fa(t,EV["guess"]-0.2,EV["another"]-0.3),fg=cK,bg=cCl,sc=pop(t,EV["guess"]-0.2))
        tab(d,"TITYUS",540,200,78,a=fa(t,EV["tityus"]-0.1,sc["e"]+1),fg=cW,bg=cK,sc=pop(t,EV["tityus"]-0.1))
        tab(d,"HIS LIVER GREW BACK TOO",540,1200,46,a=fa(t,EV["too"]-0.1,sc["e"]+1),fg=cW,bg=cR)
    hud.append(hd); return buf,hud
def amphora(buf,cx,cy,s,a=1.0):
    pts=[]
    for i in range(41):
        u=i/40; y=cy-260*s+u*520*s
        r=(40+ (150 if 0.25<u<0.95 else 0)*max(0.0,math.sin(math.pi*(u-0.25)/0.7))**0.8)*s if u>0.12 else 45*s
        if u>0.95: r=(60-200*(u-0.95))*s
        pts.append((cx+r,y))
    poly=pts+[(2*cx-x,y) for x,y in reversed(pts)]
    K(buf,M().poly(poly),BLK,a=a,sh=0.3)
    comp(buf,M().poly([(cx-150*s,cy-120*s),(cx+150*s,cy-120*s),(cx+140*s,cy+80*s),(cx-140*s,cy+80*s)]),CLAY,sh=0,rim=0,a=a)
    for sg in (1,-1): K(buf,M().pline([(cx+sg*42*s,cy-230*s),(cx+sg*110*s,cy-230*s),(cx+sg*120*s,cy-150*s)],10*s),BLK,a=a,sh=0)
def s_end(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    buf[:]=np.array(BLK,np.float32)*0.6; rgrad(buf,270,400,330,(0.35,0.22,0.12),0.5)
    z=1.0+0.08*sm((t-sc["s"])/8)
    amphora(buf,270,420,1.25*z)
    s=1.25*z; man(buf,250,420+80*s-6,0.55*s,face=1,kneel=True,arms_up=True)
    eagle(buf,320,420-40*s,0.42*s,t)
    flame(buf,200,420-60*s,0.8,t,a=sm((t-EV["sfire"]+0.2)/0.4))
    tf=Lx("Maybe the myth")[1]+0.4
    if t>tf: buf*=max(0.12,1-(t-tf)*0.9)
    def hd(d,t=t,tf=tf):
        for k,(s_,e) in enumerate((("A TITAN",EV["atitan"]),("A STOLEN FIRE",EV["sfire"]),("AN ORGAN THAT REFUSES TO DIE",EV["organ"]))):
            tab(d,s_,540,180+k*95,44 if k<2 else 40,a=fa(t,e-0.1,EV["tell"]-0.3),fg=cW if k!=2 else cK,bg=cK if k!=2 else cCl)
        big(d,"DID THE MYTH KNOW?",540,240,90,a=fa(t,EV["tell"]-0.2,tf+0.2,0.3,0.4),fg=cK,bg=cCl,sc=pop(t,EV["tell"]-0.2))
        if t>tf:
            kk=t-tf; a=sm((kk-0.2)/0.6); lg=LOGO.resize((int(LOGO.width*0.5),int(LOGO.height*0.5)),Image.LANCZOS); al=np.array(lg); al[:,:,3]=(al[:,:,3]*a).astype(np.uint8)
            d._image.alpha_composite(Image.fromarray(al),(W//2-lg.width//2,640-lg.height//2)); B.txt(d,(W//2,1000),"ORBITHOS",B.CZ(72,600),(255,215,140,int(255*a)),anchor="mm",stroke=2)
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,fire=s_fire,punish=s_punish,science=s_science,knew=s_knew,end=s_end)
BAND=(1-0.55*np.exp(-((yy-728)/78)**2))[...,None].astype(np.float32)
VIG=(1-0.25*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.010,(h,w,1)).astype(np.float32) for i in range(6)]
XS=(xx[0]-w/2)/(w/2)
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    buf,hud=render_scene(t,sc); hk=1.0; TRW=0.35
    tr=None
    if t>nb-TRW: tr=(i,i+1,(t-(nb-TRW))/(2*TRW))
    elif t<pb+TRW: tr=(i-1,i,(t-(pb-TRW))/(2*TRW))
    if tr:
        a_,b_,p=tr; p=sm(p)
        if b_==i: bufA,_=render_scene(t,SC[a_]); bufB=buf
        else: bufA=buf; bufB,_=render_scene(t,SC[b_])
        strip=np.concatenate([bufA,bufB],1); off=p*w
        k=math.sin(math.pi*p)
        u=np.arcsin(np.clip(XS*0.98,-1,1))/(math.pi/2)
        src=(w/2+(w/2)*(XS*(1-k)+u*k))+off
        mapx=np.tile(src.astype(np.float32),(h,1)); mapy=np.repeat(np.arange(h,dtype=np.float32)[:,None],w,1)
        buf=cv2.remap(strip,mapx,mapy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
        shade=(1-0.55*k*np.abs(XS)**2)[None,:,None].astype(np.float32); buf=buf*shade
        hk=abs(2*p-1)
    buf=np.clip(buf,0,1.3)
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
