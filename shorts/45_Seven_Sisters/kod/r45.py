import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid45")
for p in ["/home/claude/vid45","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
import drawkit as K
from drawkit import ink, outl, hatch, wash, glow, part, dl, circ_pts, dashl, rotp
from PIL import Image, ImageDraw
EV=ev.EV; Lx=ev.Lx
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= palette (stained glass: lead came + jewel glass, back-lit) =================
LEADC=(0.05,0.045,0.05); K.INK=LEADC
GOLD=(1.0,0.78,0.30); RUBY=(0.72,0.10,0.14); EMER=(0.10,0.52,0.32); SAPH=(0.12,0.24,0.66); AMET=(0.45,0.20,0.62)
ROSE=(0.86,0.42,0.52); TEAL=(0.10,0.55,0.60); AMBER=(0.90,0.55,0.16); PALE=(0.92,0.92,0.80); OCHRE=(0.70,0.30,0.12); WHITEG=(1.0,0.97,0.86)
SIS=[RUBY,EMER,AMBER,AMET,ROSE,TEAL,SAPH]
# ================= glass background (voronoi cells + lead) =================
_g=np.random.default_rng(7)
_seeds=[]
for gy_ in range(0,h+60,62):
    for gx_ in range(0,w+60,58): _seeds.append((gx_+_g.uniform(-24,24),gy_+_g.uniform(-26,26)))
_seeds=np.array(_seeds,np.float32); NS=len(_seeds)
_d=np.full((h,w),1e9,np.float32); LAB=np.zeros((h,w),np.int32)
for i,(sx,sy) in enumerate(_seeds):
    dd=(xx-sx)**2+(yy-sy)**2; m=dd<_d; _d[m]=dd[m]; LAB[m]=i
_e=(LAB!=np.roll(LAB,1,0))|(LAB!=np.roll(LAB,1,1))
LEAD=cv2.dilate(_e.astype(np.uint8),np.ones((3,3),np.uint8)).astype(np.float32)
LEAD=cv2.GaussianBlur(LEAD,(0,0),0.6)[...,None]
_rv=_g.uniform(-1,1,NS).astype(np.float32); _rv2=_g.uniform(-1,1,NS).astype(np.float32)
_tex=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),3); _tex/=_tex.std()
_str=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),sigmaX=1.0,sigmaY=14); _str/=_str.std()
GT=(1+0.05*_tex+0.035*_str)[...,None].astype(np.float32)
def glassbg(top,bot,var=0.22,split=None,lo=None):
    """per-cell tinted glass: colour lerps top->bot by cell centre y; optional lower band colour"""
    cy=np.clip(_seeds[:,1]/h,0,1)
    cols=np.array([lerpc(top,bot,c) for c in cy],np.float32)
    if split is not None: cols[_seeds[:,1]>split]=np.array(lo,np.float32)
    cols*=(1+var*_rv)[:,None]; cols+=0.04*_rv2[:,None]
    img=cols[LAB]
    img=img*(1-LEAD)+np.array(LEADC,np.float32)*LEAD
    return np.clip(img,0,1.2).astype(np.float32)
NIGHT=glassbg((0.05,0.08,0.26),(0.10,0.16,0.42))
GREEK=glassbg((0.10,0.20,0.48),(0.18,0.32,0.62))
AUS=glassbg((0.06,0.06,0.22),(0.16,0.12,0.36),split=600,lo=(0.62,0.24,0.10))
DEEP=glassbg((0.02,0.03,0.12),(0.05,0.08,0.24),var=0.3)
LIGHT=(1+0.22*np.exp(-(((xx-270)/300)**2+((yy-420)/420)**2)))[...,None].astype(np.float32)
# cell-wave transition order
_cd=np.hypot(_seeds[:,0]-270,_seeds[:,1]-430); _th=_cd/_cd.max()*0.8+_g.uniform(0,0.2,NS)
THP=_th[LAB].astype(np.float32)
# ================= drawing helpers =================
def pane(buf,m,col,a=1.0,lead=2):
    if a<=0 or m.x1<=m.x0: return
    comp(buf,m,col,sh=0,rim=0,a=a); outl(buf,m,a=a,th=lead,fill=0,col=LEADC)
