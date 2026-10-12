import numpy as np, cv2, math, sys, os
os.chdir("/home/claude/vid68")
for p in ["/home/claude/vid68","/home/claude/vid3","/home/claude/ep1","/home/claude/toolkit"]: sys.path.insert(0,p)
import render3 as B
import rep1 as E1
import ev
import paper as P
from paper import cl, sm, fa, spring, W, H
from PIL import Image, ImageDraw, ImageFont, ImageFilter
EV=ev.EV; Lx=ev.Lx; S=ev.S
E1.LAB.clear(); B.fx_at=lambda t:(0,0,0); B.subtitles=E1.subtitles
# ================= detective's corkboard: polaroids, index cards, sticky notes, push pins, red yarn =================
_g=np.random.default_rng(68)
def _cork():
    n1=cv2.GaussianBlur(_g.normal(0,1,(H,W)).astype(np.float32),(0,0),1.2); n1/=n1.std()
    n2=cv2.GaussianBlur(_g.normal(0,1,(H,W)).astype(np.float32),(0,0),6); n2/=n2.std()
    sp=(_g.random((H,W))<0.03).astype(np.float32); sp=cv2.GaussianBlur(sp,(0,0),1.2)*2.5
    base=np.array((0.70,0.52,0.34),np.float32)*(1+0.08*n1+0.06*n2)[...,None]-sp[...,None]*0.18
    fr=np.zeros((H,W),np.float32); fr[:28,:]=1; fr[:,:28]=1; fr[:,-28:]=1; fr[1340:1368,:]=1
    wood=np.array((0.40,0.25,0.13),np.float32)*(1+0.10*cv2.GaussianBlur(_g.normal(0,1,(H,W)).astype(np.float32),(0,0),sigmaX=40,sigmaY=1.2)[...,None])
    img=base*(1-fr[...,None])+wood*fr[...,None]
    img[1368:]=np.array((0.08,0.07,0.07),np.float32)
    return Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).convert("RGBA")
CORK=_cork()
_IF={}
def F(n,s):
    k=(n,s)
    if k not in _IF: _IF[k]=ImageFont.truetype(P.FD+n,s)
    return _IF[k]
HAND="NothingYouCouldDo-Regular.ttf"; TYPE="IBMPlexMono-Bold.ttf"; HEAD="Gloock-Regular.ttf"
def paste(img,item,x,y,rot=0.0,sc=1.0,a=1.0,shadow=True,pin_col=(205,40,35)):
    """pin an item: rotate, cast a soft drop shadow, composite centred at (x,y)"""
    sc=sc*1.28
    if a<=0.01 or sc<=0.02: return
    it=item if sc==1 else item.resize((max(1,int(item.width*sc)),max(1,int(item.height*sc))),Image.LANCZOS)
    it=it.rotate(rot,expand=True,resample=Image.BICUBIC)
    if a<1: al=it.getchannel("A").point(lambda v:int(v*a)); it.putalpha(al)
    if shadow:
        sh=Image.new("RGBA",it.size,(0,0,0,0)); sh.putalpha(it.getchannel("A").point(lambda v:int(v*0.45)))
        sh=sh.filter(ImageFilter.GaussianBlur(9)); img.alpha_composite(sh,(int(x-it.width/2+10),int(y-it.height/2+14)))
    img.alpha_composite(it,(int(x-it.width/2),int(y-it.height/2)))
    hh=item.height*sc; py=y-hh/2+9*sc; px=x+math.sin(math.radians(rot))*(hh/2-9*sc)
    if pin_col is not None and sc>0.6: pin(img,px,py,pin_col)
    return (px,py)
def pin(img,x,y,col=(205,40,35)):
    d=ImageDraw.Draw(img); d.ellipse((x-12+5,y-12+7,x+12+5,y+12+7),fill=(0,0,0,90)); d.ellipse((x-13,y-13,x+13,y+13),fill=col+(255,)); d.ellipse((x-7,y-8,x-1,y-2),fill=(255,255,255,170))
def yarn(img,pts,a=1.0):
    d=ImageDraw.Draw(img)
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        mx,my=(x0+x1)/2,(y0+y1)/2+18
        seg=[(x0+(mx-x0)*u*2 if u<0.5 else mx+(x1-mx)*(u-0.5)*2,(y0+(my-y0)*u*2) if u<0.5 else my+(y1-my)*(u-0.5)*2) for u in np.linspace(0,1,12)]
        d.line(seg,fill=(190,25,25,int(255*a)),width=5)
