import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid62")
for p in ["/home/claude/vid62","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= painted runestone =================
_g=np.random.default_rng(62)
def _nz(s): n=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),s); return n/n.std()
_a,_b,_c,_d=_nz(0.6),_nz(2.0),_nz(8),_nz(30)
spk=(_g.random((h,w))<0.025).astype(np.float32); spk=cv2.GaussianBlur(spk,(0,0),0.6)*3
spw=(_g.random((h,w))<0.015).astype(np.float32); spw=cv2.GaussianBlur(spw,(0,0),0.7)*3
gray=0.56+0.05*_a+0.05*_b+0.05*_c+0.04*_d-0.25*spk+0.22*spw
STONE=np.stack([gray*1.02,gray*1.0,gray*0.97],-1).astype(np.float32)
lich=np.clip((_d*0.8+_c*0.4-1.3)*1.2,0,1)*np.clip(0.5+_b,0,1)
STONE=STONE*(1-lich[...,None]*0.6)+lich[...,None]*np.array((0.78,0.70,0.36),np.float32)*0.6*(0.8+0.2*_a[...,None])
# slab outline
SLAB=M().poly([(40,668)]+[(40+0*k,200) for k in range(1)]+[(270+230*math.cos(a),210-150*math.sin(a)) for a in np.linspace(math.pi,0,40)]+[(500,668)]).f()
SLAB=cv2.GaussianBlur(cv2.remap(SLAB,(xx+3*_c).astype(np.float32),(yy+3*_c).astype(np.float32),cv2.INTER_LINEAR),(0,0),1.0)
_rim=np.clip(SLAB-cv2.GaussianBlur(SLAB,(0,0),10),0,1)
def _bg():
    b=np.empty((h,w,3),np.float32); k=np.clip(yy/700,0,1)[...,None]
    b[:]=np.array((0.20,0.24,0.30),np.float32)*(1-k)+np.array((0.42,0.40,0.42),np.float32)*k
    b*=(1+0.05*_d)[...,None]
    hill=M().poly([(0,640)]+[(x,620-30*math.sin(x/90)-10*math.sin(x/31)) for x in range(0,w+10,10)]+[(w,h),(0,h)]).f()
    b=b*(1-hill[...,None])+hill[...,None]*np.array((0.12,0.16,0.12),np.float32)*(1+0.1*_b[...,None])
    grd=np.clip((yy-664)/6,0,1)[...,None]; b=b*(1-grd)+grd*np.array((0.08,0.10,0.09),np.float32)*(1+0.08*_b[...,None])
    return b
