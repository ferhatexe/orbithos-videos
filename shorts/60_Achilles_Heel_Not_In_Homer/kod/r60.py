import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid60")
for p in ["/home/claude/vid60","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= Bayeux-style embroidery on linen =================
LIN=np.array((0.87,0.81,0.67),np.float32)
TERRA=(0.70,0.33,0.20); OCH=(0.83,0.66,0.30); SAGE=(0.48,0.56,0.38); TEAL=(0.27,0.42,0.42); NAVY=(0.17,0.20,0.32)
BUFF=(0.88,0.77,0.56); RED=(0.62,0.16,0.12); DGRN=(0.25,0.33,0.24); FLAMEY=(0.92,0.72,0.28)
FY0,FY1=128,612                        # main field between the borders
_g=np.random.default_rng(60)
_n1=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),40); _n1/=_n1.std()
_n2=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),0.7); _n2/=_n2.std()
WEAVE=(1+0.05*np.sin(xx*math.pi/1.1)*np.sin(yy*math.pi/1.1)+0.03*_n2+0.05*_n1)[...,None].astype(np.float32)
def linen():
    b=np.empty((h,w,3),np.float32); b[:]=LIN; return b*WEAVE
_TP={}
def threads(ang,period=2.3):
    k=round(ang,2)
    if k not in _TP:
        c,s=math.cos(ang),math.sin(ang); u=xx*c+yy*s; v=-xx*s+yy*c
        lay=0.5+0.5*np.cos(2*math.pi*u/period)
        couch=np.exp(-((v%16)-8)**2/1.2)*(0.5+0.5*np.cos(2*math.pi*u/(period*3)))
        _TP[k]=(0.80+0.24*lay-0.22*couch+0.03*_n2).astype(np.float32)
    return _TP[k]
def emb(buf,m,col,ang=0.6,outline=NAVY,ow=2,a=1.0):
    """laid-and-couched wool fill + stem-stitch outline"""
    A=(m.f() if isinstance(m,M) else m)*a
    if A.max()<=0.01: return
    T=threads(ang); c=np.array(col,np.float32)
    buf+=(c*T[...,None]-buf)*A[...,None]
    if outline is not None:
        e=np.clip(A-cv2.erode(A,np.ones((2*ow+1,2*ow+1),np.uint8)),0,1)
        st=0.75+0.25*np.cos((xx+yy)*math.pi/1.4)
        buf+=(np.array(outline,np.float32)*st[...,None]-buf)*e[...,None]
def stem(buf,pts,col=NAVY,th=2.5,a=1.0):
    m=M().pline(pts,th); A=m.f()*a; st=0.75+0.25*np.cos((xx+yy)*math.pi/1.4)
    buf+=(np.array(col,np.float32)*st[...,None]-buf)*A[...,None]
def borders(buf):
    for y0,y1 in ((40,FY0-6),(FY1+6,668)):
        stem(buf,[(28,y0),(512,y0)],NAVY,2.5); stem(buf,[(28,y1),(512,y1)],NAVY,2.5)
        cols=(TERRA,SAGE,OCH,TEAL)
        for i,x in enumerate(range(34,480,46)):
            m=M().poly([(x,y1-3),(x+12,y1-3),(x+30,y0+3),(x+18,y0+3)]); emb(buf,m,cols[i%4],1.2,NAVY,1)
            if i%2==0 and x+44<508:
                bx,by=x+36,(y0+y1)/2; emb(buf,M().ell(bx,by,7,4),cols[(i+1)%4],0.3,NAVY,1); stem(buf,[(bx+6,by-2),(bx+10,by-6)],NAVY,1.5)
    stem(buf,[(28,40),(28,668)],NAVY,2.5); stem(buf,[(512,40),(512,668)],NAVY,2.5)
    band=np.zeros((h,w),np.float32); band[676:h-14,22:w-22]=1
    emb(buf,band,(0.13,0.16,0.24),0.0,None)
    stem(buf,[(22,676),(w-22,676)],OCH,2.5); stem(buf,[(22,h-14),(w-22,h-14)],OCH,2.5)
