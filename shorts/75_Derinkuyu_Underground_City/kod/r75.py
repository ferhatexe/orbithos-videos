import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid75"); sys.path.insert(0,"/home/claude/toolkit")
from pro import *
from PIL import Image, ImageDraw
T,LINES,SC,TOTAL=load("timeline.json")
CAP=Captions(LINES); WD=CAP.W
def wt(li,sub,o=0.0): return word_t(WD,li,sub,o)
def Ls(i): return LINES[i]["s"]
def Le(i): return LINES[i]["e"]
def sm_np(x): x=np.clip(x,0,1); return x*x*(3-2*x)
def flick(t,s=0.0): return 1+0.07*math.sin(t*13.1+s)+0.05*math.sin(t*23.7+s*2.1)+0.03*math.sin(t*41.3+s*0.7)
WARM=np.array([1.0,0.60,0.30],np.float32)
# ===================== Derinkuyu: torch-lit underground cinematic + cutaway "ant farm" city, rolling-stone-door wipes =====================
def pfbm(H_,W_,seed,octs=5,base=4):
    g=np.random.default_rng(seed); out=np.zeros((H_,W_),np.float32); amp=1.0
    for o in range(octs):
        gh=base*2**o; gw=max(2,int(round(gh*W_/H_)))
        n=np.tile(g.normal(0,1,(gh,gw)).astype(np.float32),(3,3))
        out+=cv2.resize(n,(3*W_,3*H_),interpolation=cv2.INTER_CUBIC)[H_:2*H_,W_:2*W_]*amp; amp*=0.5
    return (out-out.mean())/(out.std()+1e-6)
def wblur(a,s):
    p=int(s*4)+1; ap=np.pad(a,((p,p),(p,p))+(((0,0),) if a.ndim==3 else ()),mode='wrap'); return cv2.GaussianBlur(ap,(0,0),s)[p:-p,p:-p]
# ---------- tunnel wall texture (periodic) ----------
TH,TW=1024,512
def _tex():
    h1=pfbm(TH,TW,11,6,4); vv,uu=np.mgrid[0:TH,0:TW].astype(np.float32)
    g=np.random.default_rng(17); dent=np.zeros((TH,TW),np.float32)
    for i in range(2600):
        x,y=g.uniform(0,TW),g.uniform(0,TH); a=g.normal(35,20); ax=(int(g.uniform(10,26)),int(g.uniform(3,8))); v=float(g.uniform(0.5,1.0))
        for ox in (-TW,0,TW):
            for oy in (-TH,0,TH): cv2.ellipse(dent,(int(x+ox),int(y+oy)),ax,a,0,360,v,-1,cv2.LINE_AA)
    dent=wblur(np.minimum(dent,1.2),2.0)
    hg=h1*0.55+pfbm(TH,TW,14,4,16)*0.10-dent*0.45
    gx=(np.roll(hg,-1,1)-np.roll(hg,1,1)); gy=(np.roll(hg,-1,0)-np.roll(hg,1,0))
    shade=np.clip(1.0-gx*1.8-gy*1.3,0.3,1.8)
    m=np.clip(0.5+0.5*pfbm(TH,TW,15,3,2),0,1)[...,None]
    alb=np.array([0.80,0.70,0.56],np.float32)*(1-m)+np.array([0.70,0.54,0.44],np.float32)*m
    alb=alb*(0.78+0.22*np.clip(0.5+0.5*pfbm(TH,TW,16,5,8),0,1.3))[...,None]
    c=(alb*shade[...,None]).astype(np.float32); return c,wblur(c,9).astype(np.float32)
# ---------- cutaway world ----------
CW,CHH=1700,3000; Y0=640; MPX=26.0
def dmy(m): return Y0+m*MPX
LVY=[None,900,1134,1394,1654,1914,2174,2434,2720]
CHAMB={1:[(470,760,"stable"),(860,1120,"living"),(1220,1470,"stable")],
 2:[(300,560,"store"),(660,980,"kitchen"),(1080,1350,"living")],
 3:[(420,720,"wine"),(820,1060,"store"),(1160,1480,"wine")],
 4:[(330,600,"living"),(700,1100,"church"),(1200,1430,"living")],
 5:[(450,800,"school"),(900,1150,"living"),(1250,1500,"store")],
 6:[(280,520,"well"),(620,950,"living"),(1050,1350,"store")],
 7:[(400,700,"living"),(800,1150,"store"),(1250,1450,"living")],
 8:[(560,1140,"church2")]}
RAMPS=[(1,760,980),(2,1080,820),(2,560,720),(3,1160,1430),(3,420,600),(4,1100,900),(4,330,240),(5,800,620),(5,1500,1350),(6,950,700),(6,1050,1250),(7,800,620),(7,1250,1140)]
HOUSE=(650,880); BASE=(660,860,Y0+118); SHX=1580; WLX=340
def chamber_poly(x0,x1,yf,hw,ha):
    pts=[(x0,yf),(x0,yf-hw)]
    for k in range(25):
        a=math.pi*(1-k/24); pts.append(((x0+x1)/2+math.cos(a)*(x1-x0)/2, yf-hw-math.sin(a)*ha))
    pts.append((x1,yf)); return np.array(pts,np.float32)
def chdims(kind):
    return (128,92) if kind=="church" else ((150,110) if kind=="church2" else (92,52))
def _sil_person(b,x,yf,s,col,sit=False,g=None):
    hh=1.0 if not sit else 0.7
    cv2.circle(b,(int(x),int(yf-s*1.78*hh)),max(2,int(s*0.23)),col,-1,cv2.LINE_AA)
    cv2.ellipse(b,(int(x),int(yf-s*1.05*hh)),(max(2,int(s*0.30)),max(3,int(s*0.62*hh))),0,0,360,col,-1,cv2.LINE_AA)
    if not sit:
        cv2.line(b,(int(x-s*0.12),int(yf-s*0.6)),(int(x-s*0.18),int(yf)),col,max(1,int(s*0.16)),cv2.LINE_AA)
        cv2.line(b,(int(x+s*0.12),int(yf-s*0.6)),(int(x+s*0.2),int(yf)),col,max(1,int(s*0.16)),cv2.LINE_AA)
    else: cv2.ellipse(b,(int(x+s*0.2),int(yf-s*0.25)),(int(s*0.45),int(s*0.22)),0,0,360,col,-1,cv2.LINE_AA)
def _sil_sheep(b,x,yf,s,col,d=1):
    cv2.ellipse(b,(int(x),int(yf-s*0.62)),(int(s*0.62),int(s*0.36)),0,0,360,col,-1,cv2.LINE_AA)
    cv2.ellipse(b,(int(x+d*s*0.66),int(yf-s*0.82)),(int(s*0.2),int(s*0.14)),d*20,0,360,col,-1,cv2.LINE_AA)
    for lx_ in (-0.4,-0.2,0.25,0.42): cv2.line(b,(int(x+lx_*s),int(yf-s*0.4)),(int(x+lx_*s),int(yf)),col,max(1,int(s*0.09)),cv2.LINE_AA)
def _jar(b,x,yf,s,col):
    cv2.ellipse(b,(int(x),int(yf-s*0.55)),(int(s*0.32),int(s*0.5)),0,0,360,col,-1,cv2.LINE_AA)
    cv2.rectangle(b,(int(x-s*0.12),int(yf-s*1.15)),(int(x+s*0.12),int(yf-s*0.9)),col,-1)
def glowL(buf,x,y,r,a):
    x0,x1=max(0,int(x-r*3.5)),min(buf.shape[1],int(x+r*3.5)+1); y0,y1=max(0,int(y-r*3.5)),min(buf.shape[0],int(y+r*3.5)+1)
    if x0>=x1 or y0>=y1: return
    Y_,X_=np.mgrid[y0:y1,x0:x1].astype(np.float32); buf[y0:y1,x0:x1]+=np.exp(-((X_-x)**2+(Y_-y)**2)/(r*r))*a
