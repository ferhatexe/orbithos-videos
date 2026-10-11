import json
T=json.load(open("/home/claude/vid52/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(moon=_f("The Moon is running",0.1),running=_f("The Moon is running",0.7),
cm=_f("About four",0.6),how=_f("About four",1.8),
y1969=_f("In 1969",0.5),apollo=_f("In 1969",1.4),mirrors=_f("In 1969",3.5),
lasers=_f("Scientists fire",0.9),catch=_f("Scientists fire",2.2),back=_f("Scientists fire",3.2),
trip=_f("The round trip",0.6),secs=_f("The round trip",1.4),
timing=_f("Timing it",0.2),slipping=_f("Timing it",1.9),nails=_f("Timing it",3.3),
tides=_f("The cause",0.6),pulls=_f("The cause",1.5),bulges=_f("The cause",2.8),
spins=_f("Earth spins",0.5),ahead=_f("Earth spins",2.6),tug=_f("Earth spins",3.4),
energy=_f("The Moon gains",0.8),higher=_f("The Moon gains",1.5),slows=_f("The Moon gains",2.6),
billion=_f("1.4 billion",0.6),day=_f("1.4 billion",2.0),eighteen=_f("1.4 billion",3.6),
future=_f("And in the far",0.6),small=_f("And in the far",2.0),eclipses=_f("And in the far",3.6),
allb=_f("All because",0.1),every=_f("All because",0.9))