# ---- figures ----
def warrior(buf,x,y,s,f=1,tunic=TERRA,legs=SAGE,shield=OCH,spear=True,arm=-0.4,helm=TEAL,shield_on=True,bow=False,draw=0.0):
    H=150*s
    for k,dx in enumerate((-8,8)):
        lm=M().line((x+dx*s,y-H*0.42),(x+dx*s+f*k*6*s,y-6*s),9*s); emb(buf,lm,legs,1.57,NAVY,1)
        for q in range(3): stem(buf,[(x+dx*s-5*s,y-H*0.35+q*16*s),(x+dx*s+5*s,y-H*0.35+q*16*s+3*s)],NAVY,1.4)
        emb(buf,M().ell(x+dx*s+f*k*6*s+f*7*s,y-4*s,11*s,5*s),NAVY,0,None)
    tm=M().poly([(x-16*s,y-H*0.80),(x+16*s,y-H*0.80),(x+26*s,y-H*0.40),(x-26*s,y-H*0.40)]); emb(buf,tm,tunic,0.9)
    hx,hy=x+f*3*s,y-H*0.88; emb(buf,M().circ(hx,hy,11*s),BUFF,0.0)
    emb(buf,M().poly([(hx-13*s,hy-2*s),(hx,hy-24*s),(hx+13*s,hy-2*s)]),helm,0.3)
    stem(buf,[(hx+f*4*s,hy-2*s),(hx+f*4*s,hy+8*s)],NAVY,2)
    stem(buf,[(hx+f*7*s,hy-2*s),(hx+f*9*s,hy-2*s)],NAVY,1.6)
    sx,sy=x+f*8*s,y-H*0.74
    if bow:
        ex,ey=sx+f*44*s,sy-6*s; stem(buf,[(sx,sy),(ex,ey)],BUFF,6*s)
        pts=[(ex+f*10*s*math.cos(a),ey+40*s*math.sin(a)) for a in np.linspace(-math.pi/2,math.pi/2,14)]; stem(buf,pts,DGRN,3)
        stem(buf,[pts[0],(ex-f*14*s*draw,ey),pts[-1]],NAVY,1.2)
    else:
        ex,ey=sx+f*math.sin(math.pi/2+arm)*40*s,sy-math.cos(math.pi/2+arm)*40*s; stem(buf,[(sx,sy),(ex,ey)],BUFF,6*s)
        if spear: stem(buf,[(ex-f*30*s,ey+50*s),(ex+f*40*s,ey-60*s)],NAVY,2.5); emb(buf,M().poly([(ex+f*40*s,ey-60*s),(ex+f*36*s,ey-48*s),(ex+f*48*s,ey-70*s)]),NAVY,0,None)
    if shield_on and not bow:
        cx,cy=x+f*22*s,y-H*0.58
        sh=M().poly([(cx-14*s,cy-28*s),(cx+14*s,cy-28*s),(cx+16*s,cy-10*s),(cx,cy+34*s),(cx-16*s,cy-10*s)]); emb(buf,sh,shield,1.57)
        emb(buf,M().circ(cx,cy-8*s,4*s),RED,0,None)
def arrow(buf,x0,y0,x1,y1,col=NAVY):
    stem(buf,[(x0,y0),(x1,y1)],col,2.5); a=math.atan2(y1-y0,x1-x0)
    emb(buf,M().poly([(x1+math.cos(a)*10,y1+math.sin(a)*10),(x1+math.cos(a+2.5)*9,y1+math.sin(a+2.5)*9),(x1+math.cos(a-2.5)*9,y1+math.sin(a-2.5)*9)]),col,0,None)
    for k in (0,1):
        bx,by=x0+math.cos(a)*k*8,y0+math.sin(a)*k*8
        emb(buf,M().poly([(bx,by),(bx-math.cos(a+0.6)*14,by-math.sin(a+0.6)*14),(bx+math.cos(a)*6,by+math.sin(a)*6)]),RED,0,None)
