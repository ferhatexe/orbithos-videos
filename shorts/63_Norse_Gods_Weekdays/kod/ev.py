import json
T=json.load(open("/home/claude/vid63/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(week=_f("Every week",0.1),four=_f("Every week",1.2),norse=_f("Every week",1.9),noticing=_f("Every week",3.4),
romans=_f("It started",0.9),seven=_f("It started",1.8),lights=_f("It started",3.6),sky=_f("It started",4.3),
sun=_f("the Sun, the Moon",0.15),moon=_f("the Sun, the Moon",0.65),mars=_f("the Sun, the Moon",1.15),mercury=_f("the Sun, the Moon",1.6),jupiter=_f("the Sun, the Moon",2.15),venus=_f("the Sun, the Moon",2.65),saturn=_f("the Sun, the Moon",3.05),
germanic=_f("When Germanic",0.8),swapped=_f("When Germanic",2.5),
s_mars=_f("Mars, god of war",0.1),tiw=_f("Mars, god of war",1.2),onehand=_f("Mars, god of war",2.0),tuesday=_f("Mars, god of war",4.5),
s_merc=_f("Mercury became",0.1),woden=_f("Mercury became",0.9),odin=_f("Mercury became",1.7),wednesday=_f("Mercury became",2.7),
s_jup=_f("Jupiter, the",0.1),thor=_f("Jupiter, the",1.5),thursday=_f("Jupiter, the",2.1),
s_ven=_f("And Venus",0.3),frigg=_f("And Venus",0.9),friday=_f("And Venus",2.3),
saturday=_f("Saturday simply",0.1),s_sat=_f("Saturday simply",1.3),
spanish=_f("In Spanish",0.3),never=_f("In Spanish",1.1),martes=_f("In Spanish",1.8),mierc=_f("In Spanish",2.8),jueves=_f("In Spanish",3.85),viernes=_f("In Spanish",4.55),
thurs2=_f("So the next",1.3),remember=_f("So the next",1.85))
