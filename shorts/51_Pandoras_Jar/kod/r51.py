import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid51")
for p in ["/home/claude/vid51","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
import drawkit as K
from drawkit import ink, outl, wash, glow, part, dl, circ_pts, rotp, dashl
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= palette (Art Nouveau poster, Mucha-like) =================
CREAM=(0.95,0.91,0.80); SAGE=(0.56,0.63,0.48); SAGED=(0.36,0.44,0.32); ROSE=(0.86,0.62,0.56); GOLDA=(0.86,0.66,0.30); TEALA=(0.20,0.40,0.42)
LINEC=(0.22,0.14,0.10); TERRA=(0.74,0.40,0.24); SKINA=(0.96,0.84,0.72); HAIR=(0.70,0.36,0.18); PLUM=(0.40,0.20,0.30); DUSK=(0.24,0.20,0.30)
K.INK=LINEC
cLine=(56,36,26); cGold=(220,168,76); cCream=(244,232,206); cRose=(170,70,58); cTeal=(52,102,108)
FIT=P.FD+"Italiana-Regular.ttf"; FPO=P.FD+"PoiretOne-Regular.ttf"; FGR="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
_IF={}
def _f(path,s):
    k=(path,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(path,s)
    return _IF[k]
_CZF={}
def _cz(n):
    if n not in _CZF:
        f=ImageFont.truetype("/home/claude/vid51/Cinzel.ttf",n); f.set_variation_by_axes([700]); _CZF[n]=f
    return _CZF[n]
def ttl(d,s,x,y,fs=100,a=1.0,sc=1.0,col=cLine,font=None,stroke=0):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc*0.82); f=_f(font,n) if font else _cz(n)
    while f.getlength(s)>1000 and n>20: n-=6; f=_f(font,n) if font else _cz(n)
    kw=dict(stroke_width=3,stroke_fill=(250,240,220,int(220*a))) if stroke else {}
    d.text((x,y),s,font=f,fill=col+(int(255*a),),anchor="mm",**kw)
_CT={}
def cart(d,s,x,y,fs=50,a=1.0,sc=1.0,kind="sage"):
    """art-nouveau cartouche: rounded plaque with double gold rule and corner dots"""
    if a<=0.01 or sc<=0.02: return
    k=(s,fs,kind)
    if k not in _CT:
        f=_f(FPO,fs); d0=ImageDraw.Draw(Image.new("RGBA",(4,4))); bb=d0.textbbox((0,0),s,font=f)
        tw,th=bb[2]-bb[0],bb[3]-bb[1]; px,py=int(fs*0.8),int(fs*0.42); m=16
        im=Image.new("RGBA",(tw+2*px+2*m,th+2*py+2*m),(0,0,0,0)); dd=ImageDraw.Draw(im)
        bg,fg={"sage":((92,108,80),cCream),"rose":((176,96,86),cCream),"cream":((244,232,206),cLine),"teal":((40,84,90),cCream)}[kind]
        W_,H_=tw+2*px,th+2*py
        dd.rounded_rectangle((m,m,m+W_,m+H_),radius=H_//2,fill=bg+(250,),outline=cLine+(255,),width=4)
        dd.rounded_rectangle((m+8,m+8,m+W_-8,m+H_-8),radius=(H_-16)//2,outline=cGold+(255,),width=2)
        for cx in (m+H_//2-6,m+W_-H_//2+6): dd.ellipse((cx-5,m+H_/2-5,cx+5,m+H_/2+5),fill=cGold+(255,))
        dd.text((m+px-bb[0],m+py-bb[1]),s,font=f,fill=fg+(255,),stroke_width=1,stroke_fill=fg+(255,)); _CT[k]=im
    im=_CT[k]
    if abs(sc-1)>0.01: q=max(0.05,round(sc*20)/20); im=im.resize((max(1,int(im.width*q)),max(1,int(im.height*q))),Image.BILINEAR)
    if a<0.99: ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); im=Image.fromarray(ar)
    paste(d,im,x-im.width/2,y-im.height/2)
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
def fl(buf,m,col,a=1.0,th=2):
    if a<=0 or m.x1<=m.x0: return
    comp(buf,m,col,sh=0,rim=0,a=a); outl(buf,m,a=a,th=th,fill=0,col=LINEC)
# ================= poster background =================
_g=np.random.default_rng(1508)
def poster(halo=GOLDA,ring=SAGE,ground=SAGED,cx=270,cy=360,R=190):
    img=np.zeros((h,w,3),np.float32); img[:]=CREAM
    mot=cv2.resize(_g.normal(0,1,(10,6)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC); img*=(1-0.02*mot/mot.std())[...,None]
    arch=M().poly([(40,700)]+[(40,200)]+circ_pts(270,200,230,150,math.pi,2*math.pi,50)+[(500,200),(500,700)])
    comp(img,arch,lerpc(CREAM,ring,0.35),sh=0,rim=0)
    comp(img,M().circ(cx,cy,R+26),ring,sh=0,rim=0); comp(img,M().circ(cx,cy,R),halo,sh=0,rim=0)
    rm=M()
    for k in range(36):
        an=k*math.pi/18; rm.line((cx+math.cos(an)*(R+4),cy+math.sin(an)*(R+4)),(cx+math.cos(an)*(R+22),cy+math.sin(an)*(R+22)),2)
    comp(img,rm,LINEC,sh=0,rim=0,a=0.7)
    for rr in (R*0.92,R*0.78): comp(img,M().pline(circ_pts(cx,cy,rr,n=120),2),lerpc(halo,LINEC,0.35),sh=0,rim=0)
    dots=M()
    for k in range(24): an=k*math.pi/12; dots.circ(cx+math.cos(an)*R*0.85,cy+math.sin(an)*R*0.85,3)
    comp(img,dots,CREAM,sh=0,rim=0,a=0.8)
    outl(img,M().circ(cx,cy,R+26),a=1,th=2,fill=0); outl(img,M().circ(cx,cy,R),a=1,th=1,fill=0)
    outl(img,arch,a=1,th=2,fill=0)
    comp(img,M().rect(40,600,500,700),ground,sh=0,rim=0); outl(img,M().rect(40,600,500,700),a=1,th=2,fill=0)
    # mosaic band
    mb=M()
    for k in range(23): x=44+k*20; mb.rect(x,612,x+12,624)
    comp(img,mb,GOLDA,sh=0,rim=0,a=0.85)
    # outer frame with floral corners
    fr=M().rect(14,14,w-14,22).rect(14,h-22,w-14,h-14).rect(14,14,22,h-14).rect(w-22,14,w-14,h-14); comp(img,fr,SAGED,sh=0,rim=0);
    for (x,y) in ((28,28),(w-28,28),(28,h-28),(w-28,h-28)):
        fm=M()
        for k in range(5): an=k*2*math.pi/5; fm.ell(x+math.cos(an)*9,y+math.sin(an)*9,7,4,ang=math.degrees(an))
        fl(img,fm,ROSE,1.0,1); comp(img,M().circ(x,y,4),GOLDA,sh=0,rim=0)
    return img
BG_GOLD=poster()
BG_ROSE=poster(halo=ROSE,ring=GOLDA,ground=TEALA)
BG_TEAL=poster(halo=(0.50,0.66,0.66),ring=ROSE,ground=SAGED)
BG_DUSK=poster(halo=(0.52,0.44,0.58),ring=SAGE,ground=PLUM)
# ================= figures =================
def pandora(buf,x,y,s,t,a=1.0,lift=0.0,look=0.0):
    sw=math.sin(t*1.6)
    # flowing hair (behind)
    hm=M()
    for k in range(7):
        pts=[(x-18*s-k*5*s-q*70*s,y-300*s+q*230*s+18*s*math.sin(q*5+t*2+k)) for q in np.linspace(0,1,24)]
        hm.pline(pts,(12-k)*s)
    fl(buf,hm,HAIR,a,1)
    # dress with drapery
    dress=M().poly([(x-40*s,y-210*s),(x+30*s,y-210*s),(x+60*s,y),(x-70*s,y)])
    fl(buf,dress,ROSE,a)
    dm=M()
    for k in range(5): dm.pline([(x-30*s+k*18*s+8*s*math.sin(q*4+sw+k),y-200*s+q*196*s) for q in np.linspace(0,1,16)],1.5)
    ink(buf,dm,0.55*a)
    neck=M().rect(x-8*s,y-236*s,x+8*s,y-208*s); fl(buf,neck,SKINA,a,1)
    head=M().ell(x+4*s,y-262*s,26*s,30*s); fl(buf,head,SKINA,a)
    nose=M().poly([(x+28*s,y-266*s),(x+36*s,y-252*s),(x+26*s,y-250*s)]); comp(buf,nose,SKINA,sh=0,rim=0,a=a)
    ink(buf,M().line((x+14*s,y-268*s),(x+22*s,y-266*s),2),a)
    crown=M().pline(circ_pts(x+4*s,y-262*s,30*s,34*s,math.pi*1.05,math.pi*1.95,30),6*s); fl(buf,crown,GOLDA,a,1)
    for k in range(5):
        an=math.pi*(1.1+0.2*k); comp(buf,M().circ(x+4*s+math.cos(an)*36*s,y-262*s+math.sin(an)*40*s,5*s),ROSE,sh=0,rim=0,a=a)
    hair2=M().poly([(x-24*s,y-290*s),(x+20*s,y-294*s),(x+10*s,y-270*s),(x-30*s,y-240*s)]); fl(buf,hair2,HAIR,a,1)
    # arms holding/lifting
    ar=M().line((x+20*s,y-196*s),(x+60*s,y-150*s),12*s).line((x+60*s,y-150*s),(x+90*s,y-150*s-50*s*lift),10*s)
    fl(buf,ar,SKINA,a,1)
def pithos(buf,x,y,s,a=1.0,lid=0.0,t=0.0,col=TERRA):
    body=M().poly([(x-20*s,y),(x-56*s,y-60*s),(x-70*s,y-130*s),(x-60*s,y-180*s),(x-34*s,y-200*s),(x+34*s,y-200*s),(x+60*s,y-180*s),(x+70*s,y-130*s),(x+56*s,y-60*s),(x+20*s,y)])
    fl(buf,body,col,a)
    bm=M()
    for yy_ in (150,110,70): bm.pline([(x-62*s+abs(math.sin(q*math.pi))*0,y-yy_*s+6*s*math.sin(q*math.pi)) for q in np.linspace(0,1,20)] if False else [(x-66*s*math.sin(q*math.pi*0.5+0.6),y-yy_*s) for q in (0,)],1)
    bands=M().rect(x-68*s,y-150*s,x+68*s,y-142*s).rect(x-60*s,y-96*s,x+60*s,y-90*s)
    comp(buf,bands,LINEC,sh=0,rim=0,a=0.7*a)
    wave=M().pline([(x-64*s+k*8*s,y-120*s+5*s*math.sin(k*1.2)) for k in range(17)],2); ink(buf,wave,a*0.7,col=CREAM)
    rim=M().rect(x-38*s,y-212*s,x+38*s,y-198*s); fl(buf,rim,col,a,1)
    if lid<1:
        ly=y-214*s-40*s*lid; lx=x+30*s*lid
        lm=M().poly(rotp([(lx-42*s,ly),(lx+42*s,ly),(lx+30*s,ly-12*s),(lx-30*s,ly-12*s)],0.5*lid,lx,ly)); fl(buf,lm,col,a,1)
        comp(buf,M().circ(lx,ly-16*s,6*s),GOLDA,sh=0,rim=0,a=a*(1-lid))
def wisps(buf,x,y,t,amt,a=1.0,n=7):
    if amt<=0: return
    for k in range(n):
        an=-math.pi/2+(k-(n-1)/2)*0.32; L=60+260*amt*(0.6+0.4*((k*37)%10)/10)
        pts=[(x+math.cos(an)*L*q+22*math.sin(q*6+t*3+k)*q,y+math.sin(an)*L*q) for q in np.linspace(0,1,30)]
        m=M().pline(pts,max(1,9*(1-amt*0.3))); fl(buf,m,lerpc(DUSK,PLUM,(k%3)/2),a*min(1,amt*2),1)
        hx,hy=pts[-1]; mm=M().ell(hx-8,hy,8,4,ang=30).ell(hx+8,hy,8,4,ang=-30); fl(buf,mm,DUSK,a*min(1,amt*2),1)
def hopelight(buf,x,y,t,a=1.0):
    if a<=0: return
    glow(buf,x,y,30,(0.6,0.5,0.2),0.6*a)
    fw=math.sin(t*8)*0.4
    m=M().poly([(x,y),(x-22,y-14-8*fw),(x-26,y+6),(x,y+2)]).poly([(x,y),(x+22,y-14-8*fw),(x+26,y+6),(x,y+2)])
    fl(buf,m,(1.0,0.86,0.45),a,1)
def personsil(buf,x,y,s,a=1.0,col=SAGED):
    m=M().circ(x,y-160*s,14*s).poly([(x-18*s,y-144*s),(x+18*s,y-144*s),(x+14*s,y-70*s),(x-14*s,y-70*s)]).line((x-6*s,y-72*s),(x-8*s,y),8*s).line((x+6*s,y-72*s),(x+8*s,y),8*s)
    fl(buf,m,col,a,1)
def grapes(buf,x,y,a=1.0):
    m=M()
    for r_ in range(4):
        for c_ in range(4-r_): m.circ(x-15*(3-r_)/2+c_*15,y+r_*13,7)
    fl(buf,m,PLUM,a,1); fl(buf,M().ell(x+8,y-12,12,6,ang=-20),SAGE,a,1)
def wheat(buf,x,y,a=1.0):
    m=M().line((x,y),(x,y-70),2)
    for k in range(6): m.ell(x-6,y-30-k*7,6,3,ang=-30).ell(x+6,y-30-k*7,6,3,ang=30)
    fl(buf,m,GOLDA,a,1)
def olive(buf,x,y,a=1.0):
    m=M().line((x-30,y),(x+30,y-20),2)
    for k in range(4): m.ell(x-20+k*16,y-6-k*5,8,4,ang=-30)
    fl(buf,m,SAGE,a,1); fl(buf,M().ell(x+6,y+6,7,9),SAGED,a,1)
def scroll_(buf,x,y,wd,ht,a=1.0):
    m=M().rect(x-wd/2,y-ht/2,x+wd/2,y+ht/2); fl(buf,m,CREAM,a)
    for sx in (-1,1): fl(buf,M().ell(x+sx*wd/2,y,12,ht/2+8),lerpc(CREAM,GOLDA,0.4),a,1)
    lm=M()
    for k in range(4): lm.line((x-wd/2+20,y-ht/2+20+k*18),(x+wd/2-20-(k%2)*30,y-ht/2+20+k*18),1.5)
    ink(buf,lm,0.35*a)
def boxx(buf,x,y,s,a=1.0,lid=0.0):
    m=M().rect(x-40*s,y-50*s,x+40*s,y); fl(buf,m,(0.62,0.44,0.26),a)
    lm=M().poly(rotp([(x-44*s,y-50*s),(x+44*s,y-50*s),(x+44*s,y-64*s),(x-44*s,y-64*s)],-0.6*lid,x-44*s,y-50*s)); fl(buf,lm,(0.70,0.50,0.30),a,1)
    comp(buf,M().rect(x-6*s,y-40*s,x+6*s,y-28*s),GOLDA,sh=0,rim=0,a=a)
def erasmus(buf,x,y,s,a=1.0):
    m=M().poly([(x-50*s,y),(x-40*s,y-120*s),(x+40*s,y-120*s),(x+50*s,y)]); fl(buf,m,(0.20,0.20,0.24),a)
    fl(buf,M().ell(x,y-150*s,24*s,30*s),SKINA,a); ink(buf,M().poly([(x+22*s,y-152*s),(x+30*s,y-140*s),(x+20*s,y-138*s)]),a,col=SKINA)
    fl(buf,M().poly([(x-30*s,y-160*s),(x-26*s,y-182*s),(x+26*s,y-186*s),(x+32*s,y-162*s)]),(0.15,0.15,0.18),a,1)
    fl(buf,M().rect(x-24*s,y-120*s,x+24*s,y-108*s),(0.50,0.30,0.20),a,1)
def book(buf,x,y,a=1.0):
    m=M().poly([(x-120,y),(x,y-14),(x+120,y),(x+120,y-140),(x,y-154),(x-120,y-140)]); fl(buf,m,CREAM,a)
    ink(buf,M().line((x,y-14),(x,y-154),2),a)
    lm=M()
    for k in range(5): lm.line((x-100,y-120+k*20),(x-14,y-130+k*20),1.2); lm.line((x+14,y-130+k*20),(x+100,y-120+k*20),1.2)
    ink(buf,lm,0.35*a)
# ================= scenes =================
def s_hook(t,sc):
    tt=max(t,-1.0)
    buf=BG_GOLD.copy(); hud=[]
    pandora(buf,230,600,1.25,tt,1.0,lift=0.0)
    pithos(buf,370,600,0.95,1.0,lid=0.0,t=tt)
    bx=sm((tt-EV["famous"]+0.3)/0.4)
    if bx>0:
        boxx(buf,100,680,0.9,bx); xm=M(); dl(xm,[(55,600),(145,690)],sm((tt-EV["never"]+0.1)/0.3),6); dl(xm,[(145,600),(55,690)],sm((tt-EV["never"]-0.1)/0.3),6); comp(buf,xm,(0.75,0.15,0.12),sh=0,rim=0,a=bx)
    def hd(d,t=t):
        k0=1.0 if t<0.4 else ap(t,-1,EV["famous"])
        ttl(d,"PANDORA",540,150,130,a=k0,col=cLine)
        cart(d,"NEVER OPENED A BOX",540,265,50,a=k0,kind="rose")
        cart(d,"THE MOST FAMOUS BOX…",540,170,52,a=ap(t,EV["famous"],sc["e"]+1),sc=pop(t,EV["famous"]-0.1),kind="sage")
        ttl(d,"…WASN’T A BOX",540,275,84,a=ap(t,EV["never"],sc["e"]+1),sc=pop(t,EV["never"]-0.1),col=cRose,stroke=2)
    hud.append(hd); return buf,hud
def s_myth(t,sc):
    pO=sm((t-EV["lid"]+0.3)/0.4)
    buf=BG_GOLD*(1-pO)+BG_DUSK*pO; hud=[]
    zb=sm((t-EV["zeus"]+0.3)/0.4)*(1-sm((t-EV["gift"])/0.4))
    if zb>0:
        bm=M().poly([(260,190),(300,190),(270,260),(310,260),(240,370),(262,290),(226,290)]); fl(buf,bm,GOLDA,zb)
        glow(buf,270,280,60,(0.5,0.4,0.1),0.3*zb)
    pandora(buf,220,600,1.25,t,sm((t-EV["first"]+0.6)/0.6),lift=sm((t-EV["lid"]+0.2)/0.4))
    gf=sm((t-EV["gift"]+0.2)/0.4)*(1-pO)
    if gf>0:
        for k in range(6):
            an=-math.pi*0.9+k*0.33; gx,gy=270+math.cos(an)*200,360+math.sin(an)*200
            comp(buf,M().circ(gx,gy,12),GOLDA,sh=0,rim=0,a=gf); outl(buf,M().circ(gx,gy,12),a=gf,th=1,fill=0)
            ink(buf,M().line((gx,gy),(270+math.cos(an)*120,360+math.sin(an)*120),1.2),0.4*gf)
    jv=sm((t-EV["sealed"]+0.3)/0.4)
    if jv>0:
        lid=sm((t-EV["lid"]+0.1)/0.5)
        pithos(buf,380,600,0.95,jv,lid=lid,t=t)
        ins=sm((t-EV["sick"]+0.3)/0.4)*(1-sm((t-EV["lid"])/0.3))
        if ins>0:
            for k,(lab_t) in enumerate((EV["sick"],EV["toil"],EV["evil"])):
                q=sm((t-lab_t+0.2)/0.3)
                if q>0: comp(buf,M().circ(350+k*30,470,10*q),DUSK,sh=0,rim=0,a=ins)
        wisps(buf,380,400,t,sm((t-EV["escaped"]+0.3)/1.4),1.0)
        hopelight(buf,380,395,t,sm((t-EV["hope"]+0.2)/0.5))
    def hd(d,t=t):
        cart(d,"GREEK MYTH",540,150,46,a=ap(t,EV["greek"],EV["first"]),kind="cream")
        ttl(d,"ZEUS’ ORDER",540,250,96,a=ap(t,EV["zeus"],EV["first"]),sc=pop(t,EV["zeus"]-0.1))
        ttl(d,"THE FIRST WOMAN",540,190,88,a=ap(t,EV["first"],EV["gift"]),sc=pop(t,EV["first"]-0.1),col=cRose,stroke=2)
        cart(d,"A GIFT FROM EACH GOD",540,170,48,a=ap(t,EV["gift"],EV["sealed"]),kind="sage")
        cart(d,"…AND A SEALED CONTAINER",540,170,46,a=ap(t,EV["sealed"],EV["sick"]),sc=pop(t,EV["sealed"]-0.1),kind="teal")
        for k,(e,s_) in enumerate((("sick","SICKNESS"),("toil","TOIL"),("evil","EVERY EVIL"))):
            cart(d,s_,540,150+k*90,44,a=ap(t,EV[e],EV["lid"]),sc=pop(t,EV[e]-0.1),kind="rose")
        ttl(d,"ALL ESCAPED…",540,190,96,a=ap(t,EV["escaped"],EV["hope"]),sc=pop(t,EV["escaped"]-0.1),col=cLine,stroke=2)
        ttl(d,"…EXCEPT HOPE",540,190,96,a=ap(t,EV["hope"]-0.2,sc["e"]+1),sc=pop(t,EV["hope"]-0.3),col=(150,96,20),stroke=2)
    hud.append(hd); return buf,hud
def s_jar(t,sc):
    pD=sm((t-EV["diog"]+0.3)/0.4)
    buf=BG_TEAL.copy(); hud=[]
    a1=1-pD
    if a1>0:
        sr=sm((t-EV["hesiod"]+0.3)/0.4)*(1-sm((t-EV["jar"]+0.1)/0.4))
        if sr>0: scroll_(buf,270,360,340,160,sr)
        jv=sm((t-EV["jar"]+0.3)/0.4)
        if jv>0:
            pithos(buf,250,600,1.45,a1*jv,lid=1.0,t=t)
            pv=sm((t-EV["tall"]+0.2)/0.4); personsil(buf,400,600,1.45,a1*pv)
            ink(buf,dl(M(),[(470,600),(470,600-215*1.45*pv)],1.0,1.5),a1*pv)
            wv=sm((t-EV["wine"]+0.2)/0.3)
            if wv>0: grapes(buf,110,230,a1*wv); olive(buf,270,190,a1*sm((t-EV["wine"]-0.4)/0.3)); wheat(buf,430,260,a1*sm((t-EV["wine"]-0.8)/0.3))
    if pD>0:
        jm=M().poly(rotp([(270-20,560),(270-56,500),(270-70,430),(270-60,380),(270-34,360),(270+34,360),(270+60,380),(270+70,430),(270+56,500),(270+20,560)],math.pi/2,270,460))
        fl(buf,jm,TERRA,pD)
        mouth=M().ell(170,460,16,38); fl(buf,mouth,(0.2,0.12,0.08),pD,1)
        personsil(buf,150,560,0.75,pD,col=(0.55,0.50,0.44)); comp(buf,M().ell(130,456,16,6),(0.95,0.95,0.9),sh=0,rim=0,a=pD)
        lm=M().rect(100,470,116,500); fl(buf,lm,GOLDA,pD,1); glow(buf,108,485,20,(0.5,0.4,0.1),0.5*pD*(0.8+0.2*math.sin(t*9)))
    def hd(d,t=t):
        cart(d,"HESIOD · c. 700 BC",540,150,46,a=ap(t,EV["hesiod"],EV["jar"]),kind="cream")
        ttl(d,"πίθος",540,730,110,a=ap(t,EV["pithos"],EV["jar"]),sc=pop(t,EV["pithos"]-0.1),font=FGR,col=cLine)
        ttl(d,"“PITHOS”",540,260,100,a=ap(t,EV["pithos"],EV["diog"]),sc=pop(t,EV["pithos"]-0.1),col=cRose,stroke=2)
        cart(d,"A HUGE CLAY JAR",540,370,48,a=ap(t,EV["jar"],EV["diog"]),kind="teal")
        cart(d,"AS TALL AS A PERSON",540,1240,46,a=ap(t,EV["tall"],EV["diog"]),kind="rose")
        ttl(d,"DIOGENES",540,200,100,a=ap(t,EV["diog"],sc["e"]+1),sc=pop(t,EV["diog"]-0.1))
        cart(d,"SUPPOSEDLY LIVED IN ONE",540,310,46,a=ap(t,EV["lived"]-0.3,sc["e"]+1),kind="sage")
    hud.append(hd); return buf,hud
def s_error(t,sc):
    pS=sm((t-EV["stuck"]+0.3)/0.4); pR=sm((t-EV["nexttime"]+0.3)/0.4)
    buf=BG_ROSE*(1-pR)+BG_GOLD*pR; hud=[]
    a1=1-pS; a2=pS*(1-pR); a3=pR
    if a1>0:
        erasmus(buf,130,600,1.3,a1*sm((t-EV["y1508"]+0.3)/0.4))
        book(buf,350,560,a1*sm((t-EV["latin"]+0.3)/0.4))
        bv=sm((t-EV["abox"]+0.2)/0.4)
        if bv>0: boxx(buf,350,380,1.0,a1*bv)
    if a2>0:
        ink(buf,dl(M(),[(70,330),(470,330)],sm((t-EV["stuck"]+0.1)/0.6),4),a2)
        ink(buf,M().poly([(470,318),(494,330),(470,342)]),a2*sm((t-EV["stuck"]-0.3)/0.3))
        for k in range(4):
            q=sm((t-EV["painting"]+0.2-k*0.18)/0.3)
            if q>0:
                x=100+k*110; fr=M().rect(x-36,400,x+36,500); fl(buf,fr,GOLDA,a2*q); comp(buf,M().rect(x-28,408,x+28,492),[ROSE,TEALA,SAGE,PLUM][k],sh=0,rim=0,a=a2*q)
                boxx(buf,x,486,0.45,a2*q)
    if a3>0:
        pandora(buf,230,600,1.25,t,a3); pithos(buf,370,600,0.95,a3,lid=0.0,t=t)
    def hd(d,t=t):
        ttl(d,"1508",540,180,130,a=ap(t,EV["y1508"],EV["latin"]),sc=pop(t,EV["y1508"]-0.1),col=cLine)
        cart(d,"ERASMUS",540,300,52,a=ap(t,EV["erasmus"],EV["latin"]),sc=pop(t,EV["erasmus"]-0.1),kind="cream")
        cart(d,"RETOLD IN LATIN",540,170,50,a=ap(t,EV["latin"],EV["pyxis"]),kind="sage")
        ttl(d,"“PYXIS”",540,190,110,a=ap(t,EV["pyxis"],EV["stuck"]),sc=pop(t,EV["pyxis"]-0.1),col=cRose,stroke=2)
        cart(d,"= A BOX",540,300,56,a=ap(t,EV["abox"],EV["stuck"]),sc=pop(t,EV["abox"]-0.1),kind="teal")
        ttl(d,"1508 – TODAY",540,560,64,a=ap(t,EV["stuck"],EV["painting"])*0+ap(t,EV["stuck"],EV["nexttime"]),col=cLine)
        ttl(d,"500 YEARS",540,190,110,a=ap(t,EV["five"],EV["nexttime"]),sc=pop(t,EV["five"]-0.1),col=cRose,stroke=2)
        cart(d,"EVERY PAINTING · EVERY PHRASE",540,1220,42,a=ap(t,EV["painting"],EV["nexttime"]),kind="sage")
        cart(d,"REMEMBER:",540,170,52,a=ap(t,EV["remember"],sc["e"]+1),sc=pop(t,EV["remember"]-0.1),kind="rose")
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,myth=s_myth,jar=s_jar,error=s_error)
BAND=(1-0.40*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.20*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.007,(h,w,1)).astype(np.float32) for i in range(6)]
TR=0.32; TOTAL=B.TOTAL; LOOPD=0.6
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
_yv=np.arange(h,dtype=np.float32)
def vinewipe(b1,b2,u,t):
    """art-nouveau whiplash curve sweeps across; behind it the next poster"""
    X=sm(u)*(w+260)-130+70*np.sin(_yv/130+1.3)+26*np.sin(_yv/47)
    m=(xx<X[:,None])[...,None]; out=np.where(m,b2,b1)
    d=np.abs(xx-X[:,None]); line=(d<5)[...,None]; gold=((d>=5)&(d<9))[...,None]
    out=np.where(gold,np.array(GOLDA,np.float32),out); out=np.where(line,np.array(LINEC,np.float32),out)
    lm=M()
    for k in range(9):
        y=60+k*105; x=float(X[min(h-1,y)]); sd=1 if k%2 else -1
        lm.ell(x+sd*18,y,20,8,ang=sd*35)
    comp(out,lm,SAGE,sh=0,rim=0); outl(out,lm,a=1,th=1,fill=0)
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
        buf=vinewipe(b1,b2,u,t); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    buf=np.clip(buf,0,1.2)*PT*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
