import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid39")
for p in ["/home/claude/vid39","/home/claude/vid3","/home/claude/ep1"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
from paper import *
from PIL import Image, ImageDraw
EV=ev.EV; Lx=ev.Lx; SS=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
LOGO=E1.LOGO
NAVY=(0.04,0.06,0.14); DEEP=(0.07,0.11,0.25); LAKE=(0.12,0.45,0.58); LAKE2=(0.05,0.24,0.36); GAS=(0.55,0.98,0.48)
H1=(0.08,0.14,0.19); H2=(0.11,0.20,0.23); H3=(0.15,0.27,0.27); MOON=(0.95,0.93,0.82); RUST=(0.55,0.17,0.10); MAG=(1.0,0.45,0.15); ROCK=(0.20,0.17,0.16)
cG=(140,250,125); cC=(232,238,228); cN=(14,22,40); cR=(205,60,45); cY=(250,205,70)
BS="BigShoulders-Bold"
def F_(buf,m,col,a=1.0,sh=0.14): comp(buf,m,col,sh=sh,rim=0,a=a)
def blk(d,s,x,y,fs,a=1.0,fg=cN,bg=cG,ang=0,sc=1.0,pad=(26,6)): card(d,s,x,y,fs=fs,a=a,fg=fg,bg=bg,fn=BS,torn=False,ang=ang,sc=sc,pad=pad)
def pop(t,e): return spring((t-e)/0.5)
_g=np.random.default_rng(3); STX=_g.uniform(0,w,180); STY=_g.uniform(0,520,180); STB=_g.uniform(0.3,1,180)
def stars(buf,t,a=1.0):
    m=M()
    for x,y,b in zip(STX,STY,STB): m.circ(x,y,0.6+0.9*b)
    F_(buf,m,(0.9,0.92,1.0),a=a*0.8,sh=0)
def hills(buf,yb,cols,amp=40,off=0.0):
    for k,c in enumerate(cols):
        pts=[(x,yb+k*45+amp*math.sin(x/90+k*1.7+off)+amp*0.5*math.sin(x/37+k)) for x in range(-20,w+40,20)]
        F_(buf,M().poly([(-20,h+10)]+pts+[(w+40,h+10)]),c)
def hut(buf,x,y,s,col=(0.30,0.22,0.16),roof=(0.42,0.32,0.18),light=0.0,a=1.0):
    F_(buf,M().rect(x-18*s,y-24*s,x+18*s,y),col,a=a)
    F_(buf,M().poly([(x-26*s,y-22*s),(x,y-52*s),(x+26*s,y-22*s)]),roof,a=a)
    if light>0: F_(buf,M().rect(x-5*s,y-16*s,x+5*s,y-6*s),(1.0,0.78,0.35),a=a*light,sh=0); rgrad(buf,x,y-11*s,14*s,(1,0.7,0.3),0.4*light*a)
def cow(buf,x,y,s,col,a=1.0):
    m=M().ell(x,y,22*s,11*s).ell(x+24*s,y-6*s,8*s,6*s)
    for lx in (-14,-6,8,16): m.rect(x+lx*s-1.5*s,y+6*s,x+lx*s+1.5*s,y+18*s)
    F_(buf,m,col,a=a)
def gasblob(buf,cx,cy,r,t,seed,a=0.6,col=GAS):
    g=np.random.default_rng(seed); m=M()
    for k in range(9):
        ang=k*0.7+t*0.4*g.uniform(0.5,1.5); d=r*0.55
        m.circ(cx+math.cos(ang)*d,cy+math.sin(ang)*d*0.5,r*g.uniform(0.45,0.7))
    m.circ(cx,cy,r*0.8); F_(buf,m,col,a=a,sh=0)
def section(buf,t,lvl=1.0,plume=0.0,shake=0.0,pipe=0.0,gaslevel=1.0):
    """crater cross-section: rock, lake layers, magma, CO2 bubbles"""
    ox=shake*6*math.sin(t*50)
    buf[:]=NAVY; stars(buf,t,0.5)
    F_(buf,M().poly([(-10+ox,300),(90+ox,250),(150+ox,320),(390+ox,320),(450+ox,250),(w+10+ox,300),(w+10,h+10),(-10,h+10)]),ROCK,sh=0.2)
    lake=M().poly([(150+ox,320),(390+ox,320),(350+ox,560),(270+ox,600),(190+ox,560)])
    F_(buf,lake,LAKE)
    deep=M().poly([(170+ox,430),(370+ox,430),(350+ox,560),(270+ox,600),(190+ox,560)]); F_(buf,deep,lerpc(LAKE2,(0.10,0.30,0.22),0.5*gaslevel),sh=0)
    if gaslevel>0.05:
        g=np.random.default_rng(7); bm=M()
        for k in range(int(70*gaslevel)):
            x=g.uniform(200,340); y=g.uniform(450,585); bm.circ(x+ox+2*math.sin(t*2+k),y,1.6+g.uniform(0,1.8))
        F_(buf,bm,GAS,a=0.75,sh=0)
    mg=M().ell(270+ox,820,170,70); F_(buf,mg,MAG,sh=0); rgrad(buf,270,820,180,(1,0.4,0.1),0.35)
    cr=M()
    for k,xx_ in enumerate((215,265,320)): cr.pline([(xx_+ox+8*math.sin(y/20+k),y) for y in range(605,760,8)],3)
    F_(buf,cr,(0.35,0.15,0.08),sh=0)
    bub=M()
    for k in range(12):
        u=((t*0.35+k/12)%1.0); xx_=(215,265,320)[k%3]; y=760-u*160; bub.circ(xx_+ox+8*math.sin(y/20+k%3),y,2.4)
    F_(buf,bub,GAS,a=0.9,sh=0)
    if plume>0:
        pl=M().poly([(250+ox,600),(290+ox,600),(300+ox,600-280*plume),(240+ox,600-280*plume)]); F_(buf,pl,(0.7,0.95,0.9),a=0.85,sh=0)
    if pipe>0:
        F_(buf,M().rect(266+ox,320-30,274+ox,320+270*pipe),(0.85,0.86,0.88),sh=0.2)
def counter(t,e,n,dur=1.2): return int(n*eout((t-e)/dur))
# ================= scenes =================
def s_hook(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    mo=sm((t-EV["morning"]+0.3)/1.5)
    grad(buf,[(0,lerpc(NAVY,(0.30,0.32,0.40),mo)),(520,lerpc(DEEP,(0.62,0.56,0.52),mo))])
    stars(buf,t,1-mo)
    F_(buf,M().circ(420,140,34),MOON,sh=0,a=1-mo*0.6); rgrad(buf,420,140,110,(0.7,0.75,0.9),0.15*(1-mo))
    hills(buf,360,[H1,H2],40)
    F_(buf,M().ell(270,430,90,16),LAKE,sh=0)
    hills(buf,500,[H3],30,1.0)
    F_(buf,M().rect(-5,640,w+5,h+5),lerpc((0.10,0.16,0.14),(0.30,0.34,0.30),mo))
    for k,(x,y,s) in enumerate(((80,620,1.0),(170,640,1.25),(300,630,1.1),(420,650,1.3),(500,615,0.9))):
        off=sm((t-EV["morning"]-k*0.2)/0.2) if t>EV["morning"] else 0
        hut(buf,x,y,s,light=(1-off)*(0.6+0.4*math.sin(t*3+k)))
    if mo>0: gasblob(buf,270,560,170,t,3,a=0.18*mo)
    def hd(d,t=t):
        blk(d,"21 AUGUST 1986",540,200,56,a=fa(t,EV["date"]-0.1,EV["killed"]-0.2),fg=cC,bg=cN)
        a=fa(t,EV["killed"]-0.1,EV["noexp"]-0.3)
        if a>0.01: blk(d,f"{counter(t,EV['killed'],1746):,}",540,250,150,a=a,fg=cN,bg=cG,sc=pop(t,EV["killed"]-0.1)); blk(d,"LIVES · ONE NIGHT",540,400,44,a=a,fg=cC,bg=cN)
        for k,(s,e) in enumerate((("NO EXPLOSION",EV["noexp"]),("NO FIRE",EV["nofire"]),("NO SOUND",EV["nosound"]))):
            aa=fa(t,e-0.05,EV["morning"]-0.2,0.15,0.3)
            if aa>0.01:
                blk(d,s,540,220+k*110,60,a=aa,fg=cC,bg=cN,sc=pop(t,e-0.05))
                if t>e+0.15: d.line([(330,220+k*110),(330+int(420*eout((t-e-0.15)/0.3)),220+k*110)],fill=cR+(int(255*aa),),width=8)
        blk(d,"SILENCE",540,240,110,a=fa(t,EV["silent"]-0.1,sc["e"]+1),fg=cN,bg=cC,sc=pop(t,EV["silent"]-0.1))
    hud.append(hd); return buf,hud
def bottle(buf,cx,cy,s,t,fz,shake=0.0):
    ox=shake*4*math.sin(t*40)
    m=M().rect(cx-34*s+ox,cy-60*s,cx+34*s+ox,cy+110*s).poly([(cx-34*s+ox,cy-60*s),(cx-12*s+ox,cy-110*s),(cx+12*s+ox,cy-110*s),(cx+34*s+ox,cy-60*s)]).rect(cx-12*s+ox,cy-140*s,cx+12*s+ox,cy-110*s)
    F_(buf,m,(0.55,0.85,0.70),a=0.55,sh=0.15)
    F_(buf,M().rect(cx-14*s+ox,cy-150*s,cx+14*s+ox,cy-136*s),(0.85,0.2,0.2),sh=0.1)
    g=np.random.default_rng(int(t*10)); bm=M()
    for k in range(int(10+60*fz)): bm.circ(cx+ox+g.uniform(-28,28)*s,cy+g.uniform(-50,105)*s,1.5+g.uniform(0,2.5)*s)
    F_(buf,bm,(1,1,1),a=0.85,sh=0)
def s_lake(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    ph=sm((t-EV["nyos"]+0.5)/0.6)
    gl=0.2+0.8*sm((t-EV["dissolved"]+0.3)/1.0)
    section(buf,t,gaslevel=gl)
    if t>EV["soda"]-0.4:
        fz=sm((t-EV["fizzier"]+0.3)/1.5); bottle(buf,450,470,0.9,t,fz,shake=fz)
    def hd(d,t=t):
        blk(d,"LAKE NYOS · CAMEROON",540,200,56,a=fa(t,EV["nyos"]-0.1,EV["magma"]-0.3),fg=cC,bg=cN)
        blk(d,"VOLCANIC CRATER",540,300,40,a=fa(t,EV["crater"],EV["magma"]-0.3))
        blk(d,"MAGMA",540,1540-200,46,a=fa(t,EV["magma"]-0.1,EV["bottom"]-0.3),fg=cC,bg=cR)
        blk(d,"CO₂ LEAKS UP",540,200,58,a=fa(t,EV["co2"]-0.1,EV["bottom"]-0.3),sc=pop(t,EV["co2"]-0.1))
        blk(d,"HUGE PRESSURE",540,200,58,a=fa(t,EV["pressure"]-0.1,EV["soda"]-0.4),fg=cC,bg=cN)
        blk(d,"GAS STAYS DISSOLVED",540,300,42,a=fa(t,EV["dissolved"],EV["soda"]-0.4))
        blk(d,"LIKE A SEALED SODA",540,200,58,a=fa(t,EV["soda"]-0.1,sc["e"]+1),sc=pop(t,EV["soda"]-0.1))
    hud.append(hd); return buf,hud
def s_night(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    qk=fa(t,EV["quake"]-0.05,EV["quake"]+0.8,0.1,0.3)
    pl=sm((t-EV["rose"]+0.1)/1.2); gl=1-0.8*sm((t-EV["allonce"]+0.1)/0.8)
    section(buf,t,plume=pl,shake=qk,gaslevel=gl)
    ls=sm((t-EV["landslide"]+0.1)/0.8)
    if ls>0 and t<EV["rose"]:
        x=130+70*ls; y=290+70*ls; F_(buf,M().poly(rot([(-26,-16),(24,-20),(30,12),(-20,18)],ls*2,x,y)),(0.32,0.27,0.24))
    rn=fa(t,EV["rain"]-0.1,EV["quake"]-0.1,0.2,0.3)
    if rn>0:
        g=np.random.default_rng(int(t*24))
        for k in range(80): x=g.uniform(0,w); y=g.uniform(0,600); cv2.line(buf,(int(x),int(y)),(int(x-3),int(y+16)),(0.6,0.7,0.9),1,cv2.LINE_AA)
    if t>EV["allonce"]-0.1:
        u=sm((t-EV["allonce"]+0.1)/1.0); g=np.random.default_rng(4); bm=M()
        for k in range(60): bm.circ(g.uniform(190,350),600-u*g.uniform(100,420),2+g.uniform(0,5)*u)
        F_(buf,bm,GAS,a=0.9*(1-u*0.4),sh=0)
    if t>EV["dropped"]-0.2:
        cx,cy=450,140; F_(buf,M().circ(cx,cy,52),cC and (0.9,0.92,0.9),sh=0.25)
        ang=-2.2+3.4*(1-sm((t-EV["dropped"])/0.6)); F_(buf,M().line((cx,cy),(cx+40*math.cos(ang),cy+40*math.sin(ang)),5),RUST,sh=0)
    def hd(d,t=t):
        blk(d,"~9:00 PM",540,200,64,a=fa(t,EV["nine"]-0.1,EV["landslide"]-0.2),fg=cC,bg=cN,sc=pop(t,EV["nine"]-0.1))
        for k,(s,e) in enumerate((("LANDSLIDE?",EV["landslide"]),("HEAVY RAIN?",EV["rain"]),("EARTHQUAKE?",EV["quake"]))):
            blk(d,s,300 if k!=1 else 780,200+k*100,46,a=fa(t,e-0.05,EV["rose"]-0.3,0.15,0.3),fg=cC,bg=cN,ang=(k-1)*3)
        blk(d,"TRIGGER: UNKNOWN",540,560,50,a=fa(t,EV["nobody"],EV["rose"]-0.3),fg=cN,bg=cY)
        blk(d,"PRESSURE ↓",800,320,44,a=fa(t,EV["dropped"],sc["e"]+1),fg=cC,bg=cR)
        blk(d,"ALL AT ONCE",540,200,86,a=fa(t,EV["allonce"]-0.1,sc["e"]+1),sc=pop(t,EV["allonce"]-0.1))
    hud.append(hd); return buf,hud
def s_erupt(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    grad(buf,[(0,NAVY),(520,DEEP)]); stars(buf,t,0.8)
    F_(buf,M().circ(430,120,30),MOON,sh=0)
    F_(buf,M().poly([(-10,620),(80,470),(170,520),(370,520),(460,470),(w+10,620),(w+10,h+10),(-10,h+10)]),H2)
    F_(buf,M().rect(170,505,370,535),LAKE,sh=0)
    fo=sm((t-EV["fountain"]+0.1)/0.8)*(1-0.6*sm((t-EV["cloudw"])/1.5)); top=520-300*fo
    if fo>0:
        g=np.random.default_rng(int(t*20)); m=M().poly([(255,520),(285,520),(300,top),(240,top)])
        for k in range(30): m.circ(270+g.normal(0,22),top+g.uniform(0,60),g.uniform(3,9))
        F_(buf,m,(0.80,0.95,0.98),a=0.9,sh=0)
    wv=sm((t-EV["wave"])/1.0)
    if wv>0 and wv<1: F_(buf,M().ell(170+200*wv,512,30,14),(0.85,0.97,1.0),a=1-wv,sh=0)
    cg=sm((t-EV["cloudw"]+0.2)/3.0)
    if cg>0:
        for k in range(6): gasblob(buf,190+k*35+40*cg*(k-2.5),500-60*cg+15*math.sin(k),40+80*cg,t,k+10,a=0.32)
        if t>EV["rim"]:
            u=sm((t-EV["rim"])/2.0)
            for k in range(4): gasblob(buf,120-k*40*u,520+120*u+k*25,60+40*u,t,k+30,a=0.3*u)
            for k in range(4): gasblob(buf,420+k*40*u,520+120*u+k*25,60+40*u,t,k+40,a=0.3*u)
    def hd(d,t=t,top=top):
        a=fa(t,EV["m90"]-0.1,EV["cloudw"]-0.2)
        if a>0.01:
            blk(d,"90+ M",900,int(2*top),60,a=a,fg=cN,bg=cY); d.line([(130,int(2*top)),(820,int(2*top))],fill=cY+(int(200*a),),width=3)
        blk(d,"WAVE",250,900,50,a=fa(t,EV["wave"],EV["cloudw"]-0.2),fg=cC,bg=cN)
        blk(d,"INVISIBLE CO₂ CLOUD",540,200,62,a=fa(t,EV["invisible"]-0.1,sc["e"]+1),sc=pop(t,EV["invisible"]-0.1))
    hud.append(hd); return buf,hud
def s_cloud(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    mp=sm((t-EV["km25"]+0.4)/0.6)
    if mp<1:
        grad(buf,[(0,NAVY),(520,DEEP)]); stars(buf,t,0.8)
        prof=lambda x: 470+90*math.sin(x/70)+60*math.sin(x/31)
        pts=[(x,prof(x)) for x in range(-20,w+40,8)]
        F_(buf,M().poly([(-20,h+10)]+pts+[(w+40,h+10)]),H2)
        u=sm((t-EV["sank"]+0.2)/3.0); front=-20+600*u; Lv=622-160*sm((t-EV["sank"]+0.3)/4.0)
        tops=[(x,min(y,Lv+5*math.sin(x/23+t*2))) if x<front else (x,y) for x,y in pts]
        gm=M().poly(tops+[(x,y+3) for x,y in reversed(pts)])
        F_(buf,gm,GAS,a=0.6*(1-mp),sh=0)
        if u>0:
            g=np.random.default_rng(int(t*8)); wm=M()
            for k in range(14):
                x=g.uniform(-20,min(w,front)); wm.line((x,Lv-2),(x+20,Lv-2),2)
            F_(buf,wm,(0.8,1,0.75),a=0.5*(1-mp),sh=0)
        F_(buf,M().poly([(-20,h+10)]+[(x,y+40) for x,y in pts]+[(w+40,h+10)]),H1,a=1-mp)
        if t>EV["heavier"]-0.2:
            ar=sm((t-EV["heavier"])/0.4); F_(buf,M().line((270,170),(270,170+100*ar),10).poly([(250,170+100*ar),(290,170+100*ar),(270,200+100*ar)]),GAS,a=ar*(1-mp),sh=0)
    if mp>0:
        b2=np.zeros_like(buf); b2[:]=(0.10,0.15,0.16)
        g=np.random.default_rng(5); tm=M()
        for k in range(60): tm.circ(g.uniform(0,w),g.uniform(0,h),g.uniform(20,60))
        F_(b2,tm,(0.12,0.19,0.18),sh=0)
        r=230*sm((t-EV["km25"])/1.6)
        rm=M().circ(250,400,r); F_(b2,rm,GAS,a=0.30,sh=0)
        ring=M().circ(250,400,r); inn=M().circ(250,400,max(0,r-4)); ring.m=np.clip(ring.m.astype(np.int16)-inn.m,0,255).astype(np.uint8); F_(b2,ring,GAS,sh=0)
        F_(b2,M().ell(250,400,20,13),LAKE,sh=0.2)
        for k,(nm,e,x,y) in enumerate((("NYOS",EV["vnyos"],300,350),("KAM",EV["kam"],180,330),("CHA",EV["cha"],330,470),("SUBUM",EV["subum"],380,560))):
            s_=pop(t,e)
            if s_>0.02: hut(b2,x,y,0.8*s_,light=0.8 if t<EV["asleep"] else 0.3)
        buf[:]=buf*(1-mp)+b2*mp
    def hd(d,t=t,mp=mp):
        blk(d,"HEAVIER THAN AIR",540,200,62,a=fa(t,EV["heavier"]-0.1,EV["poured"]-0.2),fg=cN,bg=cG,sc=pop(t,EV["heavier"]-0.1))
        blk(d,"IT FLOWED LIKE WATER",540,200,58,a=fa(t,EV["poured"],EV["km25"]-0.4),fg=cC,bg=cN)
        blk(d,"25 KM",780,240,90,a=mp*sm((t-EV["km25"])/0.3)*(1-sm((t-EV["villages"]+0.2)/0.3)),fg=cN,bg=cG,sc=pop(t,EV["km25"]))
        blk(d,"~50 M DEEP · NO OXYGEN",540,1200,44,a=mp*fa(t,EV["m50"],EV["villages"]-0.2),fg=cC,bg=cN)
        for nm,e,x,y in (("NYOS",EV["vnyos"],600,700),("KAM",EV["kam"],360,580),("CHA",EV["cha"],660,840),("SUBUM",EV["subum"],760,1000)):
            tx_a=mp*sm((t-e)/0.3)
            if tx_a>0.01: blk(d,nm,x,y,34,a=tx_a,fg=cC,bg=cN)
        blk(d,"FAMILIES ASLEEP",540,200,64,a=fa(t,EV["asleep"]-0.2,sc["e"]+1),fg=cC,bg=cN)
    hud.append(hd); return buf,hud
def s_dawn(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    rd=sm((t-EV["red"]+0.3)/1.5)
    grad(buf,[(0,(0.48,0.50,0.55)),(520,(0.70,0.64,0.58))])
    hills(buf,330,[(0.30,0.36,0.36),(0.25,0.32,0.30)],35)
    if rd<1:
        F_(buf,M().rect(-5,560,w+5,h+5),(0.33,0.38,0.32))
        for k,(x,y) in enumerate(((90,600),(210,590),(330,605),(450,595))): hut(buf,x,y,1.2,col=(0.38,0.32,0.26),roof=(0.48,0.40,0.28),a=1-rd)
        cn=sm((t-EV["cattle"])/0.4)
        for k in range(5): cow(buf,70+k*95,650+(k%2)*14,1.1,(0.25,0.24,0.22),a=cn*(1-rd))
        fogm=M().rect(-5,560,w+5,700); F_(buf,fogm,GAS,a=0.10*(1-rd),sh=0)
    if rd>0:
        b2=np.zeros_like(buf); grad(b2,[(0,(0.48,0.50,0.55)),(520,(0.70,0.64,0.58))]); hills(b2,300,[(0.30,0.36,0.36)],35)
        F_(b2,M().ell(270,470,220,80),lerpc(LAKE,RUST,sm((t-EV["red"])/1.5)),sh=0.25)
        if t>EV["iron"]:
            g=np.random.default_rng(int(t*6)); im=M()
            for k in range(20): im.circ(g.uniform(80,460),g.uniform(420,520),2)
            F_(b2,im,(0.9,0.5,0.3),a=0.6,sh=0)
        buf[:]=buf*(1-rd)+b2*rd
    def hd(d,t=t):
        blk(d,"MOST NEVER WOKE UP",540,200,60,a=fa(t,EV["never"]-0.1,EV["cattle"]-0.2),fg=cC,bg=cN)
        blk(d,"~3,500 CATTLE",540,200,70,a=fa(t,EV["cattle"]-0.1,EV["survivor"]-0.3),fg=cN,bg=cC,sc=pop(t,EV["cattle"]-0.1))
        blk(d,"EVEN INSECTS",540,300,44,a=fa(t,EV["insects"],EV["survivor"]-0.3),fg=cC,bg=cN)
        card(d,"“I couldn't speak…\nthere was a strange smell.”",540,260,fs=44,a=fa(t,EV["survivor"]-0.1,EV["blue"]-0.3),fn="InstrumentSerif-Italic",fg=(25,25,30),bg=(235,238,232))
        blk(d,"THE LAKE TURNED RED",540,200,62,a=fa(t,EV["red"]-0.2,sc["e"]+1),fg=cC,bg=cR,sc=pop(t,EV["red"]-0.2))
        blk(d,"IRON FROM THE DEPTHS",540,1200,44,a=fa(t,EV["iron"],sc["e"]+1),fg=cC,bg=cN)
    hud.append(hd); return buf,hud
def s_why(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    buf[:]=NAVY
    ph=sm((t-EV["before"]+0.3)/0.6)
    if ph<1:
        for k in range(14):
            r=(t*60+k*40)%560; ring=M().circ(270,420,r); inn=M().circ(270,420,max(0,r-3)); ring.m=np.clip(ring.m.astype(np.int16)-inn.m,0,255).astype(np.uint8); F_(buf,ring,GAS,a=0.35*(1-r/560)*(1-ph),sh=0)
    if ph>0:
        F_(buf,M().poly([(60,200),(480,160),(500,620),(40,640)]),(0.12,0.20,0.20),a=ph)
        for nm,(x,y),e in (("NYOS",(200,330),EV["before"]),("MONOUN",(360,500),EV["monoun"])):
            s_=pop(t,e-0.1)
            if s_>0.02: F_(buf,M().ell(x,y,30*s_,18*s_),LAKE); rgrad(buf,x,y,50,(0.5,1,0.5),0.25*s_)
        F_(buf,M().line((200,330),(360,500),3),GAS,a=ph*sm((t-EV["monoun"])/0.5),sh=0)
    def hd(d,t=t,ph=ph):
        blk(d,"LIMNIC ERUPTION",540,560,96,a=fa(t,EV["limnic"]-0.1,EV["before"]-0.3),fg=cN,bg=cG,sc=pop(t,EV["limnic"]-0.1))
        blk(d,"ONE OF THE RAREST DISASTERS",540,720,40,a=fa(t,EV["rarest"],EV["before"]-0.3),fg=cC,bg=cN)
        blk(d,"NYOS · 1986",400,560,40,a=ph*sm((t-EV["before"])/0.3),fg=cC,bg=cN)
        blk(d,"MONOUN · 1984 · 37 DEAD",720,1100,40,a=ph*sm((t-EV["y1984"])/0.3),fg=cC,bg=cR)
    hud.append(hd); return buf,hud
def s_fix(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    pp=sm((t-EV["pipe"]+0.2)/1.4); fo=sm((t-EV["pushed"]+0.1)/0.6)
    gl=1.0-0.75*sm((t-EV["keeps"])/6.0)
    section(buf,t,pipe=pp,gaslevel=gl)
    if fo>0:
        g=np.random.default_rng(int(t*24)); m=M()
        for k in range(26): m.circ(270+g.normal(0,10+12*fo),290-g.uniform(0,150*fo),g.uniform(2,6))
        F_(buf,m,(0.85,0.97,1.0),a=0.85,sh=0)
        bm=M()
        for k in range(10):
            u=((t*0.8+k/10)%1.0); bm.circ(270,590-u*300,2.5)
        F_(buf,bm,GAS,sh=0)
    if t>EV["more"]-0.2:
        u=sm((t-EV["more"]+0.2)/1.0)
        for x in (220,320): F_(buf,M().rect(x-3,290,x+3,290+250*u),(0.85,0.86,0.88),sh=0.2)
    gx=480; F_(buf,M().rect(gx-14,360,gx+14,600),(0.15,0.20,0.25),sh=0.2); F_(buf,M().rect(gx-10,600-236*gl,gx+10,596),GAS,sh=0)
    def hd(d,t=t):
        blk(d,"2001 · ONE PIPE",540,200,60,a=fa(t,EV["y2001"]-0.1,EV["more"]-0.2),fg=cC,bg=cN,sc=pop(t,EV["y2001"]-0.1))
        blk(d,"A SELF-POWERED FOUNTAIN",540,300,44,a=fa(t,EV["keeps"]-0.2,EV["more"]-0.2))
        blk(d,"2011 · MORE PIPES",540,200,60,a=fa(t,EV["y2011"]-0.1,sc["e"]+1),fg=cC,bg=cN)
        blk(d,"GAS",960,1240,36,a=sm((t-sc["s"]-0.4)/0.4),fg=cN,bg=cG)
        blk(d,"FAR LESS GAS",540,300,50,a=fa(t,EV["less"]-0.1,sc["e"]+1),fg=cN,bg=cG,sc=pop(t,EV["less"]-0.1))
    hud.append(hd); return buf,hud
def s_end(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    grad(buf,[(0,NAVY),(520,DEEP)]); stars(buf,t,0.8)
    hills(buf,260,[H1,H2],30)
    kv=M().poly([(30,340),(200,300),(380,320),(520,360),(500,560),(320,620),(120,600),(20,500)]); F_(buf,kv,LAKE2,sh=0.2)
    g=np.random.default_rng(8); lm=M()
    n=int(220*sm((t-EV["millions"]+0.2)/1.5))
    for k in range(n):
        u=g.uniform(0,1); p0=[(30,340),(200,300),(380,320),(520,360),(500,560),(320,620),(120,600),(20,500),(30,340)]; i=int(u*8); f=u*8-i
        x=p0[i][0]+(p0[i+1][0]-p0[i][0])*f+g.normal(0,10); y=p0[i][1]+(p0[i+1][1]-p0[i][1])*f+g.normal(0,10); lm.circ(x,y,1.6)
    F_(buf,lm,(1.0,0.82,0.45),sh=0)
    if t>EV["full"]-0.2:
        bm=M()
        for k in range(40):
            u=((t*0.25+k/40)%1.0); bm.circ(80+(k*37)%400,580-u*220,1.8)
        F_(buf,bm,GAS,a=0.7,sh=0)
    tf=Lx("The quietest")[1]+0.4
    if t>tf: buf*=max(0.12,1-(t-tf)*0.9)
    def hd(d,t=t,tf=tf):
        blk(d,"LAKE KIVU",540,200,96,a=fa(t,EV["kivu"]-0.1,EV["quiet"]-0.3),fg=cN,bg=cG,sc=pop(t,EV["kivu"]-0.1))
        blk(d,"FULL OF DISSOLVED GAS",540,330,44,a=fa(t,EV["full"],EV["quiet"]-0.3),fg=cC,bg=cN)
        blk(d,"MILLIONS ON ITS SHORES",540,1240,48,a=fa(t,EV["millions"],EV["quiet"]-0.3),fg=cN,bg=cY)
        blk(d,"THE QUIETEST DISASTERS\nCAN BE THE DEADLIEST",540,560,70,a=fa(t,EV["quiet"]-0.1,tf+0.2,0.3,0.4),fg=cN,bg=cG,pad=(36,14))
        if t>tf:
            kk=t-tf; a=sm((kk-0.2)/0.6); lg=LOGO.resize((int(LOGO.width*0.5),int(LOGO.height*0.5)),Image.LANCZOS); al=np.array(lg); al[:,:,3]=(al[:,:,3]*a).astype(np.uint8)
            d._image.alpha_composite(Image.fromarray(al),(W//2-lg.width//2,640-lg.height//2)); B.txt(d,(W//2,1000),"ORBITHOS",B.CZ(72,600),(255,215,140,int(255*a)),anchor="mm",stroke=2)
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,lake=s_lake,night=s_night,erupt=s_erupt,cloud=s_cloud,dawn=s_dawn,why=s_why,fix=s_fix,end=s_end)
BAND=(1-0.62*np.exp(-((yy-728)/78)**2))[...,None].astype(np.float32)
VIG=(1-0.30*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.008,(h,w,1)).astype(np.float32) for i in range(6)]
FOG=cv2.resize(np.random.default_rng(2).uniform(0,1,(12,7)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC)
FOG2=cv2.resize(np.random.default_rng(5).uniform(0,1,(40,22)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC)
FG=(0.55*FOG+0.25*FOG2+0.35*(xx/w))
FG=(FG-FG.min())/(FG.max()-FG.min())
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
        th=-0.15+1.3*p
        mB=np.clip((th-FG)/0.06,0,1); edge=np.exp(-((FG-th)/0.07)**2)
        out=bufB*mB[...,None]+bufA*(1-mB[...,None])
        out+=edge[...,None]*(np.array(GAS,np.float32)-out)*0.55
        buf=out; hk=abs(2*p-1)
    buf=np.clip(buf,0,1.3)
    buf=buf*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*hk).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
TOTAL=B.TOTAL
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
