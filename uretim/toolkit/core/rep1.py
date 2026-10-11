import numpy as np, cv2, math, sys
sys.path.insert(0,"/home/claude/vid3"); sys.path.insert(0,"/home/claude/vid8")
import render3 as B
import render8 as R8
from PIL import Image, ImageDraw
w,h,W,H=B.w,B.h,B.W,B.H; yy,xx=B.yy,B.xx
cl,sm,ein,eout,L,S,fa,txt,title=B.cl,B.sm,B.ein,B.eout,B.L,B.S,B.fa,B.txt,B.title
CLOUD=B.CLOUD; glowpt=B.glowpt; lerp=B.lerp
fMono,fMonoS,fBig,CZ,fEN=B.fMono,B.fMonoS,B.fBig,B.CZ,B.fEN
LOGO=Image.open("/mnt/user-data/outputs/orbithos_logo_seffaf.png").convert("RGBA")
B.fx_at=lambda t:(0,0,0)
band=(1-0.55*np.exp(-((yy-h*0.745)/75)**2))[...,None].astype(np.float32)
LAB={"c":("RICHARD CARRINGTON",(255,210,150)),"o":("TELEGRAPH OPERATOR",(170,220,255)),"m":("A MAN IN THE STREET",(255,170,150))}
def subtitles(d,t):
    for ln in B.LINES:
        s,e=ln["s"],ln["e"]; i=ln["i"]; nxt=B.LINES[i+1]["s"] if i+1<len(B.LINES) else e+1.2
        fe=min(e+0.5,nxt-0.03)
        if not (s-0.05<=t<=fe): continue
        rows=B.layout(i); aout=1-sm((t-(fe-0.15))/0.15)
        words=[x for r in rows for x in r]; tot=sum(len(x)+1 for x in words); starts=[]; acc=0
        for r in rows:
            rs=[]
            for wd in r: rs.append(s+(acc/tot)*(e-s)*0.92); acc+=len(wd)+1
            starts.append(rs)
        cur=0
        for ri,rs in enumerate(starts):
            if t>=rs[0]-0.05: cur=ri
        pg=cur//2 if len(rows)>2 else 0
        prow=rows[pg*2:pg*2+2] if len(rows)>2 else rows; pst=starts[pg*2:pg*2+2] if len(rows)>2 else starts
        y0=1500-(len(prow)-1)*74; lab=LAB.get(ln["kind"])
        if lab: txt(d,(W/2,y0-84),lab[0],fMonoS,lab[1]+(int(220*aout*sm((t-s)/0.2)),),anchor="ms")
        for ri,(r,rs) in enumerate(zip(prow,pst)):
            rw=sum(fEN.getlength(x) for x in r)+fEN.getlength(" ")*(len(r)-1); x=W/2-rw/2; y=y0+ri*74
            for k,wd in enumerate(r):
                ws=rs[k]; a=sm((t-ws+0.02)/0.12)*aout
                we=rs[k+1] if k+1<len(rs) else ws+(len(wd)+1)/tot*(e-s)*0.92
                col=(255,196,90) if ws<=t<we+0.05 else (lab[1] if lab else (255,255,255))
                lift=int((1-sm((t-ws)/0.15))*10)
                if a>0.01: txt(d,(x,y+lift),wd,fEN,col+(int(255*a),),anchor="ls",stroke=4)
                x+=fEN.getlength(wd+" ")
B.subtitles=subtitles
def bigglow(buf,x,y,R,col,a=1.0):
    d2=((xx-x)**2+(yy-y)**2)/(R*R); buf+=(np.exp(-d2)*a)[...,None]*np.array(col,np.float32)+(np.exp(-d2*0.12)*a*0.3)[...,None]*np.array(col,np.float32)
def rain(buf,t,a=0.35):
    g=np.random.default_rng(int(t*24))
    for k in range(170):
        x=g.uniform(0,w); y=g.uniform(0,h*0.7); cv2.line(buf,(int(x),int(y)),(int(x-4),int(y+20)),(0.5*a,0.6*a,0.7*a),1)
