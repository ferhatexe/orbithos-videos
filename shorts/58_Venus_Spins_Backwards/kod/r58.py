import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid58")
for p in ["/home/claude/vid58","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= ukiyo-e woodblock print =================
WASHI=(0.94,0.89,0.77); PRU=(0.13,0.25,0.42); LBLUE=(0.55,0.68,0.76); VERM=(0.82,0.27,0.16); OCH=(0.90,0.68,0.30)
SUMI=(0.12,0.11,0.10); PINK=(0.93,0.72,0.64); OLIVE=(0.47,0.48,0.30); SKYT=(0.86,0.42,0.18); SKYB=(0.98,0.86,0.56)
PALE=(0.97,0.90,0.66); GREY=(0.55,0.55,0.55); LEAD=(0.52,0.54,0.58)
PX0,PX1,PY0,PY1=18,522,18,672      # printed picture area; below = indigo sea register for subtitles
_g=np.random.default_rng(58)
_gr=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),sigmaX=22,sigmaY=0.7); _gr/=_gr.std()
_fb=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),0.8); _fb/=_fb.std()
_bl=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),18); _bl/=_bl.std()
GRAIN=(1+0.035*_gr+0.02*_fb+0.025*_bl)[...,None].astype(np.float32)
def fill(buf,m,col,a=1.0): comp(buf,m,col,sh=0,rim=0,a=a)
def key(buf,m,th=2,a=1.0):
    """sumi keyline around a shape"""
    A=m.f() if isinstance(m,M) else m
    e=np.clip(A-cv2.erode(A,np.ones((2*th+1,2*th+1),np.uint8)),0,1); fill(buf,e,SUMI,0.92*a)
def blk(buf,m,col,th=2,a=1.0,reg=(1,1)):
    """one colour block printed slightly off-register, then the key block"""
    A=m.f(); A2=np.roll(np.roll(A,reg[1],0),reg[0],1); fill(buf,A2,col,a); key(buf,A,th,a)
def bokashi(buf,m,c0,c1,y0,y1,a=1.0):
    A=m.f() if isinstance(m,M) else m; k=np.clip((yy-y0)/(y1-y0),0,1)[...,None]
    col=np.array(c0,np.float32)*(1-k)+np.array(c1,np.float32)*k; buf+=(col-buf)*(A*a)[...,None]
def paper():
    b=np.empty((h,w,3),np.float32); b[:]=WASHI; return b
def kasumi(buf,x0,x1,y,hh,col=(0.97,0.93,0.88),a=1.0,seed=0):
    """stylised mist band with scalloped edges"""
    m=M(); m.rect(x0+hh,y-hh/2,x1-hh,y+hh/2); m.circ(x0+hh,y,hh/2); m.circ(x1-hh,y,hh/2)
    g=np.random.default_rng(seed)
    for x in np.arange(x0+hh,x1-hh,hh*0.9): m.circ(x,y-hh/2+2,hh*0.32); m.circ(x+hh*0.45,y+hh/2-2,hh*0.30)
    A=m.f(); fill(buf,A,col,a); bokashi(buf,A*a*0.5,PINK,col,y-hh/2,y+hh/2); key(buf,A,1,0.5*a)
def sundisc(buf,x,y,r,a=1.0):
    fill(buf,cv2.GaussianBlur(M().circ(x,y,r*2.0).f(),(0,0),r*0.5),(1.0,0.86,0.45),0.55*a)
    m=M().circ(x,y,r); blk(buf,m,VERM,2,a)
def venus(buf,x,y,r,sun_dir=None,flag=None,tilt=0.0):
    m=M().circ(x,y,r); A=m.f(); fill(buf,A,OCH)
    for k in range(-4,5):
        yc=y+k*r*0.22; band=M().ell(x+r*0.15*math.sin(k*1.7+tilt),yc,r*0.95,r*0.05+r*0.03*(k%2)).f()*A
        fill(buf,band,PALE,0.9)
    if sun_dir is not None:
        dx,dy=sun_dir; dd=((xx-x)*dx+(yy-y)*dy)/r; sh=np.clip(-dd*3+0.15,0,1)*A; fill(buf,sh,PRU,0.72)
    key(buf,A,2)
    if flag is not None:
        an=flag; px,py=x+math.cos(an)*r,y+math.sin(an)*r; qx,qy=x+math.cos(an)*(r+26),y+math.sin(an)*(r+26)
        fill(buf,M().line((px,py),(qx,qy),3),SUMI)
        nx,ny=-math.sin(an),math.cos(an); f=M().poly([(qx,qy),(qx-math.cos(an)*12+nx*16,qy-math.sin(an)*12+ny*16),(qx-math.cos(an)*12,qy-math.sin(an)*12)]); blk(buf,f,VERM,1)