def _sky_land():
    H_=Y0+40; Yg,Xg=np.mgrid[0:H_,0:CW].astype(np.float32); k=np.clip(Yg/Y0,0,1)[...,None]
    top=np.array([0.05,0.07,0.20],np.float32); mid=np.array([0.48,0.24,0.26],np.float32); hor=np.array([1.25,0.60,0.20],np.float32)
    sky=np.where(k<0.6,top*(1-k/0.6)+mid*(k/0.6),mid*(1-(k-0.6)/0.4)+hor*((k-0.6)/0.4)).astype(np.float32)
    sun=(1150,455); d2=((Xg-sun[0])**2+(Yg-sun[1])**2)
    sky+=np.exp(-d2/(26**2))[...,None]*np.array([3.0,2.4,1.5],np.float32)+np.exp(-d2/(150**2))[...,None]*np.array([0.9,0.5,0.2],np.float32)*0.7+np.exp(-d2/(500**2))[...,None]*np.array([0.5,0.25,0.1],np.float32)*0.5
    # far mesas
    n1=cv2.resize(fbm((1,60),401,3,2),(CW,1))[0]; ridge=Y0-70-28*n1-40*np.clip(np.sin(Xg[0]/260.0+1),0,1)
    mm=(Yg>ridge[None,:]).astype(np.float32); mcol=np.array([0.55,0.30,0.30],np.float32)
    sky=sky*(1-mm[...,None]*0.75)+mcol*mm[...,None]*0.75
    # fairy chimneys
    g=np.random.default_rng(402); tex=cv2.resize(fbm((H_//4,CW//4),403,5,4),(CW,H_))
    def chim(cx,base,hh,bw,haze):
        x0,x1=int(cx-bw-4),int(cx+bw+4); y0,y1=int(base-hh-bw*0.6),int(base)
        x0=max(0,x0); x1=min(CW,x1)
        X_=Xg[y0:y1,x0:x1]; Y_=Yg[y0:y1,x0:x1]; f=np.clip((base-Y_)/hh,0,1.2)
        hwid=bw*(1-np.clip(f,0,1))**0.55*(1+0.06*np.sin(Y_/9.0))+bw*0.16
        inside=(np.abs(X_-cx)<hwid)&(f<1.0); rel=np.clip((X_-cx)/hwid,-1,1)
        sh=0.22+0.75*np.clip(rel*0.5+0.5,0,1)**1.5
        col=np.array([0.88,0.60,0.40],np.float32)*sh[...,None]*(0.9+0.08*tex[y0:y1,x0:x1])[...,None]
        col+=(np.clip(rel-0.7,0,1)*2.0)[...,None]*np.array([1.2,0.7,0.3],np.float32)
        capc=((Y_>base-hh-bw*0.45)&(Y_<base-hh+bw*0.12)&(((X_-cx)/(bw*0.42))**2+((Y_-(base-hh-bw*0.1))/(bw*0.32))**2<1))
        ccol=np.array([0.26,0.18,0.15],np.float32)*(0.6+0.7*np.clip(rel*0.5+0.5,0,1))[...,None]
        fogc=sky[y0:y1,x0:x1]
        col=col*(1-haze)+fogc*haze; ccol=ccol*(1-haze)+fogc*haze
        reg=sky[y0:y1,x0:x1]; reg[inside]=col[inside]; reg[capc]=ccol[capc]
    for i in range(16):
        cx=g.uniform(0,CW); chim(cx,Y0-g.uniform(20,45),g.uniform(90,160),g.uniform(26,40),0.45)
    for cx,hh,bw in ((90,330,70),(300,250,58),(470,190,44),(1000,230,50),(1290,300,64),(1500,360,74),(1650,240,56)):
        chim(cx,Y0+6,hh,bw,0.0)
    # village houses (far)
    for i in range(10):
        hx=g.uniform(0,CW); hw_=g.uniform(30,60); hh=g.uniform(24,44); yb=Y0-g.uniform(6,30)
        if abs(hx-765)<220: continue
        cv2.rectangle(sky,(int(hx),int(yb-hh)),(int(hx+hw_),int(yb)),(0.45,0.28,0.25),-1)
        cv2.rectangle(sky,(int(hx+hw_*0.55),int(yb-hh)),(int(hx+hw_),int(yb)),(0.85,0.52,0.34),-1)
    # main house
    x0,x1=HOUSE
    cv2.rectangle(sky,(x0,Y0-160),(x1,Y0),(0.36,0.24,0.20),-1); cv2.rectangle(sky,(x0+150,Y0-160),(x1,Y0),(0.90,0.58,0.36),-1)
    cv2.rectangle(sky,(x0+20,Y0-245),(x0+130,Y0-160),(0.34,0.23,0.19),-1); cv2.rectangle(sky,(x0+100,Y0-245),(x0+130,Y0-160),(0.88,0.56,0.35),-1)
    cv2.rectangle(sky,(x0-8,Y0-172),(x1+8,Y0-158),(0.50,0.36,0.28),-1)
    cv2.ellipse(sky,(x0+75,Y0-45),(28,40),0,180,360,(0.08,0.05,0.04),-1,cv2.LINE_AA); cv2.rectangle(sky,(x0+47,Y0-45),(x0+103,Y0),(0.08,0.05,0.04),-1)
    for wx,wy in ((x0+175,Y0-100),(x0+60,Y0-205)):
        cv2.ellipse(sky,(wx,wy),(14,16),0,180,360,(1.6,0.9,0.4),-1,cv2.LINE_AA); cv2.rectangle(sky,(wx-14,wy),(wx+14,wy+22),(1.6,0.9,0.4),-1)
    return sky
def _world():
    g=np.random.default_rng(500)
    Yg,Xg=np.mgrid[0:CHH,0:CW].astype(np.float32)
    n=cv2.resize(fbm((CHH//6,CW//6),501,6,4),(CW,CHH)); n2=cv2.resize(fbm((CHH//24,CW//24),502,4,3),(CW,CHH))
    strata=0.5+0.5*np.sin(Yg/41.0+n2*1.8)
    alb=np.array([0.80,0.69,0.55],np.float32)*(1-strata[...,None])+np.array([0.72,0.55,0.46],np.float32)*strata[...,None]
    alb=alb*(0.86+0.10*n)[...,None]
    gx=cv2.Sobel(n,cv2.CV_32F,1,0,ksize=5); gy=cv2.Sobel(n,cv2.CV_32F,0,1,ksize=5); sh=np.clip(1-0.02*(gx+gy),0.6,1.4)
    nf=cv2.resize(fbm((CHH//2,CW//2),505,5,40),(CW,CHH)); face=alb*(0.17*sh*(0.85+0.15*nf)*(1-0.3*np.clip((Yg-Y0)/2400,0,1)))[...,None]
    sky=_sky_land(); SH_=sky.shape[0]
    ROCKF=face.copy(); ROCKF[:Y0]=sky[:Y0]
    cv2.rectangle(ROCKF,(0,Y0-2),(CW,Y0+14),(0.20,0.15,0.09),-1); cv2.line(ROCKF,(0,Y0-2),(CW,Y0-2),(1.0,0.66,0.32),2)
    # masks
    CHm=np.zeros((CHH,CW),np.float32); LID=np.zeros((CHH,CW),np.uint8)
    def put(poly,lid):
        p=np.round(poly).astype(np.int32); cv2.fillPoly(CHm,[p],1.0,cv2.LINE_AA); cv2.fillPoly(LID,[p],int(lid))
    for lv,lst in CHAMB.items():
        yf=LVY[lv]
        for k,(x0,x1,kind) in enumerate(lst):
            hw,ha=chdims(kind); put(chamber_poly(x0,x1,yf,hw,ha),lv)
            if k+1<len(lst):
                nx0=lst[k+1][0]; put(np.array([(x1-6,yf),(x1-6,yf-50),(nx0+6,yf-50),(nx0+6,yf)],np.float32),lv)
        xe=lst[-1][1]; put(np.array([(xe-6,yf),(xe-6,yf-38),(SHX,yf-38),(SHX,yf)],np.float32),lv)
    for (lv,xa,xb) in RAMPS:
        ya,yb=LVY[lv],LVY[lv+1]; put(np.array([(xa,ya),(xa,ya-46),(xb,yb-46),(xb,yb)],np.float32),lv)
    bx0,bx1,byf=BASE; put(chamber_poly(bx0,bx1,byf,62,28),11)
    put(np.array([(bx0+8,byf),(bx0+8,byf-46),(520,LVY[1]-46),(520,LVY[1])],np.float32),11)
    put(np.array([(SHX-13,Y0-6),(SHX+13,Y0-6),(SHX+13,LVY[8]),(SHX-13,LVY[8])],np.float32),9)
    put(np.array([(WLX-15,LVY[2]-4),(WLX+15,LVY[2]-4),(WLX+15,2950),(WLX-15,2950)],np.float32),10)
    # rough edges
    dxn=cv2.resize(fbm((CHH//8,CW//8),503,5,10),(CW,CHH))*6.0; dyn=cv2.resize(fbm((CHH//8,CW//8),504,5,10),(CW,CHH))*6.0
    CHm=cv2.remap(CHm,Xg+dxn,Yg+dyn,cv2.INTER_LINEAR); CHm=cv2.GaussianBlur(CHm,(0,0),0.8)
    LID=cv2.dilate(LID,np.ones((5,5),np.uint8))
    # interior lighting
    LIGHT=np.zeros((CHH,CW),np.float32); flames=[]
    def torch(x,y,r=105,a=1.0): glowL(LIGHT,x,y,r,a); flames.append((x,y))
    for lv,lst in CHAMB.items():
        yf=LVY[lv]
        for (x0,x1,kind) in lst:
            hw,ha=chdims(kind); nT=max(1,int((x1-x0)/170))
            for j in range(nT):
                tx=x0+(x1-x0)*(j+0.5)/nT+g.uniform(-20,20); torch(tx,yf-hw*0.72,95+(x1-x0)*0.08,1.0)
            if kind=="kitchen": glowL(LIGHT,(x0+x1)/2,yf-14,70,1.6)
            if kind in ("church","church2"): glowL(LIGHT,(x0+x1)/2,yf-hw*0.5,140,0.8)
    torch(760,BASE[2]-50,90,1.1)
    for (lv,xa,xb) in RAMPS: glowL(LIGHT,(xa+xb)/2,(LVY[lv]+LVY[lv+1])/2-23,60,0.35)
    balb=alb*0.62
    ao=cv2.GaussianBlur(CHm,(0,0),9)
    INT=balb*(0.03+LIGHT[...,None]**1.3*WARM*1.35)*(0.30+0.70*np.clip(ao*1.4-0.2,0,1))[...,None]
    # vent shaft daylight
    sh_mask=(LID==9); dl=np.exp(-(Yg-Y0)/700.0)
    INT[sh_mask]=(np.array([0.55,0.62,0.75],np.float32)*(0.2+1.5*dl[...,None]))[sh_mask]
    for lv in range(1,9):
        glowL(INT[...,0],SHX-30,LVY[lv]-20,22,0.25*math.exp(-(LVY[lv]-Y0)/700.0)); glowL(INT[...,1],SHX-30,LVY[lv]-20,22,0.28*math.exp(-(LVY[lv]-Y0)/700.0)); glowL(INT[...,2],SHX-30,LVY[lv]-20,22,0.32*math.exp(-(LVY[lv]-Y0)/700.0))
    wl=(LID==10); INT[wl]=(balb*0.25)[wl]+np.array([0.05,0.06,0.07],np.float32)
    cv2.rectangle(INT,(WLX-15,2895),(WLX+15,2950),(0.05,0.22,0.30),-1); cv2.line(INT,(WLX-15,2896),(WLX+15,2896),(0.4,0.7,0.8),2)
    # silhouettes
    S=(0.025,0.016,0.012)
    for lv,lst in CHAMB.items():
        yf=LVY[lv]
        for (x0,x1,kind) in lst:
            hw,ha=chdims(kind); cx=(x0+x1)/2; W_=x1-x0
            if kind=="stable":
                for k in range(4): _sil_sheep(INT,x0+30+k*(W_-60)/3.5,yf,22+g.uniform(-2,3),S,1 if k%2 else -1)
                _sil_person(INT,x1-28,yf,21,S)
            elif kind=="living":
                for k in range(3): _sil_person(INT,x0+35+k*(W_-70)/2,yf,20+g.uniform(-2,2),S,sit=(k==1))
                _jar(INT,x1-18,yf,20,S)
            elif kind=="kitchen":
                glowL(INT[...,0],cx,yf-12,22,2.2); glowL(INT[...,1],cx,yf-12,18,1.3); glowL(INT[...,2],cx,yf-12,12,0.5)
                cv2.ellipse(INT,(int(cx),int(yf-38)),(24,18),0,0,360,S,-1,cv2.LINE_AA)
                for k in (-1,1): _sil_person(INT,cx+k*95,yf,21,S,sit=(k==1))
                for k in range(3): _jar(INT,x0+20+k*22,yf,16,S)
            elif kind=="store":
                for k in range(int(W_/34)): _jar(INT,x0+20+k*34,yf,22+(k%3)*3,S)
            elif kind=="wine":
                cv2.rectangle(INT,(int(x0+30),int(yf-30)),(int(x0+150),int(yf)),(0.30,0.20,0.14),-1); cv2.rectangle(INT,(int(x0+36),int(yf-26)),(int(x0+144),int(yf-8)),(0.16,0.04,0.05),-1)
                cv2.rectangle(INT,(int(x0+150),int(yf-12)),(int(x0+200),int(yf-4)),(0.30,0.20,0.14),-1)
                _jar(INT,x0+215,yf,24,S); _sil_person(INT,x0+90,yf-30,20,S); _jar(INT,x1-25,yf,22,S)
            elif kind in ("church","church2"):
                for k in range(5):
                    ax=x0+(k+0.5)*W_/5; cv2.ellipse(INT,(int(ax),int(yf-hw*0.75)),(int(W_/12),int(hw*0.35)),0,180,360,(0.6,0.42,0.30),3,cv2.LINE_AA)
                    cv2.rectangle(INT,(int(ax-W_/10+2),int(yf-hw*0.75)),(int(ax-W_/10+10),int(yf)),(0.40,0.28,0.20),-1)
                cv2.rectangle(INT,(int(cx-5),int(yf-hw-ha*0.6)),(int(cx+5),int(yf-hw+30)),(1.0,0.75,0.45),-1)
                cv2.rectangle(INT,(int(cx-26),int(yf-hw-ha*0.35)),(int(cx+26),int(yf-hw-ha*0.35+9)),(1.0,0.75,0.45),-1)
                for k in range(-2,3):
                    if k: _sil_person(INT,cx+k*58,yf,21,S)
            elif kind=="school":
                for k in range(5): _sil_person(INT,x0+30+k*(W_-60)/4,yf,18,S,sit=True)
                _sil_person(INT,x1-25,yf,22,S)
            elif kind=="well":
                _sil_person(INT,WLX+60,yf,21,S); cv2.line(INT,(WLX,int(yf-hw)),(WLX,int(yf+30)),(0.5,0.4,0.3),1)
    bx0,bx1,byf=BASE; _sil_person(INT,bx0+80,byf,22,S); cv2.line(INT,(bx0+110,int(byf-50)),(bx0+128,int(byf-10)),S,4)
    for (x,y) in flames:
        cv2.ellipse(INT,(int(x),int(y)),(3,6),0,0,360,(2.2,1.5,0.7),-1,cv2.LINE_AA)
    # rolling stones in niches next to ramp tops
    STONES=[]
    for (lv,xa,xb) in RAMPS[::2]:
        f=0.22; sx=xa+f*(xb-xa); sy=LVY[lv]+f*(LVY[lv+1]-LVY[lv])-23; STONES.append((sx,sy))
    lum=INT.mean(2)*CHm
    SPILL=cv2.GaussianBlur(lum,(0,0),14)*0.45+cv2.GaussianBlur(lum,(0,0),40)*0.10
    LIDS=cv2.dilate(LID,np.ones((61,61),np.uint8))
    return dict(R=ROCKF.astype(np.float16),I=INT.astype(np.float16),C=CHm.astype(np.float16),S=SPILL.astype(np.float16),L=LID,LS=LIDS,ST=np.array(STONES,np.float32))
CACHE="world75.npz"
if os.path.exists(CACHE): _z=np.load(CACHE); WW={k:_z[k] for k in _z.files}
else:
    WW=_world(); np.savez(CACHE,**WW)
ROCKF=WW["R"].astype(np.float32); INT=WW["I"].astype(np.float32); CHm=WW["C"].astype(np.float32); SPILL=WW["S"].astype(np.float32); LID=WW["L"]; LIDS=WW["LS"]; STONES=WW["ST"]
TCACHE="tex75.npz"
if os.path.exists(TCACHE): _z=np.load(TCACHE); TEXC,TEXB=_z["a"],_z["b"]
else: TEXC,TEXB=_tex(); np.savez(TCACHE,a=TEXC,b=TEXB)
def RV(t,on=1.0,ex=None):
    rv=np.zeros(16,np.float32)
    for i in range(1,12): rv[i]=on*(1+0.07*math.sin(t*11.0+i*1.7)+0.05*math.sin(t*19.3+i*2.9))
    if ex:
        for k,v in ex.items(): rv[k]=v*(1+0.07*math.sin(t*11.0+k*1.7)+0.05*math.sin(t*19.3+k*2.9))
    return rv
def cutM(cx,cy,s): return np.float32([[s,0,w/2-cx*s],[0,s,h/2-cy*s]])
def c2s(M,x,y): return (M[0,0]*x+M[0,2], M[1,1]*y+M[1,2])
def cutview(t,cx,cy,s,rv,night=0.0,hl=None):
    M=cutM(cx,cy,s); fl=cv2.INTER_LINEAR; bm=cv2.BORDER_REPLICATE
    R=cv2.warpAffine(ROCKF,M,(w,h),flags=fl,borderMode=bm); I=cv2.warpAffine(INT,M,(w,h),flags=fl,borderMode=bm)
    C=cv2.warpAffine(CHm,M,(w,h),flags=fl,borderMode=bm); Sp=cv2.warpAffine(SPILL,M,(w,h),flags=fl,borderMode=bm)
    L=cv2.warpAffine(LID,M,(w,h),flags=cv2.INTER_NEAREST,borderMode=bm); LS=cv2.warpAffine(LIDS,M,(w,h),flags=cv2.INTER_NEAREST,borderMode=bm)
    k=rv[L]; ks=rv[LS]
    if hl is not None: k=k+hl[0]*(L==hl[1]);
    kk=(0.035+0.965*np.clip(k,0,3))[...,None]
    b=R*(1-C[...,None])+I*kk*C[...,None]
    b+=(Sp*np.clip(ks,0,2))[...,None]*np.array([1.0,0.55,0.25],np.float32)*0.9
    if night>0:
        sy0=int(np.clip(M[1,1]*Y0+M[1,2],0,h))
        if sy0>0: b[:sy0]=b[:sy0]*(1-0.8*night)+np.array([0.02,0.03,0.08],np.float32)*night
    # rolling stones in niches
    for (sx,sy) in STONES:
        X,Y=c2s(M,sx,sy); r=22*s
        if -r<X<w+r and -r<Y<h+r:
            cv2.circle(b,(int(X),int(Y)),int(r),(0.30,0.25,0.20),-1,cv2.LINE_AA); cv2.circle(b,(int(X),int(Y)),int(r),(0.12,0.09,0.07),max(1,int(3*s)),cv2.LINE_AA)
            cv2.circle(b,(int(X),int(Y)),max(1,int(r*0.2)),(0.05,0.04,0.03),-1,cv2.LINE_AA)
    return b,M
def depth_meter(img,M,t,mx,a=1.0,x=96):
    if a<=0.01: return
    d=ImageDraw.Draw(img); al=int(255*a)
    y0=(M[1,1]*Y0+M[1,2])*K; y1=(M[1,1]*dmy(mx)+M[1,2])*K
    d.line((x,y0,x,y1),fill=(255,168,28,al),width=6)
    for m in range(0,int(mx)+1,10):
        y=(M[1,1]*dmy(m)+M[1,2])*K
        if y<0 or y>1900: continue
        d.line((x-14,y,x+14,y),fill=(255,255,255,al),width=4)
        if not (1050<y<1430) and y<1700 and m>0: label(img,f"{m} M",x+70,y,34,WHITE,a=a,stroke=5)
    d.ellipse((x-12,y1-12,x+12,y1+12),fill=(255,168,28,al))
# ---------- dust motes ----------
_g=np.random.default_rng(77); MOTE=np.c_[_g.uniform(0,w,260),_g.uniform(0,h,260),_g.uniform(-6,6,260),_g.uniform(-14,4,260),_g.uniform(0,6.28,260),_g.uniform(0.4,1.0,260)]
def motes(b,t,lf,amt=1.0,col=(1.0,0.75,0.45),n=180):
    lay=np.zeros((h//2,w//2),np.float32)
    for i in range(n):
        x0,y0,vx,vy,ph,sz=MOTE[i]; x=(x0+vx*t+9*math.sin(t*0.7+ph))%w; y=(y0+vy*t+7*math.cos(t*0.5+ph*1.3))%h
        a=lf(x,y)*sz*amt
        if a>0.02: cv2.circle(lay,(int(x/2),int(y/2)),1,float(a),-1,cv2.LINE_AA)
    lay=cv2.GaussianBlur(lay,(0,0),0.7); b+=cv2.resize(lay,(w,h))[...,None]*np.array(col,np.float32)*1.6
# ---------- tunnel / shaft remap ----------
def tmaps(a,b_,p,cyf,vs):
    X=(xx-w*0.5)/(w*0.5); Y=(yy-h*cyf)/(w*0.5)
    r=np.maximum((np.abs(X/a)**p+np.abs(Y/b_)**p)**(1/p),1e-4); Z=(1.0/r).astype(np.float32)
    ang=np.arctan2(Y/b_,X/a); U=((ang/(2*np.pi)+0.5)*TW*3).astype(np.float32)
    ny=(Y/b_)/r; nx_=(X/a)/r; SH=((0.88+0.22*ny)*(1-0.55*np.clip(np.abs(nx_*ny)*2.2-0.6,0,1))).astype(np.float32)
    return dict(Z=Z,U=U,SH=SH,ATT=(1/(1+(Z/1.05)**2.2)).astype(np.float32),MIP=sm_np((Z-1.0)/2.5).astype(np.float32),vs=vs)
TM_T=tmaps(0.62,0.85,5.0,0.47,320.0); TM_C=tmaps(0.70,0.70,2.0,0.46,280.0)
def tunnel_r(t,TM,off,torch=1.0,day=0.0,far=0.0,farcol=(1.0,0.6,0.3),water=False,ribs=False):
    Z=TM["Z"]; my=np.mod(Z*TM["vs"]+off,TH).astype(np.float32); U=TM["U"]
    a=cv2.remap(TEXC,U,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP); bb=cv2.remap(TEXB,U,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
    m=TM["MIP"][...,None]; tex=a*(1-m)+bb*m
    L=(torch*flick(t)*1.25*TM["ATT"])[...,None]*WARM
    if day>0:
        dl=sm_np((Z-1.2)/9.0)**1.5; L=L+(day*1.4*dl)[...,None]*np.array([0.75,0.85,1.0],np.float32)
    if far>0:
        fl=np.exp(-((1/Z)/0.10)**2); L=L+(far*0.9*sm_np((Z-1.0)/8))[...,None]*np.array(farcol,np.float32)
    b=tex*L*TM["SH"][...,None]
    if ribs:
        ph=np.mod((Z*TM["vs"]+off)/(TM["vs"]*1.4),1.0); rd=np.exp(-((ph-0.5)/0.06)**2)*sm_np((6-Z)/3)
        b*=(1-0.65*rd)[...,None]
    if day>0:
        core=sm_np((Z-7.0)/3.0)[...,None]; b=b*(1-core)+core*np.array([2.2,2.3,2.5],np.float32)*day
    if far>0:
        core=sm_np((Z-6.0)/4.0)[...,None]; b=b*(1-core)+core*np.array(farcol,np.float32)*1.6*far
    if water:
        core=sm_np((Z-6.5)/1.5); r=1/np.maximum(Z,1e-3)
        rip=0.5+0.5*np.sin(r*260-t*6); wc=np.array([0.02,0.07,0.09],np.float32)+(rip**8*core*0.6)[...,None]*np.array([1.0,0.7,0.4],np.float32)
        b=b*(1-core[...,None])+wc*core[...,None]
    return b
# ---------- relief walls (dynamic torch lighting) ----------
def nrm(hg,k):
    gx=cv2.Sobel(hg,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(hg,cv2.CV_32F,0,1,ksize=3)
    nx=-gx*k; ny=-gy*k; n=np.sqrt(nx*nx+ny*ny+1); return np.stack([nx/n,ny/n,1/n]).astype(np.float32)
def tuff_alb(seed):
    n=fbm((h,w),seed,5,4); m=np.clip(0.5+0.5*fbm((h,w),seed+9,3,2),0,1)[...,None]
    a=np.array([0.82,0.71,0.57],np.float32)*(1-m)+np.array([0.74,0.57,0.46],np.float32)*m
    return (a*(0.86+0.12*n)[...,None]).astype(np.float32)
def carve_h(seed):
    g=np.random.default_rng(seed); base=fbm((h,w),seed,6,3); af=fbm((6,4),seed+1,1,2)
    dent=np.zeros((h,w),np.float32)
    for i in range(1400):
        x,y=g.uniform(0,w),g.uniform(0,h); a=af[int(y/h*5.99),int(x/w*3.99)]*0.8+0.6+g.normal(0,0.25)
        cv2.ellipse(dent,(int(x),int(y)),(int(g.uniform(9,24)),int(g.uniform(3,7))),math.degrees(a),0,360,float(g.uniform(0.5,1.0)),-1,cv2.LINE_AA)
    dent=cv2.GaussianBlur(np.minimum(dent,1.2),(0,0),2.2)
    return (base*0.45-dent*0.30+fbm((h,w),seed+4,4,24)*0.05).astype(np.float32)
def arch_mask(x0,x1,ytop,ybot,feather=2.0):
    m=np.zeros((h,w),np.float32); p=chamber_poly(x0,x1,ybot,(ybot-ytop)-(x1-x0)/2,(x1-x0)/2)
    cv2.fillPoly(m,[np.round(p).astype(np.int32)],1.0,cv2.LINE_AA); return cv2.GaussianBlur(m,(0,0),feather)
def _reliefs():
    R={}
    # basement masonry wall
    g=np.random.default_rng(31); mk=np.ones((h,w),np.uint8)*255; alb=np.zeros((h,w,3),np.float32); y=-30
    while y<h:
        rh=int(g.uniform(70,105)); x=-int(g.uniform(0,90))
        while x<w:
            sw=int(g.uniform(110,190)); c=np.array([0.84,0.71,0.55])*g.uniform(0.82,1.08)
            cv2.rectangle(alb,(x,y),(x+sw,y+rh),tuple(float(v) for v in c),-1); cv2.rectangle(mk,(x,y),(x+sw,y+rh),0,7); x+=sw
        y+=rh
    dist=cv2.distanceTransform(mk,cv2.DIST_L2,5)
    hg=np.clip(dist/16,0,1)**0.6+0.10*fbm((h,w),32,6,8)+0.04*fbm((h,w),35,3,40)
    alb=alb*(0.9+0.1*fbm((h,w),33,5,6))[...,None]; mort=(dist<3)[...,None]; alb=np.where(mort,np.array([0.50,0.43,0.36],np.float32),alb)
    R["wall"]=(alb.astype(np.float32),nrm(hg.astype(np.float32),5.0))
    # carved tuff
    R["carve"]=(tuff_alb(40),nrm(carve_h(41),4.5))
    # chapel: niche + cross + columns
    hg=carve_h(51)*0.6; alb=tuff_alb(50)
    ni=arch_mask(150,570,170,1100,6); hg=hg-ni*3.0
    cr=np.zeros((h,w),np.float32); cv2.rectangle(cr,(338,330),(382,760),1.0,-1); cv2.rectangle(cr,(250,440),(470,484),1.0,-1); cr=cv2.GaussianBlur(cr,(0,0),3)
    hg=hg+cr*1.6
    for cx_ in (110,610):
        col=np.zeros((h,w),np.float32); cv2.rectangle(col,(cx_-34,160),(cx_+34,1280),1.0,-1); col=cv2.GaussianBlur(col,(0,0),8); hg=hg+col*1.2
        alb=alb*(1-col[...,None]*0.1)
    fres=cv2.resize(fbm((40,23),52,3,3),(w,h)); fm=ni[...,None]*np.clip(fres*0.5+0.4,0,1)[...,None]
    alb=alb*(1-fm*0.45)+np.array([0.62,0.28,0.18],np.float32)*fm*0.45
    alb=alb*(1-cr[...,None]*0.15)+np.array([0.9,0.82,0.65],np.float32)*cr[...,None]*0.15
    R["chapel"]=(alb.astype(np.float32),nrm(cv2.GaussianBlur(hg,(0,0),1.0),4.5))
    # doorway wall
    hg=carve_h(61); alb=tuff_alb(60); dm=arch_mask(222,498,600,1060,1.2)
    fr=arch_mask(196,524,574,1072,6)-dm; hg=hg-fr*0.6
    R["door"]=(alb,nrm(hg,4.5)); R["doormask"]=dm
    return R
RCACHE="rel75.npz"
if os.path.exists(RCACHE):
    _z=np.load(RCACHE); REL={k:(_z[k+"_a"],_z[k+"_n"]) for k in ("wall","carve","chapel","door")}; REL["doormask"]=_z["dm"]
else:
    REL=_reliefs(); np.savez(RCACHE,**{k+"_a":REL[k][0] for k in ("wall","carve","chapel","door")},**{k+"_n":REL[k][1] for k in ("wall","carve","chapel","door")},dm=REL["doormask"])
def relief_light(key,lights,amb=0.04):
    alb,N=REL[key]; acc=np.zeros((h,w,3),np.float32)+amb
    for (lx,ly,lz,I,col,rad) in lights:
        Lx=lx-xx; Ly=ly-yy; d2=Lx*Lx+Ly*Ly+lz*lz; inv=1/np.sqrt(d2)
        dif=np.clip((N[0]*Lx+N[1]*Ly+N[2]*lz)*inv,0,1); att=I/(1+d2/(rad*rad))
        acc+=(dif*att)[...,None]*np.array(col,np.float32)
    return alb*acc
# ---------- rolling stone disc ----------
SR_=700
def _stone():
    S2=2*SR_; Yg,Xg=np.mgrid[0:S2,0:S2].astype(np.float32); dx=Xg-SR_; dy=Yg-SR_; r=np.sqrt(dx*dx+dy*dy)/SR_; th=np.arctan2(dy,dx)
    n=cv2.resize(fbm((S2//4,S2//4),901,6,4),(S2,S2)); n2=cv2.resize(fbm((S2//8,S2//8),902,4,3),(S2,S2))
    rings=np.sin(r*95+n2*2.0)*0.5+0.5; rad=np.sin(th*60+n*1.5)*0.5+0.5
    alb=np.array([0.58,0.49,0.40],np.float32)*(0.80+0.16*n+0.08*rings)[...,None]
    alb=alb*(1-0.08*rad*np.clip(r-0.3,0,1))[...,None]
    edge=1.0+0.010*cv2.resize(fbm((1,40),903,2,3),(S2,1))[0][((th+np.pi)/(2*np.pi)*(S2-1)).astype(np.int32)]
    al=np.clip((edge-r)*SR_/2.0,0,1)
    hole=np.clip((r-0.13)*SR_/2.0,0,1); alb=alb*(0.15+0.85*hole[...,None])
    ch=np.clip(fbm((S2//2,S2//2),904,3,12),1.6,2.6)-1.6; ch=cv2.resize(ch,(S2,S2)); alb=alb*(1-0.5*ch[...,None])
    return np.dstack([alb,al]).astype(np.float32)
SCACHE="stone75.npy"
if os.path.exists(SCACHE): STN=np.load(SCACHE)
else: STN=_stone(); np.save(SCACHE,STN)
def draw_disc(b,cx,cy,R,ang,lum=1.0,ldir=(-0.6,-0.8),shadow=0.7,warm=1.0):
    x0,x1=max(0,int(cx-R*1.12)),min(w,int(cx+R*1.12)+1); y0,y1=max(0,int(cy-R*1.12)),min(h,int(cy+R*1.12)+1)
    if x0>=x1 or y0>=y1: return
    M=cv2.getRotationMatrix2D((SR_,SR_),math.degrees(ang),R/SR_); M[0,2]+=cx-SR_-x0; M[1,2]+=cy-SR_-y0
    tex=cv2.warpAffine(STN,M,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
    X=xx[y0:y1,x0:x1]-cx; Y=yy[y0:y1,x0:x1]-cy; r=np.sqrt(X*X+Y*Y)/R+1e-6
    if shadow>0:
        sd=np.exp(-np.clip(r-1.0,0,None)*9.0)*(r>0.98)*shadow; b[y0:y1,x0:x1]*=(1-sd)[...,None]
    rim=sm_np((r-0.86)/0.14); nx=X/(r*R); ny=Y/(r*R); lam=-(nx*ldir[0]+ny*ldir[1])
    hl=sm_np((0.20-r)/0.07)*(r>0.12); lam2=(nx*ldir[0]+ny*ldir[1])
    shade=(1.0+rim*0.9*lam+hl*0.7*lam2)*(0.85-0.25*(Y/R))
    col=tex[...,:3]*shade[...,None]*lum*np.array([1.0,0.82,0.64],np.float32)
    a=tex[...,3:4]; b[y0:y1,x0:x1]=b[y0:y1,x0:x1]*(1-a)+col*a
TRD=0.27; RW=760
def stonewipe(b1,b2,u):
    u=sm(u)*0.9+u*0.1; cx=w+RW-(w+2*RW)*u; cy=h*0.5
    out=np.where((xx>cx)[...,None],b2,b1).astype(np.float32)
    draw_disc(out,cx,cy,RW,-(cx-w/2)/RW,lum=0.8,shadow=0.85)
    return out
# ---------- static map ----------
def _map():
    hg=fbm((h//2,w//2),601,6,3); hg=cv2.resize(hg,(w,h),interpolation=cv2.INTER_CUBIC)
    gx=cv2.Sobel(hg,cv2.CV_32F,1,0,ksize=5); gy=cv2.Sobel(hg,cv2.CV_32F,0,1,ksize=5); shd=np.clip(0.85-(gx*0.5+gy*0.35)*0.25,0.3,1.4)
    k=np.clip(hg*0.25+0.5,0,1)[...,None]
    c=np.array([0.42,0.27,0.16],np.float32)*(1-k)+np.array([0.80,0.58,0.38],np.float32)*k
    b=c*shd[...,None]*0.62*(1-0.5*np.clip(((xx/w-0.5)**2+(yy/h-0.5)**2)*2.5,0,1))[...,None]
    return b.astype(np.float32)
MCACHE="map75.npy"
if os.path.exists(MCACHE): MAPB=np.load(MCACHE)
else: MAPB=_map(); np.save(MCACHE,MAPB)
# ====================================== shots ======================================
def sh_hook(t,end=False):
    tt=t if not end else t-TOTAL
    s=0.86+0.010*tt; cy=760+5*tt; cx=800-4*tt
    b,M=cutview(tt,cx,cy,s,RV(tt))
    motes(b,tt,lambda x,y:0.25 if y>M[1,1]*Y0+M[1,2] else 0.0,0.4,n=80)
    return b,None,1.0
def sh_wall_core(t,stage,u_hit,zoom=1.0,zc=(360,640)):
    lx=110+25*math.sin(t*1.3); I=2.4*flick(t,1)
    b=relief_light("wall",[(lx,640,200,I,(1.0,0.62,0.32),380)],0.03)
    HC=(372,612); g=np.random.default_rng(8)
    if stage>=1:
        for k in range(10):
            a=k*0.63+g.uniform(-0.2,0.2); p=[HC]; x,y=HC; L=min(1.0,[0,0.38,0.72,1.0][min(stage,3)]); nseg=int(16*L)
            for j in range(nseg): a+=g.uniform(-0.45,0.45); x+=math.cos(a)*22; y+=math.sin(a)*22; p.append((x,y))
            if len(p)>1:
                q=np.array(p,np.int32); cv2.polylines(b,[q+2],False,(0.55,0.45,0.35),2,cv2.LINE_AA); cv2.polylines(b,[q],False,(0.04,0.03,0.02),3,cv2.LINE_AA)
    if stage>=3:
        R0=150*eout(u_hit/0.25); th=np.linspace(0,2*math.pi,60,endpoint=False)
        rr=R0*(1+0.22*np.sin(th*3+1)+0.14*np.sin(th*7+2)+0.08*np.sin(th*13))
        poly=np.c_[HC[0]+np.cos(th)*rr,HC[1]+np.sin(th)*rr*1.2].astype(np.int32)
        m=np.zeros((h,w),np.float32); cv2.fillPoly(m,[poly],1.0,cv2.LINE_AA)
        cv2.polylines(b,[poly],True,(0.18,0.12,0.08),16,cv2.LINE_AA)
        tb=tunnel_r(t,TM_T,t*80,torch=0.35*min(1,zoom),far=0.25,ribs=True)
        M=cv2.getRotationMatrix2D((w/2,h*0.47),0,0.42); M[0,2]+=HC[0]-w/2; M[1,2]+=HC[1]-h*0.47
        tb=cv2.warpAffine(tb,M,(w,h),borderMode=cv2.BORDER_REPLICATE)
        b=b*(1-m[...,None])+tb*m[...,None]
    return b
def sh_wall(t):
    hits=[wt(0,"knocked")+0.02,wt(0,"down")+0.02,wt(0,"wall")+0.02]; st=sum(1 for x in hits if t>=x)
    b=sh_wall_core(t,st,t-hits[2])
    g=np.random.default_rng(9)
    for k,ht in enumerate(hits):
        e=t-ht
        if 0<e<1.2:
            glowL(b[...,0],372,612,60+e*260,0.35*(1-e/1.2)); glowL(b[...,1],372,612,60+e*260,0.30*(1-e/1.2)); glowL(b[...,2],372,612,60+e*260,0.25*(1-e/1.2))
            for i in range(14+k*10):
                a=g.uniform(0,2*math.pi); v=g.uniform(150,520); x=372+math.cos(a)*(30+k*40)+math.cos(a)*v*e; y=612+math.sin(a)*(30+k*40)+math.sin(a)*v*e*0.6+900*e*e
                sz=g.uniform(3,9+k*3); cv2.circle(b,(int(x),int(y)),int(sz),(0.55,0.45,0.35),-1,cv2.LINE_AA)
    return b,None,1.04+0.03*(t-wt(0,"knocked"))
def sh_reveal(t):
    u=sm((t-wt(0,"found")+0.1)/1.6)
    cx=lerp(760,850,u); cy=lerp(Y0+120,1500,u); s=lerp(1.9,0.52,eout(u))
    b,M=cutview(t,cx,cy,s,RV(t))
    return b,None,1.0
def sh_people(t):
    u=t-wt(0,"people"); b,M=cutview(t,1215,1060,1.75+0.04*u,RV(t))
    motes(b,t,lambda x,y:0.3,0.35,n=70)
    return b,None,1.0
def sh_village(t):
    u=t-Ls(1); b,M=cutview(t,770,470-u*12,1.45+0.05*u,RV(t,0.15,{11:1.0}))
    def hud(img):
        label(img,"1963",540,300,150,WHITE,a=fa(t,wt(1,"1963")-0.15,99,0.15,0.2))
        label(img,"DERINKUYU · TURKEY",540,430,64,ORANGE,a=fa(t,wt(1,"Derinkuyu")-0.15,99,0.15,0.2),stroke=6)
    return b,hud,1.0
def sh_hole(t):
    u=t-wt(1,"Behind")+0.1; z=1.0+1.6*ein(u/1.6)
    b=sh_wall_core(t,3,5.0,z)
    return camera(b,z,372/w,612/h),None,1.0
def sh_tunnel(t,speed=60,far=0.0,lbl=None):
    b=tunnel_r(t,TM_T,t*speed,torch=0.8,far=far,ribs=True)
    motes(b,t,lambda x,y:max(0,0.6-abs(x-w/2)/600-abs(y-h*0.5)/1000),0.8)
    return camera(b,1.02,0.5,0.47,0,0,2.0*math.sin(t*0.6)),None,1.0
def sh_floors(t):
    u=t-Ls(2); cy=lerp(860,1500,sm(u/3.2)); s=lerp(1.0,0.72,sm(u/3.2))
    ex={k:sm((u-0.15-(k-1)*0.42)/0.2) for k in range(1,9)}; ex[11]=1.0; ex[9]=1.0
    rv=RV(t,0.0,ex); b,M=cutview(t,850,cy,s,rv)
    for k in range(1,9):
        e=u-0.15-(k-1)*0.42
        if 0<e<0.5:
            X,Y=c2s(M,850,LVY[k]-60); glow(b,X,Y,180*s,(1.0,0.55,0.25),0.5*(1-e/0.5))
    mx=0
    for k in range(1,9):
        if ex[k]>0.01: mx=(LVY[k]-Y0)/MPX
    def hud(img): depth_meter(img,M,t,mx,a=fa(t,Ls(2),99,0.2,0.2))
    return b,hud,1.0
def sh_carve(t):
    u=t-wt(2,"carved"); lx=lerp(-80,800,sm(u/2.6)); I=2.6*flick(t,2)
    b=relief_light("carve",[(lx,560+80*math.sin(u),170,I,(1.0,0.62,0.32),300)],0.025)
    motes(b,t,lambda x,y:max(0,1-((x-lx)**2+(y-560)**2)/300**2),1.0)
    def hud(img):
        label(img,"VOLCANIC TUFF",540,300,116,WHITE,a=fa(t,wt(2,"soft")-0.1,99,0.15,0.2))
        label(img,"SOFT ENOUGH FOR HAND TOOLS",540,410,52,ORANGE,a=fa(t,wt(2,"volcanic")-0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.05+0.02*u
def sh_depth(t):
    u=t-Ls(3); s=lerp(0.62,0.405,eout(u/1.4)); cy=lerp(1700,1560,sm(u/1.4))
    ex={k:1.0 for k in range(1,9)}; ex[9]=1; ex[10]=1; ex[11]=1
    b,M=cutview(t,850,cy,s,RV(t,0.0,ex))
    mx=85*sm((t-wt(3,"85")+0.1)/0.9)
    def hud(img):
        depth_meter(img,M,t,max(mx,(LVY[5]-Y0)/MPX*(1-sm((t-wt(3,"85"))/0.3))),a=1.0)
        a1=fa(t,wt(3,"85")-0.1,99,0.15,0.2); label(img,f"{int(round(mx))} M DEEP",600,300,120,WHITE,a=a1)
        a2=fa(t,wt(3,"eight")-0.1,99,0.15,0.2); label(img,"8+ LEVELS",600,420,80,ORANGE,a=a2,stroke=7,sc=0.85+0.15*spring((t-wt(3,"eight")+0.1)/0.25))
        if a2>0:
            for k in range(1,9):
                Y=(M[1,1]*LVY[k]+M[1,2])*K-40;
                if 1050<Y<1430: continue
                a=sm((t-wt(3,"eight")-k*0.06)/0.12); label(img,str(k),1010,Y,40,ORANGE,a=a,stroke=5)
    return b,hud,1.0
def sh_more(t):
    u=t-wt(3,"maybe")+0.1; cy=lerp(1560,2620,sm(u/0.9)); s=lerp(0.405,0.75,sm(u/0.9))
    b,M=cutview(t,850,cy,s,RV(t))
    def hud(img):
        d=ImageDraw.Draw(img); a=sm((u-0.4)/0.3)
        for k,(x0,x1) in enumerate(((520,820),(980,1300),(380,620))):
            yb=2960+k*60; X0,Yb=c2s(M,x0,yb); X1,_=c2s(M,x1,yb)
            if a>0:
                for j in range(0,int(X1-X0),24): d.line((X0*K+j*K,Yb*K,X0*K+(j+12)*K,Yb*K),fill=(255,168,28,int(200*a)),width=4)
        label(img,"SOME SAY 18",540,320,120,ORANGE,a=fa(t,wt(3,"many")-0.15,99,0.15,0.2))
        label(img,"NOT FULLY EXCAVATED",540,440,56,WHITE,a=fa(t,wt(3,"many"),99,0.15,0.2),stroke=6)
    return b,hud,1.0
ROOMS={"stable":(615,850,"STABLES · LEVEL 1"),"kitchen":(820,1084,"KITCHEN"),"wine":(570,1344,"WINE PRESS"),"church":(900,1590,"CHURCH")}
def sh_room(t,key,t0):
    x,y,txt=ROOMS[key]; u=t-t0; s=2.05+0.10*u
    b,M=cutview(t,x+12*u,y,s,RV(t))
    motes(b,t,lambda X,Y:0.3,0.35,n=70)
    def hud(img):
        a=sm((u-0.05)/0.12); label(img,txt,540,1560,58,WHITE,bg=(150,70,20),a=a,sc=0.9+0.1*spring(u/0.25))
    return b,hud,1.0
def sh_pop(t):
    u=t-wt(4,"estimated")+0.1; s=lerp(1.1,0.62,eout(u/2.5)); cy=lerp(1250,1500,sm(u/2.5))
    b,M=cutview(t,850,cy,s,RV(t))
    def hud(img):
        a=fa(t,wt(4,"20,000")-0.1,99,0.15,0.2); label(img,"~20,000",540,300,150,ORANGE,a=a,sc=0.8+0.2*spring((t-wt(4,"20,000")+0.1)/0.25))
        label(img,"+ LIVESTOCK & FOOD",540,430,62,WHITE,a=fa(t,wt(4,"animals")-0.15,99,0.15,0.2),stroke=6)
        label(img,"ESTIMATE",540,1560,44,WHITE,bg=(60,40,30),a=a)
    return b,hud,1.0
def sh_shaft(t):
    u=t-Ls(5); b=tunnel_r(t,TM_C,-u*110,torch=0.25,day=1.0)
    motes(b,t,lambda x,y:max(0,1.2-((x-w/2)**2+(y-h*0.46)**2)/(260**2)),1.6,(0.9,0.95,1.0))
    def hud(img):
        label(img,"FRESH AIR",540,300,124,WHITE,a=fa(t,wt(5,"fresh")-0.15,99,0.15,0.2))
        label(img,"TO THE DEEPEST FLOORS",540,420,60,ORANGE,a=fa(t,wt(5,"deepest")-0.15,99,0.15,0.2),stroke=6)
    return camera(b,1.03,0.5,0.46,0,0,u*14),hud,1.0
def sh_well(t):
    u=t-Ls(6); b=tunnel_r(t,TM_C,u*140,torch=1.0,water=True)
    rx=w/2+18*math.sin(t*1.7)
    cv2.line(b,(int(w/2+6),0),(int(rx),int(h*0.46)),(0.30,0.22,0.15),3,cv2.LINE_AA)
    def hud(img):
        label(img,"HIDDEN WELLS",540,300,124,WHITE,a=fa(t,wt(6,"wells")-0.1,99,0.15,0.2))
        label(img,"NO WAY IN FROM ABOVE",540,420,62,ORANGE,a=fa(t,wt(6,"surface")-0.15,99,0.15,0.2),stroke=6)
    return camera(b,1.03,0.5,0.46,0,0,-u*10),hud,1.0
def sh_wellcut(t):
    u=t-wt(6,"enemies")+0.1; s=lerp(0.70,0.58,sm(u/1.6)); cy=lerp(1500,1700,sm(u/1.6))
    pul=0.8+0.6*(0.5+0.5*math.sin(t*7))
    b,M=cutview(t,560,cy,s,RV(t,0.45,{10:2.0}),hl=(pul*3.0,10))
    X,Y=c2s(M,WLX,LVY[2]); X2,Y2=c2s(M,WLX,2900)
    lay=np.zeros_like(b); cv2.line(lay,(int(X),int(Y)),(int(X2),int(Y2)),(0.3,0.8,1.0),max(2,int(10*s)),cv2.LINE_AA)
    b+=cv2.GaussianBlur(lay,(0,0),6)*pul*0.9+lay*0.5
    def hud(img):
        d=ImageDraw.Draw(img); sx,sy=X*K,(M[1,1]*Y0+M[1,2])*K; a=sm((u-0.2)/0.2)
        if a>0:
            r=40; d.line((sx-r,sy-r,sx+r,sy+r),fill=(235,50,40,int(255*a)),width=14); d.line((sx-r,sy+r,sx+r,sy-r),fill=(235,50,40,int(255*a)),width=14)
        label(img,"POISON-PROOF",620,300,110,(120,220,255),a=fa(t,wt(6,"poison")-0.15,99,0.15,0.2))
    return b,hud,1.0
def sh_raid(t):
    u=t-Ls(7); b,M=cutview(t,880,840-u*10,1.08+0.03*u,RV(t,1.0),night=1.0)
    sy=M[1,1]*(Y0-26)+M[1,2]
    for i in range(7):
        x=(-60+i*95+u*70)%(w+120)-60; fl=flick(t,i)
        glow(b,x,sy+3*math.sin(t*9+i),5,(2.4,1.2,0.4),1.4*fl); glow(b,x,sy,40,(0.9,0.3,0.1),0.45*fl)
        cv2.line(b,(int(x-6),int(sy+6)),(int(x-10),int(sy+52)),(0.02,0.02,0.03),6,cv2.LINE_AA); cv2.circle(b,(int(x-8),int(sy+2)),7,(0.02,0.02,0.03),-1,cv2.LINE_AA)
    def hud(img): label(img,"RAIDERS ABOVE",540,300,116,(255,110,80),a=fa(t,wt(7,"raiders")-0.1,99,0.15,0.2))
    return b,hud,1.0
DOORX0,DOORX1=690,360
def door_x(t):
    t0=wt(7,"rolling")-0.05; e=(t-t0)/1.0
    return lerp(DOORX0,DOORX1,eout(e)) if e<1 else DOORX1
def sh_door(t):
    u=t-wt(7,"rolling")+0.1
    b=relief_light("door",[(90+20*math.sin(t),480,200,2.0*flick(t,3),(1.0,0.62,0.32),340)],0.025)
    tb=tunnel_r(t,TM_T,t*28,torch=0.55,far=0.6,ribs=True)
    M=cv2.getRotationMatrix2D((w/2,h*0.47),0,0.42); M[0,2]+=360-w/2; M[1,2]+=860-h*0.47
    tb=cv2.warpAffine(tb,M,(w,h),borderMode=cv2.BORDER_REPLICATE)
    dm=REL["doormask"][...,None]; b=b*(1-dm)+tb*dm
    cx=door_x(t); R=222; draw_disc(b,cx,1062-R,R,-(cx-DOORX0)/R,lum=0.62,ldir=(-0.8,-0.5),shadow=0.6)
    def hud(img):
        label(img,"UP TO ~500 KG",540,300,120,ORANGE,a=fa(t,wt(7,"half")-0.15,99,0.15,0.2),sc=0.85+0.15*spring((t-wt(7,"half")+0.15)/0.25))
        label(img,"ROLLING STONE DOOR",540,420,62,WHITE,a=fa(t,wt(7,"stone")-0.15,99,0.15,0.2),stroke=6)
    return b,hud,1.03+0.02*u
def sh_inside(t):
    u=t-Ls(8)
    b=relief_light("carve",[(560,900,220,2.2*flick(t,4),(1.0,0.62,0.32),380)],0.025)
    rock=0.04*math.sin(u*5.0)*sm(u/0.4)*(1-sm((u-1.4)/0.4)); cx=360+rock*330
    draw_disc(b,cx,640,330,rock,lum=0.6,ldir=(0.6,0.7),shadow=0.8)
    a=sm((u-0.15)/0.3); hx,hy=cx,640
    if a>0:
        ex,ey=hx+lerp(0,330,a),hy+lerp(0,560,a)
        cv2.line(b,(int(hx),int(hy)),(int(ex),int(ey)),(0.10,0.06,0.03),30,cv2.LINE_AA); cv2.line(b,(int(hx+4),int(hy-6)),(int(ex+4),int(ey-6)),(0.55,0.33,0.15),12,cv2.LINE_AA)
    glow(b,600,1000,200,(0.9,0.45,0.15),0.35*flick(t,5))
    def hud(img):
        label(img,"LOCKED",540,300,140,ORANGE,a=fa(t,Ls(8)+0.05,99,0.15,0.2))
        label(img,"FROM THE INSIDE ONLY",540,425,62,WHITE,a=fa(t,wt(8,"inside")-0.2,99,0.15,0.2),stroke=6)
    return b,hud,1.02+0.02*u
def sh_map(t):
    u=t-Ls(9); b=MAPB.copy(); A=(360,1000); B=(400,420)
    k=sm((u-0.3)/1.6); lay=np.zeros_like(b)
    n=24
    for i in range(n):
        f0=i/n; f1=(i+0.55)/n
        if f0>k: break
        f1=min(f1,k); p0=(lerp(A[0],B[0],f0)+30*math.sin(f0*6),lerp(A[1],B[1],f0)); p1=(lerp(A[0],B[0],f1)+30*math.sin(f1*6),lerp(A[1],B[1],f1))
        cv2.line(lay,(int(p0[0]),int(p0[1])),(int(p1[0]),int(p1[1])),(1.0,0.6,0.2),5,cv2.LINE_AA)
    b+=lay*1.2+cv2.GaussianBlur(lay,(0,0),8)*1.5
    hx=lerp(A[0],B[0],k)+30*math.sin(k*6); hy=lerp(A[1],B[1],k)
    if 0<k<1: glow(b,hx,hy,10,(2.5,1.5,0.6),1.5)
    for (x,y),on in ((A,1.0),(B,sm((u-1.9)/0.3))):
        glow(b,x,y,14,(2.4,1.4,0.6),1.4*max(on,0.2)); glow(b,x,y,60,(1.0,0.5,0.2),0.5*max(on,0.2))
    def hud(img):
        label(img,"~8 KM",540,300,150,ORANGE,a=fa(t,wt(9,"eight")-0.15,99,0.15,0.2))
        label(img,"UNCONFIRMED",540,425,58,WHITE,a=fa(t,wt(9,"said")-0.15,99,0.15,0.2),stroke=6)
        label(img,"DERINKUYU",540,1630,52,WHITE,a=1.0,stroke=6)
        label(img,"KAYMAKLI?",760,630,52,WHITE,a=fa(t,Ls(9)+1.9,99,0.2,0.2),stroke=6)
    return b,hud,1.0+0.02*u
def sh_who(t):
    u=t-Ls(10); b,M=cutview(t,850,1560+u*20,0.42+0.01*u,RV(t,0.5))
    def hud(img): label(img,"BUILDERS UNKNOWN",540,320,100,WHITE,a=fa(t,Ls(10)+0.05,99,0.15,0.2))
    return b,hud,1.0
TL=[("~700 BC",120,"PHRYGIANS?"),("BYZANTINE",540,""),("1923",960,"")]
def timeline(img,a,k):
    if a<=0.01: return
    d=ImageDraw.Draw(img); y=600; al=int(255*a)
    d.line((120,y,960,y),fill=(255,255,255,int(140*a)),width=6); d.line((120,y,120+840*k,y),fill=(255,168,28,al),width=8)
    for i,(tx,x,_) in enumerate(TL):
        on=k*840>=x-120-1
        d.ellipse((x-16,y-16,x+16,y+16),fill=((255,168,28) if on else (200,200,200))+(al,)); label(img,tx,x,y+60,38,WHITE,a=a,stroke=5)
def sh_origin(t):
    u=t-wt(10,"Phrygians")+0.1; lx=lerp(700,-40,sm(u/2.6))
    b=relief_light("carve",[(lx,520,170,2.4*flick(t,6),(1.0,0.62,0.32),300)],0.025)
    b=camera(b,1.0,0.5,0.5,0,0,0)
    motes(b,t,lambda x,y:max(0,1-((x-lx)**2+(y-520)**2)/300**2),1.0)
    def hud(img):
        label(img,"PHRYGIANS?",540,300,124,ORANGE,a=fa(t,wt(10,"Phrygians")-0.1,99,0.15,0.2))
        label(img,"~2,700 YEARS AGO",540,420,60,WHITE,a=fa(t,wt(10,"2,700")-0.15,99,0.15,0.2),stroke=6)
        timeline(img,fa(t,wt(10,"Phrygians"),99,0.2,0.2),0.0)
    return b,hud,1.04+0.02*u
def sh_chapel(t):
    u=t-Ls(11); fl=flick(t,7)
    L=[(360,1150,140,1.8*fl,(1.0,0.62,0.30),330),(150+u*40,640,200,1.1*flick(t,8),(1.0,0.62,0.32),300)]
    b=relief_light("chapel",L,0.03)
    for i,x in enumerate((280,330,390,440)):
        y=1095-(i%2)*14; glow(b,x,y,4,(2.6,1.7,0.8),1.4*flick(t,i)); cv2.rectangle(b,(x-4,y+6),(x+4,y+40),(0.85,0.78,0.62),-1)
    motes(b,t,lambda x,y:max(0,0.8-((x-360)**2+(y-1000)**2)/400**2),0.8)
    def hud(img):
        label(img,"BYZANTINE ERA",540,300,116,WHITE,a=fa(t,Ls(11)+0.05,99,0.15,0.2))
        label(img,"CHURCHES CARVED IN ROCK",540,420,58,ORANGE,a=fa(t,wt(11,"expanded")-0.15,99,0.15,0.2),stroke=6)
        timeline(img,fa(t,Ls(11),99,0.2,0.2),0.5*sm((t-Ls(11))/0.5))
    return b,hud,1.04+0.02*u
def sh_greeks(t):
    u=t-wt(11,"local")+0.1; b,M=cutview(t,1100-u*15,1250,1.25+0.05*u,RV(t))
    motes(b,t,lambda x,y:0.3,0.35,n=70)
    def hud(img):
        label(img,"UNTIL 1923",540,300,130,ORANGE,a=fa(t,wt(11,"until")-0.15,99,0.15,0.2))
        timeline(img,1.0,0.5+0.5*sm((t-wt(11,"1923"))/0.5))
    return b,hud,1.0
def sh_lost(t):
    u=t-Ls(12); ex={}
    for k in range(1,12): ex[k]=1.0-sm((u-0.15-((k-1)%8)*0.16)/0.25)
    b,M=cutview(t,850,1540,0.42+0.006*u,RV(t,0.0,ex))
    motes(b,t,lambda x,y:0.15,0.5)
    yr=1923+int(40*sm((t-wt(12,"forgotten")+0.1)/1.3))
    def hud(img):
        label(img,str(yr),540,300,150,WHITE,a=fa(t,wt(12,"abandoned"),99,0.15,0.2))
        label(img,"40 YEARS OF SILENCE",540,430,64,ORANGE,a=fa(t,wt(12,"forty")-0.2,99,0.15,0.2),stroke=6)
    return b,hud,1.0
def sh_end(t): return sh_hook(t,True)
SHOTS=[(0.0,sh_hook,"cut"),(wt(0,"knocked")-0.06,sh_wall,"cut"),(wt(0,"found")-0.08,sh_reveal,"cut"),(wt(0,"people")-0.1,sh_people,"cut"),
 (Ls(1)-0.25,sh_village,"stone"),(wt(1,"Behind")-0.1,sh_hole,"cut"),(wt(1,"dark")-0.1,lambda t:sh_tunnel(t,240),"cut"),
 (Ls(2)-0.25,sh_floors,"stone"),(wt(2,"carved")-0.1,sh_carve,"cut"),
 (Ls(3)-0.15,sh_depth,"cut"),(wt(3,"maybe")-0.1,sh_more,"cut"),
 (Ls(4)-0.15,lambda t:sh_room(t,"stable",Ls(4)-0.15),"cut"),(wt(4,"kitchens")-0.08,lambda t:sh_room(t,"kitchen",wt(4,"kitchens")-0.08),"cut"),
 (wt(4,"wine")-0.08,lambda t:sh_room(t,"wine",wt(4,"wine")-0.08),"cut"),(wt(4,"churches")-0.08,lambda t:sh_room(t,"church",wt(4,"churches")-0.08),"cut"),
 (wt(4,"estimated")-0.1,sh_pop,"cut"),
 (Ls(5)-0.25,sh_shaft,"stone"),(Ls(6)-0.15,sh_well,"cut"),(wt(6,"enemies")-0.1,sh_wellcut,"cut"),
 (Ls(7)-0.25,sh_raid,"stone"),(wt(7,"rolling")-0.35,sh_door,"cut"),(Ls(8)-0.15,sh_inside,"cut"),
 (Ls(9)-0.25,sh_map,"stone"),(wt(9,"reach")-0.1,lambda t:sh_tunnel(t,900,far=1.0),"cut"),
 (Ls(10)-0.15,sh_who,"cut"),(wt(10,"Phrygians")-0.1,sh_origin,"cut"),
 (Ls(11)-0.15,sh_chapel,"cut"),(wt(11,"local")-0.1,sh_greeks,"cut"),
 (Ls(12)-0.15,sh_lost,"cut"),(Ls(13)-0.3,sh_end,"stone")]
def shot_at(t):
    i=0
    for k,s in enumerate(SHOTS):
        if t>=s[0]: i=k
    return i
SHK=[]
def render_shot(i,t):
    b,hud,z=SHOTS[i][1](t); st=SHOTS[i][0]
    z*=punch(t,[st] if (i>0 and SHOTS[i][2]=="cut") else [],0.06,0.32)
    dx=dy=0.0
    for (t0,amp,dur) in ((wt(0,"knocked")+0.02,7,0.3),(wt(0,"down")+0.02,7,0.3),(wt(0,"wall")+0.02,12,0.45),(wt(7,"rolling")+0.9,10,0.45)):
        d=shake(t,t0,amp,dur); dx+=d[0]; dy+=d[1]
    return camera(b,z,0.5,0.47,dx,dy),hud
def compose(t,fi=None):
    if fi is None: fi=int(round(t*30))
    i=shot_at(max(t,0)); nxt=SHOTS[i+1] if i+1<len(SHOTS) else None; huds=[]
    if nxt and nxt[2]=="stone" and t>nxt[0]-TRD:
        u=(t-(nxt[0]-TRD))/(2*TRD); b1,h1=render_shot(i,t); b2,h2=render_shot(i+1,t); b=stonewipe(b1,b2,u); huds=[h1] if u<0.3 else []
    elif SHOTS[i][2]=="stone" and t<SHOTS[i][0]+TRD and i>0:
        u=(t-(SHOTS[i][0]-TRD))/(2*TRD); b1,h1=render_shot(i-1,t); b2,h2=render_shot(i,t); b=stonewipe(b1,b2,u); huds=[h2] if u>0.7 else []
    else:
        b,h1=render_shot(i,t); huds=[h1]
    b=post(b,bloom=0.5,thr=0.62,tint=(1.04,0.99,0.92))
    img=to_img(b,fi)
    for hf in huds:
        if hf: hf(img)
    ha=1-sm((t-(Ls(1)-0.45))/0.25) if t<Ls(1) else sm((t-(TOTAL-0.55))/0.3)
    if ha>0.01:
        hook_title(img,[("HE BROKE ONE WALL",WHITE)],a=ha,y=250,size=124)
        s2=wt(0,"city")-0.05
        if t>=s2 or t>TOTAL-0.55:
            a2=ha*(sm((t-s2)/0.08) if t<Ls(1) else 1.0); sc=0.7+0.3*spring((t-s2)/0.22) if t<Ls(1) else 1.0
            hook_title(img,[("FOUND A CITY",ORANGE)],a=a2,y=390,size=150,sc=sc)
    return finish(img,CAP,t)
if __name__=="__main__":
    import time
    for tt in map(float,sys.argv[1:]):
        t0=time.time(); compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85); print(tt,round(time.time()-t0,2))
