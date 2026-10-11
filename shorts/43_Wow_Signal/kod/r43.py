import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid43")
for p in ["/home/claude/vid43","/home/claude/vid3","/home/claude/ep1"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw
EV=ev.EV; Lx=ev.Lx
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= palette (1977 tractor-feed computer printout + red pen) =================
PAPW=(0.965,0.962,0.930); BARG=(0.845,0.920,0.835); INK=(0.10,0.12,0.25); RED=(0.80,0.13,0.11); HOLE=(0.30,0.28,0.26); YEL=(1.0,0.90,0.40)
cI=(26,30,62); cR=(204,34,28); cPw=(252,250,242); cY=(255,222,96)
def typ(d,s,x,y,fs=54,a=1.0,sc=1.0,ang=0,pad=(24,10)): card(d,s,x,y,fs=fs,a=a,fg=cI,bg=(255,255,255),fn="IBMPlexMono-Bold",torn=False,ang=ang,sc=sc,pad=pad)
def rtag(d,s,x,y,fs=58,a=1.0,sc=1.0,ang=-3,pad=(26,10)): card(d,s,x,y,fs=fs,a=a,fg=(255,255,255),bg=cR,fn="BigShoulders-Bold",torn=False,ang=ang,sc=sc,pad=pad)
def big(d,s,x,y,fs=150,a=1.0,sc=1.0,col=cI): card(d,s,x,y,fs=fs,a=a,fg=col,bg=None,fn="BigShoulders-Bold",torn=False,sc=sc,pad=(6,6))
def dot(d,s,x,y,fs=120,a=1.0,sc=1.0,col=cI): card(d,s,x,y,fs=fs,a=a,fg=col,bg=None,fn="Silkscreen-Regular",torn=False,sc=sc,pad=(4,4))
def pen(d,s,x,y,fs=60,a=1.0,ang=-4,col=cR,rv=1.0):
    if a<=0.01 or rv<=0: return
    im=P._card_img(s,"NothingYouCouldDo-Regular",fs,col,None,ang,(6,6),False,1.18)
    if rv<1: im=im.crop((0,0,max(1,int(im.width*rv)),im.height))
    if a<0.99: ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); im=Image.fromarray(ar)
    full=P._card_img(s,"NothingYouCouldDo-Regular",fs,col,None,ang,(6,6),False,1.18)
    paste(d,im,x-full.width/2,y-full.height/2)