def mountains(buf,t=0.0):
    fill(buf,M().rect(PX0,PY0,PX1,PY1),SKYB); bokashi(buf,M().rect(PX0,PY0,PX1,420),SKYT,SKYB,PY0,420)
    far=[(PX0,420)]+[(x,402-34*math.exp(-((x-330)/90)**2)-10*math.sin(x/27)) for x in range(PX0,PX1+8,8)]+[(PX1,700),(PX0,700)]
    m=M().poly(far); fill(buf,m,LBLUE); bokashi(buf,m,PRU,LBLUE,300,440); key(buf,m,2)
    vol=[(120,520),(250,330),(292,322),(420,520)]; m=M().poly(vol); fill(buf,m,PRU); bokashi(buf,m,SUMI,PRU,320,420,0.7); key(buf,m,2)
    for k in range(5): fill(buf,M().line((262+k*6,330),(200+k*30,500),2),LBLUE,0.6)
    pl=[(PX0,520)]+[(x,505+8*math.sin(x/40)) for x in range(PX0,PX1+8,8)]+[(PX1,PY1),(PX0,PY1)]
    m=M().poly(pl); fill(buf,m,OCH); bokashi(buf,m,OCH,(0.62,0.38,0.16),505,PY1); key(buf,m,2)
    for k in range(7):
        y0=545+k*18; pts=[(x,y0+5*math.sin(x/33+k)) for x in range(PX0+10,PX1-10,6)]
        fill(buf,M().pline(pts,2),(0.55,0.32,0.14),0.8)
def frame(buf):
    """paper margin, keyline border and the indigo seigaiha register"""
    m=np.ones((h,w),np.float32); m[PY0:PY1,PX0:PX1]=0; fill(buf,m,WASHI)
    cv2.rectangle(buf,(PX0,PY0),(PX1,PY1),SUMI,3)
    buf[PY1+10:h-10,PX0:PX1]=SEI[PY1+10:h-10,PX0:PX1]
    cv2.rectangle(buf,(PX0,PY1+10),(PX1,h-10),SUMI,3)
