import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid65")
for p in ["/home/claude/vid65","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= Art Deco poster: black lacquer, gold line, teal & cream =================
BLK=np.array((0.045,0.045,0.055),np.float32); GOLD=(0.86,0.70,0.38); GOLDL=(0.98,0.86,0.55); TEAL=(0.12,0.40,0.42); CREAM=(0.93,0.88,0.76); RUST=(0.62,0.26,0.16); NAV=(0.10,0.14,0.24)
_g=np.random.default_rng(65)
_n=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),30); _n/=_n.std()
_f1=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),0.7); _f1/=_f1.std()
def fill(buf,m,col,a=1.0):
    A=(m.f() if isinstance(m,M) else m)*a; buf+=(np.array(col,np.float32)-buf)*A[...,None]
def gl(buf,pts,th=2.0,col=GOLD,a=1.0,closed=False):
    m=M().pline(list(pts)+([pts[0]] if closed else []),th); fill(buf,m,col,a)
def goldfill(buf,m,a=1.0):
    A=(m.f() if isinstance(m,M) else m)*a
    k=np.clip((yy-yy.min())/h,0,1); col=np.array(GOLDL,np.float32)*(1-0.35*np.sin(xx*0.02+yy*0.01)[...,None]*0.5)
    buf+=(col-buf)*A[...,None]
def _frame():
    b=np.empty((h,w,3),np.float32); b[:]=BLK; b*=(1+0.05*_n)[...,None]
    for inset in (16,24):
        gl(b,[(inset,inset),(w-inset,inset),(w-inset,672-inset+16),(inset,672-inset+16)],2.0 if inset==16 else 1.2,GOLD,1.0,True)
    for cx,cy,sx,sy in ((24,24,1,1),(w-24,24,-1,1),(24,664,1,-1),(w-24,664,-1,-1)):
        for k in range(3): gl(b,[(cx,cy+sy*(14+k*10)),(cx+sx*(14+k*10),cy+sy*(14+k*10)),(cx+sx*(14+k*10),cy)],1.4,GOLD)
    for k in range(9):
        a=math.pi+k*math.pi/8; gl(b,[(270,672),(270+math.cos(a)*50,672+math.sin(a)*50)],1.2,GOLD,0.8)
    fill(b,M().rect(0,676,w,h),(0.03,0.03,0.04))
    return b
FRAME=_frame()
INT=np.zeros((h,w),np.float32); INT[26:663,26:515]=1; INT=cv2.GaussianBlur(INT,(0,0),0.7)[...,None]
def base(): return FRAME.copy()
def sunburst(b,cx,cy,r0,r1,n=24,a=0.35,col=GOLD,rot=0.0):
    for k in range(n):
        an=rot+k*2*math.pi/n
        if k%2==0: fill(b,M().poly([(cx+math.cos(an)*r0,cy+math.sin(an)*r0),(cx+math.cos(an-0.06)*r1,cy+math.sin(an-0.06)*r1),(cx+math.cos(an+0.06)*r1,cy+math.sin(an+0.06)*r1)]),col,a)
def pyramid(b,cx,by,s,a=1.0,ruin=False):
    pts=[(cx-150*s,by),(cx,by-150*s),(cx+150*s,by)]
    fill(b,M().poly(pts),(0.62,0.48,0.24),a); fill(b,M().poly([(cx,by-150*s),(cx+150*s,by),(cx,by)]),(0.42,0.32,0.15),a)
    for k in range(1,8): y=by-k*18.75*s; hw=150*s*(1-k/8); gl(b,[(cx-hw,y),(cx+hw,y)],1.0,GOLDL,0.6*a)
    gl(b,pts,2.2,GOLDL,a,True)
    if ruin:
        for k in range(4): fill(b,M().poly([(cx-60*s+k*40*s,by),(cx-50*s+k*40*s,by-12*s),(cx-36*s+k*40*s,by)]),(0.30,0.24,0.12),a)
