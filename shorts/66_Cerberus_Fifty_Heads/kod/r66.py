import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid66")
for p in ["/home/claude/vid66","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= Silver-age comic page: newsprint, Ben-Day dots, bold ink =================
PAPERC=np.array((0.96,0.92,0.80),np.float32)
INK=(0.07,0.06,0.07); RED=(0.86,0.18,0.15); YEL=(0.99,0.84,0.22); BLU=(0.18,0.42,0.80); PUR=(0.45,0.22,0.55); GRN=(0.30,0.62,0.35); ORN=(0.96,0.55,0.18)
_g=np.random.default_rng(66)
_n=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),25); _n/=_n.std()
_fb=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),0.6); _fb/=_fb.std()
PX0,PX1,PY0,PY1=24,516,40,652
c15,s15=math.cos(0.26),math.sin(0.26)
_u=(xx*c15+yy*s15)/5.0; _v=(-xx*s15+yy*c15)/5.0
DOTD=np.sqrt((_u-np.round(_u))**2+(_v-np.round(_v))**2).astype(np.float32)     # distance to nearest dot centre (cells of 5px)
def fill(buf,m,col,a=1.0):
    A=(m.f() if isinstance(m,M) else m)*a; buf+=(np.array(col,np.float32)-buf)*A[...,None]
def dots(buf,m,col,tone=0.5,a=1.0):
    """Ben-Day dots: coloured dots whose radius follows the tone"""
    A=(m.f() if isinstance(m,M) else m)
    r=0.18+0.42*tone; D=np.clip((r-DOTD)/0.08,0,1)*A*a; fill(buf,D,col)
def inkline(buf,pts,th=3.0,a=1.0):
    fill(buf,M().pline(pts,th),INK,a)
def inked(buf,m,col,th=3,a=1.0,shade=None):
    A=m.f() if isinstance(m,M) else m
    fill(buf,A,col,a)
    if shade is not None: dots(buf,A*shade,INK,0.35,0.55*a)
    e=np.clip(A-cv2.erode(A,np.ones((2*th+1,2*th+1),np.uint8)),0,1); fill(buf,e,INK,a)
def page():
    b=np.empty((h,w,3),np.float32); b[:]=PAPERC; b*=(1+0.03*_n+0.015*_fb)[...,None]
    fill(b,M().rect(0,668,w,h),(0.06,0.05,0.07))
    return b
def panel(b,x0,y0,x1,y1,bg=None,tone=0.5,bgcol=None):
    m=M().rect(x0,y0,x1,y1)
    if bg=="dots": fill(b,m,(0.98,0.96,0.90)); dots(b,m,bgcol or RED,tone)
    elif bg=="burst":
        fill(b,m,YEL); cx,cy=(x0+x1)/2,(y0+y1)/2
        for k in range(18):
            a=k*2*math.pi/18
            if k%2==0: fill(b,M().poly([(cx,cy),(cx+math.cos(a)*700,cy+math.sin(a)*700),(cx+math.cos(a+0.17)*700,cy+math.sin(a+0.17)*700)]).f()*m.f(),ORN)
    elif bg is not None: fill(b,m,bg)
    inkline(b,[(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)],4)
def clip_outside(b,x0,y0,x1,y1,base):
    mk=np.ones((h,w),np.float32); mk[int(y0):int(y1),int(x0):int(x1)]=0; mk=mk[...,None]; return b*(1-mk)+base*mk
# ---- characters ----
def dog_head(b,x,y,s,ang=0.0,snarl=1.0,col=(0.30,0.16,0.16),sleep=0.0):
    c,sn=math.cos(ang),math.sin(ang)
    R=lambda dx,dy:(x+dx*s*c-dy*s*sn,y+dx*s*sn+dy*s*c)
    m=M().ell(*R(0,0),26*s,22*s,math.degrees(ang)); m.poly([R(10,-16),R(46,-6),R(48,10),R(14,16)])
    m.poly([R(-14,-14),R(-24,-44),R(0,-20)])
    inked(b,m,col,2 if s<0.6 else 3,shade=(yy>(y)).astype(np.float32)*0.6)
    if sleep>0.5: inkline(b,[R(4,-6),R(16,-4)],2)
    else: fill(b,M().circ(*R(6,-6),5*s),YEL); fill(b,M().circ(*R(7,-6),2.2*s),INK)
    if snarl>0 and sleep<0.5:
        for k in range(4): fill(b,M().poly([R(20+k*7,8),R(24+k*7,8),R(22+k*7,15)]),(1,1,1))
