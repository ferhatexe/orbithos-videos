import json
T=json.load(open("/home/claude/vid64/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(y1995=_f("In 1995",0.1),hubble=_f("In 1995",2.2),patch=_f("In 1995",2.8),empty=_f("In 1995",4.3),
pin=_f("A spot about",1.1),arm=_f("A spot about",1.9),
dipper=_f("Near the Big",0.5),nothing=_f("Near the Big",2.4),
waste=_f("Some colleagues",1.3),time=_f("Some colleagues",2.5),
ten=_f("For ten",0.5),stared=_f("For ten",2.3),n342=_f("For ten",3.4),expo=_f("For ten",4.1),
image=_f("Then the image",0.5),back=_f("Then the image",0.9),
speck=_f("Almost every",0.6),star=_f("Almost every",1.5),galaxy=_f("Almost every",2.5),n3000=_f("Almost every",3.4),
spirals=_f("Spirals, blobs",0.1),blobs=_f("Spirals, blobs",0.7),smudges=_f("Spirals, blobs",1.2),billions=_f("Spirals, blobs",2.5),
light=_f("Some of that light",0.4),years=_f("Some of that light",1.6),
y2004=_f("In 2004",0.1),udf=_f("In 2004",1.3),deeper=_f("In 2004",2.5),n10k=_f("In 2004",3.7),
special=_f("And that patch",0.9),anywhere=_f("And that patch",1.8),crowded=_f("And that patch",3.0),
emptysky=_f("So the next time",1.5),remember=_f("So the next time",2.1))
