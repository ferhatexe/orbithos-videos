import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid61")
for p in ["/home/claude/vid61","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= watercolour on cold-press paper =================
PAPER=np.array((0.975,0.96,0.925),np.float32)
_g=np.random.default_rng(61)
def _nz(s): n=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),s); return n/n.std()
_v1,_v2,_v3=_nz(1.2),_nz(4),_nz(14)
VAL=np.clip(0.5+0.10*_v1+0.16*_v2+0.08*_v3,0,1).astype(np.float32)            # paper valleys collect pigment
PTEX=(1+0.018*_v1+0.012*_v2)[...,None].astype(np.float32)
WX=(xx+2.6*_nz(6)).astype(np.float32); WY=(yy+2.6*_nz(6)).astype(np.float32)
BH=690                                   # painted area above, dark indigo register below
def paper(): b=np.empty((h,w,3),np.float32); b[:]=PAPER; return b
def wc(buf,m,col,dens=0.85,edge=0.6,gran=0.5,soft=1.6,warp=True,a=1.0):
    """one transparent wash: soft wobbly edge, pigment pooled at the rim, granulating in the paper tooth"""
    A=m.f() if isinstance(m,M) else m
    if warp: A=cv2.remap(A,WX,WY,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    if soft>0: A=cv2.GaussianBlur(A,(0,0),soft)
    E=np.clip(A-cv2.GaussianBlur(A,(0,0),5),0,1)
    D=np.clip(A*dens*(1+edge*2.2*E)*(1-gran*0.35+gran*0.7*VAL),0,1)*a
    c=np.array(col,np.float32); buf*=1-D[...,None]*(1-c)
def wcg(buf,m,c0,c1,y0,y1,dens=0.85,gran=0.4,soft=2.0,a=1.0):
    A=m.f() if isinstance(m,M) else m
    A=cv2.GaussianBlur(cv2.remap(A,WX,WY,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT),(0,0),soft)
    k=np.clip((yy-y0)/(y1-y0),0,1)[...,None]; c=np.array(c0,np.float32)*(1-k)+np.array(c1,np.float32)*k
    D=np.clip(A*dens*(1-gran*0.35+gran*0.7*VAL),0,1)*a; buf*=1-D[...,None]*(1-c)
def lift(buf,m,a=0.9,soft=2.0):
    A=(m.f() if isinstance(m,M) else m)
    if soft>0: A=cv2.GaussianBlur(A,(0,0),soft)
    A=A*a; buf+=(PAPER-buf)*A[...,None]
def pencil(buf,pts,a=0.5,th=1.2):
    m=M().pline(pts,th); A=m.f()*a*(0.7+0.3*VAL); buf*=1-A[...,None]*0.55
def brush(buf,p0,p1,col,th=6,dens=0.8):
    wc(buf,M().line(p0,p1,th),col,dens,0.5,0.4,1.0)
def arrowhead(buf,p0,p1,col,sz=12,dens=0.85):
    a=math.atan2(p1[1]-p0[1],p1[0]-p0[0])
    wc(buf,M().poly([(p1[0]+math.cos(a)*sz,p1[1]+math.sin(a)*sz),(p1[0]+math.cos(a+2.4)*sz,p1[1]+math.sin(a+2.4)*sz),(p1[0]+math.cos(a-2.4)*sz,p1[1]+math.sin(a-2.4)*sz)]),col,dens,0.4,0.3,0.6)
def _band():
    b=paper(); top=[(x,BH-6*math.sin(x/37)-5*math.sin(x/11+1)) for x in range(-10,w+20,10)]
    wc(b,M().poly(top+[(w+20,h),(-10,h)]),(0.16,0.20,0.36),0.95,0.5,0.6,2.2)
    wc(b,M().poly(top+[(w+20,h),(-10,h)]),(0.45,0.50,0.70),0.6,0.3,0.6,3.0)
    A=M().poly(top+[(w+20,h),(-10,h)]).f(); A=cv2.GaussianBlur(cv2.remap(A,WX,WY,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT),(0,0),2.2)
    return b,A
BAND,BANDA=_band()
# ---- palette (transmittance) ----
ORNG=(0.97,0.70,0.42); RUST=(0.80,0.42,0.26); BRN=(0.55,0.38,0.30); DUSK=(0.70,0.58,0.62); BLUEG=(0.62,0.78,0.95)
SKYB=(0.62,0.80,0.97); GRN=(0.65,0.82,0.55); INK=(0.30,0.28,0.32); YEL=(0.99,0.88,0.55); RED=(0.95,0.50,0.40)
def mars_land(b,t,glow=1.0,dark=0.0,sunx=270,suny=432,sunr=15):
    sky=M().rect(0,0,w,BH)
    wcg(b,sky,(0.88,0.62,0.45),(0.98,0.80,0.55),0,500,0.9,0.5,3.0)
    if dark>0: wcg(b,sky,(0.45,0.40,0.55),(0.80,0.70,0.72),0,520,0.85*dark,0.3,3.0)
    if glow>0:
        gm=np.exp(-(((xx-sunx)/170)**2+((yy-suny)/135)**2)).astype(np.float32)
        lift(b,gm,0.75*glow,0); wc(b,gm,(0.50,0.68,0.95),0.95*glow,0.0,0.2,0,False)
        g2=np.exp(-(((xx-sunx)/60)**2+((yy-suny)/50)**2)).astype(np.float32); lift(b,g2,0.6*glow,0)
    lift(b,M().circ(sunx,suny,sunr),1.0,0.8)
    far=[(x,452-22*math.exp(-((x-380)/70)**2)-6*math.sin(x/23)) for x in range(-10,w+20,10)]
    wc(b,M().poly(far+[(w+20,BH),(-10,BH)]),DUSK,0.75,0.6,0.5,1.6)
    near=[(x,500+10*math.sin(x/40)+4*math.sin(x/13)) for x in range(-10,w+20,10)]
    wc(b,M().poly(near+[(w+20,BH),(-10,BH)]),RUST,0.85,0.7,0.7,1.6)
    wc(b,M().poly(near+[(w+20,BH),(-10,BH)]),BRN,0.45,0.5,0.8,2.5)
    for k in range(9): wc(b,M().ell(40+k*58,560+((k*37)%60),10+(k%3)*5,5),BRN,0.8,0.6,0.6,1.0)
def rover(b,x,y,s,a=1.0):
    m=M(); m.rect(x-60*s,y-46*s,x+50*s,y-18*s); m.rect(x+30*s,y-120*s,x+36*s,y-46*s); m.rect(x+18*s,y-138*s,x+52*s,y-118*s)
    m.rect(x-50*s,y-62*s,x-20*s,y-46*s); m.line((x-60*s,y-18*s),(x+50*s,y-14*s),5*s)
    for wx in (-52,-6,40): m.circ(x+wx*s,y-4*s,11*s)
    wc(b,m,INK,0.92*a,0.5,0.4,1.0)
    for wx in (-52,-6,40): lift(b,M().circ(x+wx*s,y-4*s,4*s),0.6*a,0.6)
def earth_land(b,t,sunset=0.0):
    sky=M().rect(0,0,w,BH)
    if sunset<1: wcg(b,sky,(0.45,0.66,0.92),(0.80,0.90,0.99),0,480,0.9*(1-sunset),0.3,3)
    if sunset>0: wcg(b,sky,(0.55,0.42,0.62),(0.99,0.62,0.35),0,480,0.9*sunset,0.3,3); lift(b,M().circ(270,455,26),0.95*sunset,1.5); wc(b,M().circ(270,455,26),YEL,0.6*sunset,0.2,0.2,1)
    hills=[(x,470+14*math.sin(x/60)+5*math.sin(x/17)) for x in range(-10,w+20,10)]
    wc(b,M().poly(hills+[(w+20,BH),(-10,BH)]),GRN if sunset<0.5 else (0.45,0.40,0.45),0.85,0.6,0.6,1.6)
    for k in range(6): wc(b,M().ell(60+k*90,470+14*math.sin((60+k*90)/60)-24,14,30),(0.40,0.60,0.40) if sunset<0.5 else (0.30,0.28,0.32),0.85,0.5,0.5,1.2)
# ================= HUD =================
_IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(P.FD+n,s)
    return _IF[k]
def ttl(d,s,y=200,fs=82,a=1.0,sc=1.0,col=(46,32,40)):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc*1.35); f=_f("InstrumentSerif-Italic.ttf",n)
    while f.getlength(s)>960 and n>20: n-=4; f=_f("InstrumentSerif-Italic.ttf",n)
    d.text((W/2,y),s,font=f,fill=(255,250,240,int(150*a)),anchor="mm",stroke_width=6,stroke_fill=(255,250,240,int(110*a)))
    d.text((W/2,y),s,font=f,fill=col+(int(255*a),),anchor="mm")