def cerberus(b,cx,by,s,n=3,t=0.0,sleep=0.0,col=(0.30,0.16,0.16)):
    body=M().ell(cx,by-60*s,100*s,52*s)
    for dx in (-70,-35,40,75): body.rect(cx+dx*s-11*s,by-40*s,cx+dx*s+11*s,by)
    inked(b,body,col,3,shade=(yy>by-60*s).astype(np.float32))
    inkline(b,[(cx-96*s,by-70*s),(cx-130*s,by-100*s+8*math.sin(t*4)*s),(cx-150*s,by-80*s)],5*s)
    nx,ny=cx+60*s,by-90*s
    if n<=3:
        angs=np.linspace(-0.9,0.5,n) if n>1 else [0.0]
        for i,a in enumerate(angs):
            hx,hy=nx+math.cos(a-0.5)*80*s,ny+math.sin(a-0.5)*80*s
            inkline(b,[(nx,ny),(hx,hy)],22*s); fill(b,M().line((nx,ny),(hx,hy),16*s),col)
            dog_head(b,hx,hy,s*0.95,a*0.4+0.1*math.sin(t*3+i),sleep=sleep,col=col)
    else:
        g=np.random.default_rng(n)
        for i in range(n):
            a=-2.8+2.25*g.random(); L=(85+105*g.random()**0.7)*s
            hx,hy=nx+math.cos(a)*L,ny+math.sin(a)*L*0.85
            inkline(b,[(nx,ny),(hx,hy)],2.2*s); dog_head(b,hx,hy,s*(0.30 if n>60 else 0.40),a*0.3+0.15*math.sin(t*4+i),sleep=sleep,col=col)
def hero(b,x,by,s,col=RED,lion=False,lyre=False,robe=False):
    m=M(); m.circ(x,by-150*s,16*s); body=M().poly([(x-22*s,by-132*s),(x+22*s,by-132*s),(x+28*s,by-60*s),(x-28*s,by-60*s)])
    inked(b,m,(0.95,0.78,0.62),2); inked(b,body,col,3,shade=(xx>x).astype(np.float32))
    for dx in (-12,12): inked(b,M().rect(x+dx*s-6*s,by-62*s,x+dx*s+6*s,by),(0.95,0.78,0.62),2)
    if lion: inked(b,M().ell(x,by-160*s,26*s,16*s),ORN,2); inked(b,M().poly([(x-26*s,by-150*s),(x-40*s,by-90*s),(x-22*s,by-120*s)]),ORN,2)
    if robe: inked(b,M().poly([(x-28*s,by-60*s),(x+28*s,by-60*s),(x+36*s,by),(x-36*s,by)]),col,3)
    if lyre:
        lx,ly=x+38*s,by-110*s; inkline(b,[(lx-14*s,ly+20*s),(lx-18*s,ly-24*s)],4*s); inkline(b,[(lx+14*s,ly+20*s),(lx+18*s,ly-24*s)],4*s)
        inkline(b,[(lx-18*s,ly-18*s),(lx+18*s,ly-18*s)],3*s)
        for k in range(4): inkline(b,[(lx-9*s+k*6*s,ly-18*s),(lx-9*s+k*6*s,ly+18*s)],1.2)
        inked(b,M().ell(lx,ly+22*s,18*s,8*s),YEL,2)
# ================= HUD lettering =================
_IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(P.FD+n,s)
    return _IF[k]
def caption(d,s,x,y,fs=40,a=1.0,sc=1.0,bg=(252,214,60),anchor="mm"):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f("WorkSans-BoldItalic.ttf",n); s=s.upper(); tw=f.getlength(s); px,py=n*0.45,n*0.32
    x0=x-tw/2-px if anchor=="mm" else x
    d.rectangle((x0,y-n*0.55-py,x0+tw+2*px,y+n*0.55+py),fill=bg+(int(250*a),),outline=(15,12,14,int(255*a)),width=4)
    d.text((x0+px+tw/2,y),s,font=f,fill=(15,12,14,int(255*a)),anchor="mm")
