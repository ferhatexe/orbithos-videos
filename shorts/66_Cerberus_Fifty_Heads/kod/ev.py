import json
T=json.load(open("/home/claude/vid66/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(cerb=_f("Cerberus, the guard",0.1),under=_f("Cerberus, the guard",1.4),three=_f("Cerberus, the guard",2.2),orig=_f("Cerberus, the guard",3.1),fifty=_f("Cerberus, the guard",3.9),
theog=_f("In Hesiod",0.8),oldest=_f("In Hesiod",1.9),fiftyh=_f("In Hesiod",3.5),bronze=_f("In Hesiod",4.4),
orthrus=_f("His brother",0.7),twoh=_f("His brother",1.5),hydra=_f("His brother",2.9),
pindar=_f("The poet Pindar",0.3),hundred=_f("The poet Pindar",1.5),
artists=_f("Artists settled",0.1),vases=_f("Artists settled",1.5),two=_f("Artists settled",2.2),threex=_f("Artists settled",4.2),
strange=_f("His job",0.8),deadin=_f("His job",2.2),ate=_f("His job",3.1),leave=_f("His job",3.8),
heracles=_f("Heracles dragged",0.1),dragged=_f("Heracles dragged",0.7),labor=_f("Heracles dragged",2.5),
orpheus=_f("Orpheus put",0.1),music=_f("Orpheus put",1.2),
virgil=_f("And in Virgil",0.5),priestess=_f("And in Virgil",1.1),cake=_f("And in Virgil",2.1),
beaten=_f("Beaten three",0.1),strength=_f("Beaten three",1.5),music2=_f("Beaten three",2.0),snack=_f("Beaten three",2.5),
phrase=_f("That's the origin",1.4),sop=_f("That's the origin",2.2),bribe=_f("That's the origin",3.7),quiet=_f("That's the origin",4.5),
picture=_f("So whenever",0.9),remember=_f("So whenever",1.7))