def leg_big(buf,x,y,s,hl=0.0):
    calf=M().poly([(x-40*s,y-260*s),(x+40*s,y-260*s),(x+46*s,y-150*s),(x+30*s,y-40*s),(x+90*s,y-20*s),(x+130*s,y),(x-40*s,y),(x-44*s,y-60*s),(x-58*s,y-150*s)])
    emb(buf,calf,BUFF,1.4)
    for q in range(4): stem(buf,[(x-50*s,y-250*s+q*28*s),(x+40*s,y-238*s+q*28*s)],TERRA,5*s)        # sandal straps
    if hl>0: emb(buf,M().ell(x-30*s,y-22*s,30*s,26*s),OCH,0.0,RED,2,a=hl)
def scroll(buf,x,y,s,lines=6,blank=False):
    emb(buf,M().rect(x-90*s,y-70*s,x+90*s,y+70*s),BUFF,0.0)
    emb(buf,M().rect(x-104*s,y-82*s,x-86*s,y+82*s),TERRA,1.57); emb(buf,M().rect(x+86*s,y-82*s,x+104*s,y+82*s),TERRA,1.57)
    if not blank:
        for k in range(lines): stem(buf,[(x-70*s,y-50*s+k*20*s),(x+(70-((k*37)%40))*s,y-50*s+k*20*s)],NAVY,2)
def water(buf,y0,t,a=1.0):
    for k in range(6):
        pts=[(x,y0+k*16+5*math.sin(x/22+t*2+k)) for x in range(30,511,6)]
        m=M().poly(pts+[(510,y0+k*16+18),(30,y0+k*16+18)]); emb(buf,m,(TEAL,NAVY,SAGE)[k%3],0.0,None,a=a)
def baby(buf,x,y,s,ang=0.0):
    c,sn=math.cos(ang),math.sin(ang)
    R=lambda dx,dy:(x+dx*c-dy*sn,y+dx*sn+dy*c)
    emb(buf,M().ell(*R(0,0),14*s,30*s,math.degrees(ang)),BUFF,0.5)
    emb(buf,M().circ(*R(0,38*s),13*s),BUFF,0.0)
    stem(buf,[R(-5*s,-28*s),R(-6*s,-56*s)],BUFF,7*s); stem(buf,[R(5*s,-28*s),R(7*s,-54*s)],BUFF,7*s)
    return R(-6*s,-60*s)
def woman(buf,x,y,s,f=1,arm=(0,0)):
    H=170*s
    dm=M().poly([(x-14*s,y-H*0.8),(x+14*s,y-H*0.8),(x+34*s,y),(x-34*s,y)]); emb(buf,dm,TEAL,1.2)
    for q in range(4): stem(buf,[(x-30*s+q*4*s,y-q*30*s-10*s),(x+30*s-q*4*s,y-q*30*s-10*s)],OCH,1.6)
    hx,hy=x+f*2*s,y-H*0.88; emb(buf,M().circ(hx,hy,12*s),BUFF,0.0); emb(buf,M().ell(hx-f*6*s,hy-2*s,12*s,15*s),SAGE,0.4)
    stem(buf,[(x+f*6*s,y-H*0.74),arm],BUFF,6*s)
# ================= HUD: stitched lettering =================
_IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(P.FD+n,s)
    return _IF[k]
_stripe=None
def caption(img,s,y=306,fs=60,a=1.0,sc=1.0,col=(38,46,86)):
    """embroidered caption: letters filled with diagonal thread texture"""
    global _stripe
    if a<=0.01 or fs*sc<8: return
    n=int(fs*sc); f=_f("IBMPlexSerif-Bold.ttf",n)
    while f.getlength(s)>900 and n>20: n-=4; f=_f("IBMPlexSerif-Bold.ttf",n)
    L=Image.new("L",(W,H),0); ImageDraw.Draw(L).text((W/2,y),s,font=f,fill=255,anchor="mm")
    m=np.asarray(L).astype(np.float32)/255
    if _stripe is None:
        Y,X=np.mgrid[0:H,0:W]; _stripe=(0.72+0.28*np.cos((X-Y)*math.pi/2.6)).astype(np.float32)
    rgb=np.zeros((H,W,4),np.uint8); c=np.array(col,np.float32)[None,None,:]*_stripe[...,None]
    rgb[...,:3]=np.clip(c,0,255).astype(np.uint8); rgb[...,3]=(m*255*a).astype(np.uint8)
    img.alpha_composite(Image.fromarray(rgb))