def sfx(d,s,x,y,fs=110,a=1.0,sc=1.0,col=(240,60,40),rot=-8):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f("EricaOne-Regular.ttf",n)
    L=Image.new("RGBA",(int(f.getlength(s)+80),int(n*1.6)),(0,0,0,0)); dd=ImageDraw.Draw(L)
    dd.text((40,n*0.8),s,font=f,fill=col+(int(255*a),),anchor="lm",stroke_width=7,stroke_fill=(15,12,14,int(255*a)))
    L=L.rotate(rot,expand=True,resample=Image.BICUBIC); d._image.alpha_composite(L,(int(x-L.width/2),int(y-L.height/2)))
def pop(t,e): return spring((t-e)/0.4)
def ap(t,s,e): return fa(t,s-0.1,e-0.3,0.2,0.25)
# ================= shots =================
def s_hook(t,end=False):
    b=page(); panel(b,PX0,PY0,PX1,PY1,"dots",0.45,RED)
    k=sm((t-EV["fifty"]+0.3)/0.5) if not end else 0.0
    cerberus(b,230,590,1.35 if k<0.5 else 1.1,3 if k<0.5 else 50,t)
    def hd(d,t=t):
        sfx(d,"GRRR!",780,250,120,a=ap(t,EV["three"]-0.6,EV["fifty"]-0.1) if not end else ap(t,EV["picture"],99),sc=pop(t,EV["three"]-0.7))
        if not end:
            caption(d,"Guard dog of the underworld",540,140,40,a=ap(t,EV["under"]-0.6,EV["orig"]),sc=pop(t,EV["under"]-0.7))
            caption(d,"Originally: 50 heads!",540,140,52,a=ap(t,EV["orig"]-0.1,99),sc=pop(t,EV["orig"]-0.2))
        else: caption(d,"Remember...",540,140,52,a=ap(t,EV["remember"]-0.2,99),sc=pop(t,EV["remember"]-0.3))
    return b,[hd]
def s_hesiod(t):
    b=page(); panel(b,PX0,PY0,PX1,300,(0.99,0.96,0.88)); panel(b,PX0,312,PX1,PY1,"dots",0.35,PUR)
    hero(b,120,290,1.1,BLU,robe=True)
    fill(b,M().rect(180,110,470,270),(0.98,0.93,0.78)); inkline(b,[(180,110),(470,110),(470,270),(180,270),(180,110)],3)
    for k in range(6): inkline(b,[(200,135+k*24),(450-((k*29)%60),135+k*24)],2)
    cerberus(b,250,630,0.85,50,t)
    def hd(d,t=t):
        caption(d,"Hesiod's Theogony · c. 700 BC",540,110,36,a=ap(t,EV["theog"]-0.3,99),sc=pop(t,EV["theog"]-0.4))
        caption(d,"50 heads · bronze voice",540,690,44,a=ap(t,EV["fiftyh"]-0.2,99),sc=pop(t,EV["fiftyh"]-0.3),bg=(255,255,255))
    return b,[hd]
def hydra(b,cx,by,s,t):
    body=M().ell(cx,by-40*s,70*s,40*s); inked(b,body,GRN,3,shade=(yy>by-40*s).astype(np.float32))
    for i,a in enumerate(np.linspace(-2.6,-0.5,7)):
        pts=[(cx+math.cos(a)*q*120*s+8*math.sin(q*6+t*3+i)*s,by-60*s+math.sin(a)*q*120*s) for q in np.linspace(0,1,10)]
        inkline(b,pts,9*s); fill(b,M().pline(pts,5*s),GRN)
        hx,hy=pts[-1]; inked(b,M().ell(hx,hy,12*s,8*s,math.degrees(a)),GRN,2); fill(b,M().circ(hx+2*s,hy-2*s,2*s),YEL)
