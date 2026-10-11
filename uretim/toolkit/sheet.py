import sys,glob
from PIL import Image
fs=sys.argv[2:]; n=len(fs); cols=min(4,n); rows=(n+cols-1)//cols
S=Image.new("RGB",(cols*360,rows*640),(0,0,0))
for i,f in enumerate(fs): S.paste(Image.open(f).resize((360,640)),((i%cols)*360,(i//cols)*640))
S.save(sys.argv[1],quality=88)
