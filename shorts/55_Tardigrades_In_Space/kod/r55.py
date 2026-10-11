import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid55")
for p in ["/home/claude/vid55","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from drawkit import part, dl, circ_pts, rotp
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= palette (colourised scanning-electron micrograph) =================
FALSE1=(1.0,0.58,0.22); FALSE2=(0.30,0.80,0.95); FALSE3=(0.60,0.95,0.55)
cW=(240,242,246); cO=(255,160,70); cC=(90,210,245); cY=(255,220,90)
_IF={}
def _f(path,s):
    k=(path,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(path,s)
    return _IF[k]
FM=P.FD+"GeistMono-Bold.ttf"; FT=P.FD+"BigShoulders-Bold.ttf"
def ttl(d,s,x,y,fs=120,a=1.0,sc=1.0,col=cW):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f(FT,n)
    while f.getlength(s)>1000 and n>20: n-=6; f=_f(FT,n)
    d.text((x,y),s,font=f,fill=col+(int(255*a),),anchor="mm",stroke_width=5,stroke_fill=(0,0,0,int(220*a)))
def tagm(d,s,x,y,fs=40,a=1.0,sc=1.0,col=cW):
    """SEM annotation: mono text in a thin white box"""
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f(FM,n); bb=d.textbbox((0,0),s,font=f); tw,th=bb[2]-bb[0],bb[3]-bb[1]; px,py=int(n*0.5),int(n*0.35)
    d.rectangle((x-tw/2-px,y-th/2-py,x+tw/2+px,y+th/2+py),fill=(0,0,0,int(170*a)),outline=col+(int(255*a),),width=3)
    d.text((x,y),s,font=f,fill=col+(int(255*a),),anchor="mm")
def databar(d,mag,scale_txt,a=1.0):
    y0=96; d.rectangle((0,y0-34,W,y0+34),fill=(0,0,0,int(200*a)))
    f=_f(FM,30)
    d.text((40,y0),f"HV 15.0 kV   WD 9.8 mm   MAG {mag}",font=f,fill=(225,228,232,int(255*a)),anchor="lm")
    d.line((W-330,y0,W-170,y0),fill=(240,240,240,int(255*a)),width=5); d.line((W-330,y0-10,W-330,y0+10),fill=(240,240,240,int(255*a)),width=3); d.line((W-170,y0-10,W-170,y0+10),fill=(240,240,240,int(255*a)),width=3)
    d.text((W-60,y0),scale_txt,font=f,fill=(225,228,232,int(255*a)),anchor="rm")
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= height-map scene builder =================
_g=np.random.default_rng(2007)
NZ=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),1.2); NZ/=NZ.std()
NZ2=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),4); NZ2/=NZ2.std()
class HM:
    def __init__(s): s.H=np.zeros((h,w),np.float32); s.T={}   # height + false-colour tags
    def ell(s,cx,cy,rx,ry,ht,tag=None,ang=0.0,ridges=0.0):
        R=int(max(rx,ry))+2; x0,y0=max(0,int(cx-R)),max(0,int(cy-R)); x1,y1=min(w,int(cx+R)+1),min(h,int(cy+R)+1)
        if x1<=x0 or y1<=y0: return
        X=xx[y0:y1,x0:x1]-cx; Y=yy[y0:y1,x0:x1]-cy
        if ang: c,sn=math.cos(ang),math.sin(ang); X,Y=X*c+Y*sn,-X*sn+Y*c
        d2=(X/rx)**2+(Y/ry)**2; z=np.sqrt(np.clip(1-d2,0,1))*ht
        if ridges: z=z*(1+ridges*np.sin(X/ max(rx,1)*14))*(d2<1)
        np.maximum(s.H[y0:y1,x0:x1],z,out=s.H[y0:y1,x0:x1])
        if tag is not None:
            if tag not in s.T: s.T[tag]=np.zeros((h,w),np.float32)
            np.maximum(s.T[tag][y0:y1,x0:x1],(d2<1).astype(np.float32),out=s.T[tag][y0:y1,x0:x1])
    def tube(s,p0,p1,r,ht,tag=None,n=8):
        for k in range(n+1):
            f=k/n; s.ell(p0[0]+(p1[0]-p0[0])*f,p0[1]+(p1[1]-p0[1])*f,r,r,ht,tag)
    def crater(s,cx,cy,r,depth=14):
        R=int(r*1.6)+2; x0,y0=max(0,int(cx-R)),max(0,int(cy-R)); x1,y1=min(w,int(cx+R)+1),min(h,int(cy+R)+1)
        if x1<=x0 or y1<=y0: return
        d=np.sqrt((xx[y0:y1,x0:x1]-cx)**2+((yy[y0:y1,x0:x1]-cy)*1.8)**2)/r
        s.H[y0:y1,x0:x1]+=(-depth*np.clip(1-d*d,0,1)+depth*0.6*np.exp(-((d-1.05)/0.18)**2))
    def render(s,amb=0.06):
        Hs=cv2.GaussianBlur(s.H,(0,0),0.8)
        gx=cv2.Sobel(Hs,cv2.CV_32F,1,0,ksize=3)/8; gy=cv2.Sobel(Hs,cv2.CV_32F,0,1,ksize=3)/8
        slope=np.sqrt(gx*gx+gy*gy)
        lam=np.clip(0.5-0.6*(gx*0.7+gy*0.7)/(slope+0.6),0,1)
        obj=(s.H>0.3).astype(np.float32)
        Ib=0.10+0.55*np.tanh(slope*0.9)+0.28*lam*obj+0.05*NZ*obj+0.04*NZ2*obj
        Ib=Ib*obj+(amb+0.025*NZ)*(1-obj)
        out=np.repeat(np.clip(Ib,0,1.2)[...,None],3,2)
        for tag,A in s.T.items():
            col=np.array(tag,np.float32); A=cv2.GaussianBlur(A,(0,0),1.0)*obj
            out=out*(1-0.55*A[...,None])+(out*col*1.25)*(0.55*A[...,None])
        return out
