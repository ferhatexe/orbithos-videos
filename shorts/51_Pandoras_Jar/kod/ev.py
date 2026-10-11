import json
T=json.load(open("/home/claude/vid51/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(pandora=_f("Pandora never",0.0),nbox=_f("Pandora never",1.2),
famous=_f("The most famous",0.6),never=_f("The most famous",1.9),what=_f("The most famous",3.1),
greek=_f("In Greek myth",0.2),zeus=_f("In Greek myth",1.0),first=_f("In Greek myth",2.4),pname=_f("In Greek myth",2.9),
gift=_f("Each god",1.0),sealed=_f("Each god",2.4),
sick=_f("Inside were",0.8),toil=_f("Inside were",1.2),evil=_f("Inside were",1.9),
lid=_f("She lifted",0.5),escaped=_f("She lifted",1.1),excep=_f("She lifted",2.2),hope=_f("She lifted",3.13),
hesiod=_f("But the poet",1.0),box2=_f("But the poet",2.0),pithos=_f("But the poet",2.7),
jar=_f("A huge clay",0.5),tall=_f("A huge clay",1.5),wine=_f("A huge clay",2.9),
diog=_f("The philosopher",0.9),lived=_f("The philosopher",2.2),
y1508=_f("Then, in 1508",0.75),erasmus=_f("Then, in 1508",2.0),latin=_f("Then, in 1508",3.6),pyxis=_f("Then, in 1508",4.5),abox=_f("Then, in 1508",5.1),
stuck=_f("The mistake",0.4),five=_f("The mistake",1.2),painting=_f("The mistake",2.1),phrase=_f("The mistake",3.0),
nexttime=_f("So next time",0.3),dont=_f("So next time",1.6),remember=_f("So next time",2.0))