def s_family(t):
    b=page(); W3=(PX1-PX0)/3
    for i,(bgc,key) in enumerate(((BLU,"orthrus"),(RED,"orthrus"),(GRN,"hydra"))):
        x0=PX0+i*W3+(4 if i else 0); panel(b,x0,PY0+80,x0+W3-8,PY1-120,"dots",0.4,bgc)
    k1=sm((t-EV["orthrus"]+0.3)/0.4); k3=sm((t-EV["hydra"]+0.3)/0.4)
    base_=b.copy()
    if k1>0: cerberus(b,PX0+W3*0.45,PY1-230,0.5,2,t,col=(0.35,0.24,0.14))
    cerberus(b,PX0+W3*1.45,PY1-230,0.5,3,t)
    if k3>0: hydra(b,PX0+W3*2.5,PY1-230,0.62,t)
    def hd(d,t=t):
        caption(d,"Family",540,140,52,a=ap(t,Lx("His brother")[0]-0.2,99))
        caption(d,"Orthrus",PX0*2+W3*1,1110,34,a=ap(t,EV["orthrus"],99),bg=(255,255,255))
        caption(d,"Cerberus",PX0*2+W3*3,1110,34,a=ap(t,EV["orthrus"],99),bg=(255,255,255))
        caption(d,"Hydra",PX0*2+W3*5,1110,34,a=ap(t,EV["hydra"]-0.1,99),bg=(255,255,255))
    return b,[hd]
def s_hundred(t):
    b=page(); panel(b,PX0,PY0,PX1,PY1,"burst")
    cerberus(b,250,620,1.0,100,t)
    def hd(d,t=t):
        caption(d,"Pindar: a hundred heads!",540,130,50,a=ap(t,EV["pindar"]-0.2,99),sc=pop(t,EV["pindar"]-0.3))
        sfx(d,"100!",820,330,130,a=ap(t,EV["hundred"]-0.2,99),sc=pop(t,EV["hundred"]-0.3),col=(250,240,90))
    return b,[hd]
def s_vase(t):
    b=page(); panel(b,PX0,PY0,PX1,PY1,(0.99,0.95,0.86))
    vm=M().poly([(190,150),(350,150),(330,190),(420,280),(430,420),(380,560),(160,560),(110,420),(120,280),(210,190)])
    inked(b,vm,(0.80,0.42,0.20),4)
    fill(b,M().rect(130,300,410,470).f()*vm.f(),(0.10,0.08,0.08))
    k3=sm((t-EV["threex"]+0.3)/0.5)
    sub=b.copy(); cerberus(sub,270,460,0.62,2 if k3<0.5 else 3,t,col=(0.80,0.42,0.20))
    msk=(M().rect(130,300,410,470).f()*vm.f())[...,None]; b=b*(1-msk)+sub*msk
    def hd(d,t=t):
        caption(d,"Artists settled for fewer",540,130,44,a=ap(t,EV["artists"]-0.3,EV["two"]-0.1),sc=pop(t,EV["artists"]-0.4))
        caption(d,"Greek vases: usually 2",540,130,46,a=ap(t,EV["two"]-0.1,EV["threex"]-0.2),sc=pop(t,EV["two"]-0.2))
        caption(d,"Later writers: 3",540,130,52,a=ap(t,EV["threex"]-0.2,99),sc=pop(t,EV["threex"]-0.3))
    return b,[hd]
GH=[(0.0,0),(0.35,1),(0.7,2)]
def ghost(b,x,y,s,a=1.0):
    m=M().ell(x,y,18*s,26*s); m.poly([(x-18*s,y),(x+18*s,y),(x+18*s,y+30*s),(x+9*s,y+22*s),(x,y+30*s),(x-9*s,y+22*s),(x-18*s,y+30*s)])
    inked(b,m,(0.92,0.95,1.0),2,a); fill(b,M().circ(x-6*s,y-4*s,3*s),INK,a); fill(b,M().circ(x+6*s,y-4*s,3*s),INK,a)
def s_gate(t):
    b=page(); panel(b,PX0,PY0,PX1,PY1,"dots",0.55,PUR)
    gm=M().rect(330,140,470,600); inked(b,gm,(0.12,0.10,0.14),4); fill(b,M().ell(400,140,70,50),(0.12,0.10,0.14)); inkline(b,[(330,140),(330,600)],4)
    cerberus(b,230,610,0.75,3,t)
    k=cl((t-EV["deadin"]+0.5)/1.6)
    for o,i in GH:
        u=cl(k*1.4-o);
        if 0<u<1: ghost(b,60+290*u,320+i*60,0.9,1-cl((u-0.85)/0.15))
    ke=cl((t-EV["ate"]+0.4)/0.8)
    if ke>0: ghost(b,360-160*ke,200,0.9,1-cl((ke-0.8)/0.2))
    def hd(d,t=t):
        caption(d,"In: welcome",300,140,44,a=ap(t,EV["deadin"]-0.3,99),sc=pop(t,EV["deadin"]-0.4),bg=(140,230,140))
        caption(d,"Out: eaten",300,220,44,a=ap(t,EV["ate"]-0.2,99),sc=pop(t,EV["ate"]-0.3),bg=(250,120,110))
        sfx(d,"CHOMP!",640,460,100,a=ap(t,EV["leave"]-0.1,99),sc=pop(t,EV["leave"]-0.2),col=(250,90,60),rot=10)
    return b,[hd]