def tardigrade(hm,x,y,s,t,curl=0.0,walk=1.0,tag=FALSE1,ang=0.0):
    """side-view water bear: 5 wrinkled body segments + 4 pairs of stubby clawed legs; curl -> 'tun' ball"""
    k=sm(curl)
    def R(px,py):
        c,sn=math.cos(ang),math.sin(ang); dx,dy=px-x,py-y; return (x+dx*c-dy*sn,y+dx*sn+dy*c)
    segs=[(-92,-2,30,26),(-52,-6,34,34),(-8,-8,38,36),(36,-6,36,34),(78,-2,30,28)]
    for i,(dx,dy,rx,ry) in enumerate(segs):
        px,py=x+dx*s*(1-k),y+dy*s*(1-k)
        rr=(1-k)*1.0+k*1.6
        cx,cy=R(px,py); hm.ell(cx,cy,rx*s*rr,ry*s*rr*(1-0.15*k),ry*s*0.9,tag,ang,ridges=0.06*(1-k))
    hx,hy=R(x+118*s*(1-k),y-2*s); hm.ell(hx,hy,20*s*(1-k)+1,18*s*(1-k)+1,16*s,tag,ang)
    if k<0.55:
        for i,dx in enumerate((-80,-38,6,52)):
            ph=t*6*walk+i*1.4; sw=math.sin(ph)*10*s*walk
            L=24*s*(1-k/0.55)
            p0=R(x+dx*s,y+18*s); p1=R(x+dx*s+sw*0.6,y+18*s+L)
            hm.tube(p0,p1,15*s*(1-k*0.8),14*s,tag,6)
            if k<0.3:
                for c in (-1,0,1): hm.tube((p1[0],p1[1]+8*s),(p1[0]+c*9*s+4*s,p1[1]+18*s*(1-k/0.3)),2.4*s,4*s,None,3)
def capsule(hm,x,y,s):
    hm.ell(x,y,70*s,70*s,60*s,None,ridges=0.05)
    for k in range(5): hm.ell(x-90*s+k*45*s,y+80*s,18*s,6*s,8*s)
    hm.tube((x+70*s,y),(x+170*s,y-10*s),8*s,8*s); hm.ell(x+200*s,y-12*s,40*s,24*s,6*s)
def earth_hm(hm,cx,cy,R):
    hm.ell(cx,cy,R,R,R*0.6)
def droplet(hm,x,y,r): hm.ell(x,y,r,r*1.15,r*0.9,FALSE2)
def lander(hm,x,y,s,ang=0.0):
    pts=[(-40,-30),(40,-30),(40,20),(-40,20)]
    hm.ell(x,y,46*s,30*s,30*s,None,ang)
    for sd in (-1,1): hm.tube((x+sd*36*s,y+20*s),(x+sd*70*s,y+70*s),5*s,6*s); hm.ell(x+sd*72*s,y+72*s,14*s,5*s,5*s)
    hm.ell(x,y-40*s,22*s,18*s,18*s,FALSE2)