_SC={}
def _stamp_img(s,fs,ang):
    k=(s,fs,ang)
    if k in _SC: return _SC[k]
    f=F("BigShoulders-Bold",fs); d0=ImageDraw.Draw(Image.new("RGBA",(4,4))); bb=d0.textbbox((0,0),s,font=f)
    tw,th=bb[2]-bb[0],bb[3]-bb[1]; px,py=int(fs*0.30),int(fs*0.22); m=20
    im=Image.new("RGBA",(tw+2*px+2*m,th+2*py+2*m),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((m,m,m+tw+2*px,m+th+2*py),radius=int(fs*0.12),outline=cR+(255,),width=max(5,fs//11))
    d.text((m+px-bb[0],m+py-bb[1]),s,font=f,fill=cR+(255,))
    ar=np.array(im).astype(np.float32); g=np.random.default_rng(abs(hash(s))%997)
    nz=cv2.GaussianBlur(g.random(ar.shape[:2]).astype(np.float32),(0,0),1.6); nz=(nz-nz.min())/(nz.max()-nz.min()+1e-6)
    ar[...,3]*=np.clip(0.55+nz*0.9,0,1)*0.92
    im=Image.fromarray(ar.astype(np.uint8)).rotate(ang,resample=Image.BICUBIC,expand=True); _SC[k]=im; return im
def stamp(d,s,x,y,fs=90,a=1.0,ang=-8,sc=1.0):
    if a<=0.01 or sc<=0.02: return
    im=_stamp_img(s,fs,ang)
    if abs(sc-1)>0.01: q=max(0.05,round(sc*20)/20); im=im.resize((max(1,int(im.width*q)),max(1,int(im.height*q))),Image.BILINEAR)
    if a<0.99: ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); im=Image.fromarray(ar)
    paste(d,im,x-im.width/2,y-im.height/2)
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
def slam(t,e):  # stamp: big -> 1 quickly
    k=cl((t-e+0.05)/0.18); return 1.0+1.2*(1-k)**2
# ================= background: green-bar tractor-feed paper =================
BH=32
_g=np.random.default_rng(7)
PAPER=np.zeros((h,w,3),np.float32); PAPER[:]=PAPW
_bar=((yy//BH)%2==0)&(xx>30)&(xx<510)
PAPER[_bar]=BARG
_mot=cv2.resize(_g.normal(0,1,(16,10)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC); _mot/=_mot.std()
PAPER*=(1+0.018*_mot)[...,None]
_hm=M()
for y in range(12,h,24):
    _hm.circ(13.5,y,4.3); _hm.circ(w-13.5,y,4.3)
_ha=_hm.f()[...,None]; PAPER=PAPER*(1-_ha)+np.array(HOLE,np.float32)*_ha
_pm=M()
for y in range(0,h,8): _pm.line((29,y),(29,y+4),1); _pm.line((w-29,y),(w-29,y+4),1)
_pa=_pm.f()[...,None]*0.35; PAPER=PAPER*(1-_pa)+np.array((0.55,0.62,0.55),np.float32)*_pa
# faint row numbers in the margin bars (like real green-bar stock)
# ================= drawing helpers =================
def _bb(m):
    x0,y0=max(0,m.x0),max(0,m.y0); x1,y1=min(w,m.x1),min(h,m.y1); return x0,y0,x1,y1
def ink(buf,m,a=1.0,col=INK): comp(buf,m,col,sh=0,rim=0,a=a)
def outl(buf,m,a=1.0,th=1,fill=0.10,col=INK,fcol=None):
    if m.x1<=m.x0 or a<=0: return
    x0,y0,x1,y1=_bb(m)
    if x1<=x0 or y1<=y0: return
    A=m.m[y0:y1,x0:x1].astype(np.float32)/255; k=2*th+1
    er=cv2.erode(A,np.ones((k,k),np.uint8)); e=np.clip(A-er,0,1)
    Bf=buf[y0:y1,x0:x1]; c=np.array(col,np.float32); fc=np.array(fcol if fcol else col,np.float32)
    Bf+=(fc-Bf)*(A*fill*a)[...,None]; Bf+=(c-Bf)*(e*a)[...,None]
def hatch(buf,m,a=0.5,step=7,col=INK,dirn=1):
    if m.x1<=m.x0: return
    x0,y0,x1,y1=_bb(m); A=m.m[y0:y1,x0:x1].astype(np.float32)/255
    pat=(((xx[y0:y1,x0:x1]+dirn*yy[y0:y1,x0:x1])%step)<1.3).astype(np.float32)
    Bf=buf[y0:y1,x0:x1]; Bf+=(np.array(col,np.float32)-Bf)*(A*pat*a)[...,None]
def wash(buf,x,y,r,col,a=1.0):
    """soft marker wash (multiplicative-ish, works on light paper)"""
    R=int(r*2.5)+1; x0,y0=max(0,int(x)-R),max(0,int(y)-R); x1,y1=min(w,int(x)+R),min(h,int(y)+R)
    if x1<=x0 or y1<=y0 or a<=0: return
    d2=((xx[y0:y1,x0:x1]-x)**2+(yy[y0:y1,x0:x1]-y)**2)/(r*r); k=(np.exp(-d2)*a)[...,None]
    Bf=buf[y0:y1,x0:x1]; Bf+=(np.array(col,np.float32)-Bf)*k
def part(pts,u):
    p=np.asarray(pts,np.float64)
    if u>=1: return p
    if u<=0 or len(p)<2: return p[:1]
    sl=np.hypot(*np.diff(p,axis=0).T); cs=np.concatenate([[0],np.cumsum(sl)]); L=cs[-1]*u
    k=np.searchsorted(cs,L)-1; k=min(max(k,0),len(sl)-1); f=(L-cs[k])/max(sl[k],1e-9)
    return np.vstack([p[:k+1],p[k]+(p[k+1]-p[k])*f])
def dl(m,pts,u=1.0,th=1.4):
    q=part(pts,u)
    if len(q)>=2: m.pline(q,th)
    return m
def circ_pts(cx,cy,rx,ry=None,a0=0,a1=2*math.pi,n=72):
    ry=rx if ry is None else ry
    return [(cx+rx*math.cos(a0+(a1-a0)*i/n),cy+ry*math.sin(a0+(a1-a0)*i/n)) for i in range(n+1)]
def dashl(m,p0,p1,seg=6,gap=5,th=1.0):
    L=math.hypot(p1[0]-p0[0],p1[1]-p0[1]); n=int(L/(seg+gap))+1
    for k in range(n):
        a=k*(seg+gap)/L; b=min(1,(k*(seg+gap)+seg)/L)
        if a<1: m.line((p0[0]+(p1[0]-p0[0])*a,p0[1]+(p1[1]-p0[1])*a),(p0[0]+(p1[0]-p0[0])*b,p0[1]+(p1[1]-p0[1])*b),th)
    return m
def dim(m,p0,p1,th=1.2,u=1.0):
    p1=(p0[0]+(p1[0]-p0[0])*u,p0[1]+(p1[1]-p0[1])*u)
    m.line(p0,p1,th); dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)+1e-6; ux,uy=dx/L,dy/L; px,py=-uy,ux
    for (x,y),s in ((p0,1),(p1,-1)):
        m.line((x,y),(x+s*ux*9+px*4,y+s*uy*9+py*4),th); m.line((x,y),(x+s*ux*9-px*4,y+s*uy*9-py*4),th)
        m.line((x-px*7,y-py*7),(x+px*7,y+py*7),th)
    return m
def penhead(buf,x,y,a=1.0):
    ink(buf,M().circ(x,y,3.2),a,col=RED); ink(buf,M().line((x,y),(x+10,y-16),2.2),0.8*a)
def waves(buf,t,src,box,a=1.0,n=5,spd=95,gap=70,col=INK,th=1.3):
    """incoming radio wavefronts from src, clipped to box"""
    if a<=0: return
    x0,y0,x1,y1=box; m=M()
    for k in range(n):
        r=((t*spd+k*gap)%(n*gap))+40
        pts=[p for p in circ_pts(src[0],src[1],r,n=160) if x0<p[0]<x1 and y0<p[1]<y1]
        if len(pts)>2:
            fade=min(1,(r-40)/60)*(1-max(0,(r-(n*gap-60))/60))
            if fade>0.05: mm=M().pline(pts,th); ink(buf,mm,a*fade*0.75,col)
# ---- Big Ear (Kraus-type) drawing ----
def bigear(buf,cx,cy,s=1.0,u=1.0,a=1.0,fall=0.0):
    if a<=0: return
    def T(pts,dx=0,dy=0,rt=0.0,piv=(0,0)):
        out=[]
        for x,y in pts:
            x-=piv[0]; y-=piv[1]; c,sn=math.cos(rt),math.sin(rt); x,y=x*c-y*sn+piv[0],x*sn+y*c+piv[1]
            out.append((cx+(x+dx)*s,cy+(y+dy)*s))
        return out
    g=[(-210,30),(140,-35),(230,5),(-120,75),(-210,30)]
    gm=M(); dl(gm,T(g),u,1.6)
    hm=M()
    for k in range(1,9):
        f=k/9; p0=(-210+(-120+210)*f,30+(75-30)*f); p1=(140+(230-140)*f,-35+(5+35)*f)
        dl(hm,T([p0,p1]),max(0,u*1.4-0.4-0.05*k),1.0)
    ink(buf,gm,a); ink(buf,hm,0.35*a)
    # flat tiltable reflector (left)
    fd=fall; fl=[(-210,30),(-120,75),(-150,-40),(-240,-85),(-210,30)]
    fm=M(); dl(fm,T(fl,dy=180*fd**2,rt=-0.9*fd,piv=(-165,52)),cl(u*1.6-0.2),1.6)
    for k in range(1,6):
        f=k/6; dl(fm,T([(-210+90*f,30+45*f),(-240+90*f,-85+45*f)],dy=180*fd**2,rt=-0.9*fd,piv=(-165,52)),cl(u*1.6-0.4),1.0)
    outl(buf,M().poly(T(fl[:-1],dy=180*fd**2,rt=-0.9*fd,piv=(-165,52))),a=0,fill=0) if False else None
    ink(buf,fm,a*(1-0.6*fd))
    # paraboloid wall (right)
    fd2=cl(fall*1.3-0.2)
    top=[(150+90*q,-140+40*q-25*math.sin(math.pi*q)) for q in np.linspace(0,1,24)]
    bot=[(140+90*q,-35+40*q) for q in np.linspace(0,1,24)]
    pm=M(); kw=dict(dy=200*fd2**2,rt=0.7*fd2,piv=(185,-15))
    dl(pm,T(top,**kw),cl(u*1.6-0.3),1.6); dl(pm,T([bot[0],top[0]],**kw),cl(u*1.6-0.3),1.4); dl(pm,T([bot[-1],top[-1]],**kw),cl(u*1.6-0.3),1.4)
    for k in range(1,8):
        j=k*3; dl(pm,T([bot[j],top[j]],**kw),cl(u*1.6-0.5),0.9)
    for f in (0.33,0.66):
        dl(pm,T([(b[0]+(tp[0]-b[0])*f,b[1]+(tp[1]-b[1])*f) for b,tp in zip(bot,top)],**kw),cl(u*1.6-0.6),0.9)
    ink(buf,pm,a*(1-0.6*fd2))
    # feed horn hut
    hm2=M(); dl(hm2,T([(-70,40),(-40,26),(-40,8),(-70,22),(-70,40)]),cl(u*1.6-0.7),1.4); ink(buf,hm2,a)
# ---- printout (dot-matrix characters on the green bars) ----
PR_COLS,PR_ROWS=16,14; PR_X0,PR_Y0,PR_CW,PR_RH=156,640,48,48; WCOL=6; WROW=4
_gp=np.random.default_rng(1977)
PRT=[["" for _ in range(PR_COLS)] for _ in range(PR_ROWS)]
for r_ in range(PR_ROWS):
    for c_ in range(PR_COLS):
        v=_gp.choice([" "," "," ","1","1","1","2","2","3"],p=None); PRT[r_][c_]=v
for k,ch in enumerate("6EQUJ5"): PRT[WROW+k][WCOL]=ch
for k in (WROW-1,WROW+6): PRT[k][WCOL]="1"
_PC={}
def printout_img(nrows):
    if nrows in _PC: return _PC[nrows]
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im); f=F("Silkscreen-Regular",34)
    for r_ in range(nrows):
        for c_ in range(PR_COLS):
            ch=PRT[r_][c_]
            if ch.strip(): d.text((PR_X0+c_*PR_CW+PR_CW/2,PR_Y0+r_*PR_RH+PR_RH/2),ch,font=f,fill=cI+(225,),anchor="mm")
    _PC[nrows]=im; return im
def printout(d,nrows,a=1.0,hi=None):
    if a<=0.01 or nrows<=0: return
    im=printout_img(min(nrows,PR_ROWS))
    if a<0.99: ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); im=Image.fromarray(ar)
    d._image.alpha_composite(im)
    if hi:
        f=F("Silkscreen-Regular",34)
        for k,(ch,al) in enumerate(hi):
            if al>0.01: d.text((PR_X0+WCOL*PR_CW+PR_CW/2,PR_Y0+(WROW+k)*PR_RH+PR_RH/2),ch,font=f,fill=cR+(int(255*al*a),),anchor="mm",stroke_width=1,stroke_fill=cR+(int(255*al*a),))
WCX=PR_X0+WCOL*PR_CW+PR_CW/2; WCY=PR_Y0+(WROW+2.5)*PR_RH
def redring(d,u,a=1.0):
    if u<=0 or a<=0.01: return
    bb=(WCX-46,WCY-170,WCX+46,WCY+170); a0=-100
    d.arc(bb,a0,a0+360*min(u,1)*1.04,fill=cR+(int(235*a),),width=7)
def wow(d,rv,a=1.0): pen(d,"Wow!",WCX-175,WCY-10,88,a=a,ang=8,rv=rv)
# ---- objects ----
def earth(buf,cx,cy,R,a=1.0,u=1.0):
    if a<=0: return
    m=dl(M(),circ_pts(cx,cy,R,n=90),u,1.8); ink(buf,m,a)
    mm=M()
    for k in (-0.55,0,0.55): mm.pline(circ_pts(cx,cy+R*k*0.0,R*math.sqrt(1-k*k) if False else R,R*0.0+abs(R*k) if k else 1,0,math.pi*2,50),1) if False else None
    for k in (-0.5,0.0,0.5):
        yk=cy+R*k; hw=math.sqrt(max(R*R-(R*k)**2,0)); mm.line((cx-hw,yk),(cx+hw,yk),1)
    for k in (-0.5,0.5): mm.pline(circ_pts(cx,cy,R*abs(k),R,0,2*math.pi,50),1)
    ink(buf,mm,0.45*a*u)
_gc=np.random.default_rng(24)
CLD=[]
while len(CLD)<520:
    x,y=_gc.normal(0,1),_gc.normal(0,1)
    rr=math.hypot(x*0.85,y*1.15)
    if rr<2.1: CLD.append((x*62,y*44,_gc.uniform(0.9,2.1),_gc.random()))
def cloud(buf,cx,cy,rv=1.0,a=1.0,lit=0.0,t=0.0):
    if a<=0: return
    mi,mr=M(),M()
    for x,y,r,o in CLD:
        if o>rv: continue
        X,Y=cx+x*1.8,cy+y*1.8
        (mr if lit>0 and o<lit*1.05 else mi).circ(X,Y,r*(1+0.35*lit))
    ink(buf,mi,a); ink(buf,mr,a,col=RED)
def magnetar(buf,cx,cy,t,a=1.0,flare=0.0):
    if a<=0: return
    ink(buf,M().circ(cx,cy,9),a)
    m=M()
    for k,(rx,ry) in enumerate(((26,14),(44,24),(64,36))):
        m.pline(circ_pts(cx+rx,cy,rx,ry,0,2*math.pi,60),1.1); m.pline(circ_pts(cx-rx,cy,rx,ry,0,2*math.pi,60),1.1)
    ink(buf,m,0.55*a)
    if flare>0:
        rm=M()
        for k in range(16):
            an=k*math.pi/8+0.2; L=(30+60*flare)*(0.7+0.3*math.sin(t*23+k*1.7))
            rm.line((cx+math.cos(an)*14,cy+math.sin(an)*14),(cx+math.cos(an)*(14+L),cy+math.sin(an)*(14+L)),1.6)
        ink(buf,rm,a*flare,col=RED); wash(buf,cx,cy,60*flare+10,YEL,0.55*flare*a)
def flag(buf,x,y,u,a=1.0,t=0.0):
    if a<=0 or u<=0: return
    hill=M(); dl(hill,[(x-170+k*10,y+30-26*math.sin(math.pi*k/34)) for k in range(35)],cl(u*2),1.6); ink(buf,hill,a)
    ink(buf,M().ell(x,y+8,16,5),a*cl(u*2-0.4))
    H_=110*eout(cl(u*1.6-0.3)); ink(buf,M().line((x,y+6),(x,y+6-H_),2.2),a)
    if H_>60:
        wv=math.sin(t*6)*5; fl=M().poly([(x,y+6-H_),(x+52,y+6-H_+16+wv),(x,y+6-H_+32)]); comp(buf,fl,RED,sh=0,rim=0,a=a)
# ================= scenes =================
CH="6EQUJ5"; CHV=[6,14,26,30,19,5]
def s_hook(t,sc):
    buf=PAPER.copy(); hud=[]
    tt=max(t,-1.0)
    waves(buf,tt,(470,-40),(32,40,508,292),a=1.0,n=5,spd=110,gap=64,th=1.8)
    bx0,by0,bx1,by1=60,300,480,560
    fr=M().rect(bx0,by0,bx1,by0+2).rect(bx0,by1-2,bx1,by1).rect(bx0,by0,bx0+2,by1).rect(bx1-2,by0,bx1,by1); ink(buf,fr,0.9)
    gm=M()
    for k in range(1,6): dashl(gm,(bx0+k*70,by0+4),(bx0+k*70,by1-4),4,6,1)
    for k in range(1,4): dashl(gm,(bx0+4,by0+k*65),(bx1-4,by0+k*65),4,6,1)
    ink(buf,gm,0.25)
    hf=cl((tt+1.0)/3.3)
    g=np.random.default_rng(3); nz=np.cumsum(g.normal(0,1,200)); nz=(nz-np.convolve(nz,np.ones(15)/15,'same'))
    us=np.linspace(0,1,200); amp=210*np.exp(-((us-0.48)/0.085)**2)
    ys=by1-22-amp-nz*2.2; xs=bx0+6+(bx1-bx0-12)*us
    pts=list(zip(xs,ys)); m=dl(M(),pts,hf,2.0); ink(buf,m,1.0)
    if hf<1:
        q=part(pts,hf)[-1]; penhead(buf,q[0],q[1])
    # duration bracket
    du=sm((t-EV["s72"]+0.15)/0.5)
    if du>0:
        x0_,x1_=bx0+6+(bx1-bx0-12)*0.31,bx0+6+(bx1-bx0-12)*0.65
        ink(buf,dim(M(),(x0_,585),(x1_,585),u=du),0.9,col=RED)
    gone=sm((t-EV["vanished"]+0.1)/0.3)
    if gone>0: wash(buf,410,500,60,YEL,0.0)
    def hd(d,t=t,du=du,gone=gone):
        k0=1.0 if t<0.4 else ap(t,-1,EV["who"]+0.2)
        big(d,"72 SECONDS",540,250,170,a=k0,sc=1.0 if t<0.2 else 1+0.06*math.exp(-(t-EV["s72"])*4)*(t>EV["s72"]))
        pen(d,"from deep space",800,470,50,a=ap(t,EV["deep"],EV["vanished"]),ang=-6,rv=cl((t-EV["deep"]+0.1)/0.5))
        typ(d,"0 s",140,1170,34,a=1.0); typ(d,"72 s",540,1210,40,a=du*(1-gone*0.0)) if du>0 else None
        stamp(d,"GONE.",790,760,110,a=sm((t-EV["vanished"]+0.05)/0.15),ang=-12,sc=slam(t,EV["vanished"]))
        rtag(d,"WHO SENT IT?",540,250,96,a=ap(t,EV["who"],sc["e"]+1),sc=pop(t,EV["who"]-0.1),ang=-2)
    hud.append(hd); return buf,hud
def s_print(t,sc):
    buf=PAPER.copy(); hud=[]
    aBE=1-sm((t-EV["ehman"]+0.35)/0.45)
    if aBE>0:
        waves(buf,t,(120,-60),(32,40,508,360),a=aBE,n=5,spd=90,gap=70,th=1.6)
        u=sm((t-sc["s"]+0.25)/1.6); bigear(buf,270,470,1.05,u=u,a=aBE)
        sw=sm((t-EV["scanning"]+0.2)/0.4)
        if sw>0:
            an=-math.pi/2+0.45*math.sin((t-EV["scanning"])*2.2); x0_,y0_=200,470
            bm=M(); bm.line((x0_,y0_),(x0_+math.cos(an-0.06)*330,y0_+math.sin(an-0.06)*330),1.3); bm.line((x0_,y0_),(x0_+math.cos(an+0.06)*330,y0_+math.sin(an+0.06)*330),1.3)
            ink(buf,bm,0.7*sw*aBE,col=RED)
    pP=sm((t-EV["ehman"]+0.3)/0.4)
    nrows=int(cl((t-EV["ehman"]+0.2)/1.4)*PR_ROWS)
    if pP>0:
        hl=sm((t-EV["finds"]+0.1)/0.4)
        if hl>0:
            hm=M().rect((WCX-26)/2,(PR_Y0+WROW*PR_RH-4)/2,(WCX-26)/2+hl*26,(PR_Y0+(WROW+6)*PR_RH+4)/2); comp(buf,hm,YEL,sh=0,rim=0,a=0.75*pP)
        if nrows<PR_ROWS:  # printer head
            y_=(PR_Y0+nrows*PR_RH+20)/2; hdm=M().rect(60,y_-8,480,y_+8); outl(buf,hdm,a=0.9*pP,th=1,fill=0.25)
            hx=60+((t*9)%1)*400; ink(buf,M().rect(hx,y_-12,hx+30,y_+12),0.9*pP)
    # bars
    bu=sm((t-EV["umeans"]+0.3)/0.4)
    if bu>0:
        base=310
        for k,v in enumerate(CHV):
            gk=eout(cl((t-EV["umeans"]-k*0.07)/0.5)); x=95+k*70; hgt=v/30*120*gk
            bm=M().rect(x-20,base-hgt,x+20,base)
            if k==3: comp(buf,bm,RED,sh=0,rim=0,a=0.9*bu)
            else: hatch(buf,bm,0.8*bu,step=5); outl(buf,bm,a=bu,th=1,fill=0.0)
        ink(buf,M().rect(60,base,480,base+2),bu)
        nz=sm((t-EV["noise"]+0.2)/0.4)
        if nz>0: ink(buf,dashl(M(),(60,base-4),(480,base-4),5,5,1.3),nz,col=RED)
    def hd(d,t=t,aBE=aBE,pP=pP,nrows=nrows,bu=bu):
        tag_a=ap(t,EV["aug"],EV["ehman"])
        typ(d,"AUG 15, 1977",540,240,64,a=tag_a,sc=pop(t,EV["aug"]-0.1))
        big(d,"BIG EAR",540,1180,120,a=ap(t,EV["bigear"],EV["ehman"]),sc=pop(t,EV["bigear"]-0.1))
        typ(d,"OHIO STATE UNIV.",540,1300,40,a=ap(t,EV["ohio"],EV["ehman"]))
        pen(d,"scanning the sky…",760,400,52,a=ap(t,EV["scanning"],EV["ehman"]),rv=cl((t-EV["scanning"]+0.1)/0.6))
        typ(d,"JERRY EHMAN · ASTRONOMER",540,240,46,a=ap(t,EV["ehman"],EV["c0"]),sc=pop(t,EV["ehman"]-0.1))
        pen(d,"the printout",540,370,64,a=ap(t,EV["printout"],EV["c0"]),ang=-3,rv=cl((t-EV["printout"]+0.1)/0.5))
        hi=[(ch,sm((t-EV[f"c{k}"]+0.05)/0.15)*(1-sm((t-EV["umeans"])/0.4))) for k,ch in enumerate(CH)]
        printout(d,nrows,a=pP*(1-0.35*bu*(1-sm((t-EV["circles"]+0.2)/0.4))),hi=hi)
        for k,ch in enumerate(CH):
            e=EV[f"c{k}"]; dot(d,ch,190+k*140,250,130,a=sm((t-e+0.05)/0.12),sc=pop(t,e-0.05),col=cR if (k==3 and t>EV["thirty"]-0.1) else cI)
        if bu>0:
            for k,v in enumerate(CHV):
                typ(d,str(v),190+k*140,620+8,30,a=bu*cl((t-EV["umeans"]-k*0.07)/0.4),pad=(10,4)) if False else None
            stamp(d,"30×",870,420,80,a=sm((t-EV["thirty"]+0.05)/0.15),ang=-8,sc=slam(t,EV["thirty"]))
            pen(d,"noise",120,560,44,a=sm((t-EV["noise"])/0.3),ang=0)
        redring(d,cl((t-EV["circles"]+0.1)/0.9),a=1.0)
        wow(d,cl((t-EV["oneword"]+0.1)/(EV["wow"]-EV["oneword"]+0.4)))
    hud.append(hd); return buf,hud
TEA=[(-95,35),(-35,40),(-10,0),(-55,-30),(-100,-10),(-150,15),(-35,-60),(15,-35),(55,-10),(40,30)]
TEA_L=[(5,0),(0,1),(1,2),(2,3),(3,4),(4,0),(4,5),(3,6),(6,2),(2,7),(7,8),(8,9),(9,1)]
def s_search(t,sc):
    buf=PAPER.copy(); hud=[]
    pB=sm((t-EV["went"]+0.35)/0.45); aA=1-pB
    if aA>0:
        x0_,x1_,yb,yt=70,470,540,250; u=sm((t-sc["s"]+0.3)/1.4)
        ink(buf,dl(M(),[(x0_,yt),(x0_,yb),(x1_,yb)],u,1.6),aA)
        tk=M()
        for k in range(5): tk.line((x0_+k*100,yb),(x0_+k*100,yb+8),1.3)
        ink(buf,tk,aA*u)
        bandu=sm((t-EV["freq"]+0.2)/0.4)
        if bandu>0:
            bm=M().rect(240,yt,300,yb-2); hatch(buf,bm,0.55*bandu*aA,step=6,col=RED); outl(buf,bm,a=bandu*aA,th=1,fill=0,col=RED)
        g=np.random.default_rng(9); us=np.linspace(0,1,240); nz=g.normal(0,1,240)
        sp=sm((t-EV["hline"]+0.2)/0.35); amp=230*np.exp(-((us-0.5)/0.012)**2)*sp
        ys=yb-26-np.abs(nz)*7-amp; xs=x0_+6+(x1_-x0_-12)*us
        pts=list(zip(xs,ys)); ink(buf,dl(M(),pts,u,1.6),aA)
        if u<1: q=part(pts,u)[-1]; penhead(buf,q[0],q[1],aA)
    if pB>0:
        cx,cy=300,400; u=sm((t-EV["went"]+0.1)/0.8)
        gm=M()
        for k in range(-3,4): dashl(gm,(40,cy+k*60),(500,cy+k*60-30),3,6,1)
        for k in range(-4,4): dashl(gm,(cx+k*60,150),(cx+k*60+20,650),3,6,1)
        ink(buf,gm,0.3*pB)
        lm=M()
        for i,(a_,b_) in enumerate(TEA_L): dl(lm,[(cx+TEA[a_][0]*1.6,cy+TEA[a_][1]*1.6),(cx+TEA[b_][0]*1.6,cy+TEA[b_][1]*1.6)],cl(u*len(TEA_L)-i),1.3)
        ink(buf,lm,0.8*pB); sm_=M()
        for k,(x,y) in enumerate(TEA): sm_.circ(cx+x*1.6,cy+y*1.6,3.5+1.5*(k%3==0))
        ink(buf,sm_,pB)
        tx,ty=150,250
        n=int(cl((t-EV["went"]+0.1)/(EV["nothing"]-EV["went"]-0.1))*30)
        sc_=M(); g=np.random.default_rng(4)
        for k in range(n):
            ox,oy=g.normal(0,7),g.normal(0,5); sc_.pline(circ_pts(tx+ox,ty+oy,30+g.uniform(-4,6),20+g.uniform(-3,4),n=40),1)
        ink(buf,sc_,0.45*pB)
        ch=M().line((tx-48,ty),(tx-14,ty),1.6).line((tx+14,ty),(tx+48,ty),1.6).line((tx,ty-48),(tx,ty-14),1.6).line((tx,ty+14),(tx,ty+48),1.6)
        ink(buf,ch,pB,col=RED)
    def hd(d,t=t,aA=aA,pB=pB):
        typ(d,"1420 MHz",540,240,72,a=ap(t,EV["hline"],EV["went"]),sc=pop(t,EV["hline"]-0.1))
        pen(d,"hydrogen line",790,390,56,a=ap(t,EV["hline"]+0.2,EV["went"]),ang=-5,rv=cl((t-EV["hline"])/0.6))
        rtag(d,"PROTECTED BAND",540,1190,60,a=ap(t,EV["freq"],EV["notx"]+0.1),sc=pop(t,EV["freq"]-0.1))
        stamp(d,"NO EARTH TRANSMITTERS",540,1210,70,a=ap(t,EV["notx"],EV["went"])*sm((t-EV["notx"]+0.05)/0.15),ang=-5,sc=slam(t,EV["notx"]))
        for k,s_ in enumerate(("1380","1420","1460")):
            typ(d,s_,140+k*400,1130,30,a=aA*sm((t-sc["s"]-0.4)/0.4),pad=(8,3)) if False else None
        pen(d,"Sagittarius",760,1000,54,a=pB*sm((t-EV["went"]-0.3)/0.4),ang=-4)
        n=int(cl((t-EV["went"]+0.1)/(EV["nothing"]-EV["went"]-0.1))*30)
        typ(d,f"SEARCH #{max(1,n)}",540,240,66,a=ap(t,EV["went"]+0.1,sc["e"]+1))
        stamp(d,"NOTHING.",540,1150,130,a=sm((t-EV["nothing"]+0.05)/0.15),ang=-9,sc=slam(t,EV["nothing"]))
    hud.append(hd); return buf,hud
def s_answer(t,sc):
    buf=PAPER.copy(); hud=[]
    pBE=sm((t-EV["bigear2"]+0.35)/0.45); pS=sm((t-EV["sheet"]+0.35)/0.45)
    aC=1-pBE; aE=pBE*(1-pS); aS=pS
    lit=sm((t-EV["litup"]+0.1)/0.6); fl=sm((t-EV["flaring"]+0.1)/0.3)
    if aC>0:
        hyp=sm((t-EV["hypo"]+0.1)/0.3); dimk=1-0.55*hyp
        cloud(buf,250,380,rv=sm((t-EV["y2024"]+0.3)/2.4),a=aC*dimk,lit=lit*(0.6+0.4*fl))
        magnetar(buf,330,330,t,a=aC*dimk*sm((t-EV["litup"]+0.2)/0.4),flare=fl*(0.7+0.3*math.sin(t*9))*(1-sm((t-EV["moment"]-0.2)/0.5)))
        lz=sm((t-EV["laser"]+0.2)/0.35); off=sm((t-EV["moment"]-0.3)/0.4)
        if lz>0:
            ex,ey=440,600; earth(buf,ex,ey,48,a=aC*dimk*lz)
            p0=(270,410); m=M()
            for o in (-4,4): dl(m,[(p0[0]+o,p0[1]-o*0.5),(ex+o-20,ey-o*0.5-40)],lz,1.8)
            ink(buf,m,aC*dimk*(1-off),col=RED)
            if lz>=1: wash(buf,ex,ey,50,YEL,0.6*aC*(1-off)*(0.6+0.4*math.sin(t*20)))
        if t<EV["cloud"]+0.2:
            sc_=sm((t-EV["y2024"]+0.2)/0.6); wash(buf,270,380,140*sc_+1,(0.9,0.95,0.9),0.0)
    if aE>0:
        fall=sm((t-EV["torn"]+0.1)/0.9)
        bigear(buf,270,400,1.0,u=1.0,a=aE*(1-0.8*sm((t-EV["golf"])/0.5)),fall=fall)
        flag(buf,300,560,cl((t-EV["golf"]+0.2)/0.7),a=aE,t=t)
    if aS>0:
        wash(buf,270,370,170,(0.99,0.99,0.97),0.0)
    def hd(d,t=t,aC=aC,aE=aE,aS=aS):
        typ(d,"2024",540,240,80,a=ap(t,EV["y2024"],EV["laser"])*aC,sc=pop(t,EV["y2024"]-0.1))
        pen(d,"a new idea:",540,370,56,a=ap(t,EV["cause"],EV["cloud"]),rv=cl((t-EV["cause"])/0.5))
        typ(d,"HYDROGEN CLOUD",540,1180,58,a=ap(t,EV["cloud"],EV["flaring"]),sc=pop(t,EV["cloud"]-0.1))
        rtag(d,"MAGNETAR FLARE",540,1180,72,a=ap(t,EV["flaring"],EV["laser"]),sc=pop(t,EV["flaring"]-0.1))
        pen(d,"dead star",890,470,50,a=ap(t,EV["dead"],EV["laser"]),ang=-6)
        rtag(d,"NATURAL SPACE LASER",540,240,70,a=ap(t,EV["laser"],EV["hypo"]),sc=pop(t,EV["laser"]-0.1))
        pen(d,"(a maser)",540,370,50,a=ap(t,EV["laser"]+0.4,EV["hypo"]))
        typ(d,"→ EARTH",600,1170,50,a=ap(t,EV["aimed"],EV["hypo"]),sc=pop(t,EV["aimed"]-0.1))
        stamp(d,"HYPOTHESIS",540,820,120,a=ap(t,EV["hypo"],EV["bigear2"]+0.2)*sm((t-EV["hypo"]+0.05)/0.15),ang=-10,sc=slam(t,EV["hypo"]))
        big(d,"BIG EAR",540,240,120,a=aE*ap(t,EV["bigear2"],EV["torn"]),sc=pop(t,EV["bigear2"]-0.1))
        rtag(d,"TORN DOWN · 1998",540,240,72,a=aE*ap(t,EV["torn"],sc["e"]+1),sc=pop(t,EV["torn"]-0.1))
        typ(d,"→ GOLF COURSE",540,1200,60,a=aE*ap(t,EV["golf"],sc["e"]+1),sc=pop(t,EV["golf"]-0.1))
        if aS>0:
            printout(d,PR_ROWS,a=aS); redring(d,1.0,a=aS); wow(d,1.0,a=aS)
            typ(d,"ONE SHEET OF PAPER",540,240,62,a=aS*ap(t,EV["sheet"],EV["once"]),sc=pop(t,EV["sheet"]-0.1))
            big(d,"1977",540,330,150,a=aS*sm((t-EV["once"]+0.1)/0.3),sc=pop(t,EV["once"]-0.1),col=cR)
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,print=s_print,search=s_search,answer=s_answer)
BAND=(1-0.42*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.18*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.008,(h,w,1)).astype(np.float32) for i in range(6)]
TR=0.27
TOTAL=B.TOTAL; LOOPD=0.45
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
def _hud(hs):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hs: f(d)
    return ov