# ---- item factories ----
def polaroid(draw_fn,w=430,h=470,caption=None):
    im=Image.new("RGBA",(w,h),(248,246,240,255)); ph=Image.new("RGBA",(w-40,h-110),(30,30,30,255)); draw_fn(ph,ImageDraw.Draw(ph)); im.alpha_composite(ph,(20,20))
    if caption: ImageDraw.Draw(im).text((w/2,h-48),caption,font=F(HAND,36),fill=(30,30,60,255),anchor="mm")
    return im
def card(lines,w=480,h=300,head=None,font=TYPE,fs=34,col=(25,25,30)):
    im=Image.new("RGBA",(w,h),(252,250,244,255)); d=ImageDraw.Draw(im)
    d.line((0,62,w,62),fill=(220,80,80,255),width=3)
    for k in range(1,8): d.line((0,62+k*36,w,62+k*36),fill=(160,190,230,255),width=1)
    if head: d.text((24,32),head,font=F(font,fs),fill=col+(255,),anchor="lm")
    for i,s in enumerate(lines): d.text((24,62+i*36+18+ (4 if font==TYPE else 0)),s,font=F(HAND if font==TYPE else font,30 if font==TYPE else fs),fill=(30,30,80,255),anchor="lm")
    return im
def sticky(text,w=250,col=(255,232,90),fs=40):
    im=Image.new("RGBA",(w,w),col+(255,)); d=ImageDraw.Draw(im); d.rectangle((0,0,w,36),fill=tuple(int(c*0.92) for c in col)+(255,))
    lines=text.split("\n")
    for i,s in enumerate(lines): d.text((w/2,w/2+(i-(len(lines)-1)/2)*fs*1.15+10),s,font=F(HAND,fs),fill=(30,30,50,255),anchor="mm")
    return im
def clipping(head,sub,w=470,h=300):
    im=Image.new("RGBA",(w,h),(236,230,214,255)); d=ImageDraw.Draw(im)
    d.text((w/2,40),sub,font=F(HEAD,30),fill=(30,30,30,255),anchor="mm"); d.line((20,64,w-20,64),fill=(40,40,40,255),width=2)
    d.text((w/2,110),head,font=F(HEAD,44),fill=(20,20,20,255),anchor="mm")
    g=np.random.default_rng(len(head))
    for r in range(5):
        for c in range(2): d.line((24+c*(w/2),160+r*24,24+c*(w/2)+g.uniform(140,200),160+r*24),fill=(110,110,110,255),width=6)
    pts=[(0,0)]+[(x,g.uniform(0,7)) for x in range(20,w,20)]+[(w,0)]
    return im
# ---- photo scenes (drawn inside polaroids) ----
def ph_meatsky(im,d):
    w,h=im.size; d.rectangle((0,0,w,h),fill=(150,190,230,255)); d.rectangle((0,h*0.72,w,h),fill=(110,140,70,255))
    d.polygon([(60,h*0.72),(60,h*0.52),(140,h*0.40),(220,h*0.52),(220,h*0.72)],fill=(170,70,50,255)); d.rectangle((120,h*0.6,160,h*0.72),fill=(70,40,30,255))
    g=np.random.default_rng(1)
    for _ in range(24): x,y=g.uniform(10,w-10),g.uniform(10,h*0.7); s=g.uniform(6,14); d.polygon([(x,y),(x+s,y+3),(x+s-2,y+s),(x-3,y+s-2)],fill=(170,40,50,255))
def ph_soap(im,d):
    w,h=im.size; d.rectangle((0,0,w,h),fill=(160,195,225,255)); d.rectangle((0,h*0.7,w,h),fill=(105,135,70,255))
    d.ellipse((w*0.45,h*0.48,w*0.8,h*0.72),fill=(40,40,40,255)); d.polygon([(w*0.5,h*0.72),(w*0.62,h*0.85),(w*0.74,h*0.72)],fill=(230,120,40,255))
    d.ellipse((w*0.18,h*0.3,w*0.28,h*0.4),fill=(230,190,160,255)); d.polygon([(w*0.14,h*0.4),(w*0.32,h*0.4),(w*0.36,h*0.75),(w*0.10,h*0.75)],fill=(90,70,140,255))
    g=np.random.default_rng(2)
    for _ in range(16): x,y=g.uniform(10,w-10),g.uniform(10,h*0.55); s=g.uniform(6,12); d.polygon([(x,y),(x+s,y+3),(x+s-2,y+s),(x-3,y+s-2)],fill=(170,40,50,255))
