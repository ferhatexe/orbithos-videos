import json
T=json.load(open("/home/claude/vid54/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(atlas=_f("Atlas never",0.1),earth=_f("Atlas never",0.9),
logos=_f("Statues and",0.6),wrong=_f("Statues and",1.2),what=_f("Statues and",1.8),holding=_f("Statues and",2.6),
titan=_f("Atlas was a Titan",0.9),zeus=_f("Atlas was a Titan",1.7),lost=_f("Atlas was a Titan",2.3),
punish=_f("His punishment",0.3),west=_f("His punishment",1.3),sky=_f("His punishment",2.8),forever=_f("His punishment",3.74),
planet=_f("Not the planet",0.4),heavens=_f("Not the planet",1.0),
heracles=_f("Heracles once",0.2),tricked=_f("Heracles once",0.9),back=_f("Heracles once",2.2),
perseus=_f("In another myth",0.9),stone=_f("In another myth",1.7),mountains=_f("In another myth",2.9),
mixup=_f("The mix-up",0.1),statues=_f("The mix-up",1.0),farnese=_f("The mix-up",2.2),roman=_f("The mix-up",3.3),years=_f("The mix-up",4.9),
ball=_f("He carries",0.9),look=_f("He carries",1.6),const=_f("He carries",3.2),
oldest=_f("It's one of",0.6),skymap=_f("It's one of",2.0),
y1595=_f("In 1595",0.4),mercator=_f("In 1595",1.8),titled=_f("In 1595",2.8),stuck=_f("In 1595",3.9),
atlantic=_f("The Atlantic",0.4),named=_f("The Atlantic",1.5),sea=_f("The Atlantic",2.7),
nomatter=_f("So no matter",0.2),logos2=_f("So no matter",1.0))
