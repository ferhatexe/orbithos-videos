import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid74"); sys.path.insert(0,"/home/claude/toolkit")
from pro import *
from PIL import Image, ImageDraw
T,LINES,SC,TOTAL=load("timeline.json")
CAP=Captions(LINES); WD=CAP.W
def wt(li,sub,o=0.0): return word_t(WD,li,sub,o)
def Ls(i): return LINES[i]["s"]
def sm_np(x): x=np.clip(x,0,1); return x*x*(3-2*x)
# ================= Apollo 12, 14 Nov 1969: cinematic launch-day CG, storm sky, Saturn V, lightning, Mission Control CRTs =================
F32=np.float32
# ---------- cached textures ----------
CH=2600
def _clouds(seed,H,thr,soft,dark,light,base=3):
    n=fbm((H,w),seed,6,base,aspect=w/H*1.0)
    a=sm_np((n-thr)/soft).astype(F32)
    em=np.clip(0.5+(n-np.roll(n,10,0))*1.6,0,1)
    col=np.array(dark,F32)*(1-em[...,None])+np.array(light,F32)*em[...,None]
    return col.astype(F32),a
def _rain(seed,n=1100):
    g=np.random.default_rng(seed); r=np.zeros((h,w),F32)
    for i in range(n):
        x,y=g.uniform(-40,w+40),g.uniform(0,h); L=g.uniform(18,46); dx=L*0.16
        cv2.line(r,(int(x),int(y)),(int(x-dx),int(y+L)),float(g.uniform(0.25,1.0)),1,cv2.LINE_AA)
    return cv2.GaussianBlur(r,(0,0),0.6)
CACHE="tex74.npz"
if os.path.exists(CACHE):
    _z=np.load(CACHE); CL1c,CL1a,CL2c,CL2a,RAIN1,RAIN2=[_z[k] for k in ("a","b","c","d","e","f")]
else:
    CL1c,CL1a=_clouds(741,CH,-0.4,0.9,(0.16,0.17,0.20),(0.55,0.57,0.62),3)
    CL2c,CL2a=_clouds(742,CH,0.1,0.8,(0.08,0.085,0.10),(0.38,0.40,0.45),4)
    RAIN1=_rain(743,1100); RAIN2=_rain(744,500)
    np.savez(CACHE,a=CL1c,b=CL1a,c=CL2c,d=CL2a,e=RAIN1,f=RAIN2)
def scroll(tex,off):
    off=int(off)%(CH-h); return tex[off:off+h]
def storm_sky(u,vy=40,vy2=90,top=(0.10,0.11,0.14),bot=(0.34,0.36,0.40),flash=0.0,dens=1.0):
    k=(yy/h)[...,None]; b=np.array(top,F32)*(1-k)+np.array(bot,F32)*k
    c1=scroll(CL1c,CH-h-200-u*vy); a1=scroll(CL1a,CH-h-200-u*vy)[...,None]*dens
    b=b*(1-a1)+c1*a1
    c2=scroll(CL2c,CH-h-100-u*vy2); a2=scroll(CL2a,CH-h-100-u*vy2)[...,None]*0.85*dens
    b=b*(1-a2)+c2*a2
    if flash>0: b=b+(a1*0.7+a2*0.5+0.15)*np.array([0.75,0.82,1.0],F32)*flash
    return b
def rain(b,u,amt=0.22,ang=0):
    r=np.roll(RAIN1,int(u*1500)%h,0); r2=np.roll(RAIN2,int(u*2100)%h,0)
    b+=(r*amt+r2*amt*1.3)[...,None]*np.array([0.75,0.80,0.88],F32)
# ---------- Saturn V sprite (side view, meters -> px) ----------
PXM=10
def _saturn():
    Hm,Wm=118,16; Hs,Ws=Hm*PXM,Wm*PXM; cx=Ws/2
    prof=[(10.0,0.35),(10.4,0.7),(13.6,1.96),(21.0,1.96),(29.0,3.3),(46.0,3.3),(50.0,5.05),(110.0,5.05)]
    ys=np.arange(Hs)/PXM; r=np.interp(ys,[p[0] for p in prof],[p[1] for p in prof]); r[ys<10]=0
    Y,X=np.mgrid[0:Hs,0:Ws].astype(F32); ym=Y/PXM; u=(X-cx)/(np.maximum(r[:,None],1e-3)*PXM)
    ins=(np.abs(u)<=1)&(ym>=10)&(ym<=110)
    col=np.zeros((Hs,Ws,3),F32)+np.array([0.92,0.92,0.90],F32)
    BLK=np.array([0.06,0.06,0.07],F32)
    def setb(mask): col[mask]=BLK
    col[(ym>=13.6)&(ym<21)]=np.array([0.70,0.72,0.75],F32)
    for k in range(6): col[(ym>=14.5+k*1.1)&(ym<14.8+k*1.1)]=np.array([0.55,0.57,0.6],F32)
    setb((ym>=41.5)&(ym<46)&(u<0)); setb((ym>=29.0)&(ym<31.0)&(u>0))
    setb((ym>=71.5)&(ym<75.5))
    setb((ym>=75.5)&(ym<82)&(u>0)); setb((ym>=92)&(ym<104)&(u<0)); setb((ym>=104)&(ym<110)&(u>0))
    # USA letters on the S-IC
    lay=np.zeros((Hs,Ws),np.uint8)
    for i,ch in enumerate("USA"):
        cv2.putText(lay,ch,(int(cx+0.25*5.05*PXM),int(84*PXM+i*28)),cv2.FONT_HERSHEY_DUPLEX,0.9,255,2,cv2.LINE_AA)
    col[lay>128]=BLK
    # cylinder shading (light from upper-left)
    uu=np.clip(u,-1,1); nz=np.sqrt(np.clip(1-uu*uu,0,1)); dif=np.clip(-uu*0.55+nz*0.83,0,1)
    sh=(0.28+0.85*dif)[...,None]; rim=(np.clip(uu,0,1)**6)[...,None]*0.25
    col=col*sh+rim*np.array([0.6,0.7,0.9],F32)
    a=ins.astype(F32)
    # fins + engine fairings
    for sgn in (-1,1):
        p=np.array([(cx+sgn*5.0*PXM,101*PXM),(cx+sgn*7.4*PXM,106.5*PXM),(cx+sgn*7.4*PXM,110*PXM),(cx+sgn*5.0*PXM,110*PXM)],np.int32)
        cv2.fillPoly(col,[p],(0.05,0.05,0.06),cv2.LINE_AA); cv2.fillPoly(a,[p],1.0,cv2.LINE_AA)
        p=np.array([(cx+sgn*4.2*PXM,104*PXM),(cx+sgn*5.6*PXM,106*PXM),(cx+sgn*5.6*PXM,111*PXM),(cx+sgn*4.2*PXM,111*PXM)],np.int32)
        cv2.fillPoly(col,[p],(0.75,0.75,0.74),cv2.LINE_AA); cv2.fillPoly(a,[p],1.0,cv2.LINE_AA)
    for ex in (-3.0,0.0,3.0):
        p=np.array([(cx+(ex-0.9)*PXM,110*PXM),(cx+(ex+0.9)*PXM,110*PXM),(cx+(ex+1.7)*PXM,116*PXM),(cx+(ex-1.7)*PXM,116*PXM)],np.int32)
        cv2.fillPoly(col,[p],(0.10,0.09,0.09),cv2.LINE_AA); cv2.fillPoly(a,[p],1.0,cv2.LINE_AA)
    # launch escape tower
    cv2.fillPoly(col,[np.array([(cx-0.45*PXM,2*PXM),(cx+0.45*PXM,2*PXM),(cx+0.45*PXM,7*PXM),(cx-0.45*PXM,7*PXM)],np.int32)],(0.75,0.75,0.74),cv2.LINE_AA)
    cv2.fillPoly(a,[np.array([(cx-0.45*PXM,2*PXM),(cx+0.45*PXM,2*PXM),(cx+0.45*PXM,7*PXM),(cx-0.45*PXM,7*PXM)],np.int32)],1.0,cv2.LINE_AA)
    cv2.fillPoly(col,[np.array([(cx,0),(cx+0.3*PXM,2*PXM),(cx-0.3*PXM,2*PXM)],np.int32)],(0.6,0.6,0.6),cv2.LINE_AA)
    cv2.fillPoly(a,[np.array([(cx,0),(cx+0.3*PXM,2*PXM),(cx-0.3*PXM,2*PXM)],np.int32)],1.0,cv2.LINE_AA)
    for s_ in (-1,1):
        cv2.line(col,(int(cx+s_*0.4*PXM),7*PXM),(int(cx+s_*1.2*PXM),int(10.6*PXM)),(0.75,0.25,0.15),3,cv2.LINE_AA); cv2.line(a,(int(cx+s_*0.4*PXM),7*PXM),(int(cx+s_*1.2*PXM),int(10.6*PXM)),1.0,3,cv2.LINE_AA)
        cv2.line(col,(int(cx-s_*0.4*PXM),7*PXM),(int(cx+s_*1.2*PXM),int(10.6*PXM)),(0.75,0.25,0.15),2,cv2.LINE_AA); cv2.line(a,(int(cx-s_*0.4*PXM),7*PXM),(int(cx+s_*1.2*PXM),int(10.6*PXM)),1.0,2,cv2.LINE_AA)
    return np.dstack([col,a]).astype(F32)
