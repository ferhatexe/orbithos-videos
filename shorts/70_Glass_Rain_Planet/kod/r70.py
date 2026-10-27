import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid70"); sys.path.insert(0,"/home/claude/toolkit")
from pro import *
from PIL import Image, ImageDraw
T,LINES,SC,TOTAL=load("timeline.json")
CAP=Captions(LINES); WD=CAP.W
def wt(li,sub,o=0.0): return word_t(WD,li,sub,o)
def Ls(i): return LINES[i]["s"]
# ================= cinematic CG space: cobalt hot-Jupiter, K-dwarf star, glass rain =================
# ---------- textures ----------
TH,TW=512,1024
_lat=np.linspace(-1,1,TH,dtype=np.float32)[:,None]*np.ones((1,TW),np.float32)
_war=fbm((TH,TW),11,5,3,aspect=2)*0.035+fbm((TH,TW),12,4,10,aspect=2)*0.012
_band=np.sin((_lat*1.0+_war)*np.pi*8.5)*0.5+0.5
_str=cv2.resize(np.random.default_rng(13).normal(0,1,(TH//2,TW//32)).astype(np.float32),(TW,TH),interpolation=cv2.INTER_CUBIC)
_str=cv2.GaussianBlur(_str,(0,0),1.2); _str=(_str-_str.mean())/_str.std()
_fine=fbm((TH,TW),13,6,16,aspect=2)
_storm=np.exp(-(((np.arange(TW)[None,:]-TW*0.3)/40.0)**2+((np.arange(TH)[:,None]-TH*0.62)/18.0)**2)).astype(np.float32)
v=np.clip(_band*0.55+_str*0.13+_fine*0.05+0.15+_storm*0.35,0,1)[...,None]
_aw=((np.cos(np.arange(TW)*2*np.pi/TW)+1)/2)[None,:].astype(np.float32); _aw=_aw*_aw*(3-2*_aw)
v=v*(1-_aw[...,None])+np.roll(v,TW//2,1)*_aw[...,None]
C0=np.array([0.02,0.07,0.32],np.float32); C1=np.array([0.10,0.32,0.85],np.float32); C2=np.array([0.62,0.80,1.0],np.float32)
TEX=np.where(v<0.55,C0+(C1-C0)*(v/0.55),C1+(C2-C1)*((v-0.55)/0.45)).astype(np.float32)
TEX=np.concatenate([TEX,TEX[:,:8]],1)  # wrap pad
STARS=starfield(7,1500,neb=((0.05,0.025,0.11),(0.03,0.06,0.15)))
STARS2=starfield(9,900)
def planet(buf,cx,cy,R,spin,L=(-0.75,-0.35,0.55),heat=0.0,tilt=-0.18,atm=1.0,dark=1.0):
    x0,x1=max(0,int(cx-R*1.15)),min(w,int(cx+R*1.15)+1); y0,y1=max(0,int(cy-R*1.15)),min(h,int(cy+R*1.15)+1)
    if x0>=x1 or y0>=y1: return
    X=(xx[y0:y1,x0:x1]-cx)/R; Y=(yy[y0:y1,x0:x1]-cy)/R; r2=X*X+Y*Y; r=np.sqrt(r2)
    ins=r2<1; Z=np.sqrt(np.clip(1-r2,0,1))
    c,s=math.cos(tilt),math.sin(tilt); Xr=X*c-Y*s; Yr=X*s+Y*c
    lat=np.arcsin(np.clip(Yr,-1,1)); lon=np.arctan2(Xr,Z)+spin
    u=((lon/(2*np.pi))%1.0)*TW; vv=(lat/np.pi+0.5)*(TH-1)
    col=cv2.remap(TEX,u.astype(np.float32),vv.astype(np.float32),cv2.INTER_LINEAR)
    Lv=np.array(L,np.float32); Lv/=np.linalg.norm(Lv)
    nd=X*Lv[0]+Y*Lv[1]+Z*Lv[2]
    dif=np.clip(nd,0,1)**0.9; term=sm_np((nd+0.08)/0.35)
    limb=0.55+0.45*Z**0.6
    lit=col*(dif*term*limb)[...,None]*1.6
    night=col*0.02*dark
    hm=sm_np((nd-(1-2.3*heat))/0.3) if heat>0 else np.zeros_like(nd)
    hot=hm*(0.45+0.55*np.clip(_fine_s(u,vv)*1.4,0,1))
    lit=lit*(1-hm)[...,None]+night+hot[...,None]*np.array([1.5,0.30,0.04],np.float32)
    # atmosphere: in-disk fresnel + outer halo
    fr=(1-Z)**3*np.clip(nd+0.35,0,1)[...]*atm
    lit=lit+fr[...,None]*np.array([0.35,0.6,1.3],np.float32)
    out=np.clip(r-1,0,None); halo=np.exp(-out*28)*(r>=1)*np.clip(X*Lv[0]+Y*Lv[1]+0.55,0,1)*0.85*atm
    reg=buf[y0:y1,x0:x1]
    reg[:]=np.where(ins[...,None],lit,reg)+halo[...,None]*np.array([0.25,0.5,1.2],np.float32)
_FS0=cv2.resize(fbm((TH//2,TW//2),15,4,4,aspect=2),(TW,TH)); _FS=np.concatenate([_FS0*(1-_aw)+np.roll(_FS0,TW//2,1)*_aw]*1,1); _FS=np.concatenate([_FS,_FS[:,:8]],1)
def _fine_s(u,vv): return cv2.remap(_FS,u.astype(np.float32),vv.astype(np.float32),cv2.INTER_LINEAR)*0.5+0.5
def sm_np(x): x=np.clip(x,0,1); return x*x*(3-2*x)
GRAN=fbm((256,256),21,5,8)
def star(buf,cx,cy,R,t,a=1.0,streak=1.0):
    x0,x1=max(0,int(cx-R*1.05)),min(w,int(cx+R*1.05)+1); y0,y1=max(0,int(cy-R*1.05)),min(h,int(cy+R*1.05)+1)
    if x0<x1 and y0<y1:
        X=(xx[y0:y1,x0:x1]-cx)/R; Y=(yy[y0:y1,x0:x1]-cy)/R; r2=X*X+Y*Y; ins=r2<1; Z=np.sqrt(np.clip(1-r2,0,1))
        g=cv2.resize(GRAN,(x1-x0,y1-y0))
        ld=0.30+0.70*Z**0.6; col=np.array([2.0,0.85,0.25],np.float32)*(ld*(1+0.22*g))[...,None]
        buf[y0:y1,x0:x1]=np.where(ins[...,None],col*a+buf[y0:y1,x0:x1]*(1-a),buf[y0:y1,x0:x1])
    glow(buf,cx,cy,R*1.25,(0.9,0.42,0.12),0.9*a); glow(buf,cx,cy,R*2.6,(0.45,0.18,0.05),0.5*a)
    if streak>0:
        y0_,y1_=max(0,int(cy-6)),min(h,int(cy+7))
        if y0_<y1_:
            sx=np.exp(-np.abs(xx[y0_:y1_]-cx)/(w*0.45))*np.exp(-((yy[y0_:y1_]-cy)/2.5)**2)
            buf[y0_:y1_]+=(sx*streak*0.9*a)[...,None]*np.array([1.0,0.55,0.25],np.float32)
# ---------- glass rain ----------
_g=np.random.default_rng(5); NP=520
PX=_g.uniform(0,1,NP); PY=_g.uniform(0,1,NP); PZ=_g.uniform(0.25,1.0,NP)**1.6; PS=_g.uniform(0.7,1.3,NP)
def glass_rain(buf,t,speed=1.0,dens=1.0,ang=-0.06,ymin=0.0,ymax=1.0,bright=1.0,length=1.0):
    lay=np.zeros_like(buf); n=int(NP*dens)
    for i in range(n):
        z=PZ[i]; v=(0.9+1.6*z)*speed*PS[i]
        x=((PX[i]+t*v*0.55)%1.25-0.12)*w; y=(ymin+(ymax-ymin)*PY[i])*h+x*ang
        L=(20+90*z)*speed*length; th=max(1,int(1+2.2*z))
        x2=x-L; y2=y-L*ang
        c=(0.55+0.45*z)*bright; tw=0.6+0.4*math.sin(t*23+i*1.7)
        cv2.line(lay,(int(x2),int(y2)),(int(x),int(y)),(0.55*c,0.8*c,1.0*c),th,cv2.LINE_AA)
        if z>0.75 and tw>0.85: cv2.circle(lay,(int(x),int(y)),th+1,(1.6*c,1.8*c,2.0*c),-1,cv2.LINE_AA)
    buf+=cv2.GaussianBlur(lay,(0,0),0.8)+cv2.GaussianBlur(lay,(0,0),3)*0.5
CL1=fbm((h,w*2),31,6,3,aspect=2); CL2=fbm((h,w*2),32,6,5,aspect=2)
def cloudscape(buf,t,spd=40,col_hi=(0.35,0.55,1.1),col_lo=(0.01,0.03,0.14),haze=0.4,sun=(0.8,0.1)):
    o1=int(t*spd)%w; o2=int(t*spd*1.9)%w
    a=np.roll(CL1,-o1,1)[:,:w]; b=np.roll(CL2,-o2,1)[:,:w]
    yb=(yy/h)
    lay=np.clip(0.5+0.35*a+0.25*b-(yb-0.5)*0.9,0,1)
    lo=np.array(col_lo,np.float32); hi=np.array(col_hi,np.float32)
    buf[:]=lo+(hi-lo)*(lay**1.6)[...,None]
    buf+=np.exp(-((xx-sun[0]*w)**2+(yy-sun[1]*h)**2)/(2*(w*0.5)**2))[...,None]*np.array([0.5,0.35,0.25],np.float32)*haze
def droplet(buf,x,y,r,a=1.0):
    x0,x1=max(0,int(x-r-3)),min(w,int(x+r+3)); y0,y1=max(0,int(y-r-3)),min(h,int(y+r+3))
    if x0>=x1 or y0>=y1: return
    X=(xx[y0:y1,x0:x1]-x)/r; Y=(yy[y0:y1,x0:x1]-y)/r; r2=X*X+Y*Y; ins=np.clip((1-r2)*r/1.5,0,1)
    Z=np.sqrt(np.clip(1-r2,0,1))
    reg=buf[y0:y1,x0:x1]; inner=np.flip(reg,(0,1))*0.55+np.array([0.02,0.05,0.12],np.float32)
    rim=np.clip(1-Z,0,1)**3*1.4; spec=np.exp(-((X+0.38)**2+(Y+0.42)**2)/0.012)*3.0; caus=np.exp(-((X-0.3)**2+(Y-0.45)**2)/0.05)*0.6
    val=inner+rim[...,None]*np.array([0.6,0.85,1.2],np.float32)+spec[...,None]+caus[...,None]*np.array([0.5,0.8,1.0],np.float32)
    reg[:]=reg*(1-ins[...,None]*a)+val*ins[...,None]*a
def hexagon(cx,cy,r):
    return np.array([(cx+r*math.cos(math.pi/6+k*math.pi/3),cy+r*math.sin(math.pi/6+k*math.pi/3)) for k in range(6)],np.int32)
def jwst(buf,cx,cy,s,t,sweep):
    buf[:]=STARS2*0.6
    r=s*0.98; dx=s*math.sqrt(3); pos=[]
    for q in range(-2,3):
        for rr in range(-2,3):
            if abs(q+rr)>2: continue
            if (q,rr)==(0,0): continue
            x=cx+dx*(q+rr/2); y=cy+s*1.5*rr
            if abs(q)+abs(rr)+abs(q+rr)>4: continue
            pos.append((x,y))
    for i,(x,y) in enumerate(pos):
        lay=np.zeros_like(buf); cv2.fillPoly(lay,[hexagon(x,y,r)],(1,1,1),cv2.LINE_AA); m=lay[...,0:1]
        d=((xx-x)*0.6+(yy-y))/(s*2)
        base=np.array([0.95,0.62,0.18],np.float32)*(0.55+0.35*np.clip(0.5-d[...,None],0,1))
        sp=np.exp(-((xx+yy*0.5-sweep)/(s*0.6))**2)[...,None]*np.array([2.4,1.9,1.1],np.float32)
        buf[:]=buf*(1-m)+(base+sp)*m
    for k in range(3):
        a=math.pi/2+k*2*math.pi/3; cv2.line(buf,(int(cx),int(cy)),(int(cx+math.cos(a)*s*5.2),int(cy-math.sin(a)*s*5.2)),(0.08,0.07,0.06),3,cv2.LINE_AA)
    cv2.circle(buf,(int(cx),int(cy)),int(s*0.55),(0.12,0.10,0.08),-1,cv2.LINE_AA)
def egg(buf,cx,cy,s,t,crack=1.0,fume=1.0):
    X=(xx-cx)/(s*0.78); Y=(yy-cy)/s; Y2=Y*(1+0.18*np.clip(-Y,0,1)); r2=X*X+Y2*Y2; ins=np.clip((1-r2)*s/2,0,1)
    Z=np.sqrt(np.clip(1-r2,0,1)); sh=np.clip(0.25+0.75*(Z*0.7-X*0.35-Y*0.35),0,1.2)
    col=np.array([1.0,0.9,0.75],np.float32)*sh[...,None]
    buf[:]=buf*(1-ins[...,None])+col*ins[...,None]
    if crack>0:
        gg=np.random.default_rng(4); pts=[(cx-s*0.76,cy-s*0.08)]
        for k in range(1,11): pts.append((cx-s*0.76+k*s*0.152,cy-s*0.08+gg.uniform(-1,1)*s*0.07+(-1)**k*s*0.03))
        cv2.polylines(buf,[np.array(pts[:1+int(10*crack)],np.int32)],False,(0.10,0.07,0.05),2,cv2.LINE_AA)
    if fume>0:
        f=np.roll(CL1,int(-t*60),0)[:,:w]; f2=np.roll(CL2,int(-t*90),0)[:,:w]
        m=np.clip(f*0.4+f2*0.3+0.2,0,1)*np.exp(-((xx-cx)/(s*1.3))**2)*np.clip((cy-yy)/(s*2.5),0,1)*np.clip((cy+s*0.2-yy)/(s*0.6),0,1)*fume
        buf+=m[...,None]*np.array([0.25,0.75,0.15],np.float32)
def earthdot(buf,x,y,r):
    glow(buf,x,y,r*2.2,(0.2,0.45,1.0),0.6); cv2.circle(buf,(int(x),int(y)),int(r),(0.15,0.38,0.9),-1,cv2.LINE_AA)
    cv2.ellipse(buf,(int(x-r*0.2),int(y-r*0.1)),(int(r*0.5),int(r*0.3)),20,0,360,(0.15,0.5,0.2),-1,cv2.LINE_AA)
# ---------- shots: each returns (canvas buffer, hud fn(img), camera zoom) ----------
def bg(): return STARS.copy()
def sh_hook(t,k=0):
    b=bg(); star(b,w*0.12,h*0.10,46,t,0.9,0.8)
    planet(b,w*0.62,h*1.02,w*0.95,0.5+t*0.035,L=(-0.7,-0.6,0.4))
    glass_rain(b,t,speed=1.0+0.6*k,dens=0.38+0.25*k,ang=-0.05,ymin=0.30,ymax=1.0,bright=1.2,length=0.8)
    z=1.03+0.03*sm(t/3)
    return b,None,z
def sh_marble(t,close=0):
    b=bg(); R=w*(0.33+0.08*close+0.015*(t-Ls(1))); planet(b,w*0.5,h*0.42,R,1.2+t*0.06,L=(-0.8,-0.3,0.5))
    star(b,w*1.05,h*0.05,30,t,0.6,0.5)
    return b,None,1.0+0.01*(t-Ls(1))
def sh_water(t):
    b=np.zeros((h,w,3),np.float32); cloudscape(b,t,spd=24,col_hi=(0.25,0.45,1.0),col_lo=(0.0,0.02,0.10),haze=0.18)
    def hud(img):
        a=fa(t,wt(2,"water")-0.08,99,0.12,0.2); sc=0.85+0.15*spring((t-wt(2,"water")+0.08)/0.2)
        label(img,"NOT WATER",540,560,128,ORANGE,a=a,sc=sc)
    return b,hud,1.04-0.012*(t-Ls(2))
def sh_transit(t):
    b=bg(); u=(t-Ls(3)+0.3)/2.4; star(b,w*0.5,h*0.36,w*0.36,t,1.0,0.0)
    px=w*(0.05+0.9*u); lay=np.zeros_like(b); cv2.circle(lay,(int(px),int(h*0.38)),34,(1,1,1),-1,cv2.LINE_AA)
    m=lay[...,0:1]; b[:]=b*(1-m*0.97)
    glow(b,px-34,h*0.38,8,(0.3,0.5,1.0),0.6)
    return b,None,1.02+0.02*u
def sh_orbit(t):
    b=bg()*0.8; cx,cy=w*0.5,h*0.40; star(b,cx,cy,52,t,1.0,0.6)
    u=t-wt(3,"year"); ang=-math.pi/2+u*2*math.pi/1.25
    cv2.ellipse(b,(int(cx),int(cy)),(170,170),0,0,360,(0.35,0.45,0.7),1,cv2.LINE_AA)
    for k in range(18):
        a2=ang-k*0.06; cv2.circle(b,(int(cx+170*math.cos(a2)),int(cy+170*math.sin(a2))),max(1,7-k//3),(0.25*(1-k/18),0.45*(1-k/18),1.0*(1-k/18)),-1,cv2.LINE_AA)
    planet(b,cx+170*math.cos(ang),cy+170*math.sin(ang),13,0,L=(-math.cos(ang),-math.sin(ang),0.3),atm=0.6)
    def hud(img):
        days=min(2.2,max(0.0,u*1.76))
        a=fa(t,wt(3,"year")+0.05,99,0.15,0.2)
        label(img,"1 YEAR",540,1010,70,WHITE,a=a); label(img,f"{days:.1f} DAYS",540,330,150,ORANGE,a=a)
    return b,hud,1.0+0.03*sm(u/1.5)
def sh_hot(t):
    b=bg(); u=t-Ls(4); heat=sm((u-0.2)/1.4); planet(b,w*0.5,h*0.42,w*0.40,2.0+t*0.05,L=(-0.4,-0.2,0.9),heat=heat*0.9)
    star(b,-w*0.05,h*0.20,40,t,0.7,0.4)
    def hud(img):
        a=fa(t,wt(4,"1,000")-0.1,99,0.15,0.2); v=int(1000*sm((t-wt(4,"1,000")+0.1)/0.6))
        label(img,f"{v:,}°C",540,330,170,ORANGE,a=a)
    return b,hud,1.0+0.04*sm(u/2.5)
def sh_silicate(t):
    b=np.zeros((h,w,3),np.float32); cloudscape(b,t,spd=60,col_hi=(0.20,0.36,0.85),col_lo=(0.0,0.005,0.04),haze=0.06)
    g=np.random.default_rng(3)
    for i in range(70):
        x=(g.uniform(0,1)*w+t*g.uniform(60,140))%(w+40)-20; y=g.uniform(0.15,0.95)*h+math.sin(t*2+i)*6; r=g.uniform(3,9)
        glow(b,x,y,r,(0.6,0.85,1.2),0.9*(0.5+0.5*math.sin(t*9+i*2.3)))
    def hud(img):
        a=fa(t,wt(5,"silicate")-0.1,99,0.15,0.2); sc=0.85+0.15*spring((t-wt(5,"silicate")+0.1)/0.2)
        label(img,"SILICATE",540,330,150,WHITE,a=a,sc=sc)
    return b,hud,1.05-0.015*(t-Ls(5))
def sh_drops(t):
    b=np.zeros((h,w,3),np.float32); cloudscape(b,t,spd=30,col_hi=(0.12,0.22,0.6),col_lo=(0.0,0.01,0.05),haze=0.15); b=cv2.GaussianBlur(b,(0,0),9)
    g=np.random.default_rng(8)
    for i,(x0_,y0_,r) in enumerate([(0.25,0.30,95),(0.72,0.22,55),(0.62,0.62,130),(0.18,0.72,60),(0.85,0.85,40),(0.40,0.88,35),(0.88,0.45,28)]):
        x=x0_*w+t*(18+i*6)-40; y=y0_*h+math.sin(t*1.3+i)*8
        droplet(b,x,y,r)
    def hud(img):
        a=fa(t,wt(5,"glass",0)-0.05,99,0.12,0.2); sc=0.85+0.15*spring((t-wt(5,"glass")+0.05)/0.2)
        label(img,"= GLASS",540,330,160,ORANGE,a=a,sc=sc)
    return b,hud,1.0+0.03*(t-wt(5,"stuff"))
def sh_wind(t,k=0):
    b=np.zeros((h,w,3),np.float32); cloudscape(b,t,spd=320,col_hi=(0.22,0.38,0.9),haze=0.2)
    b=cv2.blur(b,(41,1)); glass_rain(b,t,speed=2.4+k*0.6,dens=1.0,ang=-0.04,bright=1.5,length=1.3)
    def hud(img):
        if k: return
        a=fa(t,wt(6,"4,500")-0.08,99,0.12,0.2); v=int(4500*sm((t-wt(6,"4,500")+0.08)/0.5))
        label(img,f"{v:,} MPH",540,330,150,ORANGE,a=a)
    return b,hud,1.02
def sh_webb(t):
    b=np.zeros((h,w,3),np.float32); u=t-Ls(7)+0.3; jwst(b,w*0.5,h*0.40,58,t,-200+u*420)
    def hud(img):
        a=fa(t,wt(7,"Webb")-0.1,99,0.15,0.2); label(img,"JAMES WEBB",540,330,96,WHITE,a=a); label(img,"SPACE TELESCOPE",540,425,52,(255,210,140),a=a,stroke=6)
    return b,hud,1.0+0.05*sm(u/2.2)
SPX=np.linspace(0,1,300)
def spec_curve(u): return 0.32+0.05*np.sin(SPX*40)+0.03*np.sin(SPX*97+1)+0.38*np.exp(-((SPX-0.62)/0.025)**2)*u
def sh_spec(t,peak=0):
    b=bg()*0.35; b+=np.array([0.01,0.015,0.04],np.float32)
    u=t-wt(7,"something"); draw=cl(u/1.2) if not peak else 1.0; pk=sm((t-Ls(8))/0.4) if peak else 0.0
    def hud(img):
        d=ImageDraw.Draw(img); x0,x1,y0,y1=120,960,1000,520
        d.line((x0,y0,x1,y0),fill=(200,215,255,200),width=4); d.line((x0,y0,x0,y1),fill=(200,215,255,200),width=4)
        cv=spec_curve(pk); n=int(len(SPX)*draw)
        pts=[(x0+(x1-x0)*SPX[i],y0-(y0-y1)*cv[i]) for i in range(n)]
        if len(pts)>1:
            d.line(pts,fill=(120,200,255,90),width=14,joint="curve"); d.line(pts,fill=(170,225,255,255),width=6,joint="curve")
        label(img,"WAVELENGTH",540,1060,40,(200,215,255),a=0.9,stroke=4)
        if peak: label(img,"H₂S",x0+(x1-x0)*0.62,y0-(y0-y1)*0.75-90,150*(0.8+0.2*spring((t-Ls(8))/0.25)),ORANGE,a=sm((t-Ls(8)+0.05)/0.12))
        else: label(img,"WHAT'S IN THE AIR?",540,330,80,WHITE,a=fa(t,wt(7,"something"),99,0.15,0.2))
    return b,hud,1.0+0.02*u
def sh_egg(t):
    b=np.zeros((h,w,3),np.float32); b+=np.array([0.02,0.03,0.05],np.float32)+np.exp(-((xx-w*0.5)**2+(yy-h*0.45)**2)/(2*(w*0.45)**2))[...,None]*np.array([0.12,0.12,0.1],np.float32)
    u=t-wt(8,"rotten"); egg(b,w*0.5,h*0.50,150,t,crack=sm(u/0.5),fume=sm((u-0.2)/0.6))
    def hud(img): label(img,"ROTTEN EGGS",540,330,128,(150,240,90),a=fa(t,wt(8,"rotten")-0.05,99,0.12,0.2))
    return b,hud,1.0+0.04*sm(u/1.5)
def sh_name(t):
    b=bg(); u=t-Ls(9)+0.3; planet(b,w*0.5,h*0.42,w*0.36,3.0+t*0.06,L=(-0.8,-0.4,0.45))
    star(b,w*0.95,h*0.08,26,t,0.5,0.4)
    def hud(img):
        a=fa(t,wt(9,"HD")-0.1,99,0.15,0.2); label(img,"HOT JUPITER",540,290,120,WHITE,a=a); label(img,"FOUND IN 2005",540,400,64,(255,210,140),a=a,stroke=6)
    return b,hud,1.0+0.03*u
def sh_dist(t):
    b=bg(); u=t-wt(9,"right"); z=sm(u/1.5)
    px=w*lerp(0.5,0.80,z); R=w*lerp(0.36,0.035,z)
    planet(b,px,h*0.42,R,3.0+t*0.06,L=(-0.8,-0.4,0.45))
    ex=w*0.18; earthdot(b,ex,h*0.42,9*z+0.01)
    def hud(img):
        a=sm((u-0.5)/0.3)
        if a>0:
            d=ImageDraw.Draw(img); y=int(h*0.42*K)
            for x in range(int(ex*K)+40,int(px*K)-60,36): d.line((x,y,x+18,y),fill=(255,255,255,int(200*a)),width=5)
            label(img,"EARTH",ex*K,y+90,44,WHITE,a=a,stroke=5); label(img,"~600 TRILLION KM",540,y-120,84,ORANGE,a=a)
    return b,hud,1.0
SHOTS=[(0.0,lambda t:sh_hook(t,0),"cut"),(wt(0,"Sideways")-0.05,lambda t:sh_hook(t,1),"cut"),
 (Ls(1)-0.3,lambda t:sh_marble(t,0),"whip"),(wt(1,"calm")-0.05,lambda t:sh_marble(t,1),"cut"),
 (Ls(2)-0.12,sh_water,"cut"),(Ls(3)-0.3,sh_transit,"whip"),(wt(3,"year")-0.05,sh_orbit,"cut"),
 (Ls(4)-0.15,sh_hot,"cut"),(Ls(5)-0.3,sh_silicate,"whip"),(wt(5,"stuff")-0.05,sh_drops,"cut"),
 (Ls(6)-0.15,lambda t:sh_wind(t,0),"cut"),(wt(6,"fling")-0.05,lambda t:sh_wind(t,1),"cut"),
 (Ls(7)-0.3,sh_webb,"whip"),(wt(7,"something")-0.05,lambda t:sh_spec(t,0),"cut"),(Ls(8)-0.05,lambda t:sh_spec(t,1),"cut"),
 (wt(8,"rotten")-0.1,sh_egg,"cut"),(Ls(9)-0.3,sh_name,"whip"),(wt(9,"right")-0.05,sh_dist,"cut")]
CUTS=[s[0] for s in SHOTS[1:]]
TR=0.17; LOOPD=0.42
def shot_at(t):
    i=0
    for k,s in enumerate(SHOTS):
        if t>=s[0]: i=k
    return i
def render_shot(i,t):
    b,hud,z=SHOTS[i][1](t); st=SHOTS[i][0]
    z*=punch(t,[st] if i>0 else [],0.06,0.32)
    dx,dy=shake(t,wt(0,"Sideways"),8,0.5); d2=shake(t,wt(6,"fling"),6,0.4); dx+=d2[0]; dy+=d2[1]
    return camera(b,z,0.5,0.45,dx,dy),hud
def whip(b1,b2,u):
    s=math.sin(math.pi*u); b=b1 if u<0.5 else b2
    off=int((u if u<0.5 else u-1)*-w*0.5)
    b=np.roll(b,off,1); k=int(2+s*90)|1; b=cv2.blur(b,(k,1))
    yb=np.exp(-((yy-h*0.45)/(6+40*s))**2)[...,None]*np.array([1.0,0.75,0.5],np.float32)*s*2.2
    return b*(1+0.8*s)+yb+s*0.08
def compose(t,fi=None):
    if fi is None: fi=int(round(t*30))
    i=shot_at(max(t,0)); nxt=SHOTS[i+1] if i+1<len(SHOTS) else None
    huds=[]
    if nxt and nxt[2]=="whip" and t>nxt[0]-TR:
        u=(t-(nxt[0]-TR))/(2*TR); b1,h1=render_shot(i,t); b2,h2=render_shot(i+1,t); b=whip(b1,b2,u)
    elif SHOTS[i][2]=="whip" and t<SHOTS[i][0]+TR and i>0:
        u=(t-(SHOTS[i][0]-TR))/(2*TR); b1,h1=render_shot(i-1,t); b2,h2=render_shot(i,t); b=whip(b1,b2,u); huds=[h2] if u>0.5 else []
    elif t>TOTAL-LOOPD:
        u=(t-(TOTAL-LOOPD))/LOOPD; b1,h1=render_shot(i,t); b2,h2=render_shot(0,t-TOTAL); b=whip(b1,b2,u)
    else:
        b,h1=render_shot(i,t); huds=[h1]
    b=post(b,bloom=0.6,thr=0.6)
    img=to_img(b,fi)
    for hf in huds:
        if hf: hf(img)
    # hook title: on the first frame, back during the loop tail
    ha=1-sm((t-2.75)/0.3) if t<3.1 else sm((t-(TOTAL-LOOPD))/0.25)
    if ha>0.01:
        hook_title(img,[("IT RAINS GLASS",WHITE)],a=ha,y=250,size=128)
        s2=wt(0,"Sideways")-0.05
        if t>=s2 or t>TOTAL-LOOPD:
            a2=ha*(sm((t-s2)/0.08) if t<3.1 else 1.0); sc=0.7+0.3*spring((t-s2)/0.22) if t<3.1 else 1.0
            hook_title(img,[("SIDEWAYS",ORANGE)],a=a2,y=390,size=150,sc=sc)
    return finish(img,CAP,t)
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
