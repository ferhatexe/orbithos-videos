import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid48")
for p in ["/home/claude/vid48","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
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
# ================= palette (Turkish ebru marbling: lapis, ivory, red ochre, gold on water) =================
LAPIS=(0.12,0.20,0.46); INDIGO=(0.05,0.07,0.19); IVORY=(0.94,0.90,0.79); OCHRE=(0.68,0.26,0.16); GOLDO=(0.86,0.64,0.26); MILK=(0.98,0.97,0.93)
TEAL=(0.12,0.40,0.42); ROSE=(0.80,0.50,0.48)
K.INK=INDIGO
cG=(232,190,104); cI=(14,20,50); cIv=(246,236,212); cR=(170,60,40)
_IF={}
def _f(path,s):
    k=(path,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(path,s)
    return _IF[k]
FIT="/home/claude/vid48/Cinzel.ttf"; FGR="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
def ttl(d,s,x,y,fs=120,a=1.0,sc=1.0,col=cIv,font=None):
    if a<=0.01 or fs*sc<8: return
    font=font or B_CZ; n=int(fs*sc); f=_f(font,n)
    while f.getlength(s)>1000 and n>20: n-=6; f=_f(font,n)
    d.text((x+3,y+4),s,font=f,fill=(6,8,20,int(160*a)),anchor="mm"); d.text((x,y),s,font=f,fill=col+(int(255*a),),anchor="mm",stroke_width=3,stroke_fill=(14,20,50,int(220*a)))
B_CZ="/home/claude/vid48/Cinzel.ttf"
_PC={}
def plate(d,s,x,y,fs=50,a=1.0,sc=1.0,kind="lapis",font=None):
    if a<=0.01 or sc<=0.02: return
    k=(s,fs,kind,font)
    if k not in _PC:
        f=_f(font or FIT,fs); d0=ImageDraw.Draw(Image.new("RGBA",(4,4))); bb=d0.textbbox((0,0),s,font=f)
        tw,th=bb[2]-bb[0],bb[3]-bb[1]; px,py=int(fs*0.6),int(fs*0.36); m=14
        im=Image.new("RGBA",(tw+2*px+2*m,th+2*py+2*m),(0,0,0,0)); dd=ImageDraw.Draw(im)
        bg,fg,ln={"lapis":((22,38,96),cG,cG),"ivory":((244,234,210),cI,(150,110,50)),"ochre":((160,58,38),cIv,cG)}[kind]
        dd.rounded_rectangle((m,m,m+tw+2*px,m+th+2*py),radius=int(fs*0.5),fill=bg+(245,),outline=ln+(255,),width=3)
        dd.rounded_rectangle((m+7,m+7,m+tw+2*px-7,m+th+2*py-7),radius=int(fs*0.42),outline=ln+(150,),width=1)
        dd.text((m+px-bb[0],m+py-bb[1]),s,font=f,fill=fg+(255,)); _PC[k]=im
    im=_PC[k]
    if abs(sc-1)>0.01: q=max(0.05,round(sc*20)/20); im=im.resize((max(1,int(im.width*q)),max(1,int(im.height*q))),Image.BILINEAR)
    if a<0.99: ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); im=Image.fromarray(ar)
    paste(d,im,x-im.width/2,y-im.height/2)
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= marbling model (Jaffer et al.: ink drops + tine lines + vortex) =================
XX=xx.astype(np.float32); YY=yy.astype(np.float32)
def drop(img,cx,cy,r,col):
    """drop of colour radius r at c: existing paint is pushed radially outward (area-preserving)"""
    dx,dy=XX-cx,YY-cy; d2=dx*dx+dy*dy; r2=r*r
    k=np.sqrt(np.clip(1-r2/np.maximum(d2,1e-6),0,1)).astype(np.float32)
    mx=(cx+dx*k).astype(np.float32); my=(cy+dy*k).astype(np.float32)
    out=cv2.remap(img,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    inside=np.clip((r-np.sqrt(d2))/1.2+0.5,0,1)[...,None]
    return out*(1-inside)+np.array(col,np.float32)*inside
def tine(img,vertical=True,spacing=60,z=40,lam=12,off=0.0,ph=0.0):
    """comb through the paint: each tine line drags the paint along it, falling off with distance"""
    if vertical:
        u=((XX-off)%spacing); dist=np.minimum(u,spacing-u)
        sgn=np.where(((XX-off)//spacing)%2==0,1,-1) if ph else 1
        dsp=z*lam/(dist+lam)*sgn; mx=XX; my=(YY-dsp).astype(np.float32)
    else:
        u=((YY-off)%spacing); dist=np.minimum(u,spacing-u)
        sgn=np.where(((YY-off)//spacing)%2==0,1,-1) if ph else 1
        dsp=z*lam/(dist+lam)*sgn; mx=(XX-dsp).astype(np.float32); my=YY
    return cv2.remap(img,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
def vortex(img,cx,cy,strength,rad):
    dx,dy=XX-cx,YY-cy; d=np.sqrt(dx*dx+dy*dy)+1e-6; ang=strength*np.exp(-d/rad)
    c,s=np.cos(-ang),np.sin(-ang); mx=cx+dx*c-dy*s; my=cy+dx*s+dy*c
    return cv2.remap(img,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
def make_ebru(seed,bg,cols,n=36,rmin=18,rmax=60,combs=(),swirls=()):
    g=np.random.default_rng(seed); img=np.zeros((h,w,3),np.float32); img[:]=bg
    for k in range(n):
        cx,cy=g.uniform(-20,w+20),g.uniform(-20,h+20)
        for j,c in enumerate(cols[g.integers(0,len(cols))]):
            img=drop(img,cx,cy,g.uniform(rmin,rmax)*(1-0.28*j),c)
    for cb in combs: img=tine(img,**cb)
    for sw in swirls: img=vortex(img,*sw)
    return img
NIGHTE=make_ebru(3,INDIGO,[[LAPIS,INDIGO],[(0.10,0.14,0.34),LAPIS],[TEAL,INDIGO]],n=40,rmin=30,rmax=90,
    combs=[dict(vertical=False,spacing=90,z=60,lam=18),dict(vertical=True,spacing=120,z=50,lam=20,ph=1)])
DAYE=make_ebru(5,IVORY,[[GOLDO,IVORY],[OCHRE,GOLDO,IVORY],[ROSE,IVORY],[(0.80,0.74,0.60),IVORY]],n=34,rmin=26,rmax=80,
    combs=[dict(vertical=True,spacing=70,z=40,lam=14,ph=1),dict(vertical=False,spacing=110,z=46,lam=16)])
# spiral galaxy pattern (drops of milk on indigo, then a strong vortex)
def galaxy_img(seed=9,n=26,strength=6.5,rad=120,cx=270,cy=430):
    g=np.random.default_rng(seed); img=NIGHTE.copy()
    for k in range(n):
        a=g.uniform(0,2*math.pi); r=abs(g.normal(0,70))
        img=drop(img,cx+math.cos(a)*r*1.3,cy+math.sin(a)*r*0.7,g.uniform(6,18)*(1.3-r/200),MILK if k%3 else GOLDO)
    img=drop(img,cx,cy,22,MILK)
    return vortex(img,cx,cy,strength,rad)
GAL=galaxy_img()
GAL_SMALL=galaxy_img(11,14,7,60)
# ================= figures =================
def outlinefill(buf,m,col,a=1.0,th=2,lc=INDIGO):
    if a<=0: return
    comp(buf,m,col,sh=0.55,dx=3,dy=5,blur=5,rim=0,a=a); outl(buf,m,a=a,th=th,fill=0,col=lc)
def zeus(buf,x,y,s,a=1.0,t=0.0):
    body=M().poly([(x-40*s,y),(x-30*s,y-150*s),(x+30*s,y-150*s),(x+44*s,y)])
    head=M().circ(x,y-176*s,24*s); beard=M().poly([(x-22*s,y-170*s),(x+22*s,y-170*s),(x+10*s,y-130*s),(x,y-122*s),(x-10*s,y-130*s)])
    arm=M().line((x+26*s,y-140*s),(x+70*s,y-190*s),12*s)
    outlinefill(buf,body,LAPIS,a); outlinefill(buf,M().rect(x-36*s,y-30*s,x+40*s,y-18*s),GOLDO,a,1); outlinefill(buf,arm,LAPIS,a); outlinefill(buf,head,(0.92,0.78,0.62),a); outlinefill(buf,beard,(0.97,0.96,0.93),a)
    bolt=[(x+70*s,y-190*s),(x+60*s,y-230*s),(x+82*s,y-232*s),(x+68*s,y-280*s)]
    bm=M().pline(bolt,6*s); outlinefill(buf,bm,GOLDO,a,1); glow(buf,x+70*s,y-240*s,30*s,(0.6,0.45,0.15),0.4*a*(0.7+0.3*math.sin(t*9)))
def baby(buf,x,y,s,a=1.0,glowk=0.0):
    m=M().ell(x,y,26*s,16*s).circ(x-24*s,y-6*s,13*s)
    outlinefill(buf,m,(0.96,0.88,0.80),a)
    if glowk>0: glow(buf,x,y,40*s,(0.5,0.42,0.2),0.6*glowk*a)
def hera(buf,x,y,s,a=1.0,rise=0.0,arm=0.0):
    hy=y-20*s-40*s*rise
    body=M().poly([(x-120*s,y),(x-110*s,y-30*s),(x+130*s,y-34*s),(x+150*s,y)])
    torso=M().poly([(x-110*s,y-30*s),(x-90*s,hy-6*s),(x-60*s,hy-10*s),(x-40*s,y-30*s)])
    head=M().circ(x-80*s,hy-28*s,20*s); crown=M().poly([(x-98*s,hy-42*s),(x-92*s,hy-62*s),(x-84*s,hy-48*s),(x-78*s,hy-66*s),(x-72*s,hy-48*s),(x-64*s,hy-62*s),(x-60*s,hy-42*s)])
    outlinefill(buf,body,ROSE,a); outlinefill(buf,torso,IVORY,a); outlinefill(buf,head,(0.92,0.80,0.66),a); outlinefill(buf,crown,GOLDO,a)
    ax=x-50*s+math.cos(-0.4+arm*0.6)*70*s*arm; ay=hy+10*s-30*s*arm
    if arm>0: outlinefill(buf,M().line((x-60*s,hy+4*s),(ax,ay),10*s),IVORY,a)
def frame(buf,a=1.0):
    if a<=0: return
    m=M().rect(18,60,522,72).rect(18,640,522,652).rect(18,60,30,652).rect(510,60,522,652)
    outlinefill(buf,m,GOLDO,a,1)
def flow(img,t,amp=3.0):
    """gentle living-water drift of the marbled surface"""
    mx=XX+amp*np.sin(YY/53+t*0.9); my=YY+amp*np.sin(XX/61-t*0.7)
    return cv2.remap(img,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
# ================= scenes =================
def s_hook(t,sc):
    tt=max(t,-1.0)
    img=vortex(GAL,270,430,0.35*tt+0.0,140) if abs(tt)>1e-3 else GAL.copy()
    buf=flow(img,tt,2.5); hud=[]
    dr=sm((tt-EV["goddess"]+0.6)/0.3)
    if dr>0 and tt<EV["goddess"]+1.6:
        k=cl((tt-EV["goddess"]+0.6)/1.2); y=-20+450*ein(k)
        m=M().circ(270,y,10).poly([(262,y-4),(270,y-26),(278,y-4)]); comp(buf,m,MILK,sh=0,rim=0,a=dr*(1-sm((k-0.92)/0.08)))
        if k>=1: buf=drop(buf,270,430,18*sm((tt-EV["goddess"]-0.6)/0.4)+0.1,MILK)
    def hd(d,t=t):
        k0=1.0 if t<0.4 else ap(t,-1,EV["goddess"])
        plate(d,"EVERY GALAXY",540,230,62,a=k0)
        ttl(d,"= SPILLED MILK",540,1180,96,a=1.0 if t<0.4 else ap(t,-1,EV["goddess"]),sc=1.0 if t<EV["spilled"] else 1+0.07*math.exp(-(t-EV["spilled"])*5))
        plate(d,"THE MILK OF A GODDESS",540,230,56,a=ap(t,EV["goddess"],sc["e"]+1),sc=pop(t,EV["goddess"]-0.1),kind="ivory")
        ttl(d,"How?",540,1180,140,a=ap(t,EV["how"],sc["e"]+1),sc=pop(t,EV["how"]-0.1),col=(255,226,150))
    hud.append(hd); return buf,hud
def s_birth(t,sc):
    pN=sm((t-EV["placed"]+0.35)/0.45)
    buf=flow(DAYE,t,3.0)*(1-pN)+flow(NIGHTE,t,2.0)*pN; hud=[]
    a=1-pN
    if a>0:
        zeus(buf,160,660,1.5,a*sm((t-sc["s"]+0.3)/0.5),t)
        mo=sm((t-EV["mortal"]+0.2)/0.4)
        if mo>0:
            m=M().poly([(360,660),(376,500),(424,500),(440,660)]).circ(400,476,22); outlinefill(buf,m,OCHRE,a*mo)
        hb=sm((t-EV["heracles"]+0.2)/0.4)
        if hb>0: baby(buf,400,440-60*hb,1.5,a*hb,glowk=sm((t-EV["immortal"]+0.2)/0.5))
        dv=sm((t-EV["divine"]+0.2)/0.4)
        if dv>0:
            m=M().circ(300,330,22).poly([(284,322),(300,280),(316,322)]); outlinefill(buf,m,MILK,a*dv)
    zl=[]
    if pN>0:
        hera(buf,290,600,1.7,pN); baby(buf,250,500,1.3,pN)
        for k in range(3):
            ph=(t*0.5+k*0.33)%1; zl.append(((180-ph*20)*2,(400-ph*60)*2,(1-ph)*pN))
    def hd(d,t=t,pN=pN,zl=zl):
        plate(d,"ZEUS · KING OF THE GODS",540,230,52,a=ap(t,EV["zeus"],EV["mortal"]),sc=pop(t,EV["zeus"]-0.1))
        plate(d,"+ A MORTAL WOMAN",540,230,56,a=ap(t,EV["mortal"],EV["heracles"]),sc=pop(t,EV["mortal"]-0.1),kind="ivory")
        ttl(d,"Heracles",540,1180,130,a=ap(t,EV["heracles"],EV["immortal"]),sc=pop(t,EV["heracles"]-0.1))
        plate(d,"HIS NAME = “GLORY OF HERA”",540,230,48,a=ap(t,EV["glory"]-0.3,EV["immortal"]),sc=pop(t,EV["glory"]-0.4),kind="ochre")
        plate(d,"TO BE IMMORTAL…",540,230,58,a=ap(t,EV["immortal"],EV["placed"]),sc=pop(t,EV["immortal"]-0.1))
        ttl(d,"Divine milk",540,1180,120,a=ap(t,EV["divine"],EV["placed"]),sc=pop(t,EV["divine"]-0.1),col=(255,248,230))
        plate(d,"HERA · ZEUS’S WIFE",540,230,56,a=ap(t,EV["hera"],sc["e"]+1),sc=pop(t,EV["hera"]-0.1),kind="ochre")
        ttl(d,"…asleep",540,1180,110,a=ap(t,EV["slept"],sc["e"]+1))
        for zx,zy,za in zl: card(d,"z",zx,zy,fs=42,a=za*0.8,fg=cIv,bg=None,fn="Italiana-Regular",torn=False,pad=(2,2))
    hud.append(hd); return buf,hud
card_z=[]
def card_z_reset():
    global card_z
    zz=list(card_z); card_z=[]
    def _f_(): return zz
    return zz
# spill: milk drops along an arc across the sky
_gs=np.random.default_rng(21)
ARC=[(80+k*12+_gs.normal(0,10),560-k*12-0.9*(k*12)**1.18/10+_gs.normal(0,10),_gs.uniform(9,19)) for k in range(36)]
def s_spill(t,sc):
    hud=[]
    img=NIGHTE.copy()
    t0=EV["sprayed"]-0.2
    n=int(cl((t-t0)/1.6)*len(ARC)) if t>t0 else 0
    for k in range(n):
        x,y,r=ARC[k]; img=drop(img,x,y,r,MILK)
    if n>0:
        st=sm((t-EV["river"]+0.3)/1.2)
        if st>0: img=tine(img,vertical=True,spacing=36,z=14*st,lam=8,ph=1)
    buf=flow(img,t,2.0)
    pF=sm((t-EV["centuries"]+0.3)/0.4)
    a=1.0
    hera(buf,300,690,1.5,a,rise=sm((t-EV["woke"]+0.2)/0.5),arm=sm((t-EV["pushed"]+0.2)/0.4))
    bx=230-60*sm((t-EV["pushed"]+0.1)/0.5); baby(buf,bx,590+20*sm((t-EV["pushed"]+0.1)/0.5),1.2,a)
    sp=sm((t-EV["stars"]+0.2)/0.6)
    if sp>0:
        m=M()
        for k in range(len(ARC)):
            x,y,r=ARC[k]
            for j in range(3):
                q=k*3+j; sx=x+math.cos(q*2.1)*r*2.2; sy=y+math.sin(q*1.7)*r*2.2
                rr=1.6+1.2*math.sin(t*4+q); m.poly([(sx,sy-rr*3),(sx+rr,sy),(sx,sy+rr*3),(sx-rr,sy)])
        comp(buf,m,(1,0.95,0.75),sh=0,rim=0,a=sp*0.9)
    frame(buf,pF)
    def hd(d,t=t,pF=pF):
        ttl(d,"Not her child!",540,1180,110,a=ap(t,EV["notchild"],EV["pushed"]),sc=pop(t,EV["notchild"]-0.1),col=(255,200,170))
        plate(d,"HERA WAKES",540,230,60,a=ap(t,EV["woke"],EV["pushed"]),sc=pop(t,EV["woke"]-0.1),kind="ochre")
        plate(d,"MILK ACROSS THE SKY",540,230,56,a=ap(t,EV["sprayed"]-0.2,EV["drops"]),sc=pop(t,EV["sprayed"]-0.3))
        plate(d,"DROPS BECOME STARS",540,230,60,a=ap(t,EV["stars"]-0.2,EV["centuries"]),sc=pop(t,EV["stars"]-0.3),kind="ivory")
        ttl(d,"A river of light",540,1180,96,a=ap(t,EV["river"],EV["centuries"]),sc=pop(t,EV["river"]-0.1),col=(255,248,230))
        plate(d,"TINTORETTO · c. 1575",540,230,50,a=ap(t,EV["tintoretto"],sc["e"]+1),sc=pop(t,EV["tintoretto"]-0.1),kind="ochre")
        plate(d,"RUBENS · 1636–37",540,1220,48,a=ap(t,EV["rubens"],sc["e"]+1),sc=pop(t,EV["rubens"]-0.1),kind="ochre")
    hud.append(hd); return buf,hud
GALPOS=[(110,180),(420,150),(380,560),(140,600),(270,330),(60,420),(480,380),(250,680),(330,90),(190,470),(470,640),(90,300)]
def s_word(t,sc):
    hud=[]
    pG=sm((t-EV["astro"]+0.35)/0.45)
    if pG<1:
        img=NIGHTE.copy()
        for k in range(len(ARC)): x,y,r=ARC[k]; img=drop(img,x,y,r,MILK)
        img=tine(img,vertical=True,spacing=36,z=14,lam=8,ph=1)
        buf=flow(img,t,2.0)*(1-pG)
    else: buf=np.zeros((h,w,3),np.float32)
    if pG>0:
        base=flow(NIGHTE,t,2.0)*0.55
        n=1+int(cl((t-EV["astro"]+0.2)/(EV["billions"]-EV["astro"]+0.4))*len(GALPOS))
        for k,(x,y) in enumerate(GALPOS[:n]):
            s=0.35+0.25*((k*7)%3)/2; sz=int(240*s); x0,y0=int(x-sz/2),int(y-sz/2)
            gi=cv2.resize(GAL_SMALL[430-120:430+120,270-120:270+120],(sz,sz))
            ang=(k*40+t*12)%360; R=cv2.getRotationMatrix2D((sz/2,sz/2),ang,1.0); gi=cv2.warpAffine(gi,R,(sz,sz),borderMode=cv2.BORDER_REFLECT)
            yy_,xx_=np.mgrid[0:sz,0:sz]; msk=np.clip(1-np.hypot(xx_-sz/2,(yy_-sz/2)*1.6)/(sz/2),0,1)[...,None]**0.8
            xa,ya=max(0,x0),max(0,y0); xb,yb=min(w,x0+sz),min(h,y0+sz)
            if xb>xa and yb>ya:
                sub=gi[ya-y0:yb-y0,xa-x0:xb-x0]; mm=msk[ya-y0:yb-y0,xa-x0:xb-x0]*sm((t-EV["astro"]-k*0.12+0.2)/0.4)
                base[ya:yb,xa:xb]=base[ya:yb,xa:xb]*(1-mm)+sub*mm
        buf=buf+base*pG
    def hd(d,t=t,pG=pG):
        ttl(d,"ΓΑΛΑΞΙΑΣ ΚΥΚΛΟΣ",540,240,82,a=ap(t,EV["greeks"],EV["romans"]),sc=pop(t,EV["greeks"]-0.1),font=FGR,col=(255,226,150))
        plate(d,"“THE MILKY CIRCLE”",540,370,52,a=ap(t,EV["milky"]-0.2,EV["romans"]),kind="ivory")
        ttl(d,"VIA LACTEA",540,240,110,a=ap(t,EV["romans"],EV["astro"]),sc=pop(t,EV["romans"]-0.1),col=(255,226,150))
        plate(d,"THE MILKY WAY",540,370,58,a=ap(t,EV["mw"]-0.1,EV["astro"]),sc=pop(t,EV["mw"]-0.2),kind="ivory")
        plate(d,"OTHER STAR SYSTEMS…",540,230,56,a=ap(t,EV["other"],EV["galaxies"]))
        ttl(d,"Galaxies",540,1180,140,a=ap(t,EV["galaxies"],sc["e"]+1),sc=pop(t,EV["galaxies"]-0.1),col=(255,248,230))
        plate(d,"BILLIONS OF THEM",540,230,58,a=ap(t,EV["billions"],sc["e"]+1),sc=pop(t,EV["billions"]-0.1),kind="ochre")
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,birth=s_birth,spill=s_spill,word=s_word)
BAND=(1-0.38*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.28*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.008,(h,w,1)).astype(np.float32) for i in range(6)]
_MN=make_ebru(77,(0,0,0),[[(1,1,1),(0,0,0)],[(0.5,0.5,0.5),(1,1,1)]],n=30,rmin=30,rmax=90,combs=[dict(vertical=True,spacing=80,z=50,lam=16,ph=1)])[...,0]
_MN=cv2.GaussianBlur(_MN,(0,0),6); _MN=(_MN-_MN.min())/(_MN.max()-_MN.min()+1e-6); _MN=0.15+0.7*_MN+0.15*(yy/h)
TR=0.33; TOTAL=B.TOTAL; LOOPD=0.6
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
def combwipe(b1,b2,u):
    """the ebru master drags a comb through the bath: old pattern smears, new one blooms through a marbled edge"""
    z1=120*sm(u); z2=120*(1-sm(u))
    c1=tine(b1,vertical=True,spacing=54,z=z1,lam=14,ph=1) if z1>0.5 else b1
    c2=tine(b2,vertical=True,spacing=54,z=-z2,lam=14,ph=1) if z2>0.5 else b2
    m=np.clip((u*1.3-_MN)/0.08+0.5,0,1)[...,None]
    edge=np.exp(-((u*1.3-_MN)/0.05)**2)[...,None]
    out=c1*(1-m)+c2*m
    return out+edge*0.35*(np.array(GOLDO,np.float32)-out)
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
        buf=combwipe(b1,b2,u); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    buf=np.clip(buf,0,1.2)*PT*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
