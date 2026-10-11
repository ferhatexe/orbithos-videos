import numpy as np, cv2, math, sys
sys.path.insert(0,"/home/claude/vid3")
import render3 as B
from PIL import Image, ImageDraw
w,h,W,H=B.w,B.h,B.W,B.H; yy,xx=B.yy,B.xx
cl,sm,ein,eout,L,S,fa,txt,title=B.cl,B.sm,B.ein,B.eout,B.L,B.S,B.fa,B.txt,B.title
CLOUD=B.CLOUD; glowpt=B.glowpt; lerp=B.lerp
fMono,fMonoS,fBig,CZ,fEN=B.fMono,B.fMonoS,B.fBig,B.CZ,B.fEN
LOGO=Image.open("/mnt/user-data/outputs/orbithos_logo_seffaf.png").convert("RGBA")
def subtitles(d,t):
    for ln in B.LINES:
        s,e=ln["s"],ln["e"]; i=ln["i"]; nxt=B.LINES[i+1]["s"] if i+1<len(B.LINES) else e+1.2
        fe=min(e+0.45,nxt-0.03)
        if not (s-0.05<=t<=fe): continue
        rows=B.layout(i); aout=1-sm((t-(fe-0.15))/0.15)
        words=[x for r in rows for x in r]; tot=sum(len(x)+1 for x in words); acc=0
        y0=1500-(len(rows)-1)*74
        for ri,r in enumerate(rows):
            rw=sum(fEN.getlength(x) for x in r)+fEN.getlength(" ")*(len(r)-1); x=W/2-rw/2; y=y0+ri*74
            for wd in r:
                ws=s+(acc/tot)*(e-s)*0.92; acc+=len(wd)+1; a=sm((t-ws+0.02)/0.12)*aout
                cur=ws<=t<ws+(len(wd)+1)/tot*(e-s)*0.92+0.05
                col=(255,196,90) if cur else (255,255,255); lift=int((1-sm((t-ws)/0.15))*14)
                if a>0.01: txt(d,(x,y+lift),wd,fEN,col+(int(255*a),),anchor="ls",stroke=4)
                x+=fEN.getlength(wd+" ")
B.subtitles=subtitles
band=(1-0.5*np.exp(-((yy-h*0.745)/70)**2))[...,None].astype(np.float32)
GY=int(h*0.62)
def night(buf,top=(0.01,0.02,0.06),hor=(0.04,0.06,0.12)):
    B.sky(buf,top,hor,yh=GY); B.stars(buf,gain=0.8,maxy=GY)
def aurora(buf,t,inten=1.0,base=260,red=0.5):
    x=xx[:GY]; y=yy[:GY]
    tot=np.zeros((GY,w),np.float32); hi=np.zeros_like(tot)
    for k,(amp,f1,ph) in enumerate([(55,0.010,0.0),(40,0.016,2.0),(30,0.023,4.0)]):
        by=base+k*45+amp*np.sin(x*f1+t*0.25+ph)+18*np.sin(x*0.041-t*0.6+ph)
        up=np.clip(by-y,0,None); dn=np.clip(y-by,0,None)
        v=np.exp(-up/(90+30*k))*(up>0)+np.exp(-dn/6)*(dn>0)
        col_n=CLOUD[(np.clip(y,0,h-1)*0+ (x*0.7+t*20+k*100)%h).astype(np.int32)%CLOUD.shape[0], (x*0+ (x*3.1+k*77)%w).astype(np.int32)%w]
        rays=(0.55+0.45*np.sin(x*0.35+col_n*9+t*1.5))**2
        tot+=v*rays*(1-0.25*k); hi+=v*rays*np.clip(up/160,0,1)
    g=np.array([0.15,1.0,0.45],np.float32); r=np.array([1.0,0.15,0.30],np.float32)
    buf[:GY]+=(tot[...,None]*g*(1-red*0.5)+hi[...,None]*r*red)*inten*0.9