_STARS=np.zeros((h,w),np.float32)
for k in range(260): cv2.circle(_STARS,(int(_g.uniform(0,w)),int(_g.uniform(0,h))),1,float(_g.uniform(0.2,0.9)),-1)
# ================= scenes =================
def s_hook(t,sc):
    tt=max(t,-1.0); hm=HM()
    tardigrade(hm,270,430+8*math.sin(tt*1.3),1.45,tt,0.0,0.6,FALSE1,0.08*math.sin(tt*0.9))
    buf=hm.render(0.03)+(_STARS*0.5)[...,None]*(hm.H<=0.3)[...,None]
    def hd(d,t=t):
        databar(d,"×180","500 µm")
        k0=1.0 if t<0.4 else ap(t,-1,EV["suit"])
        ttl(d,"SURVIVED SPACE",540,1220,124,a=k0,col=cW)
        tagm(d,"NAKED",540,1330,52,a=sm((t-EV["naked"]+0.1)/0.2)*(1-sm((t-EV["suit"])/0.3)),sc=pop(t,EV["naked"]-0.1),col=cO)
        tagm(d,"NO SUIT",300,1220,52,a=ap(t,EV["suit"],sc["e"]+1),sc=pop(t,EV["suit"]-0.1),col=cO)
        tagm(d,"NO SHIP",780,1220,52,a=ap(t,EV["ship"],sc["e"]+1),sc=pop(t,EV["ship"]-0.1),col=cO)
        tagm(d,"~0.5 mm",540,320,48,a=ap(t,EV["half"],sc["e"]+1),sc=pop(t,EV["half"]-0.1),col=cC)
        ttl(d,"HOW?",540,1330,110,a=ap(t,EV["how"],sc["e"]+1),sc=pop(t,EV["how"]-0.1),col=cY)
    return buf,[hd]
def s_meet(t,sc):
    hm=HM()
    pT=sm((t-EV["curls"]+0.2)/1.4)
    pH=sm((t-EV["everywhere"]+0.3)/0.4)*(1-sm((t-EV["bad"]+0.2)/0.4))
    if pH<=0.01:
        x=270+(0 if pT>0 else 30*math.sin((t-sc["s"])*0.5))
        tardigrade(hm,x,430,1.35 if pT<=0 else 1.35-0.15*pT,t,pT,1.0*(1-pT),FALSE1)
        if pT>0.3:
            for k in range(26):
                an=k*0.9; r=38+18*math.sin(k*3.1)
                hm.ell(x+math.cos(an)*r*1.2,430+math.sin(an)*r*0.9,9,4,3*pT,FALSE1,an)
    else:
        # habitats: moss cushion (left), mountain (centre), sea floor (right) with tiny bears
        g=np.random.default_rng(5)
        for k in range(60): hm.ell(g.uniform(20,200),g.uniform(380,600),g.uniform(8,18),g.uniform(14,30),g.uniform(10,22),FALSE3)
        for k in range(30):
            xk=230+k*3; hm.ell(xk+40*math.sin(k*0.4),600-k*10,40-k,16,30-k*0.6)
        for k in range(8): hm.ell(380+k*20,600-((k*37)%30),14,40+((k*13)%40),20,FALSE2)
        tardigrade(hm,110,480,0.35,t,0,1,FALSE1); tardigrade(hm,280,330,0.3,t,0,1,FALSE1); tardigrade(hm,440,470,0.32,t,0,1,FALSE1)
    buf=hm.render(0.05)
    def hd(d,t=t,pH=pH):
        databar(d,"×200" if pH<0.5 else "×40","500 µm" if pH<0.5 else "2 mm")
        ttl(d,"TARDIGRADE",540,1220,130,a=ap(t,EV["tardi"],EV["legs"]),sc=pop(t,EV["tardi"]-0.1),col=cO)
        tagm(d,"“WATER BEAR”",540,1330,46,a=ap(t,EV["bear"],EV["legs"]),col=cC)
        tagm(d,"8 STUBBY LEGS",300,1200,44,a=ap(t,EV["legs"],EV["everywhere"]),sc=pop(t,EV["legs"]-0.1))
        tagm(d,"CLAWS",800,1200,44,a=ap(t,EV["claws"],EV["everywhere"]),sc=pop(t,EV["claws"]-0.1))
        tagm(d,"MOSS",220,1250,40,a=ap(t,EV["everywhere"],EV["bad"]),col=cY)
        tagm(d,"MOUNTAINS",540,1180,40,a=ap(t,EV["mountain"],EV["bad"]),col=cW)
        tagm(d,"DEEP SEA",860,1250,40,a=ap(t,EV["deepsea"],EV["bad"]),col=cC)
        ttl(d,"DRIES OUT",540,1220,120,a=ap(t,EV["dries"],EV["tun"]),sc=pop(t,EV["dries"]-0.1),col=cY)
        ttl(d,"THE “TUN”",540,1220,130,a=ap(t,EV["tun"],sc["e"]+1),sc=pop(t,EV["tun"]-0.1),col=cO)
        tagm(d,"METABOLISM ~ 0",540,1330,44,a=ap(t,EV["shuts"],sc["e"]+1),col=cC)
    return buf,[hd]