def s_heracles(t):
    b=page(); panel(b,PX0,PY0,PX1,PY1,"burst")
    k=sm((t-EV["dragged"]+0.3)/1.5)
    hero(b,380-40*k,600,1.5,ORN,lion=True)
    cerberus(b,170-40*k,610,0.8,3,t)
    inkline(b,[(330-40*k,430),(250-40*k,480),(225-40*k,520)],4)
    def hd(d,t=t):
        caption(d,"Heracles · labor no. 12",540,130,46,a=ap(t,EV["heracles"]-0.3,99),sc=pop(t,EV["heracles"]-0.4))
        sfx(d,"HEAVE!",820,330,96,a=ap(t,EV["dragged"],99),sc=pop(t,EV["dragged"]-0.1),col=(250,240,90),rot=6)
    return b,[hd]
def s_orpheus(t):
    b=page(); panel(b,PX0,PY0,PX1,PY1,"dots",0.4,BLU)
    hero(b,400,610,1.4,GRN,lyre=True)
    sl=sm((t-EV["music"]+0.2)/0.6); cerberus(b,190,610,0.75,3,t,sleep=sl)
    for k in range(5):
        u=(t*0.6+k*0.2)%1; x=360-200*u; y=360-60*math.sin(u*math.pi)-k*12
        fill(b,M().ell(x,y,7,5,-20),INK); inkline(b,[(x+6,y),(x+6,y-22)],2.5)
    def hd(d,t=t):
        caption(d,"Orpheus",540,130,56,a=ap(t,EV["orpheus"]-0.3,99),sc=pop(t,EV["orpheus"]-0.4))
        sfx(d,"zzz",300,330,90,a=sl,col=(255,255,255),rot=-12)
    return b,[hd]
def s_cake(t):
    b=page(); panel(b,PX0,PY0,PX1,PY1,"dots",0.4,ORN)
    hero(b,420,610,1.4,PUR,robe=True)
    k=cl((t-EV["cake"]+0.6)/0.8); x=390-200*k; y=420-120*math.sin(math.pi*k)+60*k
    sl=sm((t-EV["cake"]-0.4)/0.8); cerberus(b,180,610,0.75,3,t,sleep=sl)
    if k<1: inked(b,M().ell(x,y,16,10),YEL,2); dots(b,M().ell(x,y,16,10),ORN,0.5)
    def hd(d,t=t):
        caption(d,"Virgil · Aeneid VI",540,130,46,a=ap(t,EV["virgil"]-0.3,EV["cake"]-0.1),sc=pop(t,EV["virgil"]-0.4))
        caption(d,"A drugged honey cake",540,130,46,a=ap(t,EV["cake"]-0.1,99),sc=pop(t,EV["cake"]-0.2))
    return b,[hd]
def s_three(t):
    b=page(); H3=(PY1-PY0)/3
    keys=["strength","music2","snack"]; cols=[RED,BLU,ORN]
    for i in range(3):
        y0=PY0+i*H3+(4 if i else 0); panel(b,PX0,y0,PX1,y0+H3-8,"dots",0.4,cols[i])
    k=[sm((t-EV[x]+0.3)/0.4) for x in keys]
    yc=[PY0+H3*(i+0.5) for i in range(3)]
    if k[0]>0: fill(b,M().circ(150,yc[0],40*k[0]),(0.95,0.78,0.62)); inked(b,M().circ(150,yc[0],40*k[0]+0.5),(0.95,0.78,0.62),3)
    if k[1]>0: hero(b,150,yc[1]+80,0.8,GRN,lyre=True)
    if k[2]>0: inked(b,M().ell(150,yc[2],44*k[2]+0.5,26*k[2]+0.5),YEL,3); dots(b,M().ell(150,yc[2],44*k[2]+0.5,26*k[2]+0.5),ORN,0.5)
    def hd(d,t=t):
        for i,(kk,s) in enumerate(zip(keys,("strength","music","a snack"))):
            caption(d,s,700,2*yc[i],56,a=ap(t,EV[kk]-0.2,99),sc=pop(t,EV[kk]-0.3),bg=(255,255,255))
        caption(d,"Beaten 3 times",540,95,44,a=ap(t,EV["beaten"]-0.3,EV["strength"]-0.1),sc=pop(t,EV["beaten"]-0.4))
    return b,[hd]
