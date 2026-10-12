import json
T=json.load(open("/home/claude/vid68/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(date=_f("On March",0.1),meat=_f("On March",2.4),sky=_f("On March",3.3),kentucky=_f("On March",3.9),
bath=_f("It happened",0.8),olympia=_f("It happened",1.8),woman=_f("It happened",2.7),soap=_f("It happened",3.4),
pieces=_f("The pieces",0.4),yards=_f("The pieces",2.0),fifty=_f("The pieces",3.0),
inches=_f("Most were",0.9),bigger=_f("Most were",2.1),
nyt=_f("The New York",0.4),sciam=_f("The New York",1.5),covered=_f("The New York",2.3),
tasted=_f("Two local",0.9),mutton=_f("Two local",1.7),venison=_f("Two local",2.3),
scient=_f("Scientists who",0.1),lung=_f("Scientists who",1.9),muscle=_f("Scientists who",2.8),cart=_f("Scientists who",3.2),
nostoc=_f("One early",1.1),jelly=_f("One early",2.0),rain=_f("One early",3.5),norain=_f("One early",4.7),
fav=_f("The favorite",0.3),vultures=_f("The favorite",2.5),midair=_f("The favorite",3.6),
really=_f("Vultures really",0.4),escape=_f("Vultures really",2.3),
lookup=_f("So if it ever",1.5),remember=_f("So if it ever",2.5))