def s_space(t,sc):
    hm=HM()
    pW=sm((t-EV["back"]+0.3)/0.4)
    if pW<1:
        earth_hm(hm,270,1180,620)
        cx,cy=270+40*math.sin(t*0.3),330
        capsule(hm,cx-40,cy,1.0)
        op=sm((t-EV["opened"]+0.2)/0.4)
        g=np.random.default_rng(8)
        for k in range(14): hm.ell(cx-40+g.uniform(-60,60),cy+g.uniform(-55,55),5,5,66,FALSE1)
        buf=hm.render(0.02)+(_STARS*0.8)[...,None]*(hm.H<=0.3)[...,None]
        cr=sm((t-EV["cosmic"]+0.2)/0.4)
        if cr>0:
            m=M()
            for k in range(10):
                ph=(t*1.7+k*0.37)%1; x0=g.uniform(0,w); y0=-40+ph*1100
                m.line((x0,y0),(x0+40,y0+120),1.6)
            buf+=(m.f()*cr*0.8)[...,None]*np.array((0.8,0.9,1.0),np.float32)
        buf*=(1-pW)
    else: buf=np.zeros((h,w,3),np.float32)
    if pW>0:
        hm2=HM(); dk=sm((t-EV["water"]+0.6)/0.6)
        if t<EV["water"]: droplet(hm2,270,120+330*sm((t-EV["back"]+0.3)/1.4),40)
        wk=sm((t-EV["woke"]+0.3)/1.2)
        tardigrade(hm2,270,460,1.2,t,1-wk,wk,FALSE1)
        if dk>0: hm2.ell(270,520,260*dk,60*dk,6,FALSE2)
        eg=sm((t-EV["eggs"]+0.2)/0.5)
        for k in range(5): hm2.ell(130+k*70,620,16*eg+0.1,13*eg+0.1,12*eg,FALSE3)
        buf=buf+hm2.render(0.05)*pW
    def hd(d,t=t,pW=pW):
        databar(d,"×1" if pW<0.5 else "×160","1 m" if pW<0.5 else "500 µm")
        ttl(d,"2007",540,1220,130,a=ap(t,EV["y2007"],EV["opened"]),sc=pop(t,EV["y2007"]-0.1))
        tagm(d,"FOTON-M3 · ESA",540,1330,44,a=ap(t,EV["y2007"]+0.4,EV["opened"]),col=cC)
        ttl(d,"EXPOSED TO SPACE",540,1220,104,a=ap(t,EV["opened"],EV["tendays"]),sc=pop(t,EV["opened"]-0.1),col=cO)
        ttl(d,"10 DAYS",540,1220,130,a=ap(t,EV["tendays"],EV["back"]),sc=pop(t,EV["tendays"]-0.1))
        tagm(d,"VACUUM",300,1330,44,a=ap(t,EV["vacuum"],EV["back"]),col=cC); tagm(d,"COSMIC RAYS",780,1330,44,a=ap(t,EV["cosmic"],EV["back"]),col=cY)
        ttl(d,"+ WATER",540,1220,120,a=ap(t,EV["water"],EV["woke"]),sc=pop(t,EV["water"]-0.1),col=cC)
        ttl(d,"THEY WOKE UP",540,1220,110,a=ap(t,EV["woke"],sc["e"]+1),sc=pop(t,EV["woke"]-0.1),col=cO)
        tagm(d,"…AND LAID EGGS",540,1330,44,a=ap(t,EV["eggs"],sc["e"]+1),col=(150,240,140))
    return buf,[hd]
