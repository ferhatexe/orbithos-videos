import numpy as np, cv2, json, math, sys
from PIL import Image, ImageDraw, ImageFont
TL=json.load(open("timeline.json")); LINES=TL["lines"]; SC=TL["scenes"]; TOTAL=TL["total"]
w,h=540,960; W,H=1080,1920; FPS=30
ST=np.load("stars.npy"); CLOUD=np.load("cloud.npy")
FD="/mnt/skills/examples/canvas-design/canvas-fonts/" if __import__("os").path.isdir("/mnt/skills/examples/canvas-design/canvas-fonts/") else "/home/claude/toolkit/assets/fonts/"
def F(n,s): return ImageFont.truetype(FD+n+".ttf",s)
def CZ(s,wt=600): f=ImageFont.truetype("Cinzel.ttf",s); f.set_variation_by_axes([wt]); return f
fEN=F("Outfit-Bold",60); fMono=F("GeistMono-Regular",26); fMonoS=F("GeistMono-Regular",22); fBig=F("BigShoulders-Bold",120)
WM=Image.open("wm_orbithos.png").convert("RGBA")
yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
vig=(1-0.4*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
grain=[np.random.default_rng(i).normal(0,0.014,(h,w,1)).astype(np.float32) for i in range(8)]
def cl(x): return min(max(x,0.0),1.0)
def sm(x): x=cl(x); return x*x*(3-2*x)
def ein(x): x=cl(x); return x*x*x
def eout(x): x=cl(x); return 1-(1-x)**3
def L(i): return LINES[i]["s"],LINES[i]["e"]
NAMES=[s["name"] for s in SC]
def S(n): return SC[NAMES.index(n)]
def scene_at(t):
    for s in SC:
        if s["s"]<=t<s["e"]: return s
    return SC[-1]
def lerp(a,b,k): return np.array(a,np.float32)*(1-k)+np.array(b,np.float32)*k
HZ=int(h*0.60)   # horizon
# ---------- sky ----------
def sky(buf,top,hor,yh=HZ):
    g=np.clip(yy/yh,0,1)[...,None]**1.3
    buf[:]=np.array(top,np.float32)*(1-g)+np.array(hor,np.float32)*g
def stars(buf,gain=1.0,rot=0.0,cx=0.5,cy=0.3,zoom=1.0,maxy=HZ):
    x,y,z,b=ST[:,0],ST[:,1],ST[:,2],ST[:,3]; c,s=math.cos(rot),math.sin(rot)
    px=cx*w+(x*c-y*s)*zoom*h*0.5; py=cy*h+(x*s+y*c)*zoom*h*0.5
    col=ST[:,4:7]*(b*gain)[:,None]; m=(px>=0)&(px<w-1)&(py>=0)&(py<maxy-2)
    for k in range(3): np.add.at(buf[:,:,k],(py[m].astype(int),px[m].astype(int)),col[m,k])
def glowpt(buf,x,y,col,r=4,a=1.0,spread=12):
    x0,y0=int(max(0,x-spread*4)),int(max(0,y-spread*4)); x1,y1=int(min(w,x+spread*4)),int(min(h,y+spread*4))
    if x1<=x0 or y1<=y0: return
    g=np.zeros((y1-y0,x1-x0),np.float32); cv2.circle(g,(int(x-x0),int(y-y0)),max(1,int(r)),1.0,-1,cv2.LINE_AA)
    g=cv2.GaussianBlur(g,(0,0),max(0.8,r*0.4))*1.5+cv2.GaussianBlur(g,(0,0),spread)*2.2
    buf[y0:y1,x0:x1]+=g[...,None]*np.array(col,np.float32)*a
def sun_eclipse(buf,cx,cy,R,t,cover):
    # cover 0..1 (1 = total)
    X=xx-cx; Y=yy-cy; r=np.sqrt(X*X+Y*Y)/R
    mx=cx+R*2.1*(1-cover); my=cy-R*0.25*(1-cover)
    rm=np.sqrt((xx-mx)**2+(yy-my)**2)/(R*1.02)
    disk=(r<1.0)*(rm>=1.0)
    glow=np.exp(-np.maximum(r-1,0)*2.5)*0.6*(1-cover*0.9)
    buf+=(disk*3.0)[...,None]*np.array([1.0,0.95,0.85],np.float32)+glow[...,None]*np.array([1.0,0.9,0.7],np.float32)
    if cover>0.9:
        k=(cover-0.9)/0.1; ang=np.arctan2(Y,X)
        cor=np.exp(-np.maximum(r-1,0)*2.0)*(0.6+0.4*np.sin(ang*9+t*0.3)*np.sin(ang*4))*(r>=1.0)
        ring=np.exp(-((r-1.0)/0.03)**2)*1.5
        buf+=((cor*1.2+ring)*k)[...,None]*np.array([0.85,0.92,1.0],np.float32)
        buf[(rm<1.0)&(r<1.2)]*=0.05
# ---------- sea ----------
def sea(buf,t,sunx=None,glit=1.0,deep=(0.02,0.16,0.32),near=(0.0,0.07,0.16),sky_hor=(0.6,0.8,0.95),storm=0.0):
    y=yy[HZ:]; x=xx[HZ:]; d=(y-HZ+2)
    z=60.0/d
    g=np.clip(d/(h-HZ),0,1)[...,None]
    base=np.array(deep,np.float32)*(1-g)+np.array(near,np.float32)*g
    amp=(1+storm*1.5)*np.clip((d-3)/110,0,1)
    Xw=(x-w/2)/d*40; Zw=400/d; CH=CLOUD.shape[0]
    n1=CLOUD[((Zw*2.0+t*25)%CH).astype(np.int32)%CH,((Xw*0.7+t*5)%w).astype(np.int32)%w]
    n2=CLOUD[((Zw*5.0-t*40)%CH).astype(np.int32)%CH,((Xw*1.9+200)%w).astype(np.int32)%w]
    wv=((n1-0.5)*2.2+(n2-0.5)*1.2)*amp*1.6
    shade=(0.10*wv*np.clip(1-z*0.02,0.2,1))[...,None]
    refl=np.exp(-d/30.0)[...,None]*np.array(sky_hor,np.float32)*0.55
    col=base*(1+shade*2.5)+refl+np.array([0.05,0.12,0.16],np.float32)*np.clip(wv,0,None)[...,None]*0.18
    if sunx is not None:
        spread=10+d*0.8
        col_g=np.exp(-((x-sunx)/spread)**2)*(np.clip(n2-0.55,0,1)*6)**2*np.clip(d/40,0.2,1)
        col+=(col_g*glit*2.2)[...,None]*np.array([1.0,0.92,0.75],np.float32)
    buf[HZ:]=col
    # foam at storm
    if storm>0:
        fo=np.clip(wv-1.0,0,1)*storm*0.5
        buf[HZ:]+=fo[...,None]*0.5
# ---------- islands ----------
_r=np.random.default_rng(4)
def mk_island(x0,x1,hmax,seed):
    g=np.random.default_rng(seed); xs=np.linspace(x0,x1,30); c=(x0+x1)/2
    hs=hmax*np.clip(1-((xs-c)/((x1-x0)/2))**2,0,1)**0.7*(0.8+0.25*g.random(30))
    return [(float(a),HZ-float(b)) for a,b in zip(xs,hs)]+[(x1,HZ),(x0,HZ)]
ISL=[(mk_island(-40,190,48,1),0.55),(mk_island(330,600,34,2),0.45),(mk_island(150,330,20,3),0.7)]
def islands(buf,col_far,col_near,which=(0,1,2),palace=False,lights=0.0,t=0):
    for i in which:
        pts,f=ISL[i]; col=tuple(float(v) for v in lerp(col_near,col_far,f))
        cv2.fillPoly(buf,[np.array(pts,np.int32)],col,cv2.LINE_AA)
    if palace:
        px,py=90,HZ-46
        c=tuple(float(v) for v in lerp(col_near,col_far,0.4))
        cv2.rectangle(buf,(px-30,py-18),(px+30,py+4),c,-1); cv2.fillPoly(buf,[np.array([(px-34,py-18),(px,py-30),(px+34,py-18)],np.int32)],c)
        for k in range(5):
            if lights>0: glowpt(buf,px-22+k*11,py-8,(1.0,0.7,0.3),r=1.2,a=lights*(0.7+0.3*math.sin(t*3+k)),spread=3)
# ---------- ship ----------
def ship(buf,x,y,t,s=1.0,col=(0.03,0.04,0.07),sail=(0.85,0.8,0.7),roll=0.0):
    ang=math.sin(t*1.3)*0.05+roll
    col=tuple(float(v) for v in col); sail=tuple(float(v) for v in sail)
    def R(px,py):
        c,sn=math.cos(ang),math.sin(ang); return (int(x+(px*c-py*sn)*s),int(y+(px*sn+py*c)*s))
    hull=[R(-60,0),R(-50,10),R(40,10),R(58,-2),R(66,-14),R(60,-4),R(-66,-6),R(-72,-18),R(-64,-4)]
    cv2.fillPoly(buf,[np.array(hull,np.int32)],col,cv2.LINE_AA)
    cv2.line(buf,R(0,0),R(0,-78),col,max(1,int(2*s)),cv2.LINE_AA)
    cv2.line(buf,R(-30,-70),R(30,-70),col,max(1,int(2*s)),cv2.LINE_AA)
    bil=math.sin(t*2)*3
    sl=[R(-30,-70),R(30,-70),R(28+bil,-22),R(-28+bil,-22)]
    cv2.fillPoly(buf,[np.array(sl,np.int32)],sail,cv2.LINE_AA)
    cv2.line(buf,R(-29,-46),R(29,-46),(sail[0]*0.7,sail[1]*0.25,sail[2]*0.2),max(1,int(3*s)),cv2.LINE_AA)
    for k in range(7):
        ox=-40+k*12; ph=math.sin(t*3+k*0.3)*5
        cv2.line(buf,R(ox,4),R(ox-8+ph,22),col,1,cv2.LINE_AA)
def clouds(buf,t,amt=0.6,col=(0.5,0.6,0.75),speed=6,yhi=HZ):
    off=int(t*speed)%h; c=CLOUD[off:off+h] if off+h<=CLOUD.shape[0] else np.vstack([CLOUD[off:],CLOUD[:off+h-CLOUD.shape[0]]])
    m=np.clip((c-0.5)*3,0,1)*np.clip((yhi-yy)/(h*0.25),0,1)*amt
    buf[:]=buf*(1-m[...,None])+m[...,None]*np.array(col,np.float32)
def rain(buf,t,a=0.3):
    g=np.random.default_rng(int(t*24))
    for k in range(160):
        x=g.uniform(0,w); y=g.uniform(0,h); cv2.line(buf,(int(x),int(y)),(int(x-6),int(y+22)),(0.5*a,0.6*a,0.75*a),1)
# ---------- HUD ----------
def txt(d,xy,s,f,fill,anchor="la",stroke=0):
    if len(fill)>3 and fill[3]<=1: return
    x0,y0,x1,y1=d.textbbox(xy,s,font=f,anchor=anchor,stroke_width=stroke)
    x0,y0=int(x0)-2,int(y0)-2; lay=Image.new("RGBA",(max(1,int(x1)-x0+4),max(1,int(y1)-y0+4)),(0,0,0,0))
    ImageDraw.Draw(lay).text((xy[0]-x0,xy[1]-y0),s,font=f,fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=(0,20,40,int(fill[3]*0.6)) if stroke else None)
    d._image.alpha_composite(lay,(max(0,x0),max(0,y0)),(max(0,-x0),max(0,-y0)))
def title(d,s,y,a,f=None,col=(250,236,200),sub=None,suby=None,subcol=(225,238,250)):
    if a<=0.01: return
    f=f or CZ(118,700); txt(d,(W//2,y),s,f,col+(int(255*a),),anchor="mm",stroke=3)
    if sub: txt(d,(W//2,suby or y+90),sub,CZ(40,500),subcol+(int(235*a),),anchor="mm",stroke=2)
def fa(t,s,e,fi=0.4,fo=0.4): return sm((t-s)/fi)*(1-sm((t-e)/fo))
def hud_frame(d,a,label,col=(210,235,255)):
    A=int(210*a); c=col+(A,); m=70; Lg=60
    for (x,y,dx,dy) in [(m,m+120,1,1),(W-m,m+120,-1,1),(m,H-m-260,1,-1),(W-m,H-m-260,-1,-1)]:
        d.line([(x,y),(x+dx*Lg,y)],fill=c,width=3); d.line([(x,y),(x,y+dy*Lg)],fill=c,width=3)
    txt(d,(m+20,m+140),label,fMono,c)
def reticle(d,x,y,a=1.0,col=(255,210,120),label=None,sz=40):
    c=col+(int(235*a),)
    for sx,sy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
        d.line([(x+sx*sz,y+sy*sz),(x+sx*(sz-14),y+sy*sz)],fill=c,width=3); d.line([(x+sx*sz,y+sy*sz),(x+sx*sz,y+sy*(sz-14))],fill=c,width=3)
    if label: txt(d,(x+sz+12,y-sz),label,fMono,c,stroke=2)
LAYOUT={}
def layout(i):
    if i in LAYOUT: return LAYOUT[i]
    rows=[[]]; cur=0; sp=fEN.getlength(" ")
    for wd in LINES[i]["en"].split(" "):
        lw=fEN.getlength(wd)
        if rows[-1] and cur+sp+lw>900: rows.append([]); cur=0
        cur+=(sp if rows[-1] else 0)+lw; rows[-1].append(wd)
    LAYOUT[i]=rows; return rows
def subtitles(d,t):
    for ln in LINES:
        s,e=ln["s"],ln["e"]; i=ln["i"]; nxt=LINES[i+1]["s"] if i+1<len(LINES) else e+1.2
        fe=min(e+0.45,nxt-0.03)
        if not (s-0.05<=t<=fe): continue
        rows=layout(i); aout=1-sm((t-(fe-0.15))/0.15)
        words=[x for r in rows for x in r]; tot=sum(len(x)+1 for x in words); acc=0
        y0=1330-(len(rows)-1)*37; pro=ln["kind"]=="x"
        if pro: txt(d,(W/2,y0-82),"THE PROPHET",fMonoS,(180,220,255,int(220*aout*sm((t-s)/0.2))),anchor="ms")
        for ri,r in enumerate(rows):
            rw=sum(fEN.getlength(x) for x in r)+fEN.getlength(" ")*(len(r)-1); x=W/2-rw/2; y=y0+ri*74
            for wd in r:
                ws=s+(acc/tot)*(e-s)*0.92; acc+=len(wd)+1; a=sm((t-ws+0.02)/0.12)*aout
                cur=ws<=t<ws+(len(wd)+1)/tot*(e-s)*0.92+0.05
                col=(170,215,255) if pro else ((255,205,110) if cur else (255,255,255))
                lift=int((1-sm((t-ws)/0.15))*14)
                if a>0.01: txt(d,(x,y+lift),wd,fEN,col+(int(255*a),),anchor="ls",stroke=4)
                x+=fEN.getlength(wd+" ")
HITS=[0.35]+[s["s"] for s in SC[1:]]
def fx_at(t):
    fl=punch=rgb=0
    for hh in HITS:
        dt=t-hh
        if 0<=dt<0.5: fl=max(fl,math.exp(-dt*9)); punch=max(punch,math.exp(-dt*7)); rgb=max(rgb,math.exp(-dt*10))
    return fl*0.7,punch,rgb
DAYSKY=((0.10,0.34,0.72),(0.62,0.80,0.95)); DUSK=((0.05,0.12,0.30),(0.95,0.60,0.40)); NIGHT=((0.02,0.05,0.14),(0.10,0.20,0.38))
def day_scene(buf,t,dark=0.0,shipx=None,storm=0.0,sunxy=(380,250),cover=0.0,isl=True):
    top=lerp(DAYSKY[0],(0.015,0.035,0.11),dark); hor=lerp(DAYSKY[1],(0.10,0.18,0.35),dark)
    if storm>0: top=lerp(top,(0.12,0.18,0.28),storm); hor=lerp(hor,(0.30,0.38,0.48),storm)
    sky(buf,top,hor)
    if dark>0.3: stars(buf,gain=(dark-0.3)*1.2)
    if storm<0.5: sun_eclipse(buf,sunxy[0],sunxy[1],34,t,cover)
    clouds(buf,t,amt=0.35+0.6*storm,col=tuple(lerp((0.85,0.9,0.97),(0.18,0.22,0.3),max(dark,storm))))
    sea(buf,t,sunx=sunxy[0] if storm<0.5 else None,glit=(1-dark)*(1-storm),deep=tuple(lerp((0.03,0.20,0.40),(0.01,0.05,0.12),max(dark,storm*0.6))),
        near=tuple(lerp((0.01,0.10,0.22),(0.0,0.03,0.07),max(dark,storm*0.6))),sky_hor=tuple(hor),storm=storm)
    if isl: islands(buf,tuple(lerp((0.45,0.58,0.72),(0.06,0.1,0.18),max(dark,storm*0.6))),tuple(lerp((0.18,0.28,0.40),(0.02,0.04,0.08),max(dark,storm*0.6))))
    if shipx is not None: ship(buf,shipx,HZ+38,t,s=1.0,roll=0.12*storm*math.sin(t*2.3),col=tuple(lerp((0.04,0.06,0.10),(0.01,0.01,0.02),dark)),sail=tuple(lerp((0.92,0.86,0.74),(0.25,0.24,0.22),max(dark,storm*0.5))))
def frame(t):
    sc=scene_at(t); n=sc["name"]; lt=t-sc["s"]; D=sc["e"]-sc["s"]
    buf=np.zeros((h,w,3),np.float32); hud=[]; shake=0.0; dark=1.0; flash=0.0
    if n=="hook":
        if t<0.35: return None,[],0
        cov=eout((t-0.35)/4.2); dk=sm((cov-0.6)/0.4)*0.85
        day_scene(buf,t,dark=dk,sunxy=(270,250),cover=cov)
    elif n=="title":
        day_scene(buf,t,sunxy=(400,230),shipx=w*0.35+lt*6)
        hud.append(lambda d,t=t,lt=lt,D=D:title(d,"THE ODYSSEY",520,fa(lt,0.1,D-0.2),sub="HOMER"))
    elif n=="voyage":
        day_scene(buf,t,sunxy=(420,210),shipx=w*0.25+lt*14)
        s3,e3=L(3); s4,e4=L(4)
        def hd(d,t=t):
            title(d,"10 YEARS OF WAR",420,fa(t,s3,e3),f=fBig,col=(255,255,255))
            title(d,"10 YEARS AT SEA",420,fa(t,s4,e4+0.4),f=fBig,col=(255,215,130))
        hud.append(hd)
    elif n=="storm":
        day_scene(buf,t,storm=0.9,shipx=w*0.45+math.sin(t)*20)
        rain(buf,t,a=0.5); shake=0.25
        if (t%3.1)<0.12: flash=0.6
    elif n=="ithaca":
        sky(buf,*DUSK); stars(buf,gain=0.25,maxy=int(HZ*0.5))
        glowpt(buf,400,HZ-8,(1.0,0.55,0.25),r=18,a=0.8,spread=40)
        sea(buf,t,sunx=400,glit=0.6,deep=(0.05,0.10,0.24),near=(0.01,0.04,0.10),sky_hor=DUSK[1])
        islands(buf,(0.30,0.28,0.40),(0.05,0.06,0.12),which=(0,2),palace=True,lights=sm(lt/2),t=t)
        ship(buf,w*0.62-lt*10,HZ+34,t,s=0.8,sail=(0.8,0.6,0.5))
        s6,_=L(6)
        hud.append(lambda d,t=t:title(d,"ITHACA",400,fa(t,s6,s6+3.0),sub="ODYSSEUS'S HOME"))
    elif n=="prophet":
        s8,e8=L(8); cov=0.55+0.45*sm((t-s8)/(e8-s8))
        day_scene(buf,t,dark=0.25+0.6*sm((t-s8)/(e8-s8)),sunxy=(270,230),cover=cov,isl=True)
        islands(buf,(0.1,0.12,0.2),(0.02,0.03,0.06),which=(0,),palace=True,lights=0.8,t=t)
        hud.append(lambda d,t=t:txt(d,(90,300),"ODYSSEY · BOOK 20 · LINES 356–357",fMonoS,(210,235,255,int(190*fa(t,s8-0.3,e8+0.5)))))
    elif n=="scholars":
        sky(buf,(0.04,0.10,0.26),(0.35,0.45,0.62)); stars(buf,gain=0.5)
        sea(buf,t,deep=(0.03,0.10,0.22),near=(0.01,0.04,0.10),sky_hor=(0.35,0.45,0.62))
        islands(buf,(0.25,0.3,0.42),(0.06,0.08,0.15))
        s9,e9=L(9); s10,e10=L(10)
        def hd(d,t=t):
            title(d,"POETRY?",440,fa(t,s9+0.8,e9+0.3),f=CZ(110,700))
            title(d,"METAPHOR?",440,fa(t,s10,e10+0.6),f=CZ(110,700),col=(200,225,255))
        hud.append(hd)
    elif n in ("science","search"):
        buf[:]=lerp((0.02,0.07,0.18),(0.05,0.16,0.32),np.clip(yy/h,0,1)[...,None])
        rot=lt*(0.05 if n=="science" else 0.6+0.9*sm(lt/6)*(1-sm((lt-(D-3))/2)))
        stars(buf,gain=1.1,rot=rot,cx=0.5,cy=0.42,zoom=1.2,maxy=h)
        for r in range(60,520,70): cv2.circle(buf,(270,int(h*0.42)),r,(0.10,0.22,0.38),1,cv2.LINE_AA)
        for k in range(12):
            a=k*math.pi/6+rot; cv2.line(buf,(270,int(h*0.42)),(int(270+math.cos(a)*600),int(h*0.42+math.sin(a)*600)),(0.08,0.18,0.32),1,cv2.LINE_AA)
        if n=="science":
            s11,_=L(11); s13,e13=L(13)
            def hd(d,t=t):
                hud_frame(d,1.0,"PNAS · 2008")
                txt(d,(90,300),"BAIKOUZIS & MAGNASCO",fMonoS,(210,235,255,int(200*sm((t-s11)/0.4))))
                txt(d,(90,332),"ROCKEFELLER UNIVERSITY · LA PLATA OBSERVATORY",fMonoS,(170,200,235,int(170*sm((t-s11-0.5)/0.4))))
                a=sm((t-s13-1.2)/0.3)
                for k in range(4): txt(d,(W//2-330+k*170,520),f"CLUE {k+1}",fMono,(255,210,120,int(230*sm((t-s13-1.2-k*0.25)/0.25))),anchor="mm",stroke=2)
            hud.append(hd)
        else:
            s20,e20=L(20); s22,e22=L(22)
            def hd(d,t=t):
                hud_frame(d,1.0,"SKY SIMULATION // REVERSE")
                p=sm((t-s20)/(e22-s20)); yr=int(1250-135*p)
                title(d,f"{yr} BC",470,sm((t-s20)/0.3),f=fBig,col=(255,255,255))
                labels=["NEW MOON","VENUS","PLEIADES + BOÖTES","MERCURY"]
                for k,lb in enumerate(labels):
                    on=(math.sin(t*(7+k*3.1)+k)>0.3) if p<0.97 else True
                    col=(120,255,160) if (p>=0.97) else ((255,210,120) if on else (90,110,140))
                    txt(d,(170,640+k*44),("✓ " if p>=0.97 else "· ")+lb,fMono,col+(230,))
            hud.append(hd)
    elif n in ("c1","c2","c3","c4"):
        if n=="c1":
            sky(buf,(0.02,0.06,0.18),(0.12,0.24,0.42)); stars(buf,gain=0.9)
            cv2.circle(buf,(300,260),40,(0.05,0.07,0.12),-1,cv2.LINE_AA); cv2.circle(buf,(300,260),40,(0.25,0.3,0.4),1,cv2.LINE_AA)
            lab,day,pos="NEW MOON","DAY 0",(300,260)
        elif n=="c2":
            sky(buf,(0.05,0.14,0.36),(0.98,0.72,0.55)); stars(buf,gain=0.35)
            glowpt(buf,330,190,(1.0,1.0,0.95),r=3,a=1.8,spread=10); lab,day,pos="VENUS","DAY −6",(330,190)
        elif n=="c3":
            sky(buf,(0.03,0.10,0.28),(0.85,0.55,0.45)); stars(buf,gain=0.5)
            g=np.random.default_rng(2)
            for k in range(7): glowpt(buf,150+g.normal(0,9),180+g.normal(0,7),(0.8,0.9,1.0),r=1.2,a=0.9,spread=4)
            B=[(390,300),(372,250),(385,205),(410,170),(430,210),(425,255)]
            cv2.polylines(buf,[np.array(B+[B[0]],np.int32)],False,(0.35,0.45,0.6),1,cv2.LINE_AA)
            for p_ in B: glowpt(buf,p_[0],p_[1],(0.9,0.9,1.0),r=1.3,a=0.9,spread=4)
            glowpt(buf,390,300,(1.0,0.7,0.4),r=2.5,a=1.3,spread=7)
            lab,day,pos="PLEIADES + BOÖTES","DAY −29",None
        else:
            sky(buf,(0.05,0.14,0.36),(0.95,0.68,0.50)); stars(buf,gain=0.3)
            glowpt(buf,120,250,(1.0,0.9,0.75),r=2,a=1.4,spread=6)
            lab,day,pos="MERCURY","DAY −33",(120,250)
        sea(buf,t,deep=(0.03,0.12,0.28),near=(0.01,0.05,0.12),sky_hor=(0.6,0.55,0.6))
        islands(buf,(0.25,0.28,0.42),(0.05,0.07,0.14))
        if n=="c3": ship(buf,w*0.55+lt*6,HZ+38,t,s=0.8,sail=(0.75,0.6,0.55))
        k=int(n[1])
        def hd(d,t=t,lab=lab,day=day,pos=pos,k=k,n=n):
            hud_frame(d,1.0,f"CLUE {k} / 4")
            title(d,day,300,sm((t-S(n)["s"])/0.3),f=fBig,col=(255,255,255))
            if pos: reticle(d,pos[0]*2,pos[1]*2,sm((t-S(n)["s"]-0.4)/0.3),label=lab)
            else:
                txt(d,(300-40,420),"PLEIADES",fMono,(200,225,255,220),anchor="mm",stroke=2); txt(d,(820,690),"BOÖTES",fMono,(200,225,255,220),anchor="mm",stroke=2)
        hud.append(hd)
    elif n=="date":
        sky(buf,(0.02,0.07,0.2),(0.2,0.35,0.55)); stars(buf,gain=0.8)
        sea(buf,t,deep=(0.02,0.08,0.2),near=(0.01,0.03,0.08),sky_hor=(0.2,0.35,0.55))
        islands(buf,(0.2,0.25,0.38),(0.04,0.06,0.12))
        s23,_=L(23)
        hud.append(lambda d,t=t:(title(d,"APRIL 16",470,sm((t-s23)/0.25),f=CZ(128,800),col=(255,220,140)),title(d,"1178 BC",610,sm((t-s23-0.35)/0.25),f=CZ(96,700))))
        shake=0.3*math.exp(-lt*3)
    elif n=="eclipse":
        s25,e25=L(25); cov=0.7+0.3*sm((t-s25)/1.2); dk=0.3+0.55*sm((t-s25)/1.5)
        day_scene(buf,t,dark=dk,sunxy=(270,230),cover=cov)
        if cov>0.99: glowpt(buf,390,300,(1.0,1.0,0.95),r=2,a=1.2*sm((t-s25-1.2)/1.0),spread=7)
        islands(buf,(0.1,0.12,0.2),(0.02,0.03,0.06),which=(0,),palace=True,lights=0.9,t=t)
        hud.append(lambda d,t=t:(txt(d,(90,300),"TOTAL SOLAR ECLIPSE",fMonoS,(210,235,255,int(200*sm((t-s25)/0.4)))),txt(d,(90,332),"PATH OF TOTALITY: IONIAN ISLANDS",fMonoS,(210,235,255,int(200*sm((t-s25-0.4)/0.4))))))
    elif n in ("doubt","end"):
        k=sm(lt/D) if n=="end" else 0
        top=lerp((0.06,0.16,0.38),(0.02,0.05,0.16),k); hor=lerp((0.95,0.62,0.45),(0.35,0.3,0.45),k)
        sky(buf,top,hor); stars(buf,gain=0.2+0.8*k)
        glowpt(buf,300,HZ-6,(1.0,0.6,0.3),r=16,a=0.9*(1-k),spread=36)
        sea(buf,t,sunx=300,glit=0.7*(1-k),deep=(0.04,0.12,0.28),near=(0.01,0.04,0.10),sky_hor=tuple(hor))
        islands(buf,(0.35,0.32,0.45),(0.06,0.07,0.14))
        ship(buf,w*0.3+(t-S("doubt")["s"])*7,HZ+36,t,s=0.9,sail=(0.85,0.65,0.55))
        if n=="end":
            dark=1-sm((t-(S("end")["e"]-1.4))/1.2)
            s30,_=L(30); hud.append(lambda d,t=t:title(d,"HE WAS REMEMBERING A SKY",430,0.0))
    # ---- post ----
    small=cv2.resize(buf,(w//4,h//4),interpolation=cv2.INTER_AREA)
    br=np.maximum(small-0.8,0); bl=cv2.GaussianBlur(br,(0,0),3)+cv2.GaussianBlur(br,(0,0),10)*1.2
    buf=buf+cv2.resize(bl,(w,h))*0.7
    buf=1-np.exp(-buf*1.35)
    buf=buf*vig+grain[int(t*FPS)%8]
    fl,punch,rgb=fx_at(t); fl=max(fl,flash)
    sx=sy=0
    if shake>0: sx=math.sin(t*37)*6*shake; sy=math.cos(t*29)*6*shake
    M=cv2.getRotationMatrix2D((w/2,h/2),0,1+0.05*punch); M[0,2]+=sx; M[1,2]+=sy
    buf=cv2.warpAffine(buf,M,(w,h),borderMode=cv2.BORDER_REFLECT)
    if rgb>0.05: k=int(5*rgb); buf[:,:,0]=np.roll(buf[:,:,0],k,1); buf[:,:,2]=np.roll(buf[:,:,2],-k,1)
    buf=(buf+fl*0.8)*dark
    return buf,hud,dark
def compose(t):
    buf,hud,dk=frame(t)
    if buf is None: img=Image.new("RGB",(W,H),(0,0,0))
    else: img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC))
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    subtitles(d,t); ov.alpha_composite(WM,((W-WM.width)//2,1775))
    img=img.convert("RGBA"); img.alpha_composite(ov); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
