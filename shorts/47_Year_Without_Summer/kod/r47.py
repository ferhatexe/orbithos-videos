import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid47")
for p in ["/home/claude/vid47","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
import drawkit as K
from drawkit import ink, outl, wash, glow, part, dl, circ_pts, rotp
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= palette (Romantic-era oil painting, Turner-like light) =================
UMBER=(0.16,0.11,0.08); OCHRE=(0.80,0.58,0.26); GOLDL=(1.0,0.86,0.52); VERM=(0.82,0.26,0.12); MIST=(0.70,0.74,0.76); SNOW=(0.94,0.95,0.97)
SLATE=(0.30,0.34,0.40); NIGHT=(0.07,0.08,0.13); LAVA=(1.0,0.45,0.10); ASH=(0.45,0.43,0.42); MOSS=(0.30,0.38,0.22)
K.INK=UMBER
cG=(232,198,122); cD=(32,24,20); cCream=(246,236,214); cR=(200,64,36)
_IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(P.FD+n+".ttf",s)
    return _IF[k]
def ttl(d,s,x,y,fs=120,a=1.0,sc=1.0,col=cCream,font="InstrumentSerif-Italic"):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f(font,n)
    while f.getlength(s)>1000 and n>20: n-=6; f=_f(font,n)
    d.text((x+4,y+5),s,font=f,fill=(10,6,4,int(150*a)),anchor="mm"); d.text((x,y),s,font=f,fill=col+(int(255*a),),anchor="mm",stroke_width=2,stroke_fill=(30,20,14,int(200*a)))
def plaque(d,s,x,y,fs=46,a=1.0,sc=1.0,ang=0,fg=cG,bg=cD): card(d,s,x,y,fs=fs,a=a,fg=fg,bg=bg,fn="Lora-Italic",torn=False,ang=ang,sc=sc,pad=(30,12))
def rplaque(d,s,x,y,fs=50,a=1.0,sc=1.0,ang=-2): plaque(d,s,x,y,fs,a,sc,ang,fg=cCream,bg=(150,40,22))
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= painterly texture =================
_g=np.random.default_rng(1816)
def _aniso(sx,sy,seed):
    a=cv2.GaussianBlur(np.random.default_rng(seed).normal(0,1,(h,w)).astype(np.float32),(0,0),sigmaX=sx,sigmaY=sy); return a/a.std()
BR1=_aniso(7,1.1,1); BR2=_aniso(1.2,6,2); BRD=cv2.warpAffine(_aniso(8,1.0,3),cv2.getRotationMatrix2D((w/2,h/2),35,1.25),(w,h),borderMode=cv2.BORDER_REFLECT)
_reg=cv2.resize(np.random.default_rng(4).random((10,6)).astype(np.float32),(w,h),interpolation=cv2.INTER_LINEAR)
BRUSH=np.where(_reg>0.5,BR1,BR2)*0.7+BRD*0.3
WEAVE=(1+0.025*(np.sin(xx*math.pi/1.5)*np.sin(yy*math.pi/1.5)))[...,None].astype(np.float32)
_cj=cv2.GaussianBlur(np.random.default_rng(5).normal(0,1,(h,w,3)).astype(np.float32),(0,0),9); _cj/=_cj.std()
_cjl=cv2.GaussianBlur(np.random.default_rng(6).normal(0,1,(h,w)).astype(np.float32),(0,0),5); _cjl/=_cjl.std()
def paintify(buf):
    sm_=cv2.blur(buf,(9,1))*0.5+cv2.blur(buf,(1,7))*0.5
    k=np.where((_reg>0.5)[...,None],0.55,0.35)
    b=buf*(1-k)+sm_*k
    b=b*(1+0.045*BRUSH)[...,None]+0.006*_cj+0.012*_cjl[...,None]
    return b*WEAVE
# ================= scene helpers =================
def vgrad(stops):
    b=np.zeros((h,w,3),np.float32); grad(b,stops); return b
def blob(buf,cx,cy,rx,ry,col,a=1.0,soft=0.5):
    R=int(max(rx,ry)*2.2)+2; x0,y0=max(0,int(cx)-R),max(0,int(cy)-R); x1,y1=min(w,int(cx)+R),min(h,int(cy)+R)
    if x1<=x0 or y1<=y0 or a<=0: return
    d=np.sqrt(((xx[y0:y1,x0:x1]-cx)/rx)**2+((yy[y0:y1,x0:x1]-cy)/ry)**2)
    k=np.clip((1-d)/max(soft,1e-3),0,1); k=k*k*(3-2*k)
    Bf=buf[y0:y1,x0:x1]; Bf+=(np.array(col,np.float32)-Bf)*(k*a)[...,None]
def softm(buf,m,col,a=1.0,s=1.2):
    if a<=0 or m.x1<=m.x0: return
    x0,y0,x1,y1=max(0,m.x0-6),max(0,m.y0-6),min(w,m.x1+6),min(h,m.y1+6)
    if x1<=x0 or y1<=y0: return
    A=cv2.GaussianBlur(m.m[y0:y1,x0:x1].astype(np.float32)/255,(0,0),s)*a
    Bf=buf[y0:y1,x0:x1]; Bf+=(np.array(col,np.float32)-Bf)*A[...,None]
def snowfall(buf,t,n=140,a=1.0,spd=1.0,seed=1,wind=0.3):
    if a<=0: return
    g=np.random.default_rng(seed); m=M()
    for k in range(n):
        x0=g.uniform(0,w); ph=g.uniform(0,1); s=g.uniform(0.6,1.4); r=g.uniform(1.8,3.6)
        y=((t*55*spd*s/h+ph)%1)*(h+20)-10; x=(x0+t*20*wind*s+8*math.sin(t*1.5+k))%w
        m.circ(x,y,r)
    softm(buf,m,(1,1,1),a,0.5)
def lightning(buf,x0,y0,y1,seed,a=1.0):
    if a<=0: return
    g=np.random.default_rng(seed); pts=[(x0,y0)]; x=x0
    for y in np.linspace(y0,y1,10)[1:]: x+=g.uniform(-26,26); pts.append((x,y))
    m=M().pline(pts,2.5); softm(buf,m,(1,1,0.95),a,0.7); glow(buf,x0,(y0+y1)/2,60,(0.6,0.6,0.7),0.5*a)
def tree(m,x,y,s):
    m.rect(x-4*s,y-40*s,x+4*s,y); m.poly([(x-34*s,y-30*s),(x,y-120*s),(x+34*s,y-30*s)]); return m
def snowcap(m,x,y,s):
    m.poly([(x-20*s,y-74*s),(x,y-120*s),(x+20*s,y-74*s),(x+8*s,y-80*s),(x,y-72*s),(x-10*s,y-80*s)]); return m
def farmhouse(buf,x,y,a=1.0,snow=1.0):
    softm(buf,M().rect(x,y-80,x+150,y),(0.42,0.20,0.14),a); softm(buf,M().poly([(x-12,y-78),(x+75,y-130),(x+162,y-78)]),UMBER,a)
    softm(buf,M().poly([(x-12,y-78),(x+75,y-130),(x+162,y-78),(x+150,y-86),(x+75,y-120),(x,y-86)]),SNOW,a*snow)
    softm(buf,M().rect(x+20,y-56,x+50,y-30),(0.95,0.75,0.40),a)
def volcano(buf,a=1.0,t=0.0,erupt=0.0):
    m=M().poly([(-20,700),(150,440),(230,400),(310,400),(390,440),(560,700)]); softm(buf,m,(0.18,0.13,0.11),a)
    if erupt>0:
        for k in range(6):
            q=((t*0.5+k/6)%1); lx=230+80*(k/6)+math.sin(k*3)*10; softm(buf,dl(M(),[(270,405),(lx-40+80*q,405+260*q)],1.0,3+2*(1-q)),LAVA,a*erupt*(1-q*0.6))
        glow(buf,270,400,50,(1.0,0.5,0.15),0.8*a*erupt)
def plume(buf,t,grow,a=1.0):
    if a<=0 or grow<=0: return
    g=np.random.default_rng(15)
    for k in range(26):
        f=k/26
        if f>grow: break
        y=400-f*360-6*math.sin(t*0.8+k); x=270+g.normal(0,1)*40*f+math.sin(t*0.6+k)*8
        r=30+90*f
        blob(buf,x,y,r*1.1,r*0.8,lerpc((0.30,0.27,0.26),(0.58,0.55,0.52),f*0.7+0.3*g.random()),a*0.9,0.7)
    glow(buf,270,380,70,(1,0.45,0.1),0.35*a)
def globe(buf,cx,cy,R,veil=0.0,a=1.0,t=0.0):
    blob(buf,cx,cy,R,R,(0.22,0.38,0.55),a,0.06)
    for k in range(5):
        an=k*1.3+t*0.25; x=cx+math.cos(an)*R*0.55; y=cy+math.sin(k*2.1)*R*0.5
        if (x-cx)**2+(y-cy)**2<(R*0.8)**2: blob(buf,x,y,R*0.22,R*0.15,MOSS,a*0.8,0.5)
    blob(buf,cx-R*0.35,cy-R*0.35,R*0.35,R*0.35,(0.55,0.70,0.85),0.35*a,1.0)
    if veil>0:
        ang=np.arctan2(yy-cy,xx-cx); d=np.sqrt((xx-cx)**2+(yy-cy)**2)
        ring=(np.abs(d-R*1.02)<R*0.30)*np.clip((veil*2*math.pi*1.1-(ang+math.pi))/0.6,0,1)
        k=(np.clip(1-np.abs(d-R*1.02)/(R*0.30),0,1)*ring*0.95*a)[...,None]
        buf+=(np.array(ASH,np.float32)-buf)*k
        inside=(d<R).astype(np.float32)[...,None]*0.55*veil*a; buf+=(np.array(ASH,np.float32)-buf)*inside
def sun(buf,x,y,r,dimk=0.0,col=GOLDL,a=1.0):
    blob(buf,x,y,r*3,r*3,lerpc(col,ASH,dimk),0.35*a*(1-0.6*dimk),1.0); blob(buf,x,y,r,r,lerpc(col,(0.8,0.75,0.65),dimk),a*(1-0.5*dimk),0.15)
def villa(buf,x,y,a=1.0,lit=1.0,t=0.0):
    softm(buf,M().rect(x,y-150,x+220,y).poly([(x-10,y-148),(x+110,y-200),(x+230,y-148)]),(0.10,0.09,0.10),a)
    wm=M()
    for r_ in range(2):
        for c_ in range(5): wm.rect(x+18+c_*40,y-128+r_*60,x+38+c_*40,y-96+r_*60)
    fl=0.85+0.15*math.sin(t*9)
    softm(buf,wm,(1.0,0.78,0.38),a*lit*fl,0.8)
    for c_ in range(5): glow(buf,x+28+c_*40,y-80,22,(1,0.6,0.2),0.18*a*lit*fl)
def candle(buf,x,y,a=1.0,t=0.0):
    softm(buf,M().rect(x-9,y-60,x+9,y),(0.90,0.86,0.74),a)
    f=M().poly([(x-6,y-62),(x+1*math.sin(t*13),y-88-4*math.sin(t*7)),(x+6,y-62)]); softm(buf,f,(1,0.85,0.4),a,0.8)
    glow(buf,x,y-74,40,(1,0.7,0.3),0.6*a)
def profile(buf,x,y,s,col,a=1.0):
    pts=[(0,0),(-10,-30),(-6,-60),(4,-80),(20,-92),(40,-92),(52,-80),(56,-66),(64,-60),(58,-54),(60,-46),(56,-40),(58,-32),(48,-26),(46,-12),(60,0),(80,30),(-30,30)]
    m=M().poly([(x+px*s,y+py*s) for px,py in pts]); softm(buf,m,col,a)
    softm(buf,M().ell(x+10*s,y-74*s,34*s,24*s).circ(x-14*s,y-64*s,16*s),col,a)
def monster(buf,x,y,s,a=1.0,col=(0.12,0.16,0.12)):
    m=M().poly([(x-34*s,y-110*s),(x+34*s,y-110*s),(x+38*s,y-40*s),(x+20*s,y-10*s),(x-20*s,y-10*s),(x-38*s,y-40*s)])
    m.poly([(x-90*s,y+60*s),(x-60*s,y),(x+60*s,y),(x+90*s,y+60*s)]).rect(x-20*s,y-14*s,x+20*s,y+4*s)
    m.rect(x-50*s,y-28*s,x-36*s,y-18*s).rect(x+36*s,y-28*s,x+50*s,y-18*s)
    softm(buf,m,col,a); softm(buf,M().rect(x-36*s,y-112*s,x+36*s,y-96*s),(0.05,0.05,0.05),a)
    softm(buf,M().line((x-22*s,y-70*s),(x-8*s,y-70*s),3*s).line((x+8*s,y-70*s),(x+22*s,y-70*s),3*s),(0.9,0.9,0.6),a*0.8)
def bat(buf,x,y,s,a=1.0,t=0.0):
    fl=math.sin(t*10)*0.3
    pts=[(0,0),(20,-10-12*fl),(40,-24-20*fl),(60,-8-16*fl),(46,-2),(30,6),(14,4),(0,14)]
    m=M().poly([(x+px*s,y+py*s) for px,py in pts]).poly([(x-px*s,y+py*s) for px,py in pts]).circ(x,y,8*s)
    softm(buf,m,(0.08,0.06,0.07),a)
# ================= scenes =================
SKYJUNE=vgrad([(0,(0.30,0.36,0.46)),(420,(0.58,0.62,0.68)),(560,(0.70,0.72,0.76)),(960,(0.80,0.82,0.86))])
def s_hook(t,sc):
    tt=max(t,-1.0)
    buf=SKYJUNE.copy(); hud=[]
    blob(buf,140,180,220,90,(0.55,0.58,0.64),0.6,1.0); blob(buf,420,120,200,80,(0.60,0.62,0.68),0.5,1.0)
    # green June hills under snow
    softm(buf,M().poly([(0,560)]+[(x,520-30*math.sin(x/90)) for x in range(0,560,20)]+[(540,960),(0,960)]),(0.88,0.90,0.92),1.0)
    trm=M(); scm=M()
    for k,(x,y,s) in enumerate(((70,600,1.3),(150,620,1.0),(420,590,1.4),(490,630,1.0),(320,640,0.8))):
        tree(trm,x,y,s); snowcap(scm,x,y,s)
    softm(buf,trm,(0.20,0.36,0.20),1.0); softm(buf,scm,SNOW,1.0)
    fl=sm((tt-EV["frank"]+0.15)/0.1)*math.exp(-max(0,tt-EV["frank"])*2.0)
    if fl>0.01:
        buf=buf*(1-0.45*min(1,fl*2))+0.0
        lightning(buf,360,0,330,7,fl);
    mk=sm((tt-EV["frank"]+0.1)/0.5)*(1-sm((tt-EV["how"]-0.6)/0.5))
    if mk>0: monster(buf,270,330,1.6,mk*0.85,col=(0.16,0.20,0.17))
    snowfall(buf,tt,150,1.0)
    def hd(d,t=t):
        k0=1.0 if t<0.4 else ap(t,-1,EV["frank"])
        ttl(d,"1816",540,250,190,a=k0,col=cCream)
        ttl(d,"Snow in June",540,420,120,a=k0*(1 if t<0.4 else sm((t-EV["snow"]+0.3)/0.3)) if t>0.4 else k0,col=(255,250,240))
        rplaque(d,"…and FRANKENSTEIN",540,260,64,a=ap(t,EV["frank"],EV["how"]),sc=pop(t,EV["frank"]-0.1))
        plaque(d,"A VOLCANO MADE A MONSTER?",540,260,52,a=ap(t,EV["how"],sc["e"]+1),sc=pop(t,EV["how"]-0.1))
    hud.append(hd); return buf,hud
SKYVOL=vgrad([(0,(0.24,0.18,0.16)),(300,(0.62,0.40,0.22)),(440,(0.86,0.56,0.26)),(700,(0.35,0.22,0.15)),(960,(0.14,0.10,0.08))])
SKYSPACE=vgrad([(0,(0.04,0.05,0.10)),(960,(0.10,0.10,0.18))])
def s_erupt(t,sc):
    pG=sm((t-EV["ash"]+0.35)/0.4)
    if pG<1:
        buf=SKYVOL.copy(); hud=[]
        ex=EV["explodes"]; grow=cl((t-ex+0.3)/2.2) if t>ex-0.3 else 0.0
        volcano(buf,1.0,t,erupt=sm((t-ex+0.2)/0.3))
        plume(buf,t,grow,1.0)
        if t>EV["recorded"]-0.4:
            lightning(buf,250+20*math.sin(t*3),140,300,int(t*3)%7+1,0.8*(0.5+0.5*math.sin(t*17)>0.6))
        fl=math.exp(-max(0,t-ex)*3)*(t>ex-0.05);
        if fl>0.01: glow(buf,270,400,160,(1,0.7,0.35),fl*1.2)
        g=np.random.default_rng(2)
        if t>ex:
            m=M()
            for k in range(30):
                vx=g.uniform(-160,160); vy=g.uniform(-300,-120); dt=(t-ex)%2.5
                x=270+vx*dt; y=400+vy*dt+170*dt*dt
                if 0<y<h: m.circ(x,y,g.uniform(2,4))
            softm(buf,m,(0.12,0.08,0.06),0.9,0.6)
        if pG>0: buf=buf*(1-pG)+SKYSPACE*pG
    else: buf=SKYSPACE.copy(); hud=[]
    if pG>0:
        st=M(); g=np.random.default_rng(9)
        for k in range(60): st.circ(g.uniform(0,w),g.uniform(0,h),g.uniform(0.6,1.3))
        softm(buf,st,(0.9,0.9,1.0),pG*0.8,0.4)
        sun(buf,470,120,26,dimk=sm((t-EV["dims"]+0.2)/0.8),a=pG)
        globe(buf,250,420,170,veil=sm((t-EV["circles"]+0.2)/1.1),a=pG,t=t)
    hud=[]
    def hd(d,t=t,pG=pG):
        plaque(d,"APRIL 1815",540,250,64,a=ap(t,EV["april"],EV["largest"]),sc=pop(t,EV["april"]-0.1))
        ttl(d,"Mount Tambora",540,1180,110,a=ap(t,EV["tambora"],EV["largest"]),sc=pop(t,EV["tambora"]-0.1))
        plaque(d,"INDONESIA",540,1290,44,a=ap(t,EV["indonesia"],EV["largest"]))
        rplaque(d,"LARGEST ERUPTION IN RECORDED HISTORY",540,250,40,a=ap(t,EV["largest"],EV["ash"]),sc=pop(t,EV["largest"]-0.1))
        ttl(d,"Tens of thousands dead",540,1200,84,a=ap(t,EV["tens"],EV["ash"]),sc=pop(t,EV["tens"]-0.1))
        plaque(d,"ASH CIRCLES THE PLANET",540,250,52,a=ap(t,EV["ash"],sc["e"]+1),sc=pop(t,EV["ash"]-0.1))
        ttl(d,"The sun dims",540,1200,110,a=ap(t,EV["dims"],sc["e"]+1),sc=pop(t,EV["dims"]-0.1))
    hud.append(hd); return buf,hud
SKYCOLD=vgrad([(0,(0.32,0.36,0.44)),(450,(0.62,0.64,0.68)),(960,(0.80,0.82,0.86))])
SKYRED=vgrad([(0,(0.30,0.12,0.12)),(250,(0.78,0.30,0.12)),(430,(1.0,0.66,0.26)),(520,(0.95,0.50,0.20)),(960,(0.22,0.12,0.10))])
def s_cold(t,sc):
    pR=sm((t-EV["sunsets"]+0.35)/0.6)
    buf=SKYCOLD*(1-pR)+SKYRED*pR; hud=[]
    land=M().poly([(0,560)]+[(x,540-20*math.sin(x/70)) for x in range(0,560,20)]+[(540,960),(0,960)])
    softm(buf,land,lerpc((0.88,0.89,0.91),(0.32,0.16,0.10),pR),1.0)
    if pR<1:
        a=1-pR
        farmhouse(buf,300,600,a,1.0)
        fr=sm((t-EV["frost"]+0.2)/0.6)
        cm=M()
        for k in range(14):
            x=30+k*18; lean=(1.1+0.2*math.sin(k))*fr
            cm.line((x,640),(x+math.sin(lean)*40,640-60*math.cos(lean)),2.5)
        softm(buf,cm,lerpc((0.30,0.50,0.22),(0.36,0.24,0.14),fr),a)
        if t>EV["europe"]-0.3:
            eu=sm((t-EV["europe"]+0.3)/0.4)
            bm=M()
            for k in range(3): bm.ell(120+k*36,470,16,8)
            softm(buf,bm,(0.42,0.30,0.18),a*eu*0.0)
        snowfall(buf,t,120,a,1.0,3)
    if pR>0:
        blob(buf,270,470,70,70,(1.0,0.86,0.5),pR,0.3); blob(buf,270,470,240,90,(1.0,0.55,0.20),0.35*pR,1.0)
        for k in range(4): blob(buf,80+k*130,300-k*20+6*math.sin(t+k),130,22,(0.55,0.16,0.10),0.55*pR,0.9)
        softm(buf,M().rect(0,520,w,560),(0.85,0.40,0.15),0.3*pR)
    def hd(d,t=t,pR=pR):
        plaque(d,"1816 · NEW ENGLAND",540,250,58,a=ap(t,EV["nextyear"],EV["frost"]),sc=pop(t,EV["nextyear"]-0.1))
        ttl(d,"Snow in June",540,1180,120,a=ap(t,EV["june2"]-0.3,EV["frost"]),sc=pop(t,EV["june2"]-0.4))
        rplaque(d,"CROPS FAIL",540,250,64,a=ap(t,EV["crops"],EV["froze"]),sc=pop(t,EV["crops"]-0.1))
        ttl(d,"Europe goes hungry",540,1180,96,a=ap(t,EV["europe"],EV["froze"]),sc=pop(t,EV["europe"]-0.1))
        plaque(d,"“EIGHTEEN HUNDRED",540,230,50,a=ap(t,EV["froze"],EV["sunsets"]),sc=pop(t,EV["froze"]-0.1))
        plaque(d,"AND FROZE TO DEATH”",540,320,50,a=ap(t,EV["froze"]+0.4,EV["sunsets"]),sc=pop(t,EV["froze"]+0.3))
        ttl(d,"Fiery red sunsets",540,1180,96,a=ap(t,EV["red"]-0.3,sc["e"]+1),sc=pop(t,EV["red"]-0.4),col=(255,226,170))
    hud.append(hd); return buf,hud
SKYSTORM=vgrad([(0,(0.10,0.11,0.16)),(420,(0.26,0.28,0.34)),(560,(0.20,0.22,0.27)),(960,(0.08,0.09,0.12))])
INTERIOR=vgrad([(0,(0.10,0.06,0.04)),(500,(0.24,0.14,0.08)),(960,(0.08,0.05,0.04))])
def s_villa(t,sc):
    pI=sm((t-EV["byron"]+0.35)/0.45)
    buf=SKYSTORM*(1-pI)+INTERIOR*pI; hud=[]
    if pI<1:
        a=1-pI
        for k in range(4): blob(buf,60+k*150,120+30*math.sin(t*0.3+k),190,60,(0.18,0.19,0.24),0.7*a,1.0)
        softm(buf,M().poly([(0,470),(120,380),(260,430),(400,350),(540,420),(540,520),(0,520)]),(0.14,0.15,0.20),a)
        lake=M().rect(0,520,w,h); softm(buf,lake,(0.12,0.15,0.20),a)
        for k in range(10): softm(buf,M().line((20+k*50+10*math.sin(t*2+k),560+k*14),(60+k*50,560+k*14),1.5),(0.35,0.38,0.45),a*0.6)
        villa(buf,160,520,a,1.0,t)
        ph=(t*0.7)%1.0
        if ph<0.12: lightning(buf,420,0,360,int(t*0.7)+3,a*(1-ph/0.12))
        rm=M(); g=np.random.default_rng(int(t*20)%9)
        for k in range(60):
            x=g.uniform(0,w); y=g.uniform(0,h); rm.line((x,y),(x-6,y+22),1)
        softm(buf,rm,(0.6,0.65,0.75),a*0.35,0.4)
    if pI>0:
        a=pI
        pM=sm((t-EV["mary"]+0.3)/0.4); pV=sm((t-EV["vampire"]+0.3)/0.4); pE=sm((t-EV["avol"]+0.3)/0.4)
        candle(buf,270,640,a,t)
        if pM<1:
            for k,x in enumerate((110,200,350,440)):
                softm(buf,M().circ(x,520,26).poly([(x-40,640),(x-30,550),(x+30,550),(x+40,640)]),(0.06,0.04,0.03),a*(1-pM))
        if pM>0:
            profile(buf,150,520,1.6,(0.05,0.03,0.02),a*pM*(1-pE))
            sk=sm((t-EV["scientist"]+0.2)/0.6)*(1-pV)
            for k in range(6):
                q=(t*0.4+k/6)%1; blob(buf,280+20*math.sin(q*6+k),560-q*260,18+30*q,14+20*q,(0.45,0.40,0.36),0.25*a*(1-q),1.0)
            if sk>0: monster(buf,370,330,1.25,a*sk*0.9,col=(0.20,0.26,0.20))
        if pV>0: bat(buf,380,300,1.8,a*pV*(1-pE),t);
        if pE>0:
            volcano(buf,a*pE,t,erupt=1.0); plume(buf,t,0.8,a*pE*0.8)
    def hd(d,t=t,pI=pI):
        plaque(d,"SWITZERLAND · 1816",540,250,56,a=ap(t,EV["swiss"],EV["byron"]),sc=pop(t,EV["swiss"]-0.1))
        ttl(d,"Trapped by storms",540,1180,100,a=ap(t,EV["storms"],EV["villa"]),sc=pop(t,EV["storms"]-0.1))
        ttl(d,"Villa Diodati",540,1180,110,a=ap(t,EV["villa"]-0.2,EV["byron"]),sc=pop(t,EV["villa"]-0.3))
        plaque(d,"LORD BYRON’S CHALLENGE:",540,230,48,a=ap(t,EV["byron"],EV["mary"]),sc=pop(t,EV["byron"]-0.1))
        ttl(d,"Who can write the best",540,350,74,a=ap(t,EV["challenge"]+0.4,EV["mary"]))
        ttl(d,"ghost story?",540,450,110,a=ap(t,EV["ghost"],EV["mary"]),sc=pop(t,EV["ghost"]-0.1),col=(255,226,170))
        plaque(d,"MARY SHELLEY, AGE 18",540,250,52,a=ap(t,EV["mary"],EV["contest"]),sc=pop(t,EV["mary"]-0.1))
        ttl(d,"Frankenstein",540,1180,130,a=ap(t,EV["builds"]-0.2,EV["contest"]),sc=pop(t,EV["builds"]-0.3),col=(214,236,190))
        plaque(d,"SAME CONTEST:",540,250,52,a=ap(t,EV["contest"],EV["avol"]),sc=pop(t,EV["contest"]-0.1))
        ttl(d,"The Vampyre",540,1180,130,a=ap(t,EV["vampire"]-0.1,EV["avol"]),sc=pop(t,EV["vampire"]-0.2),col=(240,170,160))
        plaque(d,"JOHN POLIDORI, 1819",540,1300,40,a=ap(t,EV["vampire"]+0.3,EV["avol"]))
        rplaque(d,"A VOLCANO MADE THE MONSTER",540,250,52,a=ap(t,EV["avol"],sc["e"]+1),sc=pop(t,EV["avol"]-0.1))
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,erupt=s_erupt,cold=s_cold,villa=s_villa)
BAND=(1-0.40*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.34*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.008,(h,w,1)).astype(np.float32) for i in range(6)]
TR=0.32; TOTAL=B.TOTAL; LOOPD=0.6
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
_BRI=np.random.default_rng(77).normal(0,1,h).astype(np.float32); _BRI=np.convolve(_BRI,np.ones(3)/3,'same')
_bands=4; _bh=h/_bands
_rowband=np.minimum((np.arange(h)/_bh).astype(int),_bands-1)
def brushwipe(b1,b2,u):
    """four broad brush strokes paint the next scene in, alternating direction, with bristle edges and streaks"""
    out=b1.copy()
    for k in range(_bands):
        pk=sm(cl((u-k*0.12)/0.64)); y0=int(k*_bh)-6 if k>0 else 0; y1=int((k+1)*_bh)+6 if k<_bands-1 else h
        fr=pk*(w+180)-90+28*_BRI[y0:y1]+10*np.sin(np.arange(y0,y1)/7.0)
        X=xx[y0:y1]
        msk=(X<fr[:,None]) if k%2==0 else (X>(w-fr)[:,None])
        edge=np.exp(-((X-(fr[:,None] if k%2==0 else (w-fr)[:,None]))/7)**2)
        seg=np.where(msk[...,None],b2[y0:y1],out[y0:y1])
        streak=(1+0.10*BR1[y0:y1])[...,None]
        seg=np.where(msk[...,None],seg*streak,seg)
        seg=seg*(1-0.35*edge[...,None])
        out[y0:y1]=seg
    return out
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(sc,SC[i+1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SC[i-1],sc,t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(sc,SC[0],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None:
        buf,hud=render_scene(t,sc); hk=1.0; buf=paintify(buf)
    else:
        A_,B2,ta,tb,u=pair
        b1,h1=render_scene(ta,A_); b2,h2=render_scene(tb,B2)
        buf=brushwipe(paintify(b1),paintify(b2),u); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    buf=np.clip(buf,0,1.2)*PT*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