def ph_tasters(im,d):
    w,h=im.size; d.rectangle((0,0,w,h),fill=(200,185,150,255))
    for cx,col in ((w*0.3,(80,90,120)),(w*0.7,(120,80,60))):
        d.ellipse((cx-35,h*0.18,cx+35,h*0.36),fill=(230,190,160,255)); d.rectangle((cx-45,h*0.12,cx+45,h*0.18),fill=(50,40,30,255)); d.rectangle((cx-30,h*0.06,cx+30,h*0.14),fill=(50,40,30,255))
        d.polygon([(cx-55,h*0.36),(cx+55,h*0.36),(cx+70,h),(cx-70,h)],fill=col+(255,))
    d.polygon([(w*0.45,h*0.42),(w*0.55,h*0.40),(w*0.56,h*0.48),(w*0.46,h*0.50)],fill=(170,40,50,255))
def ph_vultures(im,d):
    w,h=im.size; d.rectangle((0,0,w,h),fill=(175,200,225,255))
    for i,(x,y,s) in enumerate(((w*0.3,h*0.3,1.0),(w*0.65,h*0.22,0.8),(w*0.55,h*0.5,1.2),(w*0.2,h*0.6,0.7))):
        d.polygon([(x-60*s,y-6*s),(x-20*s,y-18*s),(x,y),(x+20*s,y-18*s),(x+60*s,y-6*s),(x+20*s,y-4*s),(x,y+8*s),(x-20*s,y-4*s)],fill=(30,25,25,255))
        d.ellipse((x+2*s,y-6*s,x+10*s,y+2*s),fill=(200,90,80,255))
    g=np.random.default_rng(4)
    for _ in range(10): x,y=g.uniform(w*0.3,w*0.7),g.uniform(h*0.55,h*0.95); s=g.uniform(6,11); d.polygon([(x,y),(x+s,y+3),(x+s-2,y+s),(x-3,y+s-2)],fill=(170,40,50,255))
def kentucky_card():
    im=Image.new("RGBA",(470,300),(252,250,244,255)); d=ImageDraw.Draw(im)
    pts=[(40,110),(120,90),(220,80),(330,70),(400,60),(440,90),(420,140),(380,170),(330,200),(200,210),(60,215),(30,180)]
    d.polygon(pts,fill=(225,215,185,255),outline=(60,60,60,255)); d.text((235,40),"KENTUCKY",font=F(TYPE,32),fill=(30,30,30,255),anchor="mm")
    d.ellipse((330,108,350,128),fill=(205,40,35,255)); d.text((320,150),"Bath Co.",font=F(HAND,34),fill=(30,30,80,255),anchor="mm")
    d.text((235,262),"near Olympia Springs",font=F(HAND,30),fill=(30,30,80,255),anchor="mm")
    return im
def strip_card():
    im=Image.new("RGBA",(480,320),(252,250,244,255)); d=ImageDraw.Draw(im)
    d.rectangle((50,90,380,220),outline=(30,30,30,255),width=4)
    g=np.random.default_rng(6)
    for _ in range(40): x,y=g.uniform(60,370),g.uniform(100,210); d.rectangle((x,y,x+7,y+6),fill=(170,40,50,255))
    d.line((50,250,380,250),fill=(30,30,30,255),width=2); d.text((215,280),"~100 yards",font=F(HAND,38),fill=(30,30,80,255),anchor="mm")
    d.line((398,90,398,220),fill=(30,30,30,255),width=2); d.text((408,155),"50",font=F(HAND,34),fill=(30,30,80,255),anchor="lm")
    d.text((240,45),"THE FALL ZONE",font=F(TYPE,34),fill=(30,30,30,255),anchor="mm")
    return im
