# pro.py — Orbithos PRO Shorts kit
# full-bleed 720x1280 float canvas -> 1080x1920, cinematic post (camera, bloom, filmic tone, vignette, grain),
# big word-chunk karaoke captions in the safe zone (active word orange), hook title on first frame + loop return.
import numpy as np, cv2, math, json, re, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1920; w,h=720,1280; K=W/w
yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
def cl(x): return min(max(x,0.0),1.0)
def sm(x): x=cl(x); return x*x*(3-2*x)
def eout(x): x=cl(x); return 1-(1-x)**3
def ein(x): x=cl(x); return x*x*x
def fa(t,s,e,fi=0.3,fo=0.3): return sm((t-s)/fi)*(1-sm((t-e)/fo))
def spring(x): x=cl(x); return 1-math.exp(-7*x)*math.cos(10*x)
def lerp(a,b,k): return a+(b-a)*k
IFD="/usr/share/fonts/opentype/inter/"; TFD="/home/claude/toolkit/assets/fonts/"; _FC={}
def IF(sz,name="InterDisplay-Black"):
    k=(name,int(sz))
    if k not in _FC: _FC[k]=ImageFont.truetype((IFD+name+".otf") if os.path.exists(IFD+name+".otf") else (TFD+name+".ttf"),int(sz))
    return _FC[k]
WM=Image.open("/home/claude/toolkit/core/wm_orbithos.png").convert("RGBA")
ORANGE=(255,168,28); WHITE=(255,255,255)

# ---------------- timeline / word timing ----------------
def load(path):
    T=json.load(open(path)); return T,T["lines"],T["scenes"],T["total"]
def _syl(tok):
    d=re.sub(r"[^0-9]","",tok)
    if d: return 1.0*len(d)+0.4
    s=re.sub(r"[^a-z]","",tok.lower())
    n=len(re.findall(r"[aeiouy]+",s)); n-= 1 if s.endswith("e") and n>1 and not s.endswith("le") else 0
    return max(1,n)
def words_of(LINES):
    out=[]
    for ln in LINES:
        toks=ln["en"].split(); wt=[]; gap=[]
        for tk in toks:
            wt.append(_syl(tk)+0.45); gap.append(0.9 if tk[-1] in ".:;?!" else (0.55 if tk[-1]=="," else 0.0))
        tot=sum(wt)+sum(gap[:-1]); acc=0; s,e=ln["s"],ln["e"]
        for i,tk in enumerate(toks):
            ws=s+(e-s)*acc/tot; acc+=wt[i]; we=s+(e-s)*acc/tot; acc+=gap[i] if i<len(toks)-1 else 0
            out.append(dict(w=tk,s=ws,e=we,li=ln["i"]))
    return out
def word_t(WORDS,li,sub,off=0.0):
    """start time of first word in line li whose text contains sub"""
    for x in WORDS:
        if x["li"]==li and sub.lower() in x["w"].lower(): return x["s"]+off
    raise KeyError((li,sub))
def _isnum(tk): t=re.sub(r"[^A-Za-z0-9]","",tk); return bool(re.search(r"[0-9]",t)) or (len(t)>=2 and t.isupper())
def chunks_of(WORDS,LINES,maxw=3,maxc=15):
    ch=[]; cur=[]; an=-1
    for i,x in enumerate(WORDS):
        brk=False
        if cur:
            brk=(cur[-1]["li"]!=x["li"] or len(cur)>=maxw or sum(len(y["w"])+1 for y in cur)+len(x["w"])>maxc or cur[-1]["w"][-1] in ".,:;?!")
            if _isnum(x["w"]) and not _isnum(cur[-1]["w"]) and not (len(cur)==1 and len(cur[0]["w"])<=3): brk=True
            if an>=1: brk=True
        if brk: ch.append(cur); cur=[]; an=-1
        cur.append(x)
        if _isnum(x["w"]): an=0
        elif an>=0: an+=1
    if cur: ch.append(cur)
    res=[]
    for k,c in enumerate(ch):
        li=c[0]["li"]; ln=LINES[li]
        nxt_line=LINES[li+1]["s"] if li+1<len(LINES) else ln["e"]+0.5
        last=not (k+1<len(ch) and ch[k+1][0]["li"]==li)
        if not last: end=ch[k+1][0]["s"]-0.06
        else: end=min(ln["e"]+0.35,nxt_line-0.10)
        res.append(dict(words=c,s=c[0]["s"]-0.06,e=end,last=last))
    return res