def star_pts(cx,cy,r,n=8,ri=0.42,rot=0.0):
    return [(cx+(r if k%2==0 else r*ri)*math.cos(rot+k*math.pi/n),cy+(r if k%2==0 else r*ri)*math.sin(rot+k*math.pi/n)) for k in range(2*n)]
def gstar(buf,cx,cy,r,a=1.0,col=WHITEG,gl=1.0,t=0.0):
    if a<=0 or r<=0.5: return
    pane(buf,M().poly(star_pts(cx,cy,r,4,0.38,t*0.0)),col,a,1)
    glow(buf,cx,cy,r*1.3,(1.0,0.85,0.5),0.45*gl*a)
def figure(cx,cy,s=1.0,arm=0.0,lean=0.0,face=False):
    """robed figure (sister) mask parts: returns (gown, head, arms) masks"""
    g=M().poly(rotp([(cx-10*s,cy-80*s),(cx+10*s,cy-80*s),(cx+30*s,cy),(cx-30*s,cy)],lean,cx,cy))
    hd=M().circ(*rotp([(cx,cy-92*s)],lean,cx,cy)[0],11*s)
    am=M()
    for sd in (-1,1):
        p0=rotp([(cx+sd*8*s,cy-74*s)],lean,cx,cy)[0]
        if face:
            hx,hy=rotp([(cx-sd*3*s,cy-90*s)],lean,cx,cy)[0]; am.line(p0,(p0[0]+sd*14*s,p0[1]+10*s),6*s); am.line((p0[0]+sd*14*s,p0[1]+10*s),(hx,hy),5*s)
        else:
            an=math.pi/2-sd*(0.5+arm); am.line(p0,(p0[0]+math.cos(an)*34*s,p0[1]+math.sin(an)*34*s),6*s)
    return g,hd,am
def sister(buf,cx,cy,s,col,a=1.0,arm=0.0,lean=0.0,face=False):
    if a<=0: return
    g,hd,am=figure(cx,cy,s,arm,lean,face); pane(buf,g,col,a,2); pane(buf,hd,PALE,a,2); pane(buf,am,col,a,1)
def hunter(buf,cx,cy,s,a=1.0,t=0.0,stride=1.0):
    if a<=0: return
    ph=math.sin(t*7)*0.35*stride
    body=M().poly([(cx-16*s,cy-120*s),(cx+16*s,cy-120*s),(cx+22*s,cy-60*s),(cx-22*s,cy-60*s)])
    legs=M().line((cx-8*s,cy-60*s),(cx-8*s+math.sin(ph)*40*s,cy),9*s).line((cx+8*s,cy-60*s),(cx+8*s-math.sin(ph)*40*s,cy),9*s)
    arm=M().line((cx+14*s,cy-112*s),(cx+56*s,cy-150*s),8*s).line((cx-14*s,cy-112*s),(cx-50*s,cy-92*s),8*s)
    club=M().line((cx+56*s,cy-150*s),(cx+70*s,cy-200*s),12*s)
    pane(buf,legs,RUBY,a,1); pane(buf,body,RUBY,a,2); pane(buf,arm,RUBY,a,1); pane(buf,club,AMBER,a,2)
    pane(buf,M().circ(cx,cy-134*s,13*s),PALE,a,2)
    for k in (-1,0,1): gstar(buf,cx+k*9*s,cy-66*s,4*s,a,GOLD,0.6)
def arch_mask(x0,x1,y0,y1):
    cx=(x0+x1)/2; r=(x1-x0)/2
    return M().poly([(x0,y1),(x0,y0+r)]+circ_pts(cx,y0+r,r,r,math.pi,2*math.pi,40)+[(x1,y0+r),(x1,y1)])