def s_sop(t):
    b=page(); panel(b,PX0,PY0,PX1,PY1,(0.99,0.95,0.86))
    card=M().rect(70,180,470,520); inked(b,card,(1,1,1),4); dots(b,M().rect(70,180,470,240),YEL,0.6)
    def hd(d,t=t):
        a=ap(t,EV["phrase"]-0.4,99)
        if a>0.01:
            d.text((540,420),"sop to Cerberus",font=_f("EricaOne-Regular.ttf",76),fill=(20,16,18,int(255*a)),anchor="mm")
            d.text((180,560),"(n.) a small bribe or",font=_f("WorkSans-BoldItalic.ttf",44),fill=(20,16,18,int(255*ap(t,EV["bribe"]-0.3,99))),anchor="lm")
            d.text((180,630),"concession to keep",font=_f("WorkSans-BoldItalic.ttf",44),fill=(20,16,18,int(255*ap(t,EV["bribe"]-0.1,99))),anchor="lm")
            d.text((180,700),"trouble quiet",font=_f("WorkSans-BoldItalic.ttf",44),fill=(20,16,18,int(255*ap(t,EV["quiet"]-0.3,99))),anchor="lm")
            d.text((180,800),"(from Virgil's honey cake)",font=_f("WorkSans-BoldItalic.ttf",34),fill=(150,40,30,int(255*ap(t,EV["quiet"],99))),anchor="lm")
        caption(d,"Old English idiom",540,180,46,a=ap(t,EV["phrase"]-0.6,99),sc=pop(t,EV["phrase"]-0.7))
    return b,[hd]
def s_end(t): return s_hook(t,end=True)
TR=0.34; TOTAL=B.TOTAL; LOOPD=0.6
SHOTS=[(0.0,s_hook),(S("heads")["s"],s_hesiod),(Lx("His brother")[0]-0.3,s_family),(Lx("The poet Pindar")[0]-0.3,s_hundred),(Lx("Artists")[0]-0.3,s_vase),
       (S("job")["s"],s_gate),(Lx("Heracles")[0]-0.3,s_heracles),(Lx("Orpheus")[0]-0.3,s_orpheus),(S("sop")["s"],s_cake),(Lx("Beaten")[0]-0.3,s_three),
       (Lx("That's the origin")[0]-0.3,s_sop),(Lx("So whenever")[0]-0.3,s_end)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
def slide(b1,b2,u,idx):
    """comic page turn: the new panel slides in over the old one with a hard ink edge and speed lines"""
    k=sm(u); dx=int((1-k)*w)*(1 if idx%2 else -1)
    M2=np.float32([[1,0,dx],[0,1,0]]); n2=cv2.warpAffine(b2,M2,(w,h),borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0))
    mk=np.zeros((h,w),np.float32)
    if dx>=0: mk[:,dx:]=1
    else: mk[:,:w+dx]=1
    out=b1*(1-mk[...,None])+n2*mk[...,None]
    ex=dx if dx>=0 else w+dx
    if 0<ex<w:
        out[:,max(0,ex-3):ex+3]=INK
        for k_ in range(8):
            y=60+k_*75; x0=ex+(30 if dx>=0 else -30); inkline(out,[(x0,y),(x0+(90 if dx>=0 else -90),y)],2,0.7)
    out[668:]=page()[668:]
    return out
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)),i+1)
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)),i)
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD),0)
    if pair is None: buf,hud=SHOTS[i][1](t); hk=1.0
    else:
        fa_,fb_,ta,tb,u,idx=pair; b1,h1=fa_(ta); b2,h2=fb_(tb)
        buf=slide(b1,b2,u,idx); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