def _sei():
    b=np.empty((h,w,3),np.float32); b[:]=(0.10,0.17,0.30)
    r=26
    for j,y in enumerate(range(PY1,h+r,r//2)):
        off=(r if j%2 else 0)
        for x in range(-r,w+r,2*r):
            for k in (1.0,0.72,0.44):
                cv2.circle(b,(x+off,y),int(r*k),(0.16,0.25,0.40),2,cv2.LINE_AA)
    return b
SEI=_sei()
# vertical title cartouche + seal
def cartouche(d,a=1.0):
    x0,y0,x1,y1=900,62,990,400; A=int(255*a)
    d.rectangle((x0,y0,x1,y1),fill=(248,236,196,A),outline=(25,22,20,A),width=4); d.rectangle((x0+8,y0+8,x1-8,y1-8),outline=(25,22,20,A),width=2)
    f=ImageFont.truetype(P.FD+"YoungSerif-Regular.ttf",50)
    for i,ch in enumerate("VENUS"): d.text(((x0+x1)/2,y0+50+i*60),ch,font=f,fill=(25,22,20,A),anchor="mm")
    sx,sy=945,450; d.rectangle((sx-34,sy-34,sx+34,sy+34),fill=(196,52,36,int(230*a)))
    for k in range(3): d.rectangle((sx-22+k*15,sy-22,sx-14+k*15,sy+22),fill=(250,230,210,int(220*a)))
# ================= HUD =================
_IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(P.FD+n,s)
    return _IF[k]
def title(d,s,y=1255,fs=68,a=1.0,sc=1.0,col=(25,22,20)):
    """printed title cartouche (pale yellow block, double keyline)"""
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f("Lora-Bold.ttf",n)
    while f.getlength(s)>820 and n>20: n-=4; f=_f("Lora-Bold.ttf",n)
    tw=f.getlength(s); px,py=n*0.6,n*0.42; x0,x1=W/2-tw/2-px,W/2+tw/2+px; y0,y1=y-n*0.5-py,y+n*0.5+py; A=int(255*a)
    d.rectangle((x0+7,y0+8,x1+7,y1+8),fill=(25,22,20,int(120*a)))
    d.rectangle((x0,y0,x1,y1),fill=(248,236,196,A),outline=(25,22,20,A),width=4); d.rectangle((x0+7,y0+7,x1-7,y1-7),outline=(25,22,20,int(200*a)),width=2)
    d.text((W/2,y+2),s,font=f,fill=col+(A,),anchor="mm")
def tag(d,s,x,y,fs=40,a=1.0,sc=1.0,bg=(196,52,36),fg=(250,240,220)):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f("Lora-Bold.ttf",n); tw=f.getlength(s); px,py=n*0.5,n*0.35
    d.rectangle((x-tw/2-px,y-n*0.5-py,x+tw/2+px,y+n*0.5+py),fill=bg+(int(240*a),),outline=(25,22,20,int(255*a)),width=3)
    d.text((x,y+1),s,font=f,fill=fg+(int(255*a),),anchor="mm")
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= shots =================
def s_hook(t):
    b=paper(); k=sm(t/40.0)
    sx,sy=110,505-30*sm((t+1)/7)
    mountains(b,t);
    sundisc(b,sx,sy,34)
    pl=[(PX0,520)]+[(x,505+8*math.sin(x/40)) for x in range(PX0,PX1+8,8)]+[(PX1,PY1),(PX0,PY1)]
    m=M().poly(pl); fill(b,m,OCH); bokashi(b,m,OCH,(0.62,0.38,0.16),505,PY1); key(b,m,2)
    for k in range(7):
        y0=545+k*18; pts=[(x,y0+5*math.sin(x/33+k)) for x in range(PX0+10,PX1-10,6)]; fill(b,M().pline(pts,2),(0.55,0.32,0.14),0.8)
    kasumi(b,PX0-40+((t*6)%30),300,190,30,seed=1); kasumi(b,250-((t*5)%30),PX1+40,250,26,seed=2); kasumi(b,PX0-20,220,440,22,seed=3)
    frame(b)
    def hd(d,t=t):
        cartouche(d)
        tag(d,"WEST",220,880,38,a=ap(t,EV["west"]-0.2,S("hook")["e"]+1),sc=pop(t,EV["west"]-0.3))
        title(d,"THE SUN RISES IN THE WEST",1255,58,a=ap(t,EV["west"]-0.2,EV["back"]-0.3),sc=pop(t,EV["west"]-0.3))
        title(d,"SPINS BACKWARDS",1255,70,a=ap(t,EV["back"]-0.1,99),sc=pop(t,EV["back"]-0.2))
    return b,[hd]
def orbit_base(b,cx=270,cy=300,R=150):
    fill(b,M().rect(PX0,PY0,PX1,PY1),(0.11,0.18,0.31))
    g=np.random.default_rng(4)
    for _ in range(70): fill(b,M().circ(g.uniform(PX0,PX1),g.uniform(PY0,PY1),g.uniform(0.8,2.0)),PALE,0.8)
    for k in range(72):
        a0=k*2*math.pi/72
        if k%2==0: fill(b,M().line((cx+math.cos(a0)*R,cy+math.sin(a0)*R),(cx+math.cos(a0+0.05)*R,cy+math.sin(a0+0.05)*R),2.5),LBLUE)
    sundisc(b,cx,cy,44)
def sim(b,D,cx=270,cy=300,R=150,shade=False,th0=math.pi*0.5,ph0=-math.pi*0.5):
    th=th0-2*math.pi*D/224.7; ph=ph0+2*math.pi*D/243.0     # screen: orbit counter-clockwise, spin clockwise (retrograde)
    vx,vy=cx+math.cos(th)*R,cy+math.sin(th)*R
    sd=(cx-vx,cy-vy); n=math.hypot(*sd); sd=(sd[0]/n,sd[1]/n)
    venus(b,vx,vy,46,sd if shade else None,ph)
    return vx,vy,th,ph
def s_spin(t):
    b=paper(); orbit_base(b)
    D=243*sm((t-EV["turn"]+0.2)/(EV["year"]-EV["turn"]-0.4)) if t>EV["turn"]-0.2 else 0.0
    vx,vy,th,ph=sim(b,D)
    # progress arcs
    if D>0:
        cv2.ellipse(b,(int(vx*16),int(vy*16)),(int(62*16),int(62*16)),0,-90,-90+360*min(D,243)/243,VERM,4,cv2.LINE_AA,4)
    frame(b)
    def hd(d,t=t,D=D):
        cartouche(d)
        a=ap(t,EV["turn"]-0.2,99)
        tag(d,f"SPIN  {int(min(D,243)):3d} / 243 DAYS",540,1210,36,a=a,bg=(196,52,36))
        yr=min(D,224.7); done=D>=224.7; yr=225 if done else yr
        tag(d,f"ORBIT {int(yr):3d} / 225 DAYS",540,1290,36,a=ap(t,EV["trip"]-0.3,99),bg=(30,60,100) if not done else (60,110,60))
        if done: tag(d,"ONE YEAR DONE — SPIN NOT FINISHED",540,140,30,a=ap(t,EV["longer"]-0.2,99),bg=(248,236,196),fg=(25,22,20))
        title(d,"A DAY LONGER THAN A YEAR",1120,52,a=ap(t,EV["year"]-0.3,99),sc=pop(t,EV["year"]-0.4))
    return b,[hd]
def s_twist(t):
    b=paper(); orbit_base(b)
    t0=EV["sunrise"]-0.3; D=234*sm((t-t0)/(EV["two"]+0.9-t0)) if t>t0 else 0.0
    vx,vy,th,ph=sim(b,D,shade=True,ph0=-math.pi*0.5+2.1)
    alpha=lambda DD: (( -math.pi*0.5+2.1+2*math.pi*DD/243.0) - (math.pi*0.5-2*math.pi*DD/224.7+math.pi))
    n=0
    for DD in np.arange(0,D,0.5):
        a1=alpha(DD)%(2*math.pi); a2=alpha(DD+0.5)%(2*math.pi)
        if a1<math.pi*1.5<=a2 or (a1>a2 and (a1<math.pi*1.5 or a2>=math.pi*1.5)): n+=1
    frame(b)
    def hd(d,t=t,D=D,n=n):
        cartouche(d)
        title(d,"THE TWIST",1255,74,a=ap(t,EV["twist"]-0.2,EV["sunrise"]-0.2),sc=pop(t,EV["twist"]-0.3))
        tag(d,f"DAY {int(D):3d}",540,140,34,a=ap(t,EV["sunrise"]-0.3,99),bg=(248,236,196),fg=(25,22,20))
        title(d,"SUNRISE TO SUNRISE: 117 DAYS",1255,54,a=ap(t,EV["d117"]-0.3,EV["almost"]),sc=pop(t,EV["d117"]-0.4))
        title(d,f"SUNRISES THIS YEAR: {n}" if n<2 else "ALMOST 2 SUNRISES A YEAR",1255,56,a=ap(t,EV["almost"]-0.2,99),sc=pop(t,EV["almost"]-0.3))
    return b,[hd]
def s_clouds(t):
    b=paper(); fill(b,M().rect(PX0,PY0,PX1,PY1),SKYB); bokashi(b,M().rect(PX0,PY0,PX1,PY1),SKYT,SKYB,PY0,600)
    for i in range(7):
        y=120+i*62; sp=(160+40*(i%3)); off=((t*sp+i*97)%(PX1-PX0+400))-200
        kasumi(b,PX0+off-260,PX0+off+20,y,30-2*i%3,col=(0.98,0.94,0.86) if i%2 else PINK,seed=i)
        for k in range(3): fill(b,M().line((PX0+off-300-k*40,y-8+k*8),(PX0+off-270-k*40,y-8+k*8),2),SUMI,0.6)
    hot=sm((t-EV["beneath"]+0.4)/0.6)
    if hot>0:
        pl=[(PX0,PY1-150*hot)]+[(x,PY1-150*hot+6*math.sin(x/30)) for x in range(PX0,PX1+8,8)]+[(PX1,PY1),(PX0,PY1)]
        m=M().poly(pl); fill(b,m,(0.55,0.20,0.10)); key(b,m,2)
        for k in range(9):
            x=PX0+30+k*55; y0=PY1-150*hot; fl=6*math.sin(t*7+k)
            fm=M().poly([(x-12,y0+4),(x+fl,y0-46-10*math.sin(t*5+k)),(x+12,y0+4)]); blk(b,fm,VERM,1)
            fm=M().poly([(x-6,y0+4),(x+fl*0.6,y0-24),(x+6,y0+4)]); fill(b,fm,OCH)
        lk=sm((t-EV["lead"]+0.2)/1.2)
        lx,ly=380,PY1-150*hot+2
        lm=M().poly([(lx-36-14*lk,ly),(lx-30+8*lk,ly-34*(1-lk)-6),(lx+30-8*lk,ly-34*(1-lk)-6),(lx+36+14*lk,ly)]); fill(b,lm,LEAD); key(b,lm,2)
        if lk>0: fill(b,M().ell(lx,ly+4,40+30*lk,6*lk+1),LEAD);
    frame(b)
    def hd(d,t=t):
        cartouche(d)
        title(d,"CLOUDS LAP VENUS IN ~4 DAYS",1255,54,a=ap(t,EV["clouds"]-0.2,EV["beneath"]-0.2),sc=pop(t,EV["clouds"]-0.3))
        title(d,"ABOUT 460 °C",1255,80,a=ap(t,EV["d460"]-0.3,EV["lead"]-0.1),sc=pop(t,EV["d460"]-0.4))
        title(d,"HOT ENOUGH TO MELT LEAD",1255,60,a=ap(t,EV["lead"]-0.2,99),sc=pop(t,EV["lead"]-0.3))
        tag(d,"LEAD",600,900,36,a=ap(t,EV["lead"]-0.2,99),bg=(80,84,92))
    return b,[hd]
def s_why(t):
    b=paper(); fill(b,M().rect(PX0,PY0,PX1,PY1),(0.11,0.18,0.31))
    g=np.random.default_rng(4)
    for _ in range(70): fill(b,M().circ(g.uniform(PX0,PX1),g.uniform(PY0,PY1),g.uniform(0.8,2.0)),PALE,0.8)
    ki=sm((t-EV["impact"]+0.6)/0.6); hit=EV["impact"]
    if t<hit+0.1:
        x,y=PX0+40+200*ki,120+170*ki
        tail=M().poly([(x-90,y-80),(x+4,y-14),(x-14,y+6)]); fill(b,tail,PALE,0.8); m=M().circ(x,y,16); blk(b,m,GREY,2)
    rot=(t-S("why")["s"])*0.6*(1 if t<hit else -1)
    venus(b,300,360,110,None,-math.pi/2+rot*2,tilt=rot)
    if t>hit:
        u=t-hit
        for i in range(10):
            an=-2.4+i*0.18; r=110+90*u; fill(b,M().circ(300+math.cos(an)*r,360+math.sin(an)*r,4*(1-cl(u/1.5))+0.5),OCH,cl(1-u/1.5))
    kt=fa(t,EV["tides"]-0.2,99)
    if kt>0:
        bm=M().ell(300,360,150+8*math.sin(t*3),126); A=np.clip(bm.f()-M().circ(300,360,112).f(),0,1); fill(b,A,LBLUE,0.55*kt); key(b,bm,1,0.6*kt)
    # arrows showing the spin direction
    for sgn,y in ((1,180),):
        a0=-2.6 if t<hit else -0.6; a1=-0.6 if t<hit else -2.6
        pts=[(300+math.cos(a)*140,360+math.sin(a)*140) for a in np.linspace(a0,a1,20)]
        fill(b,M().pline(pts,4),VERM); p2,p1=pts[-1],pts[-3]; an=math.atan2(p2[1]-p1[1],p2[0]-p1[0])
        fill(b,M().poly([(p2[0]+math.cos(an)*14,p2[1]+math.sin(an)*14),(p2[0]+math.cos(an+2.4)*14,p2[1]+math.sin(an+2.4)*14),(p2[0]+math.cos(an-2.4)*14,p2[1]+math.sin(an-2.4)*14)]),VERM)
    frame(b)
    def hd(d,t=t):
        cartouche(d)
        title(d,"WHY BACKWARDS?",1255,74,a=ap(t,EV["why"]-0.2,EV["impact"]-0.2),sc=pop(t,EV["why"]-0.3))
        tag(d,"NOBODY KNOWS FOR SURE",540,150,36,a=ap(t,EV["nobody"],99),bg=(248,236,196),fg=(25,22,20))
        title(d,"GIANT IMPACTS?",1255,74,a=ap(t,EV["impact"]-0.2,EV["tides"]-0.1),sc=pop(t,EV["impact"]-0.3))
        title(d,"OR ATMOSPHERIC TIDES?",1255,64,a=ap(t,EV["tides"]-0.1,99),sc=pop(t,EV["tides"]-0.2))
    return b,[hd]
def s_end(t):
    b=paper(); mountains(b,t)
    sx,sy=430,470+30*sm((t-S("why")["e"])/4)
    sundisc(b,sx,sy,34)
    pl=[(PX0,520)]+[(x,505+8*math.sin(x/40)) for x in range(PX0,PX1+8,8)]+[(PX1,PY1),(PX0,PY1)]
    m=M().poly(pl); fill(b,m,OCH); bokashi(b,m,OCH,(0.62,0.38,0.16),505,PY1); key(b,m,2)
    for k in range(7):
        y0=545+k*18; pts=[(x,y0+5*math.sin(x/33+k)) for x in range(PX0+10,PX1-10,6)]; fill(b,M().pline(pts,2),(0.55,0.32,0.14),0.8)
    kasumi(b,PX0-40,300,190,30,seed=1); kasumi(b,250,PX1+40,250,26,seed=2)
    frame(b)
    def hd(d,t=t):
        cartouche(d)
        tag(d,"EAST",860,880,38,a=ap(t,EV["sunset"]-0.2,99),sc=pop(t,EV["sunset"]-0.3))
        title(d,"BE PATIENT",1255,80,a=ap(t,EV["patient"]-0.2,99),sc=pop(t,EV["patient"]-0.3))
    return b,[hd]
TR=0.38; TOTAL=B.TOTAL; LOOPD=0.66
SHOTS=[(0.0,s_hook),(S("spin")["s"],s_spin),(S("twist")["s"],s_twist),(S("hell")["s"],s_clouds),(S("why")["s"],s_why),(Lx("So if you're")[0]-0.3,s_end)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
_KB=[]
def mist(b1,b2,u):
    """kasumi bands slide across, hide the old print, slide away from the new one"""
    out=(b1 if u<0.5 else b2).copy(); n=7; hh=(PY1-PY0)/n
    for i in range(n):
        y=PY0+hh*(i+0.5); d=1 if i%2 else -1; k=sm(u*2) if u<0.5 else 1-sm((u-0.5)*2)
        cover=k*(PX1-PX0+2*hh+60)
        if d>0: x0,x1=PX0-hh-30,PX0-hh-30+cover
        else: x0,x1=PX1+hh+30-cover,PX1+hh+30
        if x1-x0>5: kasumi(out,x0,x1,y,hh*1.18,col=(0.97,0.93,0.88) if i%2 else (0.96,0.86,0.80),seed=i)
    frame(out); return out
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None:
        buf,hud=SHOTS[i][1](t); hk=1.0
    else:
        fa_,fb_,ta,tb,u=pair
        if u<0.5: b1,hud=fa_(ta); buf=mist(b1,b1,u)
        else: b2,hud=fb_(tb); buf=mist(b2,b2,u)
        hk=cl(abs(u-0.5)*2.4)
    buf=np.clip(buf,0,1.1)*GRAIN
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1:
        a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
        o3=Image.new("RGBA",(W,H),(0,0,0,0)); cartouche(ImageDraw.Draw(o3)); ov.alpha_composite(o3)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
