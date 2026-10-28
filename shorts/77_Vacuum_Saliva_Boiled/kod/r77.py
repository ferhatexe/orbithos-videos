import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid77"); sys.path.insert(0,"/home/claude/toolkit")
from pro import *
from PIL import Image, ImageDraw
T,LINES,SC,TOTAL=load("timeline.json")
CAP=Captions(LINES); WD=CAP.W
def wt(li,sub,o=0.0): return word_t(WD,li,sub,o)
def Ls(i): return LINES[i]["s"]
def sm_np(x): x=np.clip(x,0,1); return x*x*(3-2*x)
# ================= 1966 NASA vacuum-chamber thriller: steel, fluorescent cold light, gauges; airlock-iris transitions =================
G=np.random.default_rng(77)
BRUSH=cv2.resize(np.random.default_rng(1).normal(0,1,(h//2,8)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC)*0.5+cv2.resize(fbm((h//4,w//4),2,4,6),(w,h))*0.5
def steel(base=(0.42,0.46,0.50)):
    return np.array(base,np.float32)*(0.85+0.12*BRUSH)[...,None]
def chamber_bg(t,red=0.0):
    """interior of the 8-ft altitude chamber: curved steel walls, ribs, fluorescent strip, floor grating"""
    b=steel((0.30,0.34,0.38))
    cyl=np.cos((xx/w-0.5)*2.6)[...,None]; b=b*(0.45+0.75*cyl)
    for k in range(7):
        x=int(w*(k+0.5)/7); cv2.line(b,(x,0),(x,int(h*0.78)),(0.18,0.2,0.22),5,cv2.LINE_AA); cv2.line(b,(x+4,0),(x+4,int(h*0.78)),(0.55,0.6,0.64),1,cv2.LINE_AA)
    cv2.rectangle(b,(int(w*0.15),18),(int(w*0.85),34),(1.6,1.7,1.8),-1); glow(b,w*0.5,26,140,(0.6,0.7,0.8),0.6)
    fl=int(h*0.78); b[fl:]=np.array([0.10,0.11,0.12],np.float32)
    for k in range(18):
        y=fl+int((k/18)**1.6*(h-fl)); cv2.line(b,(0,y),(w,y),(0.22,0.24,0.26),1)
    for k in range(-12,13): cv2.line(b,(int(w/2+k*12),fl),(int(w/2+k*90),h),(0.22,0.24,0.26),1,cv2.LINE_AA)
    if red>0:
        p=0.5+0.5*math.sin(t*9); glow(b,w*0.85,h*0.12,30,(2.0,0.2,0.1),red*p*1.2); b=b*(1-0.25*red*p)+np.array([0.3,0.0,0.0],np.float32)*red*p*0.25
    return b
def suit(b,cx,cy,s,lean=0.0,hose=1.0,t=0.0):
    """Apollo-era pressure suit, 3/4 view, soft studio shading"""
    def P(px,py): ca,sa=math.cos(lean),math.sin(lean); return (int(cx+(px*ca-py*sa)*s),int(cy+(px*sa+py*ca)*s))
    W_=(0.88,0.88,0.86); D_=(0.55,0.56,0.58)
    lay=np.zeros_like(b); m=np.zeros((h,w),np.float32)
    parts=[[P(-0.30,-0.10),P(0.30,-0.10),P(0.34,0.55),P(-0.34,0.55)],                 # torso
           [P(-0.30,0.55),P(-0.05,0.55),P(-0.10,1.25),P(-0.30,1.25)],[P(0.05,0.55),P(0.30,0.55),P(0.30,1.25),P(0.10,1.25)],   # legs
           [P(-0.30,-0.05),P(-0.45,0.0),P(-0.52,0.50),P(-0.40,0.52)],[P(0.30,-0.05),P(0.45,0.0),P(0.52,0.50),P(0.40,0.52)]]   # arms
    for pts in parts: cv2.fillPoly(m,[np.array(pts,np.int32)],1.0,cv2.LINE_AA)
    cv2.circle(m,P(0,-0.32),int(0.24*s),1.0,-1,cv2.LINE_AA)
    shade=np.clip(0.55+0.6*((xx-cx)/(s*0.6))*-0.5+0.3*np.exp(-((xx-cx+0.1*s)**2+(yy-cy)**2)/(2*(0.4*s)**2)),0.3,1.2)
    col=np.array(W_,np.float32)*shade[...,None]
    b[:]=b*(1-m[...,None])+col*m[...,None]
    for y_ in (0.15,0.35,0.85,1.05): cv2.line(b,P(-0.33,y_),P(0.33,y_),D_,2,cv2.LINE_AA)
    hc=P(0,-0.32); r=int(0.21*s)
    cv2.circle(b,hc,r,(0.03,0.04,0.06),-1,cv2.LINE_AA); cv2.ellipse(b,(hc[0]-r//3,hc[1]-r//3),(r//3,r//5),-35,0,360,(0.9,0.95,1.0),-1,cv2.LINE_AA)
    cv2.rectangle(b,P(-0.12,0.08),P(0.12,0.24),(0.3,0.32,0.36),-1)
    if hose>0:
        a=P(0.12,0.16); e=(int(w*1.05),int(cy+0.1*s))
        pts=[(int(a[0]+(e[0]-a[0])*u+math.sin(u*3.14)*30),int(a[1]+(e[1]-a[1])*u+math.sin(u*3.14)*60)) for u in np.linspace(0,hose,20)]
        cv2.polylines(b,[np.array(pts,np.int32)],False,(0.12,0.12,0.14),int(0.07*s),cv2.LINE_AA)
    return P
def gauge(img,cx,cy,R,val,vmax,title,unit,a=1.0,red_zone=None):
    d=ImageDraw.Draw(img); A=int(255*a)
    d.ellipse((cx-R-14,cy-R-14,cx+R+14,cy+R+14),fill=(40,44,50,A)); d.ellipse((cx-R,cy-R,cx+R,cy+R),fill=(236,232,220,A),outline=(20,20,20,A),width=6)
    a0,a1=math.radians(225),math.radians(-45)
    if red_zone:
        for v in np.linspace(red_zone[0],red_zone[1],30):
            an=a0+(a1-a0)*v/vmax; d.line((cx+math.cos(an)*R*0.78,cy-math.sin(an)*R*0.78,cx+math.cos(an)*R*0.92,cy-math.sin(an)*R*0.92),fill=(210,40,40,A),width=8)
    for k in range(9):
        an=a0+(a1-a0)*k/8; d.line((cx+math.cos(an)*R*0.80,cy-math.sin(an)*R*0.80,cx+math.cos(an)*R*0.95,cy-math.sin(an)*R*0.95),fill=(20,20,20,A),width=5)
    an=a0+(a1-a0)*max(0,min(val,vmax))/vmax
    d.line((cx,cy,cx+math.cos(an)*R*0.82,cy-math.sin(an)*R*0.82),fill=(200,30,30,A),width=9); d.ellipse((cx-16,cy-16,cx+16,cy+16),fill=(20,20,20,A))
    f=IF(int(R*0.22)); d.text((cx,cy+R*0.42),f"{val:.1f}",font=f,fill=(20,20,20,A),anchor="mm")
    d.text((cx,cy+R*0.66),unit,font=IF(int(R*0.13)),fill=(60,60,60,A),anchor="mm")
    label(img,title,cx,cy-R-60,46,WHITE,a=a,stroke=5)
# ---------- shots ----------
def sh_hook(t,end=False):
    tt=t-TOTAL if end else t
    b=chamber_bg(t,red=1.0); b=cv2.GaussianBlur(b,(0,0),5)
    cx,cy,R=w*0.5,h*0.42,w*0.40
    m=np.zeros((h,w),np.float32); cv2.circle(m,(int(cx),int(cy)),int(R),1.0,-1,cv2.LINE_AA); m=m[...,None]
    vis=np.zeros_like(b)+np.array([0.02,0.025,0.035],np.float32)
    cv2.ellipse(vis,(int(cx),int(cy+R*0.25)),(int(R*0.55),int(R*0.7)),0,0,360,(0.06,0.06,0.07),-1,cv2.LINE_AA)
    refl=np.exp(-(((xx-cx+R*0.35)/(R*0.30))**2+((yy-cy+R*0.45)/(R*0.12))**2))
    vis+=refl[...,None]*np.array([0.9,1.0,1.1],np.float32)*0.9
    p=0.5+0.5*math.sin(t*9); vis+=np.exp(-(((xx-cx-R*0.5)/(R*0.15))**2+((yy-cy+R*0.1)/(R*0.4))**2))[...,None]*np.array([1.2,0.1,0.05],np.float32)*0.6*p
    b=b*(1-m)+vis*m
    ring=np.exp(-((np.sqrt((xx-cx)**2+(yy-cy)**2)-R)/10)**2)[...,None]; b=b*(1-ring*0.8)+np.array([0.75,0.78,0.80],np.float32)*ring*0.8
    g=np.random.default_rng(int(t*30)%97)
    for i in range(40):
        x=cx+g.uniform(-0.3,0.3)*R; y=cy+R*0.55-((t*60+i*37)%(R*0.9)); r=g.uniform(2,6)
        cv2.circle(b,(int(x),int(y)),int(r),(0.7,0.8,0.9),1,cv2.LINE_AA)
    blk=sm((tt-wt(0,"black"))/0.5) if not end else 0.0
    b=b*(1-0.9*blk)
    return b,None,1.04+0.04*sm(max(tt,0)/4)
def sh_chamber(t):
    u=t-Ls(1); b=chamber_bg(t)
    hx,hy=w*0.5,h*0.40
    door=np.zeros_like(b); cv2.circle(door,(int(hx),int(hy)),250,(1,1,1),-1,cv2.LINE_AA)
    b=b*(1-door*0.0)
    suit(b,w*0.5,h*0.50,330,0.0,1.0,t)
    def hud(img):
        label(img,"HOUSTON · 1966",540,280,104,WHITE,a=fa(t,Ls(1)+0.1,99,0.2,0.2))
        label(img,"VACUUM CHAMBER TEST",540,390,60,ORANGE,a=fa(t,wt(1,"vacuum")-0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.03*u
ALTSTARS=starfield(5,600)
def sh_alt(t):
    u=t-Ls(2); b=np.zeros((h,w,3),np.float32); k=(yy/h)[...,None]
    z=sm(u/3.0); top=np.array([0.0,0.0,0.02],np.float32); bot=np.array([0.15,0.35,0.75],np.float32)*(1-z)+np.array([0.02,0.05,0.15],np.float32)*z
    b+=top*(1-k)+bot*k; b+=ALTSTARS*z*np.clip(1-k*1.2,0,1)
    ex=np.exp(-((yy-h*(1.05+0.3*z))/(140))**2)[...,None]*np.array([0.2,0.45,1.0],np.float32); b+=ex
    def hud(img):
        d=ImageDraw.Draw(img); ft=int(120000*sm(u/2.4))
        label(img,f"{ft:,} FT",540,300,140,WHITE)
        label(img,"~36 KM · EQUIVALENT",540,420,56,ORANGE,stroke=6)
        x=900; y0,y1=1650,520; d.line((x,y0,x,y1),fill=(255,255,255,160),width=4)
        for kk in range(7): yk=y0-(y0-y1)*kk/6; d.line((x-16,yk,x+16,yk),fill=(255,255,255,160),width=3)
        yv=y0-(y0-y1)*sm(u/2.4); d.polygon([(x-30,yv-14),(x-30,yv+14),(x-6,yv)],fill=(255,168,28,255))
    return b,hud,1.0
def sh_leak(t,phase=0):
    u=t-Ls(3); b=chamber_bg(t,red=sm((u-0.8)/0.4) if phase==0 else 1.0)
    det=sm((t-wt(3,"loose"))/0.4)
    P=suit(b,w*(0.45 if phase==0 else 0.30),h*0.50 if phase==0 else h*0.55,330 if phase==0 else 290,0.0 if phase==0 else -0.05*sm(u/2),1.0-0.55*det,t)
    if det>0:
        a=P(0.12,0.16); g=np.random.default_rng(int(t*30))
        lay=np.zeros_like(b)
        for i in range(70):
            r=g.uniform(0,1); ang=g.uniform(-0.6,0.6); L=40+r*260*det
            cv2.line(lay,a,(int(a[0]+math.cos(ang)*L),int(a[1]+math.sin(ang)*L)),(0.8,0.85,0.9),1,cv2.LINE_AA)
        b+=cv2.GaussianBlur(lay,(0,0),2)*0.8*(1.0 if phase==0 else 0.5)
    def hud(img):
        if phase==0: label(img,"HOSE CAME LOOSE",540,300,100,(255,90,80),a=fa(t,wt(3,"loose")-0.05,99,0.12,0.2),sc=0.85+0.15*spring((t-wt(3,"loose")+0.05)/0.2))
        else:
            v=3.8-3.7*sm((t-Ls(4)-0.2)/1.6); gauge(img,760,640,190,v,5.0,"SUIT PRESSURE","PSI",red_zone=(0,1.0))
    return b,hud,1.0+(0.03*u if phase==0 else 0.05*sm((t-Ls(4))/2))
def sh_boil(t):
    u=t-Ls(5); b=np.zeros((h,w,3),np.float32)+np.array([0.02,0.03,0.05],np.float32); glow(b,w*0.5,h*0.45,300,(0.15,0.25,0.4),0.6)
    cx,cy,R=w*0.5,h*0.45,230
    X=(xx-cx)/R; Y=(yy-cy)/(R*0.8); r2=X*X+Y*Y; ins=sm_np((1-r2)*8)
    Z=np.sqrt(np.clip(1-r2,0,1)); col=np.array([0.10,0.25,0.45],np.float32)*(0.4+0.6*Z)[...,None]+(np.exp(-((X+0.35)**2+(Y+0.4)**2)/0.02)*2.0)[...,None]
    b=b*(1-ins[...,None])+col*ins[...,None]
    g=np.random.default_rng(3)
    for i in range(60):
        bx=cx+g.uniform(-0.7,0.7)*R; ph=(u*g.uniform(0.6,1.4)+g.random())%1.0; by=cy+R*0.6-ph*R*1.2; rr=2+g.uniform(2,10)*ph
        if ((bx-cx)/R)**2+((by-cy)/(R*0.8))**2<0.85: cv2.circle(b,(int(bx),int(by)),int(rr),(0.8,0.9,1.0),2,cv2.LINE_AA)
    def hud(img):
        label(img,"BOILS AT 37°C",540,300,124,ORANGE,a=fa(t,wt(5,"body")-0.1,99,0.15,0.2),sc=0.85+0.15*spring((t-wt(5,"body")+0.1)/0.2))
        label(img,"= BODY TEMPERATURE",540,415,60,WHITE,a=fa(t,wt(5,"temperature")-0.1,99,0.15,0.2),stroke=6)
    return b,hud,1.0+0.04*u
def bp_at(hkm):
    P=101.325*math.exp(-hkm/7.0)*1000/133.322  # mmHg
    return 1730.63/(8.07131-math.log10(max(P,1e-3)))-233.426
def sh_chart(t):
    u=t-Ls(6); b=np.zeros((h,w,3),np.float32)+np.array([0.03,0.04,0.07],np.float32); glow(b,w*0.5,h*0.5,350,(0.1,0.15,0.3),0.5)
    def hud(img):
        d=ImageDraw.Draw(img); x0,x1,y0,y1=150,960,1020,520
        d.line((x0,y0,x1,y0),fill=(200,215,255,220),width=4); d.line((x0,y0,x0,y1),fill=(200,215,255,220),width=4)
        label(img,"ALTITUDE →",x1-110,y0+50,38,(200,215,255),stroke=4); label(img,"BOILING POINT",x0+170,y1-40,38,(200,215,255),stroke=4)
        n=int(120*cl(u/1.6)); pts=[]
        for i in range(n+1):
            hk=36.6*i/120; bp=bp_at(hk); pts.append((x0+(x1-x0)*hk/36.6,y0-(y0-y1)*max(0,min(bp,100))/100))
        if len(pts)>1: d.line(pts,fill=(120,200,255,255),width=8,joint="curve")
        yb=y0-(y0-y1)*37/100; a=fa(t,wt(6,"body")-0.2,99,0.2,0.2)
        for x in range(x0,x1,30): d.line((x,yb,x+15,yb),fill=(255,168,28,int(255*a)),width=4)
        label(img,"BODY 37°C",x0+120,yb-30,36,ORANGE,a=a,stroke=4)
        hx=x0+(x1-x0)*19.2/36.6; aa=fa(t,wt(6,"Armstrong")-0.15,99,0.15,0.2)
        if aa>0:
            d.line((hx,y0,hx,y1-20),fill=(255,90,80,int(255*aa)),width=5); d.ellipse((hx-14,yb-14,hx+14,yb+14),fill=(255,90,80,int(255*aa)))
        label(img,"ARMSTRONG LIMIT",540,300,96,(255,90,80),a=aa); label(img,"~63,000 FT · ~19 KM",540,400,56,WHITE,a=aa,stroke=6)
    return b,hud,1.0
def sh_count(t):
    u=t-Ls(7); b=chamber_bg(t,red=1.0)
    suit(b,w*0.5,h*0.52,330,-0.6*sm((t-wt(7,"collapsed"))/0.5),0.45,t)
    v=sm((u-0.3)/2.8); b=b*np.clip(1-v*np.clip(((xx/w-0.5)**2+(yy/h-0.45)**2)*5.5,0,1),0,1)[...,None]
    blk=sm((t-wt(7,"collapsed"))/0.6); b=b*(1-0.85*blk)
    def hud(img):
        d=ImageDraw.Draw(img); s=min(14.0,14*cl((t-Ls(7)-0.2)/2.6));
        label(img,f"00:{int(s):02d}",540,300,170,WHITE if s<14 else (255,90,80))
        y=420; pts=[]
        for i in range(120):
            x=200+i*5.8; ph=(i/120*3+u*1.2)%1.0; amp=(1-0.8*blk)
            yy_=y-(math.exp(-((ph-0.3)/0.02)**2)*70-math.exp(-((ph-0.34)/0.02)**2)*30)*amp
            pts.append((x,yy_))
        d.line(pts,fill=(80,255,120,int(220*(1-0.5*blk))),width=5)
    return b,hud,1.0+0.05*sm(u/3)
def sh_rescue(t,phase=0):
    u=t-Ls(8); b=np.zeros((h,w,3),np.float32); b+=steel((0.25,0.28,0.31))*(0.7+0.3*np.cos((xx/w-0.5)*2.0))[...,None]
    cv2.rectangle(b,(0,int(h*0.80)),(w,h),(0.08,0.09,0.10),-1)
    cv2.circle(b,(int(w*0.36),int(h*0.42)),230,(0.38,0.42,0.46),-1,cv2.LINE_AA); cv2.circle(b,(int(w*0.36),int(h*0.42)),230,(0.12,0.13,0.14),10,cv2.LINE_AA)
    cv2.circle(b,(int(w*0.36),int(h*0.42)),80,(0.7,0.8,0.9),-1,cv2.LINE_AA); glow(b,w*0.36,h*0.42,70,(0.6,0.7,0.8),0.5)
    for k in range(16): a=k*math.pi/8; cv2.circle(b,(int(w*0.36+205*math.cos(a)),int(h*0.42+205*math.sin(a))),9,(0.2,0.2,0.22),-1,cv2.LINE_AA)
    wx,wy,wr=w*0.78,h*0.55,95; ang=u*6 if phase==0 else u*4
    cv2.circle(b,(int(wx),int(wy)),wr,(0.75,0.12,0.10),12,cv2.LINE_AA)
    for k in range(5): a=ang+k*2*math.pi/5; cv2.line(b,(int(wx),int(wy)),(int(wx+wr*math.cos(a)),int(wy+wr*math.sin(a))),(0.75,0.12,0.10),9,cv2.LINE_AA)
    c=(0.03,0.03,0.04)
    for k,(px,ps) in enumerate(((0.62,1.0),(0.20,0.9))):
        x=w*px+(math.sin(t*12+k)*6); y=h*0.80
        cv2.circle(b,(int(x),int(y-ps*250)),int(ps*32),c,-1,cv2.LINE_AA); cv2.fillPoly(b,[np.array([(x-ps*45,y-ps*215),(x+ps*45,y-ps*215),(x+ps*40,y-ps*90),(x-ps*40,y-ps*90)],np.int32)],c,cv2.LINE_AA)
        cv2.line(b,(int(x-ps*20),int(y-ps*90)),(int(x-ps*50+math.sin(t*12+k)*30),int(y)),c,int(ps*22),cv2.LINE_AA); cv2.line(b,(int(x+ps*20),int(y-ps*90)),(int(x+ps*45-math.sin(t*12+k)*30),int(y)),c,int(ps*22),cv2.LINE_AA)
    if phase==1:
        f=sm((t-Ls(9))/1.2); fog=np.clip(fbm((h//4,w//4),int(t*10)%5+9,4,4),0,None); fog=cv2.resize(fog,(w,h))
        b=b*(1-0.5*f)+np.array([0.85,0.9,0.95],np.float32)*(fog*0.5*f)[...,None]
    def hud(img):
        if phase==0: label(img,"RACE AGAINST TIME",540,300,96,WHITE,a=fa(t,Ls(8)+0.1,99,0.2,0.2))
        else:
            s=87*cl((t-Ls(9)+0.1)/1.3); label(img,f"{int(s)//60}:{int(s)%60:02d}",540,300,170,ORANGE); label(img,"TO REPRESSURIZE (~87 S)",540,440,52,WHITE,stroke=6)
    return b,hud,1.0+0.03*u
def sh_wake(t):
    u=t-Ls(10); b=chamber_bg(t,red=0.0); b=b*(0.6+0.4*sm(u/0.8))
    suit(b,w*0.5,h*0.52,330,-0.3*(1-sm(u/1.5)),1.0,t)
    b+=np.array([0.05,0.08,0.10],np.float32)*sm(u/1.0)
    def hud(img):
        a=fa(t,wt(10,"earache")-0.15,99,0.15,0.2)
        label(img,"HE SURVIVED",540,280,120,(120,255,150),a=fa(t,Ls(10)+0.2,99,0.2,0.2)); label(img,"ONLY INJURY: AN EARACHE",540,400,56,WHITE,a=a,stroke=6)
    return b,hud,1.0+0.02*u
def sh_record(t):
    u=t-Ls(11); b=chamber_bg(t); b=cv2.GaussianBlur(b,(0,0),3)*0.6
    def hud(img):
        d=ImageDraw.Draw(img); a=sm(u/0.4); x0,y0,x1,y1=170,520,910,1060
        d.rectangle((x0,y0,x1,y1),fill=(238,232,214,int(245*a))); d.rectangle((x0,y0,x1,y0+90),fill=(30,60,120,int(245*a)))
        label(img,"NASA · MSC · INCIDENT",540,y0+46,44,WHITE,a=a,stroke=0)
        rows=["DATE: DEC 14, 1966","SUBJECT: J. LEBLANC","EXPOSURE: ~120,000 FT","CONSCIOUS: ~14 S","RECOVERED: YES"]
        for i,r in enumerate(rows): label(img,r,540,y0+150+i*72,42,(40,40,50),a=a*sm((u-0.2-i*0.18)/0.2),stroke=0)
        label(img,"ONE OF VERY FEW",540,300,100,ORANGE,a=fa(t,wt(11,"few")-0.15,99,0.15,0.2))
    return b,hud,1.0+0.02*u
SHOTS=[(0.0,sh_hook,"cut"),(Ls(1)-0.3,sh_chamber,"iris"),(Ls(2)-0.15,sh_alt,"cut"),(Ls(3)-0.25,lambda t:sh_leak(t,0),"iris"),
 (Ls(4)-0.1,lambda t:sh_leak(t,1),"cut"),(Ls(5)-0.25,sh_boil,"iris"),(Ls(6)-0.1,sh_chart,"cut"),(Ls(7)-0.25,sh_count,"iris"),
 (Ls(8)-0.25,lambda t:sh_rescue(t,0),"iris"),(Ls(9)-0.1,lambda t:sh_rescue(t,1),"cut"),(Ls(10)-0.2,sh_wake,"cut"),(Ls(11)-0.25,sh_record,"iris"),
 (wt(11,"Because")-0.2,lambda t:sh_hook(t,True),"iris")]
TR=0.22
def shot_at(t):
    i=0
    for k,s in enumerate(SHOTS):
        if t>=s[0]: i=k
    return i
def render_shot(i,t):
    b,hud,z=SHOTS[i][1](t); st=SHOTS[i][0]
    z*=punch(t,[st] if i>0 else [],0.06,0.32)
    dx,dy=shake(t,wt(3,"loose"),8,0.5); d2=shake(t,wt(0,"boil"),5,0.4); dx+=d2[0]; dy+=d2[1]
    return camera(b,z,0.5,0.45,dx,dy),hud
def iris(b1,b2,u,n=8):
    """airlock iris: steel blades close to a point, then reopen on the next shot"""
    k=1-sm(u/0.5) if u<0.5 else sm((u-0.5)/0.5); src=b1 if u<0.5 else b2
    R=k*w*0.95+2; cx,cy=w*0.5,h*0.45; rot=(1-k)*1.2
    poly=np.array([(cx+R*math.cos(rot+j*2*math.pi/n),cy+R*math.sin(rot+j*2*math.pi/n)) for j in range(n)],np.int32)
    m=np.zeros((h,w),np.float32); cv2.fillPoly(m,[poly],1.0,cv2.LINE_AA); m=m[...,None]
    blades=steel((0.30,0.33,0.36))*(0.6+0.4*np.cos(np.arctan2(yy-cy,xx-cx)*n+rot*n))[...,None]
    for j in range(n):
        p=poly[j]; a=rot+j*2*math.pi/n+math.pi/2
        cv2.line(blades,(int(p[0]),int(p[1])),(int(p[0]+math.cos(a)*w*1.5),int(p[1]+math.sin(a)*w*1.5)),(0.08,0.09,0.10),4,cv2.LINE_AA)
    return src*m+blades*(1-m)
def compose(t,fi=None):
    if fi is None: fi=int(round(t*30))
    i=shot_at(max(t,0)); nxt=SHOTS[i+1] if i+1<len(SHOTS) else None; huds=[]
    if nxt and nxt[2]=="iris" and t>nxt[0]-TR:
        u=(t-(nxt[0]-TR))/(2*TR); b1,h1=render_shot(i,t); b2,h2=render_shot(i+1,t); b=iris(b1,b2,u)
    elif SHOTS[i][2]=="iris" and t<SHOTS[i][0]+TR and i>0:
        u=(t-(SHOTS[i][0]-TR))/(2*TR); b1,h1=render_shot(i-1,t); b2,h2=render_shot(i,t); b=iris(b1,b2,u); huds=[h2] if u>0.8 else []
    else:
        b,h1=render_shot(i,t); huds=[h1]
    b=post(b,bloom=0.5,thr=0.65,tint=(0.96,1.0,1.05))
    img=to_img(b,fi)
    for hf in huds:
        if hf: hf(img)
    ha=1-sm((t-(Ls(1)-0.4))/0.25) if t<Ls(1) else sm((t-(TOTAL-0.6))/0.3)
    if ha>0.01:
        hook_title(img,[("HIS SALIVA BOILED",WHITE)],a=ha,y=250,size=124)
        s2=wt(0,"boil")-0.05
        if t>=s2 or t>TOTAL-0.6:
            a2=ha*(sm((t-s2)/0.08) if t<Ls(1) else 1.0); sc=0.7+0.3*spring((t-s2)/0.22) if t<Ls(1) else 1.0
            hook_title(img,[("IN A VACUUM",ORANGE)],a=a2,y=390,size=150,sc=sc)
    return finish(img,CAP,t)
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
