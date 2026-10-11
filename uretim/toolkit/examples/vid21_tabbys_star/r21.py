import numpy as np, cv2, math, sys
for p in ["/home/claude/vid21","/home/claude/vid3","/home/claude/ep1"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
from PIL import Image, ImageDraw
w,h,W,H=B.w,B.h,B.W,B.H; yy,xx=B.yy.astype(np.float32),B.xx.astype(np.float32)
cl,sm,ein,eout,fa,txt=B.cl,B.sm,B.ein,B.eout,B.fa,B.txt
fMono,fMonoS,fBig,CZ=B.fMono,B.fMonoS,B.fBig,B.CZ
LOGO=E1.LOGO; band=E1.band; EV=ev.EV; Lx=ev.Lx; SS=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
AMB=(255,205,120); CYAN=(120,225,255); RED=(255,95,80); GRN=(130,255,170)
def _paste(d,p,x0,y0):
    x0,y0=int(x0),int(y0); sx,sy=max(0,-x0),max(0,-y0)
    if x0>=W or y0>=H or x0+p.width<=0 or y0+p.height<=0: return
    d._image.alpha_composite(p,(max(0,x0),max(0,y0)),(sx,sy))
def dot(d,x,y,r,col,a=1.0):
    if a<=0.01: return
    r=max(1,int(r)); p=Image.new("RGBA",(2*r+4,2*r+4),(0,0,0,0)); ImageDraw.Draw(p).ellipse([2,2,2*r+2,2*r+2],fill=tuple(col)+(int(255*min(1,a)),)); _paste(d,p,x-r-2,y-r-2)
def lab(d,s,y,a,col=(255,255,255),f=None,x=None):
    if a>0.01: txt(d,(x or W//2,y),s,f or CZ(54,800),tuple(col)+(int(255*min(1,a)),),anchor="mm",stroke=3)
def glowb(buf,x,y,r,col,a):
    d2=((xx-x)**2+(yy-y)**2)/(r*r); buf+=(np.exp(-d2)*a)[...,None]*np.array(col,np.float32)
def bgspace(buf,t,g=0.6):
    buf[:]=np.array([0.004,0.008,0.02],np.float32)*(0.7+0.6*(yy/h))[...,None]; B.stars(buf,gain=g,rot=t*0.002,maxy=h)
def star(buf,cx,cy,r,b,warm=1.0):
    d2=(xx-cx)**2+(yy-cy)**2; limb=np.sqrt(np.clip(1-d2/(r*r),0,1)); disc=(d2<r*r).astype(np.float32)
    buf+=(disc*(0.55+0.6*limb))[...,None]*np.array([1.0,0.93,0.76],np.float32)*b*1.4
    buf+=(np.exp(-d2/(r*2.4)**2)*0.55*b)[...,None]*np.array([1.0,0.8,0.5],np.float32)+(np.exp(-d2/(r*6.0)**2)*0.16*b)[...,None]*np.array([1.0,0.7,0.4],np.float32)
def lcurve(buf,vals,x0,y0,wd,ht,col,upto=1.0,thick=2,panel=True,lvl=None):
    if panel: cv2.rectangle(buf,(x0-6,y0-8),(x0+wd+6,y0+ht+8),(0.012,0.022,0.04),-1); cv2.rectangle(buf,(x0-6,y0-8),(x0+wd+6,y0+ht+8),(0.09,0.13,0.2),1)
    yb=int(y0+0.04/0.34*ht)
    for x in range(x0,x0+wd,9): buf[yb,x:x+4]=0.22
    if lvl is not None:
        yl=int(y0+(1.04-lvl)/0.34*ht)
        for x in range(x0,x0+wd,7): buf[yl:yl+1,x:x+3]=np.array([0.9,0.3,0.25],np.float32)*0.8
    M=len(vals); n=max(2,int(M*upto)); xs=x0+np.arange(n)*wd/(M-1); ys=y0+(1.04-np.array(vals[:n]))/0.34*ht
    pts=np.stack([xs,np.clip(ys,y0,y0+ht)],1).astype(np.int32)
    cv2.polylines(buf,[pts],False,tuple(c*0.28 for c in col),thick*3,cv2.LINE_AA); cv2.polylines(buf,[pts],False,tuple(col),thick,cv2.LINE_AA)
    if n<M: glowb(buf,pts[-1][0],pts[-1][1],14,col,0.8)
def noise(n,amp,seed): return np.random.default_rng(seed).normal(0,amp,n)
HOOKEND=EV["giant"]+2.6; HV=[ev.hook_b(HOOKEND*i/319)+noise(1,0.0015,i)[0] for i in range(320)]
def _kep():
    x=np.linspace(0,1,420); v=1+noise(420,0.0025,9)
    for c,dp,wd in [(0.10,0.035,0.012),(0.22,0.08,0.02),(0.27,0.03,0.008),(0.41,0.15,0.018),(0.47,0.05,0.01),(0.60,0.22,0.02),(0.66,0.06,0.01),(0.82,0.11,0.03),(0.91,0.04,0.012)]: v-=dp*np.exp(-((x-c)/wd)**2)
    return list(v-0.0002*np.arange(420)/420*0)
KEP=_kep()
rng=np.random.default_rng(3); FIELD=rng.uniform(0,1,(2600,2)); FIELDB=rng.uniform(0.25,1.0,2600)**2
MINI=[1+noise(36,0.012,k) for k in range(30)]; SPEC=(2,2)
_v=1+noise(36,0.006,77)
for c,dp,wd in [(6,0.10,1.5),(14,0.22,2.0),(22,0.06,1.2),(30,0.15,1.8)]: _v=_v-dp*np.exp(-((np.arange(36)-c)/wd)**2)
MINI[SPEC[0]*6+SPEC[1]]=_v
DP=[(rng.uniform(0,6.283),rng.uniform(70,190),rng.uniform(0.15,0.5)) for _ in range(260)]
BLUE=[1+noise(200,0.002,4)[i]-(0.05*math.exp(-((i-60)/16)**2)+0.11*math.exp(-((i-120)/22)**2)+0.03*math.exp(-((i-165)/9)**2))*1.9 for i in range(200)]
RED_=[1+noise(200,0.002,5)[i]-(0.05*math.exp(-((i-60)/16)**2)+0.11*math.exp(-((i-120)/22)**2)+0.03*math.exp(-((i-165)/9)**2))*0.95 for i in range(200)]
CYG={"deneb":(270,150),"sadr":(270,300),"albireo":(270,470),"gienah":(165,265),"delta":(385,235)}; TGT=(330,380)
def scene(t,sc):
    n=sc["name"]; lt=t-sc["s"]; buf=np.zeros((h,w,3),np.float32); hud=[]
    if n=="hook":
        bgspace(buf,t,0.5); a=eout((t-0.1)/0.7); b=ev.hook_b(t)*a; star(buf,270,235,44,b)
        p=t-EV["planet"]
        if 0<p<3.2: px=180+180*(p/3.2); cv2.circle(buf,(int(px),235),7,(0.0,0.0,0.0) if abs(px-270)<44 else (0.01,0.012,0.02),-1,cv2.LINE_AA)
        lcurve(buf,HV,40,430,460,170,(0.55,0.92,1.0),upto=cl(t/HOOKEND),lvl=0.78 if t>EV["dropped"]-0.3 else None)
        def hd(d,t=t):
            lab(d,"THE STAR THAT KEEPS DIMMING",300,sm((t-0.5)/0.4)*(1-sm((t-EV["dropped"]+0.3)/0.3)),AMB,CZ(52,800))
            a=sm((t-EV["pct"]+0.1)/0.25)*(1-sm((t-EV["planet"]+0.2)/0.3)); lab(d,"-22%",330,a,RED,B.F("BigShoulders-Bold",190)); lab(d,"IN A MATTER OF DAYS",440,sm((t-EV["days"])/0.3)*(1-sm((t-EV["planet"]+0.2)/0.3)),(230,235,245),CZ(40,700))
            lab(d,"A PLANET: ~1%",330,sm((t-EV["planet"])/0.3),CYAN,CZ(60,800)); lab(d,"NOT EVEN A GIANT",440,sm((t-EV["giant"])/0.3),(230,235,245),CZ(40,700))
        hud.append(hd)
    elif n=="kepler":
        bgspace(buf,t,0.35); ph=t>EV["passes"]-0.4
        if not ph:
            fr=cl((t-EV["four"])/(EV["stars150"]-EV["four"]+0.8)); m=int(len(FIELD)*fr)
            for (fx,fy),fb in zip(FIELD[:m],FIELDB[:m]):
                x,y=int(50+fx*440),int(300+fy*330); buf[y,x]+=fb*0.9*(0.7+0.3*math.sin(t*3+fx*40))
            cv2.rectangle(buf,(45,295),(495,635),(0.25,0.5,0.6),1)
        else:
            a=sm((t-EV["passes"]+0.4)/0.6); star(buf,270,270,64,a); pp=cl((t-EV["passes"])/(EV["jupiter"]-EV["passes"]+0.8)); px=90+360*pp
            cv2.circle(buf,(int(px),270),6,(0.0,0.0,0.0),-1,cv2.LINE_AA)
            vals=[1-0.01*math.exp(-((i/319-pp*0+0.0-(i/319))**2)) for i in range(2)]
            V=[1+noise(1,0.001,i)[0]-(0.01 if abs((90+360*(i/319))-px)<64 and (90+360*(i/319))<=px+2 else 0)*(1 if (90+360*(i/319))<=px else 0) for i in range(320)]
            lcurve(buf,V,40,440,460,170,(0.55,0.92,1.0),upto=pp,lvl=0.78)
        def hd(d,t=t,ph=ph):
            s0=SS("kepler")["s"]
            if not ph:
                a=sm((t-s0)/0.5)*(1-sm((t-EV["passes"]+0.6)/0.3)); d.polygon([(340,560),(740,560),(700,760),(380,760)],fill=(70,80,100,int(170*a)))
                d.polygon([(380,480),(700,480),(740,560),(340,560)],fill=(110,125,150,int(200*a))); d.rectangle([180,590,340,660],fill=(50,90,150,int(200*a))); d.rectangle([740,590,900,660],fill=(50,90,150,int(200*a)))
                lab(d,"KEPLER SPACE TELESCOPE",300,sm((t-EV["kepler"]+0.1)/0.3)*(1-sm((t-EV["stars150"]+0.4)/0.3)),(230,235,245),CZ(48,800)); lab(d,"2009 – 2013",380,sm((t-EV["four"])/0.3)*(1-sm((t-EV["stars150"]+0.4)/0.3)),AMB,CZ(44,700))
                lab(d,"150,000 STARS",1300,sm((t-EV["stars150"])/0.3),CYAN,B.F("BigShoulders-Bold",120)); lab(d,"TINY DIPS OF LIGHT",1180,sm((t-EV["dips"])/0.3),(230,235,245),CZ(44,800))
            else:
                lab(d,"A PLANET TRANSIT",300,sm((t-EV["passes"])/0.3)*(1-sm((t-EV["jupiter"]+0.2)/0.3)),(230,235,245),CZ(54,800)); lab(d,"JUPITER: ABOUT 1%",300,sm((t-EV["jupiter"])/0.3),CYAN,CZ(58,800))
        hud.append(hd)
    elif n=="volunteers":
        bgspace(buf,t,0.2)
        for i in range(30):
            r_,c_=divmod(i,6); x0,y0=32+c_*81,150+r_*64; a=cl((t-SS("volunteers")["s"]-i*0.05)/0.4)
            if a>0: cv2.rectangle(buf,(x0,y0),(x0+72,y0+52),(0.02,0.04,0.07),-1); cv2.rectangle(buf,(x0,y0),(x0+72,y0+52),(0.1,0.16,0.24),1); vv=MINI[i]; xs=x0+np.arange(36)*72/35; ys=y0+26-(np.array(vv)-1)*160
            if a>0: cv2.polylines(buf,[np.stack([xs,np.clip(ys,y0+2,y0+50)],1).astype(np.int32)],False,(0.5*a,0.85*a,1.0*a) if i!=SPEC[0]*6+SPEC[1] or t<EV["flagged"] else (1.0,0.35,0.3),1,cv2.LINE_AA)
        fl=sm((t-EV["flagged"])/0.3)
        if fl>0:
            x0,y0=32+SPEC[1]*81,150+SPEC[0]*64; cv2.rectangle(buf,(x0-4,y0-4),(x0+76,y0+56),(1.0,0.3,0.25),2); glowb(buf,x0+36,y0+26,60+20*math.sin(t*9),(1.0,0.2,0.15),0.25*fl)
        def hd(d,t=t):
            lab(d,"PLANET HUNTERS",300,sm((t-EV["ph"]+0.2)/0.3),CYAN,CZ(58,800)); lab(d,"VOLUNTEERS",300,sm((t-EV["volunteers"])/0.3)*(1-sm((t-EV["ph"]+0.4)/0.3)),(230,235,245),CZ(58,800))
            for k in range(10):
                x=140+k*90; a=sm((t-EV["volunteers"]-k*0.1)/0.4); dot(d,x,1050,18,(150,190,230),a*0.9); d.polygon([(x-28,1130),(x+28,1130),(x+20,1078),(x-20,1078)],fill=(150,190,230,int(230*a))) if a>0.02 else None
            lab(d,"FLAGGED",1210,sm((t-EV["flagged"])/0.25),RED,B.F("BigShoulders-Bold",110))
        hud.append(hd)
    elif n=="star":
        bgspace(buf,t,0.3)
        for a_,b_ in [("deneb","sadr"),("sadr","albireo"),("gienah","sadr"),("sadr","delta")]:
            cv2.line(buf,CYG[a_],CYG[b_],(0.18,0.3,0.42),1,cv2.LINE_AA)
        for k,(x,y) in CYG.items(): glowb(buf,x,y,7,(0.8,0.9,1.0),1.4)
        cs=sm((t-EV["cyg"]+0.3)/0.4)
        tp=sm((t-EV["kic"]+0.2)/0.3); glowb(buf,TGT[0],TGT[1],9,(1.0,0.85,0.5),1.8*tp+0.2)
        lp_=cl((t-EV["ly"])/2.0)
        if lp_>0: cv2.line(buf,(270,640),(int(270+(TGT[0]-270)*lp_),int(640+(TGT[1]-640)*lp_)),(0.6,0.8,1.0),1,cv2.LINE_AA); glowb(buf,270,640,6,(0.3,0.6,1.0),1.5)
        if t>EV["nopat"]-0.4:
            a=sm((t-EV["nopat"]+0.4)/0.4); lcurve(buf,KEP,40,470,460,150,(0.55,0.92,1.0),upto=cl((t-EV["nopat"])/(SS("star")["e"]-EV["nopat"]-1.0)))
        def hd(d,t=t):
            B.reticle(d,TGT[0]*2,TGT[1]*2,tp,col=(255,210,130),sz=70) if tp>0.02 else None
            lab(d,"KIC 8462852",300,sm((t-EV["kic"])/0.3)*(1-sm((t-EV["tabby"]+0.2)/0.3)),AMB,CZ(64,800)); lab(d,"TABBY'S STAR",300,sm((t-EV["tabby"])/0.3)*(1-sm((t-EV["wtf"]+0.2)/0.3)),AMB,CZ(64,800))
            lab(d,"THE WTF STAR",300,sm((t-EV["wtf"])/0.3)*(1-sm((t-EV["flux"]+0.2)/0.3)),RED,CZ(64,800)); lab(d,"WHERE'S THE FLUX?",300,sm((t-EV["flux"])/0.3)*(1-sm((t-EV["ly"]+0.3)/0.3)),(230,235,245),CZ(52,800))
            lab(d,"TABETHA BOYAJIAN",380,sm((t-EV["boy"])/0.3)*(1-sm((t-EV["wtf"]+0.2)/0.3)),(200,215,235),CZ(38,700))
            lab(d,"1,470 LIGHT-YEARS",300,sm((t-EV["ly"])/0.3)*(1-sm((t-EV["nopat"]+0.4)/0.3)),CYAN,CZ(56,800)); lab(d,"CYGNUS",1000,cs*0.0+sm((t-EV["cyg"])/0.3)*(1-sm((t-EV["nopat"]+0.4)/0.3)),(200,215,235),CZ(44,800),x=180)
            lab(d,"NO PATTERN",300,sm((t-EV["nopat"])/0.3),RED,CZ(62,800)); lab(d,"DAYS · WEEKS",380,sm((t-EV["daysb"])/0.3),(230,235,245),CZ(42,700))
        hud.append(hd)
    elif n=="theories":
        bgspace(buf,t,0.3); star(buf,270,240,44,1.0-0.04*math.sin(t*4))
        def hd(d,t=t):
            for k,(nm,e,x) in enumerate([("COMETS?",EV["comets"],200),("SHATTERED PLANET?",EV["torn"],540),("DUST?",EV["dust"],880)]):
                a=sm((t-e)/0.35)
                if k==0:
                    for j in range(7): dot(d,x-60+j*20,930+j*12,7-j*0.6,(190,220,255),a); d.line([(x-60+j*20,930+j*12),(x+80+j*20,880+j*8)],fill=(150,190,240,int(90*a)),width=3)
                elif k==1:
                    for j in range(9): an=j*0.7; dot(d,x+math.cos(an)*(18+j*7),930+math.sin(an)*(18+j*6),12-j*0.8,(190,120,90),a)
                else:
                    for j in range(40): an=j*2.4; rr=(j*3.3)%90; dot(d,x+math.cos(an)*rr,930+math.sin(an)*rr*0.7,4,(200,170,130),a*0.85)
                lab(d,nm,1090,a,(240,235,225),CZ(38,800),x=x)
        hud.append(hd)
    elif n=="aliens":
        bgspace(buf,t,0.3); star(buf,270,300,46,1.0-0.03*math.sin(t*5))
        fl=sm((t-EV["collect"])/0.6)
        if fl>0:
            for k in range(12): an=k*math.pi/6+t*0.2; cv2.line(buf,(270,300),(int(270+math.cos(an)*230),int(300+math.sin(an)*80)),(1.0*0.35*fl,0.8*0.3*fl,0.4*0.2*fl),1,cv2.LINE_AA)
        def hd(d,t=t):
            ra=sm((t-EV["alien"]+0.3)/0.6)
            if ra>0.02:
                for i in range(30):
                    an=i*2*math.pi/30+t*0.25; x=540+math.cos(an)*330; y=600+math.sin(an)*95; front=math.sin(an)>0
                    d.rectangle([x-9,y-16,x+9,y+16],fill=(140,150,170,int(255*ra*(1.0 if front else 0.55))),outline=(200,215,235,int(200*ra)),width=2)
            lab(d,"JASON WRIGHT · PENN STATE",300,sm((t-EV["wright"])/0.3)*(1-sm((t-EV["structure"]+0.2)/0.3)),(230,235,245),CZ(46,800)); lab(d,"A GIANT STRUCTURE?",300,sm((t-EV["structure"])/0.3)*(1-sm((t-EV["headlines"]+0.2)/0.3)),AMB,CZ(56,800))
            for k,(s_,e) in enumerate([("ALIEN MEGASTRUCTURE STAR?!",EV["headlines"]),("WHAT IS DIMMING THIS STAR?",EV["headlines"]+0.5),("ALIENS OR NATURE?",EV["headlines"]+1.0)]):
                a=sm((t-e)/0.3)
                if a>0.02:
                    d.rectangle([140,930+k*130,940,1030+k*130],fill=(238,232,215,int(240*a)),outline=(120,110,90,int(255*a)),width=3); txt(d,(540,980+k*130),s_,B.F("BigShoulders-Bold",56),(30,25,20,int(255*a)),anchor="mm",stroke=0)
            lab(d,"LONG SHOT",300,sm((t-EV["longshot"])/0.25)*(1-sm((t-EV["testing"]+0.1)/0.3)),RED,fBig); lab(d,"WORTH TESTING",300,sm((t-EV["testing"])/0.3),GRN,CZ(56,800))
        hud.append(hd)
    elif n=="kickstarter":
        bgspace(buf,t,0.25)
        def hd(d,t=t):
            f=cl((t-EV["people"])/(EV["dollars"]-EV["people"]+1.3)); e=eout(f)
            lab(d,"KICKSTARTER · 2016",300,sm((t-EV["unusual"]+0.3)/0.3),GRN,CZ(58,800)); lab(d,"\"THE MOST MYSTERIOUS STAR IN THE GALAXY\"",390,sm((t-EV["y2016"])/0.3),(230,235,245),CZ(34,700))
            if t>EV["people"]-0.3:
                d.rounded_rectangle([120,600,960,650],radius=25,outline=(120,140,170,255),width=4); d.rounded_rectangle([124,604,124+int(832*e),646],radius=21,fill=(110,230,150,255))
                lab(d,f"${int(107654*e):,}",760,sm((t-EV["people"]+0.2)/0.3),(255,255,255),B.F("BigShoulders-Bold",150)); lab(d,f"{int(1703*e):,} BACKERS",890,sm((t-EV["people"]+0.2)/0.3),GRN,CZ(50,800))
            tp=sm((t-EV["telescope"])/0.5)
            if tp>0.02:
                cx,cy=540,1130; d.ellipse([cx-170,cy-170,cx+170,cy+170],outline=(120,180,230,int(255*tp)),width=4)
                for k,(sx,sy) in enumerate([(-90,-60),(20,-40),(-30,20),(90,-100),(-120,50),(60,60),(110,10),(-10,-110)]): dot(d,cx+sx,cy+sy,9,(255,220,120),tp*(0.55+0.45*math.sin(t*4+k)))
                lab(d,"LAS CUMBRES OBSERVATORY",1330,tp,(200,215,235),CZ(34,700))
        hud.append(hd)
    elif n=="test":
        bgspace(buf,t,0.15)
        def hd(d,t=t):
            for k,(ttl,sub,e,y0,vals) in enumerate([("SOLID OBJECT","ALL COLORS BLOCKED EQUALLY",EV["solid"],300,(0.8,0.8,0.8)),("DUST GRAINS","BLUE BLOCKED MORE THAN RED",EV["grains"],820,(1.0,0.62,0.32))]):
                a=sm((t-e)/0.4)
                if a<0.02: continue
                d.rounded_rectangle([120,y0,960,y0+440],radius=22,outline=(90,110,140,int(255*a)),width=3); lab(d,ttl,y0+50,a,AMB if k==0 else GRN,CZ(46,800)); lab(d,sub,y0+105,a,(200,215,235),CZ(30,700))
                for j,(nm,c) in enumerate([("R",(255,80,70)),("G",(90,230,120)),("B",(90,150,255))]):
                    hh=int(190*vals[j]*eout((t-e-0.4-j*0.15)/0.6)); x=340+j*160; d.rectangle([x,y0+400-hh,x+90,y0+400],fill=c+(int(255*a),)); txt(d,(x+45,y0+420),nm,fMono,(230,235,245,int(255*a)),anchor="mm",stroke=2)
            lab(d,"BLUE, BLOCKED MORE",1290,sm((t-EV["blue"])/0.3),(120,170,255),CZ(46,800))
        hud.append(hd)
    elif n=="result":
        bgspace(buf,t,0.15); up=cl((t-EV["dipped"])/(EV["deeper"]-EV["dipped"]+2.0))
        lcurve(buf,RED_,30,220,480,240,(1.0,0.4,0.35),upto=up,panel=True); lcurve(buf,BLUE,30,220,480,240,(0.4,0.6,1.0),upto=up,panel=False)
        def hd(d,t=t):
            lab(d,"2017",300,sm((t-EV["y2017"])/0.3)*(1-sm((t-EV["deeper"]+0.3)/0.3)),AMB,B.F("BigShoulders-Bold",120)); lab(d,"BLUE DEEPER THAN RED",300,sm((t-EV["deeper"])/0.3),(150,190,255),CZ(48,800))
            for j,(nm,c) in enumerate([("BLUE LIGHT",(100,150,255)),("RED LIGHT",(255,100,90))]): d.rectangle([700+0*j,920+j*44,724,944+j*44],fill=c+(255,)); txt(d,(740,932+j*44),nm,fMonoS,(230,235,245,255),anchor="lm",stroke=2)
            a=sm((t-EV["itdust"])/0.3)
            if a>0.02:
                lab(d,"DUST",1120,a,(220,180,130),B.F("BigShoulders-Bold",230))
                for j in range(60): an=j*2.4+t*0.3; rr=(j*7)%200; dot(d,540+math.cos(an)*rr*1.3,1120+math.sin(an)*rr*0.5,4,(210,170,120),a*0.8)
            ns=sm((t-EV["notsolid"])/0.3); na=sm((t-EV["notalien"])/0.3)
            lab(d,"NOT A SOLID OBJECT",1320,ns*(1-na),(230,235,245),CZ(40,800)); lab(d,"NOT AN ALIEN MACHINE",1320,na,RED,CZ(40,800))
        hud.append(hd)
    elif n=="open":
        bgspace(buf,t,0.25); ph=t>EV["photos"]-0.4
        if not ph:
            star(buf,270,250,40,0.9)
            for (an,rr,sp) in DP:
                a2=an+t*sp*0.4; x=270+math.cos(a2)*rr*1.2; y=250+math.sin(a2)*rr*0.42
                if 0<=x<w and 0<=y<h: buf[int(y),int(x)]+=np.array([0.7,0.55,0.4],np.float32)*sm((t-EV["where"])/1.0)
        else:
            f=cl((t-EV["photos"])/(EV["nobody"]-EV["photos"]+1.0)); xs=np.linspace(40,500,120); ys=250+f*0+ (xs-40)/460*110*np.linspace(0,1,120)**0.0
            n_=max(2,int(120*f)); cv2.polylines(buf,[np.stack([xs[:n_],(250+(xs[:n_]-40)/460*130)],1).astype(np.int32)],False,(0.55,0.92,1.0),2,cv2.LINE_AA)
        def hd(d,t=t):
            lab(d,"WHERE DOES THE DUST COME FROM?",300,sm((t-EV["where"])/0.3)*(1-sm((t-EV["photos"]+0.5)/0.3)),AMB,CZ(42,800))
            for k,(nm,e,x) in enumerate([("A SHATTERED PLANET?",EV["shattered"],300),("A STORM OF COMETS?",EV["storm"],780)]):
                a=sm((t-e)/0.3)*(1-sm((t-EV["photos"]+0.5)/0.3)); lab(d,nm,1040,a,(240,235,225),CZ(38,800),x=x)
            pa=sm((t-EV["photos"]+0.3)/0.4)
            if pa>0.02:
                for j in range(5): d.rectangle([120+j*150,1000,220+j*150,1090],fill=(40,36,30,int(230*pa)),outline=(160,150,130,int(255*pa)),width=3)
                lab(d,"1890  TO  TODAY",300,pa,(200,215,235),CZ(52,800)); lab(d,"SLOWLY FADING?",400,sm((t-EV["fading"])/0.3),AMB,CZ(56,800)); lab(d,"NOBODY KNOWS WHY",1200,sm((t-EV["nobody"])/0.3),RED,CZ(54,800))
        hud.append(hd)
    elif n=="end":
        bgspace(buf,t,0.5); tf=Lx("next strange star")[1]+0.5
        star(buf,270,300,46,1.0+0.015*math.sin(t*3)); 
        if t>tf: buf*=max(0.1,1-(t-tf)*1.1)
        def hd(d,t=t,tf=tf):
            lab(d,"IS THIS A MESSAGE?",1040,sm((t-EV["message"])/0.3)*(1-sm((t-EV["checked"]+0.2)/0.3)),AMB,CZ(58,800)); lab(d,"NOT THIS TIME",1040,sm((t-EV["wasnt"])/0.3)*(1-sm((t-tf+0.3)/0.3)),(230,235,245),CZ(58,800))
            if t>tf:
                kk=t-tf; a=sm((kk-0.3)/0.8)*(1-sm((kk-(SS("end")["e"]-tf-1.0))/0.6)); lg=LOGO.resize((int(LOGO.width*0.5),int(LOGO.height*0.5)),Image.LANCZOS); al=np.array(lg); al[:,:,3]=(al[:,:,3]*a).astype(np.uint8)
                d._image.alpha_composite(Image.fromarray(al),(W//2-lg.width//2,640-lg.height//2)); txt(d,(W//2,1000),"ORBITHOS",CZ(72,600),(255,215,140,int(255*a)),anchor="mm",stroke=2)
        hud.append(hd)
    return buf,hud
def post(buf,t):
    small=cv2.resize(buf,(w//4,h//4),interpolation=cv2.INTER_AREA); br=np.maximum(small-0.7,0)
    buf=buf+cv2.resize(cv2.GaussianBlur(br,(0,0),3)+cv2.GaussianBlur(br,(0,0),10)*1.4,(w,h))*0.8
    return (1-np.exp(-buf*1.35))*B.vig*band+B.grain[int(t*30)%8]*0.6
def compose(t):
    sc=B.scene_at(t); lt=t-sc["s"]; k=0.0
    if sc["i"]>0 if "i" in sc else B.SC.index(sc)>0: k=max(0.0,1-lt/0.6) if lt<0.6 else 0.0
    nx=[x for x in B.SC if x["s"]>sc["s"]]
    if nx and nx[0]["s"]-t<0.5: k=max(k,1-(nx[0]["s"]-t)/0.5)
    buf,hud=scene(t,sc); buf=post(buf,t)
    if k>0: buf=buf*np.array([1-0.55*k,1-0.8*k,1-0.96*k],np.float32)*(1-0.10*k*abs(math.sin(t*38)))
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if k>0: a=np.array(ov); a[:,:,3]=(a[:,:,3]*(1-0.9*k)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
TOTAL=B.TOTAL
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