def cleo(b,cx,cy,s,a=1.0):
    """deco profile: nemes headdress, kohl eye, cobra uraeus"""
    head=M().ell(cx,cy,48*s,58*s); fill(b,head,CREAM,a)
    fill(b,M().poly([(cx+40*s,cy-6*s),(cx+62*s,cy+8*s),(cx+42*s,cy+14*s)]),CREAM,a)
    fill(b,M().poly([(cx-62*s,cy-52*s),(cx+30*s,cy-62*s),(cx+28*s,cy-20*s),(cx-20*s,cy-10*s),(cx-40*s,cy+120*s),(cx-90*s,cy+120*s),(cx-70*s,cy-10*s)]),TEAL,a)
    for k in range(6): gl(b,[(cx-66*s+k*5*s,cy-40*s+k*24*s),(cx-20*s,cy-46*s+k*24*s)],2,GOLD,a)
    gl(b,[(cx-62*s,cy-52*s),(cx+30*s,cy-62*s)],3,GOLD,a)
    fill(b,M().ell(cx+20*s,cy-4*s,10*s,4*s),BLK,a); gl(b,[(cx+10*s,cy-2*s),(cx+40*s,cy-6*s)],2,BLK,a)
    gl(b,[(cx+30*s,cy-62*s),(cx+38*s,cy-80*s),(cx+30*s,cy-90*s)],3,GOLDL,a)
    fill(b,M().poly([(cx-30*s,cy+52*s),(cx+30*s,cy+40*s),(cx+10*s,cy+120*s),(cx-40*s,cy+120*s)]),CREAM,a)
    for k in range(3): gl(b,[(cx-36*s+k*4,cy+70*s+k*14*s),(cx+16*s-k*4,cy+62*s+k*14*s)],3,(TEAL,GOLD,RUST)[k],a)
def moon(b,cx,cy,r,a=1.0):
    fill(b,M().circ(cx,cy,r),CREAM,a); fill(b,M().circ(cx+r*0.35,cy-r*0.2,r*0.95),BLK,a*0.0)
    for x,y,rr in ((-0.3,-0.2,0.18),(0.25,0.15,0.22),(-0.1,0.35,0.12),(0.35,-0.35,0.1)): gl(b,[(cx+x*r+math.cos(q)*rr*r,cy+y*r+math.sin(q)*rr*r) for q in np.linspace(0,2*math.pi,30)],1.6,GOLD,a)
    gl(b,[(cx+math.cos(q)*r,cy+math.sin(q)*r) for q in np.linspace(0,2*math.pi,80)],2.2,GOLDL,a)
def lander(b,x,y,s,a=1.0):
    fill(b,M().poly([(x-26*s,y-30*s),(x+26*s,y-30*s),(x+34*s,y-6*s),(x-34*s,y-6*s)]),GOLD,a)
    fill(b,M().poly([(x-18*s,y-56*s),(x+18*s,y-56*s),(x+24*s,y-30*s),(x-24*s,y-30*s)]),CREAM,a)
    for sd in (-1,1): gl(b,[(x+sd*30*s,y-10*s),(x+sd*50*s,y+16*s)],2.5,GOLDL,a); gl(b,[(x+sd*58*s,y+16*s),(x+sd*42*s,y+16*s)],2.5,GOLDL,a)
def mammoth(b,cx,by,s,a=1.0):
    body=M().ell(cx,by-80*s,90*s,62*s); body.ell(cx+70*s,by-110*s,46*s,44*s)
    for dx in (-60,-20,25,55): body.rect(cx+dx*s-12*s,by-60*s,cx+dx*s+12*s,by)
    fill(b,body,RUST,a)
    for k in range(7): gl(b,[(cx-80*s+k*22*s,by-40*s),(cx-74*s+k*22*s,by-18*s)],1.6,(0.40,0.16,0.10),a)
    gl(b,[(cx+108*s,by-110*s),(cx+120*s,by-60*s),(cx+112*s,by-20*s)],8*s,RUST,a)
    gl(b,[(cx+92*s,by-80*s),(cx+140*s,by-70*s),(cx+150*s,by-100*s)],5*s,CREAM,a)
    fill(b,M().circ(cx+84*s,by-118*s,4*s),BLK,a)