def note(d,s,x,y,fs=46,a=1.0,col=(50,40,60)):
    if a<=0.01: return
    d.text((x,y),s,font=_f("NothingYouCouldDo-Regular.ttf",int(fs*1.3)),fill=col+(int(255*a),),anchor="mm",stroke_width=3,stroke_fill=(255,250,240,int(160*a)))
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= shots =================
def s_hook(t):
    b=paper(); mars_land(b,t,glow=0.4+0.6*sm((t-EV["sunsets"]+0.4)/0.8)); rover(b,150,640,1.0*sm((t-EV["curio"]+0.5)/0.6)+0.001,a=sm((t-EV["curio"]+0.5)/0.6))
    def hd(d,t=t):
        ttl(d,"orange days,",170,92,a=ap(t,EV["orange"]-0.2,EV["curio"]),sc=pop(t,EV["orange"]-0.3))
        ttl(d,"blue sunsets",290,104,a=ap(t,EV["sunsets"]-0.1,EV["curio"]),sc=pop(t,EV["sunsets"]-0.2),col=(40,70,130))
        ttl(d,"Curiosity · 2015",200,84,a=ap(t,EV["curio"],99),sc=pop(t,EV["curio"]-0.1))
        note(d,"Gale Crater",760,1010,50,a=ap(t,EV["gale"]-0.2,99))
    return b,[hd]