BG=_bg()
RED=(0.68,0.19,0.12); BLK=(0.10,0.09,0.09); WHT=(0.90,0.88,0.82); BLU=(0.25,0.38,0.48); OCH=(0.78,0.60,0.30)
def carve(buf,m,depth=1.0,paint=None,pa=1.0,soft=1.1):
    """incised groove lit from the top-left, optionally filled with paint"""
    A=m.f() if isinstance(m,M) else m
    if A.max()<0.01: return
    Ab=cv2.GaussianBlur(A,(0,0),soft)
    gx=cv2.Sobel(Ab,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(Ab,cv2.CV_32F,0,1,ksize=3)
    sh=(gx*0.7+gy*0.7)
    buf*=(1-0.30*Ab*depth)[...,None]
    buf+=(np.clip(sh,0,None)*0.55*depth)[...,None]*np.array((1,1,0.97),np.float32)
    buf*=(1-np.clip(-sh,0,None)*0.65*depth)[...,None]
    if paint is not None:
        Pm=cv2.GaussianBlur(A,(0,0),0.6)*pa*(0.75+0.25*np.clip(0.5+_b*0.5,0,1))
        buf+=(np.array(paint,np.float32)*(0.85+0.15*_a)[...,None]-buf)*Pm[...,None]
def fillpaint(buf,m,col,a=1.0):
    A=(m.f() if isinstance(m,M) else m)*a*(0.80+0.20*np.clip(0.5+_b*0.5,0,1))
    buf+=(np.array(col,np.float32)*(0.88+0.12*_a)[...,None]-buf)*A[...,None]
# rune band along the slab edge
def _band_path():
    pts=[(72,652),(72,215)]+[(270+198*math.cos(a),214-122*math.sin(a)) for a in np.linspace(math.pi,0,48)]+[(468,215),(468,612)]
    out=[];
    for p0,p1 in zip(pts,pts[1:]):
        L=math.hypot(p1[0]-p0[0],p1[1]-p0[1]); n=max(1,int(L/4))
        for k in range(n): out.append((p0[0]+(p1[0]-p0[0])*k/n,p0[1]+(p1[1]-p0[1])*k/n))
    return out
BP=_band_path()
def _band():
    m1=M(); m2=M(); W2=15
    for (x0,y0),(x1,y1) in zip(BP,BP[1:]):
        a=math.atan2(y1-y0,x1-x0); nx,ny=-math.sin(a)*W2,math.cos(a)*W2
        m1.line((x0+nx,y0+ny),(x1+nx,y1+ny),2.6); m2.line((x0-nx,y0-ny),(x1-nx,y1-ny),2.6)
    hx,hy=468,626; m1.ell(hx,hy,22,30); m1.circ(hx,hy+8,5,0)
    edge=np.maximum(m1.f(),m2.f())
    runes=M(); g=np.random.default_rng(7)
    for i in range(0,len(BP)-6,5):
        (x0,y0),(x1,y1)=BP[i],BP[i+1]; a=math.atan2(y1-y0,x1-x0); nx,ny=-math.sin(a),math.cos(a); tx,ty=math.cos(a),math.sin(a)
        if i%35==30: runes.circ(x0,y0,1.8); continue
        hgt=10; runes.line((x0-nx*hgt,y0-ny*hgt),(x0+nx*hgt,y0+ny*hgt),1.8)
        for _ in range(g.integers(1,3)):
            s=g.uniform(-1,1); d=g.choice([-1,1])
            runes.line((x0+nx*hgt*s,y0+ny*hgt*s),(x0+nx*hgt*(s-0.5)+tx*d*6,y0+ny*hgt*(s-0.5)+ty*d*6),1.6)
    return edge,runes.f()
BANDE,BANDR=_band()
# ================= HUD-free carved titles =================
_IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(P.FD+n,s)
    return _IF[k]
def title_mask(s,y=600,fs=44,maxw=330):
    f=_f("NationalPark-Bold.ttf",fs); n=fs
    while f.getlength(s)>maxw and n>14: n-=2; f=_f("NationalPark-Bold.ttf",n)
    L=Image.new("L",(w,h),0); ImageDraw.Draw(L).text((270,y),s,font=f,fill=255,anchor="mm")
    return np.asarray(L).astype(np.float32)/255
def ctitle(buf,s,a,y=582,fs=44,col=RED):
    if a<=0.01: return
    m=title_mask(s,y,fs); carve(buf,m*min(1,a*1.4),1.0,col,a)
def slab(t):
    b=BG.copy(); s=STONE.copy()
    carve(s,BANDE,1.0,None); carve(s,BANDR,0.9,RED,0.95)
    return b,s
def finish_slab(b,s):
    s*=(1-0.25*_rim)[...,None]
    return b*(1-SLAB[...,None])+s*SLAB[...,None]
# ---- carved figures ----
def warrior(s,x,y,sc,horns=0.0,hornfall=0.0,real=False,paint=True):
    m=M()
    m.ell(x,y-150*sc,26*sc,30*sc)                                  # head
    body=M().poly([(x-34*sc,y-118*sc),(x+34*sc,y-118*sc),(x+44*sc,y-20*sc),(x-44*sc,y-20*sc)])
    if paint: fillpaint(s,body,RED,0.9)
    carve(s,np.clip(body.f()-cv2.erode(body.f(),np.ones((5,5),np.uint8)),0,1),1.0,BLK)
    hm=M().ell(x,y-168*sc,30*sc,22*sc); hm.rect(x-30*sc,y-168*sc,x+30*sc,y-156*sc)
    if paint: fillpaint(s,hm,(0.45,0.47,0.50),0.95)
    carve(s,np.clip(hm.f()-cv2.erode(hm.f(),np.ones((5,5),np.uint8)),0,1),1.0,BLK)
    if real:
        g=M(); g.circ(x-11*sc,y-150*sc,9*sc); g.circ(x+11*sc,y-150*sc,9*sc); G=np.clip(g.f()-M().circ(x-11*sc,y-150*sc,5*sc).f()-M().circ(x+11*sc,y-150*sc,5*sc).f(),0,1)
        carve(s,G,1.0,BLK); carve(s,M().line((x,y-190*sc),(x,y-160*sc),3*sc),0.8,BLK)
    else:
        carve(s,M().circ(x-10*sc,y-150*sc,3*sc),1.0,BLK); carve(s,M().circ(x+10*sc,y-150*sc,3*sc),1.0,BLK)
    bd=M().poly([(x-22*sc,y-140*sc),(x+22*sc,y-140*sc),(x,y-104*sc)]); fillpaint(s,bd,OCH,0.9); carve(s,np.clip(bd.f()-cv2.erode(bd.f(),np.ones((3,3),np.uint8)),0,1),0.8,BLK)
    carve(s,np.clip(m.f()-cv2.erode(m.f(),np.ones((5,5),np.uint8)),0,1),1.0,BLK)
    if horns>0:
        for sd in (-1,1):
            dy=hornfall*90*sc; da=hornfall*0.8*sd
            pts=[(x+sd*(28+18*q)*sc+math.sin(da)*q*20,y-170*sc-60*sc*q**1.4+dy) for q in np.linspace(0,1,10)]
            hm2=M()
            for p0,p1,q in zip(pts,pts[1:],np.linspace(1,0.2,9)): hm2.line(p0,p1,12*sc*q+2)
            fillpaint(s,hm2,WHT,horns); carve(s,np.clip(hm2.f()-cv2.erode(hm2.f(),np.ones((3,3),np.uint8)),0,1),horns,BLK)
    # round shield + spear
    sh=M().circ(x-58*sc,y-70*sc,40*sc); fillpaint(s,sh,BLU,0.9)
    carve(s,np.clip(sh.f()-cv2.erode(sh.f(),np.ones((5,5),np.uint8)),0,1),1.0,BLK); carve(s,M().circ(x-58*sc,y-70*sc,9*sc),1.0,WHT)
    for k in range(4): a=k*math.pi/2+0.4; carve(s,M().line((x-58*sc+math.cos(a)*12*sc,y-70*sc+math.sin(a)*12*sc),(x-58*sc+math.cos(a)*36*sc,y-70*sc+math.sin(a)*36*sc),2.5),0.8,BLK)
    carve(s,M().line((x+50*sc,y),(x+50*sc,y-220*sc),4*sc),1.0,BLK); fillpaint(s,M().poly([(x+42*sc,y-220*sc),(x+58*sc,y-220*sc),(x+50*sc,y-250*sc)]),BLK,0.9)
    for dx in (-18,18): carve(s,M().line((x+dx*sc,y-20*sc),(x+dx*sc,y+10*sc),7*sc),1.0,BLK)
def gjermundbu(s,x,y,sc,a=1.0):
    dome=M().ell(x,y,110*sc,95*sc); dome.rect(x-110*sc,y,x+110*sc,y+20*sc); D=dome.f()*(yy<y+20*sc)
    fillpaint(s,D,(0.48,0.50,0.52),0.95*a); carve(s,np.clip(D-cv2.erode(D,np.ones((5,5),np.uint8)),0,1),a,BLK)
    for q in (-0.5,0,0.5): carve(s,M().line((x+q*100*sc,y-92*sc*(1-abs(q)*0.4)),(x+q*110*sc,y+18*sc),5*sc),a,BLK)
    carve(s,M().line((x-110*sc,y+12*sc),(x+110*sc,y+12*sc),6*sc),a,BLK)
    g=M(); g.circ(x-40*sc,y+52*sc,32*sc); g.circ(x+40*sc,y+52*sc,32*sc); g.rect(x-6*sc,y+20*sc,x+6*sc,y+80*sc)
    G=np.clip(g.f()-M().circ(x-40*sc,y+52*sc,22*sc).f()-M().circ(x+40*sc,y+52*sc,22*sc).f(),0,1)
    fillpaint(s,G,(0.40,0.42,0.44),a); carve(s,np.clip(G-cv2.erode(G,np.ones((3,3),np.uint8)),0,1),a,BLK)
    for k in range(9): carve(s,M().circ(x-100*sc+k*25*sc,y+110*sc,6*sc),0.6*a,None)
def vekso(s,x,y,sc,a=1.0):
    dome=M().ell(x,y,60*sc,52*sc); D=dome.f()*(yy<y+8*sc); fillpaint(s,D,OCH,0.9*a); carve(s,np.clip(D-cv2.erode(D,np.ones((5,5),np.uint8)),0,1),a,BLK)
    for sd in (-1,1):
        pts=[(x+sd*(40+60*math.sin(q*1.4))*sc,y-30*sc-120*sc*q+40*sc*q*q) for q in np.linspace(0,1,14)]
        hm=M()
        for p0,p1,q in zip(pts,pts[1:],np.linspace(1,0.3,13)): hm.line(p0,p1,12*sc*q+2)
        fillpaint(s,hm,OCH,a); carve(s,np.clip(hm.f()-cv2.erode(hm.f(),np.ones((3,3),np.uint8)),0,1),a,BLK)
    carve(s,M().circ(x-16*sc,y-10*sc,7*sc),a,BLK); carve(s,M().circ(x+16*sc,y-10*sc,7*sc),a,BLK)
    carve(s,M().poly([(x-8*sc,y),(x+8*sc,y),(x,y+26*sc)]),a,BLK)
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.05,e-0.5,0.25,0.22)
# ================= shots =================
def s_hook(t):
    b,s=slab(t); hf=sm((t-EV["never"]-0.1)/0.7)
    warrior(s,280,520,1.25,horns=max(0.0,1-hf*1.1)+0.0001,hornfall=hf)
    if hf>0: carve(s,M().line((190,190),(370,330),6).line((370,190),(190,330),6),hf,RED)
    ctitle(s,"NO HORNS",ap(t,EV["never"],EV["image"]),fs=56)
    ctitle(s,"ONLY ~150 YEARS OLD",ap(t,EV["image"],99),fs=40)
    return finish_slab(b,s),[]
