import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid53")
for p in ["/home/claude/vid53","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
import drawkit as K
from drawkit import ink, outl, hatch, wash, part, dl, circ_pts, rotp, dashl
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= palette (1930s war-room table map) =================
MAPP=(0.88,0.84,0.70); CONT=(0.55,0.38,0.22); ARMY=(0.16,0.30,0.62); EMUR=(0.76,0.16,0.12); WHEAT=(0.90,0.74,0.30); OLIVE=(0.36,0.40,0.22)
INKM=(0.12,0.10,0.08); CHIP=(0.93,0.88,0.74); K.INK=INKM
cInk=(30,26,22); cRed=(190,40,30); cBlue=(40,76,158); cSlip=(248,244,232); cOl=(84,92,52)
_IF={}
def _f(path,s):
    k=(path,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(path,s)
    return _IF[k]
FST=P.FD+"BigShoulders-Bold.ttf"
def ttl(d,s,x,y,fs=120,a=1.0,sc=1.0,col=cRed):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f(FST,n)
    while f.getlength(s)>1000 and n>20: n-=6; f=_f(FST,n)
    d.text((x+3,y+4),s,font=f,fill=(0,0,0,int(90*a)),anchor="mm"); d.text((x,y),s,font=f,fill=col+(int(255*a),),anchor="mm",stroke_width=3,stroke_fill=(250,244,230,int(230*a)))
_SL={}
def slip(d,s,x,y,fs=44,a=1.0,sc=1.0,ang=-2,pin=True):
    """typed note on a paper slip, pinned to the map"""
    if a<=0.01 or sc<=0.02: return
    k=(s,fs,ang,pin)
    if k not in _SL:
        f=_f(P.FD+"IBMPlexMono-Bold.ttf",fs); lines=s.split("\n"); d0=ImageDraw.Draw(Image.new("RGBA",(4,4)))
        tw=max(d0.textbbox((0,0),l,font=f)[2] for l in lines); lh=int(fs*1.25); th=lh*len(lines); px,py=int(fs*0.6),int(fs*0.5); m=20
        im=Image.new("RGBA",(tw+2*px+2*m,th+2*py+2*m),(0,0,0,0)); dd=ImageDraw.Draw(im)
        dd.rectangle((m+5,m+8,m+tw+2*px+5,m+th+2*py+8),fill=(0,0,0,70)); dd.rectangle((m,m,m+tw+2*px,m+th+2*py),fill=cSlip+(255,))
        for i,l in enumerate(lines): dd.text((m+px,m+py+i*lh),l,font=f,fill=cInk+(255,))
        if pin: dd.ellipse((m+(tw+2*px)/2-9,m-4,m+(tw+2*px)/2+9,m+14),fill=(200,30,30,255),outline=(90,10,10,255),width=2)
        im=im.rotate(ang,resample=Image.BICUBIC,expand=True); _SL[k]=im
    im=_SL[k]
    if abs(sc-1)>0.01: q=max(0.05,round(sc*20)/20); im=im.resize((max(1,int(im.width*q)),max(1,int(im.height*q))),Image.BILINEAR)
    if a<0.99: ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); im=Image.fromarray(ar)
    paste(d,im,x-im.width/2,y-im.height/2)
_ST={}
def stamp(d,s,x,y,fs=90,a=1.0,ang=-10,sc=1.0,col=cRed):
    if a<=0.01 or sc<=0.02: return
    k=(s,fs,ang,col)
    if k not in _ST:
        f=_f(FST,fs); bb=ImageDraw.Draw(Image.new("RGBA",(4,4))).textbbox((0,0),s,font=f); tw,th=bb[2]-bb[0],bb[3]-bb[1]; px,py=int(fs*0.3),int(fs*0.2); m=16
        im=Image.new("RGBA",(tw+2*px+2*m,th+2*py+2*m),(0,0,0,0)); dd=ImageDraw.Draw(im)
        dd.rectangle((m,m,m+tw+2*px,m+th+2*py),outline=col+(255,),width=max(5,fs//12)); dd.text((m+px-bb[0],m+py-bb[1]),s,font=f,fill=col+(255,))
        ar=np.array(im).astype(np.float32); g=np.random.default_rng(len(s)); nz=cv2.GaussianBlur(g.random(ar.shape[:2]).astype(np.float32),(0,0),1.5); nz=(nz-nz.min())/(nz.max()-nz.min()+1e-6)
        ar[...,3]*=np.clip(0.55+nz*0.9,0,1)*0.9; _ST[k]=Image.fromarray(ar.astype(np.uint8)).rotate(ang,resample=Image.BICUBIC,expand=True)
    im=_ST[k]
    if abs(sc-1)>0.01: q=max(0.05,round(sc*20)/20); im=im.resize((max(1,int(im.width*q)),max(1,int(im.height*q))),Image.BILINEAR)
    if a<0.99: ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); im=Image.fromarray(ar)
    paste(d,im,x-im.width/2,y-im.height/2)
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
def slam(t,e): k=cl((t-e+0.05)/0.18); return 1.0+1.2*(1-k)**2
# ================= the big table map (4 regions, wraps horizontally) =================
NREG=4; BW=w*NREG
_g=np.random.default_rng(1932)
def _wrapnoise(cell,seed):
    g=np.random.default_rng(seed); gw,gh=BW//cell,h//cell+2
    a=g.normal(0,1,(gh,gw)).astype(np.float32); a=np.hstack([a,a[:,:3]])
    big=cv2.resize(a,((gw+3)*cell,gh*cell),interpolation=cv2.INTER_CUBIC)[:h,:BW+0]
    return big
HGT=_wrapnoise(120,1)*0.7+_wrapnoise(45,2)*0.3
BYY,BXX=np.mgrid[0:h,0:BW].astype(np.float32)
BIG=np.zeros((h,BW,3),np.float32); BIG[:]=MAPP
BIG+=(np.clip(HGT,-1.5,1.5)*0.035)[...,None]*np.array((0.6,0.3,-0.2),np.float32)
lev=HGT*5.0; fr=np.abs(lev-np.round(lev))
cont=np.clip(1-fr/0.05,0,1); major=(np.abs(np.round(lev))%4==0)
BIG=BIG*(1-(cont*np.where(major,0.6,0.32))[...,None])+np.array(CONT,np.float32)*(cont*np.where(major,0.6,0.32))[...,None]
grid=(((BXX%60)<1.2)|((BYY%60)<1.2)).astype(np.float32)*0.22
BIG=BIG*(1-grid[...,None])+np.array((0.35,0.45,0.55),np.float32)*grid[...,None]
_st=cv2.GaussianBlur(_g.random((h,BW)).astype(np.float32),(0,0),30); _st=(_st-_st.mean())/_st.std()
BIG*=(1-0.04*_st)[...,None]
# wheat fields + farms + roads painted per region
def _paint_big():
    global BIG
    fields=[(0,1,(330,420,480,560)),(1,1,(40,380,240,560)),(1,1,(300,330,500,500)),(2,1,(60,470,250,600)),(3,1,(280,420,500,580))]
    for reg,_,(x0,y0,x1,y1) in fields:
        X0=reg*w+x0; m=np.zeros((h,BW),np.float32); m[y0:y1,X0:X0+(x1-x0)]=1
        pat=(((BXX+BYY)%9)<1.6).astype(np.float32)
        BIG=BIG*(1-(m*0.30)[...,None])+np.array(WHEAT,np.float32)*(m*0.30)[...,None]
        BIG=BIG*(1-(m*pat*0.35)[...,None])+np.array((0.62,0.48,0.16),np.float32)*(m*pat*0.35)[...,None]
        BIG[y0:y1,X0:X0+2]=INKM; BIG[y0:y1,X0+(x1-x0)-2:X0+(x1-x0)]=INKM; BIG[y0:y0+2,X0:X0+(x1-x0)]=INKM; BIG[y1-2:y1,X0:X0+(x1-x0)]=INKM
    rd=np.zeros((h,BW),np.float32)
    xs=np.arange(BW); ys=(640+30*np.sin(xs*2*np.pi*6/BW)).astype(int)
    for x,y in zip(xs,ys):
        if (x//14)%2==0: rd[y-2:y+2,x]=1
    BIG=BIG*(1-(rd*0.7)[...,None])+np.array((0.30,0.22,0.16),np.float32)*(rd*0.7)[...,None]
_paint_big()
def region(k,off=0):
    x0=(k*w+off)%BW
    if x0+w<=BW: return BIG[:,x0:x0+w].copy()
    return np.hstack([BIG[:,x0:],BIG[:,:x0+w-BW]]).copy()
# ================= map counters & arrows =================
def emu_sil(m,x,y,s,ph=0.0,run=1.0):
    m.ell(x,y-26*s,16*s,11*s,ang=-10)
    m.pline([(x+10*s,y-30*s),(x+16*s,y-50*s),(x+14*s,y-64*s)],4*s); m.ell(x+17*s,y-66*s,5*s,4*s); m.poly([(x+21*s,y-67*s),(x+28*s,y-65*s),(x+21*s,y-63*s)])
    for sd in (-1,1):
        sw=math.sin(ph+sd*1.6)*run
        knee=(x+sd*3*s+sw*6*s,y-8*s); m.line((x+sd*3*s,y-18*s),knee,2.5*s).line(knee,(x+sd*2*s+sw*12*s,y),2.5*s)
    return m
def chip(buf,x,y,kind,a=1.0,s=1.0):
    if a<=0: return
    m=M().rect(x-22*s,y-16*s,x+22*s,y+16*s); comp(buf,m,CHIP,sh=0.4,dx=2,dy=4,blur=3,rim=0,a=a); outl(buf,m,a=a,th=1,fill=0)
    if kind=="emu":
        inner=emu_sil(M(),x-2*s,y+12*s,0.45*s,0,0); comp(buf,inner,EMUR,sh=0,rim=0,a=a)
    elif kind=="inf":
        r=M().rect(x-16*s,y-10*s,x+16*s,y+10*s); outl(buf,r,a=a,th=1,fill=0,col=ARMY); ink(buf,M().line((x-16*s,y-10*s),(x+16*s,y+10*s),2).line((x-16*s,y+10*s),(x+16*s,y-10*s),2),a,col=ARMY)
    elif kind=="mg":
        r=M().rect(x-16*s,y-10*s,x+16*s,y+10*s); outl(buf,r,a=a,th=1,fill=0,col=ARMY); ink(buf,M().line((x-10*s,y),(x+12*s,y),3).line((x+6*s,y-6*s),(x+12*s,y),2).line((x+6*s,y+6*s),(x+12*s,y),2),a,col=ARMY)
    elif kind=="hq":
        r=M().rect(x-16*s,y-10*s,x+16*s,y+10*s); comp(buf,r,ARMY,sh=0,rim=0,a=a); ink(buf,M().line((x-16*s,y-10*s),(x-16*s,y-30*s),2),a); comp(buf,M().poly([(x-16*s,y-30*s),(x+2*s,y-25*s),(x-16*s,y-20*s)]),EMUR,sh=0,rim=0,a=a)
    elif kind=="truck":
        r=M().rect(x-16*s,y-6*s,x+16*s,y+8*s).rect(x+6*s,y-12*s,x+16*s,y-6*s); comp(buf,r,ARMY,sh=0,rim=0,a=a); comp(buf,M().circ(x-9*s,y+10*s,4*s).circ(x+9*s,y+10*s,4*s),INKM,sh=0,rim=0,a=a)
def arrow(buf,pts,u,col,a=1.0,wd=14,head=26,dash=False):
    if u<=0 or a<=0: return
    q=part(np.array(pts,np.float64),u)
    if len(q)<2: return
    left=[];right=[]
    for i in range(len(q)):
        p=q[i]; p2=q[min(i+1,len(q)-1)]; p1=q[max(i-1,0)]; dx,dy=p2[0]-p1[0],p2[1]-p1[1]; n=math.hypot(dx,dy)+1e-6
        wd_=wd*(0.55+0.45*i/max(1,len(q)-1))
        left.append((p[0]-dy/n*wd_/2,p[1]+dx/n*wd_/2)); right.append((p[0]+dy/n*wd_/2,p[1]-dx/n*wd_/2))
    m=M().poly(left+right[::-1])
    tip=q[-1]; pr=q[-2]; dx,dy=tip[0]-pr[0],tip[1]-pr[1]; n=math.hypot(dx,dy)+1e-6; ux,uy=dx/n,dy/n
    m.poly([(tip[0]+ux*head,tip[1]+uy*head),(tip[0]-uy*head*0.7,tip[1]+ux*head*0.7),(tip[0]+uy*head*0.7,tip[1]-ux*head*0.7)])
    if dash:
        A=m.f()*((((BXX[:, :w]+BYY[:, :w])%18)<11).astype(np.float32)); comp(buf,A*a,col,sh=0,rim=0)
    else:
        comp(buf,m,col,sh=0.3,dx=2,dy=3,blur=3,rim=0,a=a*0.85); outl(buf,m,a=a*0.8,th=1,fill=0)
def herd(buf,cx,cy,n,t,spread=60,a=1.0,vx=30,seed=0,s=0.8):
    if a<=0: return
    g=np.random.default_rng(seed); m=M()
    for k in range(n):
        x=cx+g.normal(0,spread)+((t*vx+g.uniform(0,200))%200)-100 if vx else cx+g.normal(0,spread)
        y=cy+g.normal(0,spread*0.5)
        emu_sil(m,x,y,s*g.uniform(0.8,1.2),t*14+k,1.0 if vx else 0.2)
    comp(buf,m,(0.20,0.14,0.10),sh=0.25,dx=1,dy=3,blur=2,rim=0,a=a)
def farm(buf,x,y,a=1.0):
    m=M().rect(x-14,y-12,x+14,y+6).poly([(x-18,y-12),(x,y-26),(x+18,y-12)]); comp(buf,m,(0.80,0.30,0.22),sh=0.3,rim=0,a=a); outl(buf,m,a=a,th=1,fill=0)
def compass(buf,x,y,a=1.0):
    m=M().poly([(x,y-34),(x+7,y),(x,y+34),(x-7,y)]).poly([(x-34,y),(x,y-7),(x+34,y),(x,y+7)]); outl(buf,m,a=a,th=1,fill=0.25); ink(buf,M().poly([(x,y-34),(x+7,y),(x,y)]),a)
# ================= scenes (each lives on its own region of the table) =================
def s_hook(t,sc,off=0):
    tt=max(t,-1.0); buf=region(0,off); hud=[]
    compass(buf,470,140,0.8)
    chip(buf,140,420,"hq",1.0,1.3); chip(buf,190,470,"inf",1.0,1.2); chip(buf,120,500,"mg",1.0,1.2)
    herd(buf,380,470,26,tt,55,1.0,-26,1,0.9)
    arrow(buf,[(470,360),(380,380),(260,430),(220,450)],cl((tt+1.0)/1.6),EMUR,1.0,16,28)
    lo=sm((tt-EV["lost"]+0.2)/0.6)
    if lo>0: arrow(buf,[(150,520),(110,580),(70,640)],lo,ARMY,0.9,12,22,dash=True)
    def hd(d,t=t):
        k0=1.0 if t<0.4 else ap(t,-1,EV["meta"])
        ttl(d,"AUSTRALIA",540,190,120,a=k0,col=cBlue); ttl(d,"VS. BIRDS",540,320,140,a=k0,col=cRed)
        stamp(d,"LOST",820,1150,120,a=sm((t-EV["lost"]+0.05)/0.15)*(1-sm((t-EV["meta"])/0.3)),ang=-12,sc=slam(t,EV["lost"]))
        slip(d,"NOT A METAPHOR.",540,230,52,a=ap(t,EV["meta"],sc["e"]+1),sc=pop(t,EV["meta"]-0.1))
        for k,(e,s_) in enumerate((("soldiers","SOLDIERS"),("mguns","MACHINE GUNS"),("emus0","EMUS"))):
            slip(d,s_,[230,560,860][k],1200+(k%2)*60,46,a=ap(t,EV[e],sc["e"]+1),sc=pop(t,EV[e]-0.1),ang=[-4,3,-2][k])
    return buf,[hd]
def s_setup(t,sc,off=0):
    buf=region(1,off); hud=[]
    for x,y in ((120,360),(420,300),(260,620)): farm(buf,x,y,1.0)
    ea=sm((t-EV["twenty"]+0.4)/0.5)
    n=int(10+40*sm((t-EV["twenty"]+0.2)/1.2))
    herd(buf,260,250,n,t,90,ea,22,2,0.75)
    arrow(buf,[(80,180),(160,300),(150,420)],sm((t-EV["wheat"]+0.3)/0.7),EMUR,1.0,16,26)
    arrow(buf,[(470,160),(420,250),(400,330)],sm((t-EV["wheat"]+0.1)/0.7),EMUR,1.0,16,26)
    vet=sm((t-EV["veterans"]+0.3)/0.4)*(1-sm((t-EV["major"]+0.3)/0.4))
    if vet>0:
        hm=M().ell(270,420,40,14).ell(270,404,34,22); comp(buf,hm,OLIVE,sh=0.4,rim=0,a=vet); outl(buf,hm,a=vet,th=1,fill=0)
    ob=sm((t-EV["major"]+0.3)/0.4)
    if ob>0:
        for k,(kind,e) in enumerate((("hq","major"),("inf","two"),("mg","guns"),("mg","guns"))):
            chip(buf,90+k*72,690-0,kind,ob*sm((t-EV[e]+0.3-k*0.05)/0.3),1.2)
    def hd(d,t=t):
        slip(d,"W. AUSTRALIA · NOV 1932",540,200,46,a=ap(t,EV["wa"],EV["farmers"]),sc=pop(t,EV["wa"]-0.1))
        ttl(d,"~20,000 EMUS",540,1180,120,a=ap(t,EV["twenty"],EV["farmers"]),sc=pop(t,EV["twenty"]-0.1))
        slip(d,"WHEAT FARMS",760,330,40,a=ap(t,EV["wheat"],EV["farmers"]),ang=4)
        slip(d,"FARMERS = WWI VETERANS",540,200,46,a=ap(t,EV["veterans"],EV["major"]),sc=pop(t,EV["veterans"]-0.1))
        stamp(d,"REQUEST: ARMY",540,1180,80,a=ap(t,EV["help"],EV["major"])*sm((t-EV["help"]+0.05)/0.15),ang=-6,sc=slam(t,EV["help"]),col=cBlue)
        slip(d,"ORDER OF BATTLE:\n1 MAJOR · 2 SOLDIERS\n2 LEWIS GUNS\n10,000 ROUNDS",540,240,40,a=ap(t,EV["major"],sc["e"]+1),sc=pop(t,EV["major"]-0.1))
    return buf,[hd]
def s_battle(t,sc,off=0):
    buf=region(2,off); hud=[]
    pT=sm((t-EV["truck"]+0.3)/0.4); pQ=sm((t-EV["said"]+0.3)/0.4)
    a1=1-pT
    if a1>0:
        chip(buf,120,560,"mg",a1,1.4)
        sc_=sm((t-EV["scatter"]+0.2)/1.2)
        for k in range(7):
            an=-1.2+k*0.4; p0=(150,520); p1=(150+math.cos(an)*330*sc_+1,520+math.sin(an)*260*sc_)
            arrow(buf,[p0,((p0[0]+p1[0])/2+20*math.sin(k),(p0[1]+p1[1])/2),p1],sc_,EMUR,a1*0.9,8,16)
            herd(buf,p1[0],p1[1],3,t,10+30*(1-sc_),a1,0,10+k,0.7)
        jm=sm((t-EV["jams"]+0.1)/0.2)
        if jm>0: ink(buf,M().circ(120,560,34).circ(120,560,30),0.0)
    if pT>0 and pQ<1:
        a2=pT*(1-pQ); k=sm((t-EV["truck"]+0.2)/2.6)
        tx=80+260*k; chip(buf,tx,620,"truck",a2,1.5)
        ex=min(tx+90+(t-EV["truck"])*70,455)
        herd(buf,ex,600,8,t,22,a2,0,20,1.0)
        ink(buf,dashl(M(),(tx+30,620),(ex-30,610),8,6,2),a2*0.7,col=ARMY)
        sp=sm((t-EV["kmh"]+0.3)/0.4)
        if sp>0:
            m=M()
            for j in range(5): m.line((ex+40+j*8,560+j*12),(ex+80+j*8,560+j*12),2)
            ink(buf,m,a2*sp,col=EMUR)
    if pQ>0:
        a3=pQ; herd(buf,270,560,12,t,70,a3,0,30,1.2)
        tm=M().rect(150,250,390,330).rect(250,220,330,250).rect(330,232,420,240); comp(buf,tm,OLIVE,sh=0.4,rim=0,a=a3*0.35*sm((t-EV["tanks"]+0.3)/0.4)); outl(buf,tm,a=a3*0.5*sm((t-EV["tanks"]+0.3)/0.4),th=1,fill=0)
    def hd(d,t=t):
        ttl(d,"THEY SCATTER",540,200,120,a=ap(t,EV["scatter"],EV["jams"]),sc=pop(t,EV["scatter"]-0.1))
        stamp(d,"GUN JAMMED",540,1180,96,a=ap(t,EV["jams"],EV["truck"])*sm((t-EV["jams"]+0.05)/0.15),ang=-8,sc=slam(t,EV["jams"]))
        slip(d,"PLAN B: GUN ON A TRUCK",540,200,46,a=ap(t,EV["truck"],EV["sprint"]),sc=pop(t,EV["truck"]-0.1))
        ttl(d,"OUTRUN!",540,1180,130,a=ap(t,EV["outrun"],EV["sprint"]),sc=pop(t,EV["outrun"]-0.1))
        ttl(d,"~50 KM/H",540,200,140,a=ap(t,EV["kmh"]-0.3,EV["said"]),sc=pop(t,EV["kmh"]-0.4))
        slip(d,"MAJ. MEREDITH:\n“…THE INVULNERABILITY\nOF TANKS.”",540,250,44,a=ap(t,EV["face"],sc["e"]+1),sc=pop(t,EV["face"]-0.1),ang=2)
    return buf,[hd]
def s_end(t,sc,off=0):
    buf=region(3,off); hud=[]
    rt=sm((t-EV["pulled"]+0.3)/1.0)
    chip(buf,360-200*rt,560,"hq",1.0,1.3); chip(buf,410-200*rt,600,"mg",1.0,1.2)
    if rt>0: arrow(buf,[(380,620),(280,660),(150,690)],rt,ARMY,0.9,12,22,dash=True)
    herd(buf,380,420,22,t,70,1.0,0,40,0.8)
    tl=int(cl((t-EV["rounds"]+0.3)/1.4)*100)
    if tl>0:
        m=M()
        for k in range(tl):
            gx=40+(k%20)*12; gy=150+(k//20)*22; m.rect(gx,gy,gx+4,gy+14)
        comp(buf,m,(0.72,0.56,0.22),sh=0,rim=0,a=1.0-sm((t-EV["again"]+0.3)/0.4))
    def hd(d,t=t):
        ttl(d,"~10,000 ROUNDS",540,620,110,a=ap(t,EV["rounds"],EV["again"]),sc=pop(t,EV["rounds"]-0.1),col=cInk)
        slip(d,"ARMY WITHDRAWS",540,1310,52,a=ap(t,EV["pulled"],EV["again"]),sc=pop(t,EV["pulled"]-0.1))
        for k,yr in enumerate(("1934","1943","1948")):
            e=EV["three"]+k*0.35
            slip(d,f"REQUEST {yr}",[230,540,850][k],230+(k%2)*80,40,a=ap(t,e,EV["won"]),sc=pop(t,e-0.1),ang=[-3,2,-1][k])
            stamp(d,"DENIED",[230,540,850][k],230+(k%2)*80,50,a=ap(t,EV["no"]+k*0.12,EV["won"])*sm((t-EV["no"]-k*0.12+0.05)/0.15),ang=-14,sc=slam(t,EV["no"]+k*0.12))
        ttl(d,"EMUS WIN",540,1180,150,a=ap(t,EV["won"]-0.1,sc["e"]+1),sc=pop(t,EV["won"]-0.2),col=cRed)
    return buf,[hd]
SCN=dict(hook=s_hook,setup=s_setup,battle=s_battle,end=s_end); RIDX=dict(hook=0,setup=1,battle=2,end=3)
BAND=(1-0.40*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.34*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.008,(h,w,1)).astype(np.float32) for i in range(6)]
TR=0.36; TOTAL=B.TOTAL; LOOPD=0.7
def render_scene(t,sc,off=0): return SCN[sc["name"]](t,sc,off)
def pan(b1,b2,u):
    """camera glides across the war table to the next region (they are neighbours on one big map)"""
    k=0.5*(1-math.cos(math.pi*u)); off=int(round(k*w))
    out=np.empty_like(b1)
    if off<w: out[:,:w-off]=b1[:,off:]
    if off>0: out[:,w-off:]=b2[:,:off]
    sp=math.sin(math.pi*u)
    if sp>0.05: out=cv2.blur(out,(max(1,int(sp*22)),1))
    return out,off
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(sc,SC[i+1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SC[i-1],sc,t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(sc,SC[0],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    ovs=[]
    if pair is None:
        buf,hud=render_scene(t,sc); ovs=[(hud,0,1.0)]
    else:
        A_,B2,ta,tb,u=pair
        b1,h1=render_scene(ta,A_); b2,h2=render_scene(tb,B2)
        buf,off=pan(b1,b2,u); ovs=[(h1,-off*2,1.0),(h2,(w-off)*2,1.0)]
    buf=np.clip(buf,0,1.2)*PT*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    for hud,dx,a_ in ovs:
        if dx<=-W or dx>=W: continue
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
        for f in hud: f(d)
        img.alpha_composite(ov,(max(0,dx),0),(max(0,-dx),0))
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