def spire(b,cx,by,s,a=1.0):
    fill(b,M().rect(cx-40*s,by-120*s,cx+40*s,by),CREAM,a); fill(b,M().poly([(cx-30*s,by-120*s),(cx,by-260*s),(cx+30*s,by-120*s)]),GOLD,a)
    for k in range(3): fill(b,M().poly([(cx-24*s+k*24*s,by-60*s),(cx-24*s+k*24*s,by-90*s),(cx-14*s+k*24*s,by-100*s),(cx-4*s+k*24*s,by-90*s),(cx-4*s+k*24*s,by-60*s)]),BLK,a)
def aztec(b,cx,by,s,a=1.0):
    for k in range(5): fill(b,M().rect(cx-(110-k*18)*s,by-(k+1)*28*s,cx+(110-k*18)*s,by-k*28*s),(TEAL if k%2 else (0.10,0.30,0.32)),a); gl(b,[(cx-(110-k*18)*s,by-(k+1)*28*s),(cx+(110-k*18)*s,by-(k+1)*28*s)],1.5,GOLD,a)
    fill(b,M().rect(cx-14*s,by-140*s,cx+14*s,by),RUST,a)
    for sd in (-1,1): fill(b,M().rect(cx+sd*24*s-14*s,by-176*s,cx+sd*24*s+14*s,by-140*s),RUST,a)
# ================= HUD =================
_IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(P.FD+n,s)
    return _IF[k]
cG=(245,214,140); cC=(240,228,200)
def ttl(d,s,y=1205,fs=86,a=1.0,sc=1.0,col=cG,font="PoiretOne-Regular.ttf",sp=6):
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f(font,n)
    tw=sum(f.getlength(c) for c in s)+sp*(len(s)-1)
    while tw>960 and n>20: n-=4; f=_f(font,n); tw=sum(f.getlength(c) for c in s)+sp*(len(s)-1)
    x=W/2-tw/2
    for c in s:
        d.text((x,y),c,font=f,fill=col+(int(255*a),),anchor="lm",stroke_width=1,stroke_fill=col+(int(255*a),)); x+=f.getlength(c)+sp
def num(d,s,x,y,fs=96,a=1.0,col=cG):
    if a<=0.01: return
    d.text((x,y),s,font=_f("PoiretOne-Regular.ttf",fs),fill=col+(int(255*a),),anchor="mm",stroke_width=2,stroke_fill=col+(int(255*a),))
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.3,0.28,0.25)
# ================= shots =================
def timeline(b,t,k=1.0):
    y=470; gl(b,[(50,y),(50+440*k,y)],2.5,GOLDL)
    xs=[60,330,480]
    if k>0.05: pyramid(b,95,y-12,0.42)
    if k>0.5: cleo(b,330,y-110,0.6)
    if k>0.9: moon(b,470,y-70,34); lander(b,470,y-12,0.5)
    for x in xs[:1+int(k*2.2)]: fill(b,M().circ(x,y,6),GOLDL)
def s_hook(t):
    b=base(); sunburst(b,270,470,40,330,28,0.10,GOLD,t*0.05)
    k=sm((t+0.4)/2.2); timeline(b,t,k)
    bk=sm((t-EV["moon0"]+0.2)/1.0)
    if bk>0:
        gl(b,[(60,520),(60+270*bk,520)],6,RUST); gl(b,[(330,550),(330+150*min(1,bk*1.4),550)],6,TEAL)
    def hd(d,t=t):
        ttl(d,"CLEOPATRA",1205,96,a=ap(t,EV["cleo0"]-0.2,EV["moon0"]),sc=pop(t,EV["cleo0"]-0.3))
        num(d,"~2,500 yrs",250,1110,52,ap(t,EV["moon0"],99),(230,140,110)); num(d,"~2,000",810,1170,52,ap(t,EV["moon0"]+0.3,99),(130,210,210))
        ttl(d,"CLOSER TO THE MOON",1240,72,a=ap(t,EV["moon0"],99),sc=pop(t,EV["moon0"]-0.1))
    return b,[hd]
def s_pyr(t):
    b=base(); sunburst(b,270,470,60,360,32,0.14,GOLD,t*0.04); pyramid(b,270,545,1.35)
    def hd(d,t=t):
        ttl(d,"GIZA",1205,110,a=ap(t,EV["giza"]-0.2,EV["y2560"]),sc=pop(t,EV["giza"]-0.3))
        num(d,"2560 BC",540,1205,104,ap(t,EV["y2560"]-0.1,99))
    return b,[hd]