# ---------------- captions ----------------
class Captions:
    def __init__(self,LINES,y=1215,size=104,maxw=3,maxc=15,upper=True,x=540):
        self.W=words_of(LINES); self.C=chunks_of(self.W,LINES,maxw,maxc); self.y=y; self.size=size; self.up=upper; self.x=x; self.cache={}
    def _img(self,ci,act):
        key=(ci,act)
        if key in self.cache: return self.cache[key]
        c=self.C[ci]["words"]; txts=[(x["w"].upper() if self.up else x["w"]) for x in c]
        sz=self.size; f=IF(sz)
        while sum(f.getlength(t+" ") for t in txts)>940 and sz>60: sz-=4; f=IF(sz)
        sp=f.getlength(" "); tw=sum(f.getlength(t) for t in txts)+sp*(len(txts)-1)
        pad=40; im=Image.new("RGBA",(int(tw+2*pad),int(sz*1.5+2*pad)),(0,0,0,0)); d=ImageDraw.Draw(im)
        x=pad; base=pad+sz*1.05
        sh=Image.new("RGBA",im.size,(0,0,0,0)); ds=ImageDraw.Draw(sh)
        for k,tx in enumerate(txts):
            ds.text((x,base+8),tx,font=f,fill=(0,0,0,170),anchor="ls",stroke_width=12,stroke_fill=(0,0,0,170)); x+=f.getlength(tx)+sp
        sh=sh.filter(ImageFilter.GaussianBlur(9)); im.alpha_composite(sh); x=pad
        for k,tx in enumerate(txts):
            col=ORANGE if k==act else WHITE
            d.text((x,base),tx,font=f,fill=col+(255,),anchor="ls",stroke_width=10,stroke_fill=(10,10,14,255)); x+=f.getlength(tx)+sp
        self.cache[key]=im; return im
    def draw(self,img,t,alpha=1.0):
        for ci,c in enumerate(self.C):
            if c["s"]<=t<c["e"]:
                act=0
                for k,x in enumerate(c["words"]):
                    if t>=x["s"]-0.03: act=k
                im=self._img(ci,act); u=(t-c["s"])/0.16; sc=0.80+0.20*spring(u)
                a=alpha*(1-sm((t-(c["e"]-0.08))/0.08)) if c["last"] else alpha
                if sc!=1: im=im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.BILINEAR)
                if a<0.999: im=im.copy(); al=np.array(im); al[:,:,3]=(al[:,:,3]*a).astype(np.uint8); im=Image.fromarray(al)
                img.alpha_composite(im,(int(self.x-im.width/2),int(self.y-im.height*0.62)))
                return

# ---------------- hook title ----------------
def hook_title(img,rows,a=1.0,y=250,size=150,sc=1.0,gap=1.02):
    """rows=[(text,col),...] huge stacked title, black stroke + soft shadow"""
    if a<=0.01: return
    lay=Image.new("RGBA",(W,int(len(rows)*size*gap+260)),(0,0,0,0)); d=ImageDraw.Draw(lay); sh=Image.new("RGBA",lay.size,(0,0,0,0)); ds=ImageDraw.Draw(sh)
    yy_=size*1.0+60
    for tx,col in rows:
        sz=size; f=IF(sz)
        while f.getlength(tx)>1000 and sz>60: sz-=4; f=IF(sz)
        ds.text((W/2,yy_+10),tx,font=f,fill=(0,0,0,190),anchor="ms",stroke_width=14,stroke_fill=(0,0,0,190))
        d.text((W/2,yy_),tx,font=f,fill=col+(255,),anchor="ms",stroke_width=12,stroke_fill=(8,8,12,255)); yy_+=sz*gap
    sh=sh.filter(ImageFilter.GaussianBlur(12)); sh.alpha_composite(lay); lay=sh
    if sc!=1: lay=lay.resize((int(lay.width*sc),int(lay.height*sc)),Image.BILINEAR)
    if a<0.999: al=np.array(lay); al[:,:,3]=(al[:,:,3]*a).astype(np.uint8); lay=Image.fromarray(al)
    img.alpha_composite(lay,(int(W/2-lay.width/2),int(y-60*sc)))

def label(img,tx,x,y,size=56,col=WHITE,bg=None,a=1.0,font="InterDisplay-Black",anchor="mm",stroke=8,sc=1.0):
    """on-screen card text (full-res coords)"""
    if a<=0.01: return
    f=IF(size*sc,font); d=ImageDraw.Draw(img)
    if bg is not None:
        bb=d.textbbox((x,y),tx,font=f,anchor=anchor); p=int(18*sc)
        ov=Image.new("RGBA",img.size,(0,0,0,0)); do=ImageDraw.Draw(ov)
        do.rounded_rectangle((bb[0]-p,bb[1]-p*0.8,bb[2]+p,bb[3]+p*0.8),radius=int(14*sc),fill=bg+(int(235*a),)); img.alpha_composite(ov)
        d.text((x,y),tx,font=f,fill=col+(int(255*a),),anchor=anchor)
    else:
        d.text((x,y),tx,font=f,fill=col+(int(255*a),),anchor=anchor,stroke_width=int(stroke*sc),stroke_fill=(8,8,12,int(255*a)))