MOL=[(_g.uniform(30,510),_g.uniform(60,430)) for _ in range(26)]
def s_eday(t):
    b=paper(); earth_land(b,t,0.0)
    for i,(x,y) in enumerate(MOL):
        wc(b,M().circ(x,y,4),INK,0.6,0.4,0.3,0.8)
        if t>EV["scatter"]-0.3+i*0.03:
            for k in range(3):
                a=i*1.7+k*2.1; L=26
                brush(b,(x+math.cos(a)*7,y+math.sin(a)*7),(x+math.cos(a)*L,y+math.sin(a)*L),(0.50,0.68,0.95),2.5,0.7)
    sx=60; brush(b,(sx-60,120),(MOL[0][0],MOL[0][1]),YEL,5,0.7)
    def hd(d,t=t):
        ttl(d,"Earth",200,96,a=ap(t,EV["earth"]-0.2,EV["molec"]),sc=pop(t,EV["earth"]-0.3))
        note(d,"air molecules",540,200,52,a=ap(t,EV["molec"],99))
        ttl(d,"blue goes everywhere",330,74,a=ap(t,EV["scatter"],99),sc=pop(t,EV["scatter"]-0.1),col=(40,70,130))
    return b,[hd]
def s_esunset(t):
    b=paper(); earth_land(b,t,sm((t-EV["esunset"]+0.4)/0.8))
    k=sm((t-EV["crosses"]+0.3)/1.2)
    for i in range(5):
        y=200+i*36; x1=60+400*k
        brush(b,(40,y),(x1,y+20*k),(0.98,0.60,0.40) if i%2 else YEL,4,0.75)
        if k>0.3 and i<3: brush(b,(150+i*80,y+8),(150+i*80+10,y-30),(0.55,0.70,0.95),2.5,0.6*fa(t,EV["away"]-0.6,99))
    def hd(d,t=t):
        ttl(d,"Earth sunset",200,92,a=ap(t,EV["esunset"]-0.2,EV["away"]),sc=pop(t,EV["esunset"]-0.3))
        ttl(d,"the blue is scattered away",200,66,a=ap(t,EV["away"]-0.2,EV["reds"]),sc=pop(t,EV["away"]-0.3))
        ttl(d,"reds & oranges stay",200,80,a=ap(t,EV["reds"]-0.2,99),sc=pop(t,EV["reds"]-0.3),col=(150,50,30))
    return b,[hd]
def s_thin(t):
    b=paper(); wcg(b,M().rect(0,0,w,BH),(0.30,0.28,0.45),(0.55,0.52,0.70),0,BH,0.9,0.5,3)
    cx,cy=270,380
    wc(b,M().circ(cx,cy,150),RUST,0.9,0.7,0.7,1.5); wc(b,M().circ(cx-40,cy-30,70),(0.85,0.55,0.40),0.5,0.4,0.6,4)
    for k in range(5): wc(b,M().ell(cx-60+k*30,cy+40+((k*23)%50),30,10,20),BRN,0.5,0.5,0.6,2)
    ring=M().circ(cx,cy,156).f()-M().circ(cx,cy,151).f(); wc(b,np.clip(ring,0,1),(0.85,0.75,0.65),0.6,0.0,0.2,1.0,False)
    def hd(d,t=t):
        ttl(d,"Mars",170,100,a=ap(t,EV["less"]-0.4,EV["percent"]-0.1),sc=pop(t,EV["less"]-0.5))
        ttl(d,"under 1% of Earth's air",170,72,a=ap(t,EV["percent"]-0.1,99),sc=pop(t,EV["percent"]-0.2))
        note(d,"a thin, thin atmosphere",740,1120,44,a=ap(t,EV["gas"]-0.2,99))
    return b,[hd]
