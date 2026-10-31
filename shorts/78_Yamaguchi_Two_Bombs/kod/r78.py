import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid78"); sys.path.insert(0,"/home/claude/toolkit")
from pro import *
from PIL import Image, ImageDraw
T,LINES,SC,TOTAL=load("timeline.json")
CAP=Captions(LINES); WD=CAP.W
def wt(li,sub,o=0.0): return word_t(WD,li,sub,o)
def Ls(i): return LINES[i]["s"]
def sm_np(x): x=np.clip(x,0,1); return x*x*(3-2*x)
# ================= sumi-e ink wash on washi paper, red sun; ink-bleed transitions =================
PAPER=(np.array([0.93,0.89,0.80],np.float32)*(0.94+0.05*fbm((h,w),781,6,8))[...,None]+np.random.default_rng(2).normal(0,0.012,(h,w,1)).astype(np.float32))
INK=np.array([0.08,0.07,0.07],np.float32); RED=np.array([0.80,0.12,0.10],np.float32)
FIB=fbm((h,w),782,5,5)
def wash(b,mask,a=1.0,col=INK):
    m=np.clip(mask*(0.85+0.25*FIB),0,1)[...,None]*a; return b*(1-m)+col*m
def mountains(y0,amp,seed,soft=8):
    g=np.random.default_rng(seed); xs=np.arange(0,w+20,20); n=np.cumsum(g.normal(0,1,len(xs))); n=(n-n.mean())/(n.std()+1e-6)
    r=np.interp(np.arange(w),xs,y0+amp*n); m=(yy>r[None,:]).astype(np.float32)
    m=cv2.GaussianBlur(m,(0,0),soft); fade=np.clip(1-(yy-r[None,:])/(h*0.35),0.15,1); return m*fade
M1=mountains(h*0.55,40,1)*0.7; M2=mountains(h*0.66,30,2,4)*0.85
def sun(b,x,y,r,a=1.0):
    m=np.zeros((h,w),np.float32); cv2.circle(m,(int(x),int(y)),int(r),1.0,-1,cv2.LINE_AA); m=cv2.GaussianBlur(m,(0,0),2); return wash(b,m,a,RED)
def city(b,dome=True,a=1.0):
    m=np.zeros((h,w),np.float32); g=np.random.default_rng(45); x=0; base=h*0.80
    while x<w:
        bw=g.uniform(30,80); bh=g.uniform(30,110); cv2.rectangle(m,(int(x),int(base-bh)),(int(x+bw),h),1.0,-1); x+=bw+g.uniform(2,10)
    if dome:
        cx=w*0.62; cv2.rectangle(m,(int(cx-60),int(base-150)),(int(cx+60),h),1.0,-1); cv2.ellipse(m,(int(cx),int(base-150)),(42,48),0,180,360,1.0,-1,cv2.LINE_AA)
    return wash(b,cv2.GaussianBlur(m,(0,0),1.5),0.92*a)
def bloom_cloud(b,x,y,k,a=1.0):
    m=np.zeros((h,w),np.float32); r=int(30+190*k)
    cv2.circle(m,(int(x),int(y-260*k)),r,1.0,-1,cv2.LINE_AA); cv2.rectangle(m,(int(x-24-10*k),int(y-260*k)),(int(x+24+10*k),int(y)),1.0,-1)
    m=cv2.GaussianBlur(m,(0,0),18); m*=np.clip(0.55+0.6*fbm((h,w),int(783),4,6),0,1)
    return wash(b,m,0.55*a,np.array([0.25,0.24,0.24],np.float32))
def flash(b,k): return b*(1-k)+np.array([1.0,0.98,0.92],np.float32)*k
# ---------- shots ----------
def sh_hook(t,end=False):
    tt=t-TOTAL if end else t; b=PAPER.copy(); b=sun(b,w*0.5,h*0.40,150+4*math.sin(t)); b=wash(b,M1,0.35); b=wash(b,M2,0.7)
    return b,None,1.02+0.03*sm(max(tt,0)/3)