# ---------------- cinematic post ----------------
VIG=(1-0.55*np.clip(((xx/w-0.5)**2*1.3+(yy/h-0.5)**2*0.9)*2.0,0,1))[...,None].astype(np.float32)
_G=[np.random.default_rng(100+i).normal(0,4.2,(H//2,W//2,1)).astype(np.float32) for i in range(6)]
GRAIN=[cv2.resize(g,(W,H),interpolation=cv2.INTER_NEAREST)[...,None] for g in _G]
def aces(x):
    x=np.maximum(x,0)*1.05; return np.clip((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14),0,1)
def camera(buf,zoom=1.0,cx=0.5,cy=0.5,dx=0.0,dy=0.0,rot=0.0):
    if abs(zoom-1)<1e-4 and dx==0 and dy==0 and rot==0: return buf
    M=cv2.getRotationMatrix2D((cx*w,cy*h),rot,zoom); M[0,2]+=dx; M[1,2]+=dy
    return cv2.warpAffine(buf,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
def shake(t,t0,amp=10,dur=0.5,f=31):
    k=t-t0
    if k<0 or k>dur: return 0.0,0.0
    e=(1-k/dur)**2*amp; return e*math.sin(k*f*6.28),e*math.cos(k*f*4.7)
def punch(t,times,amt=0.07,dur=0.35):
    z=1.0
    for t0 in times:
        k=t-t0
        if 0<=k<dur: z+=amt*(1-eout(k/dur))
    return z
def post(buf,bloom=0.55,thr=0.62,tint=(1.0,1.0,1.0),lift=0.0):
    hi=np.clip(buf-thr,0,None)
    small=cv2.resize(hi,(w//4,h//4),interpolation=cv2.INTER_AREA)
    b=cv2.GaussianBlur(small,(0,0),3)+0.7*cv2.GaussianBlur(small,(0,0),10)
    buf=buf+cv2.resize(b,(w,h),interpolation=cv2.INTER_LINEAR)*bloom
    buf=aces(buf*np.array(tint,np.float32))*VIG+lift
    return buf
def to_img(buf,fi):
    a=cv2.resize(np.clip(buf,0,1),(W,H),interpolation=cv2.INTER_CUBIC)*255.0
    a=np.clip(a+GRAIN[fi%len(GRAIN)],0,255).astype(np.uint8)
    return Image.fromarray(a).convert("RGBA")
def finish(img,cap,t,cap_a=1.0):
    cap.draw(img,t,cap_a); img.alpha_composite(WM,((W-WM.width)//2,1775)); return img.convert("RGB")

# ---------------- drawing helpers (canvas coords, float32 RGB 0..1+) ----------------
def glow(buf,x,y,r,col,a=1.0):
    x0,x1=max(0,int(x-r*4)),min(w,int(x+r*4)+1); y0,y1=max(0,int(y-r*4)),min(h,int(y+r*4)+1)
    if x0>=x1 or y0>=y1: return
    d2=((xx[y0:y1,x0:x1]-x)**2+(yy[y0:y1,x0:x1]-y)**2)/(r*r)
    buf[y0:y1,x0:x1]+=(np.exp(-d2)*a)[...,None]*np.array(col,np.float32)
def fbm(shape,seed,octs=5,base=4,aspect=None):
    g=np.random.default_rng(seed); out=np.zeros(shape,np.float32); amp=1.0
    asp=aspect if aspect else shape[1]/shape[0]
    for o in range(octs):
        n_=base*2**o; gh=n_+2; gw=max(3,int(n_*asp)+2)
        n=g.normal(0,1,(gh,gw)).astype(np.float32)
        out+=cv2.resize(n,(shape[1],shape[0]),interpolation=cv2.INTER_CUBIC)*amp; amp*=0.5
    return (out-out.mean())/(out.std()+1e-6)
def starfield(seed=7,n=1400,neb=None):
    g=np.random.default_rng(seed); b=np.zeros((h,w,3),np.float32)
    if neb is not None:
        n1=fbm((h,w),seed+1,6,3); n2=fbm((h,w),seed+2,6,5)
        m=np.clip(n1*0.5+0.2,0,None)**2
        b+=m[...,None]*np.array(neb[0],np.float32)*0.5+np.clip(n2,0,None)[...,None]**2*np.array(neb[1],np.float32)*0.12
    for i in range(n):
        x,y=g.uniform(0,w),g.uniform(0,h); m=g.pareto(2.2)*0.08
        c=np.array([1.0,0.9+0.1*g.random(),0.8+0.25*g.random()],np.float32)
        xi,yi=int(x),int(y); b[yi,xi]+=c*min(m*3,3)
    b=b+cv2.GaussianBlur(b,(0,0),1.2)*1.5
    return b