SCACHE="sat74.npy"
if os.path.exists(SCACHE): SAT=np.load(SCACHE)
else: SAT=_saturn(); np.save(SCACHE,SAT)
def rocket(b,x,y,s,ang=0.0,anchor=60.0,bright=1.0,flash=0.0,tint=(1,1,1),upto=None):
    """place Saturn V: sprite point (centre, anchor m) at canvas (x,y); s = canvas px per metre; ang deg (+ = lean right)"""
    sc=s/PXM; M=cv2.getRotationMatrix2D((SAT.shape[1]/2,anchor*PXM),-ang,sc); M[0,2]+=x-SAT.shape[1]/2; M[1,2]+=y-anchor*PXM
    SP=SAT if upto is None else SAT[:int(upto*PXM)]
    o=cv2.warpAffine(SP,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    a=o[...,3:4]; c=o[...,:3]*bright*np.array(tint,F32)+flash*np.array([0.7,0.8,1.0],F32)*a
    b[:]=b*(1-a)+c*a
def axis_pt(x,y,s,ang,anchor,m):
    """canvas position of the point at m metres along the rocket axis"""
    r=math.radians(ang); d=(m-anchor)*s; return x-math.sin(r)*d, y+math.cos(r)*d
def flame(b,x,y,s,ang,anchor,u,k=1.0,trail=10,L=34):
    fx,fy=axis_pt(x,y,s,ang,anchor,115.5); r=math.radians(ang); dx,dy=-math.sin(r),math.cos(r); px,py=math.cos(r),math.sin(r)
    fl=0.85+0.15*math.sin(u*53)+0.1*math.sin(u*31); L=L*(0.92+0.08*math.sin(u*37))
    # smoke / exhaust trail behind the flame
    for i in range(trail):
        d=s*(L*0.8+i*9); glow(b,fx+dx*d,fy+dy*d,s*(5+i*1.8),(0.55,0.52,0.50),(0.55-i*0.03)*k)
    lay=np.zeros((h//2,w//2),F32); core=np.zeros((h//2,w//2),F32)
    def P(a_,c_): return (int((fx+dx*a_*s+px*c_*s)/2),int((fy+dy*a_*s+py*c_*s)/2))
    cv2.fillPoly(lay,[np.array([P(0,-3.6),P(0,3.6),P(L*0.35,4.3),P(L,0),P(L*0.35,-4.3)],np.int32)],1.0,cv2.LINE_AA)
    cv2.fillPoly(core,[np.array([P(0,-3.0),P(0,3.0),P(L*0.25,3.0),P(L*0.6,0),P(L*0.25,-3.0)],np.int32)],1.0,cv2.LINE_AA)
    sg=max(1.0,s*0.9)
    lay=cv2.GaussianBlur(lay,(0,0),sg); core=cv2.GaussianBlur(core,(0,0),sg*0.6)
    lay=cv2.resize(lay,(w,h)); core=cv2.resize(core,(w,h))
    b+=(lay[...,None]*np.array([1.9,0.85,0.25],F32)+core[...,None]*np.array([2.2,1.9,1.3],F32))*k*fl
    glow(b,fx,fy,s*4.0,(2.6,2.2,1.6),0.9*k*fl)
    glow(b,fx+dx*s*L*0.4,fy+dy*s*L*0.4,s*28,(0.9,0.45,0.15),0.30*k)
# ---------- lightning ----------
def _mid(pts,disp,g,depth):
    for _ in range(depth):
        out=[pts[0]]
        for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
            L=math.hypot(x1-x0,y1-y0); nx,ny=-(y1-y0)/(L+1e-6),(x1-x0)/(L+1e-6); o=g.normal(0,disp*L)
            out+=[((x0+x1)/2+nx*o,(y0+y1)/2+ny*o),(x1,y1)]
        pts=out
    return pts
_BC={}
def bolt_geom(seed,p0,p1,branches=6,disp=0.22):
    key=(seed,tuple(map(int,p0)),tuple(map(int,p1)),branches)
    if key in _BC: return _BC[key]
    g=np.random.default_rng(seed); main=_mid([p0,p1],disp,g,7); segs=[(np.array(main,np.int32),1.0)]
    for i in range(branches):
        j=int(g.uniform(0.1,0.8)*len(main)); x0,y0=main[j]; L=math.hypot(p1[0]-p0[0],p1[1]-p0[1])*g.uniform(0.12,0.35)
        a=math.atan2(p1[1]-p0[1],p1[0]-p0[0])+g.choice([-1,1])*g.uniform(0.35,0.9)
        br=_mid([(x0,y0),(x0+math.cos(a)*L,y0+math.sin(a)*L)],disp*1.1,g,5); segs.append((np.array(br,np.int32),0.55))
        if g.random()<0.5:
            k=len(br)//2; x2,y2=br[k]; a2=a+g.choice([-1,1])*0.6; L2=L*0.45
            segs.append((np.array(_mid([(x2,y2),(x2+math.cos(a2)*L2,y2+math.sin(a2)*L2)],disp*1.2,g,4),np.int32),0.3))
    _BC[key]=segs; return segs
def bolt(b,seed,p0,p1,I,branches=6,width=2,col=(0.85,0.9,1.25)):
    if I<=0.01: return
    lay=np.zeros((h,w),F32)
    for pts,wgt in bolt_geom(seed,p0,p1,branches):
        cv2.polylines(lay,[pts],False,float(wgt),max(1,int(round(width*(1 if wgt>0.9 else 0.6)))),cv2.LINE_AA)
    sm_=cv2.resize(lay,(w//4,h//4),interpolation=cv2.INTER_AREA)
    gl=cv2.resize(cv2.GaussianBlur(sm_,(0,0),2.0)*1.6+cv2.GaussianBlur(sm_,(0,0),9)*3.0,(w,h),interpolation=cv2.INTER_LINEAR)
    b+=(lay*1.6)[...,None]*np.array([1.2,1.2,1.3],F32)*I+gl[...,None]*np.array(col,F32)*I
def flick(t,t0,dur=0.55):
    """lightning intensity envelope: main stroke + two restrikes"""
    e=t-t0
    if e<0 or e>dur: return 0.0
    v=math.exp(-e*9)+0.8*math.exp(-((e-0.09)/0.025)**2)+0.6*math.exp(-((e-0.20)/0.03)**2)
    return min(1.4,v)
# ---------- shots ----------
T_L0=wt(0,"lightning"); T_TW=wt(0,"twice")
def sh_hook(t,end=False):
    tt=t if not end else t-TOTAL
    u=tt+3.0; ang=9+0.6*math.sin(u*0.7)
    f0=flick(tt,-0.02,0.6); f1=flick(tt,T_L0-0.05); f2=flick(tt,T_TW-0.02); fl=max(f1,f2,f0*0.7)
    b=storm_sky(u,vy=150,vy2=260,top=(0.07,0.08,0.11),bot=(0.26,0.28,0.33),flash=fl*0.6)
    x,y,s=370+8*math.sin(u*0.9),735,7.0
    flame(b,x,y,s,ang,60,u,1.0,9)
    rocket(b,x,y,s,ang,60,1.0,fl*0.3)
    nx,ny=axis_pt(x,y,s,ang,60,1)
    if f1>0: bolt(b,11,(80,-20),(nx,ny),f1,7,3); bolt(b,12,axis_pt(x,y,s,ang,60,116),(40,h+20),f1*0.8,4,2)
    if f2>0: bolt(b,21,(700,-30),(nx+4,ny+6),f2,7,3); bolt(b,22,axis_pt(x,y,s,ang,60,116),(260,h+20),f2*0.8,4,2)
    if f0>0: bolt(b,7,(640,330),(560,h+20),f0*0.9,6,2)
    rain(b,u,0.16)
    return b,None,1.04+0.03*sm((tt+0.2)/3.5)
def pad_scene(t,lift,zoom_on=False):
    u=t-Ls(1)+2.0; e=max(0.0,t-lift)
    b=storm_sky(u,vy=12,vy2=25,top=(0.12,0.13,0.16),bot=(0.40,0.41,0.44))
    hor=1000
    x,s=320,6.9; base_y=hor-2-10*e*e
    # launch tower (red lattice)
    tx0,tx1,ttop=410,470,hor-int(124*s)
    lay=b.copy(); cv2.rectangle(lay,(tx0,ttop),(tx1,hor),(0.20,0.07,0.05),-1)
    for yv in range(ttop,hor,22): cv2.line(lay,(tx0,yv),(tx1,yv+22),(0.45,0.14,0.08),2,cv2.LINE_AA); cv2.line(lay,(tx1,yv),(tx0,yv+22),(0.45,0.14,0.08),2,cv2.LINE_AA)
    for k_,yv in enumerate((ttop+60,ttop+190,ttop+330,ttop+470)):
        arm=int(60*(1-sm(e/0.6))) if k_<3 else 60
        cv2.rectangle(lay,(tx0-arm-8,yv),(tx0,yv+12),(0.30,0.10,0.06),-1)
    cv2.rectangle(lay,(tx0-10,ttop-40),(tx0+4,ttop),(0.25,0.08,0.05),-1)
    b[:]=lay
    rocket(b,x,base_y-110*s+60*s,s,0,60,0.95)
    glow(b,tx1-10,ttop+10,6,(2.5,0.3,0.2),0.8+0.4*math.sin(t*6))
    for fx_ in (60,640): glow(b,fx_,hor-260,8,(2.2,2.0,1.6),1.0); glow(b,fx_,hor-260,60,(0.5,0.45,0.35),0.5)
    # ground + wet reflection
    gnd=np.array([0.10,0.10,0.11],F32); b[hor:]=gnd
    ref=cv2.GaussianBlur(b[hor-(h-hor):hor][::-1],(0,0),3)*0.35
    rip=np.sin(yy[hor:]*0.9+np.sin(xx[hor:]*0.05+u*3)*2)[...,None]*0.04
    b[hor:]=b[hor:]+ref+rip
    if e>0:
        k=sm(e/0.8)
        flame(b,x,base_y-110*s+60*s,s,0,60,u,1.2*k,4)
        for i in range(10):
            sx=x+(i-4.5)*70*k*(1+e*0.4); sy=hor-20-abs(i-4.5)*8; r=(40+e*60)*(0.6+0.4*k)
            glow(b,sx,sy,r,(0.85,0.70,0.55),0.55*k)
        glow(b,x,hor,250,(1.2,0.6,0.25),0.6*k)
    rain(b,u,0.24)
    def hud(img):
        if not zoom_on:
            label(img,"NOV 14, 1969",540,300,118,WHITE,a=fa(t,Ls(1)-0.1,99,0.2,0.2))
            label(img,"KENNEDY SPACE CENTER",540,410,58,ORANGE,a=fa(t,Ls(1)+0.3,99,0.2,0.2),stroke=6)
        else:
            label(img,"LIFTOFF",540,300,124,WHITE,a=fa(t,lift-0.1,99,0.15,0.2))
            label(img,"11:22 AM · IN THE RAIN",540,415,58,ORANGE,a=fa(t,lift+0.2,99,0.2,0.2),stroke=6)
    z=1.0+0.03*sm((t-Ls(1))/3) if not zoom_on else 1.18+0.05*sm(e/2)
    return b,hud,z
def sh_pad(t): return pad_scene(t,wt(1,"lifted"))
def sh_lift(t): return pad_scene(t,wt(1,"lifted"),True)
def sh_nixon(t):
    u=t-Ls(1); e=t-wt(1,"lifted")
    b=storm_sky(u+5,vy=8,vy2=16,top=(0.13,0.14,0.17),bot=(0.45,0.44,0.44))
    hor=860; b[hor:]=np.array([0.10,0.11,0.10],F32)
    ref=cv2.GaussianBlur(b[hor-(h-hor):hor][::-1],(0,0),4)*0.45; b[hor:]+=ref[:h-hor]
    x,s=470,3.0; by=hor-8-e*e*10-e*25
    glow(b,x,hor-60,220,(1.0,0.55,0.2),0.45)
    flame(b,x,by-110*s+60*s,s,0,60,u,1.3,8)
    rocket(b,x,by-110*s+60*s,s,0,60,0.9)
    for i in range(12): glow(b,x+(i-6)*14,hor-4,20+i*2,(0.75,0.65,0.55),0.4)
    # foreground crowd with umbrellas (silhouettes)
    g=np.random.default_rng(9); C=(0.025,0.025,0.03)
    for row,(y0,sc,n) in enumerate(((1130,0.9,16),(1210,1.2,12),(1290,1.6,8))):
        for i in range(n):
            px=g.uniform(-30,w+30); s_=sc*g.uniform(18,24)
            cv2.circle(b,(int(px),int(y0-s_*1.9)),int(s_*0.5),C,-1,cv2.LINE_AA)
            cv2.ellipse(b,(int(px),int(y0)),(int(s_*0.85),int(s_*1.4)),0,180,360,C,-1,cv2.LINE_AA)
            if g.random()<0.55:
                ux=px+g.uniform(-10,10); uy=y0-s_*3.1
                cv2.ellipse(b,(int(ux),int(uy)),(int(s_*1.9),int(s_*1.0)),0,180,360,C,-1,cv2.LINE_AA)
                cv2.line(b,(int(ux),int(uy)),(int(ux),int(y0-s_*1.5)),C,2,cv2.LINE_AA)
        cv2.rectangle(b,(0,int(y0)),(w,h),C,-1)
    # rim light from the launch on umbrellas
    rain(b,u,0.22)
    def hud(img):
        label(img,"PRESIDENT NIXON",540,300,104,WHITE,a=fa(t,wt(1,"President")-0.15,99,0.15,0.2))
        label(img,"1ST PRESIDENT AT A CREWED LAUNCH",540,405,46,ORANGE,a=fa(t,wt(1,"Nixon")+0.2,99,0.2,0.2),stroke=5)
    return b,hud,1.0+0.04*sm(u/5)
S1=wt(2,"bolt")-0.08; S2=wt(2,"another")-0.08
def climb(t,strike,alt,ang=6,seed=31,side=1):
    u=t-Ls(2)+(0 if side>0 else 3)
    fl=flick(t,strike)
    b=storm_sky(u,vy=220,vy2=420,top=(0.09,0.10,0.13),bot=(0.30,0.31,0.35),flash=fl*0.5)
    x,y,s=360,700,6.6
    flame(b,x,y,s,ang,60,u,1.0,9)
    rocket(b,x,y,s,ang,60,1.0,fl*0.3)
    if fl>0:
        nx,ny=axis_pt(x,y,s,ang,60,1)
        bolt(b,seed,(60 if side>0 else 660,-20),(nx,ny),fl,8,3)
        tx,ty=axis_pt(x,y,s,ang,60,117); bolt(b,seed+1,(tx,ty),(160 if side>0 else 600,h+30),fl*0.9,5,3)
    rain(b,u,0.12)
    def hud(img):
        a=fa(t,strike-0.05,99,0.08,0.2); sc=0.75+0.25*spring((t-strike)/0.25)
        label(img,"T+%s s"%("36.5" if side>0 else "52"),540,300,140,WHITE,a=a,sc=sc)
        label(img,alt,540,425,62,ORANGE,a=a,stroke=6)
    return b,hud,1.02+0.03*sm((t-strike+0.5)/2)
def sh_climb1(t): return climb(t,S1,"~6,400 FT UP",6,31,1)
def sh_climb2(t): return climb(t,S2,"~14,400 FT UP",-5,41,-1)
def sh_trigger(t,ph=1):
    u=t-Ls(3); tb=wt(3,"triggered")-0.05; fl=max(flick(t,tb,0.7),0.6*flick(t,tb+0.45,0.5))
    b=storm_sky(u+9,vy=10,vy2=20,top=(0.11,0.12,0.15),bot=(0.30,0.32,0.36),flash=fl*0.7)
    hor=1120; b[hor:]=np.array([0.07,0.08,0.08],F32)
    for i in range(30): cv2.line(b,(0,hor+3+i*i//4),(w,hor+3+i*i//4),(0.10,0.11,0.12),1)
    x,y,s=440,420,1.7; ang=8
    tx,ty=axis_pt(x,y,s,ang,60,117)
    # exhaust trail: curved column to the pad
    pts=[(tx+(330-tx)*(k/30)**1.6,ty+(hor-ty)*k/30) for k in range(31)]
    for k,(px,py) in enumerate(pts): glow(b,px,py,10+k*0.9,(0.55,0.55,0.58),0.45)
    glow(b,tx,ty,8,(3,2.2,1.2),1.2); glow(b,tx,ty+10,22,(1.6,0.8,0.3),0.8)
    rocket(b,x,y,s,ang,60,1.0,fl)
    if fl>0:
        bolt(b,51,(250,-20),axis_pt(x,y,s,ang,60,1),fl,6,3)
        lay=np.zeros((h,w),F32); cv2.polylines(lay,[np.array(pts,np.int32)],False,1.0,3,cv2.LINE_AA)
        j=np.random.default_rng(int(t*30)).normal(0,3,(31,2)); cv2.polylines(lay,[np.array(np.array(pts)+j,np.int32)],False,1.0,2,cv2.LINE_AA)
        b+=(lay*1.4+cv2.GaussianBlur(lay,(0,0),8)*5)[...,None]*np.array([0.8,0.9,1.3],F32)*fl
        glow(b,330,hor,60,(1.0,1.1,1.5),fl*0.8)
    rain(b,u,0.10)
    def hud(img):
        label(img,"NO THUNDER FOR 6 HOURS",540,300,74,WHITE,a=fa(t,Ls(3)+0.05,99,0.2,0.2))
        a=fa(t,tb-0.05,99,0.1,0.2); label(img,"TRIGGERED LIGHTNING",540,405,80,ORANGE,a=a,sc=0.8+0.2*spring((t-tb)/0.25))
        label(img,"EXHAUST TRAIL",230,700,40,(200,215,255),a=fa(t,tb+0.25,99,0.2,0.2),stroke=5)
        label(img,"= A GIANT WIRE",230,745,40,(200,215,255),a=fa(t,tb+0.25,99,0.2,0.2),stroke=5)
    if ph==0:
        M=cv2.getRotationMatrix2D((440,470),0,1.9+0.1*sm(u/2)); M[0,2]+=360-440; M[1,2]+=640-470
        b=cv2.warpAffine(b,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    return b,hud,(1.0+0.03*sm(u/3)) if ph else 1.0
def sh_trig0(t): return sh_trigger(t,0)
# ---------- caution & warning panel ----------
CW=["FC 1","FC 2","FC 3","MN BUS A","MN BUS B","AC BUS 1","AC BUS 2","AC BUS 1 OVLD","AC BUS 2 OVLD","FC BUS DISC","INV 1 TEMP","CMC","ISS","CRYO PRESS","GLYCOL","SPS PRESS","C/W","O2 FLOW HI","SM RCS A","SM RCS B"]
PX0,PY0,PCW,PCH,PGX,PGY=90,360,132,58,10,12   # canvas coords, 4 cols x 5 rows
def cw_rect(i):
    c,r=i%4,i//4; x=PX0+c*(PCW+PGX); y=PY0+r*(PCH+PGY); return x,y
def cw_on(t,i):
    t0=wt(4,"warning")-0.1+((i*7)%20)*0.035
    if i<3: t0=min(t0,wt(4,"three")-0.1)
    return t>=t0
def sh_panel(t,close=False):
    u=t-Ls(4); b=np.zeros((h,w,3),F32)+np.array([0.20,0.21,0.22],F32)
    n=cv2.resize(fbm((64,36),761,4,3),(w,h)); b*=(0.9+0.06*n)[...,None]
    cv2.rectangle(b,(PX0-26,PY0-26),(PX0+4*(PCW+PGX)+16,PY0+5*(PCH+PGY)+16),(0.11,0.115,0.12),-1)
    for (sx,sy) in ((PX0-14,PY0-14),(PX0+4*(PCW+PGX)+4,PY0-14),(PX0-14,PY0+5*(PCH+PGY)+4),(PX0+4*(PCW+PGX)+4,PY0+5*(PCH+PGY)+4)):
        cv2.circle(b,(sx,sy),6,(0.4,0.4,0.42),-1,cv2.LINE_AA)
    blink=0.5+0.5*(math.sin(t*18)>0)
    for i in range(20):
        x,y=cw_rect(i); on=cw_on(t,i)
        if on:
            col=(1.6,0.25,0.12) if i<3 else (1.5,0.85,0.18)
            k=blink if i<3 and t>wt(4,"three") else 1.0
            cv2.rectangle(b,(x,y),(x+PCW,y+PCH),tuple(c*0.65*k+0.05 for c in col),-1)
            glow(b,x+PCW/2,y+PCH/2,PCW*0.45,col,0.35*k)
        else: cv2.rectangle(b,(x,y),(x+PCW,y+PCH),(0.06,0.06,0.065),-1)
    # master alarm
    ma=t>wt(4,"warning")-0.15; mx,my=360,1010
    cv2.rectangle(b,(mx-120,my-34),(mx+120,my+34),(0.06,0.06,0.065) if not ma else (0.9*blink,0.08,0.05),-1)
    if ma: glow(b,mx,my,90,(1.8,0.2,0.1),0.6*blink)
    def hud(img):
        d=ImageDraw.Draw(img); f=IF(24,"InterDisplay-Bold") if os.path.exists(IFD+"InterDisplay-Bold.otf") else IF(24)
        for i in range(20):
            x,y=cw_rect(i); on=cw_on(t,i)
            d.text(((x+PCW/2)*K,(y+PCH/2)*K),CW[i],font=f,fill=(30,10,5,255) if on else (90,90,95,255),anchor="mm")
        label(img,"MASTER ALARM",mx*K,my*K,44,(255,235,230) if ma else (120,120,125),stroke=0)
        label(img,"ALARMS EVERYWHERE",540,280,92,WHITE,a=fa(t,wt(4,"warning")-0.1,wt(4,"three")-0.15,0.15,0.15))
        a=fa(t,wt(4,"three")-0.1,99,0.15,0.2)
        label(img,"FUEL CELLS 1·2·3",540,280,92,WHITE,a=a); label(img,"OFFLINE",540,395,100,(255,80,60),a=a,sc=0.8+0.2*spring((t-wt(4,"three"))/0.25))
    if close:
        hud0=hud
        def hud(img):
            a=fa(t,wt(4,"three")-0.1,99,0.15,0.2)
            label(img,"FUEL CELLS 1·2·3",540,280,92,WHITE,a=a); label(img,"OFFLINE",540,395,100,(255,80,60),a=a,sc=0.8+0.2*spring((t-wt(4,"three"))/0.25))
        return b,hud,1.0
    return b,hud,1.02+0.03*sm(u/4)
def sh_panelc(t):
    b,hud,z=sh_panel(t,True)
    # zoom on the fuel-cell row (top row of the panel)
    cx0,cy0=PX0+1.0*(PCW+PGX)+PCW/2,PY0+PCH*0.9
    M=cv2.getRotationMatrix2D((cx0,cy0),0,1.6+0.08*sm((t-wt(4,"All"))/2)); M[0,2]+=360-cx0; M[1,2]+=560-cy0
    b=cv2.warpAffine(b,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    def hud2(img):
        d=ImageDraw.Draw(img); f=IF(40)
        for i in range(20):
            x,y=cw_rect(i); p=M@np.array([x+PCW/2,y+PCH/2,1.0])
            on=cw_on(t,i); d.text((p[0]*K,p[1]*K),CW[i],font=f,fill=(30,10,5,255) if on else (90,90,95,255),anchor="mm")
        hud(img)
    return b,hud2,1.0
def sh_conrad(t):
    u=t-Ls(5); b=np.zeros((h,w,3),F32)+np.array([0.05,0.055,0.06],F32)
    # capsule window with storm rushing past
    win=storm_sky(u+20,vy=500,vy2=800,top=(0.06,0.07,0.09),bot=(0.24,0.25,0.29),flash=0.8*flick(t,Ls(5)+1.0,0.5))
    win=cv2.blur(win,(1,31)); win*=0.85+0.25*sm_np((fbm_cached()-0.3)/0.8)[...,None]
    bolt(win,61,(500,250),(300,640),flick(t,Ls(5)+1.0,0.5),5,2)
    rr=np.roll(RAIN2,int(u*900)%h,0); win+=rr[...,None]*0.18
    m=np.zeros((h,w),F32); cv2.fillPoly(m,[np.array([(160,250),(560,250),(610,620),(110,620)],np.int32)],1.0,cv2.LINE_AA)
    m=cv2.GaussianBlur(m,(0,0),2)[...,None]; b=b*(1-m)+win*m
    cv2.polylines(b,[np.array([(160,250),(560,250),(610,620),(110,620)],np.int32)],True,(0.12,0.12,0.13),14,cv2.LINE_AA)
    # instrument panel below with blinking lights
    cv2.rectangle(b,(0,640),(w,h),(0.09,0.095,0.10),-1)
    g=np.random.default_rng(3)
    for i in range(60):
        x,y=g.uniform(20,w-20),g.uniform(980,1260); ph=g.uniform(0,6)
        y=g.uniform(680,940)
        if math.sin(t*g.uniform(4,10)+ph)>0.2: glow(b,x,y,5,(1.5,0.6,0.15) if g.random()<0.6 else (1.6,0.2,0.1),0.9)
    for i in range(8): cv2.circle(b,(int(70+i*82),1215),22,(0.03,0.03,0.035),-1,cv2.LINE_AA); cv2.circle(b,(int(70+i*82),1215),22,(0.25,0.25,0.27),2,cv2.LINE_AA)
    # radio waveform (oscilloscope)
    cv2.rectangle(b,(70,960),(650,1150),(0.01,0.03,0.02),-1)
    lay=np.zeros((h,w),F32); amp=0.0
    xs=np.arange(80,640); env=(0.25+0.75*abs(math.sin(t*7.3))*(Ls(5)<t<LINES[5]["e"]))
    ys=1055+np.sin(xs*0.11+t*40)*40*env*np.sin(xs*0.013+t*3)+np.sin(xs*0.37+t*65)*14*env
    cv2.polylines(lay,[np.stack([xs,ys],1).astype(np.int32)],False,1.0,2,cv2.LINE_AA)
    b+=(lay*1.2+cv2.GaussianBlur(lay,(0,0),4)*2)[...,None]*np.array([0.3,1.3,0.5],F32)
    def hud(img):
        label(img,"PETE CONRAD",540,290,110,WHITE,a=fa(t,Ls(5)-0.1,99,0.15,0.2))
        label(img,"COMMANDER, APOLLO 12",540,400,56,ORANGE,a=fa(t,Ls(5)+0.2,99,0.15,0.2),stroke=6)
    dx,dy=shake(t,Ls(5)-0.1,5,1.5,17)
    return b,hud,1.03+0.02*math.sin(u*2)
_FBC=[]
def fbm_cached():
    if not _FBC: _FBC.append(fbm((h,w),771,4,3))
    return _FBC[0]
# ---------- Mission Control ----------
GCH="#$%&*+<>?@[]{}/\\|~^=ABCDEFGHJKLMNPQRSTUVWXYZ0123456789"
def crt_text(b,x,y,rows,cols,t,garb,sz=0.5,col=(0.35,1.35,0.55),seed=0,lh=20,cw=11):
    g=np.random.default_rng(seed+(int(t*12) if garb>0 else 0))
    x0=max(0,int(x)-40); y0=max(0,int(y)-lh-10); x1=min(w,int(x+cols*cw*sz*2+60)); y1=min(h,int(y+rows*lh+10))
    if x1<=x0 or y1<=y0: return
    m=np.zeros((y1-y0,x1-x0),np.uint8)
    for r in range(rows):
        if garb>0 and g.random()<garb*0.5: s="".join(g.choice(list(GCH)) for _ in range(cols)); off=int(g.normal(0,6*garb))
        else:
            gg=np.random.default_rng(seed*100+r); vals=[f"{gg.uniform(0,99.9):05.1f}" for _ in range(cols//6)]
            vals=[v if (r+k+int(t*3))%5 else f"{float(v)+np.random.default_rng(int(t*3)+r).uniform(-0.5,0.5):05.1f}" for k,v in enumerate(vals)]
            s=" ".join(vals); off=0
        cv2.putText(m,s,(int(x+off-x0),int(y+r*lh-y0)),cv2.FONT_HERSHEY_PLAIN,sz*2,255,1,cv2.LINE_AA)
    b[y0:y1,x0:x1]+=(m.astype(F32)/255)[...,None]*np.array(col,F32)
def consoles(b,t,garb,cam=0.0):
    # front wall screens
    cv2.rectangle(b,(40,180),(680,470),(0.02,0.03,0.05),-1)
    for i,(x0,x1) in enumerate(((60,250),(265,455),(470,660))):
        k=0.9 if i==1 else 0.6
        cv2.rectangle(b,(x0,200),(x1,440),(0.05*k,0.12*k,0.22*k),-1)
        if i==1:
            xs=np.arange(x0+5,x1-5); ys=320+np.sin((xs-x0)*0.045)*60
            cv2.polylines(b,[np.stack([xs,ys],1).astype(np.int32)],False,(0.9,0.75,0.3),2,cv2.LINE_AA)
            for k_ in range(8): cv2.line(b,(x0+k_*24,205),(x0+k_*24,435),(0.1,0.18,0.3),1)
        else: crt_text(b,x0+8,225,10,16,t,garb*0.8,0.45,(0.35,0.6,1.0),seed=i)
        glow(b,(x0+x1)/2,320,110,(0.15,0.25,0.45),0.35)
    # console rows (perspective)
    for r,(y0,sc) in enumerate(((560,0.55),(700,0.75),(880,1.0),(1120,1.35))):
        cw_=int(150*sc); gap=int(8*sc); n=int(w/(cw_+gap))+2; off=int((r*37+cam*sc*40)%(cw_+gap))
        cv2.rectangle(b,(0,y0),(w,y0+int(120*sc)),(0.10,0.11,0.12),-1)
        cv2.rectangle(b,(0,y0+int(70*sc)),(w,y0+int(78*sc)),(0.18,0.19,0.2),-1)
        for i in range(n):
            x0=i*(cw_+gap)-off; sx0,sy0,sx1,sy1=x0+int(20*sc),y0-int(95*sc),x0+cw_-int(20*sc),y0-int(5*sc)
            cv2.rectangle(b,(x0+int(10*sc),y0-int(110*sc)),(x0+cw_-int(10*sc),y0),(0.13,0.14,0.15),-1)
            gk=1.0
            if garb>0: gk=0.6+0.8*np.random.default_rng(int(t*20)+i*7+r).random()
            cv2.rectangle(b,(sx0,sy0),(sx1,sy1),(0.03*gk,0.20*gk,0.09*gk),-1)
            for k in range(5):
                ly=sy0+int((12+k*15)*sc); lw=int((sx1-sx0-10)*(0.4+0.5*((i*3+k*7+r)%5)/4))
                if garb>0: lw=int((sx1-sx0-10)*np.random.default_rng(int(t*15)+i*13+k+r*5).random()); ly+=int(np.random.default_rng(int(t*15)+k).normal(0,3*garb))
                cv2.line(b,(sx0+5,ly),(sx0+5+lw,ly),(0.3,1.2,0.5),max(1,int(2*sc)))
            glow(b,(sx0+sx1)/2,(sy0+sy1)/2,40*sc,(0.08,0.35,0.15),0.6)
        # heads (silhouettes)
        if r>=1:
            for i in range(n):
                if (i+r)%2: continue
                x0=i*(cw_+gap)-off+cw_//2; cv2.circle(b,(x0,y0+int(40*sc)),int(26*sc),(0.02,0.02,0.025),-1,cv2.LINE_AA)
                cv2.ellipse(b,(x0,y0+int(120*sc)),(int(55*sc),int(60*sc)),0,180,360,(0.02,0.02,0.025),-1,cv2.LINE_AA)
                cv2.ellipse(b,(x0,y0+int(40*sc)),(int(30*sc),int(30*sc)),0,200,340,(0.12,0.12,0.12),max(1,int(3*sc)),cv2.LINE_AA)
def glitch(b,t,amt,seed=0):
    if amt<=0: return b
    g=np.random.default_rng(int(t*30)+seed); out=b.copy()
    for _ in range(int(6*amt)+1):
        y0=int(g.uniform(0,h-40)); hh=int(g.uniform(6,60)); dx=int(g.normal(0,25*amt)); out[y0:y0+hh]=np.roll(out[y0:y0+hh],dx,1)
    d=int(5*amt)+1; out[...,0]=np.roll(out[...,0],d,1); out[...,2]=np.roll(out[...,2],-d,1)
    sn=g.normal(0,0.10*amt,(h//4,w//4)).astype(F32); out+=cv2.resize(sn,(w,h),interpolation=cv2.INTER_NEAREST)[...,None]
    out*= (1-0.12*amt*(np.sin(yy*1.6+t*40)>0))[...,None]
    return out
def sh_mocr(t,clean=False):
    u=t-Ls(6); b=np.zeros((h,w,3),F32)+np.array([0.035,0.045,0.06],F32)
    k=(yy/h)[...,None]; b=b*(1-k*0.4)
    garb=0.0 if clean else sm((t-wt(6,"data")+0.1)/0.4)
    consoles(b,t,garb,u)
    glow(b,360,320,400,(0.06,0.10,0.18),0.4)
    if garb>0: b=glitch(b,t,garb*0.8,3)
    def hud(img):
        if clean:
            a=fa(t,wt(9,"data")-0.1,99,0.15,0.2); label(img,"DATA BACK",540,290,124,(120,255,150),a=a,sc=0.8+0.2*spring((t-wt(9,"data")+0.1)/0.25)); label(img,"MISSION SAVED",540,410,62,WHITE,a=fa(t,wt(9,"back")-0.05,99,0.15,0.2),stroke=6)
        else:
            label(img,"HOUSTON",540,290,120,WHITE,a=fa(t,Ls(6)-0.15,99,0.15,0.2)); label(img,"TELEMETRY: UNREADABLE",540,405,56,(255,90,80),a=fa(t,wt(6,"garbage")-0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.04*sm(u/3) if not clean else 1.04
def sh_aaron(t,close=False):
    u=t-Ls(7); b=np.zeros((h,w,3),F32)+np.array([0.03,0.035,0.045],F32)
    # big CRT
    x0,y0,x1,y1=150,330,690,820
    cv2.rectangle(b,(x0-30,y0-30),(x1+30,y1+40),(0.13,0.135,0.14),-1)
    cv2.rectangle(b,(x0,y0),(x1,y1),(0.015,0.05,0.025),-1)
    garb=0.7
    crt_text(b,x0+18,y0+40,21,40,t,garb,0.62,seed=5,lh=21)
    hl=sm((t-wt(7,"pattern")+0.1)/0.3)
    if hl>0:
        for (ry,rx) in ((7,0),(8,0),(9,0)):
            cv2.rectangle(b,(x0+10,int(y0+40+ry*21-17)),(x1-10,int(y0+40+ry*21+5)),(1.4*hl,0.8*hl,0.1*hl),2,cv2.LINE_AA)
    glow(b,(x0+x1)/2,(y0+y1)/2,260,(0.08,0.35,0.15),0.6)
    sl=(np.sin(yy*2.2)>0.3)[...,None]*0.08; b=b*(1-sl)
    b=glitch(b,t,0.25,8)
    # silhouette with headset (foreground, lower left)
    C=(0.008,0.008,0.01); cx_,cy_=200,1020
    cv2.circle(b,(cx_,cy_),110,C,-1,cv2.LINE_AA); cv2.ellipse(b,(cx_+20,1300),(240,200),0,180,360,C,-1,cv2.LINE_AA)
    cv2.ellipse(b,(cx_,cy_),(118,118),0,200,340,(0.12,0.13,0.13),6,cv2.LINE_AA)
    cv2.line(b,(cx_+100,cy_+20),(cx_+150,cy_+80),(0.10,0.10,0.10),5,cv2.LINE_AA)
    # rim light from CRT
    cv2.ellipse(b,(cx_,cy_),(110,110),0,250,330,(0.10,0.45,0.2),3,cv2.LINE_AA)
    def hud(img):
        label(img,"JOHN AARON",540,280,118,WHITE,a=fa(t,wt(7,"John")-0.15,99,0.15,0.2))
        label(img,"EECOM · POWER SYSTEMS",540,395,58,ORANGE,a=fa(t,wt(7,"Aaron"),wt(7,"pattern")-0.1,0.15,0.15),stroke=6)
        label(img,"SAME FAULT IN A 1968 TEST",540,395,52,ORANGE,a=fa(t,wt(7,"pattern")-0.05,99,0.15,0.2),stroke=6)
    if close:
        M=cv2.getRotationMatrix2D((420,520),-3,1.7+0.1*sm((t-wt(7,"pattern"))/2)); M[0,2]+=360-420; M[1,2]+=600-520
        b=cv2.warpAffine(b,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    return b,hud,1.03+0.05*sm(u/3.5)
def sh_aaronc(t): return sh_aaron(t,True)
def sh_call(t,big=False):
    u=t-Ls(8); b=np.zeros((h,w,3),F32)+np.array([0.03,0.035,0.045],F32)
    if not big:
        consoles(b,t,0.6,u*0.5); b*=0.55
        b=glitch(b,t,0.3,4)
    else:
        consoles(b,t,0.0,u*0.3); b*=0.35
        x0,y0,x1,y1=60,400,660,780
        cv2.rectangle(b,(x0-30,y0-30),(x1+30,y1+40),(0.13,0.135,0.14),-1)
        cv2.rectangle(b,(x0,y0),(x1,y1),(0.015,0.05,0.025),-1)
        glow(b,360,590,240,(0.25,0.15,0.03),0.8)
        sl=(np.sin(yy*2.2)>0.3)[...,None]*0.08; b=b*(1-sl)
    def hud(img):
        if not big:
            g=np.random.default_rng(2)
            for i in range(7):
                a=sm((t-wt(8,"baffled")-i*0.07)/0.15)
                if a>0: label(img,"?",int(g.uniform(120,960)),int(g.uniform(520,1000)),int(g.uniform(80,150)),ORANGE if i%2 else WHITE,a=a,sc=0.7+0.3*spring((t-wt(8,"baffled")-i*0.07)/0.25))
            label(img,"A CALL NO ONE KNEW",540,300,88,WHITE,a=fa(t,Ls(8)-0.1,99,0.15,0.2))
        else:
            ts=wt(8,"SCE")-0.05; s="SCE → AUX"; n=int(np.clip((t-ts)/0.05,0,len(s)))
            txt=s[:n]+("_" if (t*4)%1<0.5 else "")
            label(img,txt,540,885,150,(255,190,60),stroke=0)
            label(img,"SIGNAL CONDITIONING",540,290,80,WHITE,a=fa(t,ts+0.2,99,0.15,0.2))
            label(img,"EQUIPMENT → BACKUP",540,390,64,ORANGE,a=fa(t,ts+0.35,99,0.15,0.2),stroke=6)
    return b,hud,1.02+0.03*sm(u/2)
def sh_callbig(t): return sh_call(t,True)
SWX=[90+i*135 for i in range(5)]; SWY=[100+j*125 for j in range(10)]
def _swpanel():
    g=np.random.default_rng(55); b=np.zeros((h,w,3),F32)+np.array([0.16,0.165,0.17],F32)
    n=cv2.resize(fbm((64,36),781,4,3),(w,h)); b*=(0.88+0.07*n)[...,None]
    m=np.zeros((h,w),np.uint8); LB=["TLM","BMAG","CB","PWR","FDAI","SCS","GMBL","RCS","CMC","O2","H2","FC","INV","BAT","UP TLM","S BAND","PCM","DSKY"]
    for j,y in enumerate(SWY):
        cv2.line(b,(20,y+58),(w-20,y+58),(0.11,0.11,0.12),2)
        for i,x in enumerate(SWX):
            cv2.circle(b,(x,y),27,(0.07,0.07,0.075),-1,cv2.LINE_AA); cv2.circle(b,(x,y),17,(0.55,0.55,0.57),-1,cv2.LINE_AA)
            if (i,j)!=(2,4):
                up=g.random()<0.5; ey=y-48 if up else y+48
                cv2.line(b,(x,y),(x,ey),(0.78,0.78,0.80),11,cv2.LINE_AA); cv2.circle(b,(x,ey),8,(0.88,0.88,0.9),-1,cv2.LINE_AA)
                tx=g.choice(LB); cv2.putText(m,tx,(x-len(tx)*7,y-40),cv2.FONT_HERSHEY_SIMPLEX,0.5,255,1,cv2.LINE_AA)
    cv2.putText(m,"SCE",(SWX[2]-24,SWY[4]-42),cv2.FONT_HERSHEY_SIMPLEX,0.75,255,2,cv2.LINE_AA)
    cv2.putText(m,"AUX",(SWX[2]+30,SWY[4]-30),cv2.FONT_HERSHEY_SIMPLEX,0.45,255,1,cv2.LINE_AA)
    cv2.putText(m,"NORM",(SWX[2]+30,SWY[4]+40),cv2.FONT_HERSHEY_SIMPLEX,0.45,255,1,cv2.LINE_AA)
    b+=(m.astype(F32)/255)[...,None]*np.array([0.75,0.75,0.72],F32)
    return b.astype(F32)
SWP=_swpanel()
def sh_switch(t):
    u=t-Ls(9); tf=wt(9,"flipped")-0.05; k=sm((t-tf)/0.12)
    b=SWP.copy(); cx,cy=SWX[2],SWY[4]
    glow(b,200,250,350,(0.20,0.19,0.17),0.45)
    hl=sm((t-wt(9,"found")+0.05)/0.25)
    if hl>0:
        cv2.circle(b,(cx,cy),62,(1.6*hl,0.85*hl,0.15*hl),3,cv2.LINE_AA); glow(b,cx,cy,70,(0.9,0.45,0.08),0.35*hl)
    L=48; ey=cy+L*math.cos(math.pi*k); thick=11+int(5*math.sin(math.pi*k))
    cv2.line(b,(cx,cy),(cx,int(ey)),(0.82,0.82,0.84),thick,cv2.LINE_AA); cv2.circle(b,(cx,int(ey)),8+int(4*math.sin(math.pi*k)),(0.92,0.92,0.94),-1,cv2.LINE_AA)
    if 0<t-tf<0.35: glow(b,cx,cy-L,14,(1.6,1.5,1.2),1.2*(1-(t-tf)/0.35))
    z=1.0+1.25*sm(u/1.4)
    M=cv2.getRotationMatrix2D((cx,cy),0,z); M[0,2]+=360-cx; M[1,2]+=(600-cy)
    b=cv2.warpAffine(b,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    def hud(img):
        label(img,"ALAN BEAN",540,280,110,WHITE,a=fa(t,Ls(9)-0.1,99,0.15,0.2))
        label(img,"1 SWITCH AMONG HUNDREDS",540,390,52,ORANGE,a=fa(t,wt(9,"obscure")-0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0
def sh_back(t): return sh_mocr(t,True)
# ---------- space ----------
STARS=starfield(81,1200)
def _earth():
    R=1700; cx,cy=360,1900+R*0.0
    d=np.sqrt((xx-cx)**2+(yy-(cy))**2)
    n=fbm((h,w),791,6,3); n2=fbm((h,w),792,6,6)
    land=sm_np((n-1.1)/0.25); cloud=np.clip(sm_np((n2+0.2)/1.6),0,1)**1.5*0.9
    n3=fbm((h,w),793,6,8); col=np.array([0.02,0.10,0.30],F32)*(1-land[...,None])*(0.85+0.15*n3[...,None])+np.array([0.26,0.25,0.15],F32)*(0.75+0.25*n3[...,None])*land[...,None]
    col=col*(1-cloud[...,None])+np.array([0.95,0.96,1.0],F32)*cloud[...,None]
    return col.astype(F32)
ECACHE="earth74.npy"
if os.path.exists(ECACHE): EARTH=np.load(ECACHE)
else: EARTH=_earth(); np.save(ECACHE,EARTH)
def sh_orbit(t):
    u=t-Ls(10); b=STARS.copy()*0.7
    R=1500; cx,cy=360+u*6,2080-u*4
    d=np.sqrt((xx-cx)**2+(yy-cy)**2); m=sm_np((R-d)/3)[...,None]
    lit=np.clip(0.25+0.9*((xx-cx)*-0.4+(yy-cy)*-0.9)/R,0,1.3)[...,None]
    e=np.roll(EARTH,int(u*12),1)*lit
    b=b*(1-m)+e*m
    atm=np.exp(-((d-R)/18)**2)[...,None]*np.array([0.35,0.6,1.3],F32)*lit*1.4; b+=atm
    b+=np.exp(-np.clip(d-R,0,None)/60)[...,None]*(d>R)[...,None]*np.array([0.05,0.12,0.3],F32)
    # spacecraft stack (S-IVB + SLA + CSM) small, side lit
    sx,sy,s=330+u*10,470,3.2
    rocket(b,sx,sy,s,62,37,1.0,upto=47)
    # cut off the lower stages: cover them? (draw only upper part) -> mask region below S-IVB: redraw stars
    glow(b,690,160,30,(1.8,1.7,1.5),1.0)
    mt=wt(10,"Moon")-0.2
    if t>mt: a=sm((t-mt)/0.4); cv2.circle(b,(600,250),int(46*a)+1,(0.75,0.74,0.72),-1,cv2.LINE_AA); glow(b,600,250,60,(0.4,0.4,0.42),0.6*a)
    def hud(img):
        label(img,"EARTH ORBIT",540,290,116,WHITE,a=fa(t,Ls(10)-0.1,99,0.15,0.2))
        label(img,"EVERY SYSTEM CHECKED",540,400,58,ORANGE,a=fa(t,wt(10,"checked"),wt(10,"Moon")-0.25,0.15,0.15),stroke=6)
        label(img,"NEXT STOP: THE MOON",540,400,62,ORANGE,a=fa(t,wt(10,"Moon")-0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u/3
def _moon():
    WSm=1400; n=fbm((WSm,WSm),801,7,4); g=np.random.default_rng(802)
    Hh=n*0.15
    Y,X=np.mgrid[0:WSm,0:WSm].astype(F32)
    for i in range(160):
        cx,cy=g.uniform(0,WSm),g.uniform(0,WSm); r=g.pareto(1.6)*12+6
        if r>200: r=200
        x0,x1,y0,y1=int(max(0,cx-r*1.6)),int(min(WSm,cx+r*1.6)),int(max(0,cy-r*1.6)),int(min(WSm,cy+r*1.6))
        d=np.sqrt((X[y0:y1,x0:x1]-cx)**2+(Y[y0:y1,x0:x1]-cy)**2)/r
        Hh[y0:y1,x0:x1]+=(-(1-d**2)*(d<1)*0.45+np.exp(-((d-1)/0.18)**2)*0.2)*r/70
    gx=cv2.Sobel(Hh,cv2.CV_32F,1,0,ksize=5)
    shade=np.clip(0.66-gx*0.55,0.22,1.15)
    return (np.array([0.55,0.54,0.52],F32)*shade[...,None]).astype(F32)
MCACHE="moon74.npy"
if os.path.exists(MCACHE): MOON=np.load(MCACHE)
else: MOON=_moon(); np.save(MCACHE,MOON)
def moon_ground(cx,cy,scale,hor=0.42):
    WSm=MOON.shape[0]; yh=h*hor; hw=WSm*0.30*scale; near=WSm*0.10*scale
    src=np.float32([[cx-hw,cy-WSm*0.42*scale],[cx+hw,cy-WSm*0.42*scale],[cx+near,cy+WSm*0.08*scale],[cx-near,cy+WSm*0.08*scale]])
    dst=np.float32([[-w*0.3,yh],[w*1.3,yh],[w,h],[0,h]]); M=cv2.getPerspectiveTransform(src,dst)
    g_=cv2.warpPerspective(MOON,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    k=np.clip((yy-yh)/(h-yh),0,1)[...,None]; g_=g_*(0.55+0.6*k)
    b=STARS.copy()*0.8; b=np.where((yy<yh)[...,None],b,g_); return b,yh
def lm(b,x,y,s,a=1.0):
    C=(0.03,0.03,0.035)
    # descent stage gold foil
    cv2.fillPoly(b,[np.array([(x-1.0*s,y-0.95*s),(x+1.0*s,y-0.95*s),(x+0.95*s,y-0.45*s),(x-0.95*s,y-0.45*s)],np.int32)],(0.85,0.62,0.18),cv2.LINE_AA)
    cv2.fillPoly(b,[np.array([(x-1.0*s,y-0.95*s),(x-0.2*s,y-0.95*s),(x-0.2*s,y-0.45*s),(x-0.95*s,y-0.45*s)],np.int32)],(1.15,0.85,0.30),cv2.LINE_AA)
    for sg in (-1,1):
        cv2.line(b,(int(x+sg*0.9*s),int(y-0.6*s)),(int(x+sg*1.6*s),int(y)),(0.75,0.7,0.6),max(2,int(s*0.07)),cv2.LINE_AA)
        cv2.ellipse(b,(int(x+sg*1.6*s),int(y)),(int(0.22*s),int(0.06*s)),0,0,360,(0.7,0.68,0.6),-1,cv2.LINE_AA)
    # ascent stage
    cv2.fillPoly(b,[np.array([(x-0.75*s,y-0.95*s),(x+0.85*s,y-0.95*s),(x+0.9*s,y-1.55*s),(x+0.4*s,y-1.95*s),(x-0.55*s,y-1.95*s),(x-0.85*s,y-1.5*s)],np.int32)],(0.62,0.62,0.64),cv2.LINE_AA)
    cv2.fillPoly(b,[np.array([(x+0.1*s,y-0.95*s),(x+0.85*s,y-0.95*s),(x+0.9*s,y-1.55*s),(x+0.4*s,y-1.95*s),(x+0.1*s,y-1.95*s)],np.int32)],(0.30,0.30,0.32),cv2.LINE_AA)
    cv2.fillPoly(b,[np.array([(x-0.45*s,y-1.75*s),(x-0.15*s,y-1.75*s),(x-0.2*s,y-1.5*s),(x-0.45*s,y-1.5*s)],np.int32)],C,cv2.LINE_AA)
    cv2.line(b,(int(x+0.2*s),int(y-1.95*s)),(int(x+0.35*s),int(y-2.35*s)),(0.7,0.7,0.72),2,cv2.LINE_AA)
    cv2.ellipse(b,(int(x+0.5*s),int(y+0.05*s)),(int(2.2*s),int(0.22*s)),0,0,360,(0.13,0.13,0.13),-1,cv2.LINE_AA)
def surveyor(b,x,y,s):
    G=(0.70,0.70,0.68)
    cv2.ellipse(b,(int(x+0.8*s),int(y+0.05*s)),(int(1.6*s),int(0.18*s)),0,0,360,(0.13,0.13,0.13),-1,cv2.LINE_AA)
    for sg in (-1,0,1): cv2.line(b,(int(x),int(y-0.9*s)),(int(x+sg*1.0*s),int(y)),G,max(2,int(s*0.06)),cv2.LINE_AA)
    cv2.line(b,(int(x),int(y-0.9*s)),(int(x),int(y-2.2*s)),G,max(2,int(s*0.06)),cv2.LINE_AA)
    cv2.fillPoly(b,[np.array([(x-0.9*s,y-2.5*s),(x+0.1*s,y-2.1*s),(x+0.1*s,y-1.9*s),(x-0.9*s,y-2.2*s)],np.int32)],(0.15,0.2,0.4),cv2.LINE_AA)
    cv2.rectangle(b,(int(x-0.3*s),int(y-1.1*s)),(int(x+0.35*s),int(y-0.6*s)),(0.85,0.85,0.82),-1)
    cv2.line(b,(int(x),int(y-2.2*s)),(int(x+0.8*s),int(y-2.6*s)),G,2,cv2.LINE_AA)
def astro(b,x,y,s):
    W_=(0.92,0.92,0.9)
    cv2.circle(b,(int(x),int(y-1.6*s)),int(0.28*s),W_,-1,cv2.LINE_AA); cv2.circle(b,(int(x+0.06*s),int(y-1.6*s)),int(0.17*s),(0.7,0.55,0.2),-1,cv2.LINE_AA)
    cv2.rectangle(b,(int(x-0.3*s),int(y-1.35*s)),(int(x+0.3*s),int(y-0.6*s)),W_,-1)
    cv2.rectangle(b,(int(x-0.45*s),int(y-1.35*s)),(int(x-0.25*s),int(y-0.8*s)),(0.8,0.8,0.78),-1)
    cv2.line(b,(int(x-0.15*s),int(y-0.6*s)),(int(x-0.25*s),int(y)),W_,int(0.2*s),cv2.LINE_AA); cv2.line(b,(int(x+0.15*s),int(y-0.6*s)),(int(x+0.25*s),int(y)),W_,int(0.2*s),cv2.LINE_AA)
    cv2.ellipse(b,(int(x+0.4*s),int(y+0.03*s)),(int(0.7*s),int(0.1*s)),0,0,360,(0.13,0.13,0.13),-1,cv2.LINE_AA)
def sh_moon(t,close=False):
    u=t-Ls(11)
    if not close:
        b,yh=moon_ground(700,800-u*10,1.0,0.40)
        cv2.circle(b,(560,190),46,(0.03,0.05,0.12),-1,cv2.LINE_AA); cv2.ellipse(b,(560,190),(46,46),0,100,260,(0.4,0.6,1.1),-1,cv2.LINE_AA)
        glow(b,560,190,60,(0.1,0.2,0.5),0.4)
        lm(b,220,760,95); surveyor(b,560,620,26)
        for k in range(9):
            px=lerp(300,530,k/8); py=lerp(770,628,k/8)+math.sin(k)*4
            if k<int(sm((t-wt(11,"walking")+0.1)/0.8)*9): cv2.circle(b,(int(px),int(py)),4,(1.2,0.75,0.2),-1,cv2.LINE_AA)
    else:
        b,yh=moon_ground(700,700-u*6,0.55,0.38)
        surveyor(b,420,760,120); astro(b,200,860,85)
    def hud(img):
        if not close:
            label(img,"OCEAN OF STORMS",540,290,96,WHITE,a=fa(t,Ls(11)-0.1,99,0.15,0.2))
            label(img,"NOV 19, 1969",540,395,62,ORANGE,a=fa(t,Ls(11)+0.2,99,0.15,0.2),stroke=6)
            label(img,"INTREPID",330,770,44,WHITE,a=fa(t,Ls(11)+0.3,99,0.2,0.2),stroke=5)
        else:
            label(img,"SURVEYOR 3",540,290,118,WHITE,a=fa(t,wt(11,"robot")-0.15,99,0.15,0.2))
            label(img,"LANDED 1967 · <600 FT AWAY",540,400,54,ORANGE,a=fa(t,wt(11,"Surveyor")-0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*sm(u/4)
def sh_moonclose(t): return sh_moon(t,True)
def cm(b,x,y,s,col=(0.55,0.55,0.58),ang=0.0):
    ca,sa=math.cos(math.radians(ang)),math.sin(math.radians(ang))
    def R(px,py): return (int(x+px*s*ca-py*s*sa),int(y+px*s*sa+py*s*ca))
    cv2.fillPoly(b,[np.array([R(0,-1.0),R(0.95,0.45),R(0.85,0.62),R(-0.85,0.62),R(-0.95,0.45)],np.int32)],col,cv2.LINE_AA)
    cv2.fillPoly(b,[np.array([R(0,-1.0),R(0.95,0.45),R(0.85,0.62),R(0.2,0.62)],np.int32)],tuple(c*0.55 for c in col),cv2.LINE_AA)
    cv2.fillPoly(b,[np.array([R(-0.98,0.45),R(-0.6,0.70),R(0,0.78),R(0.6,0.70),R(0.98,0.45)],np.int32)],tuple(c*0.45 for c in col),cv2.LINE_AA)
    cv2.fillPoly(b,[np.array([R(-0.12,-0.98),R(0.12,-0.98),R(0.1,-1.12),R(-0.1,-1.12)],np.int32)],tuple(c*0.8 for c in col),cv2.LINE_AA)
def sh_reentry(t):
    u=t-Ls(12); b=STARS.copy()*0.25; k=(yy/h)[...,None]
    b+=np.array([0.02,0.03,0.08],F32)*(1-k)+np.array([0.10,0.12,0.30],F32)*k
    x,y,s=380,560,70; ang=0.4
    # plasma trail
    x,y=360+u*12,600+u*16
    for i in range(18):
        glow(b,x-i*20,y-i*30,24+i*5,(1.6,0.55,0.18),0.55*(1-i/18))
    hx,hy=x+0.7*s*math.sin(math.radians(34)),y+0.7*s*math.cos(math.radians(34))
    glow(b,hx,hy,150,(1.2,0.4,0.12),0.6); glow(b,hx+8,hy+8,60,(2.4,1.2,0.4),0.8+0.2*math.sin(t*40))
    cm(b,x,y,s,(0.30,0.27,0.26),-34)
    b=glitch(b,t,0.08,5)
    def hud(img):
        label(img,"THE PARACHUTES",540,290,108,WHITE,a=fa(t,Ls(12)-0.1,99,0.15,0.2))
        label(img,"DAMAGED?",540,410,96,(255,90,80),a=fa(t,wt(12,"damaged")-0.1,99,0.15,0.2),sc=0.8+0.2*spring((t-wt(12,"damaged")+0.1)/0.25))
    return b,hud,1.02+0.04*sm(u/3)
def sh_chutes(t):
    to=wt(12,"opened")-0.25; e=t-to; u=t-Ls(12)
    k=(yy/h)[...,None]; b=np.array([0.14,0.30,0.58],F32)*(1-k)+np.array([0.62,0.74,0.86],F32)*k
    c1=scroll(CL1c,CH-h-500+u*60)*1.35+0.15; a1=scroll(CL1a,CH-h-500+u*60)[...,None]*0.6
    b=b*(1-a1)+np.clip(c1,0,1.2)*a1
    hor=1060; b[hor:]=np.array([0.04,0.18,0.33],F32)
    for i in range(30): cv2.line(b,(0,hor+3+i*i//4),(w,hor+3+i*i//4),(0.10,0.30,0.46),1)
    cx,cy=360+8*math.sin(u),720+6*math.sin(u*1.3); op=spring(e/0.45) if e>0 else 0.0
    sw=0.04*math.sin(u*2.0)
    for j,dx in enumerate((-175,0,175)):
        o_=max(op,0.0); px=cx+dx*(0.25+0.75*o_); py=cy-360+abs(dx)*0.25*o_
        rw=int(20+130*o_); rh=int(70+20*o_)
        for q in range(8):
            col=(0.95,0.95,0.95) if q%2 else (0.92,0.32,0.18)
            cv2.ellipse(b,(int(px),int(py)),(rw,rh),math.degrees(sw),180+q*22.5,180+(q+1)*22.5,col,-1,cv2.LINE_AA)
        cv2.ellipse(b,(int(px),int(py)),(rw,int(rh*0.22)),math.degrees(sw),0,180,(0.55,0.18,0.10),-1,cv2.LINE_AA)
        for q in (-1,-0.5,0,0.5,1): cv2.line(b,(int(px+q*rw),int(py+4)),(int(cx),int(cy-55)),(0.88,0.88,0.88),1,cv2.LINE_AA)
    cm(b,cx,cy,52,(0.66,0.66,0.70))
    if e>0 and e<0.4: glow(b,cx,cy-360,200,(0.6,0.6,0.6),0.4*(1-e/0.4))
    def hud(img):
        a=fa(t,to+0.05,99,0.12,0.2); label(img,"ALL 3 OPENED",540,290,116,WHITE,a=a,sc=0.8+0.2*spring((t-to)/0.25))
        label(img,"SPLASHDOWN · NOV 24",540,400,62,ORANGE,a=fa(t,to+0.3,99,0.15,0.2),stroke=6)
        if e<0: label(img,"NO WAY TO CHECK",540,290,96,(255,90,80),a=fa(t,wt(12,"never")-0.1,to,0.15,0.1))
    return b,hud,1.0+0.03*sm(u/3)
def sh_end(t): return sh_hook(t,True)
SHOTS=[(0.0,sh_hook,"cut"),(Ls(1)-0.25,sh_pad,"zap"),(wt(1,"lifted")-0.1,sh_lift,"cut"),(wt(1,"President")-0.25,sh_nixon,"cut"),
 (Ls(2)-0.2,sh_climb1,"zap"),(wt(2,"16")-0.15,sh_climb2,"cut"),(Ls(3)-0.15,sh_trig0,"cut"),(wt(3,"The")-0.15,sh_trigger,"cut"),
 (Ls(4)-0.15,sh_panel,"cut"),(wt(4,"All")-0.15,sh_panelc,"cut"),(Ls(5)-0.15,sh_conrad,"cut"),(Ls(6)-0.25,sh_mocr,"zap"),(Ls(7)-0.15,sh_aaron,"cut"),
 (wt(7,"pattern")-0.2,sh_aaronc,"cut"),(Ls(8)-0.2,sh_call,"zap"),(wt(8,"SCE")-0.25,sh_callbig,"cut"),(Ls(9)-0.15,sh_switch,"cut"),(wt(9,"data")-0.2,sh_back,"cut"),
 (Ls(10)-0.25,sh_orbit,"zap"),(Ls(11)-0.15,sh_moon,"cut"),(wt(11,"robot")-0.15,sh_moonclose,"cut"),(Ls(12)-0.15,sh_reentry,"cut"),
 (wt(12,"never")-0.15,sh_chutes,"cut"),(Ls(13)-0.3,sh_end,"zap")]
ZAPS=[s[0] for s in SHOTS if s[2]=="zap"]
STRIKES=[T_L0-0.05,T_TW-0.02,S1,S2,wt(3,"triggered")-0.05]
TR=0.2
def shot_at(t):
    i=0
    for k,s in enumerate(SHOTS):
        if t>=s[0]: i=k
    return i
def render_shot(i,t):
    b,hud,z=SHOTS[i][1](t); st=SHOTS[i][0]
    z*=punch(t,[st] if i>0 else [],0.06,0.32)
    dx,dy=0.0,0.0
    for s_ in STRIKES:
        d2=shake(t,s_,9,0.45); dx+=d2[0]; dy+=d2[1]
    d2=shake(t,wt(4,"warning")-0.1,6,0.5); dx+=d2[0]; dy+=d2[1]
    return camera(b,z,0.5,0.47,dx,dy),hud
def zap(b1,b2,u,seed):
    """lightning-strike transition: bolt tears across, white blowout, RGB split + glitch slices; cut at the flash"""
    out=(b1 if u<0.5 else b2).copy()
    fl=math.exp(-((u-0.5)/0.13)**2)
    g=np.random.default_rng(seed); x0=g.uniform(150,570); x1=g.uniform(100,620)
    bI=max(0.0,1-abs(u-0.48)/0.3)
    if bI>0: bolt(out,seed,(x0,-30),(x1,h+30),bI*1.3,9,3)
    d=int(18*math.exp(-((u-0.5)/0.22)**2))
    if d>0:
        out[...,0]=np.roll(out[...,0],d,1); out[...,2]=np.roll(out[...,2],-d,1)
        gg=np.random.default_rng(seed+int(u*20))
        for _ in range(5):
            y0=int(gg.uniform(0,h-50)); hh=int(gg.uniform(8,50)); out[y0:y0+hh]=np.roll(out[y0:y0+hh],int(gg.normal(0,40*d/18)),1)
    out=out*(1-fl*0.45)+np.array([1.5,1.6,1.9],F32)*fl*0.6
    return out
def compose(t,fi=None):
    if fi is None: fi=int(round(t*30))
    i=shot_at(max(t,0)); nxt=SHOTS[i+1] if i+1<len(SHOTS) else None; huds=[]
    if nxt and nxt[2]=="zap" and t>nxt[0]-TR:
        u=(t-(nxt[0]-TR))/(2*TR); b1,h1=render_shot(i,t); b2,h2=render_shot(i+1,t); b=zap(b1,b2,u,i*13+5); huds=[h1] if u<0.3 else []
    elif SHOTS[i][2]=="zap" and t<SHOTS[i][0]+TR and i>0:
        u=(t-(SHOTS[i][0]-TR))/(2*TR); b1,h1=render_shot(i-1,t); b2,h2=render_shot(i,t); b=zap(b1,b2,u,(i-1)*13+5); huds=[h2] if u>0.75 else []
    else:
        b,h1=render_shot(i,t); huds=[h1]
    b=post(b,bloom=0.5,thr=0.70,tint=(0.98,1.0,1.04))
    img=to_img(b,fi)
    for hf in huds:
        if hf: hf(img)
    ha=1-sm((t-(Ls(1)-0.45))/0.25) if t<Ls(1) else sm((t-(TOTAL-0.55))/0.3)
    if ha>0.01:
        hook_title(img,[("HIT BY LIGHTNING",WHITE)],a=ha,y=250,size=124)
        s2=T_TW-0.05
        if t>=s2 or t>TOTAL-0.55:
            a2=ha*(sm((t-s2)/0.08) if t<Ls(1) else 1.0); sc=0.7+0.3*spring((t-s2)/0.22) if t<Ls(1) else 1.0
            hook_title(img,[("TWICE",ORANGE)],a=a2,y=390,size=150,sc=sc)
    return finish(img,CAP,t)
if __name__=="__main__":
    import time
    for tt in map(float,sys.argv[1:]):
        t0=time.time(); compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85); print(tt,round(time.time()-t0,2))
