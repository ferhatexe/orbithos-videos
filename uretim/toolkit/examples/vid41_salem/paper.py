# paper-cut diorama toolkit (working res 540x960)
import numpy as np, cv2, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
w,h=540,960; W,H=1080,1920
yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
def cl(x): return min(max(x,0.0),1.0)
def sm(x): x=cl(x); return x*x*(3-2*x)
def eout(x): x=cl(x); return 1-(1-x)**3
def ein(x): x=cl(x); return x*x*x
def fa(t,s,e,fi=0.35,fo=0.35): return sm((t-s)/fi)*(1-sm((t-e)/fo))
def spring(x):  # pop-up overshoot 0->1
    x=max(0.0,x); return 1-math.exp(-6*x)*math.cos(9*x) if x<3 else 1.0
# ---- paper texture (applied to whole frame) ----
_g=np.random.default_rng(11)
_n1=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),0.8)
_n2=cv2.resize(_g.normal(0,1,(h//30,w//30)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC)
_fb=cv2.GaussianBlur(_g.normal(0,1,(h,w)).astype(np.float32),(0,0),sigmaX=7,sigmaY=0.7)
PT=(1+0.022*_n1/_n1.std()+0.03*_n2/_n2.std()+0.018*_fb/_fb.std())[...,None].astype(np.float32)
# ---- mask canvas ----
class M:
    def __init__(s,wd=w,ht=h): s.m=np.zeros((ht,wd),np.uint8); s.x0,s.y0,s.x1,s.y1=wd,ht,0,0; s.wd,s.ht=wd,ht
    def _bb(s,xs,ys,pad=2):
        s.x0=min(s.x0,int(min(xs))-pad); s.y0=min(s.y0,int(min(ys))-pad); s.x1=max(s.x1,int(max(xs))+pad); s.y1=max(s.y1,int(max(ys))+pad)
    def poly(s,pts,v=255):
        p=np.asarray(pts,np.float64)
        if len(p)<3: return s
        cv2.fillPoly(s.m,[np.round(p*16).astype(np.int32)],v,cv2.LINE_AA,shift=4); s._bb(p[:,0],p[:,1]); return s
    def circ(s,cx,cy,r,v=255):
        if r<0.5: return s
        cv2.circle(s.m,(int(round(cx*16)),int(round(cy*16))),int(round(r*16)),v,-1,cv2.LINE_AA,4); s._bb([cx-r,cx+r],[cy-r,cy+r]); return s
    def ell(s,cx,cy,ax,ay,ang=0,v=255):
        cv2.ellipse(s.m,(int(round(cx*16)),int(round(cy*16))),(max(1,int(ax*16)),max(1,int(ay*16))),ang,0,360,v,-1,cv2.LINE_AA,4); r=max(ax,ay); s._bb([cx-r,cx+r],[cy-r,cy+r]); return s
    def line(s,p0,p1,th,v=255):
        cv2.line(s.m,(int(round(p0[0]*16)),int(round(p0[1]*16))),(int(round(p1[0]*16)),int(round(p1[1]*16))),v,max(1,int(round(th))),cv2.LINE_AA,4); s._bb([p0[0]-th,p1[0]+th,p0[0]+th,p1[0]-th],[p0[1]-th,p1[1]+th,p0[1]+th,p1[1]-th]); return s
    def pline(s,pts,th,v=255):
        p=np.asarray(pts,np.float64)
        if len(p)<2: return s
        cv2.polylines(s.m,[np.round(p*16).astype(np.int32)],False,v,max(1,int(round(th))),cv2.LINE_AA,4); s._bb(p[:,0]-th,p[:,1]-th); s._bb(p[:,0]+th,p[:,1]+th); return s
    def rect(s,x0,y0,x1,y1,v=255): return s.poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],v)
    def f(s): return s.m.astype(np.float32)/255
def comp(buf,m,col,sh=0.30,dx=2,dy=4,blur=3.5,a=1.0,rim=0.10,ox=0,oy=0):
    """composite a paper layer (M or float mask) with drop shadow and lit top rim"""
    if isinstance(m,M):
        if m.x1<=m.x0: return
        pad=int(blur*3)+max(abs(dx),abs(dy))+2
        x0,y0=max(0,m.x0-pad+ox),max(0,m.y0-pad+oy); x1,y1=min(w,m.x1+pad+ox),min(h,m.y1+pad+oy)
        if x1<=x0 or y1<=y0: return
        src=np.zeros((y1-y0,x1-x0),np.float32)
        sx0,sy0=x0-ox,y0-oy; sx1,sy1=x1-ox,y1-oy
        cx0,cy0=max(0,sx0),max(0,sy0); cx1,cy1=min(m.wd,sx1),min(m.ht,sy1)
        if cx1>cx0 and cy1>cy0: src[cy0-sy0:cy1-sy0,cx0-sx0:cx1-sx0]=m.m[cy0:cy1,cx0:cx1].astype(np.float32)/255
        A=src; B=buf[y0:y1,x0:x1]
    else:
        A=m; B=buf
    A=A*a
    if sh>0:
        s=cv2.GaussianBlur(A,(0,0),blur); s=shift(s,dx,dy); B*=(1-sh*s)[...,None]
    c=np.array(col,np.float32)
    B+=(c-B)*A[...,None]
    if rim>0:
        r=np.clip(A-shift(A,0,2),0,1); B+=(r*rim)[...,None]
def shift(a,dx,dy):
    o=np.zeros_like(a); H_,W_=a.shape[:2]
    if abs(dy)>=H_ or abs(dx)>=W_: return o
    ys,yd=(slice(0,H_-dy),slice(dy,H_)) if dy>=0 else (slice(-dy,H_),slice(0,H_+dy))
    xs,xd=(slice(0,W_-dx),slice(dx,W_)) if dx>=0 else (slice(-dx,W_),slice(0,W_+dx))
    o[yd,xd]=a[ys,xs]; return o
def grad(buf,stops):
    ys=[s[0] for s in stops];
    for c in range(3): buf[...,c]=np.interp(yy[:,0],ys,[s[1][c] for s in stops])[:,None]
def rgrad(buf,cx,cy,r,col,a):
    d2=((xx-cx)**2+(yy-cy)**2)/(r*r); buf+=(np.exp(-d2)*a)[...,None]*np.array(col,np.float32)
def lerpc(a,b,k): return tuple(a[i]*(1-k)+b[i]*k for i in range(3))
def rot(pts,ang,cx=0,cy=0,sx=1.0,sy=1.0):
    c,s=math.cos(ang),math.sin(ang); out=[]
    for x,y in pts: x*=sx; y*=sy; out.append((cx+x*c-y*s,cy+x*s+y*c))
    return out
# ---- shapes ----
def leaf_pts(L,Wd,n=14,curl=0.0):
    pts=[]
    for i in range(n+1):
        u=i/n; pts.append((u*L,-Wd*math.sin(math.pi*u)**0.85+curl*L*u*u))
    for i in range(n,-1,-1):
        u=i/n; pts.append((u*L,Wd*math.sin(math.pi*u)**0.85+curl*L*u*u))
    return pts
def leaf(m,x,y,L,Wd,ang,curl=0.0): return m.poly(rot(leaf_pts(L,Wd,curl=curl),ang,x,y))
def blob(m,cx,cy,r,seed,k=7):
    g=np.random.default_rng(seed); m.circ(cx,cy,r)
    for i in range(k):
        a=g.uniform(0,6.283); d=r*g.uniform(0.45,0.85); m.circ(cx+math.cos(a)*d,cy+math.sin(a)*d*0.8,r*g.uniform(0.45,0.7))
    return m
def cloud(m,cx,cy,r,seed):
    g=np.random.default_rng(seed)
    for i in range(6):
        x=cx+(i-2.5)*r*0.55+g.uniform(-r*0.1,r*0.1); m.circ(x,cy-g.uniform(0,r*0.35)*(1-abs(i-2.5)/3),r*g.uniform(0.45,0.7)*(1-abs(i-2.5)/5))
    m.rect(cx-r*1.55,cy,cx+r*1.55,cy+r*0.35)
    return m
def ridge(Wd,y0,amp,seed,step=18,oct=3):
    g=np.random.default_rng(seed); xs=np.arange(-step,Wd+2*step,step); y=np.zeros(len(xs))
    for o in range(oct):
        k=2**o; ph=g.uniform(0,6.283,4); y+=sum(np.sin(xs/(160/k)*g.uniform(0.6,1.4)+ph[j]) for j in range(2))*amp/k/2
    return [(-step,h+50)]+list(zip(xs,y0+y))+[(Wd+2*step,h+50)]
# ---- PIL cards ----
FD="/mnt/skills/examples/canvas-design/canvas-fonts/" if __import__("os").path.isdir("/mnt/skills/examples/canvas-design/canvas-fonts/") else "/home/claude/toolkit/assets/fonts/"; _FC={}
def F(n,s):
    k=(n,s)
    if k not in _FC: _FC[k]=ImageFont.truetype(FD+n+".ttf",s)
    return _FC[k]
_CC={}
def _card_img(s,fn,fs,fg,bg,ang,pad,torn,lsp):
    k=(s,fn,fs,fg,bg,round(ang,1),pad,torn,lsp)
    if k in _CC: return _CC[k]
    f=F(fn,fs); lines=s.split("\n"); d0=ImageDraw.Draw(Image.new("RGBA",(4,4)))
    bbs=[d0.textbbox((0,0),ln,font=f) for ln in lines]; tw=max(b[2]-b[0] for b in bbs); lh=int(fs*lsp); th=lh*len(lines)
    cw,ch=tw+2*pad[0],th+2*pad[1]; m=24; im=Image.new("RGBA",(cw+2*m,ch+2*m),(0,0,0,0))
    g=np.random.default_rng(abs(hash(s))%999)
    if bg is not None:
        if torn:
            pts=[(m,m)]+[(m+cw*u,m+g.uniform(-2,2)) for u in np.linspace(0.1,0.9,8)]+[(m+cw,m)]
            pts+=[(m+cw+g.uniform(-5,5),m+ch*u) for u in np.linspace(0.08,0.92,9)]+[(m+cw,m+ch)]
            pts+=[(m+cw*u,m+ch+g.uniform(-2,2)) for u in np.linspace(0.9,0.1,8)]+[(m,m+ch)]+[(m+g.uniform(-5,5),m+ch*u) for u in np.linspace(0.92,0.08,9)]
        else: pts=[(m,m),(m+cw,m),(m+cw,m+ch),(m,m+ch)]
        sh=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(sh).polygon([(x+4,y+7) for x,y in pts],fill=(0,0,0,110)); sh=sh.filter(ImageFilter.GaussianBlur(6))
        im.alpha_composite(sh); ImageDraw.Draw(im).polygon(pts,fill=bg+(255,))
    d=ImageDraw.Draw(im)
    for i,ln in enumerate(lines):
        b=bbs[i]; lw=b[2]-b[0]
        d.text((m+cw/2-lw/2-b[0],m+pad[1]+i*lh+(lh-fs)/2-b[1]*0.0),ln,font=f,fill=fg+(255,))
    if abs(ang)>0.01: im=im.rotate(ang,resample=Image.BICUBIC,expand=True)
    _CC[k]=im; return im
def card(d,s,x,y,fs=44,a=1.0,fg=(28,30,36),bg=(250,245,232),fn="WorkSans-Bold",ang=0.0,pad=(26,14),torn=True,sc=1.0,lsp=1.18):
    if a<=0.01 or sc<=0.02: return
    im=_card_img(s,fn,fs,fg,bg,ang,pad,torn,lsp)
    if abs(sc-1)>0.01:
        q=max(0.05,round(sc*20)/20); im=im.resize((max(1,int(im.width*q)),max(1,int(im.height*q))),Image.BILINEAR)
    if a<0.99:
        arr=np.array(im); arr[...,3]=(arr[...,3]*a).astype(np.uint8); im=Image.fromarray(arr)
    x0,y0=int(x-im.width/2),int(y-im.height/2); paste(d,im,x0,y0)
def paste(d,p,x0,y0):
    x0,y0=int(x0),int(y0); sx,sy=max(0,-x0),max(0,-y0)
    if x0>=W or y0>=H or x0+p.width<=0 or y0+p.height<=0: return
    d._image.alpha_composite(p,(max(0,x0),max(0,y0)),(sx,sy))