def s_cleo(t):
    b=base(); sunburst(b,270,330,40,260,24,0.12,TEAL,-t*0.04); cleo(b,250,320,1.6)
    def hd(d,t=t):
        num(d,"69 BC",540,1130,100,ap(t,EV["born"]-0.2,99))
        ttl(d,"~2,500 YEARS LATER",1250,64,a=ap(t,EV["later"]-0.4,99),sc=pop(t,EV["later"]-0.5))
    return b,[hd]
STARS=[(_g.uniform(40,500),_g.uniform(40,640)) for _ in range(60)]
def s_moon(t):
    b=base();
    for x,y in STARS: fill(b,M().circ(x,y,1.2),CREAM,0.6)
    moon(b,270,250,135); lander(b,270,500,1.2)
    fill(b,M().rect(30,510,510,535),(0.30,0.30,0.32))
    def hd(d,t=t):
        num(d,"1969",540,1150,110,ap(t,EV["armstrong"]-0.4,99))
        ttl(d,"~2,000 YEARS AFTER HER",1260,58,a=ap(t,EV["death"]-0.4,99),sc=pop(t,EV["death"]-0.5))
    return b,[hd]
def s_ancient(t):
    b=base(); sunburst(b,350,560,50,300,24,0.10,GOLD,t*0.05); pyramid(b,360,545,0.9,ruin=True); cleo(b,140,400,0.8)
    def hd(d,t=t):
        ttl(d,"ALREADY ANCIENT",1225,84,a=ap(t,EV["ancient"]-0.3,99),sc=pop(t,EV["ancient"]-0.4))
    return b,[hd]
def s_mammoth(t):
    b=base(); sunburst(b,270,560,50,360,28,0.10,GOLD,t*0.05)
    k=sm((t-EV["mammoths"]+0.4)/0.6)
    pyramid(b,150,545,0.8)
    if k>0: mammoth(b,350,545,1.0*k+0.01,k)
    def hd(d,t=t):
        ttl(d,"STRANGER",1205,96,a=ap(t,EV["stranger"]-0.3,EV["mammoths"]-0.1),sc=pop(t,EV["stranger"]-0.4))
        ttl(d,"MAMMOTHS WERE ALIVE",1205,70,a=ap(t,EV["mammoths"]-0.1,99),sc=pop(t,EV["mammoths"]-0.2))
    return b,[hd]
def s_wrangel(t):
    b=base(); fill(b,M().rect(30,30,510,676),NAV)
    for k in range(12): gl(b,[(40,60+k*52),(500,60+k*52)],1,(0.25,0.35,0.55),0.6)
    isl=M().poly([(140,330),(210,280),(320,290),(400,320),(380,380),(280,400),(180,390)]); fill(b,isl,CREAM); gl(b,[(140,330),(210,280),(320,290),(400,320),(380,380),(280,400),(180,390)],2,GOLD,1,True)
    mammoth(b,280,372,0.32)
    def hd(d,t=t):
        ttl(d,"WRANGEL ISLAND",1150,72,a=ap(t,EV["wrangel"]-0.3,99),sc=pop(t,EV["wrangel"]-0.4))
        ttl(d,"ARCTIC OCEAN",400,48,a=ap(t,EV["arctic"]-0.2,99),col=(170,200,230))
        num(d,"~4,000 years ago",540,1260,58,ap(t,EV["y4000"]-0.2,99))
    return b,[hd]
def s_oxford(t):
    b=base(); sunburst(b,270,560,50,360,28,0.10,GOLD,t*0.05)
    spire(b,140,540,1.2); k=sm((t-EV["aztecs"]+0.4)/0.6)
    if k>0: aztec(b,385,540,1.05*k+0.01,k)
    def hd(d,t=t):
        num(d,"1096",280,320,72,ap(t,EV["teaching"]-0.3,99)); ttl(d,"OXFORD",1205,80,a=ap(t,EV["oxford"]-0.3,EV["aztecs"]-0.1),sc=pop(t,EV["oxford"]-0.4))
        num(d,"1325",780,480,72,ap(t,EV["tenoch"]-0.4,99))
        ttl(d,"TENOCHTITLAN",1205,70,a=ap(t,EV["aztecs"]-0.1,99),sc=pop(t,EV["aztecs"]-0.2))
    return b,[hd]
