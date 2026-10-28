import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid73"); sys.path.insert(0,"/home/claude/toolkit")
from pro import *
from PIL import Image, ImageDraw
T,LINES,SC,TOTAL=load("timeline.json")
CAP=Captions(LINES); WD=CAP.W
def wt(li,sub,o=0.0): return word_t(WD,li,sub,o)
def Ls(i): return LINES[i]["s"]
def sm_np(x): x=np.clip(x,0,1); return x*x*(3-2*x)
# ================= Suez 1967 "Yellow Fleet": cinematic desert aerials + animated map/infographics, sandstorm wipes =================
WS=2048
def canal_x(y): return WS*0.5+90*np.sin(y/520.0)+30*np.sin(y/170.0+1)
LAKE=(WS*0.5,WS*0.56,420,250)
def _world():
    yy2,xx2=np.mgrid[0:WS,0:WS].astype(np.float32)
    hgt=fbm((WS//4,WS//4),731,6,3); hgt=cv2.resize(hgt,(WS,WS),interpolation=cv2.INTER_CUBIC)
    rip=np.sin((xx2*0.9+yy2*0.4)/9.0+hgt*6)*0.08
    H=hgt*0.9+rip
    gx=cv2.Sobel(H,cv2.CV_32F,1,0,ksize=5); gy=cv2.Sobel(H,cv2.CV_32F,0,1,ksize=5)
    shade=np.clip(0.75-(gx*0.6+gy*0.35)*0.9,0.25,1.4)
    sand=np.array([0.80,0.60,0.34],np.float32)*shade[...,None]
    cx=canal_x(yy2); band=np.abs(xx2-cx)
    lk=((xx2-LAKE[0])/LAKE[2])**2+((yy2-LAKE[1])/LAKE[3])**2+cv2.resize(fbm((64,64),732,4,3),(WS,WS))*0.12
    water=np.clip(np.maximum(sm_np((44-band)/4),sm_np((1.0-lk)/0.04)),0,1)
    bank=np.clip(np.maximum(sm_np((70-band)/12),sm_np((1.12-lk)/0.08)),0,1)*(1-water)
    deep=np.clip(1-lk,0,1)**0.5
    wcol=np.array([0.10,0.48,0.52],np.float32)*(1-deep[...,None]*0.6)+np.array([0.02,0.20,0.32],np.float32)*deep[...,None]*0.6
    img=sand*(1-bank[...,None])+np.array([0.62,0.50,0.32],np.float32)*bank[...,None]
    img=img*(1-water[...,None])+wcol*water[...,None]
    return img.astype(np.float32),water.astype(np.float32)
CACHE="world73.npz"
if os.path.exists(CACHE): _z=np.load(CACHE); WORLD,WMASK=_z["a"],_z["b"]
else: WORLD,WMASK=_world(); np.savez(CACHE,a=WORLD,b=WMASK)
def aerial_M(cx,cy,scale,tilt=1.0,hor=0.26):
    yh=h*hor; hw=WS*0.28*scale; near=WS*0.11*scale
    src=np.float32([[cx-hw,cy-WS*0.40*scale*tilt],[cx+hw,cy-WS*0.40*scale*tilt],[cx+near,cy+WS*0.10*scale],[cx-near,cy+WS*0.10*scale]])
    dst=np.float32([[-w*0.25,yh],[w*1.25,yh],[w,h],[0,h]]); return cv2.getPerspectiveTransform(src,dst),yh
SKYG=None
SPK=fbm((h,w),77,3,60); _YH=[0]
def aerial(t,cx,cy,scale,sky=((0.25,0.40,0.62),(0.95,0.78,0.55)),hor=0.26,night=0.0,glint=1.0):
    M,yh=aerial_M(cx,cy,scale,hor=hor)
    b=cv2.warpPerspective(WORLD,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    wm=cv2.warpPerspective(WMASK,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    k=np.clip((yy-yh)/(h-yh),0,1)
    sp=np.roll(SPK,(int(t*7),int(t*11)),(0,1)); sp=np.clip(sp-2.1,0,1)*0.8
    b=b+(wm*sp*0.9*glint*np.clip(k*1.5,0,1))[...,None]*np.array([1.0,0.9,0.7],np.float32)
    _YH[0]=yh
    hz=np.exp(-k*3.5)[...,None]; top,bot=[np.array(c,np.float32) for c in sky]
    b=b*(1-hz*0.8)+bot*hz*0.8
    kk=np.clip(yy/yh,0,1)[...,None]; skyimg=top*(1-kk)+bot*kk
    b=np.where((yy<yh)[...,None],skyimg,b)
    if night>0: b=b*(1-night*0.75)+np.array([0.02,0.04,0.10],np.float32)*night
    return b,M
def proj(M,pts):
    p=cv2.perspectiveTransform(np.array([pts],np.float32),M)[0]; return p
def ship_top(b,M,x,y,L,ang=-math.pi/2,sandk=0.0,hullc=(0.12,0.10,0.10),a=1.0):
    ca,sa=math.cos(ang),math.sin(ang); W_=L*0.16
    def P(u,v): return (x+u*ca-v*sa, y+u*sa+v*ca)
    hull=[P(L*0.5,0),P(L*0.36,W_*0.5),P(-L*0.5,W_*0.5),P(-L*0.5,-W_*0.5),P(L*0.36,-W_*0.5)]
    shd=[(px+6,py+8) for px,py in hull]
    deck=[P(L*0.42,0),P(L*0.32,W_*0.38),P(-L*0.46,W_*0.38),P(-L*0.46,-W_*0.38),P(L*0.32,-W_*0.38)]
    sup=[P(-L*0.30,W_*0.33),P(-L*0.44,W_*0.33),P(-L*0.44,-W_*0.33),P(-L*0.30,-W_*0.33)]
    dc=np.array([0.50,0.42,0.33])*(1-sandk)+np.array([0.85,0.68,0.40])*sandk
    sc=np.array([0.92,0.92,0.90])*(1-sandk)+np.array([0.90,0.75,0.48])*sandk
    lay=b.copy()
    for poly_,c in ((shd,(0.0,0.0,0.0)),(hull,hullc),(deck,tuple(dc)),(sup,tuple(sc))):
        q=proj(M,poly_).astype(np.int32)
        if poly_ is shd: cv2.fillPoly(lay,[q],c,cv2.LINE_AA); lay=cv2.addWeighted(lay,0.6,b,0.4,0) if False else lay
        else: cv2.fillPoly(lay,[q],c,cv2.LINE_AA)
    for k in range(4):
        u0=L*(0.25-k*0.14); q=proj(M,[P(u0,W_*0.24),P(u0-L*0.09,W_*0.24),P(u0-L*0.09,-W_*0.24),P(u0,-W_*0.24)]).astype(np.int32)
        cv2.fillPoly(lay,[q],tuple(np.array(dc)*0.6),cv2.LINE_AA)
    m=(yy>_YH[0]+2)[...,None]*a; b[:]=b*(1-m)+lay*m
# ---------- side-view ship + crowd ----------
def ship_side(b,x,y,s,sandk=0.0,col=(0.06,0.06,0.07)):
    hull=np.array([(x-1.0*s,y-0.12*s),(x+1.05*s,y-0.12*s),(x+0.92*s,y+0.10*s),(x-0.95*s,y+0.10*s)],np.int32)
    cv2.fillPoly(b,[hull],col,cv2.LINE_AA)
    sup=tuple(np.array([0.85,0.84,0.80])*(1-sandk)+np.array([0.80,0.62,0.35])*sandk)
    cv2.rectangle(b,(int(x-0.82*s),int(y-0.36*s)),(int(x-0.45*s),int(y-0.12*s)),sup,-1)
    cv2.rectangle(b,(int(x-0.72*s),int(y-0.50*s)),(int(x-0.56*s),int(y-0.36*s)),(0.2,0.1,0.08),-1)
    for mx in (-0.15,0.25,0.65):
        cv2.line(b,(int(x+mx*s),int(y-0.12*s)),(int(x+mx*s),int(y-0.45*s)),col,max(2,int(s*0.02)),cv2.LINE_AA)
        cv2.line(b,(int(x+mx*s),int(y-0.42*s)),(int(x+(mx+0.18)*s),int(y-0.14*s)),col,max(1,int(s*0.01)),cv2.LINE_AA)
def crowd(b,t,y0,n=90,col=(0.02,0.02,0.03)):
    g=np.random.default_rng(5)
    for i in range(n):
        x=g.uniform(-10,w+10); s=g.uniform(14,22); y=y0+g.uniform(0,40)
        cv2.circle(b,(int(x),int(y-s*1.6)),int(s*0.42),col,-1,cv2.LINE_AA)
        cv2.ellipse(b,(int(x),int(y)),(int(s*0.6),int(s*1.1)),0,180,360,col,-1,cv2.LINE_AA)
        if g.random()<0.45:
            a=-1.9+0.5*math.sin(t*8+i)
            cv2.line(b,(int(x+s*0.3),int(y-s*0.9)),(int(x+s*0.3+math.cos(a)*s*1.2),int(y-s*0.9+math.sin(a)*s*1.2)),col,max(2,int(s*0.18)),cv2.LINE_AA)
    cv2.rectangle(b,(0,int(y0+30)),(w,h),col,-1)
# ---------- flags (PIL, full-res) ----------
def flag(d,code,x,y,fw,fh,a=255):
    def R(x0,y0,x1,y1,c): d.rectangle((x+x0*fw,y+y0*fh,x+x1*fw,y+y1*fh),fill=c+(a,))
    if code=="DE": R(0,0,1,1/3,(10,10,10)); R(0,1/3,1,2/3,(221,0,0)); R(0,2/3,1,1,(255,206,0))
    elif code=="PL": R(0,0,1,0.5,(245,245,245)); R(0,0.5,1,1,(220,20,60))
    elif code=="BG": R(0,0,1,1/3,(245,245,245)); R(0,1/3,1,2/3,(0,150,110)); R(0,2/3,1,1,(214,38,18))
    elif code=="FR": R(0,0,1/3,1,(0,35,149)); R(1/3,0,2/3,1,(245,245,245)); R(2/3,0,1,1,(237,41,57))
    elif code=="SE": R(0,0,1,1,(0,106,167)); R(0.31,0,0.44,1,(254,204,0)); R(0,0.42,1,0.58,(254,204,0))
    elif code=="CS": R(0,0,1,0.5,(245,245,245)); R(0,0.5,1,1,(215,20,26)); d.polygon([(x,y),(x+fw*0.5,y+fh*0.5),(x,y+fh)],fill=(17,69,126,a))
    elif code=="US":
        for k in range(13): R(0,k/13,1,(k+1)/13,(178,34,52) if k%2==0 else (245,245,245))
        R(0,0,0.4,7/13,(60,59,110))
        for i in range(5):
            for j in range(4): d.ellipse((x+fw*(0.04+i*0.075),y+fh*(0.05+j*0.12),x+fw*(0.04+i*0.075)+5,y+fh*(0.05+j*0.12)+5),fill=(255,255,255,a))
    elif code=="GB":
        R(0,0,1,1,(1,33,105)); lw=fh*0.2
        d.line((x,y,x+fw,y+fh),fill=(255,255,255,a),width=int(lw)); d.line((x,y+fh,x+fw,y),fill=(255,255,255,a),width=int(lw))
        d.line((x,y,x+fw,y+fh),fill=(200,16,46,a),width=int(lw*0.35)); d.line((x,y+fh,x+fw,y),fill=(200,16,46,a),width=int(lw*0.35))
        R(0.42,0,0.58,1,(255,255,255)); R(0,0.36,1,0.64,(255,255,255)); R(0.45,0,0.55,1,(200,16,46)); R(0,0.41,1,0.59,(200,16,46))
    d.rectangle((x,y,x+fw,y+fh),outline=(20,20,20,a),width=3)
# ---------- shots ----------
CONVOY=[(i,canal_x(WS*0.98-i*140)) for i in range(7)]
def convoy(b,M,t,speed=14,sandk=0.0,n=7,y0=None):
    for i in range(n):
        y=(y0 if y0 else WS*0.95)-i*150-t*speed; x=float(canal_x(y))
        x2=float(canal_x(y-30)); ang=math.atan2(-30,x2-x)
        ship_top(b,M,x,y,100,ang,sandk)
def sh_hook(t,end=False):
    tt=t if not end else t-TOTAL
    cy=WS*0.78-tt*10; b,M=aerial(tt,WS*0.5,cy,0.95,sky=((0.30,0.45,0.70),(1.0,0.80,0.55)))
    convoy(b,M,tt+3)
    glow(b,w*0.80,h*0.25,40,(2.2,1.6,0.9),0.9); glow(b,w*0.80,h*0.25,200,(0.8,0.5,0.25),0.5)
    return b,None,1.02+0.03*sm((tt+0.0)/5)
def sh_war(t):
    u=t-Ls(1); b,M=aerial(t,WS*0.5,WS*0.72,0.95,sky=((0.02,0.03,0.08),(0.15,0.12,0.20)),night=0.85,glint=0.2)
    convoy(b,M,t,speed=0)
    for k,(fx,fy,ft) in enumerate(((0.25,0.30,0.4),(0.70,0.28,1.3),(0.45,0.27,2.2),(0.85,0.32,3.0))):
        e=t-Ls(1)-ft
        if 0<e<1.2: glow(b,w*fx,h*fy,10+60*eout(e/0.3),(2.5,1.5,0.6),1.6*(1-e/1.2)); glow(b,w*fx,h*fy,150,(0.8,0.4,0.15),0.6*(1-e/1.2))
    def hud(img): label(img,"JUNE 1967",540,300,124,WHITE,a=fa(t,Ls(1)+0.1,99,0.2,0.2)); label(img,"SIX-DAY WAR",540,420,70,ORANGE,a=fa(t,wt(1,"war")-0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.04*u
# ---- schematic animated map (full-res HUD on dark canvas) ----
def mapbg():
    b=np.zeros((h,w,3),np.float32)+np.array([0.80,0.66,0.44],np.float32)*0.55
    n=cv2.resize(fbm((80,45),740,4,3),(w,h)); b*= (0.9+0.08*n)[...,None]
    cv2.fillPoly(b,[np.array([(0,0),(w,0),(w,int(h*0.16)),(int(w*0.6),int(h*0.20)),(int(w*0.3),int(h*0.17)),(0,int(h*0.19))],np.int32)],(0.05,0.22,0.40),cv2.LINE_AA)
    cv2.fillPoly(b,[np.array([(int(w*0.40),h),(int(w*0.47),int(h*0.86)),(int(w*0.56),int(h*0.84)),(int(w*0.72),h)],np.int32)],(0.05,0.22,0.40),cv2.LINE_AA)
    return b
MAPPTS=[(540,330),(560,520),(530,700),(548,900),(560,1120),(560,1290)]   # full-res canal polyline Port Said -> Suez
def map_canal(d,a=255,blocked=0.0,lake=1.0,timsah=1.0):
    d.line(MAPPTS,fill=(40,140,170,a),width=16,joint="curve")
    d.ellipse((540-110*lake,880-62*lake,540+110*lake,880+62*lake),fill=(40,140,170,a))
    d.ellipse((520-34,690-22,520+34,690+22),fill=(40,140,170,a))
def sh_map(t,phase=0):
    b=mapbg()
    def hud(img):
        d=ImageDraw.Draw(img)
        map_canal(d)
        label(img,"MEDITERRANEAN",540,150,40,(220,235,255),stroke=5); label(img,"RED SEA",660,1500,44,(220,235,255),stroke=5)
        label(img,"PORT SAID",760,420,36,WHITE,stroke=5); label(img,"SUEZ",720,1290,36,WHITE,stroke=5)
        if phase==0:
            a=sm((t-wt(1,"sealed"))/0.2); sc=1.4-0.4*spring((t-wt(1,"sealed"))/0.25)
            for (x,y) in ((540,380),(560,1250)):
                if a>0:
                    r=40*sc; d.line((x-r,y-r,x+r,y+r),fill=(230,40,40,int(255*a)),width=14); d.line((x-r,y+r,x+r,y-r),fill=(230,40,40,int(255*a)),width=14)
            label(img,"CANAL CLOSED",540,280,96,(255,90,80),a=a*fa(t,0,Ls(2)-0.3,0.01,0.2))
        if phase>=1:
            for (x,y) in ((540,380),(560,1250)): d.line((x-40,y-40,x+40,y+40),fill=(230,40,40,255),width=14); d.line((x-40,y+40,x+40,y-40),fill=(230,40,40,255),width=14)
            n=int(min(14,max(0,(t-Ls(2)-0.2)/0.12))) if phase==1 else 14
            g=np.random.default_rng(14)
            for i in range(n):
                ang=g.uniform(0,2*math.pi); r=g.uniform(0,1)**0.5
                x=540+math.cos(ang)*r*85; y=880+math.sin(ang)*r*45
                d.ellipse((x-9,y-9,x+9,y+9),fill=(255,206,60,255),outline=(40,30,10,255),width=3)
            label(img,"GREAT BITTER LAKE",540,1010,46,WHITE,stroke=5)
            if phase==1: label(img,f"{n} SHIPS",540,330,130,ORANGE,a=fa(t,Ls(2)+0.1,99,0.15,0.2))
        if phase==2:
            a=sm((t-Ls(3)-0.3)/0.25); x,y=520,690
            d.ellipse((x-11,y-11,x+11,y+11),fill=(255,206,60,int(255*a)),outline=(40,30,10,int(255*a)),width=3)
            r=30+20*(0.5+0.5*math.sin(t*6)); d.ellipse((x-r,y-r,x+r,y+r),outline=(255,206,60,int(200*a)),width=4)
            label(img,"LAKE TIMSAH",330,690,46,WHITE,a=a,stroke=5); label(img,"+1 ALONE",540,330,120,ORANGE,a=a)
    z=1.0+(0.25*sm((t-Ls(2))/1.5) if phase==1 else (0.0 if phase==0 else 0.18))
    return b,hud,1.0
def sh_yellow(t):
    u=t-Ls(4); yrs=1967+int(8*sm((u-0.3)/3.0)); sandk=sm((u-0.2)/3.0)*0.85
    sunp=(u*0.8)%1.0
    b,M=aerial(t,LAKE[0],LAKE[1]+330,0.85,sky=((0.30,0.45,0.70),(1.0,0.82,0.58)),hor=0.18)
    g=np.random.default_rng(7)
    for i in range(14):
        a=g.uniform(0,2*math.pi); r=g.uniform(0.15,0.8)**0.6
        ship_top(b,M,LAKE[0]+math.cos(a)*r*LAKE[2]*0.75,LAKE[1]+math.sin(a)*r*LAKE[3]*0.75,70,-math.pi/2+0.5+g.normal(0,0.15),sandk)
    def hud(img):
        label(img,str(yrs),540,300,150,WHITE,a=fa(t,Ls(4)+0.1,99,0.2,0.2))
        label(img,"THE YELLOW FLEET",540,430,84,(255,206,60),a=fa(t,wt(4,"Yellow")-0.1,99,0.15,0.2),sc=0.85+0.15*spring((t-wt(4,"Yellow")+0.1)/0.2))
    return b,hud,1.0+0.03*u
CODES=["GB","DE","SE","PL","BG","CS","FR","US"]
def sh_crews(t):
    b=np.zeros((h,w,3),np.float32)+np.array([0.06,0.07,0.10],np.float32); glow(b,w*0.5,h*0.45,320,(0.3,0.25,0.18),0.5)
    def hud(img):
        d=ImageDraw.Draw(img); u=t-Ls(5)
        label(img,"8 COUNTRIES",540,300,124,WHITE,a=fa(t,wt(5,"eight")-0.1,99,0.15,0.2))
        for i,c in enumerate(CODES):
            a=sm((u-0.3-i*0.12)/0.2)
            if a<=0: continue
            col,row=i%2,i//2; x=180+col*380; y=470+row*190; fw,fh=330,160
            sc=0.8+0.2*spring((u-0.3-i*0.12)/0.25); fw2,fh2=fw*sc,fh*sc
            flag(d,c,x+(fw-fw2)/2,y+(fh-fh2)/2,fw2,fh2,int(255*a))
        a=fa(t,wt(5,"Cold")-0.1,99,0.15,0.2)
        if a>0: label(img,"EAST  ×  WEST",540,1260+0,60,ORANGE,a=a,stroke=6)
    return b,hud,1.0
def sh_assoc(t):
    u=t-Ls(6); b,M=aerial(t,LAKE[0],LAKE[1]+300,0.80,sky=((0.25,0.35,0.6),(0.95,0.70,0.45)),hor=0.16)
    g=np.random.default_rng(7); pts=[]
    for i in range(14):
        a=g.uniform(0,2*math.pi); r=g.uniform(0.15,0.8)**0.6; x=LAKE[0]+math.cos(a)*r*LAKE[2]*0.75; y=LAKE[1]+math.sin(a)*r*LAKE[3]*0.75
        ship_top(b,M,x,y,70,-math.pi/2+0.5+g.normal(0,0.15),0.5); pts.append(proj(M,[(x,y)])[0])
    k=sm((u-0.3)/1.5); lay=np.zeros_like(b)
    for i in range(14):
        for j in range(i+1,14):
            if (i*7+j)%4==0 and k>(i+j)/28:
                cv2.line(lay,(int(pts[i][0]),int(pts[i][1])),(int(pts[j][0]),int(pts[j][1])),(1.0,0.75,0.3),2,cv2.LINE_AA)
    b+=lay*0.9+cv2.GaussianBlur(lay,(0,0),4)*0.8
    def hud(img):
        a=fa(t,wt(6,"Great")-0.1,99,0.15,0.2); label(img,"GREAT BITTER LAKE",540,300,92,WHITE,a=a); label(img,"ASSOCIATION · 1967",540,400,64,ORANGE,a=a,stroke=6)
    return b,hud,1.0+0.03*u
def sh_life(t):
    u=t-Ls(7); k=(yy/h)[...,None]; b=np.array([0.20,0.22,0.40],np.float32)*(1-k)+np.array([1.0,0.62,0.35],np.float32)*k
    hor=int(h*0.56); glow(b,w*0.5,hor-30,60,(2.2,1.3,0.6),1.0); glow(b,w*0.5,hor-20,260,(0.8,0.4,0.2),0.6)
    cv2.rectangle(b,(0,hor),(w,h),(0.30,0.22,0.20),-1)
    for i in range(30):
        y=hor+8+i*i*0.9; cv2.line(b,(0,int(y)),(w,int(y)),(0.55+0.4*math.sin(i+t*2)*0.2,0.38,0.28),1)
    glow(b,w*0.5,hor+60,90,(0.9,0.5,0.2),0.5)
    ship_side(b,w*0.18,hor+20,140,0.6); ship_side(b,w*0.86,hor+30,120,0.6)
    bx=w*(0.32+0.38*sm(u/3.0)); cv2.ellipse(b,(int(bx),hor+90),(38,10),0,0,180,(0.04,0.03,0.03),-1,cv2.LINE_AA)
    cv2.rectangle(b,(int(bx-12),hor+76),(int(bx+10),hor+88),(0.04,0.03,0.03),-1)
    def hud(img):
        label(img,"SHARED EVERYTHING",540,300,96,WHITE,a=fa(t,Ls(7)+0.1,99,0.2,0.2))
        label(img,"CHURCH ON THE NORDWIND",540,410,50,ORANGE,a=fa(t,wt(7,"church")-0.1,99,0.15,0.2),stroke=5)
    return b,hud,1.0+0.02*u
def sh_games(t):
    u=t-Ls(8); k=(yy/h)[...,None]; b=np.array([0.25,0.45,0.75],np.float32)*(1-k)+np.array([0.75,0.85,0.95],np.float32)*k
    hor=int(h*0.50); cv2.rectangle(b,(0,hor),(w,h),(0.10,0.42,0.50),-1)
    for i in range(40): cv2.line(b,(0,hor+6+i*i),(w,hor+6+i*i),(0.2,0.55,0.62),1)
    for i in range(4):
        x=(w*(0.1+0.22*i)+u*(40+i*8))%(w+80)-40; y=hor+60+i*70
        cv2.fillPoly(b,[np.array([(x,y-90-i*8),(x,y),(x+50+i*5,y)],np.int32)],(0.97,0.97,0.95),cv2.LINE_AA)
        cv2.ellipse(b,(int(x+20),int(y+6)),(46,9),0,0,180,(0.75,0.15,0.12),-1,cv2.LINE_AA)
    ship_side(b,w*0.80,hor+15,90,0.4,(0.08,0.08,0.09))
    def hud(img):
        d=ImageDraw.Draw(img)
        label(img,"BITTER LAKE",540,280,104,WHITE,a=fa(t,wt(8,"Olympics")-0.15,99,0.15,0.2)); label(img,"OLYMPICS · 1968",540,390,70,ORANGE,a=fa(t,wt(8,"Olympics")-0.15,99,0.15,0.2),stroke=6)
        for i,(sub,txt) in enumerate((("sailing","SAILING"),("diving","DIVING"),("archery","ARCHERY"))):
            a=sm((t-wt(8,sub)+0.05)/0.15)
            if a>0:
                x=200+i*340; y=1010
                d.ellipse((x-58,y-58,x+58,y+58),fill=(255,206,60,int(240*a)),outline=(120,80,10,int(255*a)),width=6)
                label(img,txt,x,y+100,40,WHITE,a=a,stroke=5)
                if txt=="ARCHERY":
                    for r_,c_ in ((40,(255,255,255)),(28,(220,40,40)),(14,(255,255,255)),(6,(220,40,40))): d.ellipse((x-r_,y-r_,x+r_,y+r_),fill=c_+(int(255*a),))
                elif txt=="SAILING": d.polygon([(x-10,y-38),(x-10,y+25),(x+30,y+25)],fill=(255,255,255,int(255*a))); d.rectangle((x-30,y+28,x+34,y+38),fill=(255,255,255,int(255*a)))
                else:
                    d.ellipse((x-10,y-40,x+10,y-20),fill=(255,255,255,int(255*a))); d.line((x,y-20,x+18,y+30),fill=(255,255,255,int(255*a)),width=12)
    return b,hud,1.0+0.02*u
def sh_podium(t):
    b=np.zeros((h,w,3),np.float32)+np.array([0.05,0.06,0.10],np.float32); glow(b,w*0.5,h*0.55,300,(0.45,0.35,0.15),0.6)
    def hud(img):
        d=ImageDraw.Draw(img); u=t-Ls(9)
        for rank,code,x,hh,t0,col in ((1,"PL",540,360,0.0,(255,206,60)),(2,"DE",250,260,wt(9,"West")-Ls(9),(210,210,220)),(3,"GB",830,190,wt(9,"second")-Ls(9)+0.2,(205,127,50))):
            a=sm((u-t0)/0.2)
            if a<=0: continue
            hh2=hh*eout((u-t0)/0.35); y1=1180
            d.rectangle((x-130,y1-hh2,x+130,y1),fill=col+(int(255*a),)); label(img,str(rank),x,y1-hh2/2,110,(30,30,40),a=a,stroke=0)
            flag(d,code,x-90,y1-hh2-150,180,110,int(255*a))
        label(img,"POLAND WINS",540,300,120,ORANGE,a=fa(t,Ls(9),99,0.15,0.2))
    return b,hud,1.0
def sh_stamp(t):
    b=np.zeros((h,w,3),np.float32)+np.array([0.80,0.74,0.62],np.float32); n=cv2.resize(fbm((64,36),750,4,3),(w,h)); b*=(0.92+0.05*n)[...,None]
    u=t-Ls(10)
    def hud(img):
        d=ImageDraw.Draw(img); a=sm(u/0.3); x0,y0,x1,y1=230,470,850,1130; sc=0.9+0.1*spring(u/0.3)
        cx,cy=540,800; W2,H2=(x1-x0)*sc/2,(y1-y0)*sc/2; x0,x1,y0,y1=cx-W2,cx+W2,cy-H2,cy+H2
        d.rectangle((x0,y0,x1,y1),fill=(250,246,236,int(255*a)))
        for k in range(26):
            for (px,py) in ((x0+k*(x1-x0)/25,y0),(x0+k*(x1-x0)/25,y1)): d.ellipse((px-9,py-9,px+9,py+9),fill=(205,190,160,int(255*a)))
        for k in range(33):
            for (px,py) in ((x0,y0+k*(y1-y0)/32),(x1,y0+k*(y1-y0)/32)): d.ellipse((px-9,py-9,px+9,py+9),fill=(205,190,160,int(255*a)))
        d.rectangle((x0+40,y0+40,x1-40,y1-40),fill=(30,95,120,int(255*a)))
        d.rectangle((x0+40,y0+380,x1-40,y1-40),fill=(225,190,110,int(255*a)))
        d.polygon([(x0+110,y0+400),(x1-90,y0+400),(x1-130,y0+460),(x0+140,y0+460)],fill=(40,30,25,int(255*a)))
        d.rectangle((x0+150,y0+330,x0+300,y0+400),fill=(240,240,235,int(255*a))); d.rectangle((x0+190,y0+290,x0+240,y0+330),fill=(120,40,30,int(255*a)))
        label(img,"GREAT BITTER LAKE",540,y0+110,48,WHITE,a=a,stroke=0); label(img,"ASSOCIATION",540,y0+170,48,WHITE,a=a,stroke=0)
        ps=sm((t-wt(10,"letters")+0.1)/0.15)
        if ps>0:
            r=150; cx2,cy2=720,1000; d.ellipse((cx2-r,cy2-r,cx2+r,cy2+r),outline=(170,30,30,int(220*ps)),width=10)
            label(img,"DELIVERED",cx2,cy2,46,(170,30,30),a=ps,stroke=0)
        label(img,"THEIR OWN STAMPS",540,300,100,(40,30,25),a=fa(t,wt(10,"stamps")-0.1,99,0.15,0.2),stroke=0)
    return b,hud,1.0+0.02*u
def sh_reopen(t):
    u=t-Ls(11); b,M=aerial(t,WS*0.5,WS*0.62-u*25,0.95,sky=((0.30,0.48,0.75),(0.95,0.85,0.65)))
    for i,y in enumerate((WS*0.62,WS*0.50)):
        yy_=y-u*35; ship_top(b,M,float(canal_x(yy_)),yy_,100,-math.pi/2,0.85)
    def hud(img):
        label(img,"JUNE 1975",540,300,124,WHITE,a=fa(t,wt(11,"1975")-0.1,99,0.15,0.2)); label(img,"8 YEARS LATER",540,420,70,ORANGE,a=fa(t,wt(11,"1975")+0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
def sh_home(t):
    u=t-Ls(12); k=(yy/h)[...,None]; b=np.array([0.10,0.12,0.25],np.float32)*(1-k)+np.array([0.95,0.55,0.35],np.float32)*k
    hor=int(h*0.62); cv2.rectangle(b,(0,hor),(w,h),(0.38,0.26,0.28),-1)
    for i in range(30): cv2.line(b,(0,hor+4+i*i//2),(w,hor+4+i*i//2),(0.55,0.36,0.32),1)
    for x0_,ww,hh in ((0,90,120),(80,60,200),(140,110,90),(470,70,170),(540,120,110),(650,80,150)): cv2.rectangle(b,(x0_,hor-hh),(x0_+ww,hor),(0.16,0.13,0.20),-1)
    for x_ in (120,520,660): cv2.line(b,(x_,hor-200),(x_+90,hor-260),(0.16,0.13,0.20),6); cv2.line(b,(x_,hor),(x_,hor-200),(0.16,0.13,0.20),6)
    sx=w*(1.15-0.62*sm(u/3.5)); ship_side(b,sx,hor+90,260,0.85,(0.05,0.05,0.07))
    if u>0.4:
        for i in range(6):
            e=(u-0.4-i*0.15)%1.2; glow(b,sx-0.64*260+e*20,hor+90-0.5*260-e*90,10+e*25,(0.6,0.6,0.62),0.5*(1-e/1.2))
    crowd(b,t,int(h*0.86))
    def hud(img):
        label(img,"ONLY 2 OF 15",540,300,120,ORANGE,a=fa(t,wt(12,"two")-0.1,99,0.15,0.2))
        label(img,"HAMBURG · 1975",540,420,70,WHITE,a=fa(t,wt(12,"Hamburg")-0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.02*u
def sh_end(t): return sh_hook(t,True)
SHOTS=[(0.0,sh_hook,"cut"),(Ls(1)-0.25,sh_war,"sand"),(wt(1,"sealed")-0.2,lambda t:sh_map(t,0),"cut"),(Ls(2)-0.1,lambda t:sh_map(t,1),"cut"),
 (Ls(3)-0.1,lambda t:sh_map(t,2),"cut"),(Ls(4)-0.25,sh_yellow,"sand"),(Ls(5)-0.25,sh_crews,"sand"),(Ls(6)-0.15,sh_assoc,"cut"),
 (Ls(7)-0.2,sh_life,"cut"),(Ls(8)-0.25,sh_games,"sand"),(Ls(9)-0.15,sh_podium,"cut"),(Ls(10)-0.25,sh_stamp,"sand"),
 (Ls(11)-0.25,sh_reopen,"sand"),(Ls(12)-0.15,sh_home,"cut"),(Ls(13)-0.3,sh_end,"sand")]
TR=0.22
def shot_at(t):
    i=0
    for k,s in enumerate(SHOTS):
        if t>=s[0]: i=k
    return i
def render_shot(i,t):
    b,hud,z=SHOTS[i][1](t); st=SHOTS[i][0]
    z*=punch(t,[st] if i>0 else [],0.06,0.32)
    dx,dy=shake(t,wt(1,"war"),6,0.5); d2=shake(t,wt(1,"sealed"),6,0.4); dx+=d2[0]; dy+=d2[1]
    return camera(b,z,0.5,0.45,dx,dy),hud
SN=fbm((h,w*2),760,6,4,aspect=2)
def sandwipe(b1,b2,u):
    p=-w*0.3+u*w*1.6; n=np.roll(SN,-int(u*300),1)[:,:w]
    front=p+n*60
    m=sm_np((front-xx)/50)[...,None]
    dens=np.exp(-((xx-front)/140)**2)*np.clip(0.6+0.4*n,0,1)
    out=b1*(1-m)+b2*m
    out=out*(1-dens[...,None]*0.85)+np.array([0.85,0.62,0.35],np.float32)*dens[...,None]*0.95
    return out
def compose(t,fi=None):
    if fi is None: fi=int(round(t*30))
    i=shot_at(max(t,0)); nxt=SHOTS[i+1] if i+1<len(SHOTS) else None; huds=[]
    if nxt and nxt[2]=="sand" and t>nxt[0]-TR:
        u=(t-(nxt[0]-TR))/(2*TR); b1,h1=render_shot(i,t); b2,h2=render_shot(i+1,t); b=sandwipe(b1,b2,u)
    elif SHOTS[i][2]=="sand" and t<SHOTS[i][0]+TR and i>0:
        u=(t-(SHOTS[i][0]-TR))/(2*TR); b1,h1=render_shot(i-1,t); b2,h2=render_shot(i,t); b=sandwipe(b1,b2,u); huds=[h2] if u>0.75 else []
    else:
        b,h1=render_shot(i,t); huds=[h1]
    b=post(b,bloom=0.45,thr=0.68,tint=(1.03,1.0,0.95))
    img=to_img(b,fi)
    for hf in huds:
        if hf: hf(img)
    ha=1-sm((t-(Ls(1)-0.45))/0.25) if t<Ls(1) else sm((t-(TOTAL-0.55))/0.3)
    if ha>0.01:
        hook_title(img,[("15 SHIPS GOT STUCK",WHITE)],a=ha,y=250,size=124)
        s2=wt(0,"eight")-0.05
        if t>=s2 or t>TOTAL-0.55:
            a2=ha*(sm((t-s2)/0.08) if t<Ls(1) else 1.0); sc=0.7+0.3*spring((t-s2)/0.22) if t<Ls(1) else 1.0
            hook_title(img,[("FOR 8 YEARS",ORANGE)],a=a2,y=390,size=150,sc=sc)
    return finish(img,CAP,t)
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
