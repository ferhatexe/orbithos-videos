import json
T=json.load(open("/home/claude/vid67/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(gold0=_f("The gold in",0.3),ring=_f("The gold in",1.0),dead=_f("The gold in",2.7),smash=_f("The gold in",3.5),
forge=_f("Stars forge",0.5),cores=_f("Stars forge",1.7),iron=_f("Stars forge",2.4),beyond=_f("Stars forge",3.3),paying=_f("Stars forge",4.5),
heavier=_f("Heavier atoms",0.2),flood=_f("Heavier atoms",1.3),neutrons=_f("Heavier atoms",1.9),decay=_f("Heavier atoms",3.2),
nstars=_f("One place",1.5),collide=_f("One place",2.3),
city=_f("Each one is",0.7),hsun=_f("Each one is",1.6),
y2017=_f("In 2017",0.1),detect=_f("In 2017",1.8),waves=_f("In 2017",2.8),exactly=_f("In 2017",4.0),crash=_f("In 2017",4.7),dist=_f("In 2017",5.3),
tele=_f("Telescopes then",0.2),debris=_f("Telescopes then",1.3),kilonova=_f("Telescopes then",2.2),
light=_f("In its light",0.3),fresh=_f("In its light",0.8),est=_f("In its light",2.4),five=_f("In its light",3.1),sr=_f("In its light",4.2),
gold2=_f("Gold, platinum",0.1),plat=_f("Gold, platinum",0.7),uran=_f("Gold, platinum",1.4),violent=_f("Gold, platinum",2.7),born=_f("Gold, platinum",4.3),
seegold=_f("So the next",1.1),remember=_f("So the next",1.6))