def alley(buf,t):
    buf[:]=np.array([0.02,0.035,0.06],np.float32)*(0.6+0.4*(1-yy/h))[...,None]
    cv2.fillPoly(buf,[np.array([(0,0),(150,0),(150,700),(0,960)],np.int32)],(0.02,0.025,0.035))
    cv2.fillPoly(buf,[np.array([(540,0),(400,0),(400,700),(540,960)],np.int32)],(0.025,0.03,0.04))
    cv2.fillPoly(buf,[np.array([(150,700),(400,700),(540,960),(0,960)],np.int32)],(0.04,0.045,0.055))
    for k in range(10):
        y=700+k*k*3; cv2.line(buf,(int(150-k*15),y),(int(400+k*14),y),(0.06,0.065,0.08),1)
    cv2.rectangle(buf,(170,420),(260,640),(0.05,0.035,0.02),-1)
    cv2.rectangle(buf,(280,470),(380,600),(0.9,0.55,0.22),-1)
    bigglow(buf,330,535,80,(1.0,0.6,0.25),a=0.45)
    fl=0.9+0.1*math.sin(t*7); glowpt(buf,215,400,(1.0,0.7,0.35),r=5,a=1.1*fl,spread=18)
    pass
    rain(buf,t)
def shop(buf,t,dim=1.0):
    buf[:]=np.array([0.10,0.06,0.03],np.float32)*(0.5+0.5*(1-yy/h))[...,None]*dim
    for sy in [220,340,460]:
        cv2.rectangle(buf,(20,sy),(520,sy+8),(0.05,0.03,0.015),-1)
        g=np.random.default_rng(sy)
        x=30
        while x<500:
            wd=int(g.uniform(20,60)); ht=int(g.uniform(30,90)); k=g.integers(0,3)
            col=(0.06,0.04,0.02)
            if k==0: cv2.rectangle(buf,(x,sy-ht),(x+wd,sy),col,-1)
            elif k==1: cv2.ellipse(buf,(x+wd//2,sy-ht//2),(wd//2,ht//2),0,0,360,col,-1)
            else: cv2.circle(buf,(x+wd//2,sy-wd//2),wd//2,col,-1); cv2.circle(buf,(x+wd//2,sy-wd//2),wd//2-4,(0.2*dim,0.15*dim,0.08*dim),1)
            x+=wd+int(g.uniform(8,20))
    for k,(px,py) in enumerate([(90,560),(450,560)]):
        cv2.rectangle(buf,(px-25,py-120),(px+25,py+80),(0.08,0.05,0.025),-1)
        a=math.sin(t*2*math.pi/1.6+k)*0.35; bx=int(px+math.sin(a)*50); by=int(py-40+math.cos(a)*50)
        cv2.line(buf,(px,py-40),(bx,by),(0.5,0.38,0.15),2,cv2.LINE_AA); cv2.circle(buf,(bx,by),8,(0.6,0.45,0.18),-1,cv2.LINE_AA)
        cv2.circle(buf,(px,py-90),18,(0.75,0.68,0.5),-1,cv2.LINE_AA)
    cv2.rectangle(buf,(60,640),(480,700),(0.07,0.045,0.02),-1)
    fl=0.9+0.1*math.sin(t*6)*math.sin(t*2.3)
    bigglow(buf,270,300,170,(1.0,0.62,0.28),a=0.55*fl*dim)
    glowpt(buf,270,300,(1.0,0.75,0.4),r=6,a=1.3*fl*dim,spread=20)
    g=np.random.default_rng(1)
    for k in range(60):
        x=(g.uniform(100,440)+math.sin(t*0.3+k)*20); y=(g.uniform(150,600)-t*6*g.uniform(0.5,1.5))%450+150
        cv2.circle(buf,(int(x),int(y)),1,(0.5*dim,0.4*dim,0.25*dim),-1)
def watch(d,cx,cy,R,hh=11,mm=18,ticking=0.0,t=0.0,back=False,a=1.0):
    A=int(255*a)
    d.ellipse([cx-R-18,cy-R-18,cx+R+18,cy+R+18],fill=(170,125,50,A)); d.ellipse([cx-R-8,cy-R-8,cx+R+8,cy+R+8],fill=(215,170,80,A))
    d.rectangle([cx-16,cy-R-60,cx+16,cy-R-18],fill=(200,155,70,A)); d.ellipse([cx-30,cy-R-100,cx+30,cy-R-50],outline=(200,155,70,A),width=10)
    if back:
        d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=(200,155,65,A))
        for r in range(20,R,14): d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=(185,140,55,int(A*0.5)),width=2)
        txt(d,(cx,cy-20),"R. C.",CZ(90,700),(120,80,25,A),anchor="mm"); txt(d,(cx,cy+70),"1859",CZ(70,700),(120,80,25,A),anchor="mm")
        return
    d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=(240,232,210,A))
    for k,nm in enumerate(["XII","I","II","III","IV","V","VI","VII","VIII","IX","X","XI"]):
        an=-math.pi/2+k*math.pi/6; txt(d,(cx+math.cos(an)*R*0.8,cy+math.sin(an)*R*0.8),nm,CZ(int(R*0.16),700),(50,40,30,A),anchor="mm")
    sec=(t*ticking)
    m=mm+int(sec)//60*0+ (int(sec)/60.0 if ticking else 0)
    ma=-math.pi/2+(m/60)*2*math.pi; ha=-math.pi/2+((hh%12)+m/60)/12*2*math.pi
    d.line([(cx,cy),(cx+math.cos(ha)*R*0.5,cy+math.sin(ha)*R*0.5)],fill=(30,25,20,A),width=12)
    d.line([(cx,cy),(cx+math.cos(ma)*R*0.75,cy+math.sin(ma)*R*0.75)],fill=(30,25,20,A),width=8)
    if ticking:
        sa=-math.pi/2+(math.floor(t)%60)/60*2*math.pi; d.line([(cx,cy),(cx+math.cos(sa)*R*0.82,cy+math.sin(sa)*R*0.82)],fill=(170,40,30,A),width=3)
    d.ellipse([cx-12,cy-12,cx+12,cy+12],fill=(30,25,20,A))
def hourglass(d,cx,cy,sc,fill,t,a=1.0,flip=0.0):
    A=int(255*a); hw,hh=110*sc,190*sc
    d.rectangle([cx-hw-20,cy-hh-30,cx+hw+20,cy-hh],fill=(90,55,25,A)); d.rectangle([cx-hw-20,cy+hh,cx+hw+20,cy+hh+30],fill=(90,55,25,A))
    glass=[(cx-hw,cy-hh),(cx+hw,cy-hh),(cx+14*sc,cy),(cx+hw,cy+hh),(cx-hw,cy+hh),(cx-14*sc,cy)]
    d.polygon(glass,fill=(200,220,230,int(A*0.18)),outline=(220,235,245,A))
    top=cl(1-fill); bot=cl(fill)
    if top>0.01:
        yt=cy-hh*top*0.95; wt=(hw-14*sc)*(1-(cy-yt)/hh)+14*sc
        d.polygon([(cx-wt*0.95,yt),(cx+wt*0.95,yt),(cx+12*sc,cy-4),(cx-12*sc,cy-4)],fill=(225,180,95,A))
    if bot>0.01:
        yb=cy+hh-hh*bot*0.9
        d.polygon([(cx-hw*0.95,cy+hh),(cx+hw*0.95,cy+hh),(cx+hw*0.3,yb),(cx,yb-25*sc*bot),(cx-hw*0.3,yb)],fill=(225,180,95,A))
    if 0.01<fill<0.999: d.line([(cx,cy),(cx,cy+hh-hh*bot*0.9-25*sc*bot)],fill=(225,180,95,A),width=int(4*sc)+1)
def glove(d,x,y,s,a=1.0):
    A=int(255*a); d.rounded_rectangle([x-70*s,y,x+70*s,y+170*s],radius=int(50*s),fill=(18,16,20,A))
    for k in range(4): d.rounded_rectangle([x-66*s+k*34*s,y-80*s,x-40*s+k*34*s,y+20*s],radius=int(13*s),fill=(18,16,20,A))
def warp(buf,k,t):
    if k<=0: return buf
    cx,cy=w/2,h*0.42; X=xx-cx; Y=yy-cy; r=np.sqrt(X*X+Y*Y)+1e-3; th=np.arctan2(Y,X)
    th2=th+k*3.0*np.exp(-r/260); r2=r*(1+0.35*k*np.sin(r*0.04-t*8))
    mx=(cx+np.cos(th2)*r2).astype(np.float32); my=(cy+np.sin(th2)*r2).astype(np.float32)
    out=cv2.remap(buf,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    g=np.random.default_rng(int(t*30)); 
    for i in range(int(200*k)):
        a=g.uniform(0,6.283); rr=g.uniform(20,400)*(1-k*0.5); x=cx+math.cos(a+t*3)*rr; y=cy+math.sin(a+t*3)*rr
        cv2.circle(out,(int(x),int(y)),1,(1.0*k,0.8*k,0.45*k),-1)
    out=out*(1-0.3*k)+np.array([0.35,0.25,0.1],np.float32)*k*0.4*np.exp(-r/300)[...,None]
    return out
WARP_IN={"redhill":1.6,"telegraph":1.6,"return":1.6}
def frame(t):
    sc=B.scene_at(t); n=sc["name"]; lt=t-sc["s"]; D=sc["e"]-sc["s"]
    buf=np.zeros((h,w,3),np.float32); hud=[]; dark=1.0; wk=0.0
    if n in WARP_IN and lt<WARP_IN[n]: wk=(1-lt/WARP_IN[n])**1.3
    nxt=[s for s in B.SC if s["s"]>sc["s"]]
    if nxt and nxt[0]["name"] in WARP_IN and sc["e"]-t<1.0: wk=max(wk,(1-(sc["e"]-t))**1.5)
    if n=="alley":
        if t<0.3: return None,[],0
        alley(buf,t); buf*=sm(t/2.0)
        def hd(d,t=t):
            a=sm((t-0.8)/0.6); txt(d,(660,900),"ANTIQUES",CZ(40,700),(255,215,150,int(230*a)),anchor="mm")
            s1,e1=L(1); ta=fa(t,e1+0.3,S("alley")["e"]-0.3,0.6,0.4)
            title(d,"THE TIME ANTIQUARIAN",330,ta,f=CZ(76,800),col=(255,220,160))
            title(d,"EPISODE 1 · THE STOPPED WATCH",430,ta,f=CZ(40,600),col=(235,230,220))
            txt(d,(W//2,1180),"INSPIRED BY REAL EVENTS",fMonoS,(220,220,220,int(200*ta)),anchor="mm")
        hud.append(hd)
    elif n in ("shop","watch","hourglass","return","teaser","end"):
        shop(buf,t,dim=0.7 if n in ("watch","hourglass") else 1.0)
        if n=="end": buf*=1-sm((lt-1.5)/2.0)*0.85
        def hd(d,t=t,n=n,lt=lt):
            if n=="shop":
                a=sm((t-L(4)[0])/0.6); d.rectangle([380,1180,700,1300],fill=(120,85,50,int(255*a))); d.line([(380,1240),(700,1240)],fill=(90,60,30,int(255*a)),width=6); d.line([(540,1180),(540,1300)],fill=(90,60,30,int(255*a)),width=6)
            elif n=="watch":
                a=sm(lt/0.6); back=t>L(6)[0]
                watch(d,540,700,250,back=back,a=a); glove(d,540,1000,1.1,a=a*0.95)
            elif n=="hourglass":
                a=sm(lt/0.5); fl=cl((t-L(7)[0]-1.5)/60.0)
                hourglass(d,540,700,1.4,fl,t,a=a)
            elif n=="return":
                watch(d,560,1050,120,ticking=1.0,t=t,a=sm(lt/0.8)); hourglass(d,300,840,0.9,1.0,t,a=sm(lt/0.8))
            elif n=="teaser":
                a=sm((t-L(32)[0])/0.8)
                d.rectangle([330,980,750,1260],fill=(120,85,50,int(255*a)))
                if a>0:
                    cx,cy,R=540,930,150; pts=[]
                    for k in range(32):
                        base=k*2*math.pi/32+t*0.1
                        for da,rr in [(-0.05,R-14),(-0.03,R),(0.03,R),(0.05,R-14)]: pts.append((cx+math.cos(base+da)*rr,cy+math.sin(base+da)*rr))
                    d.polygon(pts,fill=(60,120,95,int(255*a))); d.ellipse([cx-40,cy-40,cx+40,cy+40],fill=(40,80,65,int(255*a)))
                title(d,"NEXT: THE BRONZE GEAR",330,fa(t,L(33)[1]+0.3,S("teaser")["e"]+2),f=CZ(60,800),col=(150,235,200))
            elif n=="end":
                a=sm((t-L(34)[0])/0.6)
                title(d,"THE TIME ANTIQUARIAN",420,a,f=CZ(70,800),col=(255,220,160)); title(d,"TO BE CONTINUED…",520,a,f=CZ(44,600),col=(235,230,220))
                kk=cl((t-L(34)[1]-0.8)/1.0)
                if kk>0:
                    lg=LOGO.resize((int(LOGO.width*0.32),int(LOGO.height*0.32)),Image.LANCZOS); al=np.array(lg); al[:,:,3]=(al[:,:,3]*kk).astype(np.uint8)
                    d._image.alpha_composite(Image.fromarray(al),(W//2-lg.width//2,760-lg.height//2)); txt(d,(W//2,960),"ORBITHOS",CZ(52,600),(255,215,140,int(255*kk)),anchor="mm")
        hud.append(hd)
        if n=="teaser": glowpt(buf,270,465,(0.3,1.0,0.7),r=40,a=0.4*sm((t-L(32)[0])/0.8),spread=90)
    elif n in ("redhill","flare"):
        B.sky(buf,(0.35,0.5,0.7),(0.85,0.82,0.75),yh=int(h*0.55))
        pts=[(0,int(h*0.55))]+[(x,int(h*0.53-20*math.sin(x/80))) for x in range(0,w+20,20)]+[(w,h),(0,h)]
        cv2.fillPoly(buf,[np.array(pts,np.int32)],(0.18,0.22,0.12),cv2.LINE_AA)
        if n=="redhill" and t<L(11)[0]:
            cv2.rectangle(buf,(200,int(h*0.44)),(340,int(h*0.53)),(0.25,0.2,0.18),-1); cv2.ellipse(buf,(270,int(h*0.44)),(60,40),0,180,360,(0.35,0.33,0.32),-1,cv2.LINE_AA)
            g=np.random.default_rng(int(t*10))
            for k in range(30): cv2.circle(buf,(int(320+g.normal(0,10)),int(h*0.40-((t*20+k*9)%120))),int(4+k%4),(0.55,0.55,0.55),-1)
        else:
            buf[:]=np.array([0.10,0.07,0.05],np.float32)*(0.7+0.3*(1-yy/h))[...,None]
            fl=0.0
            if n=="flare": fl=sm((t-L(12)[0]-0.3)/0.3)*(1-sm((t-L(14)[0])/1.5))
            R8.sundisk(buf,270,330,170,flare=fl,t=t)
            fx=(120 if n=="redhill" or t<L(13)[1] else 120-200*cl((t-L(13)[1])/1.5))
            cv2.circle(buf,(int(fx),int(h*0.60)),16,(0.04,0.03,0.03),-1,cv2.LINE_AA)
            cv2.fillPoly(buf,[np.array([(fx-26,h*0.62),(fx+26,h*0.62),(fx+34,h*0.78),(fx-34,h*0.78)],np.int32)],(0.04,0.03,0.03),cv2.LINE_AA)
        def hd(d,t=t,n=n):
            if n=="redhill": title(d,"REDHILL · 1 SEPTEMBER 1859",280,fa(t,L(9)[0],L(10)[1]),f=CZ(48,800),col=(255,240,215))
            if n=="flare":
                title(d,"11:18 AM",250,fa(t,L(12)[0],L(13)[1]),f=fBig,col=(255,255,255))
                if t>L(16)[0]: watch(d,860,1120,90,ticking=1.0,t=t,a=sm((t-L(16)[0])/0.5))
        hud.append(hd)
    elif n=="telegraph":
        buf[:]=np.array([0.10,0.06,0.03],np.float32)*(0.6+0.4*(1-yy/h))[...,None]
        cv2.rectangle(buf,(330,120),(500,360),(0.05,0.03,0.03),-1)
        sub=np.zeros((240,170,3),np.float32); tmp=np.zeros((h,w,3),np.float32); R8.aurora(tmp,t,inten=1.4,red=1.0,base=250)
        buf[120:360,330:500]=cv2.resize(tmp[100:560,150:490],(170,240))*0.9+np.array([0.05,0.0,0.02],np.float32)
        cv2.line(buf,(415,120),(415,360),(0.05,0.03,0.02),3); cv2.line(buf,(330,240),(500,240),(0.05,0.03,0.02),3)
        R8.sparks(buf,210,520,t,a=1.0); R8.sparks(buf,160,500,t+0.3,a=0.8,seed=3)
        if t>L(19)[0]+2.5: glowpt(buf,300,560,(1.0,0.45,0.1),r=12,a=1.4*(0.8+0.2*math.sin(t*15)),spread=30)
        cv2.circle(buf,(420,560),14,(0.03,0.02,0.02),-1,cv2.LINE_AA); cv2.fillPoly(buf,[np.array([(396,580),(444,580),(456,700),(384,700)],np.int32)],(0.03,0.02,0.02),cv2.LINE_AA)
        hud.append(lambda d,t=t:(R8.telegraph_key(d,420,1110,s=1.2),title(d,"LONDON · THAT NIGHT",250,fa(t,L(18)[0],L(18)[1]+0.6),f=CZ(52,800),col=(255,230,200))))
    elif n in ("street","sand"):
        R8.night(buf); R8.aurora(buf,t,inten=1.5,red=1.0,base=260); R8.town(buf,t,lit=1.0)
        g=np.random.default_rng(5)
        for k in range(14):
            x=int(20+k*38+g.normal(0,6)); y=R8.GY+60; hgt=int(g.uniform(40,58))
            cv2.circle(buf,(x,y-hgt),6,(0.01,0.01,0.015),-1,cv2.LINE_AA); cv2.rectangle(buf,(x-8,y-hgt+6),(x+8,y+20),(0.01,0.01,0.015),-1)
        if n=="sand":
            p=sm((t-L(25)[0])/1.0); buf*=(1-0.25*p*(0.5+0.5*math.sin(t*8)))
            buf+=np.array([0.25,0.0,0.0],np.float32)*p*0.35*(np.sqrt((xx/w-0.5)**2+(yy/h-0.5)**2)*2)[...,None]
            def hd(d,t=t):
                fl=0.97+0.03*cl((t-L(25)[0])/(S("sand")["e"]-L(25)[0]))
                hourglass(d,540,640,1.0,fl,t,a=sm((t-L(25)[0])/0.6))
            hud.append(hd)
    small=cv2.resize(buf,(w//4,h//4),interpolation=cv2.INTER_AREA)
    br=np.maximum(small-0.7,0); bl=cv2.GaussianBlur(br,(0,0),3)+cv2.GaussianBlur(br,(0,0),10)*1.3
    buf=buf+cv2.resize(bl,(w,h))*0.8
    buf=1-np.exp(-buf*1.35)
    lum=buf.mean(2,keepdims=True); buf=buf*0.88+lum*np.array([1.05,0.95,0.8],np.float32)*0.12
    buf=buf*B.vig*band+B.grain[int(t*30)%8]*1.4
    if wk>0: buf=warp(buf,wk,t)
    return buf*dark,hud,dark
B.frame=frame; compose=B.compose; TOTAL=B.TOTAL
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
