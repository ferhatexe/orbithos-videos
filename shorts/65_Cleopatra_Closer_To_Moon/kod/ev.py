import json
T=json.load(open("/home/claude/vid65/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(cleo0=_f("Cleopatra lived",0.2),closer=_f("Cleopatra lived",1.2),moon0=_f("Cleopatra lived",2.1),building=_f("Cleopatra lived",3.1),pyr0=_f("Cleopatra lived",3.9),
giza=_f("The Great Pyramid",1.0),y2560=_f("The Great Pyramid",2.75),
born=_f("Cleopatra was born",0.6),later=_f("Cleopatra was born",2.5),
death=_f("And about two",1.5),armstrong=_f("And about two",2.0),moon=_f("And about two",3.1),
toher=_f("To her",0.1),ancient=_f("To her",1.6),
stranger=_f("It gets stranger",0.5),built=_f("It gets stranger",1.5),mammoths=_f("It gets stranger",2.2),alive=_f("It gets stranger",3.3),
herd=_f("A last small",0.5),wrangel=_f("A last small",1.3),arctic=_f("A last small",2.5),y4000=_f("A last small",3.9),
oxford=_f("And Oxford",0.4),teaching=_f("And Oxford",1.5),centuries=_f("And Oxford",2.5),aztecs=_f("And Oxford",3.9),tenoch=_f("And Oxford",4.9),
neat=_f("History isn't",0.3),overlaps=_f("History isn't",1.7),
chapters=_f("Things we file",1.1),side=_f("Things we file",2.3),
egypt=_f("So the next",1.5),remember=_f("So the next",3.0))
