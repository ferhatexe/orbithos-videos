import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid50")
for p in ["/home/claude/vid50","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
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
# ================= palette (late-gothic illuminated manuscript) =================
VELL=(0.92,0.86,0.70); INKB=(0.12,0.08,0.06); VERM=(0.78,0.16,0.10); ULTRA=(0.12,0.22,0.62); GOLDL=(0.92,0.72,0.28); VERD=(0.24,0.48,0.30)
ROSEP=(0.88,0.62,0.56); SKINC=(0.94,0.80,0.66); WOODC=(0.52,0.33,0.18); WHITEL=(0.97,0.95,0.88); PURP=(0.46,0.22,0.46)
K.INK=INKB
cGold=(236,190,84); cInk=(36,24,18); cVerm=(196,44,28); cVell=(244,232,204)
CZ="/home/claude/vid50/Cinzel.ttf"
_IF={}
def _f(path,s,wt=None):
    k=(path,s,wt)
    if k not in _IF:
        f=ImageFont.truetype(path,s)
        if wt: f.set_variation_by_axes([wt])
        _IF[k]=f
    return _IF[k]
def ttl(d,s,x,y,fs=96,a=1.0,sc=1.0,col=cGold):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f(CZ,n,800)
    while f.getlength(s)>1000 and n>20: n-=6; f=_f(CZ,n,800)
    d.text((x,y),s,font=f,fill=col+(int(255*a),),anchor="mm",stroke_width=4,stroke_fill=(40,22,12,int(230*a)))
def rubric(d,s,x,y,fs=46,a=1.0,sc=1.0,col=cVerm):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f(P.FD+"Lora-BoldItalic.ttf",n)
    while f.getlength(s)>1000 and n>16: n-=4; f=_f(P.FD+"Lora-BoldItalic.ttf",n)
    d.text((x,y),s,font=f,fill=col+(int(255*a),),anchor="mm")
_IC={}
def initial(d,ch,x,y,sz=150,a=1.0,sc=1.0):
    """illuminated initial: gold letter on a blue/red quartered square with white filigree"""
    if a<=0.01: return
    k=(ch,sz)
    if k not in _IC:
        im=Image.new("RGBA",(sz+16,sz+16),(0,0,0,0)); dd=ImageDraw.Draw(im)
        dd.rectangle((8,8,8+sz,8+sz),fill=(28,52,150,255),outline=(236,190,84,255),width=5)
        dd.rectangle((8+sz//2,8,8+sz,8+sz//2),fill=(176,36,24,255)); dd.rectangle((8,8+sz//2,8+sz//2,8+sz),fill=(176,36,24,255))
        for i in range(8):
            r=sz*0.12; cx=8+sz*(0.15+0.7*(i%4)/3); cy=8+sz*(0.12 if i<4 else 0.88); dd.ellipse((cx-r/3,cy-r/3,cx+r/3,cy+r/3),outline=(250,240,220,200),width=2)
        f=_f(CZ,int(sz*0.8),900); dd.text((8+sz/2,8+sz/2+sz*0.04),ch,font=f,fill=(236,190,84,255),anchor="mm",stroke_width=3,stroke_fill=(60,30,10,255))
        _IC[k]=im
    im=_IC[k]
    if abs(sc-1)>0.01: q=max(0.05,round(sc*20)/20); im=im.resize((max(1,int(im.width*q)),max(1,int(im.height*q))),Image.BILINEAR)
    if a<0.99: ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); im=Image.fromarray(ar)
    paste(d,im,x-im.width/2,y-im.height/2)
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= the page =================
_g=np.random.default_rng(1518)
PAGE=np.zeros((h,w,3),np.float32); PAGE[:]=VELL
_bl=cv2.resize(_g.normal(0,1,(9,5)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC); _bl/=_bl.std(); PAGE*=(1-0.04*_bl)[...,None]
_sp=cv2.GaussianBlur((_g.random((h,w))>0.9985).astype(np.float32),(0,0),1.0)*6; PAGE-=(np.clip(_sp,0,1)*0.25)[...,None]*np.array((0.5,0.6,0.7),np.float32)
PX0,PY0,PX1,PY1=46,150,494,640
def _border(img):
    m=M().rect(18,22,w-18,26).rect(18,h-26,w-18,h-22).rect(18,22,22,h-22).rect(w-22,22,w-18,h-22); comp(img,m,GOLDL,sh=0,rim=0)
    vm=M(); lm=M()
    for k in range(40):
        y=40+k*23; x=30+6*math.sin(k*1.3)
        vm.pline([(x,y),(x+8*math.sin(k),y+12),(x,y+23)],1.6); lm.ell(x+9*(1 if k%2 else -1),y+10,6,3,ang=(30 if k%2 else -30))
        x=w-30+6*math.sin(k*1.1); vm.pline([(x,y),(x-8*math.sin(k),y+12),(x,y+23)],1.6); lm.ell(x+9*(1 if k%2 else -1),y+10,6,3,ang=(30 if k%2 else -30))
    comp(img,vm,ULTRA,sh=0,rim=0,a=0.8); comp(img,lm,VERD,sh=0,rim=0,a=0.85)
    for (x,y) in ((30,40),(w-30,40),(30,h-40),(w-30,h-40)): comp(img,M().circ(x,y,8),GOLDL,sh=0,rim=0); comp(img,M().circ(x,y,4),VERM,sh=0,rim=0)
    return img
PAGE=_border(PAGE)
def diaper(c1,c2,dot=GOLDL,cell=26):
    img=np.zeros((h,w,3),np.float32)
    chk=((((xx-PX0)//cell)+((yy-PY0)//cell))%2==0)
    img[:]=np.where(chk[...,None],np.array(c1,np.float32),np.array(c2,np.float32))
    d=(((xx-PX0)%cell-cell/2)**2+((yy-PY0)%cell-cell/2)**2)<6
    img[d]=dot
    ln=(((xx-PX0)%cell)<1)|(((yy-PY0)%cell)<1); img[ln]*=0.75
    return img
def panel(bgimg,ground=VERD):
    img=PAGE.copy(); A=M().rect(PX0,PY0,PX1,PY1).f()[...,None]
    img=img*(1-A)+bgimg*A
    comp(img,M().rect(PX0,PY1-70,PX1,PY1),ground,sh=0,rim=0)
    gm=M()
    for k in range(30): x=PX0+8+k*15; gm.line((x,PY1-68),(x+4,PY1-78),1.2)
    comp(img,gm,lerpc(ground,(0.1,0.2,0.1),0.5),sh=0,rim=0)
    fr=M().rect(PX0-6,PY0-6,PX1+6,PY0).rect(PX0-6,PY1,PX1+6,PY1+6).rect(PX0-6,PY0-6,PX0,PY1+6).rect(PX1,PY0-6,PX1+6,PY1+6)
    comp(img,fr,GOLDL,sh=0.3,dx=2,dy=3,blur=3,rim=0.15); outl(img,M().rect(PX0-7,PY0-7,PX1+7,PY1+7),a=0.8,th=1,fill=0)
    return img
BG_STREET=panel(diaper(ULTRA,lerpc(ULTRA,(0,0,0),0.25)))
BG_HALL=panel(diaper(VERM,lerpc(VERM,(0,0,0),0.25)),ground=WOODC)
BG_SHRINE=panel(diaper((0.18,0.38,0.30),(0.12,0.28,0.22)),ground=(0.55,0.50,0.42))
BG_WHY=panel(diaper(PURP,lerpc(PURP,(0,0,0),0.3)),ground=(0.40,0.34,0.22))
# ================= gothic figures =================
def fig(buf,x,y,s,col,t=0.0,dance=1.0,ph=0.0,hat=None,a=1.0,shoes=None,robe=False,armsup=0.0):
    if a<=0: return
    q=t*7+ph; sw=math.sin(q)*dance
    lean=0.12*sw
    def R(pts): return rotp(pts,lean,x,y)
    if robe: body=M().poly(R([(x-18*s,y-92*s),(x+18*s,y-92*s),(x+30*s,y),(x-30*s,y)]))
    else: body=M().poly(R([(x-16*s,y-92*s),(x+16*s,y-92*s),(x+24*s,y-38*s),(x-24*s,y-38*s)]))
    legs=M()
    if not robe:
        for sd in (-1,1):
            kick=max(0,sd*sw)*0.9
            hip=R([(x+sd*8*s,y-40*s)])[0]; foot=(hip[0]+sd*(10+30*kick)*s,y-kick*26*s)
            legs.line(hip,foot,8*s)
            legs.poly([(foot[0]-4*s,foot[1]-3*s),(foot[0]+sd*20*s,foot[1]+1*s),(foot[0]-4*s,foot[1]+4*s)])
    arms=M()
    for sd in (-1,1):
        sh_=R([(x+sd*14*s,y-86*s)])[0]
        an=-math.pi/2+sd*(0.6+0.7*abs(math.sin(q*0.5+sd)))*dance-(1-dance)*(-math.pi/2+sd*0.3)*0+0
        if dance<0.05: an=math.pi/2+sd*0.25-armsup*sd*1.9
        el=(sh_[0]+math.cos(an)*24*s,sh_[1]+math.sin(an)*24*s); an2=an+sd*0.6*sw
        arms.line(sh_,el,6*s).line(el,(el[0]+math.cos(an2)*20*s,el[1]+math.sin(an2)*20*s),5*s)
    head=R([(x,y-104*s)])[0]
    for m_,c_ in ((legs,lerpc(col,INKB,0.35)),(body,col),(arms,col)):
        comp(buf,m_,c_,sh=0,rim=0,a=a); outl(buf,m_,a=a,th=1,fill=0)
    if shoes is not None and not robe:
        sm_=M()
        for sd in (-1,1):
            kick=max(0,sd*sw)*0.9; hip=R([(x+sd*8*s,y-40*s)])[0]; foot=(hip[0]+sd*(10+30*kick)*s,y-kick*26*s)
            sm_.poly([(foot[0]-6*s,foot[1]-5*s),(foot[0]+sd*22*s,foot[1]+1*s),(foot[0]-6*s,foot[1]+6*s)])
        comp(buf,sm_,shoes,sh=0,rim=0,a=a); outl(buf,sm_,a=a,th=1,fill=0)
    hm=M().circ(head[0],head[1],12*s); comp(buf,hm,SKINC,sh=0,rim=0,a=a); outl(buf,hm,a=a,th=1,fill=0)
    if hat=="coif": m=M().poly([(head[0]-13*s,head[1]+2*s),(head[0]-12*s,head[1]-10*s),(head[0],head[1]-15*s),(head[0]+12*s,head[1]-10*s),(head[0]+13*s,head[1]+2*s),(head[0]+8*s,head[1]-6*s),(head[0]-8*s,head[1]-6*s)]); comp(buf,m,WHITEL,sh=0,rim=0,a=a); outl(buf,m,a=a,th=1,fill=0)
    if hat=="doctor": m=M().rect(head[0]-14*s,head[1]-26*s,head[0]+14*s,head[1]-10*s).rect(head[0]-18*s,head[1]-12*s,head[0]+18*s,head[1]-8*s); comp(buf,m,INKB,sh=0,rim=0,a=a)
    if hat=="cap": m=M().ell(head[0],head[1]-10*s,14*s,7*s); comp(buf,m,VERM,sh=0,rim=0,a=a)
def building(buf,x,y,wd,ht,a=1.0):
    m=M().rect(x,y-ht,x+wd,y); comp(buf,m,(0.92,0.86,0.72),sh=0,rim=0,a=a); outl(buf,m,a=a,th=1,fill=0)
    r=M().poly([(x-8,y-ht),(x+wd/2,y-ht-wd*0.55),(x+wd+8,y-ht)]); comp(buf,r,VERM,sh=0,rim=0,a=a); outl(buf,r,a=a,th=1,fill=0)
    tm=M()
    for k in range(4): tm.line((x+k*wd/3,y-ht),(x+k*wd/3,y),2.5)
    tm.line((x,y-ht/2),(x+wd,y-ht/2),2.5).line((x,y-ht),(x+wd/3,y-ht/2),2).line((x+wd*2/3,y-ht/2),(x+wd,y-ht),2)
    ink(buf,tm,a*0.85,col=WOODC)
def cathedral(buf,x,y,a=1.0):
    m=M().poly([(x-26,y),(x-26,y-200),(x-14,y-230),(x,y-330),(x+14,y-230),(x+26,y-200),(x+26,y)]).rect(x-90,y-120,x+90,y)
    comp(buf,m,(0.72,0.40,0.36),sh=0,rim=0,a=a); outl(buf,m,a=a,th=1,fill=0)
    wm=M().circ(x,y-160,12).rect(x-60,y-90,x-40,y-40).rect(x+40,y-90,x+60,y-40)
    comp(buf,wm,ULTRA,sh=0,rim=0,a=a)
def stage(buf,a=1.0):
    m=M().rect(PX0+30,PY1-120,PX1-30,PY1-100); comp(buf,m,WOODC,sh=0.3,rim=0,a=a); outl(buf,m,a=a,th=1,fill=0)
    lm=M()
    for k in range(6): x=PX0+40+k*80; lm.rect(x,PY1-100,x+8,PY1-60)
    comp(buf,lm,lerpc(WOODC,INKB,0.3),sh=0,rim=0,a=a)
def lute(buf,x,y,a=1.0,t=0.0):
    m=M().ell(x,y,18,24,ang=-30).line((x+8,y-16),(x+40,y-60),5); comp(buf,m,(0.80,0.56,0.26),sh=0,rim=0,a=a); outl(buf,m,a=a,th=1,fill=0)
def drum(buf,x,y,a=1.0,t=0.0):
    m=M().rect(x-20,y-16,x+20,y+16); comp(buf,m,VERM,sh=0,rim=0,a=a); outl(buf,m,a=a,th=1,fill=0)
    st=M().line((x+24,y-26+6*math.sin(t*14)),(x+6,y-18),3); ink(buf,st,a)
def chapel(buf,x,y,a=1.0):
    m=M().rect(x-80,y-160,x+80,y).poly([(x-96,y-160),(x,y-240),(x+96,y-160)])
    comp(buf,m,(0.90,0.88,0.80),sh=0.3,rim=0,a=a); outl(buf,m,a=a,th=1,fill=0)
    cm=M().rect(x-4,y-290,x+4,y-236).rect(x-16,y-276,x+16,y-268); comp(buf,cm,GOLDL,sh=0,rim=0,a=a)
    dm=M().poly([(x-28,y),(x-28,y-70),(x,y-96),(x+28,y-70),(x+28,y)]); comp(buf,dm,WOODC,sh=0,rim=0,a=a); outl(buf,dm,a=a,th=1,fill=0)
def sun(buf,x,y,a=1.0,t=0.0):
    comp(buf,M().circ(x,y,26),GOLDL,sh=0,rim=0,a=a); m=M()
    for k in range(12): an=k*math.pi/6+t*0.3; m.poly([(x+math.cos(an-0.12)*28,y+math.sin(an-0.12)*28),(x+math.cos(an)*46,y+math.sin(an)*46),(x+math.cos(an+0.12)*28,y+math.sin(an+0.12)*28)])
    comp(buf,m,GOLDL,sh=0,rim=0,a=a); outl(buf,M().circ(x,y,26),a=a,th=1,fill=0)
# ================= scenes =================
GY=PY1-70
def s_hook(t,sc):
    tt=max(t,-1.0)
    buf=BG_STREET.copy(); hud=[]
    building(buf,70,GY,110,170); building(buf,360,GY,110,200)
    fig(buf,270,GY+6,1.6,VERM,tt,1.0,0.0,hat="coif")
    n=int(cl((tt-EV["hundreds"]+0.3)/1.0)*8)
    for k in range(n):
        x=90+k*48+(k%2)*10; s=0.7+0.1*(k%3); fig(buf,x,GY+20+((k*13)%10),s,[ULTRA,VERD,PURP,ROSEP,WOODC][k%5],tt,1.0,k*1.7,hat=["coif","cap",None][k%3],a=sm((tt-EV["hundreds"]+0.3-k*0.06)/0.3))
    def hd(d,t=t):
        k0=1.0 if t<0.4 else ap(t,-1,EV["month"])
        ttl(d,"THE DANCING",590,130,80,a=k0); ttl(d,"PLAGUE",590,220,90,a=k0,col=cVerm)
        initial(d,"D",165,175,130,a=k0)
        rubric(d,"She could not stop.",540,1320,52,a=ap(t,EV["stop"],EV["month"]))
        ttl(d,"HUNDREDS",540,175,96,a=ap(t,EV["hundreds"],sc["e"]+1),sc=pop(t,EV["hundreds"]-0.1),col=cVerm)
        rubric(d,"…but why?",540,1320,60,a=ap(t,EV["what"],sc["e"]+1))
    hud.append(hd); return buf,hud
def s_start(t,sc):
    buf=BG_STREET.copy(); hud=[]
    cathedral(buf,400,GY)
    fig(buf,190,GY+6,1.45,VERM,t,1.0,0.0,hat="coif")
    n=0
    if t>EV["others"]-0.2: n=int(cl((t-EV["others"]+0.2)/2.4)*12)
    for k in range(n):
        x=80+(k*67)%360; y_=GY+18+((k*29)%22); fig(buf,x,y_,0.6+0.12*((k*7)%3),[ULTRA,VERD,PURP,ROSEP,WOODC,GOLDL][k%6],t,1.0,k*1.3,hat=["coif","cap",None][k%3])
    hs=sm((t-EV["heat"]+0.3)/0.4)
    if hs>0: sun(buf,110,190,hs,t)
    nt=sm((t-EV["daynight"]+0.2)/0.4)*(1-hs*0.0)
    if nt>0 and hs<1:
        mm=M().circ(440,180,22); comp(buf,mm,WHITEL,sh=0,rim=0,a=nt*(1-hs)); comp(buf,M().circ(450,172,20),ULTRA,sh=0,rim=0,a=nt*(1-hs))
    def hd(d,t=t):
        rubric(d,"Strasbourg · July 1518",540,170,54,a=ap(t,EV["july"],EV["others"]),sc=pop(t,EV["july"]-0.1))
        ttl(d,"FRAU TROFFEA",540,1320,80,a=ap(t,EV["troffea"],EV["others"]),sc=pop(t,EV["troffea"]-0.1))
        n_=int(cl((t-EV["alone"])/1.0)*6); ttl(d,f"DAY {max(1,n_)}",540,170,96,a=ap(t,EV["alone"]+0.3,EV["others"]),col=cVerm) if t>EV["alone"] else None
        ttl(d,"DOZENS",540,170,100,a=ap(t,EV["dozens"],EV["four"]),sc=pop(t,EV["dozens"]-0.1))
        ttl(d,"~400?",540,170,120,a=ap(t,EV["four"],EV["daynight"]),sc=pop(t,EV["four"]-0.1),col=cVerm)
        rubric(d,"estimates range from 50 to 400",540,1320,44,a=ap(t,EV["four"]+0.2,EV["daynight"]))
        ttl(d,"DAY & NIGHT",540,170,96,a=ap(t,EV["daynight"],sc["e"]+1),sc=pop(t,EV["daynight"]-0.1))
        rubric(d,"in the summer heat",540,1320,54,a=ap(t,EV["heat"],sc["e"]+1))
    hud.append(hd); return buf,hud
def s_cure(t,sc):
    pS=sm((t-EV["guild"]+0.3)/0.4)
    buf=BG_STREET*(1-pS)+BG_HALL*pS; hud=[]
    a1=1-pS
    if a1>0:
        fig(buf,150,GY+6,1.5,INKB,t,0.0,0,hat="doctor",robe=True,a=a1,armsup=sm((t-EV["cure"]+0.2)/0.4))
        fig(buf,340,GY+10,1.2,VERM,t,1.0,0.5,hat="coif",a=a1)
        if t>EV["hot"]-0.2:
            hm=M()
            for k in range(3): hm.pline([(330+k*14+6*math.sin(t*6+k+q*6),330-q*80) for q in np.linspace(0,1,14)],2)
            ink(buf,hm,a1*sm((t-EV["hot"]+0.2)/0.3),col=VERM)
    if pS>0:
        stage(buf,pS)
        fig(buf,110,GY-40,1.0,PURP,t,0.0,0,hat="cap",a=pS*sm((t-EV["musicians"]+0.3)/0.4)); lute(buf,124,GY-110,pS*sm((t-EV["musicians"]+0.3)/0.4))
        fig(buf,430,GY-40,1.0,VERD,t,0.0,0,hat="cap",a=pS*sm((t-EV["musicians"]+0.3)/0.4)); drum(buf,450,GY-104,pS*sm((t-EV["musicians"]+0.3)/0.4),t)
        for k in range(5):
            x=170+k*50; fl=sm((t-EV["collapsed"]+0.2-k*0.1)/0.6) if k in (1,3) else 0
            if fl>0.6:
                m=M().ell(x,GY+20,30,9); comp(buf,m,[ULTRA,VERM,GOLDL,ROSEP,WOODC][k],sh=0,rim=0,a=pS); outl(buf,m,a=pS,th=1,fill=0); comp(buf,M().circ(x-30,GY+16,10),SKINC,sh=0,rim=0,a=pS)
            else: fig(buf,x,GY+10,0.85,[ULTRA,VERM,GOLDL,ROSEP,WOODC][k],t*(1.0+0.6*sm((t-EV["worse"])/1.0)),1.0,k*1.9,hat=["coif","cap",None][k%3],a=pS)
    def hd(d,t=t):
        rubric(d,"The doctors’ verdict:",540,150,48,a=ap(t,EV["doctors"],EV["guild"]))
        ttl(d,"“HOT BLOOD”",540,225,92,a=ap(t,EV["hot"],EV["cure"]),sc=pop(t,EV["hot"]-0.1),col=cVerm)
        ttl(d,"CURE: MORE DANCING",540,225,70,a=ap(t,EV["more"]-0.3,EV["guild"]),sc=pop(t,EV["more"]-0.4))
        rubric(d,"guildhalls cleared",540,150,50,a=ap(t,EV["guild"],EV["worse"]))
        ttl(d,"A STAGE + MUSICIANS",540,225,66,a=ap(t,EV["stage"],EV["worse"]),sc=pop(t,EV["stage"]-0.1))
        ttl(d,"IT GOT WORSE",540,190,92,a=ap(t,EV["worse"],sc["e"]+1),sc=pop(t,EV["worse"]-0.1),col=cVerm)
        rubric(d,"some may have danced until they collapsed",540,1320,40,a=ap(t,EV["collapsed"],sc["e"]+1))
    hud.append(hd); return buf,hud
def s_shrine(t,sc):
    buf=BG_SHRINE.copy(); hud=[]
    chapel(buf,370,GY)
    k=sm((t-EV["shrine"]+0.6)/1.4)
    cart=M().rect(80+120*k,GY-50,200+120*k,GY-20); comp(buf,cart,WOODC,sh=0.3,rim=0); outl(buf,cart,a=1,th=1,fill=0)
    for dx in (100,180): comp(buf,M().circ(dx+120*k,GY-16,14),lerpc(WOODC,INKB,0.4),sh=0,rim=0)
    st=sm((t-EV["stops"]+0.2)/1.0)
    rs=sm((t-EV["redshoes"]+0.2)/0.4)
    for j in range(3):
        fig(buf,110+j*44+120*k,GY-52,0.7,[ULTRA,VERD,PURP][j],t,1.0-st,j*1.4,hat="coif",shoes=(0.85,0.10,0.08) if rs>0.5 else None)
    if t>EV["prayed"]-0.3:
        fig(buf,300,GY+6,1.1,(0.30,0.24,0.20),t,0.0,0,robe=True,a=sm((t-EV["prayed"]+0.3)/0.4),armsup=1.0)
    sim=sm((t-EV["similar"]+0.3)/0.4)
    if sim>0:
        wash(buf,PX0+6,PY0+6,10,VELL,0)
        A=M().rect(PX0,PY0,PX1,PY1).f()[...,None]*sim*0.85; buf[:]=buf*(1-A)+PAGE*A
        for k2,(x,y) in enumerate(((150,300),(380,260),(250,420),(420,470))):
            fig(buf,x,y+40,0.55,[VERM,ULTRA,VERD,PURP][k2],t,1.0,k2*2.1,hat="coif",a=sim*sm((t-EV["similar"]-k2*0.15)/0.3))
    def hd(d,t=t,sim=sim):
        ttl(d,"SHRINE OF ST. VITUS",540,180,74,a=ap(t,EV["shrine"],EV["redshoes"]),sc=pop(t,EV["shrine"]-0.1))
        ttl(d,"RED SHOES",540,180,100,a=ap(t,EV["redshoes"],EV["slowly"]),sc=pop(t,EV["redshoes"]-0.1),col=cVerm)
        rubric(d,"crosses in their hands · holy water",540,1320,42,a=ap(t,EV["prayed"],EV["slowly"]))
        ttl(d,"…IT STOPS",540,180,100,a=ap(t,EV["stops"]-0.2,EV["similar"]),sc=pop(t,EV["stops"]-0.3))
        rubric(d,"Aachen 1374 · Strasbourg 1518 · …",540,1320,46,a=ap(t,EV["similar"]+0.3,sc["e"]+1))
        ttl(d,"NOT THE FIRST",540,180,92,a=ap(t,EV["similar"],sc["e"]+1),sc=pop(t,EV["similar"]-0.1),col=cVerm)
    hud.append(hd); return buf,hud
def s_why(t,sc):
    pB=sm((t-EV["began"]+0.3)/0.4)
    buf=BG_WHY*(1-pB)+BG_STREET*pB; hud=[]
    a1=1-pB
    if a1>0:
        fm=M()
        for k in range(4):
            x=110+k*100; fm.pline([(x,GY-150),(x+6,GY-210),(x+16,GY-220)],3); fm.ell(x+18,GY-222,8,4,ang=40)
        ink(buf,fm,a1*sm((t-EV["famine"]+0.3)/0.4),col=(0.55,0.45,0.25))
        bw=M().ell(270,GY+40,50,14); comp(buf,bw,(0.62,0.50,0.38),sh=0,rim=0,a=a1*sm((t-EV["famine"]+0.3)/0.4)); outl(buf,bw,a=a1*sm((t-EV["famine"]+0.3)/0.4),th=1,fill=0)
        sp=cl((t-EV["fear"]+0.2)/2.0)
        for k in range(7):
            x=90+k*60; on=sp*7>k
            fig(buf,x,GY+8,0.75,[VERM,ULTRA,VERD,PURP,ROSEP,GOLDL,WOODC][k],t,1.0 if on else 0.0,k*1.3,hat=["coif","cap",None][k%3],a=a1)
            if on and k<6 and sp*7<k+1.6:
                lm=M(); dl(lm,[(x+10,GY-120),(x+30,GY-140),(x+50,GY-120)],1.0,2); ink(buf,lm,a1,col=VERM)
    if pB>0:
        building(buf,70,GY,110,170,pB); building(buf,360,GY,110,200,pB); fig(buf,270,GY+6,1.6,VERM,t,1.0,0.0,hat="coif",a=pB)
    def hd(d,t=t):
        ttl(d,"MASS HYSTERIA?",540,180,90,a=ap(t,EV["hysteria"],EV["fear"]),sc=pop(t,EV["hysteria"]-0.1),col=cVerm)
        rubric(d,"a city crushed by famine and disease",540,1320,46,a=ap(t,EV["famine"]-0.3,EV["fear"]))
        ttl(d,"FEAR SPREADS",540,180,96,a=ap(t,EV["fear"],EV["began"]),sc=pop(t,EV["fear"]-0.1))
        rubric(d,"person to person",540,1320,52,a=ap(t,EV["person"],EV["began"]))
        ttl(d,"STRASBOURG · 1518",540,180,80,a=ap(t,EV["strasbourg"],sc["e"]+1),sc=pop(t,EV["strasbourg"]-0.1))
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,start=s_start,cure=s_cure,shrine=s_shrine,why=s_why)
BAND=(1-0.40*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.22*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.008,(h,w,1)).astype(np.float32) for i in range(6)]
TR=0.32; TOTAL=B.TOTAL; LOOPD=0.6
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
def pageturn(b1,b2,u):
    """the page lifts from the right edge and turns over to the left, revealing the next leaf"""
    k=sm(u); xc=w*(1-k)*1.15-30; cw=60*(1-abs(2*k-1))+14
    out=np.where((xx>=xc+cw)[...,None],b2,b1)
    band=(xx>=xc)&(xx<xc+cw)
    f=np.clip((xx-xc)/max(cw,1),0,1)
    back=np.array(VELL,np.float32)*(0.78+0.22*np.sin(f*math.pi))[...,None]
    out=np.where(band[...,None],back,out)
    sh=np.clip(1-(xx-(xc+cw))/40,0,1)*(xx>=xc+cw); out*=(1-0.35*sh)[...,None]
    sh2=np.clip(1-(xc-xx)/25,0,1)*(xx<xc); out*=(1-0.20*sh2)[...,None]
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
        buf=pageturn(b1,b2,u); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    buf=np.clip(buf,0,1.2)*PT*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