def pop(t,e): return spring((t-e)/0.5)
def ap(t,s,e): return fa(t,s-0.1,e-0.25,0.3,0.3)
# ================= shots =================
def s_hook(t,arrow_on=True):
    b=linen(); leg_big(b,230,560,1.25,hl=fa(t,EV["heel0"],EV["homer"]+0.5,0.3,0.4))
    if arrow_on:
        k=sm((t+0.3)/0.9); x1,y1=196+60*(1-k),528+30*(1-k)
        arrow(b,x1+150,y1+16,x1,y1)
    borders(b)
    def hd(img,t=t):
        caption(img,"ACHILLES' HEEL",a=ap(t,0.05,EV["homer"]-0.1),sc=pop(t,0.0),fs=72)
        caption(img,"HOMER NEVER MENTIONS IT",a=ap(t,EV["homer"]-0.1,99),sc=pop(t,EV["homer"]-0.2),fs=54)
    return b,[hd]
def s_duel(t):
    b=linen()
    for k in range(3): stem(b,[(40,600-k*3),(500,600-k*3)],DGRN,2)
    warrior(b,150,598,1.6,1,TERRA,SAGE,OCH)
    ast=1-cl((t-EV["graze"]+0.5)/0.4)
    warrior(b,410,598,1.4,-1,SAGE,OCH,TEAL,spear=False,arm=-0.9)
    if t>EV["spear"]-0.3:
        k=cl((t-EV["spear"]+0.3)/0.6); x0,y0=360,420; x1,y1=200+0*k,380
        hx=x0+(x1-x0)*k; hy=y0+(y1-y0)*k-40*math.sin(math.pi*k)
        if k<1: arrow(b,hx+70,hy-10,hx,hy)
        if k>=1: stem(b,[(165,560),(240,600)],NAVY,2.5)
    bl=fa(t,EV["graze"],99,0.2,0.3)
    if bl>0:
        emb(b,M().ell(206,404,6,8),RED,0,None,a=bl)
        for i in range(3): emb(b,M().ell(204+i*3,418+i*14*bl,3,5),RED,0,None,a=bl)
    borders(b)
    def hd(img,t=t):
        caption(img,"THE ILIAD",a=ap(t,EV["iliad"]-0.2,EV["invul"]),sc=pop(t,EV["iliad"]-0.3),fs=70)
        caption(img,"NOT INVULNERABLE",a=ap(t,EV["invul"],99),sc=pop(t,EV["invul"]-0.1),fs=60)
    return b,[hd]
def s_paris(t):
    b=linen(); scroll(b,140,280,0.8)
    for k in range(3): stem(b,[(40,600-k*3),(500,600-k*3)],DGRN,2)
    dr=cl((t-EV["paris"])/0.8)
    warrior(b,150,598,1.25,1,OCH,TERRA,SAGE,bow=True,draw=dr*(1-cl((t-EV["arrow"])/0.1)))
    warrior(b,420,598,1.45,-1,TERRA,SAGE,OCH)
    if t>EV["arrow"]:
        k=cl((t-EV["arrow"])/0.5); x=230+(380-230)*k; y=470-30*math.sin(math.pi*k)
        arrow(b,x-60,y,x,y)
    borders(b)
    def hd(img,t=t):
        caption(img,"THE POEM ENDS FIRST",a=ap(t,EV["ends"]-0.2,EV["paris"]-0.1),sc=pop(t,EV["ends"]-0.3),fs=56)
        caption(img,"PARIS · AN ARROW",a=ap(t,EV["paris"]-0.1,99),sc=pop(t,EV["paris"]-0.2),fs=64)
    return b,[hd]
