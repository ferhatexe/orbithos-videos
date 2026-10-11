import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid37")
for p in ["/home/claude/vid37","/home/claude/vid3","/home/claude/ep1"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
from paper import *
from PIL import Image, ImageDraw
EV=ev.EV; Lx=ev.Lx; SS=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
LOGO=E1.LOGO
RED=(200,40,40); INK=(30,26,22); PAPER=(238,226,200); PENCIL=(90,86,80)
TYPE="IBMPlexMono-Bold"; SERIF="LibreBaskerville-Regular"; HEAD="Gloock-Regular"
CODE=["WRGOABABD","MLIAOI","WTBIMPANETP","MLIABOAIAQC","ITTMTSAMSTGAB"]
# ---------- PIL helpers (full-res coords) ----------
def typed(d,s,x,y,fs,t,e,a=1.0,col=INK,bg=PAPER,cps=28,anchor="c"):
    if a<=0.01 or t<e: return
    n=min(len(s),int((t-e)*cps)+1); sub=s[:n]
    card(d,sub+(" " * (len(s)-n)),x,y,fs=fs,a=a,fg=col,bg=bg,fn=TYPE,torn=False,pad=(22,12))
def stamp(d,s,x,y,fs,a,ang=-8,col=RED,sc=1.0):
    if a<=0.01: return
    f=F("BigShoulders-Bold",int(fs)); tw=int(f.getlength(s)); th=int(fs*1.1); pad=18
    im=Image.new("RGBA",(tw+2*pad+8,th+2*pad+8),(0,0,0,0)); dd=ImageDraw.Draw(im)
    dd.rectangle([4,4,tw+2*pad+3,th+2*pad+3],outline=col+(255,),width=7); dd.text((pad+4,pad+4+fs*0.02),s,font=f,fill=col+(255,))
    arr=np.array(im); g=np.random.default_rng(len(s)); m=g.uniform(0.55,1.0,arr.shape[:2]); arr[...,3]=(arr[...,3]*m*a).astype(np.uint8)
    im=Image.fromarray(arr).rotate(ang,resample=Image.BICUBIC,expand=True)
    if abs(sc-1)>0.01: im=im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.BILINEAR)
    paste(d,im,x-im.width//2,y-im.height//2)
def tx(d,s,x,y,fs,col,a,fn=SERIF,anchor="mm",stroke=0,sc=(0,0,0)):
    if a<=0.01: return
    B.txt(d,(x,y),s,F(fn,fs),col+(int(255*min(1,a)),),anchor=anchor,stroke=stroke)
def poptime(t,e): return spring((t-e)/0.5)
# ---------- scene helpers (working res) ----------
def zoom(buf,cx,cy,z,tx_=None,ty_=None):
    if abs(z-1)<0.002: return buf
    tx_=w/2 if tx_ is None else tx_; ty_=h/2 if ty_ is None else ty_
    Mx=np.float32([[z,0,tx_-cx*z],[0,z,ty_-cy*z]]); return cv2.warpAffine(buf,Mx,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
def sea(buf,t,y0,col_sky_top,col_sky_hor,col_sea,col_sand,ysand=640):
    grad(buf,[(0,col_sky_top),(y0,col_sky_hor),(y0+1,col_sea),(ysand,lerpc(col_sea,col_sky_hor,0.35)),(ysand+1,col_sand),(h,lerpc(col_sand,(0,0,0),0.25))])
    wv=M(); g=np.random.default_rng(5)
    for k in range(40):
        f=g.uniform(0,1)**1.6; yy_=y0+8+f*(ysand-y0-14)+2*math.sin(t*0.9+k); L_=8+40*f*g.uniform(0.5,1.2)
        x=(g.uniform(0,w+80)+t*(6+14*f))%(w+80)-40; wv.line((x,yy_),(x+L_,yy_),0.8+1.2*f)
    comp(buf,wv,lerpc(col_sky_hor,(1,1,1),0.3),sh=0,rim=0,a=0.45)
    fo=M().poly([(0,ysand+4)]+[(x,ysand+4+5*math.sin(x/40+t*1.2)) for x in range(0,w+20,20)]+[(w,ysand+16),(0,ysand+16)]); comp(buf,fo,lerpc(col_sand,(1,1,1),0.5),sh=0,rim=0,a=0.7)
def seawall(buf,x0,x1,ytop,ybot,col):
    m=M().rect(x0,ytop,x1,ybot); comp(buf,m,col,sh=0.4)
    ln=M()
    for i,y in enumerate(np.arange(ytop+18,ybot,20)):
        ln.line((x0,y),(x1,y),1.2)
        for x in np.arange(x0+(i%2)*22,x1,44): ln.line((x,y-20),(x,y),1.2)
    comp(buf,ln,lerpc(col,(0,0,0),0.35),sh=0,rim=0,a=0.8)
def man(buf,x,y,s=1.0,arm=0.0,suit=(0.16,0.15,0.15),skin=(0.75,0.62,0.52),a=1.0):
    """slumped man sitting against a wall; (x,y)= hip on sand; facing right; arm: 0 rest .. 1 raised"""
    S_=s
    def P(px,py): return (x+px*S_,y+py*S_)
    lg=M().poly([P(-6,-10),P(10,-14),P(120,-6),P(122,8),P(0,8)]).poly([P(8,-4),P(118,-14),P(122,-2),P(10,10)])
    comp(buf,lg,lerpc(suit,(0,0,0),0.15),a=a)
    sh=M().ell(*P(128,-6),12*S_,7*S_,-10).ell(*P(126,6),12*S_,7*S_,10); comp(buf,sh,(0.05,0.05,0.05),a=a); comp(buf,M().ell(*P(131,-9),4*S_,2*S_),(0.9,0.9,0.9),sh=0,rim=0,a=a*0.8)
    tr=M().poly([P(-14,4),P(18,0),P(12,-78),P(-22,-84),P(-30,-70)]); comp(buf,tr,suit,a=a)
    comp(buf,M().poly([P(-2,-80),P(10,-78),P(4,-60)]),(0.92,0.92,0.9),sh=0,a=a)
    hd=M().circ(*P(-4,-98),15*S_); comp(buf,hd,skin,a=a)
    comp(buf,M().ell(*P(-9,-108),15*S_,8*S_,-20),(0.12,0.1,0.08),sh=0.1,a=a)
    ang=-0.3-2.1*arm; sx,sy=P(-6,-70); L_=60*S_
    ex,ey=sx+math.cos(1.2+ang)*L_*0.5,sy+math.sin(1.2+ang)*L_*0.5; hx,hy=ex+math.cos(0.9+ang*1.1)*L_*0.5,ey+math.sin(0.9+ang*1.1)*L_*0.5
    ar=M().line((sx,sy),(ex,ey),11*S_).line((ex,ey),(hx,hy),10*S_); comp(buf,ar,lerpc(suit,(1,1,1),0.06),a=a); comp(buf,M().circ(hx,hy,5*S_),skin,a=a,sh=0.1)
    return P(2,-82)   # collar point
def person(buf,x,y,s,col,hat=False,a=1.0,walk=0.0,ph=0.0,woman=False):
    H_=110*s; sw=math.sin(ph)*0.35*walk; lg=M()
    for sg in (1,-1): lg.line((x,y-0.45*H_),(x+math.sin(sg*sw)*0.45*H_,y),0.08*H_)
    comp(buf,lg,col,a=a)
    if woman: comp(buf,M().poly([(x-0.12*H_,y-0.8*H_),(x+0.12*H_,y-0.8*H_),(x+0.2*H_,y-0.3*H_),(x-0.2*H_,y-0.3*H_)]),col,a=a)
    else: comp(buf,M().rect(x-0.13*H_,y-0.82*H_,x+0.13*H_,y-0.42*H_),col,a=a)
    comp(buf,M().circ(x,y-0.9*H_,0.08*H_),col,a=a)
    if hat: comp(buf,M().ell(x,y-0.96*H_,0.14*H_,0.025*H_).rect(x-0.07*H_,y-1.02*H_,x+0.07*H_,y-0.96*H_),col,a=a)
def wood(buf,c0=(0.36,0.25,0.16),c1=(0.30,0.20,0.12)):
    g=np.random.default_rng(4); n=cv2.resize(g.normal(0,1,(8,h//20)).astype(np.float32),(w,h)); base=np.array(c0,np.float32)
    buf[:]=base*(0.85+0.08*np.sin(xx/9+n*3))[...,None]+np.array(c1,np.float32)*0.1
def felt(buf,c=(0.80,0.74,0.62)):
    grad(buf,[(0,c),(h,lerpc(c,(0,0,0),0.18))])
def stone_light(buf,cx,cy,r,col,a): rgrad(buf,cx,cy,r,col,a)
def helix(buf,cxl,t,y0,y1,amp,cols,a=1.0,phase=0.0):
    for k in range(2):
        pts=[]; dots=M()
        for y in np.arange(y0,y1,4):
            ph=(y-y0)/38+t*1.6+phase+k*math.pi; pts.append((cxl+amp*math.sin(ph),y))
        comp(buf,M().pline(pts,3.2),cols[k],sh=0.2,rim=0,a=a)
    rung=M()
    for y in np.arange(y0+8,y1,16):
        ph=(y-y0)/38+t*1.6+phase; x1=cxl+amp*math.sin(ph); x2=cxl+amp*math.sin(ph+math.pi); rung.line((x1,y),(x2,y),1.6)
    comp(buf,rung,(0.85,0.85,0.95),sh=0,rim=0,a=a*0.6)
# ================= scenes =================
def s_hook(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; col=[]
    sea(buf,t,330,(0.04,0.04,0.06),(0.32,0.30,0.30),(0.12,0.12,0.13),(0.40,0.36,0.30),ysand=520)
    comp(buf,M().circ(400,150,26),(0.92,0.90,0.82),sh=0); rgrad(buf,400,150,90,(0.6,0.58,0.5),0.25)
    seawall(buf,-10,w+10,560,640,(0.30,0.28,0.26))
    sandm=M().rect(-5,640,w+5,h+5); comp(buf,sandm,(0.42,0.38,0.32),sh=0.3)
    z=1+0.25*sm((t-0.2)/12)
    man(buf,170,690,1.1)
    rgrad(buf,150,640,160,(0.85,0.80,0.65),0.18+0.06*math.sin(t*2))
    buf=zoom(buf,250,600,z,270,560)
    def hd(d,t=t):
        typed(d,"1 DECEMBER 1948",540,200,44,t,0.3,a=fa(t,0.3,EV["wallet"]-0.3))
        typed(d,"SOMERTON BEACH · SOUTH AUSTRALIA",540,290,28,t,0.9,a=fa(t,0.9,EV["wallet"]-0.3))
        a=fa(t,EV["wallet"]-0.1,EV["secret"]-0.4)
        stamp(d,"NO WALLET",330,220,74,a*sm((t-EV["wallet"])/0.15),-8,sc=1+0.5*(1-sm((t-EV["wallet"])/0.2)))
        stamp(d,"NO NAME",760,330,74,a*sm((t-EV["noname"])/0.15),6,sc=1+0.5*(1-sm((t-EV["noname"])/0.2)))
        typed(d,"LABELS: CUT OUT",540,470,40,t,EV["labels"],a=a)
        a=fa(t,EV["secret"]-0.1,EV["y74"]-0.3)
        if a>0.01:
            s_=poptime(t,EV["tamam"]-0.2)
            card(d,"Tamám Shud",540,330,fs=96,a=a*sm((t-EV["tamam"]+0.2)/0.3),fg=(25,22,18),bg=(240,232,210),fn=SERIF,torn=True,pad=(46,22),sc=s_)
            typed(d,"HIDDEN IN A SECRET POCKET",540,190,32,t,EV["secret"],a=a)
        a=fa(t,EV["y74"]-0.1,sc["e"]+1)
        card(d,"74 YEARS",540,300,fs=150,a=a,fn="BigShoulders-Bold",fg=(240,232,210),bg=(25,22,18),torn=False,sc=poptime(t,EV["y74"]-0.1))
        typed(d,"TO LEARN WHO HE WAS",540,450,34,t,EV["who"],a=a)
    hud.append(hd); return buf,hud,col,0.0
def s_beach(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; col=[]
    ev_=sm((t-EV["evening"]+0.3)/1.2)
    sea(buf,t,300,lerpc((0.70,0.72,0.74),(0.10,0.10,0.14),ev_),lerpc((0.92,0.90,0.86),(0.40,0.34,0.30),ev_),lerpc((0.55,0.58,0.60),(0.18,0.17,0.18),ev_),lerpc((0.86,0.80,0.70),(0.36,0.32,0.28),ev_),ysand=520)
    comp(buf,M().circ(110,200,40),lerpc((1,0.98,0.9),(0.9,0.7,0.5),ev_),sh=0)
    seawall(buf,-10,w+10,540,620,lerpc((0.62,0.58,0.52),(0.26,0.24,0.22),ev_))
    comp(buf,M().rect(-5,620,w+5,h+5),lerpc((0.82,0.76,0.64),(0.30,0.27,0.23),ev_),sh=0.3)
    if t<EV["evening"]:
        sw=sm((t-EV["swim"]+0.4)/2.5); px=w+60-sw*190
        person(buf,px,700,0.95,(0.30,0.28,0.26),walk=1-sm((t-EV["swim"]-2.3)/0.3),ph=t*6)
        comp(buf,M().rect(px-10,620,px+12,660),(0.9,0.88,0.82),sh=0.2)
    arm=0.0
    if t>EV["raised"]-0.1: arm=sm((t-EV["raised"]+0.1)/0.6)*(1-sm((t-EV["drop"])/0.35))
    cx,cy=man(buf,170,670,1.05,arm=arm)
    if t<EV["evening"]:
        for k in range(3):
            u=((t*0.35+k/3)%1.0); sx=cx+8+u*40+10*math.sin(t*2+k*2); sy=cy-6-u*90
            rgrad(buf,sx,sy,8+u*14,(0.85,0.85,0.85),0.25*(1-u)*sm((t-EV["cig"]+0.3)/0.4))
    if ev_>0:
        rgrad(buf,470,330,120,(1.0,0.85,0.55),0.35*ev_)
        comp(buf,M().rect(466,330,474,540),(0.1,0.1,0.1),a=ev_); comp(buf,M().circ(470,325,10),(1,0.92,0.7),sh=0,a=ev_)
        g=np.random.default_rng(int(t*14))
        for i in range(10): rgrad(buf,cx-10+g.uniform(-30,30),cy-40+g.uniform(-30,20),2,(0.9,0.9,0.9),0.5*ev_)
    z=1.0; zx,zy=270,560
    for e,(zz,px_,py_),e2 in ((EV["suit"],(1.7,190,600),EV["legs"]-0.2),(EV["legs"],(1.6,250,660),EV["cig"]-0.2),(EV["cig"],(2.4,cx+10,cy-10),EV["cold"]-0.2)):
        k=sm((t-e+0.2)/0.6)*(1-sm((t-e2)/0.5))
        if k>0: z=1+(zz-1)*k; zx,zy=px_,py_
    buf=zoom(buf,zx,zy,z,270,520)
    def hd(d,t=t):
        typed(d,"SOMERTON BEACH, ADELAIDE",540,200,36,t,EV["somerton"],a=fa(t,EV["somerton"],EV["suit"]-0.3))
        typed(d,"~6:30 AM",540,290,40,t,EV["dawn"],a=fa(t,EV["dawn"],EV["suit"]-0.3))
        for s,e,y in (("NEAT SUIT",EV["suit"],200),("BRAND NEW SHOES",EV["shoes"],290),("FEET CROSSED",EV["crossed"],380),("HALF-SMOKED CIGARETTE",EV["cig"],470)):
            typed(d,s,540,y if e<EV["cig"] else 200,34,t,e,a=fa(t,e,(EV["legs"]-0.2) if e<EV["legs"] else (EV["cig"]-0.2) if e<EV["cig"] else EV["cold"]-0.2,0.15,0.25))
        stamp(d,"NO SIGNS OF VIOLENCE",540,260,64,fa(t,EV["noviol"]-0.1,EV["evening"]-0.3,0.12,0.3),-5)
        typed(d,"30 NOVEMBER · ~7 PM",540,200,36,t,EV["evening"],a=fa(t,EV["evening"],sc["e"]+1))
        card(d,"“We thought he was asleep.”",540,330,fs=44,a=fa(t,EV["asleep"]-0.2,sc["e"]+1),fn="InstrumentSerif-Italic",fg=INK,bg=PAPER)
    hud.append(hd); return buf,hud,col,0.0
def s_pockets(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; col=[]
    felt(buf,(0.78,0.74,0.66))
    items=[("train",EV["train"],(140,170)),("bus",EV["bus"],(390,170)),("gum",EV["gum"],(130,330)),("matches",EV["matches"],(270,330)),("combs",EV["combs"],(410,330)),("pack",EV["pack"],(270,500))]
    for nm,e,(x,y) in items:
        s_=spring((t-e+0.15)/0.5)
        if s_<0.02: continue
        if nm in("train","bus"):
            comp(buf,M().poly(rot([(-70,-34),(70,-34),(70,34),(-70,34)],-0.08 if nm=="train" else 0.06,x,y,s_,s_)),(0.93,0.90,0.82),sh=0.35)
            ln=M()
            for k in range(3): ln.line(rot([(-50,-12+k*12)],0,x,y,s_,s_)[0],rot([(30-k*10,-12+k*12)],0,x,y,s_,s_)[0],2)
            comp(buf,ln,(0.3,0.28,0.25),sh=0,rim=0)
        elif nm=="gum": comp(buf,M().poly(rot([(-14,-46),(14,-46),(14,46),(-14,46)],0.3,x,y,s_,s_)),(0.85,0.82,0.75),sh=0.35)
        elif nm=="matches":
            comp(buf,M().poly(rot([(-40,-26),(40,-26),(40,26),(-40,26)],-0.1,x,y,s_,s_)),(0.60,0.55,0.48),sh=0.35)
            comp(buf,M().poly(rot([(-40,-8),(40,-8),(40,8),(-40,8)],-0.1,x,y,s_,s_)),(0.30,0.27,0.24),sh=0)
        elif nm=="combs":
            for k in range(2):
                cm=M().rect(x-46*s_,y-24*s_+k*34,x+46*s_,y-16*s_+k*34)
                for i in range(18): cm.rect(x-44*s_+i*5*s_,y-16*s_+k*34,x-42*s_+i*5*s_,y-4*s_+k*34)
                comp(buf,cm,(0.18,0.16,0.14),sh=0.3)
        else:
            op=sm((t-EV["brand"]+0.1)/0.6)
            comp(buf,M().rect(x-70*s_,y-50*s_,x+70*s_,y+50*s_),(0.35,0.32,0.28),sh=0.4)
            comp(buf,M().rect(x-62*s_,y-42*s_,x+62*s_,y+42*s_),(0.88,0.84,0.76),sh=0)
            if op>0:
                for k in range(5): comp(buf,M().rect(x-58+k*24,y-40-60*op,x-42+k*24,y+30-60*op),(0.95,0.94,0.9),sh=0.3)
                for k in range(5): comp(buf,M().rect(x-58+k*24,y-40-60*op,x-42+k*24,y-26-60*op),(0.75,0.58,0.40),sh=0)
    ct=sm((t-EV["cut"]+0.3)/0.4)
    if t>EV["nomoney"]-0.4:
        k=sm((t-EV["nomoney"]+0.4)/0.4); buf2=np.zeros_like(buf); felt(buf2,(0.70,0.66,0.58))
        comp(buf2,M().poly([(110,250),(430,250),(470,620),(70,620)]),(0.92,0.92,0.9),sh=0.4)
        comp(buf2,M().poly([(200,250),(270,330),(340,250),(320,230),(270,280),(220,230)]),(0.84,0.84,0.82),sh=0.3)
        lab=M().rect(240,290,300,320); comp(buf2,lab,(0.75,0.70,0.60),sh=0.2,a=1-ct)
        st=M()
        for i in range(8): st.line((236+i*9,290),(240+i*9,286),1.4); st.line((236+i*9,322),(240+i*9,326),1.4)
        comp(buf2,st,(0.3,0.3,0.3),sh=0,rim=0,a=ct)
        sx=180+120*sm((t-EV["cut"]+0.6)/0.8); sc_=M()
        op_=abs(math.sin(t*10))*0.4
        sc_.poly(rot([(0,-4),(70,-2),(70,2),(0,4)],-op_,sx,305)).poly(rot([(0,-4),(70,-2),(70,2),(0,4)],op_,sx,305)).circ(sx-14,295,11).circ(sx-14,315,11)
        comp(buf2,sc_,(0.25,0.25,0.27),sh=0.35,a=sm((t-EV["cut"]+0.8)/0.3)*(1-sm((t-EV["cut"]-0.5)/0.4)))
        buf[:]=buf*(1-k)+buf2*k
    def hd(d,t=t):
        a0=1-sm((t-EV["nomoney"]+0.4)/0.3)
        for (s,e,x,y) in (("TRAIN TICKET",EV["train"],280,470),("BUS TICKET",EV["bus"],780,470),("GUM",EV["gum"],260,790),("MATCHES",EV["matches"],540,790),("2 COMBS",EV["combs"],820,790),("CIGARETTES",EV["pack"],540,1180)):
            typed(d,s,x,y,26,t,e,a=a0,cps=40)
        card(d,"ARMY CLUB",540,1000,fs=30,a=a0*sm((t-EV["pack"])/0.3)*(1-sm((t-EV["brand"])/0.3)),fn=HEAD,fg=(30,30,30),bg=(220,210,190),torn=False)
        card(d,"…KENSITAS INSIDE",540,1260,fs=30,a=a0*sm((t-EV["brand"]-0.2)/0.3),fn=TYPE,fg=(255,255,255),bg=(150,30,30),torn=False)
        stamp(d,"NO MONEY",300,230,70,sm((t-EV["nomoney"])/0.12),-7)
        stamp(d,"NO ID",780,250,70,sm((t-EV["noid"])/0.12),6)
        typed(d,"LABELS CAREFULLY REMOVED",540,1250,32,t,EV["cut"])
    hud.append(hd); return buf,hud,col,0.0
def s_autopsy(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; col=[]
    grad(buf,[(0,(0.86,0.86,0.82)),(h,(0.70,0.70,0.66))])
    ph2=sm((t-EV["poison"]+0.4)/0.5); ph3=sm((t-EV["expert"]+0.4)/0.5)
    a1=1-ph2
    if a1>0.01:
        bd=M().circ(270,150,48).poly([(200,200),(340,200),(372,260),(352,600),(188,600),(168,260)])
        comp(buf,bd,(0.93,0.91,0.86),sh=0.3,a=a1)
        ol=M()
        pts=[(270+48*math.cos(u),150+48*math.sin(u)) for u in np.linspace(0,6.3,60)]; ol.pline(pts,2)
        ol.pline([(200,200),(168,260),(188,600),(352,600),(372,260),(340,200),(200,200)],2); comp(buf,ol,(0.35,0.33,0.30),sh=0,rim=0,a=a1)
        comp(buf,M().ell(240,330,48,30,-15).ell(300,320,40,26,10),(0.72,0.62,0.58),sh=0.15,a=a1*0.7)
        lv=sm((t-EV["liver"])/0.6); comp(buf,M().ell(240,400,56,30,8),lerpc((0.72,0.55,0.48),(0.38,0.18,0.18),lv),sh=0.2,a=a1)
        sk=1+2*sm((t-EV["three"]+0.1)/1.0); sp=M().ell(330,385,16*math.sqrt(sk),26*math.sqrt(sk),20); comp(buf,sp,(0.52,0.30,0.32),sh=0.25,a=a1)
        if t>EV["spleen"]: rgrad(buf,330,385,50*math.sqrt(sk),(0.4,0.1,0.1),0.15*a1)
    if ph2>0.01 and ph3<0.99:
        a2=ph2*(1-ph3)
        comp(buf,M().rect(70,470,470,500),(0.42,0.30,0.20),sh=0.35,a=a2)
        for k in range(5):
            x=110+k*80; tb=M().rect(x-14,250,x+14,450).circ(x,450,14); comp(buf,tb,(0.92,0.94,0.95),sh=0.3,a=a2)
            comp(buf,M().rect(x-12,360,x+12,450).circ(x,450,12),(0.62,0.66,0.66),sh=0,a=a2)
    if ph3>0.01:
        comp(buf,M().poly([(110,240),(430,220),(450,560),(130,580)]),(0.95,0.93,0.86),sh=0.4,a=ph3)
        ln=M()
        for k in range(8): ln.line((140,280+k*36),(420,268+k*36),1.0)
        comp(buf,ln,(0.6,0.65,0.75),sh=0,rim=0,a=ph3*0.6)
        u=sm((t-EV["wrote"]+0.3)/1.4); pts=[(160+i*4,330+8*math.sin(i*0.7)+3*math.sin(i*2.3)) for i in range(int(60*u)+1)]
        if len(pts)>1: comp(buf,M().pline(pts,2.4),(0.15,0.15,0.2),sh=0,rim=0,a=ph3)
        pts2=[(160+i*4,400+8*math.sin(i*0.9)+3*math.sin(i*2.1)) for i in range(int(50*sm((t-EV["wrote"]-0.6)/1.2))+1)]
        if len(pts2)>1: comp(buf,M().pline(pts2,2.4),(0.15,0.15,0.2),sh=0,rim=0,a=ph3)
        pen=(160+60*4*u,330); comp(buf,M().line(pen,(pen[0]+60,pen[1]-90),7),(0.15,0.12,0.1),sh=0.4,a=ph3*sm((t-EV["wrote"]+0.5)/0.3))
    def hd(d,t=t):
        typed(d,"AUTOPSY · 2 DEC 1948",540,180,36,t,sc["s"]+0.3,a=fa(t,sc["s"]+0.3,EV["poison"]-0.4))
        card(d,"SPLEEN ×3",820,690,fs=56,a=fa(t,EV["three"],EV["poison"]-0.4),fn="BigShoulders-Bold",fg=(255,255,255),bg=(150,30,30),torn=False,sc=poptime(t,EV["three"]))
        typed(d,"LIVER: CONGESTED",300,950,30,t,EV["liver"],a=fa(t,EV["liver"],EV["poison"]-0.4))
        typed(d,"POISON?",540,250,60,t,EV["poison"],a=fa(t,EV["poison"],EV["expert"]-0.4))
        for k in range(5):
            e=EV["clean"]+k*0.12; stamp(d,"NEGATIVE",220+k*160,1010,30,fa(t,e,EV["expert"]-0.4,0.1,0.3),-12+k*5)
        typed(d,"A RARE POISON THAT VANISHES?",540,250,34,t,EV["rare"],a=fa(t,EV["rare"],sc["e"]+1))
        card(d,"He wouldn't say it aloud.\nHe wrote it down.",540,1240,fs=42,a=fa(t,EV["court"],sc["e"]+1),fn="InstrumentSerif-Italic",fg=INK,bg=PAPER)
    hud.append(hd); return buf,hud,col,0.0
def s_suitcase(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; col=[]
    grad(buf,[(0,(0.42,0.38,0.32)),(560,(0.55,0.50,0.42)),(561,(0.30,0.24,0.18)),(h,(0.22,0.18,0.14))])
    sh_=M()
    for k in range(4): sh_.rect(20,100+k*110,520,108+k*110)
    comp(buf,sh_,(0.22,0.18,0.14),sh=0.3)
    g=np.random.default_rng(1); bx=M()
    for k in range(4):
        x=30
        while x<500:
            ww=g.uniform(50,90); hh=g.uniform(40,80); bx.rect(x,100+k*110-hh,x+ww,100+k*110); x+=ww+g.uniform(6,20)
    comp(buf,bx,(0.36,0.30,0.24),sh=0.3)
    cxc,cyc=440,70; comp(buf,M().circ(cxc,cyc,40),(0.92,0.90,0.84),sh=0.4)
    hh_=M().line((cxc,cyc),(cxc+18*math.sin(t*0.1),cyc-18*math.cos(t*0.1)),3).line((cxc,cyc),(cxc+28*math.sin(t*1.2),cyc-28*math.cos(t*1.2)),2); comp(buf,hh_,(0.1,0.1,0.1),sh=0,rim=0)
    comp(buf,M().rect(-5,560,w+5,620),(0.22,0.16,0.11),sh=0.4)
    op=sm((t-EV["again"]+0.3)/0.8)
    sx,sy=270,540
    body=M().rect(sx-150,sy-110,sx+150,sy); comp(buf,body,(0.66,0.48,0.30),sh=0.55)
    stp=M().rect(sx-95,sy-110,sx-80,sy).rect(sx+80,sy-110,sx+95,sy); comp(buf,stp,(0.35,0.24,0.15),sh=0.15)
    comp(buf,M().rect(sx-120,sy-104,sx-104,sy-92).rect(sx+104,sy-104,sx+120,sy-92),(0.85,0.75,0.45),sh=0.2)
    if op<0.5:
        comp(buf,M().rect(sx-150,sy-110,sx+150,sy-96),(0.52,0.36,0.22),sh=0)
        hd_=M().rect(sx-34,sy-134,sx+34,sy-124).rect(sx-34,sy-134,sx-24,sy-110).rect(sx+24,sy-134,sx+34,sy-110); comp(buf,hd_,(0.30,0.20,0.12),sh=0.3)
    else:
        lid=M().poly([(sx-150,sy-110),(sx+150,sy-110),(sx+150,sy-110-200*(op-0.5)*2),(sx-150,sy-110-200*(op-0.5)*2)]); comp(buf,lid,(0.58,0.42,0.26),sh=0.3)
        comp(buf,M().rect(sx-140,sy-104,sx+140,sy-8),(0.80,0.78,0.72),sh=0.1)
        cl_=M().poly([(sx-130,sy-90),(sx-20,sy-96),(sx-30,sy-20),(sx-128,sy-18)]); comp(buf,cl_,(0.55,0.55,0.58),sh=0.25)
    th=spring((t-EV["thread"]+0.1)/0.6)
    if th>0.02 and op>0.5:
        def cf(b,th=th):
            comp(b,M().ell(sx+70,sy-56,34*th,30*th),(0.93,0.48,0.12),sh=0.35)
            comp(b,M().ell(sx+70,sy-56,10*th,9*th),(0.85,0.80,0.70),sh=0)
            if t>EV["mend"]: comp(b,M().pline([(sx+90,sy-40)]+[(sx+100+i*6,sy-40+i*2+8*math.sin(i*0.6)) for i in range(int(14*sm((t-EV["mend"])/0.8))+1)],2.2),(0.93,0.48,0.12),sh=0.2,rim=0)
        col.append(cf)
    tg=fa(t,EV["items"]-0.2,sc["e"]+1)
    if tg>0:
        for k,(x,y) in enumerate(((150,450),(270,445),(390,452))):
            if t>EV["items"]+k*0.2: comp(buf,M().poly(rot([(-30,-14),(30,-14),(36,0),(30,14),(-30,14)],0.1*(k-1),x,y)),(0.92,0.88,0.78),sh=0.35,a=tg)
    def hd(d,t=t):
        typed(d,"ADELAIDE RAILWAY STATION",540,200,36,t,EV["station"],a=fa(t,EV["station"],EV["again"]-0.3))
        typed(d,"LEFT: 30 NOVEMBER 1948",540,290,36,t,EV["daybefore"],a=fa(t,EV["daybefore"],EV["again"]-0.3))
        stamp(d,"LABELS REMOVED",540,250,62,fa(t,EV["again"],EV["thread"]-0.2,0.12,0.3),-6)
        card(d,"ORANGE THREAD",540,250,fs=54,a=fa(t,EV["thread"],EV["items"]-0.3),fn="BigShoulders-Bold",fg=(255,255,255),bg=(225,110,30),torn=False,sc=poptime(t,EV["thread"]))
        typed(d,"SAME AS HIS POCKET REPAIR",540,360,30,t,EV["mend"],a=fa(t,EV["mend"],EV["items"]-0.3))
        if t>EV["keane"]-0.3:
            for k,(s,x,y) in enumerate((("KEANE",300,890),("KEAN",540,880),("T. KEANE",780,895))):
                tx(d,s,x,y,30,INK,fa(t,EV["keane"]-0.3+k*0.2,sc["e"]+1),fn=TYPE)
        stamp(d,"NO MISSING KEANE",540,280,62,fa(t,EV["nokeane"],sc["e"]+1,0.12,0.3),-5)
    hud.append(hd); return buf,hud,col,0.0
def s_scrap(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; col=[]
    bk=sm((t-EV["final"]+0.4)/0.6)
    grad(buf,[(0,(0.46,0.44,0.43)),(h,(0.30,0.29,0.28))])
    g=np.random.default_rng(2); tw_=M()
    for i in range(0,w,6): tw_.line((i,0),(i-30,h),1.0)
    comp(buf,tw_,(0.38,0.36,0.35),sh=0,rim=0,a=0.7)
    comp(buf,M().rect(-5,200,w+5,300),(0.36,0.34,0.33),sh=0.5)
    comp(buf,M().rect(60,190,90,310).rect(450,190,480,310),(0.40,0.38,0.37),sh=0.4)
    comp(buf,M().circ(270,250,16),(0.20,0.18,0.16),sh=0.4); comp(buf,M().circ(266,246,3).circ(274,254,3),(0.4,0.38,0.35),sh=0)
    st=M()
    for x in range(10,w,14): st.line((x,206),(x+7,206),1.6); st.line((x,294),(x+7,294),1.6)
    comp(buf,st,(0.55,0.52,0.48),sh=0,rim=0)
    po=sm((t-EV["tiny"]+0.2)/0.5)
    if po>0:
        comp(buf,M().rect(330,220,330+90*po,290),(0.30,0.29,0.28),sh=0.4)
        pst=M()
        for y in range(224,290,10): pst.line((330,y),(330,y+5),1.4); pst.line((330+90*po,y),(330+90*po,y+5),1.4)
        comp(buf,pst,(0.6,0.56,0.5),sh=0,rim=0,a=po)
    ro=sm((t-EV["rolled"]+0.2)/0.8); un=sm((t-EV["twowords2"])/0.8)
    if ro>0:
        y=300+ro*150; L_=40+380*un; hh=14+60*un
        comp(buf,M().rect(270-L_/2,y-hh/2,270+L_/2,y+hh/2),(0.93,0.90,0.82),sh=0.45)
        if un<0.95: comp(buf,M().ell(270+L_/2,y,7,hh/2),(0.82,0.78,0.70),sh=0.2)
    if bk>0:
        b2=np.zeros_like(buf); grad(b2,[(0,(0.20,0.15,0.12)),(h,(0.12,0.09,0.07))])
        comp(b2,M().rect(110,110,430,600),(0.38,0.20,0.14),sh=0.5)
        orn=M()
        for r in (0,1): orn.pline([(126+r*10,126+r*10),(414-r*10,126+r*10),(414-r*10,584-r*10),(126+r*10,584-r*10),(126+r*10,126+r*10)],2)
        for k in range(8):
            a_=k*math.pi/4; orn.pline([(270+math.cos(a_+u)*(40+20*math.sin(4*u)),400+math.sin(a_+u)*(40+20*math.sin(4*u))) for u in np.linspace(0,0.8,12)],2)
        comp(b2,orn,(0.85,0.70,0.40),sh=0,rim=0)
        buf[:]=buf*(1-bk)+b2*bk
    def hd(d,t=t,bk=bk):
        typed(d,"APRIL 1949",540,180,40,t,EV["april"],a=fa(t,EV["april"],EV["rolled"]-0.3))
        typed(d,"A HIDDEN FOB POCKET",540,700,34,t,EV["tiny"],a=fa(t,EV["tiny"],EV["rolled"]-0.3))
        un=sm((t-EV["twowords2"])/0.8); y=(300+150)*2
        tx(d,"Tamám Shud",540,y,int(40+60*un),(25,22,18),un*(1-bk),fn=SERIF)
        typed(d,"PERSIAN: “IT IS FINISHED”",540,1180,34,t,EV["finished"],a=fa(t,EV["persian"],EV["final"]-0.3))
        a=bk
        tx(d,"RUBÁIYÁT",540,420,64,(235,200,120),a*sm((t-EV["rubaiyat"]+0.3)/0.4),fn=HEAD)
        tx(d,"OF",540,500,30,(235,200,120),a*sm((t-EV["rubaiyat"])/0.4),fn=SERIF)
        tx(d,"OMAR KHAYYÁM",540,560,50,(235,200,120),a*sm((t-EV["rubaiyat"]+0.1)/0.4),fn=HEAD)
        typed(d,"THE BOOK'S LAST WORDS",540,1240,32,t,EV["final"],a=a)
    hud.append(hd); return buf,hud,col,0.0
def car(buf,x,y,s,colc):
    m=M().poly([(x-150*s,y),(x-140*s,y-40*s),(x-90*s,y-48*s),(x-60*s,y-90*s),(x+50*s,y-92*s),(x+90*s,y-50*s),(x+150*s,y-40*s),(x+158*s,y)])
    comp(buf,m,colc,sh=0.45)
    comp(buf,M().poly([(x-52*s,y-80*s),(x-6*s,y-82*s),(x-6*s,y-52*s),(x-80*s,y-50*s)]).poly([(x+4*s,y-82*s),(x+44*s,y-82*s),(x+76*s,y-52*s),(x+4*s,y-52*s)]),(0.62,0.66,0.70),sh=0)
    for wx in (-90,95): comp(buf,M().circ(x+wx*s,y,28*s),(0.08,0.08,0.08),sh=0.3); comp(buf,M().circ(x+wx*s,y,12*s),(0.6,0.6,0.6),sh=0)
def s_book(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; col=[]
    bc=sm((t-EV["matched"]+0.4)/0.6)
    if bc<1:
        grad(buf,[(0,(0.70,0.70,0.70)),(420,(0.86,0.84,0.80)),(421,(0.55,0.52,0.48)),(h,(0.40,0.38,0.34))])
        comp(buf,M().rect(-5,300,w+5,330),(0.62,0.62,0.64),sh=0)
        cx_=270+40*math.sin(t*0.2); car(buf,cx_,560,1.25,(0.22,0.22,0.24))
        bb=sm((t-EV["car"]+0.2)/0.5)
        if bb>0:
            rgrad(buf,cx_-20,500,60,(1,0.95,0.8),0.4*bb)
            comp(buf,M().poly(rot([(-26,-18),(26,-18),(26,18),(-26,18)],0.3,cx_-20,500)),(0.40,0.22,0.15),sh=0.4,a=bb)
        buf=zoom(buf,cx_-20,500,1+1.4*sm((t-EV["car"]+0.3)/1.4),270,420)
    if bc>0:
        b2=np.zeros_like(buf); grad(b2,[(0,(0.30,0.26,0.22)),(h,(0.18,0.15,0.12))])
        comp(b2,M().rect(90,90,450,620),(0.88,0.84,0.74),sh=0.5)
        tr=M().poly([(380,90),(450,90),(450,170),(430,160),(420,130),(400,124)]); comp(b2,tr,(0.30,0.26,0.22),sh=0,rim=0)
        mv=sm((t-EV["matched"])/0.7); px=380+60*(1-mv); py=60+40*(1-mv)
        comp(b2,M().poly([(px,py+30),(px+70,py+30),(px+70,py+110),(px+50,py+100),(px+40,py+70),(px+20,py+64)]),(0.93,0.90,0.82),sh=0.4)
        bl=sm((t-EV["phone"])/0.5)
        if bl>0:
            comp(b2,M().rect(140,180,320,210),(0.35,0.34,0.33),sh=0,rim=0,a=0.35*bl)
            blur=cv2.GaussianBlur(b2[170:220,130:330],(0,0),4); b2[170:220,130:330]=blur
        buf[:]=buf*(1-bc)+b2*bc
    def hd(d,t=t,bc=bc):
        typed(d,"JULY 1949",540,200,40,t,EV["july"],a=fa(t,EV["july"],EV["car"]-0.2))
        typed(d,"FOUND IN A CAR NEAR THE BEACH",540,290,30,t,EV["car"],a=fa(t,EV["car"],EV["matched"]-0.5))
        stamp(d,"MATCH",780,240,70,fa(t,EV["matched"]+0.6,sc["e"]+1,0.12,0.3),-10)
        tx(d,"PHONE NUMBER",460,340,26,(120,30,30),bc*sm((t-EV["phone"])/0.3),fn=TYPE)
        for k,ln in enumerate(CODE):
            e=EV["five"]+k*0.3; a=bc*sm((t-e)/0.4)*0.85
            if a>0.01:
                tx(d,ln,540,560+k*90,48,PENCIL,a,fn="NothingYouCouldDo-Regular")
                if k==1: d.line([(330,560+k*90),(750,560+k*90)],fill=PENCIL+(int(200*a),),width=4)
    hud.append(hd); return buf,hud,col,0.0
def s_code(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; col=[]
    nu=sm((t-EV["nurse"]+0.4)/0.6)
    grad(buf,[(0,(0.12,0.11,0.12)),(h,(0.06,0.06,0.07))])
    if nu<1:
        comp(buf,M().rect(70,160,470,600),(0.80,0.76,0.66),sh=0.5,a=1-nu)
        uv=(t-sc["s"])*0.45%1.4-0.2
        def cf(b,uv=uv,nu=nu):
            rgrad(b,70+400*uv,380,120,(0.45,0.15,0.85),0.55*(1-nu)); rgrad(b,70+400*uv,380,50,(0.6,0.3,1.0),0.35*(1-nu))
        col.append(cf)
    if nu>0:
        b2=np.zeros_like(buf); grad(b2,[(0,(0.40,0.38,0.36)),(h,(0.20,0.19,0.18))])
        rgrad(b2,170,300,180,(0.8,0.75,0.65),0.3)
        wm_=M().circ(170,300,62).ell(170,250,70,40).poly([(110,330),(230,330),(260,600),(80,600)]).ell(120,320,30,60,15).ell(220,320,30,60,-15)
        comp(b2,wm_,(0.12,0.11,0.11),sh=0.4)
        cs=M().circ(390,320,64).poly([(340,360),(440,360),(470,600),(310,600)]); comp(b2,cs,(0.90,0.88,0.84),sh=0.45,a=sm((t-EV["castf"]+0.2)/0.5))
        comp(b2,M().ell(372,316,7,4).ell(408,316,7,4),(0.75,0.73,0.70),sh=0,a=sm((t-EV["castf"]+0.2)/0.5))
        sk=sm((t-EV["shaken"])/0.3)*(1-sm((t-EV["shaken"]-1.2)/0.4))
        if sk>0: b2=np.roll(b2,int(3*math.sin(t*60)*sk),1)
        buf[:]=buf*(1-nu)+b2*nu
    def hd(d,t=t,nu=nu):
        a0=1-nu
        g=np.random.default_rng(int(t*12))
        for k,ln in enumerate(CODE):
            s=ln
            if EV["naval"]<t<EV["nobody"]: s="".join(c if g.uniform()<0.5 else chr(65+int(g.integers(26))) for c in ln)
            tx(d,s,540,400+k*110,58,(70,60,55),a0,fn=TYPE)
            if k==1: d.line([(340,400+k*110),(740,400+k*110)],fill=(70,60,55,int(220*a0)),width=5)
        typed(d,"NAVAL INTELLIGENCE",540,200,36,t,EV["naval"],a=fa(t,EV["naval"],EV["nobody"]-0.2)*a0)
        typed(d,"+ DECADES OF AMATEURS",540,1260,32,t,EV["amateurs"],a=fa(t,EV["amateurs"],EV["nurse"]-0.4))
        stamp(d,"UNSOLVED",540,640,120,a0*sm((t-EV["cracked"])/0.12),-9,sc=1+0.6*(1-sm((t-EV["cracked"])/0.2)))
        typed(d,"A YOUNG NURSE, NEARBY",540,180,36,t,EV["nurse"],a=fa(t,EV["nurse"],sc["e"]+1))
        typed(d,"PLASTER CAST",780,1120,30,t,EV["castf"],a=nu*sm((t-EV["castf"])/0.3))
        card(d,"“I didn't know him.”",540,1250,fs=48,a=fa(t,EV["didnt"]-0.2,sc["e"]+1),fn="InstrumentSerif-Italic",fg=INK,bg=PAPER)
    hud.append(hd); return buf,hud,col,0.0
def s_years(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; col=[]
    grad(buf,[(0,(0.62,0.62,0.62)),(500,(0.80,0.78,0.74)),(501,(0.45,0.48,0.40)),(h,(0.30,0.32,0.27))])
    comp(buf,M().poly([(170,560),(170,330),(200,290),(270,270),(340,290),(370,330),(370,560)]),(0.70,0.68,0.64),sh=0.5)
    gr=M()
    for k in range(30): x=k*19; gr.poly([(x,600),(x+4,570-5*(k%3)),(x+8,600)])
    comp(buf,gr,(0.32,0.36,0.28),sh=0.2)
    fl=M()
    for k in range(5): fl.circ(240+k*14,560-6*(k%2),7)
    comp(buf,fl,(0.85,0.85,0.82),sh=0.2)
    def hd(d,t=t):
        tx(d,"THE",540,700,34,(60,58,55),1,fn=SERIF); tx(d,"UNKNOWN",540,780,52,(60,58,55),1,fn=HEAD); tx(d,"MAN",540,860,52,(60,58,55),1,fn=HEAD); tx(d,"1948",540,940,30,(60,58,55),1,fn=SERIF)
        for s,e,x,y,ang in (("A SPY?",EV["spy"],270,260,-6),("SUICIDE?",EV["suicide"],800,320,5),("A HEARTBROKEN\nLOVER?",EV["lover"],540,1200,-3)):
            card(d,s,x,y,fs=54,a=sm((t-e+0.1)/0.25),fn="BigShoulders-Bold",fg=INK,bg=PAPER,ang=ang,sc=poptime(t,e-0.1))
    hud.append(hd); return buf,hud,col,0.0
TREE=None
def _tree():
    g=np.random.default_rng(9); nodes=[(270,140,0,-1)]; edges=[]
    for gen in range(1,6):
        prev=[i for i,n in enumerate(nodes) if n[2]==gen-1]
        for p in prev:
            for c in range(int(g.integers(2,4))):
                x=nodes[p][0]+g.uniform(-200,200)/gen**0.6; y=140+gen*90+g.uniform(-15,15); nodes.append((min(max(x,20),520),y,gen,p)); edges.append((p,len(nodes)-1))
    return nodes,edges
TREE=_tree()
def s_dna(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; col=[]
    grad(buf,[(0,(0.04,0.10,0.14)),(h,(0.02,0.04,0.07))])
    ph_t=sm((t-EV["tree"]+0.4)/0.6); ph_n=sm((t-EV["webb"]+0.4)/0.6)
    a1=1-ph_t
    if t<EV["abbott"]-0.2:
        k=sm((t-EV["exhumed"]+0.3)/0.6)
        b0=np.zeros_like(buf); grad(b0,[(0,(0.55,0.55,0.55)),(520,(0.70,0.68,0.64)),(521,(0.35,0.30,0.25)),(h,(0.25,0.22,0.18))])
        comp(b0,M().poly([(170,560),(170,330),(200,290),(270,270),(340,290),(370,330),(370,560)]),(0.70,0.68,0.64),sh=0.5)
        hole=M().rect(130,600,410,600+220*k); comp(b0,hole,(0.18,0.14,0.10),sh=0.3)
        buf[:]=b0
    else:
        if a1>0.01:
            helix(buf,190,t,90,620,70,[(0.20,0.85,0.95),(0.98,0.45,0.70)],a=a1)
            comp(buf,M().circ(400,360,95),(0.85,0.92,0.95),sh=0.4,a=a1*0.25); comp(buf,M().circ(400,360,90),(0.10,0.18,0.22),sh=0,a=a1)
            comp(buf,M().pline([(330+i*3,330+20*math.sin(i*0.12+t)) for i in range(50)],3),(0.80,0.65,0.40),sh=0,rim=0,a=a1*sm((t-EV["hairs"])/0.4))
        if ph_t>0.01:
            nodes,edges=TREE; gt=cl((t-EV["tree"])/2.6); n_show=int(len(nodes)*gt)+1
            ln=M(); dt=M()
            for (p,c) in edges:
                if c<n_show: ln.line(nodes[p][:2],nodes[c][:2],1.4)
            for i,n in enumerate(nodes[:n_show]): dt.circ(n[0],n[1],5 if n[2]<5 else 3.5)
            comp(buf,ln,(0.35,0.70,0.85),sh=0,rim=0,a=ph_t*(1-ph_n*0.7)); comp(buf,dt,(0.75,0.92,1.0),sh=0,rim=0,a=ph_t*(1-ph_n*0.7))
            hl=sm((t-EV["announced"])/0.8)
            if hl>0:
                i=len(nodes)-1; path=[]
                while i>=0: path.append(nodes[i][:2]); i=nodes[i][3]
                comp(buf,M().pline(path,4),(1.0,0.80,0.25),sh=0,rim=0,a=hl*(1-ph_n*0.7)); rgrad(buf,*path[0],30,(1.0,0.8,0.3),0.8*hl*(1-ph_n))
        if ph_n>0:
            rgrad(buf,270,330,260,(0.20,0.45,0.60),0.25*ph_n)
    def hd(d,t=t):
        typed(d,"2021 · EXHUMED",540,200,40,t,EV["y2021"],a=fa(t,EV["y2021"],EV["abbott"]-0.3))
        typed(d,"DEREK ABBOTT · COLLEEN FITZPATRICK",540,200,28,t,EV["abbott"],a=fa(t,EV["abbott"],EV["tree"]-0.3),bg=(230,240,245))
        typed(d,"DNA FROM HAIRS IN THE PLASTER CAST",540,1250,28,t,EV["hairs"],a=fa(t,EV["hairs"],EV["tree"]-0.3),bg=(230,240,245))
        card(d,"~4,000 PEOPLE",540,1250,fs=56,a=fa(t,EV["k4"],EV["webb"]-0.4),fn="BigShoulders-Bold",fg=(20,30,40),bg=(140,220,240),torn=False,sc=poptime(t,EV["k4"]))
        typed(d,"JULY 2022",540,200,40,t,EV["y2022"],a=fa(t,EV["y2022"],EV["webb"]-0.4),bg=(230,240,245))
        a=sm((t-EV["webb"]+0.2)/0.4)
        if a>0.01:
            card(d,"CARL WEBB",540,560,fs=130,a=a,fn=HEAD,fg=(255,255,255),bg=(25,90,120),torn=False,sc=poptime(t,EV["webb"]-0.2),pad=(50,26))
            typed(d,"ELECTRICAL ENGINEER",540,760,36,t,EV["engineer"],bg=(230,240,245))
            typed(d,"MELBOURNE · BORN 1905",540,850,36,t,EV["melb"],bg=(230,240,245))
        stamp(d,"NOT OFFICIALLY CONFIRMED",540,280,54,sm((t-EV["notconf"])/0.15),-5,col=(230,90,80))
        card(d,"HOW HE DIED?",330,1060,fs=42,a=sm((t-EV["how"])/0.3),fn="BigShoulders-Bold",fg=INK,bg=PAPER,ang=-4)
        card(d,"THE CODE?",770,1080,fs=42,a=sm((t-EV["codew"])/0.3),fn="BigShoulders-Bold",fg=INK,bg=PAPER,ang=4)
    hud.append(hd)
    cm=sm((t-EV["abbott"]+0.4)/1.5)
    return buf,hud,col,cm
def s_end(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]; col=[]
    sea(buf,t,330,(0.03,0.03,0.05),(0.30,0.28,0.28),(0.10,0.10,0.12),(0.36,0.32,0.28),ysand=520)
    comp(buf,M().circ(400,150,26),(0.92,0.90,0.82),sh=0); rgrad(buf,400,150,90,(0.6,0.58,0.5),0.25)
    seawall(buf,-10,w+10,560,640,(0.28,0.26,0.24))
    comp(buf,M().rect(-5,640,w+5,h+5),(0.38,0.34,0.30),sh=0.3)
    st=t-sc["s"]; u=st/9.0
    px=120+u*420+30*math.sin(st*1.3); py=600-u*420+25*math.sin(st*2.1); ang=st*1.8
    comp(buf,M().poly(rot([(-30,-10),(30,-10),(30,10),(-30,10)],ang,px,py,1,max(0.2,abs(math.cos(st*2.4))))),(0.93,0.90,0.82),sh=0.4)
    tf=Lx("Tamam Shud. It is")[1]+0.4
    if t>tf: buf*=max(0.12,1-(t-tf)*0.9)
    def hd(d,t=t,tf=tf):
        typed(d,"NO NAME.",540,200,40,t,EV["noname2"],a=fa(t,EV["noname2"],EV["tamam3"]-0.3))
        typed(d,"A SECRET POCKET.",540,280,40,t,EV["secret2"],a=fa(t,EV["secret2"],EV["tamam3"]-0.3))
        typed(d,"TWO WORDS OF POETRY.",540,360,40,t,EV["poetry"],a=fa(t,EV["poetry"],EV["tamam3"]-0.3))
        a=fa(t,EV["tamam3"]-0.2,tf+0.2,0.3,0.4)
        tx(d,"Tamám Shud",540,420,120,(240,232,210),a,fn=SERIF,stroke=2)
        tx(d,"IT IS FINISHED.",540,560,44,(200,190,170),a*sm((t-EV["finished3"])/0.4),fn=TYPE)
        tx(d,"…BUT THE MYSTERY ISN'T.",540,650,44,(230,90,80),a*sm((t-EV["mystery"])/0.4),fn=TYPE)
        if t>tf:
            kk=t-tf; a=sm((kk-0.2)/0.6); lg=LOGO.resize((int(LOGO.width*0.5),int(LOGO.height*0.5)),Image.LANCZOS); al=np.array(lg); al[:,:,3]=(al[:,:,3]*a).astype(np.uint8)
            d._image.alpha_composite(Image.fromarray(al),(W//2-lg.width//2,640-lg.height//2)); B.txt(d,(W//2,1000),"ORBITHOS",B.CZ(72,600),(255,215,140,int(255*a)),anchor="mm",stroke=2)
    hud.append(hd); return buf,hud,col,0.0
SCN=dict(hook=s_hook,beach=s_beach,pockets=s_pockets,autopsy=s_autopsy,suitcase=s_suitcase,scrap=s_scrap,book=s_book,code=s_code,years=s_years,dna=s_dna,end=s_end)
BAND=(1-0.62*np.exp(-((yy-728)/78)**2))[...,None].astype(np.float32)
VIG=(1-0.45*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.022,(h,w,1)).astype(np.float32) for i in range(8)]
SEP=np.array([[0.05,0.04,0.035],[0.36,0.28,0.20],[0.70,0.60,0.46],[0.97,0.92,0.80]],np.float32)
def sepia(buf):
    L=np.clip(buf[...,0]*0.3+buf[...,1]*0.59+buf[...,2]*0.11,0,1.2)
    x=np.clip(L,0,1)*3; i=np.minimum(x.astype(np.int32),2); f=(x-i)[...,None]
    return SEP[i]*(1-f)+SEP[i+1]*f
def film(buf,t):
    g=np.random.default_rng(int(t*30)); fl=1+0.025*math.sin(t*23)+g.uniform(-0.015,0.015)
    buf=buf*fl
    for k in range(int(g.integers(0,3))):
        x=int(g.uniform(0,w)); a_=g.uniform(0.04,0.10); buf[:,x:x+1]+=a_*(1 if g.uniform()<0.5 else -1)
    return buf
def render_scene(t,sc):
    buf,hud,col,cm=SCN[sc["name"]](t,sc)
    toned=sepia(buf); out=toned*(1-cm)+buf*cm
    for f in col: f(out)
    return out,hud
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    buf,hud=render_scene(t,sc)
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    fl=0.0; dev=0.0
    if t>nb-0.14: fl=sm((t-(nb-0.14))/0.14)
    if t>=pb and t<pb+0.75: dev=1-sm((t-pb)/0.75); fl=max(fl,math.exp(-(t-pb)*14))
    if dev>0:
        k=dev; bl=cv2.GaussianBlur(buf,(0,0),1+4*k); buf=bl*k+buf*(1-k); buf=buf*(1-0.35*k)+0.55*k
    buf=np.clip(buf,0,1.3)
    buf=film(buf,t)*VIG*BAND+GR[int(t*30)%8]
    buf=buf*(1-fl)+fl*1.0
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    hk=(1-fl)*(1-dev*0.8)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*hk).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
TOTAL=B.TOTAL
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