def town(buf,t,lit=1.0,col=(0.015,0.018,0.03),seed=4):
    g=np.random.default_rng(seed); x=0; pts=[(0,h)]
    wins=[]
    while x<w:
        bw=int(g.uniform(40,80)); bh=int(g.uniform(40,110)); y0=GY+30-bh
        pts+=[(x,GY+30),(x,y0),(x+bw//2,y0-int(g.uniform(10,30))),(x+bw,y0),(x+bw,GY+30)]
        if g.random()<0.6: cv2.rectangle(buf,(x+bw-15,y0-22),(x+bw-8,y0),col,-1)
        for k in range(int(g.integers(1,4))): wins.append((x+int(g.uniform(8,bw-12)),y0+int(g.uniform(15,bh-10)),g.random()))
        x+=bw
    pts.append((w,h))
    cv2.fillPoly(buf,[np.array(pts,np.int32)],col,cv2.LINE_AA)
    sx=300; cv2.fillPoly(buf,[np.array([(sx-12,GY-60),(sx,GY-150),(sx+12,GY-60)],np.int32)],col,cv2.LINE_AA); cv2.rectangle(buf,(sx-18,GY-60),(sx+18,GY+30),col,-1)
    cv2.rectangle(buf,(0,GY+30),(w,h),col,-1)
    for (wx,wy,r_) in wins:
        if r_<lit: cv2.rectangle(buf,(wx,wy),(wx+6,wy+8),(1.0,0.72,0.35),-1)
def sundisk(buf,cx,cy,R,flare=0.0,t=0.0):
    d=np.sqrt((xx-cx)**2+(yy-cy)**2)/R; m=d<1
    limb=np.clip(1-d*d,0,1)**0.35
    buf[m]=(np.array([0.98,0.86,0.62],np.float32)*limb[...,None])[m]
    for (sx,sy,rr) in [(cx-30,cy-10,14),(cx-5,cy+5,10),(cx+18,cy-8,8),(cx-45,cy+15,6)]:
        cv2.circle(buf,(int(sx),int(sy)),rr,(0.25,0.17,0.10),-1,cv2.LINE_AA); cv2.circle(buf,(int(sx),int(sy)),int(rr*0.55),(0.08,0.05,0.03),-1,cv2.LINE_AA)
    if flare>0:
        for (fx,fy) in [(cx-20,cy-4),(cx+6,cy+2)]: glowpt(buf,fx,fy,(1.0,1.0,1.0),r=6,a=2.5*flare,spread=12)
def bigglow(buf,x,y,R,col,a=1.0):
    d2=((xx-x)**2+(yy-y)**2)/(R*R); buf+=(np.exp(-d2)*a)[...,None]*np.array(col,np.float32)+(np.exp(-d2*0.15)*a*0.35)[...,None]*np.array(col,np.float32)
def space_sun(buf,t,x=-60,y=None,R=220):
    y=y or h*0.40; bigglow(buf,x,y,R*0.8,(1.0,0.6,0.25),a=1.8)
def earth(buf,x,y,r,lights=0.0,t=0.0):
    d=np.sqrt((xx-x)**2+(yy-y)**2); m=d<r
    sh=np.clip(((xx-x)*(-0.8)+(yy-y)*(-0.2))/r*0.9+0.4,0,1)
    col=np.array([0.10,0.30,0.70],np.float32)*(0.25+0.75*sh[...,None])+CLOUD[:h][...,None]*np.array([0.2,0.25,0.2],np.float32)*0.3
    buf[m]=col[m]
    if lights>0:
        g=np.random.default_rng(3)
        for k in range(160):
            a=g.uniform(0,6.283); rr=np.sqrt(g.random())*r*0.95; px,py=x+math.cos(a)*rr,y+math.sin(a)*rr
            if (px-x)>-r*0.2: cv2.circle(buf,(int(px),int(py)),1,(1.0*lights,0.75*lights,0.3*lights),-1)
    cv2.circle(buf,(int(x),int(y)),int(r+3),(0.3,0.6,1.0),1,cv2.LINE_AA)
def cme(buf,x0,y0,rad,t,a=1.0,ang=0.0,spread=0.6):
    d=np.sqrt((xx-x0)**2+(yy-y0)**2); th=np.arctan2(yy-y0,xx-x0)-ang
    shell=np.exp(-((d-rad)/(18+rad*0.06))**2)*np.exp(-(th/spread)**2)
    n=CLOUD[:h]; buf+=(shell*(0.6+0.8*n)*a)[...,None]*np.array([1.0,0.55,0.25],np.float32)
def sparks(buf,cx,cy,t,a=1.0,seed=0):
    g=np.random.default_rng(int(t*4)+seed); k=(t*4)%1.0
    for i in range(50):
        an=g.uniform(-math.pi,0); sp=g.uniform(30,120); x=cx+math.cos(an)*sp*k; y=cy+math.sin(an)*sp*k+80*k*k
        cv2.circle(buf,(int(x),int(y)),1,(1.0*(1-k)*a,0.85*(1-k)*a,0.5*(1-k)*a),-1,cv2.LINE_AA)
    glowpt(buf,cx,cy,(0.8,0.9,1.0),r=4,a=a*(1-k)*1.8,spread=14)
def telegraph_key(d,x,y,s=1.0,a=1.0):
    A=int(255*a); B_=(180,130,60,A); D=(90,60,30,A)
    d.rectangle([x-150*s,y+20*s,x+150*s,y+50*s],fill=(70,45,25,A))
    d.rectangle([x-120*s,y-10*s,x+100*s,y+20*s],fill=B_,outline=D,width=3)
    d.polygon([(x-100*s,y-10*s),(x+80*s,y-40*s),(x+90*s,y-30*s),(x-90*s,y)],fill=B_,outline=D)
    d.ellipse([x+70*s,y-70*s,x+120*s,y-30*s],fill=(30,25,20,A),outline=D,width=3)
    for k in range(2): d.ellipse([x-110*s+k*40*s,y-2*s,x-94*s+k*40*s,y+14*s],fill=(220,190,120,A))
def frame(t):
    sc=B.scene_at(t); n=sc["name"]; lt=t-sc["s"]; D=sc["e"]-sc["s"]
    buf=np.zeros((h,w,3),np.float32); hud=[]; shake=0.0; dark=1.0; flash=0.0
    if n=="hook":
        if t<0.35: return None,[],0
        night(buf); aurora(buf,t,inten=sm((t-0.9)/1.2)*1.3,red=0.7); town(buf,t)
        if 0.35<t<1.0: flash=max(flash,math.exp(-(t-0.4)*6)*1.2)
        hud.append(lambda d,t=t:title(d,"THE CARRINGTON EVENT",330,sm((t-1.4)/0.4)*(1-sm((t-S("observ")["s"]+0.4)/0.3)),f=CZ(64,800),sub="1859",suby=420,col=(255,235,200)))
    elif n in ("observ","flare"):
        buf[:]=np.array([0.10,0.07,0.05],np.float32)*(0.7+0.3*(1-yy/h))[...,None]
        bigglow(buf,270,380,260,(1.0,0.85,0.6),a=0.25)
        fl=0.0
        if n=="flare":
            s4,_=L(4); fl=sm((t-s4-0.8)/0.3)*(1-sm((t-s4-4.5)/1.0))
            if 0<t-s4-0.8<0.3: flash=0.5
        sundisk(buf,270,380,170,flare=fl,t=t)
        def hd(d,t=t,n=n):
            if n=="observ":
                title(d,"REDHILL · ENGLAND",250,fa(t,S("observ")["s"]+0.3,L(2)[1]+0.6),f=CZ(56,800),col=(255,235,200))
                title(d,"RICHARD CARRINGTON",250,fa(t,L(3)[0]+0.3,S("observ")["e"]),f=CZ(60,800),col=(255,215,150))
            else:
                title(d,"11:18 AM",250,fa(t,L(4)[0],L(5)[1]+0.3),f=fBig,col=(255,255,255))
                title(d,"FIRST SOLAR FLARE EVER RECORDED",1210,fa(t,L(6)[0],S("flare")["e"]),f=CZ(46,800),col=(255,215,150))
        hud.append(hd)
    elif n in ("cme","miss"):
        buf[:]=np.array([0.01,0.02,0.05],np.float32); B.stars(buf,gain=0.9,maxy=h)
        space_sun(buf,t,x=-40,y=h*0.36,R=240)
        if n=="cme":
            p=cl(lt/(D-0.5)); rad=80+(w-50)*p; cme(buf,-40,h*0.36,rad,t,a=1.2)
            earth(buf,470,h*0.36,26,t=t)
            def hd(d,t=t,p=p):
                hrs=17.6*p; title(d,f"{hrs:04.1f} HOURS",1130,sm((t-L(8)[0])/0.3),f=fBig,col=(255,255,255))
                title(d,"CORONAL MASS EJECTION",250,fa(t,L(7)[0]+1,L(7)[1]+0.6),f=CZ(54,800),col=(255,200,140))
            hud.append(hd)
        else:
            ox,oy,ro=-40,h*0.36,470
            cv2.circle(buf,(ox,int(oy)),ro,(0.15,0.25,0.45),1,cv2.LINE_AA)
            ang_e=0.18-lt*0.01; ex,ey=ox+math.cos(ang_e)*ro,oy+math.sin(ang_e)*ro; earth(buf,ex,ey,16,t=t)
            p=cl((t-L(22)[0])/3.5); cme(buf,ox,oy,80+500*p,t,a=1.2,ang=-0.33,spread=0.25)
            def hd(d,t=t):
                title(d,"JULY 23, 2012",250,fa(t,L(22)[0],S("miss")["e"]),f=CZ(64,800),col=(255,210,150))
                title(d,"MISSED BY 9 DAYS",1130,sm((t-L(23)[0])/0.3),f=fBig,col=(255,120,90))
            hud.append(hd)
    elif n in ("aurora","end"):
        k=1.0 if n=="aurora" else 1.0
        night(buf)
        red=0.9 if n=="aurora" else 0.6
        aurora(buf,t,inten=1.3,red=red)
        lit=1.0
        s27,e27=L(27); tf=e27+0.7
        if n=="end": lit=1-sm((t-L(27)[0])/2.0)
        if n=="aurora" and lt<4.5:
            for px in [60,140,420,490]:
                cv2.line(buf,(px,GY+30),(px+8,GY-70),(0.02,0.02,0.03),4,cv2.LINE_AA)
                for f in range(5):
                    a=f*0.9+px; cv2.line(buf,(px+8,GY-70),(int(px+8+math.cos(a)*45),int(GY-70+math.sin(a)*18+14)),(0.02,0.02,0.03),3,cv2.LINE_AA)
            cv2.rectangle(buf,(0,GY+30),(w,h),(0.015,0.018,0.03),-1)
        else: town(buf,t,lit=lit)
        if n=="end" and t>tf: flash=math.exp(-(t-tf)*3)*1.2; buf*=max(0.1,1-(t-tf)*1.5)
        def hd(d,t=t,n=n,tf=tf,lt=lt):
            if n=="aurora":
                title(d,"HAVANA · PANAMA",250,fa(t,L(10)[0],L(10)[1]+0.5),f=CZ(62,800),col=(255,230,200))
                title(d,"MIDNIGHT · NEW ENGLAND",250,fa(t,L(11)[0],S("aurora")["e"]),f=CZ(54,800),col=(255,230,200))
            elif t>tf:
                kk=t-tf; a=sm(kk/0.6)*(1-sm((kk-(S("end")["e"]-tf-0.9))/0.6)); scl=0.5+0.08*eout(kk/1.5)
                lg=LOGO.resize((int(LOGO.width*scl),int(LOGO.height*scl)),Image.LANCZOS)
                al=np.array(lg); al[:,:,3]=(al[:,:,3]*a).astype(np.uint8); d._image.alpha_composite(Image.fromarray(al),(W//2-lg.width//2,640-lg.height//2))
                txt(d,(W//2,1000),"ORBITHOS",CZ(72,600),(255,215,140,int(255*a)),anchor="mm",stroke=2)
        hud.append(hd)
    elif n=="miners":
        night(buf); aurora(buf,t,inten=1.4,red=1.0,base=230)
        pts=[(0,GY+20)]+[(x,int(GY-80*np.exp(-((x-150)/120)**2)-120*np.exp(-((x-420)/100)**2))) for x in range(0,w+20,20)]+[(w,h),(0,h)]
        cv2.fillPoly(buf,[np.array(pts,np.int32)],(0.02,0.02,0.03),cv2.LINE_AA)
        for tx in [180,260]: cv2.fillPoly(buf,[np.array([(tx-30,GY+60),(tx,GY+10),(tx+30,GY+60)],np.int32)],(0.12,0.08,0.06),cv2.LINE_AA)
        fl=0.8+0.2*math.sin(t*13)*math.sin(t*7); glowpt(buf,330,GY+55,(1.0,0.55,0.2),r=6,a=1.2*fl*sm((t-L(12)[0]-1.5)/0.6),spread=22)
        hud.append(lambda d,t=t:title(d,"COLORADO",250,fa(t,S("miners")["s"]+0.3,S("miners")["e"]-0.2),f=CZ(66,800),col=(255,230,200),sub="1 AM · \"IT'S DAWN\"",suby=330))
    elif n in ("telegraph","battery"):
        buf[:]=np.array([0.10,0.06,0.03],np.float32)*(0.6+0.4*(1-yy/h))[...,None]
        glowpt(buf,120,200,(1.0,0.7,0.3),r=16,a=0.9*(0.85+0.15*math.sin(t*9)),spread=70)
        cv2.line(buf,(0,300),(w,280),(0.2,0.15,0.1),2,cv2.LINE_AA); cv2.line(buf,(270,285),(270,480),(0.2,0.15,0.1),2,cv2.LINE_AA)
        if n=="telegraph":
            sparks(buf,300,480,t,a=1.0); sparks(buf,210,470,t+0.3,a=0.8,seed=5)
            s14,_=L(14)
            if t>s14+1.8:
                ff=0.8+0.2*math.sin(t*15); glowpt(buf,390,560,(1.0,0.45,0.1),r=10,a=1.4*ff,spread=26)
            if (t%1.3)<0.08: flash=0.35
        else:
            glowpt(buf,300,470,(0.5,1.0,0.6),r=5,a=0.7*(0.5+0.5*math.sin(t*6)),spread=20)
        def hd(d,t=t,n=n):
            telegraph_key(d,560,1000,s=1.3)
            if n=="telegraph":
                d.rectangle([700,1080,1000,1120],fill=(235,225,200,255))
                for k in range(8): d.rectangle([715+k*34,1092,715+k*34+(18 if k%3 else 6),1106],fill=(20,20,20,255))
                title(d,"WASHINGTON, D.C.",250,fa(t,L(15)[0],S("telegraph")["e"]),f=CZ(56,800),col=(255,230,200))
                title(d,"TELEGRAPH OFFICES",250,fa(t,L(13)[0],L(14)[1]),f=CZ(56,800),col=(255,230,200))
            else:
                title(d,"BOSTON — PORTLAND",250,fa(t,L(16)[0],L(16)[1]+0.3),f=CZ(62,800),col=(255,230,200))
                title(d,"BATTERIES: DISCONNECTED",250,fa(t,L(17)[0],L(17)[1]+0.3),f=CZ(52,800),col=(170,255,190))
                title(d,"POWERED BY THE SKY",250,fa(t,L(18)[0],S("battery")["e"]),f=CZ(62,800),col=(170,255,190))
        hud.append(hd)
    elif n in ("modern","quebec","cost"):
        buf[:]=np.array([0.01,0.02,0.05],np.float32); B.stars(buf,gain=0.7,maxy=h)
        lights=1.0
        if n=="quebec": lights=1-sm((t-L(21)[0]-1.5)/2.0)
        if n=="cost": lights=0.6+0.4*math.sin(t*6)**2
        earth(buf,270,h*0.41,140,lights=lights,t=t)
        if n=="modern":
            for k in range(6):
                a=t*0.4+k*1.05; x=270+math.cos(a)*230; y=h*0.38+math.sin(a)*70
                if math.sin(a)>-0.2 or abs(x-270)>150: glowpt(buf,x,y,(0.8,0.9,1.0),r=2,a=1.2,spread=5)
        def hd(d,t=t,n=n):
            if n=="modern":
                for k,wd in enumerate(["POWER GRIDS","SATELLITES","GPS","INTERNET"]):
                    a=sm((t-L(20)[0]-0.3-k*0.7)/0.3); txt(d,(W//2,1080+k*0),wd if False else "",fMono,(255,255,255,0))
                labs=["POWER GRIDS","SATELLITES","GPS","INTERNET"]; k=int(cl((t-L(20)[0])/(L(20)[1]-L(20)[0]))*3.99)
                if t>L(20)[0]: title(d,labs[k],360,1.0,f=CZ(64,800),col=(200,230,255))
                title(d,"ONLY TELEGRAPH WIRES",250,fa(t,L(19)[0],L(19)[1]+0.3),f=CZ(56,800),col=(255,230,200))
            elif n=="quebec":
                title(d,"QUEBEC · 1989",250,sm((t-L(21)[0])/0.3),f=CZ(64,800),col=(255,230,200))
                title(d,"9 HOURS OF DARKNESS",360,sm((t-L(21)[0]-2.5)/0.3),f=fBig,col=(255,255,255))
            else:
                title(d,"UP TO $2.6 TRILLION",270,sm((t-L(24)[0]-2.0)/0.3),f=fBig,col=(255,120,90)); title(d,"U.S. ALONE",380,sm((t-L(24)[0]-3.5)/0.3),f=CZ(54,800),col=(255,230,200))
        hud.append(hd)
    small=cv2.resize(buf,(w//4,h//4),interpolation=cv2.INTER_AREA)
    br=np.maximum(small-0.7,0); bl=cv2.GaussianBlur(br,(0,0),3)+cv2.GaussianBlur(br,(0,0),10)*1.3
    buf=buf+cv2.resize(bl,(w,h))*0.8
    buf=1-np.exp(-buf*1.35); buf=buf*B.vig*band+B.grain[int(t*30)%8]
    fl,punch,rgb=B.fx_at(t); fl=max(fl,flash)
    sx=sy=0
    if shake>0: sx=math.sin(t*37)*7*shake; sy=math.cos(t*29)*7*shake
    M=cv2.getRotationMatrix2D((w/2,h/2),0,1+0.05*punch); M[0,2]+=sx; M[1,2]+=sy
    buf=cv2.warpAffine(buf,M,(w,h),borderMode=cv2.BORDER_REFLECT)
    if rgb>0.05: k=int(5*rgb); buf[:,:,0]=np.roll(buf[:,:,0],k,1); buf[:,:,2]=np.roll(buf[:,:,2],-k,1)
    return (buf+fl*0.8)*dark,hud,dark
B.frame=frame; compose=B.compose; TOTAL=B.TOTAL
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