def s_statius(t):
    b=linen()
    for k in range(3): stem(b,[(40,600-k*3),(500,600-k*3)],DGRN,2)
    warrior(b,140,598,1.5,1,TEAL,OCH,SAGE,spear=False,shield_on=False,arm=0.2,helm=SAGE)
    for k in range(5): emb(b,M().ell(136-12+k*6,368-6*abs(k-2),5,8,30*(k-2)),SAGE,0,None)   # laurel
    scroll(b,350,400,1.1,lines=7)
    nib=sm((t-EV["statius"])/2.0); stem(b,[(275,430+20*math.sin(t*6)),(195,390)],NAVY,2.5)
    borders(b)
    def hd(img,t=t):
        caption(img,"CENTURIES LATER",a=ap(t,S("statius")["s"]+0.2,EV["roman"]),sc=pop(t,S("statius")["s"]+0.1),fs=62)
        caption(img,"STATIUS · 1ST CENTURY AD",a=ap(t,EV["roman"],99),sc=pop(t,EV["roman"]-0.1),fs=50)
    return b,[hd]
def s_styx(t):
    b=linen(); water(b,470,t)
    dk=sm((t-EV["dipped"]+0.3)/1.0); dry=fa(t,EV["dry"]-0.2,99,0.3,0.3)
    emb(b,M().poly([(28,462),(200,462),(236,612),(28,612)]),SAGE,0.2)
    for k in range(3): stem(b,[(30,466+k*4),(205,466+k*4)],DGRN,2)
    by=300+170*dk; hx,hy=baby(b,320,by,1.2,0.0)
    woman(b,150,466,1.25,1,arm=(hx-4,hy+2))
    wm=M().poly([(212,470),(510,470),(510,612),(250,612)]).f()*np.clip((yy-468)/8,0,1)
    over=linen(); water(over,470,t); b=b*(1-wm[...,None]*dk)+over*(wm[...,None]*dk)
    if dry>0: emb(b,M().ell(hx+4,hy+10,16,14),OCH,0,RED,2,a=dry)
    borders(b)
    def hd(img,t=t):
        caption(img,"THETIS",a=ap(t,EV["thetis"]-0.3,EV["styx"]-0.1),sc=pop(t,EV["thetis"]-0.4),fs=72)
        caption(img,"THE RIVER STYX",a=ap(t,EV["styx"]-0.1,EV["held"]-0.1),sc=pop(t,EV["styx"]-0.2),fs=64)
        caption(img,"HELD BY ONE HEEL",a=ap(t,EV["held"]-0.1,99),sc=pop(t,EV["held"]-0.2),fs=62)
    return b,[hd]
def s_strike(t):
    b=linen(); leg_big(b,230,560,1.25,hl=fa(t,EV["there"]-0.3,99,0.2,0.3))
    k=sm((t-EV["arrow2"]+0.4)/0.6); x1,y1=196+180*(1-k),528-40*(1-k)
    arrow(b,x1+150,y1+16,x1,y1)
    borders(b)
    def hd(img,t=t):
        caption(img,"LATER RETELLINGS",a=ap(t,EV["later"]-0.4,EV["arrow2"]),sc=pop(t,EV["later"]-0.5),fs=62)
        caption(img,"THE ARROW FINDS THE HEEL",a=ap(t,EV["arrow2"],99),sc=pop(t,EV["arrow2"]-0.1),fs=52)
    return b,[hd]
def s_fire(t):
    b=linen()
    for k in range(3): stem(b,[(40,600-k*3),(500,600-k*3)],DGRN,2)
    woman(b,170,600,1.45,1,arm=(290,350))
    hx,hy=baby(b,320,420,1.1,-math.pi/2); stem(b,[(290,350),(300,412)],BUFF,6)
    for i in range(7):
        x=270+i*18; ht=60+20*math.sin(t*7+i*1.3); fm=M().poly([(x-14,598),(x+4*math.sin(t*9+i),598-ht),(x+14,598)]); emb(b,fm,(RED,FLAMEY)[i%2],1.57,NAVY,1)
    emb(b,M().rect(250,585,400,600),TERRA,0)
    borders(b)
    def hd(img,t=t):
        caption(img,"AN OLDER VERSION: FIRE",a=ap(t,EV["older"]-0.2,99),sc=pop(t,EV["older"]-0.3),fs=56)
    return b,[hd]
