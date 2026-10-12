import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid64")
for p in ["/home/claude/vid64","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import *
from PIL import Image, ImageDraw, ImageFont
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= chalk on a slate blackboard =================
_g=np.random.default_rng(64)
def _nz(s): n=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),s); return n/n.std()
_f1,_f2,_f3,_f4=_nz(0.55),_nz(1.5),_nz(12),_nz(40)
BOARD=np.array((0.12,0.19,0.16),np.float32)
def _board():
    b=np.empty((h,w,3),np.float32); b[:]=BOARD
    haze=np.clip(0.5+0.35*_f4+0.25*_f3,0,1)*0.07; b+=haze[...,None]*np.array((0.9,0.95,0.9),np.float32)
    for k in range(7):     # old eraser swirls
        cx,cy,r=_g.uniform(40,500),_g.uniform(60,640),_g.uniform(60,150)
        ring=np.clip(M().ell(cx,cy,r,r*0.5,_g.uniform(0,180)).f()-M().ell(cx,cy,r*0.8,r*0.38,0).f(),0,1)
        b+=cv2.GaussianBlur(ring,(0,0),8)[...,None]*0.04
    frame=np.zeros((h,w),np.float32); frame[:14,:]=1; frame[:,:12]=1; frame[:,-12:]=1
    wood=np.array((0.42,0.27,0.14),np.float32)*(1+0.12*_f2[...,None])
    b=b*(1-frame[...,None])+wood*frame[...,None]
    wall=np.zeros((h,w),np.float32); wall[690:,:]=1; b=b*(1-wall[...,None])+wall[...,None]*np.array((0.11,0.10,0.10),np.float32)*(1+0.06*_f3[...,None])
    tray=np.zeros((h,w),np.float32); tray[674:690,:]=1; b=b*(1-tray[...,None])+wood*0.9*tray[...,None]
    for x,c in ((150,(0.95,0.95,0.92)),(190,(0.95,0.75,0.75)),(370,(0.75,0.85,0.98))): fill(b,M().rect(x,664,x+30,674).f(),c)
    fill(b,M().rect(400,656,470,674).f(),(0.35,0.22,0.12)); fill(b,M().rect(400,668,470,674).f(),(0.55,0.55,0.55))
    return b
def fill(buf,A,col,a=1.0): buf+=(np.array(col,np.float32)-buf)*(A*a)[...,None]
GRAIN=np.clip(0.55+0.55*_f1+0.15*_f2,0,1).astype(np.float32)
def chalk(buf,m,col=(0.95,0.95,0.92),a=1.0,dust=True):
    """chalk skips over the slate grain; a faint dust halo around every stroke"""
    A=(m.f() if isinstance(m,M) else m)
    if A.max()<0.01 or a<=0.01: return
    T=A*GRAIN*a
    if dust: buf+=(cv2.GaussianBlur(A,(0,0),3)*0.10*a)[...,None]*np.array(col,np.float32)
    fill(buf,np.clip(T*1.15,0,1),col)
BOARDIMG=None
def board():
    global BOARDIMG
    if BOARDIMG is None: BOARDIMG=_board()
    return BOARDIMG.copy()
def partial(pts,k):
    n=max(2,int(len(pts)*cl(k))); return pts[:n]
def stroke(buf,pts,k=1.0,th=3.0,col=(0.95,0.95,0.92),a=1.0):
    if k<=0.01: return
    chalk(buf,M().pline(partial(pts,k),th),col,a)
