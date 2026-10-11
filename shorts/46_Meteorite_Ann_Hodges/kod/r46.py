import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid46")
for p in ["/home/claude/vid46","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
import drawkit as K
from drawkit import ink, outl, hatch, wash, glow, part, dl, circ_pts, dashl, dim, rotp
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= palette (1950s atomic-age mid-century illustration, offset-print misregistration) =================
CREAM=(0.96,0.92,0.82); TURQ=(0.25,0.66,0.64); TURQD=(0.14,0.44,0.46); CORAL=(0.94,0.44,0.36); MUST=(0.93,0.72,0.24)
CHAR=(0.17,0.17,0.21); PINK=(0.95,0.72,0.68); WOOD=(0.58,0.36,0.20); SKY=(0.62,0.83,0.84); PLUM=(0.45,0.25,0.38); WHITE=(1,0.98,0.94)
K.INK=CHAR
cC=(44,44,54); cCo=(238,110,90); cT=(62,166,160); cM=(236,184,62); cCr=(246,236,212)
_TF={}
def ttl(d,s,x,y,fs=120,a=1.0,sc=1.0,col=cC,ang=0):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc)
    if n not in _TF: _TF[n]=ImageFont.truetype(P.FD+"Boldonse-Regular.ttf",n)
    f=_TF[n]
    while f.getlength(s)>1000 and n>20:
        n-=6; _TF.setdefault(n,ImageFont.truetype(P.FD+"Boldonse-Regular.ttf",n)); f=_TF[n]
    off=max(3,n//28)
    d.text((x+off,y+off),s,font=f,fill=(44,44,54,int(70*a)),anchor="mm")
    d.text((x,y),s,font=f,fill=col+(int(255*a),),anchor="mm")
def tag(d,s,x,y,fs=54,a=1.0,sc=1.0,ang=-3,fg=cCr,bg=cCo): card(d,s,x,y,fs=fs,a=a,fg=fg,bg=bg,fn="BricolageGrotesque-Bold",torn=False,ang=ang,sc=sc,pad=(26,12))
def ttag(d,s,x,y,fs=54,a=1.0,sc=1.0,ang=2): tag(d,s,x,y,fs,a,sc,ang,fg=cCr,bg=cT)
def mtag(d,s,x,y,fs=54,a=1.0,sc=1.0,ang=-2): tag(d,s,x,y,fs,a,sc,ang,fg=cC,bg=cM)
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
def flat(buf,m,col,a=1.0,mis=(3,2)):
    """flat print colour with slight offset-print misregistration shadow"""
    if a<=0 or m.x1<=m.x0: return
    comp(buf,m,lerpc(col,CHAR,0.55),sh=0,rim=0,a=0.22*a,ox=mis[0],oy=mis[1]); comp(buf,m,col,sh=0,rim=0,a=a)
# ================= background =================
_g=np.random.default_rng(54)
PAGE=np.zeros((h,w,3),np.float32); PAGE[:]=CREAM
_mot=cv2.resize(_g.normal(0,1,(12,8)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC); _mot/=_mot.std(); PAGE*=(1-0.025*_mot)[...,None]
_dots=((xx%9<2.2)&(yy%9<2.2)).astype(np.float32)*0.04; PAGE-=_dots[...,None]*0.6
def boomerang(m,cx,cy,s,ang):
    pts=[(-1,0),(-0.2,-0.35),(1,-0.1),(0.1,-0.05),(-0.15,0.1)]
    return m.poly(rotp([(cx+x*s,cy+y*s) for x,y in pts],ang,cx,cy))
_bm=M()
for k in range(14): boomerang(_bm,_g.uniform(30,510),_g.uniform(60,700),_g.uniform(26,46),_g.uniform(0,6.28))
_ba=_bm.f()[...,None]*0.07; PAGE=PAGE*(1-_ba)+np.array(TURQ,np.float32)*_ba
def sparkle(m,cx,cy,r,n=4,ri=0.18,rot=0.0):
    return m.poly([(cx+(r if k%2==0 else r*ri)*math.cos(rot+k*math.pi/n),cy+(r if k%2==0 else r*ri)*math.sin(rot+k*math.pi/n)) for k in range(2*n)])
_sm=M()
for k in range(9): sparkle(_sm,_g.uniform(30,510),_g.uniform(60,700),_g.uniform(6,12))
_sa=_sm.f()[...,None]*0.18; PAGE=PAGE*(1-_sa)+np.array(MUST,np.float32)*_sa
# ================= objects =================
def burst(buf,cx,cy,r,col=MUST,a=1.0,n=12,rot=0.0,inner=CORAL):
    if a<=0 or r<=1: return
    flat(buf,M().poly([(cx+(r if k%2==0 else r*0.55)*math.cos(rot+k*math.pi/n),cy+(r if k%2==0 else r*0.55)*math.sin(rot+k*math.pi/n)) for k in range(2*n)]),col,a)
    flat(buf,M().poly([(cx+(r*0.6 if k%2==0 else r*0.32)*math.cos(-rot+k*math.pi/n),cy+(r*0.6 if k%2==0 else r*0.32)*math.sin(-rot+k*math.pi/n)) for k in range(2*n)]),inner,a)
_rk=np.random.default_rng(3)
ROCK=[(math.cos(q)*(1+0.18*_rk.uniform(-1,1)),math.sin(q)*(0.8+0.15*_rk.uniform(-1,1))) for q in np.linspace(0,2*math.pi,11)[:-1]]
def rock(buf,cx,cy,s,a=1.0,rot=0.0,tail=0.0,tdir=(-0.6,-0.8)):
    if a<=0: return
    if tail>0:
        L=tail; tx,ty=tdir; px,py=-ty,tx
        for col,wf,lf in ((MUST,1.0,1.0),(CORAL,0.65,0.75),(WHITE,0.3,0.45)):
            tm=M().poly([(cx+px*s*wf,cy+py*s*wf),(cx+tx*L*lf,cy+ty*L*lf),(cx-px*s*wf,cy-py*s*wf)]); flat(buf,tm,col,a*0.95,(0,0))
    m=M().poly(rotp([(cx+x*s,cy+y*s) for x,y in ROCK],rot,cx,cy)); flat(buf,m,CHAR,a)
    for dx,dy,r in ((-0.3,-0.2,0.18),(0.25,0.15,0.13),(0.1,-0.35,0.1)):
        q=rotp([(cx+dx*s,cy+dy*s)],rot,cx,cy)[0]; comp(buf,M().circ(q[0],q[1],r*s),(0.30,0.30,0.34),sh=0,rim=0,a=a)
def couch(buf,x,y,a=1.0):
    flat(buf,M().rect(x,y-60,x+300,y).rect(x-14,y-90,x+16,y).rect(x+284,y-90,x+314,y),CORAL,a)
    flat(buf,M().rect(x+10,y-110,x+290,y-55),lerpc(CORAL,CHAR,0.12),a)
    ink(buf,M().rect(x,y,x+8,y+22).rect(x+292,y,x+300,y+22),a)
    for k in (1,2): ink(buf,M().line((x+k*100,y-108),(x+k*100,y-60),1.5),0.4*a)
def sleeper(buf,x,y,a=1.0,t=0.0,awake=0.0):
    hy=y-80-10*awake
    flat(buf,M().ell(x+150,y-70,120,22),TURQ,a)
    flat(buf,M().circ(x+20,hy,20),PINK,a); flat(buf,M().ell(x+4,hy-8,16,14),PLUM,a); flat(buf,M().circ(x-8,hy-12,8),PLUM,a)
    if awake<0.5:
        for k in range(3):
            ph=(t*0.6+k*0.33)%1; zx=x+40+ph*40; zy=hy-30-ph*60
            card_z.append((zx,zy,1-ph))
    else:
        ink(buf,M().circ(x+16,hy-3,2.5).circ(x+28,hy-3,2.5),a); ink(buf,M().pline(circ_pts(x+22,hy+8,6,4,0,math.pi,10),1.5),a)
card_z=[]
def radio(buf,x,y,a=1.0,shake=0.0):
    ox=shake*3*math.sin(y+shake*80)
    flat(buf,M().rect(x+ox,y-130,x+90+ox,y),WOOD,a)
    flat(buf,M().rect(x+12+ox,y-118,x+78+ox,y-70),CREAM,a)
    gm=M()
    for k in range(5): gm.line((x+16+ox,y-112+k*9),(x+74+ox,y-112+k*9),1.5)
    ink(buf,gm,0.6*a); ink(buf,M().circ(x+30+ox,y-40,8).circ(x+60+ox,y-40,8),a)
    ink(buf,M().rect(x+8+ox,y,x+14+ox,y+20).rect(x+76+ox,y,x+82+ox,y+20),a)
CEIL=230
def room(buf,a=1.0,hole=0.0,hx=330):
    flat(buf,M().rect(0,0,w,CEIL),(0.86,0.80,0.68),a,(0,0)); ink(buf,M().rect(0,CEIL-2,w,CEIL+3),a)
    flat(buf,M().rect(0,560,w,h),lerpc(TURQD,CHAR,0.25),a,(0,0)); ink(buf,M().rect(0,557,w,561),a)
    for k in range(6): ink(buf,M().line((k*100,561),(k*100-60,700),1.2),0.25*a)
    flat(buf,M().rect(60,280,180,400),SKY,a); ink(buf,M().rect(60,280,180,284).rect(60,396,180,400).rect(60,280,64,400).rect(176,280,180,400).rect(118,280,122,400),a)
    if hole>0:
        hm=M().poly([(hx-38*hole,CEIL),(hx-20*hole,CEIL-32),(hx+10*hole,CEIL-26),(hx+40*hole,CEIL-38),(hx+34*hole,CEIL+2)]); comp(buf,hm,(0.55,0.75,0.82),sh=0,rim=0,a=a)
        dm=M()
        for k in range(8): dm.rect(hx-30+k*9,CEIL+((k*37)%40)*hole*2,hx-25+k*9,CEIL+5+((k*37)%40)*hole*2)
        ink(buf,dm,0.6*a*hole)
def house(buf,x,y,a=1.0,hole=0.0):
    flat(buf,M().rect(x,y-110,x+260,y),CREAM,a); outl(buf,M().rect(x,y-110,x+260,y),a=a,th=1,fill=0)
    flat(buf,M().poly([(x-20,y-108),(x+130,y-170),(x+280,y-108)]),CORAL,a)
    flat(buf,M().rect(x+30,y-80,x+90,y-30),SKY,a); flat(buf,M().rect(x+170,y-80,x+210,y),TURQ,a)
    flat(buf,M().rect(x+200,y-200,x+226,y-140),WOOD,a)
    if hole>0: ink(buf,M().ell(x+140,y-150,14*hole,8*hole),a)
def person(buf,x,y,s,col,a=1.0,hat=False,arm=0.0):
    flat(buf,M().circ(x,y-120*s,16*s),PINK,a)
    flat(buf,M().poly([(x-22*s,y-102*s),(x+22*s,y-102*s),(x+28*s,y-40*s),(x-28*s,y-40*s)]),col,a)
    ink(buf,M().line((x-10*s,y-40*s),(x-12*s,y),9*s).line((x+10*s,y-40*s),(x+12*s,y),9*s),a)
    ink(buf,M().line((x+20*s,y-96*s),(x+20*s+math.cos(arm)*40*s,y-96*s+math.sin(arm)*40*s),7*s),a)
    if hat: flat(buf,M().ell(x,y-134*s,30*s,7*s).ell(x,y-142*s,16*s,10*s),MUST,a)
def jet(buf,x,y,s,a=1.0):
    m=M().poly([(x-60*s,y),(x+60*s,y-6*s),(x+70*s,y),(x+60*s,y+6*s)]).poly([(x-10*s,y),(x+20*s,y-40*s),(x+30*s,y-40*s),(x+20*s,y)]).poly([(x-10*s,y),(x+20*s,y+40*s),(x+30*s,y+40*s),(x+20*s,y)]).poly([(x-60*s,y),(x-50*s,y-22*s),(x-40*s,y-22*s),(x-40*s,y)])
    flat(buf,m,(0.70,0.72,0.74),a); ink(buf,M().circ(x+8*s,y-22*s,6*s),a,col=(0.15,0.3,0.6))
def car(buf,x,y,a=1.0):
    flat(buf,M().poly([(x,y-20),(x+20,y-46),(x+90,y-46),(x+120,y-24),(x+150,y-20),(x+150,y),(x,y)]),TURQ,a)
    flat(buf,M().poly([(x+28,y-42),(x+86,y-42),(x+104,y-24),(x+24,y-24)]),SKY,a); ink(buf,M().circ(x+32,y,13).circ(x+118,y,13),a)
def barn(buf,x,y,a=1.0):
    flat(buf,M().poly([(x,y),(x,y-70),(x+60,y-110),(x+120,y-70),(x+120,y)]),CORAL,a); flat(buf,M().rect(x+40,y-50,x+80,y),CREAM,a)
    ink(buf,M().line((x+40,y-50),(x+80,y),2).line((x+80,y-50),(x+40,y),2),a)
def door(buf,x,y,a=1.0,ang=0.0):
    flat(buf,M().rect(x-6,y-300,x+156,y),WOOD,a)
    dm=M().poly(rotp([(x,y-294),(x+150*math.cos(ang),y-294),(x+150*math.cos(ang),y),(x,y)],0,x,y)); flat(buf,dm,MUST,a)
    ink(buf,M().circ(x+130*math.cos(ang),y-150,6),a)
def case(buf,x,y,a=1.0):
    flat(buf,M().rect(x-110,y-40,x+110,y+120),WOOD,a)
    outl(buf,M().rect(x-100,y-200,x+100,y-40),a=a,th=2,fill=0.25,col=CHAR,fcol=SKY)
    ink(buf,M().line((x-80,y-190),(x-40,y-150),2).line((x-60,y-190),(x-30,y-160),1.5),0.5*a,col=WHITE)
# ================= scenes =================
def s_hook(t,sc):
    global card_z
    card_z=[]
    buf=PAGE.copy(); hud=[]
    tt=max(t,-1.0)
    th=0.95  # impact time on the couch
    k=cl((tt+0.6)/(th+0.6))
    room(buf,1.0,hole=sm((tt-0.15+0.6)/0.2) if tt>-0.45 else 0.0)
    radio(buf,420,550,1.0,shake=math.exp(-max(0,tt-th)*4)*(tt>th))
    couch(buf,90,552,1.0)
    sleeper(buf,110,500,1.0,tt,awake=sm((tt-th-0.3)/0.4))
    if tt<th:
        rx,ry=330-80*(1-k)*0+(-20)*k, -60+(470+60)*ein(k)**0.7
        rx=330+(-60)*k
        rock(buf,rx,ry,26,1.0,rot=tt*6,tail=140,tdir=(0.25,-1.0))
    else:
        rock(buf,268,520,22,1.0,rot=0.3)
        b=math.exp(-(tt-th)*2.2); burst(buf,268,505,30+70*(1-b),MUST,a=b,rot=tt*0.5)
    def hd(d,t=t):
        k0=1.0 if t<0.4 else ap(t,-1,EV["survived"])
        ttl(d,"HIT BY A",540,230,110,a=k0)
        ttl(d,"METEORITE",540,380,150,a=k0,col=cCo,sc=1.0 if t<th else 1+0.08*math.exp(-(t-th)*5))
        for zx,zy,za in card_z: card(d,"z",zx*2,zy*2,fs=40,a=za*0.8*(1-sm((t-th)/0.2)),fg=cC,bg=None,fn="BricolageGrotesque-Bold",torn=False,pad=(2,2))
        mtag(d,"SHE SURVIVED",540,250,76,a=ap(t,EV["survived"],sc["e"]+1),sc=pop(t,EV["survived"]-0.1))
        ttl(d,"BUT THEN…",540,400,110,a=ap(t,EV["strangest"],sc["e"]+1),sc=pop(t,EV["strangest"]-0.1),col=cT)
    hud.append(hd); return buf,hud
def s_strike(t,sc):
    global card_z
    card_z=[]
    buf=PAGE.copy(); hud=[]
    pN=sm((t-EV["ann"]+0.3)/0.35); pF=sm((t-EV["across"]+0.3)/0.35); pC=sm((t-EV["stone"]+0.3)/0.35); pW=sm((t-EV["wakes"]+0.3)/0.35)
    a1=1-pN; a2=pN*(1-pF); a3=pF*(1-pC); a4=pC*(1-pW); a5=pW
    if a1>0:
        # postcard of Sylacauga
        flat(buf,M().rect(60,200,480,520),SKY,a1); flat(buf,M().poly([(60,520),(60,430),(200,380),(330,420),(480,370),(480,520)]),TURQ,a1)
        house(buf,150,500,a1); outl(buf,M().rect(60,200,480,520),a=a1,th=3,fill=0)
        sparkle_m=M(); sparkle(sparkle_m,430,250,24,4,0.2,t); flat(buf,sparkle_m,MUST,a1)
    if a2>0:
        room(buf,a2); couch(buf,90,552,a2); sleeper(buf,110,500,a2,t); radio(buf,420,550,a2)
    if a3>0:
        flat(buf,M().rect(0,0,w,520),SKY,a3,(0,0)); flat(buf,M().poly([(0,520),(0,470),(160,440),(300,470),(540,430),(540,560),(0,560)]),TURQ,a3)
        house(buf,150,540,a3); flat(buf,M().rect(0,555,w,h),lerpc(TURQD,CHAR,0.25),a3,(0,0))
        k=cl((t-EV["across"]+0.2)/1.6)
        rock(buf,-40+540*k,120+180*k,14,a3,rot=t*5,tail=160,tdir=(-0.94,-0.34))
        b=sm((t-EV["boom"]+0.1)/0.2)*math.exp(-max(0,t-EV["boom"])*1.5)
        if b>0.01: burst(buf,300,250,40+90*b,MUST,a=a3*min(1,b*2),rot=t)
    if a4>0:
        # cut-away diagram: roof -> ceiling -> radio -> hip
        flat(buf,M().poly([(20,190),(270,90),(520,190)]),CORAL,a4); flat(buf,M().rect(40,190,500,620),CREAM,a4); outl(buf,M().rect(40,190,500,620),a=a4,th=2,fill=0)
        ink(buf,M().rect(40,300,500,306),a4)
        radio(buf,370,600,a4); couch(buf,80,600,a4)
        flat(buf,M().ell(220,532,110,20),TURQ,a4); flat(buf,M().circ(110,512,18),PINK,a4); flat(buf,M().ell(96,504,14,12),PLUM,a4)
        P_=[(300,40),(300,140),(300,303),(410,470),(230,525)]; ts=[EV["stone"],EV["stone"]+0.9,EV["ceiling"],EV["radio"],EV["hip"]]
        if t<ts[1]: q=(300,40+100*cl((t-ts[0])/0.9)); seg=0
        else:
            q=P_[-1]
            for j in range(1,len(ts)-1):
                if t<ts[j+1]:
                    f=cl((t-ts[j])/(ts[j+1]-ts[j]))**0.6; q=(P_[j][0]+(P_[j+1][0]-P_[j][0])*f,P_[j][1]+(P_[j+1][1]-P_[j][1])*f); break
        pm=M()
        pts=[P_[0]]
        for j in range(1,len(P_)):
            if t>ts[j]-0.01: pts.append(P_[j])
            else: break
        pts.append(q)
        for a_,b_ in zip(pts,pts[1:]): dashl(pm,a_,b_,8,6,2.5)
        ink(buf,pm,a4*0.8,col=CORAL)
        for j,e in ((2,"ceiling"),(3,"radio"),(4,"hip")):
            bb=math.exp(-max(0,t-EV[e])*3)*(t>EV[e]);
            if bb>0.02: burst(buf,P_[j][0],P_[j][1],18+30*bb,MUST,a=a4*bb,n=8)
        rock(buf,q[0],q[1],16,a4,rot=t*4)
    if a5>0:
        room(buf,a5); couch(buf,90,552,a5); radio(buf,420,550,a5); sleeper(buf,110,500,a5,t,awake=1.0)
        rock(buf,300,600,20,a5,rot=0.4); burst(buf,300,600,40,MUST,a=0.35*a5,n=10,rot=t*0.3)
        bm=M().ell(230,486,26,16); comp(buf,bm,(0.42,0.28,0.50),sh=0,rim=0,a=0.8*a5*sm((t-EV["bruise"]+0.1)/0.4))
    def hd(d,t=t,a1=a1,a3=a3,a4=a4,a5=a5):
        ttag(d,"NOV. 30, 1954",540,250,70,a=ap(t,EV["nov"],EV["ann"]),sc=pop(t,EV["nov"]-0.1))
        ttl(d,"SYLACAUGA, ALABAMA",540,1170,64,a=ap(t,EV["syl"],EV["ann"]),sc=pop(t,EV["syl"]-0.1),col=cC)
        tag(d,"ANN HODGES",540,250,76,a=ap(t,EV["ann"],EV["across"]),sc=pop(t,EV["ann"]-0.1))
        ttl(d,"FIREBALL!",540,250,120,a=ap(t,EV["fireball"],EV["boom"]),sc=pop(t,EV["fireball"]-0.1),col=cCo)
        ttl(d,"BOOM!",540,250,170,a=ap(t,EV["boom"],EV["stone"]),sc=pop(t,EV["boom"]-0.1),col=cM,ang=-4)
        mtag(d,"8.5 POUNDS",820,170,60,a=ap(t,EV["stone"],EV["wakes"]),sc=pop(t,EV["stone"]-0.1))
        for n_,(e,x,y) in enumerate((("ceiling",680,560),("radio",920,820),("hip",380,960))):
            ttag(d,f"{n_+1}. {e.upper()}",x,y,40,a=ap(t,EV[e],EV["wakes"]),sc=pop(t,EV[e]-0.1))
        tag(d,"A HUGE BRUISE",540,250,72,a=ap(t,EV["bruise"],sc["e"]+1),sc=pop(t,EV["bruise"]-0.1))
        mtag(d,"+ A METEORITE",620,1290,56,a=ap(t,EV["floor"],sc["e"]+1),sc=pop(t,EV["floor"]-0.1))
    hud.append(hd); return buf,hud
def s_fight(t,sc):
    buf=PAGE.copy(); hud=[]
    pL=sm((t-EV["comes"]+0.3)/0.35); pP=sm((t-EV["public"]+0.3)/0.35)
    a1=1-pL; a2=pL*(1-pP); a3=pP
    if a1>0:
        rk=(270,380)
        k=sm((t-EV["airforce"]+0.1)/1.0)
        if t<EV["airforce"]:
            person(buf,150,600,1.4,(0.20,0.28,0.50),a1,hat=False,arm=-0.4); rock(buf,215,450,18,a1)
            ink(buf,M().ell(150,415,26,8).rect(128,400,172,415),a1,col=(0.15,0.2,0.4))
        jx=-120+k*760; jet(buf,jx,300-k*120,1.3,a1*sm((t-EV["airforce"]+0.4)/0.3))
        if k>0: rock(buf,jx-30,330-k*120,12,a1*(1 if k<0.95 else 0))
    if a2>0:
        # tug of war over the rock
        rock(buf,270,430,30,a2,rot=math.sin(t*3)*0.1)
        sway=12*math.sin(t*2.5)
        ink(buf,M().line((80+sway,430),(470+sway,430),4),a2,col=WOOD)
        person(buf,80+sway,620,1.3,PLUM,a2,arm=-0.2)
        person(buf,470+sway,620,1.3,TURQ,a2,arm=math.pi+0.2)
        flat(buf,M().circ(462+sway,620-128*1.3,10),PLUM,a2)
        flat(buf,M().poly([(60+sway,620-150*1.3),(80+sway,620-185*1.3),(100+sway,620-150*1.3)]),MUST,a2*0.0)
        flat(buf,M().rect(48+sway,620-170*1.3,112+sway,620-160*1.3),CHAR,a2*0.0)
    if a3>0:
        g=np.random.default_rng(8)
        for k in range(12):
            x=50+k*40+g.uniform(-8,8); y=620+g.uniform(0,20); col=[TURQ,CORAL,MUST,PLUM][k%4]
            person(buf,x,y,0.7,col,a3,arm=-1.2-0.3*math.sin(t*6+k))
        rk=(270,330+18*math.sin(t*2)); rock(buf,rk[0],rk[1],30,a3); burst(buf,270,330,70,MUST,a=0.4*a3,rot=t*0.4,n=10)
    def hd(d,t=t,a1=a1,a2=a2,a3=a3):
        tag(d,"OFFICIALS TAKE IT",540,250,64,a=ap(t,EV["officials"],EV["airforce"]),sc=pop(t,EV["officials"]-0.1))
        ttag(d,"THEN THE U.S. AIR FORCE",540,250,58,a=ap(t,EV["airforce"],EV["comes"]),sc=pop(t,EV["airforce"]-0.1))
        ttl(d,"SUED!",540,250,150,a=ap(t,EV["sues"],EV["public"]),sc=pop(t,EV["sues"]-0.1),col=cCo,ang=-3)
        mtag(d,"THE LANDLADY",230,1140,46,a=ap(t,EV["landlady"],EV["public"]))
        ttag(d,"ANN",860,1140,52,a=ap(t,EV["landlady"]+0.3,EV["public"]))
        card(d,"“Meteorites belong to the landowner”",540,420,40,a=ap(t,EV["landowner"]-0.4,EV["public"]),fg=cC,bg=cCr,fn="BricolageGrotesque-Bold",torn=True,pad=(22,12),ang=1)
        tag(d,"THE PUBLIC SIDES WITH ANN",540,250,52,a=ap(t,EV["public"],EV["keeps"]),sc=pop(t,EV["public"]-0.1))
        ttl(d,"SHE KEEPS IT",540,250,110,a=ap(t,EV["keeps"],sc["e"]+1),sc=pop(t,EV["keeps"]-0.1),col=cT)
    hud.append(hd); return buf,hud
def s_end(t,sc):
    global card_z
    card_z=[]
    buf=PAGE.copy(); hud=[]
    pA=sm((t-EV["nobuyer"]+0.3)/0.35); pR=sm((t-EV["allb"]+0.3)/0.35)
    a1=1-pA; a2=pA*(1-pR); a3=pR
    if a1>0:
        flat(buf,M().rect(0,0,w,560),SKY,a1,(0,0)); flat(buf,M().poly([(0,560),(0,500),(200,470),(540,510),(540,560)]),TURQ,a1)
        flat(buf,M().poly([(200,700),(250,560),(290,560),(420,700)]),(0.80,0.66,0.48),a1,(0,0)); flat(buf,M().rect(0,560,w,h),lerpc(TURQ,CHAR,0.2),a1,(0,0)); flat(buf,M().poly([(170,700),(250,560),(290,560),(430,700)]),(0.80,0.66,0.48),a1,(0,0))
        fx=120+min(t-sc["s"],2)*30
        person(buf,fx,630,1.1,(0.30,0.45,0.70),a1,hat=True,arm=0.6 if t<EV["sold"] else -1.0)
        if t<EV["sold"]: rock(buf,fx+60,650,12,a1)
        sd=sm((t-EV["sold"]+0.1)/0.3)
        if sd>0:
            dm=M(); dm.circ(fx+80,470,30); flat(buf,dm,MUST,a1*sd)
        barn(buf,330,500,a1*sm((t-EV["farm"]+0.1)/0.3)); car(buf,360,640,a1*sm((t-EV["car"]+0.1)/0.3))
    if a2>0:
        dk=sm((t-EV["doorstop"]+0.2)/0.4); mk=sm((t-EV["museum"]+0.2)/0.4)
        if mk<1:
            door(buf,190,600,a2*(1-mk),ang=0.6); rock(buf,200+150*math.cos(0.6)+20,585,20,a2*(1-mk)*dk)
            flat(buf,M().rect(0,600,w,h),lerpc(TURQD,CHAR,0.25),a2*(1-mk),(0,0))
        if mk>0:
            case(buf,270,560,a2*mk); rock(buf,270,470,30,a2*mk)
    if a3>0:
        room(buf,a3); radio(buf,420,550,a3); couch(buf,90,552,a3); sleeper(buf,110,500,a3,t)
    def hd(d,t=t,a1=a1,a2=a2,a3=a3):
        mtag(d,"A SECOND PIECE",540,250,64,a=ap(t,EV["second"],EV["sold"]),sc=pop(t,EV["second"]-0.1))
        tag(d,"SOLD!",540,250,90,a=ap(t,EV["sold"],EV["nobuyer"]+0.0),sc=pop(t,EV["sold"]-0.1))
        card(d,"$",(120+min(t-ev.S("end")["s"],2)*30+80)*2,940,fs=60,a=a1*sm((t-EV["sold"]+0.1)/0.3),fg=cC,bg=None,fn="Boldonse-Regular",torn=False,pad=(2,2))
        ttag(d,"A FARM + A CAR",540,390,58,a=ap(t,EV["farm"],EV["nobuyer"]),sc=pop(t,EV["farm"]-0.1))
        tag(d,"NO BUYER",540,250,80,a=ap(t,EV["nobuyer"],EV["doorstop"]),sc=pop(t,EV["nobuyer"]-0.1))
        ttl(d,"A DOORSTOP",540,250,120,a=ap(t,EV["doorstop"],EV["museum"]),sc=pop(t,EV["doorstop"]-0.1),col=cCo)
        ttag(d,"ALABAMA MUSEUM OF NATURAL HISTORY",540,1210,40,a=ap(t,EV["museum"],EV["allb"]))
        ttl(d,"A MUSEUM PIECE",540,250,96,a=ap(t,EV["museum"],EV["allb"]),sc=pop(t,EV["museum"]-0.1),col=cT)
        ttl(d,"ONE QUIET AFTERNOON",540,250,74,a=ap(t,EV["quiet"],sc["e"]+1),sc=pop(t,EV["quiet"]-0.1))
        for zx,zy,za in card_z: card(d,"z",zx*2,zy*2,fs=40,a=za*0.8*a3,fg=cC,bg=None,fn="BricolageGrotesque-Bold",torn=False,pad=(2,2))
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,strike=s_strike,fight=s_fight,end=s_end)
BAND=(1-0.40*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.20*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.010,(h,w,1)).astype(np.float32) for i in range(6)]
TR=0.30; TOTAL=B.TOTAL; LOOPD=0.6
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
_ang=np.arctan2(yy-480,xx-270); _dist=np.hypot(xx-270,yy-480)
def starwipe(b1,b2,u,rot):
    """atomic-age starburst iris: a 12-point star grows from the centre revealing b2, rimmed with mustard & coral"""
    R=(sm(u)*1.1)*1150
    rr=R*(0.62+0.38*np.abs(np.cos((_ang+rot)*6))**3)
    m=(_dist<rr)[...,None]; out=np.where(m,b2,b1)
    edge=((_dist>=rr)&(_dist<rr+16))[...,None]; edge2=((_dist>=rr+16)&(_dist<rr+28))[...,None]
    out=np.where(edge,np.array(MUST,np.float32),out); out=np.where(edge2,np.array(CORAL,np.float32),out)
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
        buf=starwipe(b1,b2,u,t*0.8); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    buf=np.clip(buf,0,1.2)*PT*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
