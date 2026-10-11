import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid44")
for p in ["/home/claude/vid44","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
import drawkit as K
from drawkit import ink, outl, hatch, wash, part, dl, circ_pts, dashl, dim, rotp
from PIL import Image, ImageDraw
EV=ev.EV; Lx=ev.Lx
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= palette (1919 newspaper, two-colour print: black + molasses brown) =================
NEWS=(0.905,0.875,0.795); INK=(0.07,0.06,0.06); MOL=(0.33,0.15,0.05); MOLD=(0.20,0.08,0.03); MOLH=(0.66,0.40,0.16)
K.INK=INK
cI=(20,17,16); cM=(92,42,14); cN=(236,226,204)
def head(d,s,x,y,fs=130,a=1.0,sc=1.0,col=cI): card(d,s,x,y,fs=fs,a=a,fg=col,bg=None,fn="Gloock-Regular",torn=False,sc=sc,pad=(6,4),lsp=1.02)
def deck(d,s,x,y,fs=48,a=1.0,sc=1.0): card(d,s,x,y,fs=fs,a=a,fg=cI,bg=None,fn="LibreBaskerville-Regular",torn=False,sc=sc,pad=(6,4))
def btag(d,s,x,y,fs=60,a=1.0,sc=1.0,ang=-2,pad=(26,10)): card(d,s,x,y,fs=fs,a=a,fg=cN,bg=cM,fn="YoungSerif-Regular",torn=False,ang=ang,sc=sc,pad=pad)
def clip(d,s,x,y,fs=48,a=1.0,sc=1.0,ang=2): card(d,s,x,y,fs=fs,a=a,fg=cI,bg=(240,232,212),fn="LibreBaskerville-Regular",torn=True,ang=ang,sc=sc,pad=(26,14))
def sfx(d,s,x,y,fs=90,a=1.0,sc=1.0,ang=-6): card(d,s,x,y,fs=fs,a=a,fg=cM,bg=None,fn="EricaOne-Regular",torn=False,ang=ang,sc=sc,pad=(4,4))
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= background: newsprint page =================
_g=np.random.default_rng(1919)
PAGE=np.zeros((h,w,3),np.float32); PAGE[:]=NEWS
_mot=cv2.resize(_g.normal(0,1,(14,8)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC); _mot/=_mot.std()
PAGE*=(1-0.03*_mot)[...,None]
_tm=M()
for (x0,x1) in ((30,168),(186,354),(372,510)):
    for y in range(40,h-30,9):
        if _g.random()<0.08: continue
        L=_g.uniform(0.55,1.0)*(x1-x0); _tm.line((x0,y),(x0+L,y),1.6)
_ta=_tm.f()[...,None]*0.075; PAGE=PAGE*(1-_ta)+np.array(INK,np.float32)*_ta
_rm=M().line((177,36),(177,h-28),1).line((363,36),(363,h-28),1)
for y_ in (22,27): _rm.line((14,y_),(w-14,y_),1.2 if y_==22 else 2.2)
for y_ in (h-22,h-17): _rm.line((14,y_),(w-14,y_),1.2)
_ra=_rm.f()[...,None]*0.32; PAGE=PAGE*(1-_ra)+np.array(INK,np.float32)*_ra
# ================= objects =================
def molfill(buf,m,a=1.0,sheen=None,t=0.0):
    if a<=0 or m.x1<=m.x0: return
    comp(buf,m,MOL,sh=0.25,dx=2,dy=4,blur=4,rim=0,a=a)
    if sheen is not None:
        sm_=M(); sm_.pline(sheen,2.0); comp(buf,sm_,MOLH,sh=0,rim=0,a=0.7*a)
def wave_pts(xc,gy,H,t,lip=1.0):
    back=[(x,gy-H*max(0,(x+60)/(xc+60))**1.7+4*math.sin(x/22-t*5)) for x in np.linspace(-60,xc,34)]
    Y=gy-H; wb=3*math.sin(t*4)
    lipp=[(xc+20,Y-8),(xc+45,Y-4+wb),(xc+65,Y+12+wb),(xc+74,Y+34+wb),(xc+66,Y+54+wb),(xc+50,Y+58+wb),(xc+40,Y+46),(xc+30,Y+42),(xc+22,Y+56),(xc+24,Y+95),(xc+42,gy-H*0.45),(xc+82,gy-H*0.12),(xc+104,gy+2)]
    return back+lipp+[(-60,gy+2)],back
def molwave(buf,xc,gy,H,t,a=1.0):
    if a<=0: return
    pts,back=wave_pts(xc,gy,H,t); m=M().poly(pts)
    sheen=[(x,y+9) for x,y in back[8:]]
    molfill(buf,m,a,sheen,t)
    g=np.random.default_rng(abs(int(t*12)))
    dm=M()
    for k in range(7):
        q=(t*1.3+k*0.37)%1; dm.circ(xc+30+q*60+k*4,gy-H+18+q*q*160+k*9,3.5*(1-q)+1.5)
    comp(buf,dm,MOL,sh=0,rim=0,a=a)
def house(m,x,y,wd,ht,roof=0):
    m.rect(x,y-ht,x+wd,y)
    if roof==1: m.poly([(x-3,y-ht),(x+wd/2,y-ht-wd*0.35),(x+wd+3,y-ht)])
    elif roof==2: m.rect(x-3,y-ht-6,x+wd+3,y-ht)
    return m
HOUSES=[(30,58,120,1),(92,48,92,2),(144,62,140,0),(210,52,104,1),(266,70,156,2),(340,50,110,0),(394,60,132,1),(458,54,98,2)]
def city(buf,gy,a=1.0,crush=None,t=0.0,winx=True):
    if a<=0: return
    for k,(x,wd,ht,rf) in enumerate(HOUSES):
        c=crush(x+wd/2) if crush else 0.0
        if c>=1: continue
        m=house(M(),x,gy,wd,ht,rf)
        if c>0:
            hh=ht*(1-c); pts=[(x,gy),(x+wd,gy),(x+wd,gy-hh),(x,gy-hh)]; ang=0.18*c*(1 if k%2 else -1)
            m=M().poly(rotp(pts,ang,x+wd/2,gy))
        ink(buf,m,a)
        if winx and c==0:
            wm=M()
            for r_ in range(int(ht//30)):
                for c_ in range(int(wd//18)):
                    wm.rect(x+6+c_*18,gy-ht+10+r_*30,x+14+c_*18,gy-ht+24+r_*30)
            comp(buf,wm,(0.80,0.70,0.48),sh=0,rim=0,a=a*0.9)
def railway(buf,gy,y0,a=1.0,bend=0.0,cx=300):
    if a<=0: return
    def Y(x): return y0+bend*60*math.exp(-((x-cx)/70)**2)
    m=M(); xs=np.linspace(20,520,60)
    m.pline([(x,Y(x)) for x in xs],3); m.pline([(x,Y(x)+16) for x in xs],2)
    for k in range(25):
        x0=20+k*20; m.line((x0,Y(x0)),(x0+10,Y(x0+10)+16),1.4); m.line((x0+10,Y(x0+10)+16),(x0+20,Y(x0+20)),1.4)
    for x in range(60,520,110):
        lean=bend*0.5*math.exp(-((x-cx)/70)**2)*(1 if x<cx else -1)
        m.line((x,Y(x)+16),(x+lean*60,gy),4)
    ink(buf,m,a)
TX0,TX1,TY0,TY1=170,370,250,610
def tank(buf,lvl=0.0,a=1.0,shake=0.0,t=0.0,burst=0.0):
    if a<=0: return
    ox=shake*3*math.sin(t*70)
    if burst<=0:
        body=M().rect(TX0+ox,TY0,TX1+ox,TY1).ell((TX0+TX1)/2+ox,TY0,(TX1-TX0)/2,14)
        comp(buf,body,NEWS,sh=0.3,dx=3,dy=5,blur=5,rim=0,a=a)
        if lvl>0:
            ly=TY1-(TY1-TY0-6)*lvl; mm=M().rect(TX0+6+ox,ly,TX1-6+ox,TY1-4); molfill(buf,mm,a,[(TX0+10+ox,ly+6),(TX1-10+ox,ly+6)])
        o=M()
        for x0,y0,x1,y1 in ((TX0,TY0,TX0,TY1),(TX1,TY0,TX1,TY1),(TX0,TY1,TX1,TY1)): o.line((x0+ox,y0),(x1+ox,y1),3)
        o.pline(circ_pts((TX0+TX1)/2+ox,TY0,(TX1-TX0)/2,14,0,2*math.pi,60),3)
        for y in range(TY0+40,TY1,46):
            o.line((TX0+ox,y),(TX1+ox,y),1.2)
            for x in range(TX0+8,TX1-4,12): o.circ(x+ox,y+5,1.6)
        ink(buf,o,a)
    else:
        b=eout(burst)
        for sd in (-1,1):
            xa,xb=(TX0,(TX0+TX1)/2) if sd<0 else ((TX0+TX1)/2,TX1)
            pts=[(xa,TY0+8),(xb,TY0+8),(xb,TY1),(xa,TY1)]
            pv=(TX0,TY1) if sd<0 else (TX1,TY1)
            rp=rotp(pts,sd*1.05*b,pv[0],pv[1]); m=M().poly(rp); comp(buf,m,NEWS,sh=0.3,rim=0,a=a); outl(buf,m,a=a,th=1,fill=0)
            r=M()
            for y in range(TY0+40,TY1,46): r.pline(rotp([(xa,y),(xb,y)],sd*1.05*b,pv[0],pv[1]),1.2)
            ink(buf,r,a)
def rivets(buf,t,t0,a=1.0):
    if t<t0 or a<=0: return
    g=np.random.default_rng(31); m=M(); lm=M()
    for k in range(22):
        tk=t0+k*0.08
        if t<tk: continue
        dt=t-tk; sd=-1 if k%2 else 1; y=TY0+60+(k*37)%330; x=(TX1 if sd>0 else TX0)
        vx=sd*g.uniform(260,420); vy=g.uniform(-220,-60)
        px,py=x+vx*dt,y+vy*dt+300*dt*dt
        if -10<px<w+10 and py<h: m.circ(px,py,4.6); lm.line((px-sd*18,py-vy*0.04),(px,py),1.2)
    ink(buf,m,a); ink(buf,lm,0.5*a)
def thermo(buf,x,y,lvl,a=1.0):
    if a<=0: return
    o=M().pline([(x-9,y-170),(x-9,y),(x+9,y),(x+9,y-170)],2).pline(circ_pts(x,y-170,9,9,math.pi,2*math.pi,20),2)
    o.pline(circ_pts(x,y+16,18,n=40),2.5)
    for k in range(8): o.line((x+12,y-k*20),(x+20,y-k*20),1.2)
    ink(buf,o,a); f=M().circ(x,y+16,13).rect(x-4,y-150*lvl,x+4,y+4); ink(buf,f,a)
def barrel(m,x,y,s=1.0):
    m.ell(x,y,26*s,36*s); return m
def chain(buf,t,a=1.0):
    if a<=0: return
    e=[EV["meant"]-0.2,EV["alcohol"]-0.2,EV["explosives"]-0.2]
    k=[sm((t-x)/0.35) for x in e]
    if k[0]>0:
        m=M().rect(60,420,140,520).ell(100,420,40,10).ell(100,520,40,10); molfill(buf,m,a*k[0]); o=M()
        for y in (440,500): o.line((60,y),(140,y),2)
        ink(buf,o,a*k[0])
    if k[1]>0:
        ink(buf,dl(M(),[(155,470),(195,470)],k[1],2.5),a); ink(buf,M().poly([(195,462),(205,470),(195,478)]),a*k[1])
        f=M().poly([(250,400),(270,400),(270,440),(305,520),(215,520),(250,440)]); outl(buf,f,a=a*k[1],th=1,fill=0.0)
        ink(buf,M().poly([(225,500),(295,500),(305,520),(215,520)]),a*k[1]*0.6)
        for j in range(3): ink(buf,M().circ(258+j*6,390-((t*40+j*15)%40),3),a*k[1]*0.6)
    if k[2]>0:
        ink(buf,dl(M(),[(320,470),(360,470)],k[2],2.5),a); ink(buf,M().poly([(360,462),(370,470),(360,478)]),a*k[2])
        sh=M().rect(395,430,455,525).poly([(395,430),(425,375),(455,430)]); ink(buf,sh,a*k[2])
        ink(buf,M().rect(395,500,455,507),0.0); comp(buf,M().rect(392,505,458,512),MOL,sh=0,rim=0,a=a*k[2])
def person_m(x,y,s=1.0,arms=0.0,t=0.0):
    m=M().circ(x,y-120*s,13*s).poly([(x-18*s,y-104*s),(x+18*s,y-104*s),(x+14*s,y-40*s),(x-14*s,y-40*s)])
    for sd in (-1,1):
        an=-math.pi/2+sd*(0.5+0.4*arms)+0.08*math.sin(t*3+sd)
        m.line((x+sd*15*s,y-100*s),(x+sd*15*s+math.cos(an)*48*s,y-100*s+math.sin(an)*48*s),7*s)
        m.line((x+sd*8*s,y-42*s),(x+sd*10*s,y+10*s),9*s)
    return m
def gavel(buf,x,y,ang,a=1.0):
    pv=(x+140,y); hm=M().poly(rotp([(x,y-8),(x+140,y-8),(x+140,y+8),(x,y+8)],ang,*pv)); hm.poly(rotp([(x-40,y-30),(x,y-30),(x,y+30),(x-40,y+30)],ang,*pv))
    ink(buf,hm,a)
def bomb(buf,x,y,a=1.0,t=0.0):
    if a<=0: return
    ink(buf,M().circ(x,y,40).rect(x-12,y-52,x+12,y-36),a); ink(buf,dl(M(),[(x,y-52),(x+12,y-70),(x+30,y-74)],1.0,2),a)
    for k in range(5):
        an=k*1.26+t*6; ink(buf,M().line((x+30,y-74),(x+30+math.cos(an)*12,y-74+math.sin(an)*12),1.5),a)
def sun(buf,x,y,a=1.0,t=0.0):
    if a<=0: return
    ink(buf,M().circ(x,y,30),a)
    m=M()
    for k in range(12):
        an=k*math.pi/6+t*0.4; m.line((x+math.cos(an)*40,y+math.sin(an)*40),(x+math.cos(an)*58,y+math.sin(an)*58),3)
    ink(buf,m,a)
# ================= scenes =================
GY=640
def s_hook(t,sc):
    buf=PAGE.copy(); hud=[]
    tt=max(t,-1.0)
    xc=200+34*tt
    crush=lambda x: cl((xc+20-x)/50)
    railway(buf,GY,GY-210,a=1.0,bend=0.0)
    city(buf,GY,1.0,crush=crush,t=tt)
    molwave(buf,xc,GY,250+12*math.sin(tt*2),tt)
    ink(buf,M().rect(14,GY,w-14,GY+3),1.0)
    dr=sm((t-EV["syrup"]+0.4)/0.3)
    if dr>0:
        y=330+(t-EV["syrup"]+0.4)*0.0; m=M().circ(460,330+22*dr,14*dr).poly([(460-10*dr,330+12*dr),(460,300),(460+10*dr,330+12*dr)]); molfill(buf,m,dr)
    def hd(d,t=t):
        k0=1.0 if t<0.4 else ap(t,-1,EV["how"]+0.1)
        deck(d,"BOSTON · JANUARY 15, 1919",540,150,40,a=k0)
        head(d,"MOLASSES WAVE",540,270,128,a=k0)
        head(d,"KILLS 21",540,410,150,a=k0,col=cM if t>EV["n21"]-0.05 else cI,sc=1.0 if t<EV["n21"] else 1+0.08*math.exp(-(t-EV["n21"])*5))
        head(d,"HOW CAN",540,260,140,a=ap(t,EV["how"],sc["e"]+1),sc=pop(t,EV["how"]-0.1))
        head(d,"SYRUP KILL?",540,410,150,a=ap(t,EV["syrup"]-0.1,sc["e"]+1),sc=pop(t,EV["syrup"]-0.15),col=cM)
    hud.append(hd); return buf,hud
def s_tank(t,sc):
    buf=PAGE.copy(); hud=[]
    pC=sm((t-EV["meant"]+0.3)/0.35); pW=sm((t-EV["warm"]+0.3)/0.35)
    aA=1-pC*(1-pW); aCh=pC*(1-pW)
    burst=cl((t-EV["burst"]+0.05)/0.7)
    if aA>0:
        ink(buf,M().rect(14,TY1,w-14,TY1+3),aA)
        lvl=0.2+0.7*eout(cl((t-EV["gallons"]+0.3)/1.4)) if t<EV["meant"] else 0.9
        if t<EV["gallons"]-0.3: lvl=0.2*sm((t-EV["tank"]+0.3)/0.6)
        shake=sm((t-EV["sound"]+0.1)/0.3)*(1 if burst<=0 else 0)
        if burst>0:
            r=eout(burst); m=M()
            m.poly([(270-260*r-30,TY1+2)]+[(270+math.cos(q)*(30+300*r),TY1-(200*(1-r*0.6))*abs(math.sin(q))**0.7+6*math.sin(q*9+t*8)) for q in np.linspace(math.pi,2*math.pi,40)]+[(270+260*r+30,TY1+2)])
            molfill(buf,m,aA)
        tank(buf,lvl,aA,shake,t,burst)
        rivets(buf,t,EV["rivets"]-0.05,aA)
        thermo(buf,470,430,0.25+0.5*sm((t-EV["warm"]+0.2)/0.8),a=aA*pW)
    if aCh>0: chain(buf,t,aCh)
    def hd(d,t=t,pW=pW,aCh=aCh,burst=burst):
        deck(d,"JANUARY 15, 1919",540,200,52,a=ap(t,EV["jan"],EV["gallons"]),sc=pop(t,EV["jan"]-0.1))
        n=int(eout(cl((t-EV["gallons"]+0.2)/1.2))*2300000)
        head(d,f"{n:,}",540,240,140,a=ap(t,EV["gallons"],EV["meant"]),col=cM)
        deck(d,"GALLONS OF MOLASSES",540,350,46,a=ap(t,EV["gallons"]+0.3,EV["meant"]))
        deck(d,"PURITY DISTILLING CO.",540,1290,38,a=ap(t,EV["tank"],EV["meant"]))
        btag(d,"INDUSTRIAL ALCOHOL",540,260,58,a=ap(t,EV["alcohol"],EV["warm"]),sc=pop(t,EV["alcohol"]-0.1))
        head(d,"FOR EXPLOSIVES",540,1210,96,a=ap(t,EV["explosives"],EV["warm"]),sc=pop(t,EV["explosives"]-0.1))
        deck(d,"WORLD WAR I MUNITIONS",540,1310,36,a=ap(t,EV["explosives"]+0.3,EV["warm"]))
        head(d,"ODDLY WARM",540,240,120,a=ap(t,EV["warm"],EV["sound"]),sc=pop(t,EV["warm"]-0.1))
        clip(d,"2°F yesterday · 40°F today",790,560,40,a=ap(t,EV["warm"]+0.3,EV["sound"]))
        sfx(d,"RAT-TAT-TAT!",540,240,110,a=ap(t,EV["gun"]-0.1,EV["burst"]),sc=pop(t,EV["gun"]-0.15))
        btag(d,"RIVETS POPPING",540,1220,66,a=ap(t,EV["rivets"],EV["burst"]),sc=pop(t,EV["rivets"]-0.1))
        head(d,"TANK BURSTS",540,250,140,a=ap(t,EV["burst"]-0.05,sc["e"]+1),sc=pop(t,EV["burst"]-0.15),col=cM)
    hud.append(hd); return buf,hud
def s_wave(t,sc):
    buf=PAGE.copy(); hud=[]
    pB=sm((t-EV["crush"]+0.3)/0.35)
    t0=sc["s"]
    if pB<1:
        a=1-pB; xc=60+eout(cl((t-t0)/3.2))*250
        ink(buf,M().rect(14,GY,w-14,GY+3),a)
        H=300
        molwave(buf,xc,GY,H,t,a)
        du=sm((t-EV["ft25"]+0.15)/0.5)
        if du>0: ink(buf,dim(M(),(xc+70,GY),(xc+70,GY-H),u=du),a*0.9)
        sp=sm((t-EV["rushes"]+0.2)/0.4)
        if sp>0:
            m=M()
            for k in range(7):
                y=GY-40-k*38; ph=(t*3+k*0.37)%1; x=xc+110+ph*160
                m.line((x,y),(x+40*(1-ph)+10,y),2)
            ink(buf,m,a*sp)
        # little figure running
        if t<EV["crush"]:
            px=xc+150+(t-t0)*40; ink(buf,person_m(px,GY,0.55,0.6,t*4),a)
    if pB>0:
        xc=-40+eout(cl((t-EV["crush"]+0.3)/2.0))*520
        crush=lambda x: cl((xc+10-x)/40)
        bend=sm((t-EV["bends"]+0.2)/0.6)
        railway(buf,GY,GY-230,a=pB,bend=bend,cx=300)
        city(buf,GY,pB,crush=crush,t=t)
        g=np.random.default_rng(int(t*10)%5)
        m=M().poly([(-20,GY+3)]+[(x,GY-120-10*math.sin(x/30-t*6)) for x in np.linspace(-20,xc,30)]+[(xc+30,GY+3)]); molfill(buf,m,pB,[(x,GY-110-10*math.sin(x/30-t*6)) for x in np.linspace(0,xc-10,20)])
        ink(buf,M().rect(14,GY,w-14,GY+3),pB)
    def hd(d,t=t,pB=pB):
        head(d,"BROWN WAVE",540,240,140,a=ap(t,EV["brown"],EV["ft25"]),sc=pop(t,EV["brown"]-0.1),col=cM)
        head(d,"25 FEET HIGH",540,240,130,a=ap(t,EV["ft25"],EV["mph"]),sc=pop(t,EV["ft25"]-0.1))
        head(d,"35 MPH",540,240,170,a=ap(t,EV["mph"],EV["crush"]),sc=pop(t,EV["mph"]-0.1),col=cM)
        deck(d,"faster than you can run",540,380,44,a=ap(t,EV["mph"]+0.4,EV["crush"]))
        btag(d,"BUILDINGS CRUSHED",540,240,66,a=ap(t,EV["buildings"],EV["bends"]),sc=pop(t,EV["buildings"]-0.1))
        btag(d,"ELEVATED RAILWAY BENT",540,240,60,a=ap(t,EV["bends"],sc["e"]+1),sc=pop(t,EV["bends"]-0.1))
    hud.append(hd); return buf,hud
def s_stuck(t,sc):
    buf=PAGE.copy(); hud=[]
    pB=sm((t-EV["half"]+0.3)/0.35)
    cool=sm((t-EV["cooled"]+0.2)/1.2); thk=sm((t-EV["thick"]+0.2)/0.8)
    lvl=GY-90
    if pB<1:
        a=1-pB
        amp=10*(1-thk); spd=6*(1-0.9*thk)
        m=M().poly([(14,GY+3)]+[(x,lvl-amp*math.sin(x/34-t*spd)) for x in np.linspace(14,w-14,40)]+[(w-14,GY+3)])
        molfill(buf,m,a,[(x,lvl+10-amp*math.sin(x/34-t*spd)) for x in np.linspace(30,w-30,30)])
        if thk>0:
            pm=M().line((90,250),(300,400),9); ink(buf,pm,a*thk)
            sw=4*math.sin(t*1.3); top=(296,404); L=lvl-top[1]; neck=1.5+4*(1-thk*0.6)
            q=[(top[0]+sw*f*f-(10*(1-f)+neck*f*(1-f)*2+3*f*f*4),top[1]+L*f) for f in np.linspace(0,1,20)]
            q2=[(top[0]+sw*f*f+(10*(1-f)+neck*f*(1-f)*2+3*f*f*4),top[1]+L*f) for f in np.linspace(1,0,20)]
            molfill(buf,M().poly(q+q2),a*thk)
            molfill(buf,M().ell(296,404,20,9),a*thk)
        thermo(buf,470,400,0.75-0.6*cool,a=a*sm((t-EV["real"]+0.2)/0.4))
    if pB>0:
        m=M().poly([(14,GY+3)]+[(x,lvl-2*math.sin(x/40)) for x in np.linspace(14,w-14,40)]+[(w-14,GY+3)])
        for k,(x,s) in enumerate(((150,1.2),(300,1.0),(420,1.1))):
            ink(buf,person_m(x,lvl+60*s,s,0.7+0.2*k,t),pB)
        molfill(buf,m,pB,[(x,lvl+10) for x in np.linspace(30,w-30,30)])
        cu=sm((t-EV["cleanup"]+0.2)/0.4)
        if cu>0:
            ink(buf,M().poly([(500,250),(530,240),(530,262)]),pB*cu); dm=M()
            for k in range(14):
                q=((t*1.6+k/14)%1); x=500-q*300; y=250+q*q*200; dm.line((x,y),(x-10,y+3),2)
            ink(buf,dm,pB*cu)
    def hd(d,t=t,pB=pB):
        head(d,"THE REAL",540,240,140,a=ap(t,EV["real"],EV["cooled"]),sc=pop(t,EV["real"]-0.1))
        head(d,"KILLER…",540,390,150,a=ap(t,EV["next"],EV["cooled"]),sc=pop(t,EV["next"]-0.1),col=cM)
        head(d,"IT COOLED",540,240,140,a=ap(t,EV["cooled"],EV["thick"]),sc=pop(t,EV["cooled"]-0.1))
        head(d,"THICK AS GLUE",540,240,130,a=ap(t,EV["thick"],EV["half"]),sc=pop(t,EV["thick"]-0.1),col=cM)
        clip(d,"4× thicker in the cold",560,700,40,a=ap(t,EV["glue"],EV["half"]))
        head(d,"½ OF VICTIMS",540,240,130,a=ap(t,EV["half"],EV["cleanup"]),sc=pop(t,EV["half"]-0.1))
        btag(d,"DIED STUCK",540,380,72,a=ap(t,EV["stuck"],EV["cleanup"]),sc=pop(t,EV["stuck"]-0.1))
        head(d,"CLEANUP: WEEKS",540,240,120,a=ap(t,EV["cleanup"],sc["e"]+1),sc=pop(t,EV["cleanup"]-0.1))
    hud.append(hd); return buf,hud
def s_end(t,sc):
    buf=PAGE.copy(); hud=[]
    pB=sm((t-EV["locals"]+0.3)/0.35)
    if pB<1:
        a=1-pB
        bomb(buf,130,400,a*sm((t-EV["anarch"]+0.2)/0.3),t)
        xk=sm((t-EV["court"]+0.1)/0.4)
        if xk>0:
            m=M(); dl(m,[(70,340),(190,460)],xk,9); dl(m,[(190,340),(70,460)],cl(xk*2-1),9); comp(buf,m,MOL,sh=0,rim=0,a=a)
        # cracked tank on the right
        ty=sm((t-EV["weak"]+0.3)/0.4)
        if ty>0:
            o=M().pline([(425,330),(437,370),(419,410),(441,460),(429,520)],3); outl(buf,M().rect(380,330,480,520),a=a*ty,th=1,fill=0.0); ink(buf,o,a*ty)
        gv=sm((t-EV["court"]+0.3)/0.3); sl=EV["weak"]
        ang=(0.7-0.7*sm((t-sl+0.15)/0.15)) if t<sl+0.3 else 0.25*sm((t-sl-0.3)/0.6)
        if gv>0: gavel(buf,250,562,ang,a*gv); ink(buf,M().rect(196,594,294,608),a*gv)
    if pB>0:
        wm=M().poly([(14,GY+3)]+[(x,480+4*math.sin(x/25+t*2)) for x in np.linspace(14,w-14,50)]+[(w-14,GY+3)])
        comp(buf,wm,(0.62,0.48,0.32),sh=0,rim=0,a=pB*0.85)
        lm=M()
        for k in range(5):
            y=500+k*28; lm.pline([(x,y+3*math.sin(x/20+t*2+k)) for x in np.linspace(30,w-30,60)],1.2)
        ink(buf,lm,0.6*pB)
        pier=M().rect(30,440,250,452)
        for x in range(40,250,40): pier.rect(x,452,x+6,520)
        ink(buf,pier,pB)
        smk=M()
        for k in range(4):
            x0=90+k*110; ph=(t*0.5+k*0.27)%1
            smk.pline([(x0+10*math.sin(q*8+t*2+k),470-ph*60-q*140) for q in np.linspace(0,1,30)],2)
        ink(buf,smk,pB*sm((t-EV["sweet"]+0.3)/0.5)*0.8,col=MOL)
        sun(buf,440,250,pB*sm((t-EV["warmday"]+0.2)/0.4),t)
    def hd(d,t=t,pB=pB):
        clip(d,"THE COMPANY:",540,220,44,a=ap(t,EV["company"],EV["court"]))
        head(d,"“ANARCHISTS!”",540,330,120,a=ap(t,EV["anarch"],EV["court"]),sc=pop(t,EV["anarch"]-0.1))
        clip(d,"THE COURT:",540,220,44,a=ap(t,EV["court"],EV["locals"]),ang=-2)
        head(d,"TANK TOO WEAK",540,330,120,a=ap(t,EV["weak"]-0.1,EV["locals"]),sc=pop(t,EV["weak"]-0.15),col=cM)
        deck(d,"victims sued — and won",540,1300,38,a=ap(t,EV["weak"]+0.3,EV["locals"]))
        head(d,"SMELLED SWEET",540,240,128,a=ap(t,EV["sweet"]-0.1,EV["allb"]),sc=pop(t,EV["sweet"]-0.15),col=cM)
        deck(d,"FOR DECADES",540,370,56,a=ap(t,EV["decades"],EV["allb"]))
        deck(d,"BOSTON HARBOR",540,1300,40,a=ap(t,EV["harbor"],EV["allb"]))
        deck(d,"ON A WARM DAY IN",540,240,52,a=ap(t,EV["warmday"]-0.1,sc["e"]+1))
        head(d,"1919",540,370,170,a=ap(t,EV["y1919"]-0.05,sc["e"]+1),sc=pop(t,EV["y1919"]-0.1),col=cM)
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,tank=s_tank,wave=s_wave,stuck=s_stuck,end=s_end)
BAND=(1-0.40*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.22*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.010,(h,w,1)).astype(np.float32) for i in range(6)]
TR=0.30; TOTAL=B.TOTAL; LOOPD=0.6
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
_xs=np.arange(w,dtype=np.float32)
def _drip(seed,t):
    g=np.random.default_rng(seed); d=np.zeros(w,np.float32)
    for k in range(9):
        c=g.uniform(0,w); wd=g.uniform(8,22); L=g.uniform(30,90)
        d+=L*np.exp(-((_xs-c)/wd)**2)
    return d+8*np.sin(_xs/41+t*3)
_GL=np.clip(cv2.GaussianBlur(np.random.default_rng(5).normal(0,1,(h,w)).astype(np.float32),(0,0),sigmaX=2,sigmaY=40)*1.5,0,1)
def pour(b1,b2,u,t):
    """molasses sheet pours down over b1, then slides off revealing b2"""
    F=sm(u/0.6)*(h+260)-130; Tt=sm((u-0.4)/0.6)*(h+260)-130
    fr=F+_drip(3,t); tl=Tt+10*np.sin(_xs/37+t*2)-30
    Y=yy
    inb=(Y<fr[None,:])&(Y>tl[None,:])
    out=np.where((Y<=tl[None,:])[...,None],b2,b1)
    sheet=np.empty_like(b1); sheet[:]=MOL
    sheet+=(np.array(MOLH,np.float32)-np.array(MOL,np.float32))*(_GL*0.45)[...,None]
    edge=np.exp(-((fr[None,:]-Y)/10)**2)*0.5; sheet+=edge[...,None]*(np.array(MOLH,np.float32)-sheet)
    sheet*=np.clip(1-0.25*((Y-tl[None,:])/60).clip(0,1),0.6,1)[...,None] if False else 1
    out=np.where(inb[...,None],sheet,out)
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
        buf=pour(b1,b2,u,t); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
        if B2 is SC[0] and A_ is not SC[0] and u>0.5: hk=1.0 if u>0.85 else hk
    buf=np.clip(buf,0,1.2)*PT*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