def s_overlap(t):
    b=base(); k=sm((t-EV["neat"]+0.4)/1.0); ko=sm((t-EV["overlaps"]+0.3)/0.9)
    cols=[RUST,TEAL,GOLD,CREAM];
    for i in range(4):
        y=200+i*90; x0=60+i*60*(1-ko)+ko*i*20; x1=x0+260+ko*120
        fill(b,M().rect(x0,y,x0+(x1-x0)*k,y+50),cols[i],0.75)
        gl(b,[(x0,y),(x0+(x1-x0)*k,y),(x0+(x1-x0)*k,y+50),(x0,y+50)],1.5,GOLDL,1,True)
    def hd(d,t=t):
        ttl(d,"NOT A NEAT LINE",1205,80,a=ap(t,EV["neat"]-0.2,EV["overlaps"]-0.1),sc=pop(t,EV["neat"]-0.3))
        ttl(d,"IT OVERLAPS",1205,96,a=ap(t,EV["overlaps"]-0.1,EV["side"]),sc=pop(t,EV["overlaps"]-0.2))
        ttl(d,"SIDE BY SIDE",1205,96,a=ap(t,EV["side"]-0.2,99),sc=pop(t,EV["side"]-0.3))
    return b,[hd]
def s_end(t):
    b=base(); sunburst(b,270,470,40,330,28,0.10,GOLD,t*0.05); timeline(b,t,1.0)
    def hd(d,t=t):
        ttl(d,"REMEMBER",1205,100,a=ap(t,EV["remember"]-0.3,99),sc=pop(t,EV["remember"]-0.4))
    return b,[hd]
TR=0.36; TOTAL=B.TOTAL; LOOPD=0.62
SHOTS=[(0.0,s_hook),(S("pyramid")["s"],s_pyr),(Lx("Cleopatra was born")[0]-0.3,s_cleo),(Lx("And about two")[0]-0.3,s_moon),(Lx("To her")[0]-0.3,s_ancient),
       (S("mammoth")["s"],s_mammoth),(Lx("A last small")[0]-0.3,s_wrangel),(S("oxford")["s"],s_oxford),(Lx("History isn't")[0]-0.3,s_overlap),(Lx("So the next")[0]-0.3,s_end)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
_AN=np.arctan2(yy-470,xx-270)
def fan(b1,b2,u):
    """Deco fan: gold-edged blades sweep shut over the old poster and fan open on the new one"""
    n=12; seg=2*math.pi/n; ph=(_AN+math.pi)%seg/seg
    cov=sm(u*2) if u<0.5 else 1-sm((u-0.5)*2)
    m=(ph<cov).astype(np.float32); m=cv2.GaussianBlur(m,(0,0),0.8)
    src=b1 if u<0.5 else b2
    blade=np.empty_like(src); blade[:]=BLK; blade+=(np.abs(np.sin((_AN+math.pi)*n/2))*0.05)[...,None]
    out=src*(1-m[...,None])+blade*m[...,None]
    edge=np.exp(-(((ph-cov)*seg*np.sqrt((xx-270)**2+(yy-470)**2))/1.6)**2)*(cov>0.01)*(cov<0.99)
    fill(out,np.clip(edge,0,1),GOLDL,0.9)
    out=out*(1-(yy>=676)[...,None])+FRAME*(yy>=676)[...,None]
    return out
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None: buf,hud=SHOTS[i][1](t); hk=1.0; buf=buf*INT+FRAME*(1-INT)
    else:
        fa_,fb_,ta,tb,u=pair
        if u<0.5: b1,hud=fa_(ta); buf=fan(b1,b1,u)
        else: b2,hud=fb_(tb); buf=fan(b2,b2,u)
        buf=buf*INT+FRAME*(1-INT)
        hk=cl(abs(u-0.5)*2.4)
    buf=buf*(1+0.04*_f1[...,None]*0.5)
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
