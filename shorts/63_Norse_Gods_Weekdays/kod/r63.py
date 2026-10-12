import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid63")
for p in ["/home/claude/vid63","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= astronomical clock dial =================
CX,CY,RD=270,320,236
GOLD=np.array((0.88,0.68,0.30),np.float32); GOLDD=np.array((0.52,0.36,0.12),np.float32)
NAVY=(0.05,0.10,0.26); ENAM=(0.10,0.24,0.55); RENAM=(0.52,0.10,0.10); NIGHT=(0.03,0.04,0.10)
_g=np.random.default_rng(63)
def _nz(s): n=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),s); return n/n.std()
_a,_b,_c=_nz(0.8),_nz(4),_nz(20)
R2=np.sqrt((xx-CX)**2+(yy-CY)**2); ANG=np.arctan2(yy-CY,xx-CX)
def fill(buf,m,col,a=1.0):
    A=(m.f() if isinstance(m,M) else m)*a; buf+=(np.array(col,np.float32)-buf)*A[...,None]
def gold(buf,m,a=1.0,soft=1.0):
    """raised gilt relief: brushed gold with a bevel lit from the upper left"""
    A=(m.f() if isinstance(m,M) else m)
    if A.max()<0.01: return
    Ab=cv2.GaussianBlur(A,(0,0),soft); gx=cv2.Sobel(Ab,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(Ab,cv2.CV_32F,0,1,ksize=3)
    sh=np.clip(1+(-gx-gy)*1.6,0.35,1.7)
    col=GOLD[None,None,:]*(0.92+0.08*_a[...,None]+0.06*np.sin(xx*0.9)[...,None])*sh[...,None]
    buf+=(col-buf)*(A*a)[...,None]
_FG={}
def glyph(ch,x,y,size,font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    k=(ch,int(size),font)
    if k not in _FG: _FG[k]=ImageFont.truetype(font,int(size))
    L=Image.new("L",(w,h),0); ImageDraw.Draw(L).text((x,y),ch,font=_FG[k],fill=255,anchor="mm")
    return np.asarray(L).astype(np.float32)/255
def _dial():
    b=np.empty((h,w,3),np.float32); b[:]=NAVY; b*=(1+0.06*_c)[...,None]
    for _ in range(160):
        x,y=_g.uniform(0,w),_g.uniform(0,h); fill(b,M().circ(x,y,_g.uniform(0.6,1.6)),(0.9,0.85,0.7),_g.uniform(0.3,0.9))
    disc=M().circ(CX,CY,RD).f()
    # sky of the dial: blue day above the horizon arc, dark night below (like Prague's orloj)
    hor=(yy>CY+40+0.0006*(xx-CX)**2*-1).astype(np.float32)
    day=np.array((0.18,0.38,0.72),np.float32); night=np.array(NIGHT,np.float32)
    k=np.clip((yy-(CY-RD))/(RD*1.2),0,1)[...,None]
    sky=day*(1-k*0.5)
    inner=disc[...,None]*(sky*(1-hor[...,None])+night*hor[...,None])
    b=b*(1-disc[...,None])+inner
    for r,th in ((RD,7),(RD-14,2.5),(RD-60,3),(RD-104,2.5),(118,3)):
        ring=np.clip(M().circ(CX,CY,r+th/2).f()-M().circ(CX,CY,r-th/2).f(),0,1); gold(b,ring,1.0,0.8)
    num=["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII"]*2
    for i in range(24):
        a=-math.pi/2+i*2*math.pi/24; x,y=CX+math.cos(a)*(RD-7),CY+math.sin(a)*(RD-7)
        gold(b,M().circ(x,y,2.2),1.0,0.6)
    for i in range(48):
        a=i*2*math.pi/48; gold(b,M().line((CX+math.cos(a)*(RD-60),CY+math.sin(a)*(RD-60)),(CX+math.cos(a)*(RD-52),CY+math.sin(a)*(RD-52)),2),1.0,0.6)
    return b
DIAL=_dial()
# planets & gods
MR=RD-37; MED=[(CX+math.cos(-math.pi/2+i*2*math.pi/7)*MR,CY+math.sin(-math.pi/2+i*2*math.pi/7)*MR) for i in range(7)]
ROM_SYM=["☉","☽","♂","☿","♃","♀","♄"]
ROM_NAME=["SOL","LUNA","MARS","MERCURY","JUPITER","VENUS","SATURN"]
DAY=["SUNDAY","MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"]
NORSE={2:"TIW",3:"WODEN",4:"THOR",5:"FRIGG"}
def emblem_norse(i,x,y,s):
    m=M()
    if i==2:   # Tiwaz rune
        m.line((x,y-26*s),(x,y+26*s),5*s); m.line((x,y-26*s),(x-16*s,y-8*s),5*s); m.line((x,y-26*s),(x+16*s,y-8*s),5*s)
    elif i==3: # Ansuz rune
        m.line((x-8*s,y-26*s),(x-8*s,y+26*s),5*s); m.line((x-8*s,y-24*s),(x+14*s,y-10*s),5*s); m.line((x-8*s,y-8*s),(x+14*s,y+6*s),5*s)
    elif i==4: # hammer
        m.rect(x-22*s,y-22*s,x+22*s,y-6*s); m.rect(x-4*s,y-8*s,x+4*s,y+26*s); m.circ(x,y+28*s,5*s)
    elif i==5: # spindle
        m.line((x,y-28*s),(x,y+28*s),3.5*s); m.ell(x,y+10*s,16*s,5*s)
        for k in range(4): m.line((x-6*s,y-18*s+k*6*s),(x+6*s,y-15*s+k*6*s),2*s)
    return m.f()
def medallion(b,i,x,y,s=1.0,norse=0.0,hl=0.0):
    r=33*s
    fill(b,M().circ(x,y,r),ENAM if norse<0.5 else RENAM)
    if hl>0: fill(b,M().circ(x,y,r),(0.95,0.85,0.5),0.25*hl)
    ring=np.clip(M().circ(x,y,r+3).f()-M().circ(x,y,r-2).f(),0,1); gold(b,ring)
    if norse<0.5: gold(b,glyph(ROM_SYM[i],x,y+2*s,40*s,"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),1-norse*2)
    else: gold(b,emblem_norse(i,x,y,s*0.9),(norse-0.5)*2)
def hand(b,ang,L=RD-70,a=1.0):
    x1,y1=CX+math.cos(ang)*L,CY+math.sin(ang)*L
    m=M().line((CX,CY),(x1,y1),5); m.poly([(x1+math.cos(ang)*18,y1+math.sin(ang)*18),(x1+math.cos(ang+2.5)*12,y1+math.sin(ang+2.5)*12),(x1+math.cos(ang-2.5)*12,y1+math.sin(ang-2.5)*12)])
    m.circ(CX,CY,12); gold(b,m.f()*a,1.0,0.8)
def med_ang(i): return -math.pi/2+i*2*math.pi/7
# ================= HUD =================
_IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(n if n.startswith("/") else P.FD+n,s)
    return _IF[k]
cG=(242,204,120)
def ttl(d,s,y=1240,fs=92,a=1.0,sc=1.0,col=cG):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f("Italiana-Regular.ttf",n)
    while f.getlength(s)>980 and n>20: n-=4; f=_f("Italiana-Regular.ttf",n)
    d.text((W/2,y),s,font=f,fill=col+(int(255*a),),anchor="mm",stroke_width=2,stroke_fill=col+(int(255*a),))
def lab(d,s,x,y,fs=30,a=1.0,col=(250,235,200)):
    if a<=0.01: return
    d.text((x,y),s,font=_f("LibreBaskerville-Regular.ttf",fs),fill=col+(int(255*a),),anchor="mm",stroke_width=3,stroke_fill=(8,14,36,int(230*a)))
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
def base(t,norse_k=None,hl=None,big=None,hand_ang=None):
    b=DIAL.copy()
    for i,(x,y) in enumerate(MED):
        nk=norse_k[i] if norse_k else 0.0; hk=hl[i] if hl else 0.0
        medallion(b,i,x,y,1.0+0.25*hk,nk,hk)
    if hand_ang is not None: hand(b,hand_ang)
    if big is not None:
        i,nk,a=big
        fill(b,M().circ(CX,CY,104),(0.04,0.08,0.22),0.85*a)
        if nk<0.5: gold(b,glyph(ROM_SYM[i],CX,CY+6,130,"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),a*(1-nk*2))
        else: gold(b,emblem_norse(i,CX,CY,3.0),a*(nk-0.5)*2)
    return b
# ================= shots =================
def s_hook(t):
    ang=-math.pi/2+2*math.pi*(4/7)*sm((t+0.4)/2.5)
    b=base(t,hand_ang=ang,norse_k=[0,0,1,1,1,1,0],hl=[1.0*fa(t,EV["four"]-0.2,EV["noticing"]+0.4)*(1 if i in (2,3,4,5) else 0) for i in range(7)])
    def hd(d,t=t):
        ttl(d,"FOUR NORSE GODS",1240,92,a=ap(t,EV["four"]-0.2,99),sc=pop(t,EV["four"]-0.3))
        ttl(d,"every week",1330,64,a=ap(t,EV["norse"],99))
    return b,[hd]
def s_rome(t):
    keys=["sun","moon","mars","mercury","jupiter","venus","saturn"]
    hl=[fa(t,EV[k]-0.15,EV[k]+0.5,0.15,0.3) for k in keys]
    cur=max([i for i,k in enumerate(keys) if t>=EV[k]-0.2],default=None)
    b=base(t,hl=hl,hand_ang=med_ang(cur) if cur is not None else -math.pi/2)
    def hd(d,t=t):
        ttl(d,"THE ROMANS",1240,92,a=ap(t,EV["romans"]-0.2,EV["seven"]-0.1),sc=pop(t,EV["romans"]-0.3))
        ttl(d,"7 DAYS · 7 WANDERING LIGHTS",1240,66,a=ap(t,EV["seven"]-0.1,99),sc=pop(t,EV["seven"]-0.2))
        for i,k in enumerate(keys):
            x,y=MED[i]; a=ap(t,EV[k]-0.15,99)
            lx,ly=x+(CX-x)*0.42,y+(CY-y)*0.42; lab(d,ROM_NAME[i],lx*2,ly*2,32,a)
    return b,[hd]
SWAPS=[(2,"s_mars","tiw","tuesday"),(3,"s_merc","woden","wednesday"),(4,"s_jup","thor","thursday"),(5,"s_ven","frigg","friday")]
def s_swap(t):
    nk=[0.0]*7; hl=[0.0]*7; big=None; cur=None
    for i,k0,kg,kd in SWAPS:
        if t>=EV[k0]-0.3: cur=(i,k0,kg,kd)
        nk[i]=sm((t-EV[kg]+0.2)/0.5)
    if cur:
        i,k0,kg,kd=cur; hl[i]=1.0; big=(i,nk[i],sm((t-EV[k0]+0.3)/0.4))
    b=base(t,norse_k=nk,hl=hl,big=big,hand_ang=med_ang(cur[0]) if cur else -math.pi/2+2*math.pi*(t-S("swap")["s"])/4)
    def hd(d,t=t,cur=cur):
        ttl(d,"THEIR OWN GODS",1240,88,a=ap(t,EV["germanic"]-0.2,EV["s_mars"]-0.2),sc=pop(t,EV["germanic"]-0.3))
        for i,k0,kg,kd in SWAPS:
            end=min([EV[x[1]] for x in SWAPS if EV[x[1]]>EV[k0]],default=99)-0.3
            ttl(d,f"{ROM_NAME[i]} = {NORSE[i]}",1225,78,a=ap(t,EV[kg]-0.1,end),sc=pop(t,EV[kg]-0.2))
            ttl(d,DAY[i],1320,70,a=ap(t,EV[kd]-0.2,end),sc=pop(t,EV[kd]-0.3),col=(255,255,255))
            x,y=MED[i]; lx,ly=x+(CX-x)*0.40,y+(CY-y)*0.40; lab(d,DAY[i][:3],lx*2,ly*2,36,ap(t,EV[kd]-0.2,99))
    return b,[hd]
def s_latin(t):
    nk=[0,0,1,1,1,1,0]; hl=[0.0]*7; hl[6]=fa(t,EV["saturday"]-0.2,EV["spanish"],0.2,0.3)
    sp=[(2,"martes","martes"),(3,"mierc","miércoles"),(4,"jueves","jueves"),(5,"viernes","viernes")]
    ang=med_ang(6)
    for i,k,_ in sp:
        if t>=EV[k]-0.2: ang=med_ang(i)
    if t>=Lx("So the next")[0]-0.2: ang=med_ang(4)
    rk=[0.0]*7
    for i,k,_ in sp: rk[i]=fa(t,EV[k]-0.2,Lx("So the next")[0],0.2,0.3)
    nk2=[nk[i]*(1-rk[i]) for i in range(7)]
    hl=[max(hl[i],rk[i]) for i in range(7)]
    if t>=EV["thurs2"]-0.2: hl[4]=1.0
    b=base(t,norse_k=nk2,hl=hl,hand_ang=ang)
    def hd(d,t=t):
        ttl(d,"SATURDAY = SATURN",1240,80,a=ap(t,EV["saturday"]-0.2,EV["spanish"]),sc=pop(t,EV["saturday"]-0.3))
        ttl(d,"SPANISH KEPT THE ROMANS",1240,66,a=ap(t,EV["spanish"],Lx("So the next")[0]),sc=pop(t,EV["spanish"]-0.1))
        for i,k,s in sp:
            x,y=MED[i]; lx,ly=x+(CX-x)*0.42,y+(CY-y)*0.42; lab(d,s,lx*2,ly*2,36,ap(t,EV[k]-0.2,Lx("So the next")[0]),(255,225,150))
        ttl(d,"THOR'S DAY",1240,96,a=ap(t,EV["thurs2"]-0.2,99),sc=pop(t,EV["thurs2"]-0.3))
    return b,[hd]
TR=0.36; TOTAL=B.TOTAL; LOOPD=0.62
SHOTS=[(0.0,s_hook),(S("rome")["s"],s_rome),(S("swap")["s"],s_swap),(S("latin")["s"],s_latin)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
def sweep(b1,b2,u):
    """a gilt hand sweeps once around the dial, carrying the new picture behind it"""
    a0=-math.pi/2; cur=a0+u*2*math.pi
    rel=(ANG-a0)%(2*math.pi); m=(rel<u*2*math.pi).astype(np.float32); m=cv2.GaussianBlur(m,(0,0),1.2)
    out=b1*(1-m[...,None])+b2*m[...,None]
    hand(out,cur,RD+40,1.0); return out
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None: buf,hud=SHOTS[i][1](t); hk=1.0
    else:
        fa_,fb_,ta,tb,u=pair; b1,h1=fa_(ta); b2,h2=fb_(tb)
        buf=sweep(b1,b2,u); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
