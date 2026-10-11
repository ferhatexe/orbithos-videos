import numpy as np, cv2, math, sys
for p in ["/home/claude/vid20","/home/claude/vid3","/home/claude/ep1"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
from PIL import Image, ImageDraw
w,h,W,H=B.w,B.h,B.W,B.H; yy,xx=B.yy.astype(np.float32),B.xx.astype(np.float32)
cl,sm,ein,eout,fa,txt,title=B.cl,B.sm,B.ein,B.eout,B.fa,B.txt,B.title
CLOUD=B.CLOUD; glowpt=B.glowpt; bigglow=E1.bigglow
fMono,fMonoS,fBig,CZ=B.fMono,B.fMonoS,B.fBig,B.CZ
LOGO=E1.LOGO; band=E1.band; EV=ev.EV; Lx=ev.Lx; SS=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
GOLD=(255,214,120); JADE=(120,220,160); RUBY=(255,80,60)
# ------------------------------------------------------------------ cup geometry (working res)
CX=270; RIM_Y=250; BODY_END=552; TW=1440
def hw_of(y):
    if y<RIM_Y or y>BODY_END: return 0.0
    if y<=480: return 130-8*((y-RIM_Y)/230.0)
    q=(y-480)/72.0; return max(34.0,122*math.sqrt(max(0.0,1-q*q)))
HWROW=np.array([hw_of(y) for y in range(h)],np.float32); YI=np.clip(yy.astype(np.int32),0,h-1)
HWMAP=HWROW[YI]; INSIDE=cv2.GaussianBlur(((np.abs(xx-CX)<HWMAP)&(HWMAP>0)).astype(np.float32),(0,0),0.8)
U=np.clip((xx-CX)/np.maximum(HWMAP,1.0),-1,1); NZ=np.sqrt(np.clip(1-U*U,0,1)); THETA=np.arcsin(U).astype(np.float32)
def _poly(pts):
    m=np.zeros((h,w),np.float32); cv2.fillPoly(m,[np.array(pts,np.int32)],1.0,cv2.LINE_AA); return m
RIMM=cv2.GaussianBlur(_poly([(CX-136,RIM_Y-9),(CX+136,RIM_Y-9),(CX+134,RIM_Y+15),(CX-134,RIM_Y+15)]),(0,0),0.7)
FOOTM=cv2.GaussianBlur(_poly([(CX-24,BODY_END-4),(CX+24,BODY_END-4),(CX+28,572),(CX+84,594),(CX+84,606),(CX-84,606),(CX-84,594),(CX-28,572)]),(0,0),0.7)
NZM=np.sqrt(np.clip(1-((xx-CX)/140.0)**2,0,1))
def build_tex():
    fig=Image.new("L",(TW,h),0); vin=Image.new("L",(TW,h),0); df=ImageDraw.Draw(fig); dv=ImageDraw.Draw(vin)
    def person(x,yb,s,arms="up",horns=False,staff=False):
        c=255; wd=lambda v:max(2,int(v*s))
        df.ellipse([x-11*s,yb-192*s,x+11*s,yb-168*s],fill=c)
        df.polygon([(x-17*s,yb-165*s),(x+17*s,yb-165*s),(x+13*s,yb-95*s),(x-13*s,yb-95*s)],fill=c)
        df.line([(x-6*s,yb-95*s),(x-14*s,yb)],fill=c,width=wd(10)); df.line([(x+6*s,yb-95*s),(x+16*s,yb)],fill=c,width=wd(10))
        if arms=="up": df.line([(x-14*s,yb-158*s),(x-40*s,yb-214*s)],fill=c,width=wd(8)); df.line([(x+14*s,yb-158*s),(x+38*s,yb-206*s)],fill=c,width=wd(8))
        else: df.line([(x-14*s,yb-158*s),(x-30*s,yb-110*s)],fill=c,width=wd(8)); df.line([(x+14*s,yb-158*s),(x+34*s,yb-120*s)],fill=c,width=wd(8))
        if horns: df.line([(x-8*s,yb-190*s),(x-14*s,yb-206*s)],fill=c,width=wd(5)); df.line([(x+8*s,yb-190*s),(x+14*s,yb-206*s)],fill=c,width=wd(5)); df.line([(x-10*s,yb-100*s),(x-40*s,yb-70*s)],fill=c,width=wd(5))
        if staff: df.line([(x+34*s,yb-120*s),(x+34*s,yb-236*s)],fill=c,width=wd(5)); df.ellipse([x+27*s,yb-252*s,x+41*s,yb-232*s],fill=c)
    def vine(x0,yb,hgt,ph=0.5,amp=34):
        pts=[(x0+amp*math.sin(k/60*13+ph)*(1-0.3*k/60),yb-hgt*k/60) for k in range(61)]; dv.line(pts,fill=255,width=6,joint="curve")
        for k in range(3,60,6): x,y=pts[k]; sd=1 if (k//6)%2 else -1; dv.ellipse([min(x+sd*4,x+sd*24),y-8,max(x+sd*4,x+sd*24),y+8],fill=255)
    person(720,520,1.0,"up"); vine(720,520,215)
    for x in range(560,900,3): dv.point((x,int(478+20*math.sin(x/24))),fill=255)
    df.ellipse([535,455,625,495],fill=255); df.ellipse([610,428,640,456],fill=255)
    for lx in (545,565,605,620): df.line([(lx,485),(lx-4,522)],fill=255,width=8)
    df.line([(535,462),(505,440),(498,420)],fill=255,width=6)
    person(960,520,1.0,"down",staff=True)
    for cx_,cy_ in [(925,430),(941,430),(933,446),(917,446),(949,446),(933,462)]: df.ellipse([cx_-8,cy_-8,cx_+8,cy_+8],fill=255)
    person(1180,520,0.95,"up",horns=True); person(300,520,0.95,"down",horns=True); vine(300,520,190,1.2,26); person(120,520,0.9,"up"); vine(120,520,180,2.0,24)
    for y0 in (284,526): df.line([(0,y0),(TW,y0)],fill=255,width=3)
    f=np.asarray(fig,np.float32)/255; v=np.asarray(vin,np.float32)/255
    return cv2.GaussianBlur(f,(0,0),1.0),cv2.GaussianBlur(v,(0,0),1.0)
FIGT,VINET=build_tex()
_SPEC=np.exp(-((U-0.38)/0.10)**2)*0.5+np.exp(-((U+0.55)/0.06)**2)*0.18
GREENB=(np.array([0.30,0.58,0.40],np.float32)*(0.26+0.74*NZ**0.9)[...,None]).astype(np.float32)
SPECC=(_SPEC[...,None]*np.array([0.7,1.0,0.8],np.float32)*0.55).astype(np.float32); GEDGE=np.array([0.5,0.85,0.6],np.float32)*0.55
REDB=(np.array([0.95,0.09,0.05],np.float32)*(0.42+0.58*NZ**0.6)[...,None]).astype(np.float32); REDGE=np.array([1.0,0.5,0.25],np.float32)*0.75
REDGLOW=(np.exp(-(((xx-CX)/70.0)**2+((yy-410)/120.0)**2))[...,None]*np.array([1.0,0.42,0.14],np.float32)*0.55).astype(np.float32)
def cup_render(buf,Lf,Lb,rot,crack=0.0,rimglow=0.0):
    if Lf<=0.003 and Lb<=0.003: return
    mx=(((THETA+rot)/(2*math.pi)+0.5)%1.0*TW).astype(np.float32)
    fig=cv2.remap(FIGT,mx,yy,cv2.INTER_LINEAR); vin=cv2.remap(VINET,mx,yy,cv2.INTER_LINEAR); fg=np.clip(fig+vin*0.85,0,1)
    edge=np.clip(fg-cv2.GaussianBlur(fg,(0,0),2.0),0,1)*3
    fg3=fg[...,None]; e3=edge[...,None]
    col=0
    if Lf>0.003: col=col+(GREENB*(1-0.30*fg3)+e3*GEDGE+SPECC)*Lf
    if Lb>0.003: col=col+(REDB*(1-0.42*fg3)+e3*REDGE+REDGLOW)*Lb
    m=INSIDE[...,None]; buf[:]=buf*(1-m)+col*m
    if crack>0:
        pts=[(CX-16,RIM_Y+16),(CX-6,290),(CX-22,330),(CX-4,372),(CX-18,418),(CX+2,462),(CX-10,500)]; k=int(len(pts)*cl(crack))+1
        cv2.polylines(buf,[np.array(pts[:k],np.int32)],False,(0.02,0.02,0.02),2,cv2.LINE_AA); cv2.polylines(buf,[np.array([(x+2,y) for x,y in pts[:k]],np.int32)],False,(0.9,0.95,0.9),1,cv2.LINE_AA)
    gl=np.array([0.85,0.62,0.22],np.float32); lum=min(1.0,0.35+0.65*max(Lf,Lb))
    for M in (RIMM,FOOTM):
        c=(gl*(0.3+0.7*NZM**0.7)[...,None])*lum; mm=M[...,None]; buf[:]=buf*(1-mm)+c*mm
    if rimglow>0: buf+=RIMM[...,None]*np.array([1.0,0.85,0.4],np.float32)*rimglow
def pedestal(buf,Lf,Lb):
    m=_poly([(CX-105,606),(CX+105,606),(CX+126,672),(CX-126,672)]); buf[:]=buf*(1-m[...,None])+np.array([0.03,0.03,0.04],np.float32)*m[...,None]
    top=np.exp(-(((xx-CX)/130.0)**2+((yy-606)/9.0)**2)); buf+=top[...,None]*(np.array([0.5,0.55,0.45],np.float32)*Lf+np.array([0.6,0.12,0.06],np.float32)*Lb)*0.6
BEAMF=cv2.GaussianBlur(_poly([(0,0),(70,0),(CX+150,540),(CX-150,320)]),(0,0),22)
_g=np.random.default_rng(3); MOTE=_g.uniform(0,1,(90,2)); MOTES=_g.uniform(0.3,1,90)
def stage(buf,t,Lf,Lb,orb=0.0,flash=0.0):
    buf[:]=np.array([0.010,0.011,0.016],np.float32)*(0.6+0.4*(1-yy/h))[...,None]
    buf+=(BEAMF*0.20*Lf)[...,None]*np.array([1.0,0.95,0.85],np.float32)
    if orb>0 or Lb>0:
        bigglow(buf,CX,410,150+90*Lb,(1.0,0.86,0.7) if Lb<0.4 else (1.0,0.34,0.12),a=0.5*orb+0.7*Lb)
        for k in range(14):
            an=k*math.pi/7+t*0.15; L_=260*(0.5+0.5*math.sin(t*1.7+k))*(orb+Lb)
            cv2.line(buf,(CX,410),(int(CX+math.cos(an)*L_),int(410+math.sin(an)*L_)),(0.35*orb+0.3*Lb,0.2*orb,0.1*Lb),3,cv2.LINE_AA)
    for (mx,my),mb in zip(MOTE,MOTES):
        x=(mx*w+10*math.sin(t*0.3+mx*9))%w; y=(my*h*0.85-t*6*mb)%(h*0.85)
        if BEAMF[int(y),int(x)]>0.3 or Lb>0.2: buf[int(y),int(x)]+=0.5*mb*max(Lf,Lb)
    pedestal(buf,Lf,Lb)
def _paste(d,patch,x0,y0):
    x0,y0=int(x0),int(y0); sx,sy=max(0,-x0),max(0,-y0)
    if x0>=W or y0>=H or x0+patch.width<=0 or y0+patch.height<=0: return
    d._image.alpha_composite(patch,(max(0,x0),max(0,y0)),(sx,sy))
def dot(d,x,y,r,col,a=1.0):
    if a<=0.01: return
    r=max(1,int(r)); p=Image.new("RGBA",(2*r+4,2*r+4),(0,0,0,0)); ImageDraw.Draw(p).ellipse([2,2,2*r+2,2*r+2],fill=tuple(col)+(int(255*min(1,a)),)); _paste(d,p,x-r-2,y-r-2)
def gdot(d,x,y,r,col,a=1.0):
    if a<=0.01: return
    R=int(r*3.4)+2; p=Image.new("RGBA",(2*R+4,2*R+4),(0,0,0,0)); pd=ImageDraw.Draw(p); c=R+2
    for m,al in [(3.4,0.10),(2.1,0.20),(1.0,1.0)]:
        L=Image.new("RGBA",p.size,(0,0,0,0)); ImageDraw.Draw(L).ellipse([c-r*m,c-r*m,c+r*m,c+r*m],fill=tuple(col)+(int(255*min(1,a)*al),)); p.alpha_composite(L)
    _paste(d,p,x-R-2,y-R-2)
def lab(d,s,y,a,col=(255,255,255),f=None,x=None):
    if a>0.01: txt(d,(x or W//2,y),s,f or CZ(54,800),tuple(col)+(int(255*a),),anchor="mm",stroke=3)
def person_pil(d,x,yb,s,col,a=1.0,arms="up",horns=False,staff=False):
    C=tuple(col)+(int(255*a),); D_=tuple(int(v*0.72) for v in col)+(int(255*a),); wd=lambda v:max(2,int(v*s))
    d.line([(x-7*s,yb-72*s),(x-11*s,yb)],fill=C,width=wd(12)); d.line([(x+7*s,yb-72*s),(x+13*s,yb)],fill=C,width=wd(12))
    d.polygon([(x-18*s,yb-165*s),(x+18*s,yb-165*s),(x+30*s,yb-70*s),(x-30*s,yb-70*s)],fill=C)
    for k in range(-2,3): d.line([(x+k*8*s,yb-150*s),(x+k*11*s,yb-72*s)],fill=D_,width=max(1,int(2*s)))
    d.line([(x-19*s,yb-125*s),(x+19*s,yb-125*s)],fill=D_,width=max(2,int(3*s)))
    d.ellipse([x-12*s,yb-194*s,x+12*s,yb-166*s],fill=C); d.ellipse([x-13*s,yb-198*s,x+13*s,yb-180*s],fill=D_)
    if arms=="up":
        for (sx,tx,ty) in [(-15,-42,-216),(15,40,-208)]: d.line([(x+sx*s,yb-158*s),(x+tx*s,yb+ty*s+yb*0-yb+yb)],fill=C,width=wd(10)) if False else d.line([(x+sx*s,yb-158*s),(x+tx*s,yb+ty*s)],fill=C,width=wd(10)); dot(d,x+tx*s,yb+ty*s,max(3,int(7*s)),col,a)
    else:
        for (sx,tx,ty) in [(-15,-32,-108),(15,36,-118)]: d.line([(x+sx*s,yb-158*s),(x+tx*s,yb+ty*s)],fill=C,width=wd(10)); dot(d,x+tx*s,yb+ty*s,max(3,int(7*s)),col,a)
    if horns: d.line([(x-8*s,yb-192*s),(x-15*s,yb-210*s)],fill=C,width=wd(6)); d.line([(x+8*s,yb-192*s),(x+15*s,yb-210*s)],fill=C,width=wd(6))
    if staff: d.line([(x+36*s,yb-118*s),(x+36*s,yb-236*s)],fill=C,width=wd(6)); d.ellipse([x+28*s,yb-254*s,x+44*s,yb-232*s],fill=C)
RNG=np.random.default_rng(11); PART=[(RNG.uniform(-1,1),RNG.uniform(-1,1),RNG.uniform(0,6.28),RNG.integers(0,2)) for _ in range(70)]
# ------------------------------------------------------------------ scenes
def scene(t,sc):
    n=sc["name"]; lt=t-sc["s"]; D=sc["e"]-sc["s"]; buf=np.zeros((h,w,3),np.float32); hud=[]; flash=0.0; shake=0.0
    Lf=Lb=orb=0.0; rot=0.5*math.sin(t*0.35); crack=0.0; rimg=0.0; cup=False
    if n=="hook":
        cup=True; Lf0=eout((t-EV["lighton"])/1.1); turn=sm((t-EV["turns"])/(EV["blood"]-EV["turns"]+0.7)); orb=sm((t-EV["light"])/0.8)
        Lb=turn; Lf=Lf0*(1-0.88*turn); e=t-EV["blood"]
        if 0<e<1.0: flash=0.55*math.exp(-e*5); shake=max(0,1-e/0.6)*0.6
        def hd(d,t=t):
            lab(d,"GREEN",330,sm((t-EV["green"]+0.1)/0.25)*(1-sm((t-EV["light"]+0.3)/0.3)),JADE,fBig)
            lab(d,"REFLECTED LIGHT",420,sm((t-EV["green"]+0.1)/0.25)*(1-sm((t-EV["light"]+0.3)/0.3)),(200,235,215),CZ(40,700))
            lab(d,"A LIGHT, BEHIND THE GLASS",330,sm((t-EV["light"])/0.3)*(1-sm((t-EV["turns"]+0.2)/0.3)),GOLD,CZ(46,800))
            a=sm((t-EV["blood"]+0.2)/0.25); lab(d,"BLOOD RED",330,a,RUBY,fBig); lab(d,"TRANSMITTED LIGHT",420,a,(255,190,170),CZ(40,700))
        hud.append(hd)
    elif n=="cup":
        cup=True; Lf=1.0; rot=t*0.28
        def hd(d,t=t):
            lab(d,"THE LYCURGUS CUP",290,fa(t,SS("cup")["s"]+0.3,SS("cup")["e"]),GOLD,CZ(64,800))
            lab(d,"ROME · 4TH CENTURY AD",380,sm((t-EV["rome"])/0.3)*(1-sm((t-EV["museum"]+0.3)/0.3)),(240,235,220),CZ(42,700))
            lab(d,"BRITISH MUSEUM · LONDON",380,sm((t-EV["museum"])/0.3),(240,235,220),CZ(42,700))
            a=sm((t-SS("cup")["s"]-2.5)/0.5); x=CX*2+250
            d.line([(x,RIM_Y*2),(x,604*2)],fill=(220,220,230,int(200*a)),width=4); d.line([(x-14,RIM_Y*2),(x+14,RIM_Y*2)],fill=(220,220,230,int(200*a)),width=4); d.line([(x-14,604*2),(x+14,604*2)],fill=(220,220,230,int(200*a)),width=4)
            txt(d,(x+18,(RIM_Y+604)),"ABOUT 16 CM",CZ(30,700),(230,230,240,int(255*a)),anchor="lm",stroke=2)
        hud.append(hd)
    elif n=="myth":
        buf[:]=np.array([0.055,0.04,0.025],np.float32); bigglow(buf,270,420,260,(0.9,0.6,0.25),a=0.18)
        def hd(d,t=t):
            p=cl((t-EV["vine"]+0.3)/(EV["traps"]-EV["vine"]+0.9)); yb=1150
            d.rounded_rectangle([90,430,990,1200],radius=30,outline=(210,170,90,140),width=5)
            person_pil(d,400,yb,3.0,(214,196,160),arms="up"); person_pil(d,780,yb,3.0,(214,196,160),arms="down",staff=True)
            nym=sm((t-EV["amb"])/(EV["vine"]-EV["amb"]+0.4)); person_pil(d,170,yb,2.0,(int(214-120*nym),int(196-20*nym),int(160-70*nym)),arms="down")
            pts=[(400+70*math.sin(k/60*13+0.5)*(1-0.3*k/60),yb-3.0*215*k/60) for k in range(61)]; n_=int(61*p)
            if n_>1: d.line(pts[:n_],fill=(96,170,90,255),width=12,joint="curve")
            for k in range(3,n_,6): x,y=pts[k]; sd=1 if (k//6)%2 else -1; d.ellipse([min(x+sd*8,x+sd*46),y-16,max(x+sd*8,x+sd*46),y+16],fill=(110,190,100,255))
            if p>0.05: d.line([(170+60,yb-70),(300,yb-40),(pts[0][0]-20,yb-10)],fill=(96,170,90,int(255*sm(p*3))),width=10)
            lab(d,"KING LYCURGUS",330,sm((t-EV["lyc"])/0.3)*(1-sm((t-EV["dio"]+0.2)/0.3)),GOLD,CZ(58,800)); lab(d,"THE GOD DIONYSUS",330,sm((t-EV["dio"])/0.3)*(1-sm((t-EV["amb"]+0.2)/0.3)),(230,215,255),CZ(58,800))
            lab(d,"AMBROSIA BECOMES A VINE",330,sm((t-EV["amb"])/0.3)*(1-sm((t-EV["traps"]+0.3)/0.3)),(150,235,150),CZ(58,800)); lab(d,"TRAPPED",330,sm((t-EV["traps"])/0.25),RUBY,fBig)
        hud.append(hd)
    elif n=="cage":
        buf[:]=np.array([0.03,0.045,0.04],np.float32); bigglow(buf,200,470,200,(0.3,0.8,0.5),a=0.18)
        def hd(d,t=t):
            d.rectangle([300,560,430,1150],fill=(60,150,100,int(150*sm((t-SS("cage")["s"])/0.5))),outline=(150,235,190,220),width=4)
            a=sm((t-EV["deep"])/0.4); lift=sm((t-EV["floatw"])/0.6)
            for k,(y,s_) in enumerate([(830,1.4),(1140,1.4)]): person_pil(d,650+int(70*lift),y,s_,(225,210,175),a=a,arms="up" if k==0 else "down")
            b=sm((t-EV["bridges"])/0.5)
            for k,y in enumerate([640,720,790,860,960,1040,1100]):
                bb=cl(b*7-k*0.9)
                if bb>0: d.line([(430,y),(430+(650+int(70*lift)-430-24)*bb,y)],fill=(240,230,190,255),width=5)
            lab(d,"GLASS BLANK: ABOUT 15 MM THICK",330,sm((t-SS("cage")["s"]-0.4)/0.4)*(1-sm((t-EV["deep"]+0.2)/0.3)),(200,240,215),CZ(46,800))
            lab(d,"CARVED SO DEEP…",330,sm((t-EV["deep"])/0.3)*(1-sm((t-EV["bridges"]+0.3)/0.3)),GOLD,CZ(52,800)); lab(d,"TINY BRIDGES",330,sm((t-EV["bridges"])/0.3),(255,240,200),fBig)
            lab(d,"CAGE CUP",1230,sm((t-EV["bridges"]-1)/0.4),(200,240,215),CZ(46,800))
        hud.append(hd)
    elif n=="secret":
        buf[:]=np.array([0.015,0.03,0.05],np.float32)
        for k in range(0,w,30): cv2.line(buf,(k,0),(k,h),(0.02,0.05,0.07),1)
        for k in range(0,h,30): cv2.line(buf,(0,k),(w,k),(0.02,0.05,0.07),1)
        if t>EV["em"]: sy=int(((t-EV["em"])*160)%h); buf+=np.exp(-((yy-sy)/5)**2)[...,None]*np.array([0.1,0.5,0.4],np.float32)*0.35
        def hd(d,t=t):
            lab(d,"THE REAL SECRET",330,fa(t,EV["secret"],EV["y1990"]-0.3),GOLD,CZ(66,800))
            a=sm((t-EV["inside"])/0.5)*(1-sm((t-EV["y1990"]+0.2)/0.4))
            d.rectangle([260,700,820,1000],fill=(60,160,105,int(170*a)),outline=(160,240,200,int(255*a)),width=5)
            for k,(px,py,ph,kind) in enumerate(PART[:36]):
                dot(d,540+px*250,850+py*130+3*math.sin(t*2+ph),4,GOLD if kind else (215,225,235),a*0.9)
            lab(d,"INSIDE THE GLASS",1120,a,(220,245,230),CZ(46,800))
            m=sm((t-EV["y1990"])/0.5)
            if m>0.01:
                d.rectangle([380,1130,780,1160],fill=(70,80,95,int(255*m))); d.rectangle([690,760,730,1130],fill=(70,80,95,int(255*m))); d.polygon([(640,760),(780,760),(770,700),(650,700)],fill=(90,100,120,int(255*m)))
                d.rectangle([480,640,580,900],fill=(110,120,140,int(255*m)),outline=(180,190,210,int(255*m)),width=4); d.rectangle([505,600,555,640],fill=(150,160,180,int(255*m)))
                d.rectangle([470,1085,650,1110],fill=(85,95,110,int(255*m))); d.polygon([(520,1085),(590,1085),(600,1060),(535,1050)],fill=(70,170,110,int(255*m)))
                e=sm((t-EV["em"])/0.5)
                if e>0: d.polygon([(520,900),(560,900),(560,1085),(520,1085)],fill=(120,255,190,int(90*e*(0.6+0.4*math.sin(t*20)))))
            lab(d,"1990",330,sm((t-EV["y1990"])/0.3)*(1-sm((t-EV["em"]+0.3)/0.3)),(255,255,255),fBig)
            lab(d,"ELECTRON MICROSCOPE",330,sm((t-EV["em"])/0.3),(150,255,205),CZ(52,800))
        hud.append(hd)
    elif n=="particles":
        buf[:]=np.array([0.012,0.03,0.025],np.float32)
        def hd(d,t=t):
            zoom=1-0.62*sm((t-EV["thousand"]+0.5)/0.7); R=int(380*zoom); cx,cy=540,850-int(120*(1-zoom))
            d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=(20,60,45,255),outline=(150,235,190,230),width=6)
            for k,(px,py,ph,kind) in enumerate(PART):
                a=sm((t-EV["gold"]-k*0.03)/0.4)
                x=cx+px*R*0.86+10*math.sin(t*0.9+ph); y=cy+py*R*0.86+10*math.cos(t*0.8+ph)
                if (x-cx)**2+(y-cy)**2<(R*0.94)**2: gdot(d,x,y,max(2,int(9*zoom)),GOLD if kind else (220,230,240),a)
            lab(d,"GOLD + SILVER",330,sm((t-EV["gold"])/0.3)*(1-sm((t-EV["nm"]+0.2)/0.3)),GOLD,CZ(62,800))
            nmA=sm((t-EV["nm"])/0.4)*(1-sm((t-EV["thousand"]+0.3)/0.3))
            if nmA>0: d.line([(340,1180),(740,1180)],fill=(255,255,255,int(255*nmA)),width=6); lab(d,"50–100 NM",1240,nmA,(255,255,255),CZ(54,800))
            lab(d,"50–100 NM",330,nmA,(255,255,255),fBig)
            hA=sm((t-EV["hair"]+0.3)/0.5)
            if hA>0:
                d.rounded_rectangle([160,1000,920,1080],radius=40,fill=(120,85,50,int(255*hA))); lab(d,"A HUMAN HAIR: ABOUT 80,000 NM",1040,hA,(255,240,225),CZ(36,800))
                dot(d,540,1150,3,GOLD,hA); lab(d,"1,000 TIMES THINNER",1230,hA,GOLD,CZ(60,800))
        hud.append(hd)
    elif n=="light":
        buf[:]=np.array([0.012,0.015,0.03],np.float32)
        def hd(d,t=t):
            nano=sm((t-EV["nano"]+0.3)/0.4); vis=1-nano
            if vis>0.01:
                back=t>EV["back"]; d.rectangle([480,560,620,1100],fill=(60,150,100,int(140*vis)),outline=(150,235,190,int(230*vis)),width=4)
                for k,(px,py,ph,kind) in enumerate(PART[:34]): dot(d,550+px*60,830+py*250,4,GOLD if kind else (215,225,235),vis*0.9)
                ex,ey=150,1000; d.ellipse([ex-46,ey-26,ex+46,ey+26],outline=(230,230,240,int(255*vis)),width=5); dot(d,ex,ey,12,(230,230,240),vis)
                lx,ly=(900,700) if back else (150,620); gdot(d,lx,ly,22,(255,245,210),vis)
                t0=EV["back"] if back else SS("light")["s"]
                for j in range(8):
                    ph=((t-t0)/2.4+j/8.0)%1.0; hy=640+j*60
                    if not back:
                        if ph<0.4: q=ph/0.4; gdot(d,lx+(480-lx)*q,ly+(hy-ly)*q,7,(255,250,235),vis)
                        elif j%2==0: q=(ph-0.4)/0.4; 
                        if ph>=0.4 and j%2==0 and ph<0.8: q=(ph-0.4)/0.4; gdot(d,480+(ex-480)*q,hy+(ey-hy)*q,9,(90,255,140),vis*(1-0.3*q))
                        elif ph>=0.4 and j%2==1 and ph<0.9: q=(ph-0.4)/0.5; gdot(d,620+(900-620)*q,hy+30*q,7,(255,90,70),vis*(1-q))
                    else:
                        if ph<0.4: q=ph/0.4; gdot(d,lx+(620-lx)*q,ly+(hy-ly)*q,7,(255,250,235),vis)
                        elif j%2==0 and ph<0.55: q=(ph-0.4)/0.15; d.ellipse([620-30*q,hy-30*q,620+30*q,hy+30*q],outline=(90,255,140,int(255*(1-q)*vis)),width=4)
                        elif j%2==1 and 0.4<=ph<0.85: q=(ph-0.4)/0.45; gdot(d,480+(ex-480)*q,hy+(ey-hy)*q,9,(255,80,60),vis)
                lab(d,"REFLECTED: GREEN",330,sm((t-EV["scatter"]+0.6)/0.3)*(1-sm((t-EV["back"]+0.3)/0.3))*vis,JADE,CZ(56,800),)
                lab(d,"TRANSMITTED: RED",330,sm((t-EV["absorbed"])/0.3)*vis,RUBY,CZ(56,800))
                lab(d,"LIGHT FROM THE FRONT",1250,sm((t-EV["front"])/0.3)*(1-sm((t-EV["back"]+0.3)/0.3))*vis,(230,235,245),CZ(42,700)); lab(d,"LIGHT FROM BEHIND",1250,sm((t-EV["back"])/0.3)*vis,(230,235,245),CZ(42,700))
            lab(d,"NANOTECHNOLOGY",700,nano*sm((t-EV["nano"])/0.3),GOLD,fBig); lab(d,"16 CENTURIES BEFORE THE WORD",840,sm((t-EV["word"]+0.6)/0.4),(240,235,225),CZ(44,800))
        hud.append(hd)
    elif n=="debate":
        buf[:]=np.array([0.04,0.03,0.02],np.float32); bigglow(buf,270,420,260,(0.8,0.5,0.2),a=0.12)
        gp=cl((t-EV["precise"]+0.4)/1.4)
        if gp>0:
            hit=t>EV["less"]
            for r_ in range(45):
                for c_ in range(60):
                    if (r_*60+c_)/2700.0>gp: break
                    x,y=30+c_*8,180+r_*8; buf[y:y+7,x:x+7]=(0.22,0.20,0.18)
            if hit:
                a=sm((t-EV["less"])/0.4); x,y=30+41*8,180+17*8; buf[y:y+7,x:x+7]=np.array([1.0,0.85,0.4],np.float32)*(0.6+0.4*math.sin(t*10)); glowpt(buf,x+3,y+3,(1.0,0.8,0.3),r=6,a=1.5*a,spread=26)
        def hd(d,t=t):
            lab(d,"?",600,sm((t-EV["q"])/0.3)*(1-sm((t-EV["precise"]+0.5)/0.3)),GOLD,B.F("BigShoulders-Bold",420))
            lab(d,"≈ 1 IN 2,700",330,sm((t-EV["ppm"])/0.3)*(1-sm((t-EV["luck"]+0.3)/0.3)),GOLD,fBig); lab(d,"SILVER + GOLD, IN PARTS PER MILLION",1240,sm((t-EV["ppm"])/0.3)*(1-sm((t-EV["luck"]+0.3)/0.3)),(235,230,220),CZ(36,700))
            a=sm((t-EV["luck"])/0.3)
            if a>0:
                d.rounded_rectangle([100,560,500,1000],radius=30,fill=(30,22,16,int(245*a)),outline=(210,170,90,int(255*a)),width=5); d.rounded_rectangle([580,560,980,1000],radius=30,fill=(30,22,16,int(245*a*sm((t-EV["recipe"]+0.1)/0.3))),outline=(210,170,90,int(255*a*sm((t-EV["recipe"]+0.1)/0.3))),width=5)
                s_=180; cx_,cy_=300,730; d.rounded_rectangle([cx_-s_/2,cy_-s_/2,cx_+s_/2,cy_+s_/2],radius=26,fill=(240,235,225,int(255*a)))
                for px_,py_ in [(-45,-45),(45,-45),(0,0),(-45,45),(45,45)]: dot(d,cx_+px_,cy_+py_,15,(30,25,20),a)
                lab(d,"LUCK?",900,a,(255,235,200),CZ(52,800),x=300)
                b=sm((t-EV["recipe"])/0.3)
                if b>0:
                    d.rounded_rectangle([700,640,860,830],radius=18,fill=(230,215,175,int(255*b))); 
                    for r_ in range(5): d.line([(720,670+r_*30),(840-(r_%2)*30,670+r_*30)],fill=(120,90,50,int(255*b)),width=4)
                    lab(d,"SECRET RECIPE?",900,b,(255,235,200),CZ(40,800),x=780)
            lab(d,"NO ONE KNOWS FOR SURE",1180,sm((t-EV["noone"])/0.3),(255,255,255),CZ(50,800))
        hud.append(hd)
    elif n=="cracked":
        cup=True; Lf=1.0; rot=0.3; crack=cl((t-EV["cracked"])/0.9); rimg=0.35*sm((t-EV["rim"])/0.4)*(0.7+0.3*math.sin(t*8))
        def hd(d,t=t):
            lab(d,"BRITISH MUSEUM · ROOM 41",290,fa(t,SS("cracked")["s"]+0.3,EV["cracked"]-0.2),(240,235,220),CZ(50,800))
            lab(d,"CRACKED",300,sm((t-EV["cracked"])/0.25),RUBY,fBig); lab(d,"THE METAL RIM STAYS",400,sm((t-EV["rim"])/0.3),GOLD,CZ(50,800))
        hud.append(hd)
    elif n=="modern":
        buf[:]=np.array([0.02,0.025,0.035],np.float32)
        for k in range(0,w,30): cv2.line(buf,(k,0),(k,h),(0.03,0.04,0.055),1)
        for k in range(0,h,30): cv2.line(buf,(0,k),(w,k),(0.03,0.04,0.055),1)
        def hd(d,t=t):
            filmA=sm((t-EV["stamp"]+0.3)/0.6)*(1-0.0); s0=cl((t-EV["changes"])/(EV["hundred"]-EV["changes"]))
            cols=[(70,150,100),(140,180,80),(220,170,60),(240,110,50),(230,60,50)]; idx=s0*4; i=int(min(3,idx)); f=idx-i
            col=tuple(int(cols[i][k]*(1-f)+cols[i+1][k]*f) for k in range(3))
            if filmA>0:
                d.rounded_rectangle([250,640,830,1020],radius=28,fill=col+(int(255*filmA),),outline=(230,235,240,int(255*filmA)),width=5)
                g=cl((t-EV["billion"]+0.2)/0.9)
                for r_ in range(9):
                    for c_ in range(13):
                        if (r_*13+c_)/117.0<=g: dot(d,285+c_*42,672+r_*40,9,(20,25,30),0.55*filmA); d.arc([285+c_*42-9,672+r_*40-9,285+c_*42+9,672+r_*40+9],0,180,fill=(240,230,200,int(220*filmA)),width=2)
                sp=sm((t-EV["sprayed"])/0.3)*(1-sm((t-EV["mini"])/0.5))
                if sp>0:
                    for k in range(40): dot(d,300+(k*97)%520,560+((t*300+k*53)%460),3,GOLD if k%2 else (220,230,240),sp*0.9)
            for k,(e,c) in enumerate([(EV["liquid"],(120,180,255)),(EV["liquid"]+1.2,(245,245,250)),(EV["liquid"]+2.4,(240,190,90))]):
                q=(t-e)/0.9
                if 0<=q<1: y=380+(640-380)*q*q; dot(d,540+(k-1)*160,y,16,c,1-0.0); d.polygon([(540+(k-1)*160-12,y),(540+(k-1)*160+12,y),(540+(k-1)*160,y-46)],fill=c+(255,))
            lab(d,"UNIVERSITY OF ILLINOIS",330,sm((t-EV["illinois"])/0.3)*(1-sm((t-EV["stamp"]+0.2)/0.3)),(230,235,245),CZ(54,800))
            lab(d,"STAMP-SIZED",330,sm((t-EV["stamp"])/0.3)*(1-sm((t-EV["billion"]+0.2)/0.3)),(230,235,245),CZ(60,800))
            lab(d,"1,000,000,000 NANO-CUPS",330,sm((t-EV["billion"])/0.3)*(1-sm((t-EV["mini"]-0.2)/0.3)),GOLD,CZ(50,800))
            lab(d,"EACH ONE, A TINY LYCURGUS CUP",330,sm((t-EV["mini"])/0.3)*(1-sm((t-EV["hundred"]-0.3)/0.3)),GOLD,CZ(44,800))
            lab(d,"100×",1160,sm((t-EV["hundred"])/0.3)*(1-sm((t-EV["diseases"]-0.4)/0.3)),(255,255,255),B.F("BigShoulders-Bold",230)); lab(d,"MORE SENSITIVE TO SALT",1290,sm((t-EV["hundred"])/0.3)*(1-sm((t-EV["diseases"]-0.4)/0.3)),(230,235,245),CZ(40,700))
            da=sm((t-EV["diseases"])/0.5)
            if da>0:
                for k in range(60):
                    x=250+k*9.7; y1=1120+40*math.sin(k*0.3+t*2); y2=1120-40*math.sin(k*0.3+t*2); dot(d,x,y1,5,(120,255,200),da); dot(d,x,y2,5,(255,140,200),da)
                    if k%4==0: d.line([(x,y1),(x,y2)],fill=(220,230,240,int(150*da)),width=2)
                lab(d,"DISEASE DIAGNOSIS · SOMEDAY",940,da,(230,255,240),CZ(46,800))
        hud.append(hd)
    elif n=="end":
        cup=True; rot=t*0.3; tr=sm((t-EV["trapped"])/0.8); Lf=0.55+0.25*math.sin(t*0.8); Lb=0.35+0.45*tr; orb=0.4*tr
        e=t-EV["trapped"]
        if 0<e<0.8: flash=0.35*math.exp(-e*4)
        tf=Lx("And we are only")[1]+0.5
        def hd(d,t=t,tf=tf):
            lab(d,"LIGHT · TRAPPED · IN GLASS",300,sm((t-EV["trapped"])/0.4)*(1-sm((t-tf)/0.4)),GOLD,CZ(54,800))
            if t>tf:
                kk=t-tf; a=sm((kk-0.3)/0.8)*(1-sm((kk-(SS("end")["e"]-tf-1.0))/0.6))
                lg=LOGO.resize((int(LOGO.width*0.5),int(LOGO.height*0.5)),Image.LANCZOS); al=np.array(lg); al[:,:,3]=(al[:,:,3]*a).astype(np.uint8)
                d._image.alpha_composite(Image.fromarray(al),(W//2-lg.width//2,640-lg.height//2)); txt(d,(W//2,1000),"ORBITHOS",CZ(72,600),(255,215,140,int(255*a)),anchor="mm",stroke=2)
        hud.append(hd)
    if cup:
        stage(buf,t,Lf,Lb,orb); cup_render(buf,Lf,Lb,rot,crack,rimg)
        if n=="end":
            tf=Lx("And we are only")[1]+0.5
            if t>tf: buf*=max(0.1,1-(t-tf)*1.1)
    return buf,hud,flash,shake
def post(buf,t,flash,shake):
    small=cv2.resize(buf,(w//4,h//4),interpolation=cv2.INTER_AREA); br=np.maximum(small-0.68,0)
    buf=buf+cv2.resize(cv2.GaussianBlur(br,(0,0),3)+cv2.GaussianBlur(br,(0,0),10)*1.4,(w,h))*0.8
    buf=1-np.exp(-buf*1.35); buf=buf*B.vig*band+B.grain[int(t*30)%8]*0.6+flash
    if shake>0: M=np.float32([[1,0,math.sin(t*40)*7*shake],[0,1,math.cos(t*33)*7*shake]]); buf=cv2.warpAffine(buf,M,(w,h),borderMode=cv2.BORDER_REFLECT)
    return buf
def render(t,sc):
    buf,hud,flash,shake=scene(t,sc); buf=post(buf,t,flash,shake)
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    B.subtitles(d,t); ov.alpha_composite(B.WM,((W-B.WM.width)//2,1775)); img.alpha_composite(ov); return img.convert("RGB")
XS=np.arange(W,dtype=np.float32)[None,:,None]
def compose(t):
    scs=B.SC
    for i in range(1,len(scs)):
        s=scs[i]["s"]
        if abs(t-s)<0.44:
            A=np.asarray(render(t,scs[i-1]),np.float32); Bn=np.asarray(render(t,scs[i]),np.float32); pos=W/2+(t-s)*W*1.25
            out=np.where(XS<pos,Bn,A); dx=XS-pos
            core=np.exp(-(dx/16.0)**2); left=np.exp(-((dx+70)/70.0)**2)*(dx<0); right=np.exp(-((dx-90)/90.0)**2)*(dx>0)
            out=out+core*230+left*np.array([25,110,55],np.float32)+right*np.array([120,20,15],np.float32)
            return Image.fromarray(np.clip(out,0,255).astype(np.uint8))
    return render(t,B.scene_at(t))
TOTAL=B.TOTAL
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