def s_tendon(t):
    b=linen(); leg_big(b,230,560,1.25)
    tk=sm((t-EV["tendon"]+0.2)/1.2)
    pts=[(176+6*math.sin(q*3),260+270*q) for q in np.linspace(0,tk,12)]
    if tk>0.05: stem(b,pts,RED,6)
    borders(b)
    def hd(img,t=t):
        caption(img,"TENDO ACHILLIS",a=ap(t,EV["tendon"]-0.2,EV["y1693"]-0.1),sc=pop(t,EV["tendon"]-0.3),fs=66)
        caption(img,"NAMED IN 1693",a=ap(t,EV["y1693"]-0.1,99),sc=pop(t,EV["y1693"]-0.2),fs=66)
        caption(img,"by a Flemish anatomist",y=1180,fs=44,a=ap(t,EV["flemish"]-0.2,99))
    return b,[hd]
def s_word(t):
    b=linen()
    emb(b,M().rect(70,190,470,560),BUFF,0.0)
    for k in range(10): emb(b,M().rect(86+k*38,206,104+k*38,224),(TERRA,SAGE,OCH,TEAL)[k%4],0.8,None)
    for k in range(10): emb(b,M().rect(86+k*38,526,104+k*38,544),(TEAL,OCH,SAGE,TERRA)[k%4],0.8,None)
    borders(b)
    def hd(img,t=t):
        caption(img,"A WORD FOR WEAKNESS",a=ap(t,EV["word"]-0.3,99),sc=pop(t,EV["word"]-0.4),fs=56)
        caption(img,"“ACHILLES' HEEL”",y=700,fs=78,a=ap(t,EV["word"]-0.1,99),sc=pop(t,EV["word"]-0.2),col=(130,40,30))
        caption(img,"1800s",y=880,fs=90,a=ap(t,EV["c1800"]-0.2,99),sc=pop(t,EV["c1800"]-0.3))
    return b,[hd]
def s_end(t):
    b=linen(); leg_big(b,230,560,1.25,hl=fa(t,EV["yourheel"]-0.2,99,0.3,0.4)); borders(b)
    def hd(img,t=t):
        caption(img,"REMEMBER",a=ap(t,EV["remember"]-0.3,99),sc=pop(t,EV["remember"]-0.4),fs=72)
    return b,[hd]
TR=0.38; TOTAL=B.TOTAL; LOOPD=0.66
SHOTS=[(0.0,s_hook),(S("iliad")["s"],s_duel),(Lx("And the poem")[0]-0.3,s_paris),(S("statius")["s"],s_statius),(Lx("His mother")[0]-0.3,s_styx),
       (Lx("In later")[0]-0.3,s_strike),(Lx("An older")[0]-0.3,s_fire),(S("later")["s"],s_tendon),(Lx("And Achilles' heel as")[0]-0.3,s_word),(Lx("So when")[0]-0.3,s_end)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
_RO=np.random.default_rng(3).permutation(int(h/6)+1).astype(np.float32)/(int(h/6)+1)
ROW=(_RO[(yy/6).astype(int)]*0.55+(yy/h)*0.45).astype(np.float32)
def restitch(b1,b2,u):
    """old embroidery is unpicked row by row, then the new picture is stitched in"""
    base=linen(); borders(base)
    if u<0.5: k=u*2; keep=(ROW>=k).astype(np.float32); src=b1
    else: k=(u-0.5)*2; keep=(ROW<k).astype(np.float32); src=b2
    keep=cv2.GaussianBlur(keep,(0,0),0.6)
    field=np.zeros((h,w),np.float32); field[FY0:FY1,28:512]=1
    m=(keep*field)[...,None]; out=base*(1-m)+src*m
    edge=np.exp(-((ROW-k)/0.012)**2)*field; out+=(np.array(OCH,np.float32)-out)*(edge*0.6)[...,None]
    return out
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
        if u<0.5: b1,hud=fa_(ta); buf=restitch(b1,None,u)
        else: b2,hud=fb_(tb); buf=restitch(None,b2,u)
        hk=cl(abs(u-0.5)*2.4)
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0))
    for f in hud: f(ov)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*max(0,hk)).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
