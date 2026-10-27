import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid71"); sys.path.insert(0,"/home/claude/toolkit")
from pro import *
from PIL import Image, ImageDraw
T,LINES,SC,TOTAL=load("timeline.json")
CAP=Captions(LINES); WD=CAP.W
def wt(li,sub,o=0.0): return word_t(WD,li,sub,o)
def Ls(i): return LINES[i]["s"]
def sm_np(x): x=np.clip(x,0,1); return x*x*(3-2*x)
# ================= cinematic documentary CG: Siberian taiga 1908, airburst, archival 1927 =================
G=np.random.default_rng(71)
# ---------- top-down blast field (static, 2048^2) ----------
FS=2048; FC=(FS*0.5,FS*0.5)
def _field():
    gx=fbm((FS//4,FS//4),3,6,4); gy=fbm((FS//4,FS//4),4,5,10)
    ground=np.clip(0.5+0.18*gx+0.08*gy,0,1)
    ground=cv2.resize(ground,(FS,FS),interpolation=cv2.INTER_CUBIC)[...,None]
    img=np.array([0.10,0.09,0.06],np.float32)+ground*np.array([0.16,0.15,0.09],np.float32)
    bog=cv2.resize(np.clip(fbm((64,64),5,4,3),0,None),(FS,FS))
    yy2,xx2=np.mgrid[0:FS,0:FS].astype(np.float32); dc=np.sqrt((xx2-FC[0])**2+(yy2-FC[1])**2)
    bm=(bog>0.9)*(dc<330)
    pass
    lay=np.zeros((FS,FS,3),np.float32); sh=np.zeros((FS,FS),np.float32)
    g=np.random.default_rng(9)
    for i in range(16000):
        r=np.sqrt(g.uniform(0.04,1.0))*FS*0.72; a=g.uniform(0,2*np.pi)
        a2=a+0.12*math.sin(a*2+1.3)+g.normal(0,0.05)  # butterfly-ish skew
        x=FC[0]+r*math.cos(a); y=FC[1]+r*math.sin(a)*0.92
        L=g.uniform(26,58)*(1.0 if r>260 else 0.0)
        if L==0: continue
        x2=x+L*math.cos(a2); y2=y+L*math.sin(a2)
        c=g.uniform(0.45,0.75)
        cv2.line(sh,(int(x+3),int(y+4)),(int(x2+3),int(y2+4)),1.0,3,cv2.LINE_AA)
        cv2.line(lay,(int(x),int(y)),(int(x2),int(y2)),(c*0.62,c*0.55,c*0.45),2,cv2.LINE_AA)
    img=img*(1-0.55*cv2.GaussianBlur(sh,(0,0),2)[...,None])
    m=(lay.sum(2)>0)[...,None]; img=np.where(m,lay,img)
    for i in range(500):  # standing stripped trunks at the centre (seen from above: dots + shadows)
        r=np.sqrt(g.uniform(0,1))*240; a=g.uniform(0,2*np.pi); x=FC[0]+r*math.cos(a); y=FC[1]+r*math.sin(a)
        cv2.line(img,(int(x),int(y)),(int(x+14),int(y+22)),(0.03,0.03,0.03),2,cv2.LINE_AA); cv2.circle(img,(int(x),int(y)),3,(0.55,0.5,0.42),-1,cv2.LINE_AA)
    return img.astype(np.float32)
CACHE="field71.npy"
FIELD=np.load(CACHE) if os.path.exists(CACHE) else _field()
if not os.path.exists(CACHE): np.save(CACHE,FIELD)
def field_view(cx,cy,scale,tilt=0.0,rot=0.0,haze=0.0,sky=None,hor=0.30):
    """top-down (tilt=0) or oblique aerial (tilt>0) camera over the blast field"""
    if tilt<=0:
        M=cv2.getRotationMatrix2D((cx,cy),rot,1/scale); M[0,2]+=w/2-cx; M[1,2]+=h/2-cy
        return cv2.warpAffine(FIELD,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    # oblique: map a trapezoid of the field to the screen below the horizon
    yh=int(h*hor); hw=FS*0.30*scale; near=FS*0.10*scale
    src=np.float32([[cx-hw,cy-FS*0.42*scale],[cx+hw,cy-FS*0.42*scale],[cx+near,cy+FS*0.08*scale],[cx-near,cy+FS*0.08*scale]])
    dst=np.float32([[-w*0.2,yh],[w*1.2,yh],[w,h],[0,h]])
    Mp=cv2.getPerspectiveTransform(src,dst)
    out=cv2.warpPerspective(FIELD,Mp,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    k=np.clip((yy-yh)/(h-yh),0,1)[...,None]; hz=np.exp(-k*4.0)*0.9
    skyc=sky if sky is not None else sky_grad(DAWN)
    hc=np.array([0.75,0.55,0.40],np.float32)
    out=out*(1-hz)+hc*hz*0.9
    return np.where((yy<yh)[...,None],skyc,out)
# ---------- skies, forest, cabin ----------
DAWN=((0.05,0.08,0.20),(0.55,0.42,0.40),(1.05,0.62,0.32)); NIGHTGLOW=((0.04,0.05,0.12),(0.30,0.32,0.40),(0.85,0.70,0.55))
def sky_grad(p,hor=0.55):
    k=np.clip(yy/(h*hor),0,1)[...,None]; a,b,c=[np.array(x,np.float32) for x in p]
    return np.where(k<0.6,a+(b-a)*(k/0.6),b+(c-b)*((k-0.6)/0.4))*np.ones((h,w,3),np.float32)
def ridge(y0,amp,seed,step=6):
    g=np.random.default_rng(seed); xs=np.arange(0,w+step,step); n=np.cumsum(g.normal(0,1,len(xs))); n=(n-n.mean())/(n.std()+1e-6)
    n=cv2.GaussianBlur(n.reshape(1,-1).astype(np.float32),(0,0),3).ravel(); return np.interp(np.arange(w),xs,y0+amp*n)
def forest_mask(y0,size,seed,dens=1.0):
    g=np.random.default_rng(seed); m=np.zeros((h,w),np.float32); base=ridge(y0,size*0.6,seed)
    x=-20
    while x<w+20:
        hh=size*g.uniform(0.7,1.3); b=base[int(min(max(x,0),w-1))]
        pts=[(x,b-hh)]
        for k in range(6):
            yk=b-hh+hh*(k+1)/6; wk=hh*0.20*(k+1)/6+2
            pts=[(x-wk,yk)]+pts+[(x+wk,yk)]
        cv2.fillPoly(m,[np.array(pts,np.int32)],1.0,cv2.LINE_AA); x+=g.uniform(3,9)/dens*size/30
    m[np.arange(h)[:,None]>base[None,:]]=1.0
    return m
FM=[forest_mask(h*0.58,30,1),forest_mask(h*0.66,55,2),forest_mask(h*0.80,110,3)]
POLES=np.zeros((h,w),np.float32)
for i in range(70):
    x=G.uniform(-10,w+10); b=h*G.uniform(0.62,1.05); hh=G.uniform(0.25,0.55)*h; th=max(2,int(G.uniform(2,9)*(b/h)))
    cv2.line(POLES,(int(x),int(b)),(int(x+G.normal(0,4)),int(b-hh)),1.0,th,cv2.LINE_AA)
    if G.random()<0.5: cv2.line(POLES,(int(x),int(b-hh*0.7)),(int(x+G.uniform(-25,25)),int(b-hh*0.8)),1.0,max(1,th//2),cv2.LINE_AA)
def taiga(t,sky=None,fog=(0.80,0.58,0.45),light=1.0):
    b=sky.copy() if sky is not None else sky_grad(DAWN)
    cols=[np.array([0.20,0.16,0.18],np.float32),np.array([0.09,0.08,0.09],np.float32),np.array([0.025,0.025,0.03],np.float32)]
    for k,(m,c) in enumerate(zip(FM,cols)):
        b=b*(1-m[...,None])+c*light*m[...,None]
        if k<2:
            f=np.exp(-((yy-h*(0.60+0.07*k))/(40+20*k))**2)[...,None]*np.array(fog,np.float32)*0.35; b=b+f
    return b
SMK=fbm((h,w*2),77,6,3,aspect=2)
def smoke(b,t,a=0.5,col=(0.35,0.30,0.28),y0=0.3,spd=12):
    s=np.roll(SMK,-int(t*spd),1)[:,:w]; m=np.clip(s*0.5+0.1,0,1)*np.clip((yy-h*y0)/(h*0.3),0,1)*a
    return b*(1-m[...,None])+np.array(col,np.float32)*m[...,None]
def fireball(b,x,y,ang,L,a=1.0,size=10):
    lay=np.zeros_like(b); dx,dy=math.cos(ang),math.sin(ang)
    for k in range(40):
        u=k/40; px=x-dx*L*u; py=y-dy*L*u; r=size*(1-u)*1.2+2
        cv2.circle(lay,(int(px),int(py)),int(r),(1.0*(1-u)+0.3*u,0.55*(1-u)+0.25*u,0.25*(1-u)+0.2*u),-1,cv2.LINE_AA)
    b+=cv2.GaussianBlur(lay,(0,0),4)*a*1.2+cv2.GaussianBlur(lay,(0,0),14)*a
    glow(b,x,y,size*2.2,(3.0,2.2,1.4),a); glow(b,x,y,size*7,(1.2,0.6,0.25),a*0.7)
def cabin(b,x,y,s,shake=(0,0),win=1.0,man=None):
    dx,dy=shake; x+=dx; y+=dy
    body=np.array([(x,y),(x+s*2.2,y),(x+s*2.2,y-s*1.0),(x+s*1.1,y-s*1.65),(x,y-s*1.0)],np.int32)
    cv2.fillPoly(b,[body],(0.03,0.025,0.025),cv2.LINE_AA)
    for k in range(5): cv2.line(b,(int(x),int(y-s*0.2*k)),(int(x+s*2.2),int(y-s*0.2*k)),(0.07,0.05,0.04),2,cv2.LINE_AA)
    cv2.rectangle(b,(int(x+s*1.4),int(y-s*0.75)),(int(x+s*1.8),int(y-s*0.4)),(1.0*win,0.6*win,0.25*win),-1)
    cv2.rectangle(b,(int(x-s*0.6),int(y-s*0.05)),(int(x+s*2.4),int(y+s*0.06)),(0.04,0.03,0.03),-1)
    if man is not None:
        mx,my,ang=man; c=(0.02,0.02,0.02)
        def R(px,py): return (int(mx+px*math.cos(ang)-py*math.sin(ang)),int(my+px*math.sin(ang)+py*math.cos(ang)))
        cv2.circle(b,R(0,-s*0.62),int(s*0.11),c,-1,cv2.LINE_AA)
        cv2.fillPoly(b,[np.array([R(-s*0.12,-s*0.5),R(s*0.12,-s*0.5),R(s*0.15,-s*0.15),R(-s*0.15,-s*0.15)],np.int32)],c,cv2.LINE_AA)
        cv2.line(b,R(-s*0.1,-s*0.15),R(s*0.25,-s*0.1),c,int(s*0.08),cv2.LINE_AA); cv2.line(b,R(s*0.25,-s*0.1),R(s*0.25,s*0.15),c,int(s*0.07),cv2.LINE_AA)
        cv2.line(b,R(-s*0.15,-s*0.15),R(-s*0.2,s*0.15),c,int(s*0.05),cv2.LINE_AA)  # stool
def cabin_man(b,man,s):
    mx,my,ang=man; c=(0.015,0.012,0.012)
    def R(px,py): return (int(mx+px*math.cos(ang)-py*math.sin(ang)),int(my+px*math.sin(ang)+py*math.cos(ang)))
    cv2.circle(b,R(0,-s*0.66),int(s*0.10),c,-1,cv2.LINE_AA)
    cv2.fillPoly(b,[np.array([R(-s*0.13,-s*0.55),R(s*0.13,-s*0.55),R(s*0.16,-s*0.2),R(-s*0.16,-s*0.2)],np.int32)],c,cv2.LINE_AA)
    cv2.line(b,R(-s*0.1,-s*0.22),R(s*0.24,-s*0.2),c,int(s*0.09),cv2.LINE_AA); cv2.line(b,R(s*0.24,-s*0.2),R(s*0.26,0),c,int(s*0.08),cv2.LINE_AA)
    cv2.line(b,R(-s*0.12,-s*0.48),R(s*0.18,-s*0.36),c,int(s*0.05),cv2.LINE_AA)
    cv2.line(b,R(-s*0.18,-s*0.2),R(-s*0.18,0),c,int(s*0.04),cv2.LINE_AA); cv2.line(b,R(s*0.02,-s*0.2),R(s*0.02,0),c,int(s*0.04),cv2.LINE_AA)
def newspaper(b,t):
    u=sm((t-wt(3,"some")+0.05)/0.5); y0=h*(1.05-0.42*u)
    P=np.array([(w*0.06,y0),(w*0.98,y0-60),(w*1.02,y0+520),(w*0.02,y0+560)],np.float32)
    cv2.fillPoly(b,[P.astype(np.int32)],(0.82,0.76,0.62),cv2.LINE_AA)
    def Q(a_,c_): return (int(P[0][0]+(P[1][0]-P[0][0])*a_+(P[3][0]-P[0][0])*c_),int(P[0][1]+(P[1][1]-P[0][1])*a_+(P[3][1]-P[0][1])*c_))
    cv2.line(b,Q(0.08,0.10),Q(0.92,0.10),(0.12,0.10,0.09),16,cv2.LINE_AA)
    cv2.line(b,Q(0.08,0.17),Q(0.92,0.17),(0.25,0.22,0.2),2,cv2.LINE_AA)
    for col in range(3):
        for k in range(12):
            a0=0.08+col*0.29; cv2.line(b,Q(a0,0.24+k*0.055),Q(a0+0.25,0.24+k*0.055),(0.35,0.32,0.28),3,cv2.LINE_AA)
def city(b,glowk=1.0):
    g=np.random.default_rng(12); x=0; base=h*0.84
    while x<w:
        bw=g.uniform(40,110); bh=g.uniform(40,150); c=(0.02,0.02,0.03)
        cv2.rectangle(b,(int(x),int(base-bh)),(int(x+bw),int(h)),c,-1)
        if g.random()<0.4: cv2.fillPoly(b,[np.array([(x,base-bh),(x+bw/2,base-bh-bw*0.5),(x+bw,base-bh)],np.int32)],c,cv2.LINE_AA)
        if g.random()<0.15: cv2.fillPoly(b,[np.array([(x+bw*0.4,base-bh),(x+bw*0.5,base-bh-150),(x+bw*0.6,base-bh)],np.int32)],c,cv2.LINE_AA)
        for k in range(int(bh/30)):
            if g.random()<0.25: cv2.rectangle(b,(int(x+g.uniform(8,bw-16)),int(base-bh+20+k*30)),(int(x+g.uniform(8,bw-16))+7,int(base-bh+30+k*30)),(0.9,0.6,0.25),-1)
        x+=bw+g.uniform(0,6)
def reader(b,x,y,s,lit=1.0):
    rc=(0.55,0.47,0.40); e=max(3,int(s*0.02))
    cv2.circle(b,(int(x),int(y-s*1.55)),int(s*0.2)+e,rc,-1,cv2.LINE_AA)
    cv2.fillPoly(b,[np.array([(x-s*0.3-e,y-s*1.3-e),(x+s*0.3+e,y-s*1.3-e),(x+s*0.35+e,y),(x-s*0.35-e,y)],np.int32)],rc,cv2.LINE_AA)
    c=(0.015,0.015,0.02)
    cv2.circle(b,(int(x),int(y-s*1.55)),int(s*0.2),c,-1,cv2.LINE_AA)
    cv2.fillPoly(b,[np.array([(x-s*0.3,y-s*1.3),(x+s*0.3,y-s*1.3),(x+s*0.35,y),(x-s*0.35,y)],np.int32)],c,cv2.LINE_AA)
    paper=np.array([(x+s*0.05,y-s*1.25),(x+s*0.85,y-s*1.4),(x+s*0.9,y-s*0.8),(x+s*0.1,y-s*0.7)],np.int32)
    cv2.fillPoly(b,[paper],(0.75*lit,0.72*lit,0.62*lit),cv2.LINE_AA)
    for k in range(5): cv2.line(b,(int(x+s*0.18),int(y-s*(1.2-0.09*k))),(int(x+s*0.8),int(y-s*(1.33-0.09*k))),(0.3*lit,0.28*lit,0.25*lit),1,cv2.LINE_AA)
SCR=G.uniform(0,1,(60,3))
def archival(b,t,fi):
    lum=b.mean(2,keepdims=True); s=lum*np.array([1.15,0.95,0.70],np.float32)*1.1+np.array([0.05,0.035,0.02],np.float32)
    s=cv2.GaussianBlur(s,(0,0),1.1)
    g=np.random.default_rng(fi%7)
    for i in range(6):
        x=int(g.uniform(0,w)); cv2.line(s,(x,0),(x+int(g.uniform(-8,8)),h),(0.85,0.75,0.6),1,cv2.LINE_AA)
    for i in range(30): cv2.circle(s,(int(g.uniform(0,w)),int(g.uniform(0,h))),int(g.uniform(1,3)),(0.05,0.04,0.03),-1)
    s=s*(1-0.6*np.clip(((xx/w-0.5)**2+(yy/h-0.5)**2)*2.5,0,1))[...,None]*(0.95+0.05*math.sin(t*40))
    return s

# ---------- ground-level flattened forest (static perspective render) ----------
YH=0.42*h
def _fallen():
    g=np.random.default_rng(1908); f=w*0.95; Hc=5.0
    k=np.clip((yy-YH)/(h-YH),0,1)[...,None]
    gt=fbm((h,w),41,6,4)[...,None]
    FOG=np.array([0.40,0.31,0.26])
    img=np.array([0.36,0.28,0.23],np.float32)*(1-k**0.5)+np.array([0.10,0.075,0.055],np.float32)*k**0.5
    img=img*(1+0.12*gt)
    rid=ridge(YH-4,4,44,8); mask=(yy>=rid[None,:]).astype(np.float32)
    logs=[]
    EX,EZ=-260.0,700.0
    for i in range(700):
        Z=7.5+190*g.random()**1.25; X=g.uniform(-1.0,1.0)*Z*0.8
        L=g.uniform(6,18)*(0.5 if g.random()<0.2 else 1.0); phi=math.atan2(Z-EZ,X-EX)+g.normal(0,0.07); r=g.uniform(0.07,0.14)
        logs.append((Z,X,L,phi,r))
    logs.sort(key=lambda q:-q[0])
    def P(X_,Z_): return (w/2+X_*f/Z_, YH+Hc*f/Z_)
    for Z,X,L,phi,r in logs:
        X2=X+L*math.cos(phi); Z2=max(3.0,Z+L*math.sin(phi))
        x0,y0=P(X,Z); x1,y1=P(X2,Z2); Zm=(Z+Z2)/2; th=max(1,int(round(2*r*f/Zm)))
        fog=1-math.exp(-Zm/80)
        pale=np.array([0.52,0.47,0.40])*(1-fog)+FOG*fog; shd=np.array([0.05,0.04,0.03])*(1-fog)+FOG*0.8*fog
        o=max(1,th//2)
        cv2.line(img,(int(x0),int(y0+o)),(int(x1),int(y1+o)),tuple(float(v) for v in shd),th+1,cv2.LINE_AA)
        cv2.line(img,(int(x0),int(y0)),(int(x1),int(y1)),tuple(float(v) for v in pale),th,cv2.LINE_AA)
        if th>=3: cv2.line(img,(int(x0),int(y0+th*0.3)),(int(x1),int(y1+th*0.3)),tuple(float(v)*0.55 for v in pale),max(1,th//3),cv2.LINE_AA)
    for i in range(22):  # snapped stumps
        Z=9+150*g.random()**1.3; X=g.uniform(-1,1)*Z*0.7; x,y=P(X,Z); hh=g.uniform(1.0,3.0)*f/Z; th=max(1,int(0.3*f/Z))
        fog=1-math.exp(-Z/80); c=tuple(float(v) for v in np.array([0.62,0.56,0.47])*(1-fog)+FOG*fog)
        cv2.line(img,(int(x),int(y)),(int(x),int(y-hh)),c,th,cv2.LINE_AA)
    return img.astype(np.float32),mask
FALLEN,FMASK=_fallen()
def fallen(sky,t,z=1.0):
    b=sky*(1-FMASK[...,None])+FALLEN*FMASK[...,None]
    return b
# ---------- shots ----------
def sh_hook(t,k=0):
    z=1.0+0.05*sm(t/4.5)
    sky=sky_grad(DAWN,0.42); b=fallen(sky,t)
    glow(b,w*0.78,YH-4,26,(2.4,1.5,0.7),0.9); glow(b,w*0.78,YH,170,(0.8,0.45,0.22),0.55)
    b=smoke(b,t,0.30,(0.55,0.43,0.36),0.20,14)
    return b,None,z
def sh_center(t):
    u=t-(wt(0,"and")-0.05); b=field_view(FC[0],FC[1],2.4-0.5*sm(u/1.2),rot=6*u); b=smoke(b,t,0.2,(0.4,0.36,0.32),0.0,10)
    return b,None,1.0
def sh_trading(t,phase=0):
    u=t-Ls(1); flash=sm((u+0.2)/1.4) if phase==0 else 1.0
    sky=sky_grad(((0.06,0.07,0.16),(0.5+0.8*flash,0.45+0.5*flash,0.4+0.2*flash),(1.0+1.5*flash,0.75+0.9*flash,0.45+0.5*flash)),0.62)
    b=sky.copy()
    for k_,(m_,c_) in enumerate(zip(FM[:2],[(0.30,0.24,0.24),(0.16,0.13,0.13)])): b=b*(1-m_[...,None])+np.array(c_,np.float32)*(1-0.5*flash)*m_[...,None]
    glow(b,w*0.62,h*0.42,30+70*flash,(3.0,2.4,1.5),0.6+1.0*flash)
    sx,sy=(0,0)
    man=(w*0.62,h*0.875,0.0)
    if phase==1:
        v=t-Ls(2); sx,sy=shake(t,wt(2,"blast"),18,0.8)
        dust=sm((v-0.25)/0.6); b=b*(1-0.5*dust)+np.array([0.45,0.35,0.25],np.float32)*0.5*dust*np.clip(1-(yy/h-0.5),0,1)[...,None]
        k=sm((t-wt(2,"threw"))/0.35); man=(w*(0.62-0.22*k),h*(0.875-0.05*math.sin(math.pi*k)),-1.3*k)
    cv2.rectangle(b,(0,int(h*0.875)),(w,h),(0.03,0.025,0.02),-1)
    cabin(b,-w*0.18,h*0.875,200,(sx*0.5,sy*0.5),win=0.6,man=None)
    cabin_man(b,man,230)
    def hud(img):
        if phase==0: label(img,"VANAVARA · 65 KM AWAY",540,300,58,(255,220,170),a=fa(t,Ls(1)+0.1,99,0.2,0.2),stroke=6)
    return b,hud,1.02+0.02*u
def sh_glow(t,close=0):
    sky=sky_grad(((0.02,0.03,0.08),(0.28,0.30,0.40),(0.95,0.78,0.60)),0.70)
    b=sky.copy(); s=np.roll(SMK,-int(t*6),1)[:,:w]
    b+=np.clip(s*0.3+0.15,0,1)[...,None]*np.clip(1-yy/(h*0.7),0,1)[...,None]*np.array([0.25,0.28,0.35],np.float32)
    city(b)
    if close: newspaper(b,t)
    if close: b=camera(b,1.0,0.5,0.5)
    def hud(img):
        a=fa(t,wt(3,"midnight")-0.1,99,0.12,0.2)
        if a>0: label(img,"12:00 AM",540,330,150,ORANGE,a=a,sc=0.85+0.15*spring((t-wt(3,"midnight")+0.1)/0.2))
        else: label(img,"JULY 1908",540,330,96,WHITE,a=fa(t,Ls(3),99,0.2,0.2))
    return b,hud,1.0+0.03*(t-Ls(3))/3+(0.25*sm((t-wt(3,"some"))/0.5) if close else 0)
def sh_1927(t,fi=0):
    sky=sky_grad(((0.55,0.55,0.55),(0.72,0.72,0.72),(0.80,0.80,0.80)),0.42)
    b=camera(fallen(sky,t),1.25,0.30,0.55)
    b=archival(b,t,fi)
    def hud(img):
        label(img,"LEONID KULIK",540,300,104,WHITE,a=fa(t,Ls(4)+0.15,99,0.2,0.2))
        label(img,"19 YEARS LATER",540,410,64,(255,210,140),a=fa(t,wt(4,"1927"),99,0.2,0.2),stroke=6)
    return b,hud,1.0+0.03*(t-Ls(4))
def sh_map(t,close=0):
    u=t-Ls(5)+0.1; sc=lerp(2.2,1.45,sm(u/2.5)) if not close else lerp(0.9,0.6,sm((t-wt(5,"pointing"))/1.2))
    b=field_view(FC[0],FC[1],sc,rot=8*u)
    def hud(img):
        if not close:
            a=fa(t,wt(5,"giant")-0.1,99,0.15,0.2)
            label(img,"AREA > LONDON",540,320,108,ORANGE,a=a,sc=0.85+0.15*spring((t-wt(5,"giant")+0.1)/0.2)); label(img,"2,150 KM²",540,430,60,WHITE,a=a,stroke=6)
        else:
            d=ImageDraw.Draw(img); cx,cy=540,int(h*0.5*K); a=sm((t-wt(5,"pointing"))/0.3)
            for k in range(8):
                an=k*math.pi/4+0.2; r0=150; r1=150+260*sm((t-wt(5,"pointing")-k*0.03)/0.5)
                if r1>r0+10:
                    x0_,y0_,x1_,y1_=cx+r0*math.cos(an),cy+r0*math.sin(an),cx+r1*math.cos(an),cy+r1*math.sin(an)
                    d.line((x0_,y0_,x1_,y1_),fill=(255,168,28,int(230*a)),width=9)
                    hx,hy=math.cos(an),math.sin(an); d.polygon([(x1_+hx*26,y1_+hy*26),(x1_-hy*16,y1_+hx*16),(x1_+hy*16,y1_-hx*16)],fill=(255,168,28,int(230*a)))
            d.ellipse((cx-16,cy-16,cx+16,cy+16),fill=(255,255,255,int(255*a)))
    return b,hud,1.0
def sh_poles(t):
    sky=sky_grad(((0.30,0.33,0.38),(0.62,0.62,0.62),(0.78,0.74,0.68)),0.75); b=sky.copy()
    b=b*(1-FM[0][...,None])+np.array([0.35,0.36,0.38],np.float32)*FM[0][...,None]
    fogm=np.exp(-((yy-h*0.68)/120)**2)[...,None]*0.35; b=b*(1-fogm)+np.array([0.75,0.74,0.72],np.float32)*fogm
    b=b*(1-POLES[...,None]*0.92)+np.array([0.06,0.055,0.05],np.float32)*POLES[...,None]*0.92
    cv2.rectangle(b,(0,int(h*0.95)),(w,h),(0.05,0.05,0.045),-1)
    def hud(img): label(img,"STILL STANDING",540,320,112,WHITE,a=fa(t,wt(6,"standing")-0.1,99,0.15,0.2),sc=0.85+0.15*spring((t-wt(6,"standing")+0.1)/0.2))
    return b,hud,1.0+0.02*(t-Ls(6))
def sh_rock(t):
    u=t-Ls(7)+0.3; b=sky_grad(((0.01,0.02,0.07),(0.10,0.15,0.35),(0.6,0.45,0.4)),0.9)
    b+=np.clip(starfield(3,500),0,2)*np.clip(1-yy/(h*0.7),0,1)[...,None]*0.6
    b=b*(1-FM[0][...,None])+np.array([0.02,0.02,0.03],np.float32)*FM[0][...,None]
    p=sm(u/1.8); fireball(b,w*(0.95-0.6*p),h*(0.05+0.32*p),math.atan2(0.32,-0.6),300+200*p,1.0,12+6*p)
    return b,None,1.0+0.03*u
def sh_burst(t):
    u=t-wt(7,"exploded")+0.05; b=taiga(t,sky_grad(((0.08,0.08,0.16),(0.55,0.38,0.32),(0.95,0.60,0.38)),0.6),light=0.6)
    e=eout(u/0.5); glow(b,w*0.55,h*0.24,15+70*e,(3.0,2.2,1.4),1.6*(1-0.4*sm(u/2))); glow(b,w*0.55,h*0.24,200*e+20,(1.0,0.5,0.22),0.6)
    ring=np.exp(-((np.sqrt((xx-w*0.55)**2+((yy-h*0.24)*1.0)**2)-(80+600*sm(u/1.4)))/14)**2)*(1-sm(u/1.6))
    b+=ring[...,None]*np.array([1.2,1.0,0.8],np.float32)*0.8
    def hud(img): label(img,"5–10 KM UP",540,880,96,WHITE,a=fa(t,wt(7,"miles")-0.1,99,0.15,0.2))
    return b,hud,1.0+0.04*sm(u/2)
def sh_mega(t):
    u=t-wt(7,"hundreds"); b=np.zeros((h,w,3),np.float32)+np.array([0.03,0.025,0.03],np.float32)
    glow(b,w*0.5,h*0.45,40+220*eout(u/0.5),(2.4,1.5,0.8),1.6); glow(b,w*0.5,h*0.45,420,(0.6,0.3,0.15),0.6)
    glow(b,w*0.18,h*0.78,6,(2.0,1.5,1.0),1.4)
    def hud(img):
        a=fa(t,wt(7,"hundreds")-0.05,99,0.15,0.2)
        label(img,"10–15 MEGATONS",540,320,116,ORANGE,a=a,sc=0.85+0.15*spring((t-wt(7,"hundreds")+0.05)/0.2))
        label(img,"HIROSHIMA",0.18*w*K,0.78*h*K+70,40,WHITE,a=a,stroke=5)
    return b,hud,1.0+0.02*u
def sh_sky(t):
    b=taiga(t,sky_grad(((0.10,0.12,0.25),(0.60,0.45,0.42),(1.0,0.65,0.40)),0.6))
    b=smoke(b,t,0.45,(0.45,0.38,0.35),0.0,8); glow(b,w*0.55,h*0.18,90,(0.9,0.6,0.35),0.5)
    def hud(img): label(img,"NO IMPACT",540,320,120,WHITE,a=fa(t,wt(8,"ground")-0.1,99,0.15,0.2))
    return b,hud,1.0+0.04*(t-Ls(8))
SHOTS=[(0.0,lambda t:sh_hook(t,0),"cut"),(wt(0,"and")-0.05,sh_center,"cut"),
 (Ls(1)-0.3,lambda t:sh_trading(t,0),"blast"),(Ls(2)-0.1,lambda t:sh_trading(t,1),"cut"),
 (Ls(3)-0.3,lambda t:sh_glow(t,0),"blast"),(wt(3,"some")-0.05,lambda t:sh_glow(t,1),"cut"),
 (Ls(4)-0.3,sh_1927,"blast"),(Ls(5)-0.1,lambda t:sh_map(t,0),"cut"),(wt(5,"pointing")-0.05,lambda t:sh_map(t,1),"cut"),
 (Ls(6)-0.1,sh_poles,"cut"),(Ls(7)-0.3,sh_rock,"blast"),(wt(7,"exploded")-0.05,sh_burst,"cut"),(wt(7,"hundreds")-0.05,sh_mega,"cut"),
 (Ls(8)-0.1,sh_sky,"cut")]
TR=0.2; LOOPD=0.45
def shot_at(t):
    i=0
    for k,s in enumerate(SHOTS):
        if t>=s[0]: i=k
    return i
_FI=[0]
def render_shot(i,t):
    f=SHOTS[i][1]
    b,hud,z=(sh_1927(t,_FI[0]) if f is sh_1927 else f(t)); st=SHOTS[i][0]
    z*=punch(t,[st] if i>0 else [],0.06,0.32)
    dx,dy=shake(t,wt(2,"threw"),14,0.6); d2=shake(t,wt(7,"exploded"),10,0.6); d3=shake(t,wt(0,"flattened"),6,0.4)
    dx+=d2[0]+d3[0]; dy+=d2[1]+d3[1]
    return camera(b,z,0.5,0.45,dx,dy),hud
def blast(b1,b2,u,cx=0.5,cy=0.45):
    r=np.sqrt((xx-cx*w)**2+(yy-cy*h)**2); R=eout(u)*w*1.25
    m=sm_np((R-r)/18)[...,None]; edge=np.exp(-((r-R)/(22+30*u))**2)[...,None]
    # radial push on the old frame near the front
    out=b1*(1-m)+b2*m
    return out+edge*np.array([1.6,1.1,0.7],np.float32)*(1-u*0.6)+np.array([0.5,0.35,0.2],np.float32)*max(0,0.5-abs(u-0.15))*0.6
def compose(t,fi=None):
    if fi is None: fi=int(round(t*30))
    _FI[0]=fi
    i=shot_at(max(t,0)); nxt=SHOTS[i+1] if i+1<len(SHOTS) else None; huds=[]
    if nxt and nxt[2]=="blast" and t>nxt[0]-TR:
        u=(t-(nxt[0]-TR))/(2*TR); b1,h1=render_shot(i,t); b2,h2=render_shot(i+1,t); b=blast(b1,b2,u)
    elif SHOTS[i][2]=="blast" and t<SHOTS[i][0]+TR and i>0:
        u=(t-(SHOTS[i][0]-TR))/(2*TR); b1,h1=render_shot(i-1,t); b2,h2=render_shot(i,t); b=blast(b1,b2,u); huds=[h2] if u>0.6 else []
    elif t>TOTAL-LOOPD:
        u=(t-(TOTAL-LOOPD))/LOOPD; b1,h1=render_shot(i,t); b2,h2=render_shot(0,t-TOTAL); b=blast(b1,b2,u)
    else:
        b,h1=render_shot(i,t); huds=[h1]
    b=post(b,bloom=0.5,thr=0.65,tint=(1.04,1.0,0.94))
    img=to_img(b,fi)
    for hf in huds:
        if hf: hf(img)
    ha=1-sm((t-(Ls(1)-0.1))/0.25) if t<Ls(1)+0.2 else sm((t-(TOTAL-LOOPD))/0.3)
    if ha>0.01:
        hook_title(img,[("80 MILLION TREES",WHITE)],a=ha,y=250,size=124)
        s2=wt(0,"crater")-0.05
        if t>=s2 or t>TOTAL-LOOPD:
            a2=ha*(sm((t-s2)/0.08) if t<Ls(1)+0.2 else 1.0); sc=0.7+0.3*spring((t-s2)/0.22) if t<Ls(1)+0.2 else 1.0
            hook_title(img,[("NO CRATER",ORANGE)],a=a2,y=390,size=150,sc=sc)
    return finish(img,CAP,t)
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
