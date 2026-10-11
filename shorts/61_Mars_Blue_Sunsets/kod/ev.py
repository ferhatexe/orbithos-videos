import json
T=json.load(open("/home/claude/vid61/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(orange=_f("On Mars, the sky",1.1),sunsets=_f("On Mars, the sky",2.2),blue0=_f("On Mars, the sky",2.8),
curio=_f("NASA's Curiosity",0.5),photo=_f("NASA's Curiosity",1.3),y2015=_f("NASA's Curiosity",2.0),gale=_f("NASA's Curiosity",3.1),
earth=_f("On Earth",0.2),molec=_f("On Earth",0.9),scatter=_f("On Earth",1.4),daysblue=_f("On Earth",3.3),
esunset=_f("At sunset, sunlight",0.2),crosses=_f("At sunset, sunlight",1.0),away=_f("At sunset, sunlight",2.6),reds=_f("At sunset, sunlight",3.7),
less=_f("Mars has less",0.5),percent=_f("Mars has less",1.1),gas=_f("Mars has less",2.4),
dust=_f("Instead, fine dust",0.9),tints=_f("Instead, fine dust",2.2),
grains=_f("But the grains",0.4),size=_f("But the grains",1.3),fwd=_f("But the grains",2.4),direc=_f("But the grains",3.5),
bsunset=_f("So at sunset, a cool",0.3),glow=_f("So at sunset, a cool",1.2),gathers=_f("So at sunset, a cool",1.8),
reverse=_f("Like an Earth",0.3),
smaller=_f("The Sun looks",0.9),thirds=_f("The Sun looks",1.8),
high=_f("And high dust",0.3),twilight=_f("And high dust",1.2),hours=_f("And high dust",2.5),
watch=_f("So if you ever",0.7),remember=_f("So if you ever",2.1))
