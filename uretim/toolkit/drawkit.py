"""Shared line/shape drawing helpers on the 540x960 float canvas (import after paper). Set drawkit.INK for default ink colour."""
import numpy as np, cv2, math
from paper import M, comp, w, h, xx, yy
INK=(0.1,0.1,0.1)
def _bb(m):
    x0,y0=max(0,m.x0),max(0,m.y0); x1,y1=min(w,m.x1),min(h,m.y1); return x0,y0,x1,y1
def ink(buf,m,a=1.0,col=None): comp(buf,m,INK if col is None else col,sh=0,rim=0,a=a)
def addm(buf,m,col,a=1.0):
    if m.x1<=m.x0: return
    x0,y0,x1,y1=_bb(m)
    if x1<=x0 or y1<=y0: return
    A=m.m[y0:y1,x0:x1].astype(np.float32)*(a/255); buf[y0:y1,x0:x1]+=A[...,None]*np.array(col,np.float32)
def outl(buf,m,a=1.0,th=1,fill=0.10,col=None,fcol=None):
    col=INK if col is None else col
    if m.x1<=m.x0 or a<=0: return
    x0,y0,x1,y1=_bb(m)
    if x1<=x0 or y1<=y0: return
    A=m.m[y0:y1,x0:x1].astype(np.float32)/255; k=2*th+1
    er=cv2.erode(A,np.ones((k,k),np.uint8)); e=np.clip(A-er,0,1)
    Bf=buf[y0:y1,x0:x1]; c=np.array(col,np.float32); fc=np.array(fcol if fcol else col,np.float32)
    Bf+=(fc-Bf)*(A*fill*a)[...,None]; Bf+=(c-Bf)*(e*a)[...,None]
def hatch(buf,m,a=0.5,step=7,col=None,dirn=1):
    col=INK if col is None else col
    if m.x1<=m.x0: return
    x0,y0,x1,y1=_bb(m); A=m.m[y0:y1,x0:x1].astype(np.float32)/255
    pat=(((xx[y0:y1,x0:x1]+dirn*yy[y0:y1,x0:x1])%step)<1.3).astype(np.float32)
    Bf=buf[y0:y1,x0:x1]; Bf+=(np.array(col,np.float32)-Bf)*(A*pat*a)[...,None]
def wash(buf,x,y,r,col,a=1.0):
    R=int(r*2.5)+1; x0,y0=max(0,int(x)-R),max(0,int(y)-R); x1,y1=min(w,int(x)+R),min(h,int(y)+R)
    if x1<=x0 or y1<=y0 or a<=0: return
    d2=((xx[y0:y1,x0:x1]-x)**2+(yy[y0:y1,x0:x1]-y)**2)/(r*r); k=(np.exp(-d2)*a)[...,None]
    Bf=buf[y0:y1,x0:x1]; Bf+=(np.array(col,np.float32)-Bf)*k
def glow(buf,x,y,r,col,a=1.0):
    R=int(r*3)+1; x0,y0=max(0,int(x)-R),max(0,int(y)-R); x1,y1=min(w,int(x)+R),min(h,int(y)+R)
    if x1<=x0 or y1<=y0 or a<=0: return
    d2=((xx[y0:y1,x0:x1]-x)**2+(yy[y0:y1,x0:x1]-y)**2)/(r*r); buf[y0:y1,x0:x1]+=(np.exp(-d2)*a)[...,None]*np.array(col,np.float32)
def part(pts,u):
    p=np.asarray(pts,np.float64)
    if u>=1: return p
    if u<=0 or len(p)<2: return p[:1]
    sl=np.hypot(*np.diff(p,axis=0).T); cs=np.concatenate([[0],np.cumsum(sl)]); L=cs[-1]*u
    k=np.searchsorted(cs,L)-1; k=min(max(k,0),len(sl)-1); f=(L-cs[k])/max(sl[k],1e-9)
    return np.vstack([p[:k+1],p[k]+(p[k+1]-p[k])*f])
def dl(m,pts,u=1.0,th=1.4):
    q=part(pts,u)
    if len(q)>=2: m.pline(q,th)
    return m
def circ_pts(cx,cy,rx,ry=None,a0=0,a1=2*math.pi,n=72):
    ry=rx if ry is None else ry
    return [(cx+rx*math.cos(a0+(a1-a0)*i/n),cy+ry*math.sin(a0+(a1-a0)*i/n)) for i in range(n+1)]
def dashl(m,p0,p1,seg=6,gap=5,th=1.0):
    L=math.hypot(p1[0]-p0[0],p1[1]-p0[1])+1e-6; n=int(L/(seg+gap))+1
    for k in range(n):
        a=k*(seg+gap)/L; b=min(1,(k*(seg+gap)+seg)/L)
        if a<1: m.line((p0[0]+(p1[0]-p0[0])*a,p0[1]+(p1[1]-p0[1])*a),(p0[0]+(p1[0]-p0[0])*b,p0[1]+(p1[1]-p0[1])*b),th)
    return m
def dim(m,p0,p1,th=1.2,u=1.0):
    p1=(p0[0]+(p1[0]-p0[0])*u,p0[1]+(p1[1]-p0[1])*u)
    m.line(p0,p1,th); dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)+1e-6; ux,uy=dx/L,dy/L; px,py=-uy,ux
    for (x,y),s in ((p0,1),(p1,-1)):
        m.line((x,y),(x+s*ux*9+px*4,y+s*uy*9+py*4),th); m.line((x,y),(x+s*ux*9-px*4,y+s*uy*9-py*4),th)
        m.line((x-px*7,y-py*7),(x+px*7,y+py*7),th)
    return m
def rotp(pts,ang,cx,cy):
    c,s=math.cos(ang),math.sin(ang); return [(cx+(x-cx)*c-(y-cy)*s,cy+(x-cx)*s+(y-cy)*c) for x,y in pts]