DUST=[(_g.uniform(10,530),_g.uniform(40,470),_g.uniform(1.5,4)) for _ in range(120)]
def s_dust(t):
    b=paper(); mars_land(b,t,glow=0.0,sunx=400,suny=150,sunr=15)
    k=sm((t-EV["dust"]+0.4)/0.8)
    for x,y,r in DUST:
        xx_=(x+t*8*(r/3))%540; wc(b,M().circ(xx_,y+3*math.sin(t+x),r),RUST,0.75*k,0.4,0.5,0.6)
    rover(b,380,640,0.9)
    def hd(d,t=t):
        ttl(d,"fine dust",200,100,a=ap(t,EV["dust"]-0.2,EV["tints"]),sc=pop(t,EV["dust"]-0.3))
        ttl(d,"tints the day orange",200,80,a=ap(t,EV["tints"]-0.1,99),sc=pop(t,EV["tints"]-0.2),col=(150,60,30))
    return b,[hd]
def s_grain(t):
    b=paper(); wcg(b,M().rect(0,0,w,BH),(0.92,0.85,0.78),(0.98,0.93,0.86),0,BH,0.6,0.5,3)
    gx,gy=300,360
    wc(b,M().circ(gx,gy,52),RUST,0.9,0.8,0.8,1.6); wc(b,M().circ(gx-16,gy-14,20),(0.90,0.65,0.50),0.5,0.3,0.4,3)
    lift(b,M().circ(70,360,36),0.95,1.5); wc(b,M().circ(70,360,36),YEL,0.5,0.4,0.3,1.0)
    k=cl((t-EV["size"]+0.4)/0.8); brush(b,(110,360),(110+(gx-60-110)*k,360),YEL,6,0.7)
    kb=sm((t-EV["fwd"]+0.3)/0.7); kr=sm((t-EV["fwd"]+0.1)/0.9)
    for i,a in enumerate((-0.12,0.0,0.12)):
        if kb>0: p0=(gx+58,gy+a*60); p1=(gx+58+180*kb*math.cos(a),gy+180*kb*math.sin(a)); brush(b,p0,p1,(0.40,0.58,0.95),5,0.85); arrowhead(b,p0,p1,(0.40,0.58,0.95))
    for i,a in enumerate((-2.2,-1.4,-0.7,0.7,1.4,2.2)):
        if kr>0: p0=(gx+math.cos(a)*58,gy+math.sin(a)*58); p1=(gx+math.cos(a)*(58+110*kr),gy+math.sin(a)*(58+110*kr)); brush(b,p0,p1,(0.97,0.62,0.40),4,0.7); arrowhead(b,p0,p1,(0.97,0.62,0.40),10)
    pencil(b,[(gx-52,gy+80),(gx+52,gy+80)],0.6); pencil(b,[(gx-52,gy+74),(gx-52,gy+86)],0.6); pencil(b,[(gx+52,gy+74),(gx+52,gy+86)],0.6)
    def hd(d,t=t):
        ttl(d,"the perfect grain size",190,74,a=ap(t,EV["grains"]-0.2,EV["fwd"]-0.1),sc=pop(t,EV["grains"]-0.3))
        ttl(d,"blue goes forward",190,86,a=ap(t,EV["fwd"]-0.1,99),sc=pop(t,EV["fwd"]-0.2),col=(40,70,140))
        note(d,"sunlight",140,640,46,a=ap(t,EV["size"]-0.3,99))
        note(d,"dust grain",600,980,46,a=ap(t,EV["grains"],99))
    return b,[hd]
def s_bsunset(t,glow=None):
    b=paper(); g=sm((t-EV["bsunset"]+0.2)/1.2) if glow is None else glow
    mars_land(b,t,glow=g); rover(b,150,640,1.0)
    def hd(d,t=t):
        ttl(d,"a blue glow",190,100,a=ap(t,EV["glow"]-0.2,EV["reverse"]-0.1),sc=pop(t,EV["glow"]-0.3),col=(40,70,140))
        ttl(d,"an Earth sunset, in reverse",190,72,a=ap(t,EV["reverse"]-0.1,99),sc=pop(t,EV["reverse"]-0.2))
    return b,[hd]
