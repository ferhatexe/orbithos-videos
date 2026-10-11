"""Orbithos standard Shorts thumbnail (1080x1920). YouTube's Shorts grid crops to ~2:3 (y≈150..1770),
so everything important lives inside that safe zone: title band (top), artwork (middle), label pill + logo (bottom)."""
from PIL import Image, ImageDraw, ImageFont
W,H=1080,1920; FD="/mnt/skills/examples/canvas-design/canvas-fonts/" if __import__("os").path.isdir("/mnt/skills/examples/canvas-design/canvas-fonts/") else "/home/claude/toolkit/assets/fonts/"
def _fit(text,font,size,maxw):
    while size>40:
        f=ImageFont.truetype(FD+font,size)
        if f.getlength(text)<=maxw: return f
        size-=4
    return ImageFont.truetype(FD+font,size)
def make(bg,line1,line2,col2,label,out,wm_path="/home/claude/vid3/wm_orbithos.png",band=(14,18,40,215),label_col=(196,60,55)):
    img=bg.convert("RGBA").resize((W,H)); ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    d.rectangle([0,150,W,600],fill=band); img.alpha_composite(ov); d=ImageDraw.Draw(img)
    f1=_fit(line1,"BigShoulders-Bold.ttf",150,980); f2=_fit(line2,"BigShoulders-Bold.ttf",150,980)
    d.text((W//2,268),line1,font=f1,fill=(255,255,255),anchor="mm",stroke_width=6,stroke_fill=(10,12,30))
    d.text((W//2,455),line2,font=f2,fill=col2,anchor="mm",stroke_width=6,stroke_fill=(40,10,10))
    fl=_fit(label,"LibreBaskerville-Regular.ttf",50,820); tw=fl.getlength(label)
    d.rounded_rectangle([W//2-tw/2-34,1395,W//2+tw/2+34,1475],radius=12,fill=label_col,outline=(255,255,255),width=3)
    d.text((W//2,1436),label,font=fl,fill=(255,255,255),anchor="mm")
    wm=Image.open(wm_path).convert("RGBA"); wm=wm.resize((int(wm.width*1.45),int(wm.height*1.45)),Image.LANCZOS)
    img.alpha_composite(wm,((W-wm.width)//2,1590-wm.height//2))
    img.convert("RGB").save(out,quality=92)
