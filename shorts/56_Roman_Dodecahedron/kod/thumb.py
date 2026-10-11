import sys; sys.path.insert(0,"/home/claude/toolkit")
from r56 import *
import thumbstd
b=bg(); border(b)
dodeca(b,270,468,140,0.95,0.52,t=0.0)
img=Image.fromarray((paint(tiles(b))*255).astype(np.uint8))
thumbstd.make(img,"NOBODY KNOWS","WHAT THIS WAS FOR",(236,196,110),"HISTORY · ROMAN MYSTERY","/mnt/user-data/outputs/orbithos_roman_dodecahedron_kucuk_resim.jpg",band=(40,22,16,230),label_col=(122,34,24))