_GCH={}
def gbanner(d,s,x,y,fs=64,a=1.0,sc=1.0,kind="gold"):
    if a<=0.01 or sc<=0.02: return
    k=(s,fs,kind)
    if k not in _GCH:
        f=B.CZ(fs,800); d0=ImageDraw.Draw(Image.new("RGBA",(4,4))); bb=d0.textbbox((0,0),s,font=f)
        tw,th=bb[2]-bb[0],bb[3]-bb[1]; px,py=int(fs*0.55),int(fs*0.34); m=16
        im=Image.new("RGBA",(tw+2*px+2*m,th+2*py+2*m),(0,0,0,0)); dd=ImageDraw.Draw(im)
        fill={"gold":(232,176,70),"ruby":(168,28,40),"pale":(236,232,206),"blue":(36,64,150)}[kind]
        fg=(24,18,28) if kind in ("gold","pale") else (250,238,210)
        dd.rounded_rectangle((m,m,m+tw+2*px,m+th+2*py),radius=int(fs*0.3),fill=fill+(255,),outline=(14,12,16,255),width=max(6,fs//9))
        dd.line((m+fs*0.2,m+th+2*py-fs*0.25,m+tw+2*px-fs*0.2,m+th+2*py-fs*0.25),fill=tuple(int(c*0.82) for c in fill)+(255,),width=3)
        dd.text((m+px-bb[0],m+py-bb[1]),s,font=f,fill=fg+(255,))
        _GCH[k]=im
    im=_GCH[k]
    if abs(sc-1)>0.01: q=max(0.05,round(sc*20)/20); im=im.resize((max(1,int(im.width*q)),max(1,int(im.height*q))),Image.BILINEAR)
    if a<0.99: ar=np.array(im); ar[...,3]=(ar[...,3]*a).astype(np.uint8); im=Image.fromarray(ar)
    paste(d,im,x-im.width/2,y-im.height/2)
_CZC={}
def _cz(n):
    if n not in _CZC: _CZC[n]=B.CZ(n,800)
    return _CZC[n]
def gtitle(d,s,x,y,fs=120,a=1.0,sc=1.0,col=(255,226,150)):
    if a<=0.01 or fs*sc<8: return
    f=_cz(int(fs*sc)); B.txt(d,(x,y),s,f,col+(int(255*a),),anchor="mm",stroke=5)
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= scenes =================
CL7=[(-60,-40),(-20,-62),(22,-46),(58,-58),(-40,4),(10,-8),(48,12)]
def cluster(buf,cx,cy,s,t,miss=-1,mk=0.0,a=1.0,pulse=0.0):
    for k,(x,y) in enumerate(CL7):
        r=(9+3*((k*5)%3))*s*(1+0.25*pulse*math.sin(t*8+k))
        aa=a*(1-mk if k==miss else 1)
        gstar(buf,cx+x*s,cy+y*s,r,aa,WHITEG,1.0)
def s_hook(t,sc):
    buf=NIGHT.copy(); hud=[]
    tt=max(t,-1.0)
    for j,(x0,x1,col,fig) in enumerate(((40,250,GREEK,0),(290,500,AUS,1))):
        am=arch_mask(x0,x1,160,640)
        A=am.f()[...,None]; buf[:]=buf*(1-A)+col*A
        outl(buf,am,a=1,th=3,fill=0)
        cx=(x0+x1)/2
        pulse=sm((t-EV["seven"]+0.1)/0.3)*(1-sm((t-EV["hunter"])/0.4))
        mk=sm((t-EV["missing"]+0.1)/0.4)
        cluster(buf,cx,300,0.95,tt,miss=6 if j==0 else 4,mk=mk,pulse=pulse)
        hx=cx-60+((tt*30+j*20)%120)
        hunter(buf,hx,600,0.62,1.0,tt+j)
        for k in range(3): sister(buf,cx+10+k*26,600,0.38,SIS[k+j*2],1.0,arm=0.2,lean=-0.1)
    if t>EV["never"]-0.3:
        u=sm((t-EV["never"]+0.3)/0.5); m=M()
        dashl(m,(250-20,420),(250-20+60*u,420),6,5,2.5); ink(buf,m,1.0,col=GOLD)
    def hd(d,t=t):
        k0=1.0 if t<0.4 else ap(t,-1,EV["seven"])
        gbanner(d,"THE SAME STORY",540,190,70,a=k0,sc=1.0 if t<EV["same"] else 1+0.06*math.exp(-(t-EV["same"])*5))
        gbanner(d,"GREECE",290,1330,44,a=1.0,kind="pale"); gbanner(d,"AUSTRALIA",790,1330,44,a=1.0,kind="ruby")
        gbanner(d,"7 SISTERS",540,190,76,a=ap(t,EV["seven"],EV["missing"]),sc=pop(t,EV["seven"]-0.1))
        gbanner(d,"1 IS MISSING",540,190,76,a=ap(t,EV["missing"],EV["how"]),sc=pop(t,EV["missing"]-0.1),kind="ruby")
        gbanner(d,"THEY NEVER MET",540,190,70,a=ap(t,EV["how"],sc["e"]+1),sc=pop(t,EV["how"]-0.1),kind="blue")
        gtitle(d,"?",540,840,190,a=ap(t,EV["samestar"]-0.1,sc["e"]+1),sc=pop(t,EV["samestar"]-0.15))
    hud.append(hd); return buf,hud
def s_greece(t,sc):
    buf=GREEK.copy(); hud=[]
    pO=sm((t-EV["orion"]+0.3)/0.35); pM=sm((t-EV["merope"]+0.3)/0.35)
    aA=1-pO; aO=pO*(1-pM); aM=pM
    gy=640; ink(buf,M().rect(0,gy,w,h),1.0,col=(0.14,0.20,0.36)); outl(buf,M().rect(-5,gy,w+5,h+5),a=1,th=2,fill=0)
    if aA>0:
        # Atlas holding the sky, daughters around him
        u=sm((t-sc["s"]-0.1)/0.7)
        globe=M().circ(270,300,95); pane(buf,globe,SAPH,aA*max(u,0.25),3)
        for k in range(5): ink(buf,M().pline(circ_pts(270,300,95,95*(0.25+0.18*k),0,2*math.pi,60),1.5),aA*max(u,0.25))
        for k in range(7): gstar(buf,270+math.cos(k*0.9+t*0.3)*60,300+math.sin(k*0.9+t*0.3)*60,6,aA*max(u,0.25),GOLD,0.5)
        body=M().poly([(240,400),(300,400),(320,520),(220,520)]); legs=M().line((240,515),(210,600),16).line((300,515),(330,560),16).line((330,560),(320,600),14)
        arms=M().line((245,410),(195,330),12).line((295,410),(345,330),12)
        pane(buf,legs,AMET,aA*u,1); pane(buf,body,AMET,aA*u,2); pane(buf,arms,AMET,aA*u,1); pane(buf,M().circ(270,385,18),PALE,aA*u,2)
        for k in range(7):
            e=EV["daughters"]+k*0.08; ak=aA*sm((t-e+0.2)/0.3)
            x=60+k*70 if k<3 else 60+(k+1)*70-20
            if k>=3: x=330+(k-3)*55+25
            if k<3: x=70+k*55
            sister(buf,x,620,0.62,SIS[k],ak,arm=0.15,lean=0.05*math.sin(t+k))
    if aO>0:
        fl=sm((t-EV["gods"]+0.1)/0.9)
        hx=40+((t-EV["orion"])*55)
        hunter(buf,hx,620,1.0,aO,t,1.0)
        for k in range(7):
            x0=230+k*42; y0=620-(k%2)*8
            y=y0-fl*(300+40*math.sin(k*1.7))-0; x=x0+fl*(-40+12*k)
            if fl<0.7: sister(buf,x+(t-EV["orion"])*30*(1-fl),y,0.55*(1-fl*0.9),SIS[k],aO*(1-sm((fl-0.5)/0.3)),arm=0.4,lean=-0.25)
            if fl>0.3: gstar(buf,x+(t-EV["orion"])*30*(1-fl),y-40,12*sm((fl-0.3)/0.5),aO,WHITEG,1.0)
    if aM>0:
        for k,(x,y) in enumerate(CL7):
            r=12; dimk=sm((t-EV["faint"]+0.2)/0.6) if k==6 else 0
            gstar(buf,270+x*2.4,230+y*2.4,r*(1-0.5*dimk),aM*(1-0.65*dimk),WHITEG,1-0.8*dimk)
        sister(buf,250,600,1.4,SIS[6],aM,face=t>EV["hid"]-0.1)
        if t>EV["mortal"]-0.2:
            mm=sm((t-EV["mortal"]+0.2)/0.4)*(1-sm((t-EV["faint"])/0.4))
            pane(buf,M().poly([(392,470),(428,470),(446,600),(374,600)]),(0.55,0.45,0.36),aM*mm,2); pane(buf,M().circ(410,452,16),PALE,aM*mm,2)
            hm=M().circ(332,430,11).circ(348,430,11).poly([(322,435),(358,435),(340,456)]); pane(buf,hm,RUBY,aM*mm,1)
    def hd(d,t=t,aA=aA,aO=aO,aM=aM):
        gbanner(d,"THE PLEIADES",540,190,76,a=ap(t,EV["pleiades"],EV["atlas"]),sc=pop(t,EV["pleiades"]-0.1))
        gbanner(d,"DAUGHTERS OF ATLAS",540,190,60,a=ap(t,EV["atlas"]-0.3,EV["orion"]),sc=pop(t,EV["atlas"]-0.4),kind="pale")
        gbanner(d,"ORION · THE HUNTER",540,190,62,a=ap(t,EV["orion"],EV["gods"]),sc=pop(t,EV["orion"]-0.1),kind="ruby")
        gbanner(d,"MADE INTO STARS",540,190,66,a=ap(t,EV["gods"],EV["merope"]),sc=pop(t,EV["gods"]-0.1))
        gbanner(d,"MEROPE",540,190,80,a=ap(t,EV["merope"],sc["e"]+1),sc=pop(t,EV["merope"]-0.1),kind="ruby")
        gbanner(d,"MARRIED A MORTAL",540,1200,52,a=ap(t,EV["mortal"],EV["faint"]),kind="pale")
        gbanner(d,"THE FAINT STAR",540,1200,60,a=ap(t,EV["faint"],sc["e"]+1),sc=pop(t,EV["faint"]-0.1))
    hud.append(hd); return buf,hud
ORI=[(140,250),(250,240),(170,330),(195,335),(220,340),(150,450),(255,440),(105,150)]  # Betelgeuse,Bellatrix,belt x3,Saiph,Rigel,head(Meissa) (rough)
def s_aus(t,sc):
    buf=AUS.copy(); hud=[]
    pB=sm((t-EV["again"]+0.3)/0.35)
    u=sm((t-EV["orion2"]+0.3)/0.8)
    off=(t-sc["s"])*6
    ox,oy=-10+off,40
    # man figure through Orion stars
    pts=[(x+ox,y+oy) for x,y in ORI]
    m=M()
    for a_,b_ in ((7,0),(7,1),(0,2),(1,4),(2,3),(3,4),(2,5),(4,6)): dl(m,[pts[a_],pts[b_]],u,2.2)
    ink(buf,m,0.8,col=(0.9,0.7,0.45))
    for k,(x,y) in enumerate(pts): gstar(buf,x,y,10 if k in (0,6) else 7,1.0,WHITEG if k!=0 else (1.0,0.6,0.4),1.0)
    if u>0.5:
        sp=M().line(pts[1],(pts[1][0]+110,pts[1][1]-90),3); ink(buf,dl(M(),[pts[1],(pts[1][0]+110,pts[1][1]-90)],sm((u-0.5)*2),3),1.0,col=AMBER)
    # sisters running ahead (upper right)
    cx,cy=360+off*0.5,215
    hid=sm((t-EV["hiding"]+0.2)/0.5)
    for k,(x,y) in enumerate(CL7):
        gstar(buf,cx+x*1.3,cy+y*1.3,9,sm((t-EV["chasing"]+0.3-k*0.06)/0.3)*(1-hid*(k==3)),WHITEG,1.0)
    if hid>0:
        cl_=M().ell(cx+(CL7[3][0])*1.3+8,cy+CL7[3][1]*1.3,30*hid,18*hid); pane(buf,cl_,(0.10,0.08,0.22),hid,2)
    # land band: campfire + figures sitting
    fx,fy=270,665
    if True:
        fl=M().poly([(fx-14,fy),(fx,fy-34-6*math.sin(t*11)),(fx+14,fy)]); pane(buf,fl,AMBER,1.0,1); glow(buf,fx,fy-14,26,(1,0.6,0.2),0.5)
        for sd in (-1,1):
            sm_=M().circ(fx+sd*70,fy-46,10).poly([(fx+sd*70-14,fy-34),(fx+sd*70+14,fy-34),(fx+sd*70+22,fy),(fx+sd*70-22,fy)])
            pane(buf,sm_,(0.25,0.10,0.06),1.0,2)
    def hd(d,t=t,pB=pB,hid=hid):
        gbanner(d,"AUSTRALIA",540,190,76,a=ap(t,EV["aus"],EV["orion2"]),sc=pop(t,EV["aus"]-0.1),kind="ruby")
        gbanner(d,"ORION = A HUNTER",540,190,62,a=ap(t,EV["orion2"],EV["again"]),sc=pop(t,EV["orion2"]-0.1))
        gbanner(d,"7 SISTERS",760,620,46,a=ap(t,EV["chasing"],EV["again"]),kind="pale")
        gbanner(d,"ONE IS HIDING",540,190,66,a=ap(t,EV["hiding"],sc["e"]+1),sc=pop(t,EV["hiding"]-0.1),kind="ruby")
        gtitle(d,"6",540,1180,170,a=ap(t,EV["six"],sc["e"]+1),sc=pop(t,EV["six"]-0.1))
    hud.append(hd); return buf,hud
# Pleiades (deg offsets from Alcyone; x east->left)
PL=dict(Alcyone=(0,0,2.9),Atlas=(-0.380,0.05,3.6),Pleione=(-0.388,-0.033,5.1),Electra=(0.597,0.0,3.7),Maia=(0.380,-0.267,3.9),
        Merope=(0.266,0.15,4.2),Taygeta=(0.521,-0.367,4.3),Celaeno=(0.612,-0.183,5.4))
def s_sky(t,sc):
    buf=DEEP.copy(); hud=[]
    g=np.random.default_rng(11)
    sm_=M()
    for k in range(70): sm_.circ(g.uniform(20,520),g.uniform(60,700),g.uniform(0.6,1.4))
    ink(buf,sm_,0.7,col=(0.85,0.85,1.0))
    sep=sm((t-EV["apart"]+0.6)/1.4)
    rew=sm((t-EV["backward"]+0.2)/0.6)
    cx,cy,S=330,380,320
    for name,(x,y,mag) in PL.items():
        if name=="Celaeno": continue
        X,Y=cx-x*S,cy+y*S
        if name=="Pleione": X,Y=X-30*sep,Y-48*sep
        r=max(3,15-2.7*(mag-2.9))
        a=1.0
        if name=="Pleione": a=0.25+0.75*sep
        gstar(buf,X,Y,r*(1 if name!="Pleione" else (0.6+0.6*sep)),a,WHITEG,1.0)
    if rew>0 and t<EV["hypo"]:
        # rewind dial
        dx,dy,R=120,560,62; dm=M().circ(dx,dy,R); pane(buf,dm,(0.16,0.14,0.30),rew,3)
        for k in range(12): ink(buf,M().line((dx+math.cos(k*0.52)*R*0.78,dy+math.sin(k*0.52)*R*0.78),(dx+math.cos(k*0.52)*R*0.92,dy+math.sin(k*0.52)*R*0.92),2),rew,col=GOLD)
        an=-(t-EV["backward"])*7 if t<EV["apart"]+0.8 else -(EV["apart"]+0.8-EV["backward"])*7
        ink(buf,M().line((dx,dy),(dx+math.cos(an)*R*0.7,dy+math.sin(an)*R*0.7),4),rew,col=GOLD)
    hy=sm((t-EV["hypo"]+0.2)/0.5)
    if hy>0:
        # the two "storytellers' arches" return faintly
        for x0,x1 in ((40,250),(290,500)): outl(buf,arch_mask(x0,x1,160,640),a=0.5*hy,th=2,fill=0.0,col=GOLD)
    def hd(d,t=t,sep=sep,rew=rew):
        gbanner(d,"LOOK UP TONIGHT",540,190,64,a=ap(t,EV["look"],EV["see6"]),sc=pop(t,EV["look"]-0.1),kind="blue")
        gtitle(d,"6",540,1180,170,a=ap(t,EV["see6"],EV["y2021"]),sc=pop(t,EV["see6"]-0.1))
        gbanner(d,"2021 · ASTRONOMERS",540,190,58,a=ap(t,EV["y2021"],EV["hundred"]),sc=pop(t,EV["y2021"]-0.1),kind="pale")
        gbanner(d,"REWIND TIME",540,1200,56,a=ap(t,EV["backward"],EV["hundred"]))
        n=int(eout(cl((t-EV["hundred"]+0.3)/1.2))*100000)
        gtitle(d,f"−{n:,} YEARS",540,195,92,a=ap(t,EV["hundred"],EV["hypo"]),col=(255,226,150))
        lab_a=ap(t,EV["atlas2"],EV["hypo"])
        if lab_a>0:
            ax,ay=(330+0.380*320)*2,(380+0.05*320)*2; px_,py_=ax-60*sep,ay-96*sep-0
            B.txt(d,(ax+70,ay+60),"ATLAS",B.CZ(40,700),(255,226,150,int(255*lab_a)),anchor="mm",stroke=3)
            B.txt(d,(px_-40,py_-60),"PLEIONE",B.CZ(40,700),(255,226,150,int(255*lab_a)),anchor="mm",stroke=3)
        gtitle(d,"7",540,1180,170,a=ap(t,EV["seven2"]-0.1,EV["hypo"]),sc=pop(t,EV["seven2"]-0.15))
        gbanner(d,"A HYPOTHESIS",540,190,64,a=ap(t,EV["hypo"],EV["oldest"]),sc=pop(t,EV["hypo"]-0.1),kind="ruby")
        gbanner(d,"THE OLDEST STORY?",540,190,64,a=ap(t,EV["oldest"],sc["e"]+1),sc=pop(t,EV["oldest"]-0.1))
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,greece=s_greece,aus=s_aus,sky=s_sky)
BAND=(1-0.45*np.exp(-((yy-728)/80)**2))[...,None].astype(np.float32)
VIG=(1-0.30*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.008,(h,w,1)).astype(np.float32) for i in range(6)]
TR=0.32; TOTAL=B.TOTAL; LOOPD=0.6
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
def panes(b1,b2,u):
    sw=(THP<u)[...,None]; out=np.where(sw,b2,b1)
    fl=np.clip(1-(u-THP)/0.12,0,1)*(THP<u); out=out+(fl*0.55)[...,None]*np.array(WHITEG,np.float32)
    return out
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
        buf=panes(b1,b2,u*1.12); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    flick=1+0.025*math.sin(t*1.7)+0.015*math.sin(t*4.3)
    buf=np.clip(buf*GT*LIGHT*flick,0,1.3)*VIG*BAND+GR[int(t*30)%6]
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