def s_helmet(t):
    b,s=slab(t); gjermundbu(s,270,350,1.1)
    ctitle(s,"ONE HELMET",ap(t,S("helmet")["s"]+0.2,EV["norway"]),fs=54)
    ctitle(s,"NORWAY 1943",ap(t,EV["norway"]-0.1,EV["gjer"]-0.1),fs=54)
    ctitle(s,"GJERMUNDBU",ap(t,EV["gjer"]-0.1,99),fs=52)
    return finish_slab(b,s),[]
def s_real(t):
    b,s=slab(t); ck=sm((t-EV["horns"]+0.2)/0.5)
    warrior(s,230,530,1.2,real=True)
    if ck>0:
        warrior(s,390,560,0.75,horns=1.0)
        k=sm((t-EV["blade"]+0.3)/0.6); x0,y0=440,200; x1,y1=430-10*k,300+62*k
        carve(s,M().line((x0,y0),(x1,y1),6),ck,BLK); fillpaint(s,M().poly([(x1-14,y1-6),(x1+10,y1-12),(x1-2,y1+16)]),(0.55,0.56,0.58),ck)
    ctitle(s,"ROUND CAP · EYE GUARD",ap(t,EV["rounded"],EV["nohorns"]-0.1),fs=36)
    ctitle(s,"NO HORNS",ap(t,EV["nohorns"]-0.1,EV["battle"]),fs=58)
    ctitle(s,"HORNS = A HANDLE",ap(t,EV["horns"],99),fs=46)
    return finish_slab(b,s),[]