_gm=np.random.default_rng(19)
CRAT=[(_gm.uniform(0,w),_gm.uniform(470,960),_gm.uniform(14,60)) for _ in range(26)]
def s_moon(t,sc):
    hm=HM()
    pR=sm((t-EV["whyis"]+0.3)/0.4)
    for x,y,r in CRAT: hm.crater(x,y,r,10)
    hm.H+=np.clip((yy-460)/40,0,1)*20+NZ2*1.2*(yy>460)
    hm.H[yy<460]=0
    tc=EV["crashed"]
    if t<tc:
        k=sm((t-EV["lander"]+0.6)/(tc-EV["lander"]+0.6)); lander(hm,120+250*k,-60+560*k,1.0,0.5*k)
    else:
        g=np.random.default_rng(3); dk=1-math.exp(-(t-tc)*3)
        for i in range(20):
            an=g.uniform(math.pi,2*math.pi); dd=g.uniform(20,140)*dk
            hm.ell(370+math.cos(an)*dd*1.6,500+math.sin(an)*dd*0.6+30,g.uniform(4,12),g.uniform(3,8),8,FALSE2 if i%5==0 else None)
        hm.crater(370,520,40,14)
    th=sm((t-EV["thousands"]+0.2)/0.5)
    if th>0:
        for k in range(9): tardigrade(hm,62+k*52,500+(k%3)*30,0.22,0,0.0,0,FALSE1,(k%3-1)*0.4)
    buf=hm.render(0.02)+(_STARS*0.8)[...,None]*(hm.H<=0.3)[...,None]*(yy<470)[...,None]
    eh=M().circ(440,170,40); buf+=(cv2.GaussianBlur(eh.f(),(0,0),1.2)*0.55)[...,None]*np.array((0.5,0.75,1.0),np.float32)
    if pR>0:
        hm3=HM(); tardigrade(hm3,270,430,1.45,t-45.05,0.0,0.6,FALSE1)
        b3=hm3.render(0.03)+(_STARS*0.5)[...,None]*(hm3.H<=0.3)[...,None]; buf=buf*(1-pR)+b3*pR
    def hd(d,t=t):
        databar(d,"×1","1 m")
        ttl(d,"2019",540,1220,130,a=ap(t,EV["y2019"],EV["crashed"]),sc=pop(t,EV["y2019"]-0.1))
        tagm(d,"BERESHEET LANDER",540,1330,44,a=ap(t,EV["lander"],EV["crashed"]+0.5),col=cC)
        ttl(d,"CRASH",540,1220,150,a=ap(t,EV["crashed"],EV["thousands"]),sc=pop(t,EV["crashed"]-0.1),col=cO)
        ttl(d,"THOUSANDS OF TARDIGRADES",540,1220,84,a=ap(t,EV["thousands"],EV["survive"]),sc=pop(t,EV["thousands"]-0.1),col=cO)
        ttl(d,"SURVIVED?",540,1220,130,a=ap(t,EV["survive"],EV["without"]),sc=pop(t,EV["survive"]-0.1),col=cY)
        tagm(d,"NOBODY KNOWS",540,1330,48,a=ap(t,EV["nobody"],EV["without"]),col=cW)
        ttl(d,"NO WATER = NO WAKE-UP",540,1220,90,a=ap(t,EV["without"],EV["whyis"]-0.1),sc=pop(t,EV["without"]-0.1),col=cC)
    return buf,[hd]
SCN=dict(hook=s_hook,meet=s_meet,space=s_space,moon=s_moon)
BAND=(1-0.30*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.30*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
SCAN=(1+0.03*np.sin(yy*math.pi/1.5))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.018,(h,w,1)).astype(np.float32) for i in range(6)]
TR=0.34; TOTAL=B.TOTAL; LOOPD=0.6
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
def zoomblur(img,z,blur):
    Mx=cv2.getRotationMatrix2D((w/2,h/2.3),0,z); out=cv2.warpAffine(img,Mx,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    if blur>0.3: out=cv2.GaussianBlur(out,(0,0),blur)
    return out
def magchange(b1,b2,u):
    """microscope magnification jump: the old field zooms in and defocuses, the new one pulls into focus"""
    if u<0.5:
        k=u*2; return zoomblur(b1,1+1.6*k*k,9*k)*(1-0.6*k)+np.array((0.9,0.92,0.95),np.float32)*0.35*k*k
    k=(u-0.5)*2; return zoomblur(b2,0.6+0.4*sm(k),9*(1-k))*(0.4+0.6*k)+np.array((0.9,0.92,0.95),np.float32)*0.35*(1-k)**2
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(sc,SC[i+1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SC[i-1],sc,t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(sc,SC[0],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None:
        buf,hud=render_scene(t,sc); hk=1.0
    else:
        A_,B2,ta,tb,u=pair
        b1,h1=render_scene(ta,A_); b2,h2=render_scene(tb,B2)
        buf=magchange(b1,b2,u); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    buf=np.clip(buf,0,1.2)*VIG*BAND*SCAN+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
