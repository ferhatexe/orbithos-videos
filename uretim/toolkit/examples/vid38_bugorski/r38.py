import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid38")
for p in ["/home/claude/vid38","/home/claude/vid3","/home/claude/ep1"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
from paper import *
from PIL import Image, ImageDraw
EV=ev.EV; Lx=ev.Lx; SS=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
LOGO=E1.LOGO
CR=(0.93,0.88,0.78); RD=(0.80,0.13,0.11); BK=(0.10,0.09,0.09); GY=(0.55,0.52,0.48); YL=(0.98,0.80,0.25)
cR=(205,35,30); cK=(25,22,22); cC=(238,226,200); cY=(250,205,65)
BS="BigShoulders-Bold"
def blk(d,s,x,y,fs,a=1.0,fg=cC,bg=cR,ang=0,sc=1.0,pad=(26,6)):
    card(d,s,x,y,fs=fs,a=a,fg=fg,bg=bg,fn=BS,torn=False,ang=ang,sc=sc,pad=pad)
def pop(t,e): return spring((t-e)/0.5)
# halftone dot field (precomputed)
HT=np.zeros((h,w),np.float32)
for y in range(0,h,8):
    for x in range(0,w,8): cv2.circle(HT,(x+(4 if (y//8)%2 else 0),y),2,1.0,-1,cv2.LINE_AA)
def halftone(buf,mask,col,a=1.0):
    m=HT*mask*a; buf+=(np.array(col,np.float32)-buf)*m[...,None]
# head profile (facing right) normalized
PROF=[(-0.55,-0.10),(-0.52,-0.42),(-0.34,-0.66),(-0.05,-0.76),(0.25,-0.68),(0.42,-0.50),(0.48,-0.24),(0.50,-0.12),(0.64,0.04),(0.66,0.08),(0.52,0.12),(0.55,0.20),(0.50,0.26),(0.53,0.31),(0.46,0.40),(0.36,0.47),(0.22,0.50),(0.18,0.80),(-0.28,0.80),(-0.30,0.42),(-0.50,0.18)]
def _cr(P_,n=8):
    P_=np.array(P_); out=[]; L=len(P_)
    for i in range(L-1):
        p0,p1,p2,p3=P_[max(i-1,0)],P_[i],P_[i+1],P_[min(i+2,L-1)]
        for u in np.linspace(0,1,n,endpoint=False):
            out.append(0.5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u**3))
    out.append(P_[-1]); return [tuple(p) for p in out]
PROFS=_cr(PROF[:17])+[PROF[17],PROF[18]]+_cr(PROF[18:]+[PROF[0]])
def head(buf,cx,cy,s,col=BK,ang=0.0,a=1.0,sh=0.18,swell=0.0):
    pts=[(px*s,py*s) for px,py in PROFS]; m=M().poly(rot(pts,ang,cx,cy))
    if swell>0: m.ell(*rot([(0.30*s,0.05*s)],ang,cx,cy)[0],0.30*s*swell,0.36*s*swell,math.degrees(ang))
    comp(buf,m,col,sh=sh,rim=0,a=a); return lambda px,py: rot([(px*s,py*s)],ang,cx,cy)[0]
def sunburst(buf,cx,cy,r,n,t,col,a=1.0,spd=0.2):
    m=M()
    for k in range(n):
        a0=k*2*math.pi/n+t*spd; m.poly([(cx,cy),(cx+r*math.cos(a0),cy+r*math.sin(a0)),(cx+r*math.cos(a0+math.pi/n),cy+r*math.sin(a0+math.pi/n))])
    comp(buf,m,col,sh=0,rim=0,a=a)
def beamline(buf,p0,p1,u,th=5,a=1.0,glow=True):
    if u<=0: return
    x=p0[0]+(p1[0]-p0[0])*u; y=p0[1]+(p1[1]-p0[1])*u
    if glow:
        g=M().line(p0,(x,y),th*4); comp(buf,g,YL,sh=0,rim=0,a=0.35*a)
    comp(buf,M().line(p0,(x,y),th),(1,0.97,0.85),sh=0,rim=0,a=a)
def bg(buf,col=CR,diag=None):
    buf[:]=col
    if diag:
        c,ang,off,wd=diag; d_=(xx*math.cos(ang)+yy*math.sin(ang))-off; m=(np.abs(d_)<wd).astype(np.float32); buf+=(np.array(c,np.float32)-buf)*m[...,None]
# ================= scenes =================
def s_hook(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    bg(buf,CR,(RD,-0.6,520,90) if t<EV["flash"] else None)
    fl=sm((t-EV["flash"]+0.1)/0.25)*(1-sm((t-EV["nopain"]-0.5)/0.6))
    if fl>0: sunburst(buf,300,380,900,24,t,YL,a=fl); comp(buf,M().circ(300,380,120+40*fl),(1,0.97,0.85),sh=0,a=fl)
    else: comp(buf,M().circ(330,330,170),RD,sh=0.12)
    P=head(buf,260,400,330)
    bp=sm((t-EV["protons"]+0.2)/0.9)
    beamline(buf,(-20,P(-0.6,-0.08)[1]),(w+20,P(0.8,0.06)[1]),bp,th=4+2*fl)
    dk=sm((t-EV["expected"]+0.2)/0.6)*(1-sm((t-EV["didnt"])/0.5)); buf*=1-0.45*dk
    def hd(d,t=t):
        blk(d,"1978",250,230,130,a=fa(t,EV["y1978"]-0.1,EV["protons"]-0.4),sc=pop(t,EV["y1978"]-0.1))
        blk(d,"A PARTICLE ACCELERATOR",540,1180,46,a=fa(t,EV["acc"]-0.1,EV["protons"]-0.4),fg=cC,bg=cK,ang=-3)
        blk(d,"≈ SPEED OF LIGHT",740,250,52,a=fa(t,EV["light"]-0.1,EV["flash"]-0.3),fg=cC,bg=cK,ang=3,sc=pop(t,EV["light"]-0.1))
        blk(d,"BRIGHTER THAN\n1,000 SUNS",540,240,72,a=fa(t,EV["suns"]-0.1,EV["expected"]-0.3),fg=cK,bg=cY,ang=-3,sc=pop(t,EV["suns"]-0.1))
        blk(d,"NO PAIN",540,1180,64,a=fa(t,EV["nopain"]-0.1,EV["expected"]-0.3),ang=3)
        blk(d,"DAYS TO LIVE?",540,260,80,a=fa(t,EV["expected"]-0.1,EV["didnt"]-0.1),fg=cC,bg=cK)
        blk(d,"HE DIDN'T DIE.",540,260,96,a=fa(t,EV["didnt"]-0.05,sc["e"]+1),sc=pop(t,EV["didnt"]-0.05))
    hud.append(hd); return buf,hud
def s_lab(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    bg(buf,CR,(RD,0.7,620,60))
    rg=sm((t-EV["u70"]+0.6)/0.8)
    if rg<1:
        a=1-rg; P=head(buf,170,460,300,a=a)
        comp(buf,M().rect(330,170,520,560),BK,sh=0.15,a=a)
        for k in range(6): comp(buf,M().rect(350,200+k*55,500,230+k*55),RD if k%2 else GY,sh=0,rim=0,a=a)
    if rg>0:
        cx,cy,R=270,380,200
        ring=M().circ(cx,cy,R+14); inner=M().circ(cx,cy,R-14); ring.m=np.clip(ring.m.astype(np.int16)-inner.m,0,255).astype(np.uint8); comp(buf,ring,BK,sh=0.2,a=rg)
        mg=M()
        for k in range(24):
            a0=k*2*math.pi/24; mg.poly(rot([(-10,-24),(10,-24),(10,24),(-10,24)],a0,cx+R*math.cos(a0),cy+R*math.sin(a0)))
        comp(buf,mg,RD,sh=0.15,a=rg)
        sp=1.2+5*sm((t-EV["push"])/1.5)
        for k in range(6):
            a0=t*sp+k*2*math.pi/6
            for j in range(6): rgrad(buf,cx+R*math.cos(a0-j*0.04),cy+R*math.sin(a0-j*0.04),6-j*0.7,YL,0.9*rg*(1-j/6))
        halftone(buf,(((xx-cx)**2+(yy-cy)**2)<(R-20)**2).astype(np.float32),RD,0.5*rg)
    def hd(d,t=t,rg=rg):
        a=fa(t,EV["name"]-0.1,EV["u70"]-0.5)
        blk(d,"ANATOLI BUGORSKI",540,200,78,a=a,sc=pop(t,EV["name"]-0.1))
        blk(d,"AGE 36 · PHYSICIST",540,300,44,a=a*sm((t-EV["age"])/0.3),fg=cC,bg=cK)
        blk(d,"PROTVINO · SOUTH OF MOSCOW",540,1180,40,a=a*sm((t-EV["prot"])/0.3),fg=cC,bg=cK,ang=-2)
        blk(d,"U-70 SYNCHROTRON",540,200,72,a=fa(t,EV["u70"]-0.1,sc["e"]+1),sc=pop(t,EV["u70"]-0.1))
        blk(d,"≈ 1.5 KM",540,760,90,a=fa(t,EV["km"]-0.1,sc["e"]+1),fg=cK,bg=cY,ang=-4,sc=pop(t,EV["km"]-0.1))
    hud.append(hd); return buf,hud
def s_accident(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    bg(buf,(0.86,0.82,0.74))
    al=sm((t-EV["path"]+0.1)/0.2)
    if al>0 and int(t*4)%2==0: buf[:]=buf*0.85+np.array(RD,np.float32)*0.15
    py=470
    comp(buf,M().rect(-5,py-26,w+5,py+26),GY,sh=0.3); comp(buf,M().rect(-5,py-4,w+5,py+4),RD,sh=0,rim=0)
    for x in range(-40,w+40,120): comp(buf,M().rect(x+((t*600)%120)-10,py-30,x+((t*600)%120)+10,py+30),BK,sh=0.1,rim=0,a=0.0)
    comp(buf,M().rect(330,py-110,470,py-26),BK,sh=0.2); comp(buf,M().rect(345,py-96,455,py-60),(0.25,0.3,0.28),sh=0,rim=0)
    for k in range(3):
        e=EV["failed"]+k*0.25; on=t<e; x=120+k*70
        comp(buf,M().circ(x,180,24),BK,sh=0.15); comp(buf,M().circ(x,180,17),(0.3,0.85,0.3) if on else (0.25,0.25,0.25),sh=0,rim=0)
        if not on: comp(buf,M().line((x-16,164),(x+16,196),5).line((x+16,164),(x-16,196),5),RD,sh=0,rim=0)
    lean=sm((t-EV["leaned"]+0.3)/1.2)*0.7+0.3*sm((t-EV["path"]+0.2)/0.6)
    hx=250; hy=py-300+230*lean
    P=head(buf,hx,hy,190,BK,ang=0.2+1.1*lean)
    nx,ny=P(-0.05,0.75); comp(buf,M().line((nx,ny),(nx-120,ny+150),95).line((nx-120,ny+150),(nx-150,h+40),130),BK,sh=0.15)
    for k in range(5):
        x=((t*500+k*130)%(w+80))-40; comp(buf,M().line((x,py),(x+40,py),4),(1,0.97,0.85),sh=0,rim=0,a=sm((t-sc["s"])/0.3))
    if al>0: rgrad(buf,hx,py,90,YL,0.6*al)
    def hd(d,t=t):
        blk(d,"13 JULY 1978",540,1180,64,a=fa(t,EV["july"]-0.1,EV["safety"]-0.3),fg=cC,bg=cK)
        blk(d,"FAULTY EQUIPMENT",760,330,40,a=fa(t,EV["equip"],EV["safety"]-0.3),ang=3)
        blk(d,"SAFETY SYSTEMS: FAILED",540,1180,50,a=fa(t,EV["failed"],EV["path"]-0.3),sc=pop(t,EV["failed"]))
        blk(d,"BEAM: ON",780,560,54,a=fa(t,EV["running"],sc["e"]+1),fg=cK,bg=cY,ang=-4,sc=pop(t,EV["running"]))
    hud.append(hd); return buf,hud
def s_beam(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    bg(buf,CR)
    ph2=sm((t-EV["five"]+0.4)/0.5); ph3=sm((t-EV["yet"]+0.4)/0.5)
    a1=1-ph2
    if a1>0.01:
        comp(buf,M().circ(300,380,230),RD,sh=0,a=a1)
        P=head(buf,270,400,380,CR,a=a1,sh=0.25)
        ol=M().pline([P(px,py) for px,py in PROFS+[PROFS[0]]],4); comp(buf,ol,BK,sh=0,rim=0,a=a1)
        br=M().ell(*P(-0.08,-0.30),0.42*380,0.30*380,-8); comp(buf,br,(0.88,0.78,0.72),sh=0,rim=0,a=a1*0.8)
        comp(buf,M().ell(*P(-0.10,0.0),14,22),BK,sh=0,rim=0,a=a1*0.7)
        u=sm((t-EV["entered"]+0.2)/1.6)
        beamline(buf,P(-0.9,-0.12),P(0.95,0.06),u,th=5,a=a1)
        if t>EV["back"]: rgrad(buf,*P(-0.55,-0.10),26,YL,0.8*a1)
        if t>EV["nose"]: rgrad(buf,*P(0.62,0.04),26,YL,0.8*a1)
    if ph2>0.01 and ph3<0.99:
        a2=ph2*(1-ph3)
        comp(buf,M().rect(60,620,480,628),BK,sh=0,a=a2)
        for k,(val,col,e) in enumerate(((5,BK,EV["five"]),(2000,RD,EV["two"]),(3000,RD,EV["three"]))):
            g=sm((t-e+0.1)/0.9); hh=max(4,(val/3000)*480*g); x=110+k*150
            comp(buf,M().rect(x-50,620-hh,x+50,620),col,sh=0.2,a=a2)
            if k>0: halftone(buf,np.pad(np.ones((int(hh),100),np.float32),((620-int(hh),h-620),(x-50,w-x-50)))[:h,:w],BK,0.35*a2)
    if ph3>0.01:
        cx,cy=270,360
        comp(buf,M().circ(cx,cy,170),BK,sh=0.2,a=ph3); comp(buf,M().circ(cx,cy,150),CR,sh=0,a=ph3)
        hr=t*0.6; mn=t*7
        comp(buf,M().line((cx,cy),(cx+80*math.sin(hr),cy-80*math.cos(hr)),10).line((cx,cy),(cx+120*math.sin(mn),cy-120*math.cos(mn)),6),RD,sh=0,rim=0,a=ph3)
    def hd(d,t=t,ph2=ph2,ph3=ph3):
        a1=1-ph2
        blk(d,"IN",150,560,46,a=a1*sm((t-EV["back"])/0.3),fg=cC,bg=cK)
        blk(d,"OUT",940,640,46,a=a1*sm((t-EV["nose"])/0.3),fg=cC,bg=cK)
        a2=ph2*(1-ph3)
        for k,(s,e) in enumerate((("5 Gy\nLETHAL",EV["five"]),("2,000 Gy\nIN",EV["two"]),("3,000 Gy\nOUT",EV["three"]))):
            blk(d,s,220+k*300,1340-120,40 if k else 34,a=a2*sm((t-e)/0.3),fg=cC,bg=cK if k==0 else cR)
        blk(d,"HE FINISHED HIS WORK DAY",540,200,52,a=ph3*sm((t-EV["yet"])/0.3))
        blk(d,"DOCTOR: NEXT MORNING",540,1180,48,a=ph3*sm((t-EV["doctor"])/0.3),fg=cC,bg=cK,ang=-2)
    hud.append(hd); return buf,hud
def s_after(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    bg(buf,CR,(BK,-0.5,300,40))
    sw=sm((t-EV["swollen"]+0.2)/1.5)
    P=head(buf,270,420,380,BK,swell=0.0)
    if sw>0: comp(buf,M().ell(*P(0.32,0.06),0.30*380*sw*0.9,0.34*380*sw*0.9),RD,sh=0.2,a=0.85)
    pu=sm((t-EV["peeled"]+0.2)/2.0)
    if pu>0:
        p0=P(-0.6,-0.10); p1=P(0.66,0.05); n=int(26*pu)
        dl=M()
        for k in range(n):
            u0=k/26; u1=u0+0.022; dl.line((p0[0]+(p1[0]-p0[0])*u0,p0[1]+(p1[1]-p0[1])*u0),(p0[0]+(p1[0]-p0[0])*u1,p0[1]+(p1[1]-p0[1])*u1),6)
        comp(buf,dl,YL,sh=0,rim=0)
    ob=sm((t-EV["obs"]+0.2)/0.5)
    if ob>0:
        comp(buf,M().rect(30,650,510,720),BK,sh=0.2,a=ob)
        pts=[];
        for x in range(40,500,3):
            u=(x-40+t*120)%120; y=685-(30 if 40<u<46 else (-14 if 46<=u<50 else 0)); pts.append((x,y))
        comp(buf,M().pline(pts,3),(0.4,1.0,0.5),sh=0,rim=0,a=ob)
    def hd(d,t=t):
        blk(d,"NEXT MORNING",540,200,56,a=fa(t,EV["swollen"]-0.4,EV["peeled"]-0.3),fg=cC,bg=cK)
        blk(d,"LEFT SIDE: SWOLLEN",540,300,46,a=fa(t,EV["swollen"],EV["peeled"]-0.3))
        blk(d,"SKIN · BONE · BRAIN",540,200,58,a=fa(t,EV["burned"],EV["obs"]-0.3),sc=pop(t,EV["burned"]))
        blk(d,"EXPECTED TO DIE",540,200,66,a=fa(t,EV["die"]-0.3,sc["e"]+1),fg=cC,bg=cK)
    hud.append(hd); return buf,hud
def s_survive(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    bg(buf,RD)
    sunburst(buf,270,380,900,20,t,(0.86,0.18,0.14),a=1.0,spd=0.15)
    ph=sm((t-EV["nobody"]+0.3)/0.5)
    if ph>0:
        b2=np.zeros_like(buf); bg(b2,CR)
        P=head(b2,270,420,380,(0.86,0.80,0.70),sh=0.2)
        ol=M().pline([P(px,py) for px,py in PROFS+[PROFS[0]]],3); comp(b2,ol,BK,sh=0,rim=0)
        nr=sm((t-EV["narrow"])/0.6); th=40*(1-nr)+2.5*nr
        comp(b2,M().line(P(-0.9,-0.12),P(0.95,0.06),th),YL,sh=0,rim=0,a=0.9)
        if t>EV["thin"]-0.2:
            mx,my=P(0.05,-0.04); z=sm((t-EV["thin"]+0.2)/0.5)
            comp(b2,M().circ(mx+90,my-150,80*z),CR,sh=0.3); ring=M().circ(mx+90,my-150,86*z); inn=M().circ(mx+90,my-150,78*z); ring.m=np.clip(ring.m.astype(np.int16)-inn.m,0,255).astype(np.uint8); comp(b2,ring,BK,sh=0)
            comp(b2,M().line((mx+90-70*z,my-150),(mx+90+70*z,my-150),6*z),YL,sh=0,rim=0); comp(b2,M().line((mx+30,my-90),(mx,my),3),BK,sh=0,rim=0,a=z)
        buf[:]=buf*(1-ph)+b2*ph
    def hd(d,t=t,ph=ph):
        blk(d,"BUT HE\nDIDN'T DIE.",540,620,140,a=(1-ph)*sm((t-EV["butnot"]+0.2)/0.3),fg=cR,bg=cC,sc=pop(t,EV["butnot"]-0.2),pad=(40,16))
        blk(d,"WHY?",540,200,80,a=fa(t,EV["nobody"],EV["narrow"]-0.2),fg=cC,bg=cK)
        blk(d,"A VERY NARROW BEAM",540,200,58,a=fa(t,EV["narrow"]-0.1,sc["e"]+1))
        blk(d,"ONLY A THIN LINE DAMAGED",540,1180,46,a=fa(t,EV["thin"],sc["e"]+1),fg=cC,bg=cK,ang=-2)
    hud.append(hd); return buf,hud
def face_front(buf,cx,cy,s,t,aging):
    comp(buf,M().ell(cx,cy,110*s,140*s),(0.90,0.80,0.68),sh=0.25)
    comp(buf,M().ell(cx,cy-110*s,118*s,60*s).rect(cx-118*s,cy-110*s,cx-96*s,cy-10*s).rect(cx+96*s,cy-110*s,cx+118*s,cy-10*s),BK,sh=0.1)
    comp(buf,M().ell(cx-40*s,cy-10*s,14*s,7*s).ell(cx+40*s,cy-10*s,14*s,7*s),BK,sh=0,rim=0)
    comp(buf,M().line((cx-30*s,cy+70*s),(cx,cy+76*s),4).line((cx,cy+76*s),(cx+32*s,cy+66*s),4),BK,sh=0,rim=0)
    comp(buf,M().line((cx,cy-150*s),(cx,cy+150*s),3),RD,sh=0,rim=0)
    if aging>0:
        wr=M()
        for k in range(4): wr.pline([(cx-20*s-i*4*s,cy-60*s-k*12*s+3*math.sin(i)) for i in range(16)],2)
        wr.pline([(cx-60*s,cy+10*s),(cx-70*s,cy+40*s),(cx-60*s,cy+70*s)],2); wr.pline([(cx-58*s,cy-14*s),(cx-80*s,cy-20*s)],2); wr.pline([(cx-58*s,cy-4*s),(cx-80*s,cy+2*s)],2)
        comp(buf,wr,(0.45,0.35,0.30),sh=0,rim=0,a=aging)
def s_cost(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    bg(buf,CR,(RD,0.9,700,50))
    ph=sm((t-EV["smooth"]+0.5)/0.5)
    if ph<1:
        a=1-ph
        for k,(e,x,y) in enumerate(((EV["ear"],150,260),(EV["paral"],390,260),(EV["seiz"],150,500),(EV["tired"],390,500))):
            s_=spring((t-e+0.1)/0.5)
            if s_<0.02: continue
            comp(buf,M().rect(x-95*s_,y-95*s_,x+95*s_,y+95*s_),BK if k%3==0 else RD,sh=0.2,a=a)
            ic=M()
            if k==0: ic.ell(x,y,30*s_,48*s_); inn=M().ell(x+6*s_,y,16*s_,30*s_); ic.m=np.clip(ic.m.astype(np.int16)-inn.m,0,255).astype(np.uint8); ic.line((x-60*s_,y-60*s_),(x+60*s_,y+60*s_),9)
            elif k==1: ic.ell(x,y,50*s_,66*s_); ic.rect(x,y-70*s_,x+55*s_,y+70*s_,0)
            elif k==2: ic.poly([(x+10*s_,y-70*s_),(x-30*s_,y+5*s_),(x,y+5*s_),(x-14*s_,y+70*s_),(x+34*s_,y-14*s_),(x+4*s_,y-14*s_)])
            else:
                ic.rect(x-60*s_,y-30*s_,x+50*s_,y+30*s_); inn=M().rect(x-50*s_,y-20*s_,x+40*s_,y+20*s_); ic.m=np.clip(ic.m.astype(np.int16)-inn.m,0,255).astype(np.uint8); ic.rect(x+50*s_,y-12*s_,x+62*s_,y+12*s_).rect(x-46*s_,y-16*s_,x-28*s_,y+16*s_)
            comp(buf,ic,CR,sh=0,rim=0,a=a)
    if ph>0:
        b2=np.zeros_like(buf); bg(b2,CR,(RD,0.9,700,50)); face_front(b2,270,400,1.6,t,sm((t-EV["aged"]+0.3)/1.2)); buf[:]=buf*(1-ph)+b2*ph
    def hd(d,t=t,ph=ph):
        a=1-ph
        for s,e,x,y in (("LEFT EAR: DEAF",EV["ear"],300,720),("FACE: PARALYZED",EV["paral"],780,720),("SEIZURES",EV["seiz"],300,1200),("FATIGUE",EV["tired"],780,1200)):
            blk(d,s,x,y,34,a=a*sm((t-e)/0.3),fg=cC,bg=cK)
        blk(d,"FROZEN",760,200,60,a=ph*sm((t-EV["smooth"])/0.3),fg=cC,bg=cK,ang=-3)
        blk(d,"AGED",320,200,60,a=ph*sm((t-EV["aged"])/0.3),ang=3)
    hud.append(hd); return buf,hud
def s_mind(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    bg(buf,CR,(RD,-0.7,560,70))
    P=head(buf,200,430,330,BK)
    br=M().ell(*P(-0.05,-0.32),0.36*330,0.26*330,-8); comp(buf,br,(0.95,0.75,0.70),sh=0,rim=0)
    ln=M()
    for k in range(5): ln.pline([(P(-0.35+k*0.13,-0.5)[0]+6*math.sin(i*0.8),P(0,-0.5)[1]+i*10) for i in range(9)],3)
    comp(buf,ln,RD,sh=0,rim=0)
    ok=spring((t-EV["intact"]+0.1)/0.5)
    if ok>0.02: comp(buf,M().pline([(380,220),(410,260),(470,170)],18*ok),RD,sh=0.2)
    st=sm((t-EV["back2"]+0.3)/0.6)
    for k in range(int(6*st)):
        comp(buf,M().rect(330,600-k*26,500,624-k*26),RD if k%2 else BK,sh=0.15)
    def hd(d,t=t):
        blk(d,"MIND: INTACT",540,200,72,a=fa(t,EV["intact"]-0.1,EV["back2"]-0.2),sc=pop(t,EV["intact"]-0.1))
        blk(d,"BACK AT WORK",540,200,64,a=fa(t,EV["back2"]-0.1,EV["phd"]-0.2),fg=cC,bg=cK)
        blk(d,"PhD",540,200,110,a=fa(t,EV["phd"]-0.1,EV["s77"]-0.2),sc=pop(t,EV["phd"]-0.1))
        blk(d,"WORKED UNTIL AGE 77",540,200,64,a=fa(t,EV["s77"]-0.1,sc["e"]+1),fg=cK,bg=cY,sc=pop(t,EV["s77"]-0.1))
    hud.append(hd); return buf,hud
def s_end(t,sc):
    buf=np.zeros((h,w,3),np.float32); hud=[]
    bg(buf,CR)
    lb=sm((t-EV["lightb"]+0.2)/0.6)
    sunburst(buf,300,400,900,24,t,RD if lb<0.5 else YL,a=0.35+0.65*lb,spd=0.1)
    comp(buf,M().circ(320,380,170),RD,sh=0.12)
    P=head(buf,260,420,330)
    beamline(buf,(-20,P(-0.6,-0.08)[1]),(w+20,P(0.8,0.06)[1]),1.0,th=4)
    tf=Lx("He saw a light")[1]+0.4
    if t>tf: buf*=max(0.10,1-(t-tf)*0.9)
    def hd(d,t=t,tf=tf):
        blk(d,"THE ONLY ONE",540,230,90,a=fa(t,EV["only"]-0.1,EV["lightb"]-0.3),fg=cC,bg=cK,sc=pop(t,EV["only"]-0.1))
        blk(d,"BRIGHTER THAN\n1,000 SUNS",540,230,80,a=fa(t,EV["lightb"]-0.1,tf+0.2,0.3,0.4),fg=cK,bg=cY)
        blk(d,"…AND HE LIVED.",540,1180,74,a=fa(t,EV["lived"]-0.1,tf+0.2,0.3,0.4),sc=pop(t,EV["lived"]-0.1))
        if t>tf:
            kk=t-tf; a=sm((kk-0.2)/0.6); lg=LOGO.resize((int(LOGO.width*0.5),int(LOGO.height*0.5)),Image.LANCZOS); al=np.array(lg); al[:,:,3]=(al[:,:,3]*a).astype(np.uint8)
            d._image.alpha_composite(Image.fromarray(al),(W//2-lg.width//2,640-lg.height//2)); B.txt(d,(W//2,1000),"ORBITHOS",B.CZ(72,600),(255,215,140,int(255*a)),anchor="mm",stroke=2)
    hud.append(hd); return buf,hud
SCN=dict(hook=s_hook,lab=s_lab,accident=s_accident,beam=s_beam,after=s_after,survive=s_survive,cost=s_cost,mind=s_mind,end=s_end)
BAND=(1-0.62*np.exp(-((yy-728)/78)**2))[...,None].astype(np.float32)
VIG=(1-0.22*np.clip(((xx/w-0.5)**2*1.6+(yy/h-0.5)**2*1.0)*2.2,0,1))[...,None].astype(np.float32)
GR=[np.random.default_rng(i).normal(0,0.010,(h,w,1)).astype(np.float32) for i in range(6)]
def render_scene(t,sc): return SCN[sc["name"]](t,sc)
ANG=-0.75; CA,SA=math.cos(ANG),math.sin(ANG); DV=xx*CA+yy*SA; DMIN,DMAX=float(DV.min()),float(DV.max())
def compose(t):
    SC=B.SC; i=[k for k,s in enumerate(SC) if s["s"]<=t][-1]; sc=SC[i]
    nb=SC[i+1]["s"] if i+1<len(SC) else 1e9; pb=sc["s"] if i>0 else -1e9
    buf,hud=render_scene(t,sc); hk=1.0; TRW=0.3
    tr=None
    if t>nb-TRW: tr=(i,i+1,(t-(nb-TRW))/(2*TRW))
    elif t<pb+TRW: tr=(i-1,i,(t-(pb-TRW))/(2*TRW))
    if tr:
        a_,b_,p=tr; p=sm(p)
        if b_==i: bufA,_=render_scene(t,SC[a_]); bufB=buf
        else: bufA=buf; bufB,_=render_scene(t,SC[b_])
        th=DMIN-140+(DMAX-DMIN+280)*p
        mB=np.clip((th-60-DV)/2,0,1); band=((DV>th-60)&(DV<th+60)).astype(np.float32); stripe=((DV>th+38)&(DV<th+48)).astype(np.float32)
        out=bufB*mB[...,None]+bufA*(1-mB[...,None])
        out=out*(1-band[...,None])+np.array(RD,np.float32)*band[...,None]
        hb=HT*band; out+= (np.array(BK,np.float32)-out)*(hb*0.5)[...,None]
        out=out*(1-stripe[...,None])+np.array(BK,np.float32)*stripe[...,None]
        buf=out; hk=abs(2*p-1)
    buf=np.clip(buf,0,1.3)
    buf=buf*PT*VIG*BAND+GR[int(t*30)%6]
    buf[...,0]=np.roll(buf[...,0],1,1)
    img=Image.fromarray(cv2.resize((np.clip(buf,0,1)*255).astype(np.uint8),(W,H),interpolation=cv2.INTER_CUBIC)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for f in hud: f(d)
    if hk<1: a=np.array(ov); a[:,:,3]=(a[:,:,3]*hk).astype(np.uint8); ov=Image.fromarray(a)
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(ov); img.alpha_composite(o2); return img.convert("RGB")
TOTAL=B.TOTAL
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