def s_paint(t):
    b,s=slab(t)
    for p0,p1 in (((180,560),(260,260)),((340,560),(260,260)),((260,560),(260,300))): carve(s,M().line(p0,p1,6),1.0,BLK)
    cv_=M().rect(170,280,350,460); fillpaint(s,cv_,WHT,0.95); carve(s,np.clip(cv_.f()-cv2.erode(cv_.f(),np.ones((5,5),np.uint8)),0,1),1.0,BLK)
    k=sm((t-EV["c19"]+0.3)/1.4)
    if k>0:
        fillpaint(s,M().ell(260,370,20,22),RED,k)
        for sd in (-1,1):
            hm=M()
            pts=[(260+sd*(18+10*q),352-30*q) for q in np.linspace(0,1,6)]
            for p0,p1 in zip(pts,pts[1:]): hm.line(p0,p1,5)
            fillpaint(s,hm,OCH,k)
        fillpaint(s,M().rect(236,392,284,446),BLU,k)
    carve(s,M().line((400,520),(330,420),4),1.0,BLK); fillpaint(s,M().circ(330,420,5),RED,1.0)
    ctitle(s,"WHERE FROM?",ap(t,S("opera")["s"]+0.2,EV["c19"]-0.1),fs=54)
    ctitle(s,"1800s PAINTERS",ap(t,EV["c19"]-0.1,99),fs=50)
    return finish_slab(b,s),[]