_IF={}
def _f(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(P.FD+n,s)
    return _IF[k]
_TM={}
def text_mask(s,x,y,fs,font="SmoochSans-Medium.ttf"):
    k=(s,x,y,fs,font)
    if k not in _TM:
        L=Image.new("L",(w,h),0); ImageDraw.Draw(L).text((x,y),s,font=_f(font,fs),fill=255,anchor="mm"); _TM[k]=np.asarray(L).astype(np.float32)/255
    return _TM[k]
def write(buf,s,x,y,fs,k,col=(0.95,0.95,0.92),a=1.0,font="SmoochSans-Medium.ttf"):
    """text 'written' left to right"""
    if k<=0.01 or a<=0.01: return
    fs=int(fs*1.22); A=text_mask(s,x,y,fs,font); f=_f(font,fs); tw=f.getlength(s); x0=x-tw/2
    rev=np.clip((x0+tw*k*1.05-xx)/6,0,1); chalk(buf,A*rev,col,a)
YEL=(0.98,0.90,0.55); PINK=(0.98,0.72,0.72); BLU=(0.65,0.82,1.0); ORG=(0.98,0.75,0.45); WH=(0.95,0.95,0.92)
def wk(t,e,d=0.8): return cl((t-e)/d)
def circle_pts(cx,cy,r,a0=0,a1=2*math.pi,n=60,wob=1.5,seed=0):
    g=np.random.default_rng(seed); return [(cx+(r+g.normal(0,wob))*math.cos(a),cy+(r+g.normal(0,wob))*math.sin(a)) for a in np.linspace(a0,a1,n)]
# ---- drawings ----
def hubble(b,x,y,s,k=1.0):
    pts=[(x-70*s,y-22*s),(x+60*s,y-22*s),(x+60*s,y+22*s),(x-70*s,y+22*s),(x-70*s,y-22*s)]
    stroke(b,pts,k,3)
    stroke(b,[(x+60*s,y-26*s),(x+86*s,y-30*s),(x+86*s,y+30*s),(x+60*s,y+26*s)],k,3)
    for sd in (-1,1):
        pp=[(x-20*s,y+sd*22*s),(x-20*s,y+sd*80*s),(x+20*s,y+sd*80*s),(x+20*s,y+sd*22*s)]; stroke(b,pp,k,2.5,BLU)
        for q in range(1,4): stroke(b,[(x-20*s,y+sd*(22+q*14.5)*s),(x+20*s,y+sd*(22+q*14.5)*s)],k,1.5,BLU)
def dipper(b,x,y,s,k=1.0):
    st=[(0,0),(40,6),(78,20),(108,40),(118,80),(170,84),(176,46)]
    P_=[(x+a*s,y+b_*s) for a,b_ in st]
    for i,(px,py) in enumerate(P_):
        if k>i/7: chalk(b,M().circ(px,py,4),WH)
    stroke(b,P_+[P_[3]],k,1.8,WH,0.7)
GAL=[]
for i in range(260):
    t_=_g.choice(["dot","dot","ell","ell","spiral"]); GAL.append((_g.uniform(0,1),_g.uniform(0,1),t_,_g.uniform(2,9) if t_!="dot" else _g.uniform(1,2.5),
        [WH,YEL,ORG,PINK,BLU][_g.integers(0,5)],_g.uniform(0,180),_g.uniform(0,1)))
def galaxies(b,x0,y0,x1,y1,k=1.0,dens=1.0,zoom=1.0,cx=None,cy=None):
    n=int(len(GAL)*dens)
    for i,(u,v,tp,sz,col,ang,ord_) in enumerate(GAL[:n]):
        if ord_>k: continue
        x=x0+(x1-x0)*u; y=y0+(y1-y0)*v
        if cx is not None: x=cx+(x-cx)*zoom; y=cy+(y-cy)*zoom; sz*=zoom
        if not (x0-10<x<x1+10 and y0-10<y<y1+10): continue
        if tp=="dot": chalk(b,M().circ(x,y,sz),col,0.9,False)
        elif tp=="ell": chalk(b,M().ell(x,y,sz,sz*0.5,ang),col,0.8,False)
        else:
            for arm in (0,math.pi):
                pts=[(x+math.cos(arm+q*3+math.radians(ang))*sz*q*0.9,y+math.sin(arm+q*3+math.radians(ang))*sz*q*0.55) for q in np.linspace(0.15,1.2,12)]
                chalk(b,M().pline(pts,1.4),col,0.9,False)
            chalk(b,M().circ(x,y,1.6),col,1,False)
def box(b,x0,y0,x1,y1,k=1.0,col=WH):
    stroke(b,[(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)],k,2.5,col)
# ================= shots =================
def s_hook(t):
    b=board()
    write(b,"1995",110,70,64,wk(t,EV["y1995"]-0.2,0.6),YEL)
    hubble(b,140,230,1.0,wk(t,EV["hubble"]-0.4,0.9))
    k=wk(t,EV["patch"]-0.2,0.8); stroke(b,circle_pts(400,180,46,seed=1),k,3,PINK)
    if k>0: stroke(b,[(230,215),(350,190)],k,1.5,WH,0.6)
    write(b,"\"empty\"",400,262,46,wk(t,EV["empty"]-0.1,0.5),PINK)
    pk=wk(t,EV["pin"]-0.3,0.7)
    if pk>0:
        stroke(b,[(70,520),(160,470),(260,440),(380,420)],pk,6,WH)
        chalk(b,M().circ(392,418,4),YEL,pk); write(b,"pinhead",410,385,38,wk(t,EV["pin"],0.5),YEL)
        write(b,"at arm's length",230,560,46,wk(t,EV["arm"]-0.2,0.7))
    return b,[]
def s_dipper(t):
    b=board(); dipper(b,120,180,1.4,wk(t,EV["dipper"]-0.4,1.0))
    write(b,"Big Dipper",200,110,48,wk(t,EV["dipper"]-0.1,0.6))
    k=wk(t,EV["dipper"]+0.4,0.6); stroke(b,circle_pts(420,330,30,seed=3),k,3,PINK)
    stroke(b,[(330,250),(398,312)],k,1.5,PINK,0.7)
    write(b,"nothing here?",360,420,48,wk(t,EV["nothing"]-0.2,0.6),PINK)
    return b,[]
def s_stare(t):
    b=board()
    write(b,"\"a waste of",200,110,50,wk(t,EV["waste"]-0.2,0.5),ORG)
    write(b,"telescope time\"",250,160,50,wk(t,EV["time"]-0.4,0.6),ORG)
    tk=cl((t-EV["ten"]+0.3)/1.6)
    for d in range(10):
        if tk*10>d:
            x=70+d*24 if d%5!=4 else 0
            if d%5==4: stroke(b,[(60+(d//5)*140,300),(170+(d//5)*140,240)],1,3,WH)
            else: stroke(b,[(70+(d//5)*140+(d%5)*24,230),(70+(d//5)*140+(d%5)*24,310)],1,3,WH)
    write(b,"10 days",410,270,56,wk(t,EV["ten"]+0.2,0.6),YEL)
    hubble(b,170,470,0.8,1.0)
    stroke(b,[(250,460),(420,420)],wk(t,EV["stared"]-0.3,0.6),1.5,WH,0.6)
    stroke(b,circle_pts(440,415,24,seed=5),wk(t,EV["stared"]-0.2,0.5),2.5,PINK)
    n=int(342*cl((t-EV["n342"]+0.4)/1.0));
    if n>0: write(b,f"{n} exposures",300,600,52,1.0,BLU)
    return b,[]
def s_reveal(t):
    b=board(); x0,y0,x1,y1=70,120,470,520
    box(b,x0,y0,x1,y1,wk(t,EV["image"]-0.3,0.6))
    g=cl((t-EV["back"])/1.2)
    galaxies(b,x0+8,y0+8,x1-8,y1-8,g)
    if t>EV["galaxy"]-0.3:
        zk=sm((t-EV["galaxy"]+0.3)/0.8); stroke(b,circle_pts(300,290,40,seed=7),zk,2.5,YEL)
        write(b,"not stars: galaxies",270,580,52,wk(t,EV["galaxy"]-0.2,0.6),YEL)
    if t>EV["n3000"]-0.2: write(b,"~3,000",270,80,64,wk(t,EV["n3000"]-0.2,0.5),PINK)
    return b,[]
def s_kinds(t):
    b=board(); cxs=[(105,250),(270,250),(435,250)]
    labs=[("spirals","spirals"),("blobs","blobs"),("smudges","smudges")]
    for i,((x,y),(lb,k_)) in enumerate(zip(cxs,labs)):
        k=wk(t,EV[k_]-0.25,0.6)
        if k<=0: continue
        if i==0:
            for arm in (0,math.pi):
                pts=[(x+math.cos(arm+q*3.4)*50*q,y+math.sin(arm+q*3.4)*30*q) for q in np.linspace(0.1,1.2,30)]; stroke(b,pts,k,3,BLU)
            chalk(b,M().circ(x,y,7),YEL,k)
        elif i==1: chalk(b,M().ell(x,y,44*k+1,30*k+1,20),ORG,0.8); chalk(b,M().ell(x,y,22*k+1,15*k+1,20),YEL,0.9)
        else:
            for q in range(5): chalk(b,M().ell(x-20+q*10,y+(q%2)*8,18,8,30),PINK,0.5*k)
        write(b,lb,x,y+80,40,wk(t,EV[k_]-0.1,0.5))
    write(b,"each = billions of stars",270,480,50,wk(t,EV["billions"]-0.4,0.8),YEL)
    lk=wk(t,EV["light"]-0.3,1.2)
    if lk>0:
        for q in range(3): stroke(b,[(60,515+q*12),(60+400*lk,515+q*12)],1,2,WH,0.7)
        write(b,"light travelling for",270,575,40,wk(t,EV["light"],0.6),BLU); write(b,"billions of years",270,622,40,wk(t,EV["years"]-0.3,0.6),BLU)
    return b,[]
def s_udf(t):
    b=board(); x0,y0,x1,y1=70,140,470,540
    box(b,x0,y0,x1,y1,1.0,BLU)
    write(b,"2004: Ultra Deep Field",270,90,52,wk(t,EV["y2004"]-0.2,0.8),BLU)
    galaxies(b,x0+8,y0+8,x1-8,y1-8,1.0,dens=1.0)
    dk=cl((t-EV["deeper"]+0.2)/1.2)
    if dk>0:
        g2=np.random.default_rng(9)
        for i in range(int(380*dk)): x,y=g2.uniform(x0+8,x1-8),g2.uniform(y0+8,y1-8); chalk(b,M().circ(x,y,g2.uniform(0.8,1.6)),[WH,YEL,PINK,BLU][i%4],0.8,False)
    write(b,"~10,000",270,600,64,wk(t,EV["n10k"]-0.2,0.5),PINK)
    return b,[]
def s_anywhere(t):
    b=board(); cx,cy=270,560
    stroke(b,circle_pts(cx,cy,230,math.pi,2*math.pi,80,1.0,11),1.0,3,WH)
    ak=cl((t-EV["anywhere"]+0.4)/1.4)
    for i,a in enumerate(np.linspace(math.pi*1.12,math.pi*1.88,6)):
        if ak*6>i:
            ex,ey=cx+math.cos(a)*230,cy+math.sin(a)*230
            stroke(b,[(cx,cy),(ex,ey)],1,1.5,WH,0.5)
            chalk(b,M().circ(ex,ey,18),BLU,0.25)
            g2=np.random.default_rng(20+i)
            for q in range(14): chalk(b,M().circ(ex+g2.normal(0,8),ey+g2.normal(0,8),g2.uniform(0.8,1.8)),[YEL,PINK,WH][q%3],0.9,False)
    write(b,"not special",270,110,64,wk(t,EV["special"]-0.3,0.6),PINK)
    write(b,"point anywhere",270,180,52,wk(t,EV["anywhere"]-0.2,0.6))
    write(b,"remember:",270,260,60,wk(t,EV["remember"]-0.3,0.5),YEL)
    return b,[]
TR=0.40; TOTAL=B.TOTAL; LOOPD=0.70
SHOTS=[(0.0,s_hook),(Lx("Near the Big")[0]-0.3,s_dipper),(S("stare")["s"],s_stare),(S("reveal")["s"],s_reveal),(Lx("Spirals")[0]-0.3,s_kinds),
       (S("deeper")["s"],s_udf),(Lx("And that patch")[0]-0.3,s_anywhere)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
def erase(b1,b2,u):
    """a felt eraser zig-zags down the board; the old drawing smears away and the next is chalked in"""
    rows=4; ue=cl(u/0.7); hh=(660-20)/rows
    prog=ue*rows; m=np.zeros((h,w),np.float32)
    for r in range(rows):
        k=cl(prog-r); y0=20+r*hh
        if k<=0: continue
        if r%2==0: m[int(y0):int(y0+hh),:int(w*k)]=1
        else: m[int(y0):int(y0+hh),int(w*(1-k)):]=1
    m=cv2.GaussianBlur(m,(0,0),6)
    blank=board(); smear=cv2.GaussianBlur(b1,(0,0),9)*0.25+blank*0.75
    out=b1*(1-m[...,None])+smear*m[...,None]
    nk=cl((u-0.55)/0.45); out=out*(1-nk)+b2*nk
    if ue<1:
        r=min(rows-1,int(prog)); k=cl(prog-r); y=20+r*hh+hh/2; x=w*k if r%2==0 else w*(1-k)
        er=M().rect(x-46,y-22,x+46,y+22).f(); fill(out,er,(0.40,0.26,0.13)); fill(out,M().rect(x-46,y+10,x+46,y+22).f(),(0.55,0.55,0.55))
    return out
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None: buf,_=SHOTS[i][1](t)
    else:
        fa_,fb_,ta,tb,u=pair; b1,_=fa_(ta); b2,_=fb_(tb); buf=erase(b1,b2,u)
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