def _perf(buf,y):
    """tractor-feed perforation between two pages"""
    if -4<y<h+4:
        m=M()
        for x in range(34,w-30,9): m.line((x,y),(x+4,y),1.2)
        ink(buf,m,0.6); y0=max(0,int(y)); y1=min(h,int(y)+5); buf[y0:y1]*=0.94
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(sc,SC[i+1],nb,t,t)
    elif t<pb+TR: pair=(SC[i-1],sc,pb,t,t)
    elif t>TOTAL-LOOPD: pair=(sc,SC[0],TOTAL-LOOPD/2,t,t-TOTAL)   # loop: feed back into the opening frame
    if pair is None:
        buf,hud=render_scene(t,sc); ov=_hud(hud)
    else:
        A_,B2,bnd,ta,tb=pair
        if A_ is sc and B2 is SC[0]: u=cl((t-(TOTAL-LOOPD))/LOOPD)
        else: u=cl((t-(bnd-TR))/(2*TR))
        k=0.5*(1-math.cos(math.pi*u)); off=int(round(k*h))
        b1,h1=render_scene(ta,A_); b2,h2=render_scene(tb,B2)
        buf=np.empty_like(b1)
        if off<h: buf[:h-off]=b1[off:]
        if off>0: buf[h-off:]=b2[:off]
        _perf(buf,h-off)
        o1=_hud(h1); o2=_hud(h2); ov=Image.new("RGBA",(W,H),(0,0,0,0))
        ov.alpha_composite(o1,(0,0),(0,2*off)) if 2*off<H else None
        if off>0: ov.alpha_composite(o2,(0,H-2*off),(0,0,W,2*off))
    buf=np.clip(buf,0,1.2)*PT*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