def s_stage(t):
    b,s=slab(t)
    for sd in (-1,1):
        cm=M().poly([(270+sd*190,170),(270+sd*190,560),(270+sd*130,560),(270+sd*150,170)]); fillpaint(s,cm,RED,0.95)
        for k in range(4): carve(s,M().line((270+sd*(185-k*12),175),(270+sd*(178-k*10),555),2.5),0.8,BLK)
    carve(s,M().line((90,560),(450,560),6),1.0,BLK)
    warrior(s,270,550,1.0,horns=sm((t-EV["costume"]+0.2)/0.6)+0.001)
    ctitle(s,"WAGNER'S RING · 1876",ap(t,EV["y1876"]-0.2,EV["doepler"]),fs=40)
    ctitle(s,"COSTUMES: C. E. DOEPLER",ap(t,EV["doepler"],99),fs=38)
    return finish_slab(b,s),[]
def s_stuck(t):
    b,s=slab(t); k=sm((t-EV["sensation"]+0.3)/1.0)
    for i,(x,y,sc) in enumerate(((270,540,0.9),(150,470,0.55),(390,470,0.55),(160,330,0.4),(380,330,0.4))):
        if i==0 or k>i*0.15: warrior(s,x,y,sc,horns=1.0,paint=True)
    ctitle(s,"THE LOOK STUCK",ap(t,EV["sensation"]-0.1,99),fs=50)
    return finish_slab(b,s),[]
def s_bronze(t):
    b,s=slab(t); k=sm((t-EV["bronze"]+0.4)/0.6)
    vekso(s,190,360,0.85,max(0.02,k)); vekso(s,350,360,0.85,max(0.02,k))
    tl=sm((t-EV["y1700"]+0.3)/1.4)
    if tl>0:
        carve(s,M().line((110,490),(110+320*tl,490),4),1.0,BLK)
        carve(s,M().circ(110,490,7),1.0,OCH)
        if tl>0.98: carve(s,M().circ(430,490,7),1.0,RED)
    ctitle(s,"BRONZE AGE · c. 900 BC",ap(t,EV["bronze"]-0.2,EV["y1700"]),fs=38)
    ctitle(s,"~1,700 YEARS EARLIER",ap(t,EV["y1700"],EV["cerem"]-0.1),fs=42)
    ctitle(s,"CEREMONIAL",ap(t,EV["cerem"]-0.1,99),fs=56)
    return finish_slab(b,s),[]
def s_end(t):
    b,s=slab(t); warrior(s,280,520,1.25,horns=1.0)
    ctitle(s,"REMEMBER",ap(t,EV["remember"]-0.2,99),fs=56)
    return finish_slab(b,s),[]
TR=0.36; TOTAL=B.TOTAL; LOOPD=0.62
SHOTS=[(0.0,s_hook),(S("helmet")["s"],s_helmet),(Lx("It's a rounded")[0]-0.3,s_real),(S("opera")["s"],s_paint),(Lx("Then in 1876")[0]-0.3,s_stage),
       (Lx("The opera was")[0]-0.3,s_stuck),(S("bronze")["s"],s_bronze),(Lx("So next time")[0]-0.3,s_end)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
def turn(img,u):
    """the slab turns about its vertical axis: squeeze to an edge, then open on the carved far face"""
    k=abs(math.cos(math.pi*u)); out=BG.copy()
    if k<0.02: return out
    Mx=np.float32([[k,0,270*(1-k)],[0,1,0]]); sq=cv2.warpAffine(img,Mx,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    sm_=cv2.warpAffine(SLAB,Mx,(w,h),flags=cv2.INTER_LINEAR)
    shade=(0.55+0.45*k)
    return out*(1-sm_[...,None])+sq*sm_[...,None]*shade
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None: buf,_=SHOTS[i][1](t)
    else:
        fa_,fb_,ta,tb,u=pair
        buf,_=(fa_(ta) if u<0.5 else fb_(tb)); buf=turn(buf,u)
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