def nostoc_card():
    im=card([],480,320,"THEORY #1: NOSTOC",TYPE,32); d=ImageDraw.Draw(im)
    d.ellipse((150,110,330,250),fill=(120,150,70,200)); d.ellipse((190,130,260,180),fill=(170,200,110,200))
    d.text((240,285),"jelly-like bacterium",font=F(HAND,32),fill=(30,30,80,255),anchor="mm")
    return im
def stamp(img,x,y,text,a=1.0,rot=-14):
    L=Image.new("RGBA",(520,160),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rectangle((6,6,514,154),outline=(200,30,30,int(230*a)),width=8); d.text((260,82),text,font=F(HEAD,80),fill=(200,30,30,int(230*a)),anchor="mm")
    L=L.rotate(rot,expand=True,resample=Image.BICUBIC); img.alpha_composite(L,(int(x-L.width/2),int(y-L.height/2)))
def pop(t,e): return spring((t-e)/0.45)
def ap(t,s,e): return fa(t,s-0.1,e-0.3,0.25,0.25)
# pre-built items
P_SKY=polaroid(ph_meatsky,430,470,"Mar 3, 1876"); P_SOAP=polaroid(ph_soap,400,440,"soap-making"); P_TASTE=polaroid(ph_tasters,400,440,"the tasters"); P_VULT=polaroid(ph_vultures,430,470,"suspects")
C_KY=kentucky_card(); C_STRIP=strip_card(); C_NOSTOC=nostoc_card()
C_LAB=card(["lung tissue","muscle","cartilage"],470,250,"LAB REPORT",TYPE,32)
C_NYT=clipping("SHOWER OF MEAT","The New York Times · 1876"); C_SA=clipping("A STRANGE FALL","Scientific American · 1876")
C_DATE=card(["Bath County, Kentucky","clear sky"],470,220,"MARCH 3, 1876",TYPE,34)
# ================= shots =================
def s_hook(t,end=False):
    img=CORK.copy()
    k=pop(t,-0.2) if not end else 1.0
    p1=paste(img,P_SKY,540,560,-4,k)
    paste(img,C_DATE,560,1060,3,pop(t,EV["date"]+0.4) if not end else 1.0,pin_col=(40,90,200))
    p3=None
    if (t>EV["meat"]-0.2) or end: p3=paste(img,sticky("MEAT?!"),860,250,8,pop(t,EV["meat"]-0.2) if not end else 1.0,pin_col=(240,200,40))
    if end:
        p4=paste(img,P_VULT,230,250,6,0.55,pin_col=None); pin(img,230,140); yarn(img,[(230,140),p1,p3]); pin(img,*p1); pin(img,*p3,(240,200,40))
    return img
def s_scene(t):
    img=CORK.copy(); q1=paste(img,C_KY,540,330,-3,pop(t,S("scene")["s"]+0.1))
    if t>EV["woman"]-0.3:
        q2=paste(img,P_SOAP,560,900,4,pop(t,EV["woman"]-0.3)); yarn(img,[q1,q2]); pin(img,*q1); pin(img,*q2)
    if t>EV["soap"]: paste(img,sticky("making\nsoap",230,(255,180,200)),860,1150,-8,pop(t,EV["soap"]))
    return img
def s_strip(t):
    img=CORK.copy(); paste(img,C_STRIP,540,440,2,pop(t,EV["pieces"]-0.4))
    if t>EV["inches"]-0.3: paste(img,sticky("~2 inches\neach",260),760,960,-6,pop(t,EV["inches"]-0.3))
    if t>EV["bigger"]-0.2: paste(img,sticky("a few\nbigger!",230,(160,230,170)),330,1010,7,pop(t,EV["bigger"]-0.2))
    return img
def s_press(t):
    img=CORK.copy(); paste(img,C_NYT,540,420,-5,pop(t,EV["nyt"]-0.3))
    if t>EV["sciam"]-0.3: paste(img,C_SA,560,880,4,pop(t,EV["sciam"]-0.3))
    return img
def s_taste(t):
    img=CORK.copy(); paste(img,P_TASTE,540,520,-3,pop(t,S("clues")["s"]+0.1))
    if t>EV["mutton"]-0.3: paste(img,sticky("mutton?",230),300,1080,-8,pop(t,EV["mutton"]-0.3))
    if t>EV["venison"]-0.3: paste(img,sticky("venison?",230,(255,180,200)),780,1080,6,pop(t,EV["venison"]-0.3))
    return img
def s_lab(t):
    img=CORK.copy(); paste(img,C_LAB,540,520,2,pop(t,EV["scient"]-0.2))
    if t>EV["lung"]: paste(img,sticky("NOT a\nplant?",240),780,950,-7,pop(t,EV["lung"]))
    return img
def s_nostoc(t):
    img=CORK.copy(); paste(img,C_NOSTOC,540,520,-2,pop(t,Lx("One early")[0]+0.3))
    if t>EV["norain"]-0.3: stamp(img,540,560,"NO RAIN",sm((t-EV["norain"]+0.3)/0.25))
    return img
def s_vult(t):
    img=CORK.copy(); v1=paste(img,P_VULT,540,540,-3,pop(t,EV["fav"]-0.3))
    if t>EV["vultures"]-0.2:
        v2=paste(img,sticky("THEORY #2\nVULTURES",290,(160,230,170),40),540,1100,4,pop(t,EV["vultures"]-0.2),pin_col=(240,200,40)); yarn(img,[v1,v2]); pin(img,*v1); pin(img,*v2,(240,200,40))
    return img
def s_why(t):
    img=CORK.copy(); paste(img,P_VULT,330,430,-6,1.0)
    if t>EV["really"]-0.3: paste(img,card(["they throw up to get","light enough for a","quick escape"],520,260,"FIELD NOTE",TYPE,32),600,960,3,pop(t,EV["really"]-0.3))
    return img
def s_end(t): return s_hook(t,end=True)
TR=0.30; TOTAL=B.TOTAL; LOOPD=0.55
SHOTS=[(0.0,s_hook),(S("scene")["s"],s_scene),(Lx("The pieces")[0]-0.3,s_strip),(Lx("The New York")[0]-0.3,s_press),(S("clues")["s"],s_taste),
       (Lx("Scientists who")[0]-0.3,s_lab),(Lx("One early")[0]-0.3,s_nostoc),(S("answer")["s"],s_vult),(Lx("Vultures really")[0]-0.3,s_why),(Lx("So if it ever")[0]-0.3,s_end)]
def shot_at(t): return [k for k,(s,_) in enumerate(SHOTS) if s<=t][-1]
def flash(i1,i2,u):
    """camera flash: the board blows out white and the next shot is snapped in"""
    src=i1 if u<0.5 else i2
    k=max(0.0,1-abs(u-0.5)*2.6)**1.4
    z=1+0.04*math.sin(math.pi*u)
    a=np.asarray(src.convert("RGB")).astype(np.float32)
    if z!=1:
        M2=cv2.getRotationMatrix2D((W/2,700),0,z); a=cv2.warpAffine(a,M2,(W,H),borderMode=cv2.BORDER_REPLICATE)
    a=a*(1-k)+255*k*np.array((1,0.98,0.94),np.float32)
    out=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert("RGBA"); return out
def compose(t):
    i=shot_at(max(t,0)); st=SHOTS[i][0]; nb=SHOTS[i+1][0] if i+1<len(SHOTS) else 1e9; pb=st if i>0 else -1e9
    pair=None
    if t>nb-TR: pair=(SHOTS[i][1],SHOTS[i+1][1],t,t,cl((t-(nb-TR))/(2*TR)))
    elif t<pb+TR: pair=(SHOTS[i-1][1],SHOTS[i][1],t,t,cl((t-(pb-TR))/(2*TR)))
    elif t>TOTAL-LOOPD: pair=(SHOTS[i][1],SHOTS[0][1],t,t-TOTAL,cl((t-(TOTAL-LOOPD))/LOOPD))
    if pair is None: img=SHOTS[i][1](t)
    else:
        fa_,fb_,ta,tb,u=pair; img=flash(fa_(ta) if u<0.5 else None,fb_(tb) if u>=0.5 else None,u)
    bot=CORK.crop((0,1340,W,H)); img.alpha_composite(bot,(0,1340))
    o2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(o2); B.subtitles(d2,t); o2.alpha_composite(B.WM,((W-B.WM.width)//2,1775))
    img.alpha_composite(o2); return img.convert("RGB")
if __name__=="__main__":
    for tt in map(float,sys.argv[1:]): compose(tt).save(f"t_{tt:06.2f}.jpg",quality=85)