def sh_hiro(t):
    u=t-Ls(1); b=PAPER.copy(); b=wash(b,M1,0.25); b=city(b,True)
    tb=wt(1,"three")-0.6; k=cl((t-tb)/2.0)
    if t>tb: b=bloom_cloud(b,w*0.45,h*0.80,eout(k)); b=flash(b,max(0,1-(t-tb)/0.35)*0.9)
    def hud(img):
        label(img,"AUG 6, 1945",540,280,120,(20,18,18),stroke=0,a=fa(t,Ls(1),99,0.2,0.2)); label(img,"HIROSHIMA",540,390,70,(200,30,25),stroke=0,a=fa(t,Ls(1)+0.3,99,0.2,0.2))
        label(img,"~3 KM AWAY",540,1010,64,(20,18,18),stroke=0,a=fa(t,wt(1,"kilometers")-0.1,99,0.15,0.2))
    return b,hud,1.0+0.03*u
def sh_travel(t):
    u=t-Ls(2); b=PAPER.copy(); b=wash(b,M2,0.3)
    def hud(img):
        d=ImageDraw.Draw(img); x0,y0,x1,y1=230,620,850,880
        d.line([(x0,y0),(540,y0+60),(x1,y1)],fill=(30,28,28,200),width=6,joint="curve")
        for (x,y,n,c) in ((x0,y0,"HIROSHIMA",(30,28,28)),(x1,y1,"NAGASAKI",(200,30,25))):
            d.ellipse((x-18,y-18,x+18,y+18),fill=c+(255,)); label(img,n,x,y-60,48,c,stroke=0)
        k=sm(u/2.8); px=x0+(x1-x0)*k; py=y0+(y1-y0)*k+math.sin(k*math.pi)*30
        d.rounded_rectangle((px-34,py-20,px+34,py+20),8,fill=(20,18,18,255))
        label(img,"~300 KM HOME",540,330,96,(20,18,18),stroke=0,a=fa(t,Ls(2)+0.2,99,0.2,0.2))
    return b,hud,1.0+0.02*u
def sh_naga(t):
    u=t-Ls(3); b=PAPER.copy()
    m=np.zeros((h,w),np.float32); cv2.rectangle(m,(int(w*0.15),int(h*0.28)),(int(w*0.85),int(h*0.62)),1.0,8)
    cv2.line(m,(int(w*0.5),int(h*0.28)),(int(w*0.5),int(h*0.62)),1.0,6); cv2.line(m,(int(w*0.15),int(h*0.45)),(int(w*0.85),int(h*0.45)),1.0,6)
    for x,s in ((w*0.30,1.0),(w*0.66,0.95)):
        cv2.circle(m,(int(x),int(h*0.70)),int(34*s),1.0,-1,cv2.LINE_AA); cv2.ellipse(m,(int(x),int(h*0.86)),(int(70*s),int(110*s)),0,180,360,1.0,-1,cv2.LINE_AA)
    cv2.rectangle(m,(int(w*0.20),int(h*0.86)),(int(w*0.80),int(h*0.88)),1.0,-1)
    b=wash(b,cv2.GaussianBlur(m,(0,0),1.2),0.9)
    tb=wt(3,"Nagasaki")-0.1
    if t>tb: k=max(0,1-(t-tb)/0.5); win=np.zeros((h,w),np.float32); cv2.rectangle(win,(int(w*0.15),int(h*0.28)),(int(w*0.85),int(h*0.62)),1.0,-1); b=b*(1-win[...,None]*k)+np.array([1.2,1.15,1.0],np.float32)*win[...,None]*k; b=flash(b,k*0.6)
    def hud(img):
        label(img,"AUG 9, 1945",540,280,120,(20,18,18),stroke=0,a=fa(t,Ls(3),99,0.2,0.2)); label(img,"NAGASAKI",540,390,70,(200,30,25),stroke=0,a=fa(t,Ls(3)+0.3,99,0.2,0.2))
    return b,hud,1.0+0.03*u