def s_size(t):
    b=paper(); mars_land(b,t,glow=1.0,sunx=360,suny=430,sunr=16)
    k=sm((t-EV["smaller"]+0.4)/0.7)
    pencil(b,[(150+80*math.cos(a),250+80*math.sin(a)) for a in np.linspace(0,2*math.pi,60)],0.7*k,1.6)
    if k>0: wc(b,M().circ(390,250,53),YEL,0.6*k,0.5,0.4,1.2); pencil(b,[(390+53*math.cos(a),250+53*math.sin(a)) for a in np.linspace(0,2*math.pi,60)],0.7*k,1.4)
    def hd(d,t=t):
        note(d,"from Earth",300,700,46,a=ap(t,EV["smaller"]-0.2,99))
        note(d,"from Mars",780,700,46,a=ap(t,EV["smaller"],99))
        ttl(d,"a smaller Sun: about 2/3",190,74,a=ap(t,EV["thirds"]-0.3,99),sc=pop(t,EV["thirds"]-0.4))
    return b,[hd]
def s_twilight(t):
    b=paper(); dk=sm((t-EV["twilight"]+0.6)/1.6)
    mars_land(b,t,glow=1.0,dark=dk,suny=432+50*dk); rover(b,150,640,1.0)
    def hd(d,t=t):
        ttl(d,"twilight lingers",190,96,a=ap(t,EV["twilight"]-0.3,EV["hours"]-0.1),sc=pop(t,EV["twilight"]-0.4))
        ttl(d,"up to two hours",190,96,a=ap(t,EV["hours"]-0.1,99),sc=pop(t,EV["hours"]-0.2),col=(40,70,140))
    return b,[hd]
def s_end(t):
    b=paper(); mars_land(b,t,glow=0.4); rover(b,150,640,0.001,a=0.0)
    def hd(d,t=t):
        ttl(d,"remember",190,96,a=ap(t,EV["remember"]-0.2,99),sc=pop(t,EV["remember"]-0.3))
    return b,[hd]
TR=0.40; TOTAL=B.TOTAL; LOOPD=0.70
SHOTS=[(0.0,s_hook),(S("earth")["s"],s_eday),(Lx("At sunset, sunlight")[0]-0.3,s_esunset),(S("mars")["s"],s_thin),(Lx("Instead")[0]-0.3,s_dust),
       (Lx("But the grains")[0]-0.3,s_grain),(S("blue")["s"],s_bsunset),(Lx("The Sun looks")[0]-0.3,s_size),(Lx("And high dust")[0]-0.3,s_twilight),(Lx("So if you ever")[0]-0.3,s_end)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
_ang=np.arctan2(yy-400,xx-270)
CENT=[(270,380),(120,250),(420,520),(300,200),(150,500),(400,300),(270,450),(100,300),(440,200),(270,380)]
def bloom(b1,b2,u,idx):
    """a drop of clear water lands and spreads; the next painting blooms inside its cauliflower edge"""
    cx,cy=CENT[idx%len(CENT)]; d=np.sqrt((xx-cx)**2+(yy-cy)**2)
    an=np.arctan2(yy-cy,xx-cx); edge=1+0.10*np.sin(an*7+idx)+0.06*np.sin(an*13+idx*2)+0.05*_v3
    R=sm(u)*900; inside=np.clip((R*edge-d)/6,0,1).astype(np.float32)
    out=b1*(1-inside[...,None])+b2*inside[...,None]
    ring=np.exp(-((d-R*edge)/5)**2).astype(np.float32)*(R>2)
    out*=1-(ring*0.30)[...,None]*(1-np.array((0.70,0.62,0.66),np.float32))
    return out
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)),i+1)
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)),i)
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD),0)
    if pair is None:
        buf,hud=SHOTS[i][1](t); hk=1.0
    else:
        fa_,fb_,ta,tb,u,idx=pair; b1,h1=fa_(ta); b2,h2=fb_(tb)
        buf=bloom(b1,b2,u,idx); hud=h1 if u<0.5 else h2; hk=cl(abs(u-0.5)*2.4)
    buf=buf*(1-BANDA[...,None])+BAND*BANDA[...,None]
    buf=buf*PTEX
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
