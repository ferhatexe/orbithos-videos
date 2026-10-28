import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid72"); sys.path.insert(0,"/home/claude/toolkit")
from pro import *
from PIL import Image, ImageDraw
T,LINES,SC,TOTAL=load("timeline.json")
CAP=Captions(LINES); WD=CAP.W
def wt(li,sub,o=0.0): return word_t(WD,li,sub,o)
def Ls(i): return LINES[i]["s"]
def sm_np(x): x=np.clip(x,0,1); return x*x*(3-2*x)
# ================= "last Soviet citizen": orbital CG + 1991 newsreel, CRT channel-switch transitions =================
TH,TW=512,1024
_aw=((np.cos(np.arange(TW)*2*np.pi/TW)+1)/2)[None,:].astype(np.float32); _aw=_aw*_aw*(3-2*_aw)
def _tile(a): return a*(1-_aw)+np.roll(a,TW//2,1)*_aw
_lat=np.linspace(-1,1,TH,dtype=np.float32)[:,None]*np.ones((1,TW),np.float32)
land=_tile(fbm((TH,TW),501,6,3,aspect=2)); landm=sm_np((land-0.35)/0.12)
cloud=_tile(fbm((TH,TW),502,6,5,aspect=2)); cloudm=np.clip((cloud-0.55)/1.0,0,1)**1.2
lights=_tile(fbm((TH,TW),503,4,40,aspect=2)); lightm=np.clip((lights-1.2)/0.8,0,1)*landm*(np.abs(_lat)<0.75)
ice=sm_np((np.abs(_lat)-0.80)/0.06)
veg=_tile(fbm((TH,TW),504,5,6,aspect=2))
OCEAN=np.array([0.015,0.06,0.18],np.float32); LANDC=np.where((veg>0)[...,None],np.array([0.10,0.16,0.06],np.float32),np.array([0.30,0.24,0.14],np.float32))
DAYTEX=OCEAN*(1-landm[...,None])+LANDC*landm[...,None]; DAYTEX=DAYTEX*(1-ice[...,None])+np.array([0.85,0.88,0.92],np.float32)*ice[...,None]
DAYTEX=DAYTEX*(1-0.85*cloudm[...,None])+np.array([0.95,0.95,0.97],np.float32)*0.85*cloudm[...,None]
NIGHTTEX=(lightm*(1-0.7*cloudm))[...,None]*np.array([2.2,1.4,0.6],np.float32)
def _pad(a): return np.concatenate([a,a[:,:8]],1)
DAYTEX=_pad(DAYTEX.astype(np.float32)); NIGHTTEX=_pad(NIGHTTEX.astype(np.float32))
STARS=starfield(72,1600)
def earth(buf,cx,cy,R,spin,L=(0.9,-0.3,0.3),tilt=0.35):
    x0,x1=max(0,int(cx-R*1.1)),min(w,int(cx+R*1.1)+1); y0,y1=max(0,int(cy-R*1.1)),min(h,int(cy+R*1.1)+1)
    if x0>=x1 or y0>=y1: return
    X=(xx[y0:y1,x0:x1]-cx)/R; Y=(yy[y0:y1,x0:x1]-cy)/R; r2=X*X+Y*Y; r=np.sqrt(r2); ins=r2<1; Z=np.sqrt(np.clip(1-r2,0,1))
    c,s=math.cos(tilt),math.sin(tilt); Xr=X*c-Y*s; Yr=X*s+Y*c
    lat=np.arcsin(np.clip(Yr,-1,1)); lon=np.arctan2(Xr,Z)+spin
    u=(((lon/(2*np.pi))%1.0)*TW).astype(np.float32); v=((lat/np.pi+0.5)*(TH-1)).astype(np.float32)
    day=cv2.remap(DAYTEX,u,v,cv2.INTER_LINEAR); nit=cv2.remap(NIGHTTEX,u,v,cv2.INTER_LINEAR)
    Lv=np.array(L,np.float32); Lv/=np.linalg.norm(Lv); nd=X*Lv[0]+Y*Lv[1]+Z*Lv[2]
    lit=sm_np((nd+0.1)/0.3); col=day*(np.clip(nd,0,1)**0.8*1.5*lit)[...,None]+nit*(1-sm_np((nd+0.15)/0.2))[...,None]
    fr=(1-Z)**2.5; col=col+fr[...,None]*np.array([0.25,0.5,1.1],np.float32)*np.clip(nd+0.3,0,1)[...,None]
    out=np.clip(r-1,0,None); halo=np.exp(-out*45)*(r>=1)*np.clip(X*Lv[0]+Y*Lv[1]+0.4,0,1)
    reg=buf[y0:y1,x0:x1]; reg[:]=np.where(ins[...,None],col,reg)+halo[...,None]*np.array([0.3,0.55,1.2],np.float32)
def poly(buf,pts,col,cx,cy,s,ang,a=1.0):
    ca,sa=math.cos(ang),math.sin(ang)
    P=np.array([(cx+(x*ca-y*sa)*s,cy+(x*sa+y*ca)*s) for x,y in pts],np.int32)
    if a>=1: cv2.fillPoly(buf,[P],col,cv2.LINE_AA)
    else: lay=buf.copy(); cv2.fillPoly(lay,[P],col,cv2.LINE_AA); buf[:]=buf*(1-a)+lay*a
def rect(x0,y0,x1,y1): return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
def mir(buf,cx,cy,s,ang,sun=1.0):
    M=[(rect(-1.6,-0.16,1.6,0.16),(0.55,0.55,0.52)),(rect(-0.16,-1.5,0.16,1.5),(0.50,0.50,0.48)),(rect(1.6,-0.12,2.6,0.12),(0.48,0.47,0.45)),
       (rect(-2.4,-0.12,-1.6,0.12),(0.52,0.51,0.48)),(rect(-0.13,1.5,0.13,2.2),(0.45,0.45,0.43))]
    P=[rect(-1.2,-1.35,-0.25,-0.35),rect(0.25,-1.35,1.2,-0.35),rect(-1.2,0.35,-0.25,1.35),rect(0.25,0.35,1.2,1.35),rect(1.8,-1.0,2.4,-0.14),rect(1.8,0.14,2.4,1.0),rect(-2.2,-0.9,-1.7,-0.14)]
    for pts in P:
        poly(buf,pts,(0.05*sun,0.09*sun,0.22*sun),cx,cy,s,ang)
    for pts,c in M: poly(buf,pts,tuple(v*sun for v in c),cx,cy,s,ang)
    for pts in P[:4]:
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        for k in range(1,5):
            yk=min(ys)+(max(ys)-min(ys))*k/5; poly(buf,rect(min(xs),yk-0.008,max(xs),yk+0.008),(0.6*sun,0.5*sun,0.25*sun),cx,cy,s,ang)
    glow(buf,cx+math.cos(ang)*1.4*s,cy+math.sin(ang)*1.4*s,3,(1.5,1.2,0.8),0.6*sun)
def archival(b,t,fi,bw=False):
    lum=b.mean(2,keepdims=True); s=lum*(np.array([1.0,1.0,1.0],np.float32) if bw else np.array([1.15,0.98,0.75],np.float32))*1.15
    s=cv2.GaussianBlur(s,(0,0),1.2); g=np.random.default_rng(fi%9)
    for i in range(5):
        x=int(g.uniform(0,w)); cv2.line(s,(x,0),(x+int(g.uniform(-6,6)),h),(0.8,0.75,0.65),1,cv2.LINE_AA)
    for i in range(25): cv2.circle(s,(int(g.uniform(0,w)),int(g.uniform(0,h))),int(g.uniform(1,3)),(0.04,0.04,0.04),-1)
    return s*(1-0.6*np.clip(((xx/w-0.5)**2+(yy/h-0.5)**2)*2.4,0,1))[...,None]*(0.93+0.07*math.sin(t*37))
_F=[0]
def night_sky(top=(0.01,0.015,0.05),bot=(0.06,0.07,0.14)):
    k=(yy/h)[...,None]; return np.array(top,np.float32)*(1-k)+np.array(bot,np.float32)*k+STARS*0.5*(1-k)
SMK=fbm((h,w*2),77,6,3,aspect=2)
# ---------- shots ----------
def sh_hook(t,k=0):
    b=STARS.copy(); earth(b,w*0.5,h*1.35,w*1.25,0.9+t*0.012,L=(0.95,-0.25,0.2))
    u=t; mir(b,w*(0.62-0.02*u),h*(0.36+0.004*u),46,0.35+0.02*u)
    return b,None,1.03+0.03*sm(t/5)
def sh_passport(t):
    b=np.zeros((h,w,3),np.float32)+np.array([0.04,0.035,0.035],np.float32)
    glow(b,w*0.5,h*0.42,260,(0.35,0.22,0.12),0.6)
    def hud(img):
        d=ImageDraw.Draw(img); u=sm((t-Ls(1)+0.3)/0.4); x0,y0=200,int(380+60*(1-u)); x1,y1=880,1060
        d.rounded_rectangle((x0+12,y0+16,x1+12,y1+16),28,fill=(0,0,0,140))
        d.rounded_rectangle((x0,y0,x1,y1),28,fill=(120,22,24,255),outline=(70,10,12,255),width=6)
        label(img,"СССР",540,y0+150,120,(232,190,96),stroke=0,font="InterDisplay-Black")
        d.ellipse((540-90,y0+260,540+90,y0+440),outline=(232,190,96,255),width=8)
        st=[(540+80*math.cos(-math.pi/2+k*math.pi/5)*(1 if k%2==0 else 0.4),y0+350+80*math.sin(-math.pi/2+k*math.pi/5)*(1 if k%2==0 else 0.4)) for k in range(10)]
        d.polygon(st,fill=(232,190,96,255))
        label(img,"SERGEI",540,y0+530,64,(232,190,96),stroke=0); label(img,"KRIKALEV",540,y0+610,76,(232,190,96),stroke=0)
    return b,hud,1.0+0.04*(t-Ls(1))
def sh_launch(t):
    b=night_sky((0.02,0.03,0.08),(0.20,0.12,0.12)); u=t-Ls(2)+0.3; rise=ein(cl((u-0.6)/3.0))*h*0.45
    cv2.rectangle(b,(0,int(h*0.86)),(w,h),(0.02,0.018,0.02),-1)
    cx=w*0.5; by=h*0.86-8-rise
    for dx in (-30,30):
        poly(b,[(dx*0.6,-150),(dx*1.0,-60),(dx*1.15,0),(dx*0.5,0)],(0.55,0.55,0.55),cx,by,1.0,0)
    poly(b,rect(-16,-300,16,0),(0.70,0.70,0.68),cx,by,1.0,0); poly(b,[(-14,-300),(0,-345),(14,-300)],(0.62,0.62,0.6),cx,by,1.0,0)
    fl=0.8+0.2*math.sin(t*40)
    glow(b,cx,by+30,40,(2.6,1.7,0.8),1.4*fl); glow(b,cx,by+80,120,(1.4,0.7,0.25),0.9*fl)
    s=np.roll(SMK,-int(t*30),1)[:,:w]; m=np.clip(s*0.5+0.3,0,1)*np.exp(-((yy-(h*0.86))/(90))**2)*np.clip(sm((u-0.3)/1.0),0,1)
    b=b*(1-m[...,None])+np.array([0.9,0.65,0.45],np.float32)*m[...,None]*0.9
    def hud(img):
        label(img,"MAY 1991",540,300,120,WHITE,a=fa(t,Ls(2),99,0.2,0.2))
        a=fa(t,wt(2,"five")-0.05,99,0.15,0.2); label(img,"PLAN: ~5 MONTHS",540,420,70,ORANGE,a=a,sc=0.85+0.15*spring((t-wt(2,"five")+0.05)/0.2))
    return b,hud,1.0+0.03*u
def sh_falling(t):
    b=STARS.copy(); earth(b,w*0.5,h*0.45,w*0.42,2.4+t*0.03,L=(0.7,-0.4,0.6))
    return b,None,1.0+0.05*(t-Ls(3))
def tank(b,x,y,s,col):
    poly(b,[(-1.2,0),(1.2,0),(1.0,0.35),(-1.0,0.35)],col,x,y,s,0); poly(b,rect(-1.3,-0.25,1.3,0.02),col,x,y,s,0)
    poly(b,[(-0.5,-0.25),(0.4,-0.25),(0.3,-0.6),(-0.4,-0.6)],col,x,y,s,0); poly(b,rect(0.3,-0.48,1.6,-0.40),col,x,y,s,0)
def sh_coup(t):
    b=np.zeros((h,w,3),np.float32); k=(yy/h)[...,None]; b+=np.array([0.55,0.55,0.55],np.float32)*(1-k)+np.array([0.35,0.35,0.35],np.float32)*k
    c=(0.10,0.10,0.10); base=int(h*0.62)
    for x0,ww,hh in ((0,120,180),(110,90,260),(190,140,150),(320,100,300),(410,150,200),(550,170,240)):
        cv2.rectangle(b,(x0,base-hh),(x0+ww,base),c,-1)
    for cx_,r in ((370,40),(470,30),(250,26)):
        cv2.circle(b,(cx_,base-300-r if cx_==370 else base-220),r,c,-1,cv2.LINE_AA); cv2.line(b,(cx_,base-300-2*r if cx_==370 else base-220-r),(cx_,base-380 if cx_==370 else base-280),c,4)
    cv2.rectangle(b,(0,base),(w,h),(0.22,0.22,0.22),-1)
    u=t-Ls(4); x=w*0.95-u*110
    tank(b,x,h*0.80,110,(0.05,0.05,0.05)); tank(b,x+330,h*0.74,70,(0.08,0.08,0.08))
    b=archival(b,t,_F[0],bw=True)
    def hud(img): label(img,"AUGUST 1991",540,300,120,WHITE,a=fa(t,Ls(4)+0.1,99,0.2,0.2)); label(img,"MOSCOW",540,410,70,ORANGE,a=fa(t,wt(4,"Moscow")-0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
def sh_sign(t):
    b=np.zeros((h,w,3),np.float32); k=(yy/h)[...,None]; b+=np.array([0.30,0.36,0.45],np.float32)*(1-k)+np.array([0.10,0.10,0.12],np.float32)*k
    s=np.roll(SMK,-int(t*10),1)[:,:w]; b+=np.clip(s*0.2,0,1)[...,None]*0.15
    tsw=wt(5,"Saint")-0.1
    def hud(img):
        d=ImageDraw.Draw(img); f=min(1.0,max(0.0,(t-tsw)/0.35)); sy=abs(math.cos(math.pi*f)); txt="LENINGRAD" if f<0.5 else "ST. PETERSBURG"
        hh=int(220*sy)+2; y0,x0,x1=620-hh//2,110,970
        d.rectangle((530,620,550,1180),fill=(40,40,44,255))
        d.rounded_rectangle((x0,y0,x1,y0+hh),18,fill=(30,70,150,255),outline=(240,240,240,255),width=8)
        if sy>0.15:
            sz=110 if f<0.5 else 92; fnt=IF(sz)
            lay=Image.new("RGBA",(900,200),(0,0,0,0)); ImageDraw.Draw(lay).text((450,100),txt,font=fnt,fill=(255,255,255,255),anchor="mm")
            lay=lay.resize((900,max(1,int(200*sy)))); img.alpha_composite(lay,(90,620-lay.height//2))
    return b,hud,1.0+0.02*(t-Ls(5))
def sh_seats(t):
    b=np.zeros((h,w,3),np.float32)+np.array([0.05,0.06,0.09],np.float32); glow(b,w*0.5,h*0.45,300,(0.15,0.18,0.3),0.6)
    def hud(img):
        d=ImageDraw.Draw(img); u=t-Ls(6)
        label(img,"NEXT SOYUZ",540,300,110,WHITE,a=fa(t,Ls(6),99,0.2,0.2))
        rows=[("COMMANDER",WHITE,0.4),("PAYING AUSTRIAN",(170,210,255),wt(6,"Flights")-Ls(6)),("KAZAKH GUEST",(255,210,140),wt(6,"seat")-Ls(6))]
        for i,(tx,col,t0) in enumerate(rows):
            a=sm((u-t0)/0.25); y=520+i*170
            if a<=0: continue
            d.rounded_rectangle((170,y,910,y+130),22,fill=(20,24,36,int(235*a)),outline=col+(int(255*a),),width=5)
            label(img,tx,540,y+66,62,col,a=a,stroke=0)
        a=sm((t-wt(6,"replacement"))/0.25)
        if a>0:
            y=1030; d.rounded_rectangle((170,y,910,y+120),22,outline=(255,80,70,int(255*a)),width=5)
            label(img,"HIS REPLACEMENT",540,y+62,58,(255,120,110),a=a,stroke=0); d.line((190,y+60,890,y+60),fill=(255,80,70,int(255*a)),width=10)
    return b,hud,1.0
def sh_window(t):
    b=np.zeros((h,w,3),np.float32)+np.array([0.03,0.03,0.04],np.float32)
    lay=STARS.copy(); earth(lay,w*0.5,h*0.95,w*0.9,1.6+t*0.02,L=(0.8,-0.5,0.3))
    m=np.zeros((h,w),np.float32); cv2.circle(m,(int(w*0.5),int(h*0.42)),230,1.0,-1,cv2.LINE_AA); m=m[...,None]
    b=b*(1-m)+lay*m; cv2.circle(b,(int(w*0.5),int(h*0.42)),236,(0.25,0.25,0.27),14,cv2.LINE_AA)
    for k in range(8): a=k*math.pi/4; cv2.circle(b,(int(w*0.5+250*math.cos(a)),int(h*0.42+250*math.sin(a))),7,(0.35,0.35,0.37),-1,cv2.LINE_AA)
    rc=(0.10,0.16,0.30); cv2.ellipse(b,(int(w*0.36)+5,int(h*0.98)),(174,154),0,180,360,rc,-1,cv2.LINE_AA); cv2.circle(b,(int(w*0.36)+5,int(h*0.78)),76,rc,-1,cv2.LINE_AA)
    c=(0.01,0.01,0.012); cv2.ellipse(b,(int(w*0.36),int(h*0.98)),(170,150),0,180,360,c,-1,cv2.LINE_AA); cv2.circle(b,(int(w*0.36),int(h*0.78)),72,c,-1,cv2.LINE_AA)
    def hud(img): label(img,"HE STAYED",540,300,130,ORANGE,a=fa(t,wt(7,"stay")-0.1,99,0.15,0.2),sc=0.85+0.15*spring((t-wt(7,"stay")+0.1)/0.2))
    return b,hud,1.0+0.03*(t-Ls(7))
def flag(b,x,y,wd,ht,cols,t,a=1.0):
    n=len(cols);
    for i,c in enumerate(cols):
        for j in range(24):
            u0,u1=j/24,(j+1)/24; dy0=math.sin(t*5+u0*7)*ht*0.06*u0; dy1=math.sin(t*5+u1*7)*ht*0.06*u1
            y0=y+ht*i/n; y1=y+ht*(i+1)/n
            pts=np.array([(x+wd*u0,y0+dy0),(x+wd*u1,y0+dy1),(x+wd*u1,y1+dy1),(x+wd*u0,y1+dy0)],np.int32)
            sh=0.85+0.15*math.sin(t*5+u0*7+1.5)
            if a>=1: cv2.fillPoly(b,[pts],tuple(v*sh for v in c),cv2.LINE_AA)
def sh_flag(t):
    b=night_sky((0.02,0.03,0.08),(0.10,0.10,0.18)); base=int(h*0.80)
    c=(0.06,0.03,0.03)
    cv2.rectangle(b,(0,base),(w,h),c,-1)
    for x in range(0,w,40): cv2.rectangle(b,(x,base-26),(x+22,base),c,-1)
    poly(b,rect(-70,-420,70,0),c,w*0.20,base,1.0,0); poly(b,[(-80,-420),(0,-560),(80,-420)],c,w*0.20,base,1.0,0)
    glow(b,w*0.20,base-570,8,(2.0,0.4,0.3),0.9)
    px=int(w*0.62); cv2.line(b,(px,int(h*0.18)),(px,base),(0.6,0.6,0.62),5,cv2.LINE_AA)
    u=t-Ls(8)+0.3; ttd=wt(8,"dissolved")
    top=int(h*0.20); bot=int(base-200)
    if t<ttd+0.4:
        y=top+(bot-top)*sm((t-ttd+0.6)/1.0); flag(b,px+3,y,190,125,[(0.75,0.05,0.05)],t)
    else:
        y=bot-(bot-top)*sm((t-ttd-0.4)/1.4); flag(b,px+3,y,190,126,[(0.95,0.95,0.95),(0.05,0.2,0.65),(0.75,0.06,0.06)],t)
    glow(b,px+90,top+60,180,(0.25,0.22,0.3),0.4)
    def hud(img): label(img,"DECEMBER 1991",540,300,104,WHITE,a=fa(t,Ls(8)+0.1,99,0.2,0.2)); label(img,"USSR → RUSSIA",540,410,70,ORANGE,a=fa(t,ttd,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
def sh_orbit(t):
    b=STARS.copy(); earth(b,w*0.5,h*0.45,w*0.33,3.0+t*0.05,L=(0.8,-0.3,0.5))
    a=(t-wt(8,"circling"))*2.4; cv2.ellipse(b,(int(w*0.5),int(h*0.45)),(int(w*0.40),int(w*0.12)),-18,0,360,(0.45,0.5,0.7),1,cv2.LINE_AA)
    ex=w*0.5+w*0.40*math.cos(a); ey=h*0.45+w*0.12*math.sin(a); r=-18*math.pi/180
    X=ex-w*0.5; Y=ey-h*0.45; mx=w*0.5+X*math.cos(r)-Y*math.sin(r); my=h*0.45+X*math.sin(r)+Y*math.cos(r)
    glow(b,mx,my,5,(2.0,1.8,1.4),1.0)
    def hud(img): label(img,"STILL UP THERE",540,300,110,WHITE,a=fa(t,wt(8,"circling")-0.1,99,0.15,0.2))
    return b,hud,1.0+0.02*(t-wt(8,"while"))
def sh_baikonur(t):
    b=night_sky((0.15,0.12,0.18),(0.75,0.45,0.30)); base=int(h*0.78)
    cv2.rectangle(b,(0,base),(w,h),(0.10,0.07,0.05),-1)
    c=(0.03,0.025,0.03)
    poly(b,rect(-16,-300,16,0),c,w*0.58,base,1.0,0); poly(b,[(-14,-300),(0,-345),(14,-300)],c,w*0.58,base,1.0,0)
    for dx in (-30,30): poly(b,[(dx*0.6,-150),(dx*1.0,-60),(dx*1.15,0),(dx*0.5,0)],c,w*0.58,base,1.0,0)
    for x in (w*0.40,w*0.76):
        cv2.line(b,(int(x),base),(int(x),base-360),c,10);
        for k in range(10): cv2.line(b,(int(x-14),base-k*36),(int(x+14),base-k*36-30),c,3)
    glow(b,w*0.2,base-10,40,(2.0,1.2,0.5),0.8)
    def hud(img):
        d=ImageDraw.Draw(img); label(img,"BAIKONUR",540,300,124,WHITE,a=fa(t,wt(9,"Baikonur")-0.1,99,0.15,0.2))
        tk=wt(9,"Kazakhstan")-0.1; a1=fa(t,Ls(9)+0.3,99,0.2,0.2)
        if t<tk: label(img,"USSR",540,450,86,(255,120,110),a=a1,stroke=6)
        else:
            a=sm((t-tk)/0.15); sc=1.3-0.3*spring((t-tk)/0.25)
            label(img,"KAZAKHSTAN",540,450,96,ORANGE,a=a,sc=sc)
    return b,hud,1.0+0.03*(t-Ls(9))
def sh_landing(t):
    b=np.zeros((h,w,3),np.float32); k=(yy/h)[...,None]; b+=np.array([0.62,0.66,0.72],np.float32)*(1-k)+np.array([0.85,0.86,0.88],np.float32)*k
    base=int(h*0.80); cv2.rectangle(b,(0,base),(w,h),(0.86,0.88,0.90),-1)
    s=np.roll(SMK,-int(t*8),1)[:,:w]; b=b+np.clip(s*0.2,0,1)[...,None]*0.15*(yy<base)[...,None]
    u=t-Ls(10)+0.3; cy=h*0.36+u*30; cx=w*0.52+math.sin(t*0.8)*10
    poly(b,[(-1.0,0),(-0.8,-0.55),(-0.3,-0.8),(0.3,-0.8),(0.8,-0.55),(1.0,0),(0.6,0.12),(-0.6,0.12)],(0.95,0.55,0.15),cx,cy,150,0)
    for i in range(-3,4): cv2.line(b,(int(cx+i*40),int(cy-110+abs(i)*10)),(int(cx+i*40),int(cy)),(0.98,0.95,0.9),12,cv2.LINE_AA)
    for sx in (-140,-60,60,140): cv2.line(b,(int(cx+sx),int(cy+10)),(int(cx),int(cy+300)),(0.3,0.3,0.3),1,cv2.LINE_AA)
    poly(b,[(-0.5,0),(0.5,0),(0.35,-0.45),(-0.35,-0.45)],(0.18,0.16,0.14),cx,cy+340,90,0)
    def hud(img):
        tc=wt(10,"311")-0.1; a=fa(t,tc,99,0.12,0.2); v=int(311*sm((t-tc)/0.9))
        label(img,"MARCH 1992",540,300,104,(30,40,60),a=fa(t,Ls(10)+0.1,tc-0.1,0.2,0.15),stroke=0)
        label(img,f"{v} DAYS",540,330,150,ORANGE,a=a); label(img,"PLANNED: ~150",540,450,64,(30,40,60),a=fa(t,wt(10,"twice")-0.1,99,0.15,0.2),stroke=0)
    return b,hud,1.0+0.02*u
def sh_shuttle(t):
    b=night_sky((0.05,0.10,0.25),(0.45,0.55,0.70)); base=int(h*0.86); cv2.rectangle(b,(0,base),(w,h),(0.05,0.06,0.06),-1)
    u=t-Ls(11)+0.3; rise=ein(cl((u-0.3)/3.0))*h*0.5; cx=w*0.5; by=base-10-rise
    poly(b,rect(-30,-330,30,0),(0.85,0.45,0.15),cx,by,1.0,0); poly(b,[(-30,-330),(0,-380),(30,-330)],(0.85,0.45,0.15),cx,by,1.0,0)
    for dx in (-44,44): poly(b,rect(dx-12,-280,dx+12,0),(0.92,0.92,0.92),cx,by,1.0,0); poly(b,[(dx-12,-280),(dx,-305),(dx+12,-280)],(0.92,0.92,0.92),cx,by,1.0,0)
    poly(b,[(30,-260),(70,-300),(80,-60),(110,-10),(30,-10)],(0.95,0.95,0.95),cx,by,1.0,0)
    poly(b,[(75,-300),(68,-330),(82,-300)],(0.2,0.2,0.2),cx,by,1.0,0)
    fl=0.85+0.15*math.sin(t*37)
    for dx in (-44,44,0): glow(b,cx+dx,by+20,26,(2.8,2.0,1.0),1.2*fl)
    glow(b,cx,by+90,130,(1.4,0.8,0.3),0.8*fl)
    s=np.roll(SMK,-int(t*20),1)[:,:w]; m=np.clip(s*0.5+0.35,0,1)*np.exp(-((xx-cx)/150)**2)*np.clip((yy-by-40)/200,0,1)*sm(u/0.8)
    b=b*(1-m[...,None])+np.array([0.92,0.88,0.84],np.float32)*m[...,None]
    def hud(img): label(img,"1994 · STS-60",540,300,104,WHITE,a=fa(t,Ls(11)+0.1,99,0.2,0.2)); label(img,"FIRST RUSSIAN ON A SHUTTLE",540,410,56,ORANGE,a=fa(t,wt(11,"first")-0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
def sh_end(t):
    b,_,z=sh_hook(t-TOTAL+0.0)
    def hud(img): label(img,"THE LAST",540,300,120,WHITE,a=fa(t,wt(12,"last")-0.1,TOTAL-0.65,0.15,0.2)); label(img,"SOVIET CITIZEN",540,430,110,ORANGE,a=fa(t,wt(12,"Soviet")-0.1,TOTAL-0.65,0.15,0.2))
    return b,hud,z
SHOTS=[(0.0,sh_hook,"cut"),(Ls(1)-0.3,sh_passport,"tv"),(Ls(2)-0.1,sh_launch,"cut"),(Ls(3)-0.25,sh_falling,"tv"),
 (Ls(4)-0.2,sh_coup,"tv"),(Ls(5)-0.2,sh_sign,"cut"),(Ls(6)-0.25,sh_seats,"tv"),(Ls(7)-0.15,sh_window,"cut"),
 (Ls(8)-0.25,sh_flag,"tv"),(wt(8,"while")-0.05,sh_orbit,"cut"),(Ls(9)-0.2,sh_baikonur,"cut"),(Ls(10)-0.25,sh_landing,"tv"),
 (Ls(11)-0.25,sh_shuttle,"cut"),(Ls(12)-0.25,sh_end,"tv")]
TR=0.18; LOOPD=0.0
def shot_at(t):
    i=0
    for k,s in enumerate(SHOTS):
        if t>=s[0]: i=k
    return i
def render_shot(i,t):
    b,hud,z=SHOTS[i][1](t); st=SHOTS[i][0]
    z*=punch(t,[st] if i>0 else [],0.06,0.32)
    dx,dy=shake(t,wt(4,"tanks"),7,0.5); d2=shake(t,wt(6,"cut"),5,0.4); dx+=d2[0]; dy+=d2[1]
    return camera(b,z,0.5,0.45,dx,dy),hud
def tv(b1,b2,u):
    """CRT channel switch: picture collapses to a bright line + static, next channel opens with a vertical roll"""
    g=np.random.default_rng(int(u*1000)); st=g.random((h//4,w//4)).astype(np.float32); st=cv2.resize(st,(w,h),interpolation=cv2.INTER_NEAREST)[...,None]
    if u<0.5:
        k=1-sm(u/0.5); hh=max(2,int(h*k)); img=cv2.resize(b1,(w,hh)); out=np.zeros_like(b1); y0=(h-hh)//2; out[y0:y0+hh]=img*(1+1.5*(1-k))
        out=out*(1-0.5*(1-k))+st*0.35*(1-k)*(np.abs(yy-h/2)<hh/2+6)[...,None]
    else:
        k=sm((u-0.5)/0.5); roll=int((1-k)*h*0.35); out=np.roll(b2,roll,0); out=out*(0.6+0.4*k)+st*0.45*(1-k)
    scan=(0.85+0.15*(np.sin(yy*math.pi/2)>0))[...,None]
    return out*scan
def compose(t,fi=None):
    if fi is None: fi=int(round(t*30))
    _F[0]=fi
    i=shot_at(max(t,0)); nxt=SHOTS[i+1] if i+1<len(SHOTS) else None; huds=[]
    if nxt and nxt[2]=="tv" and t>nxt[0]-TR:
        u=(t-(nxt[0]-TR))/(2*TR); b1,h1=render_shot(i,t); b2,h2=render_shot(i+1,t); b=tv(b1,b2,u)
    elif SHOTS[i][2]=="tv" and t<SHOTS[i][0]+TR and i>0:
        u=(t-(SHOTS[i][0]-TR))/(2*TR); b1,h1=render_shot(i-1,t); b2,h2=render_shot(i,t); b=tv(b1,b2,u)
    else:
        b,h1=render_shot(i,t); huds=[h1]
    b=post(b,bloom=0.5,thr=0.65)
    img=to_img(b,fi)
    for hf in huds:
        if hf: hf(img)
    ha=1-sm((t-(Ls(1)-0.4))/0.25) if t<Ls(1) else sm((t-(TOTAL-0.6))/0.3)
    if ha>0.01:
        hook_title(img,[("HE LEFT THE USSR",WHITE)],a=ha,y=250,size=124)
        s2=wt(0,"no")-0.05
        if t>=s2 or t>TOTAL-0.6:
            a2=ha*(sm((t-s2)/0.08) if t<Ls(1) else 1.0); sc=0.7+0.3*spring((t-s2)/0.22) if t<Ls(1) else 1.0
            hook_title(img,[("HIS COUNTRY VANISHED",ORANGE)],a=a2,y=390,size=130,sc=sc)
    return finish(img,CAP,t)
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