def sh_later(t):
    u=t-Ls(4); b=PAPER.copy(); b=sun(b,w*0.5,h*(0.58-0.12*sm(u/3)),120); b=wash(b,M1,0.3); b=wash(b,M2,0.75)
    def hud(img):
        label(img,"SURVIVED. AGAIN.",540,280,110,(200,30,25),stroke=0,a=fa(t,wt(4,"survived")-0.1,99,0.15,0.2))
        label(img,"1916 – 2010",540,400,70,(20,18,18),stroke=0,a=fa(t,wt(4,"93")-0.1,99,0.15,0.2))
        label(img,"ANTI-NUCLEAR VOICE",540,1010,56,(20,18,18),stroke=0,a=fa(t,wt(4,"nuclear")-0.1,99,0.15,0.2))
    return b,hud,1.0+0.02*u
def sh_end(t):
    b,_,z=sh_hook(t,True)
    def hud(img):
        if t<TOTAL-0.7:
            a=fa(t,wt(5,"officially")-0.1,TOTAL-0.7,0.15,0.2); d=ImageDraw.Draw(img); r=110
            d.ellipse((820-r,560-r,820+r,560+r),outline=(200,30,25,int(255*a)),width=12); label(img,"2009",820,560,74,(200,30,25),a=a,stroke=0)
            label(img,"OFFICIALLY RECOGNIZED",540,330,80,(20,18,18),a=a,stroke=0)
    return b,hud,z
SHOTS=[(0.0,sh_hook,"cut"),(Ls(1)-0.25,sh_hiro,"ink"),(Ls(2)-0.25,sh_travel,"ink"),(Ls(3)-0.25,sh_naga,"ink"),(Ls(4)-0.25,sh_later,"ink"),(Ls(5)-0.25,sh_end,"ink")]
TR=0.25
def shot_at(t):
    i=0
    for k,s in enumerate(SHOTS):
        if t>=s[0]: i=k
    return i
def render_shot(i,t):
    b,hud,z=SHOTS[i][1](t); z*=punch(t,[SHOTS[i][0]] if i>0 else [],0.05,0.32)
    dx,dy=shake(t,wt(1,"three")-0.6,6,0.5); d2=shake(t,wt(3,"Nagasaki")-0.1,6,0.5)
    return camera(b,z,0.5,0.45,dx+d2[0],dy+d2[1]),hud
INKN=fbm((h,w),790,5,4)
def ink(b1,b2,u):
    r=np.sqrt((xx-w*0.5)**2+(yy-h*0.45)**2)/(w*1.1)+INKN*0.12
    k=eout(u)*1.25; m=sm_np((k-r)/0.04)[...,None]; edge=np.exp(-((r-k)/0.035)**2)[...,None]
    return b1*(1-m)+b2*m-edge*0.75*(1-u)
def compose(t,fi=None):
    if fi is None: fi=int(round(t*30))
    i=shot_at(max(t,0)); nxt=SHOTS[i+1] if i+1<len(SHOTS) else None; huds=[]
    if nxt and nxt[2]=="ink" and t>nxt[0]-TR:
        u=(t-(nxt[0]-TR))/(2*TR); b1,_=render_shot(i,t); b2,_=render_shot(i+1,t); b=ink(b1,b2,u)
    elif SHOTS[i][2]=="ink" and t<SHOTS[i][0]+TR and i>0:
        u=(t-(SHOTS[i][0]-TR))/(2*TR); b1,_=render_shot(i-1,t); b2,h2=render_shot(i,t); b=ink(b1,b2,u); huds=[h2] if u>0.8 else []
    else:
        b,h1=render_shot(i,t); huds=[h1]
    b=np.clip(b,0,1.1)*(0.80+0.20*VIG)*1.06
    img=to_img(b,fi)
    for hf in huds:
        if hf: hf(img)
    ha=1-sm((t-(Ls(1)-0.4))/0.25) if t<Ls(1) else sm((t-(TOTAL-0.55))/0.3)
    if ha>0.01:
        hook_title(img,[("SURVIVED TWO",WHITE)],a=ha,y=250,size=130)
        s2=wt(0,"atomic")-0.05
        if t>=s2 or t>TOTAL-0.55:
            a2=ha*(sm((t-s2)/0.08) if t<Ls(1) else 1.0); sc=0.7+0.3*spring((t-s2)/0.22) if t<Ls(1) else 1.0
            hook_title(img,[("ATOMIC BOMBS",(230,40,35))],a=a2,y=395,size=150,sc=sc)
    return finish(img,CAP,t)
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
