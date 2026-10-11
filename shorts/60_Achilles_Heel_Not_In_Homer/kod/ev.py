import json
T=json.load(open("/home/claude/vid60/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(heel0=_f("Achilles' heel is",0.5),famous=_f("Achilles' heel is",1.4),homer=_f("Achilles' heel is",3.2),never=_f("Achilles' heel is",3.6),
iliad=_f("In the Iliad",0.3),invul=_f("In the Iliad",1.5),spear=_f("In the Iliad",2.7),graze=_f("In the Iliad",3.6),blood=_f("In the Iliad",4.6),
ends=_f("And the poem",0.8),dies=_f("And the poem",1.4),paris=_f("And the poem",2.5),arrow=_f("And the poem",3.6),
centuries=_f("The heel story",1.2),roman=_f("The heel story",2.2),statius=_f("The heel story",3.3),firstc=_f("The heel story",4.2),
thetis=_f("His mother",0.7),dipped=_f("His mother",1.5),styx=_f("His mother",2.8),invul2=_f("His mother",3.4),
held=_f("But she held",0.5),heel=_f("But she held",1.1),dry=_f("But she held",2.3),
later=_f("In later",0.3),arrow2=_f("In later",1.4),there=_f("In later",2.5),
older=_f("An older",0.4),burning=_f("An older",1.5),fire=_f("An older",2.6),
tendon=_f("The tendon",0.3),y1693=_f("The tendon",1.3),flemish=_f("The tendon",2.3),
word=_f("And Achilles' heel as",1.1),weak=_f("And Achilles' heel as",1.6),caught=_f("And Achilles' heel as",2.4),c1800=_f("And Achilles' heel as",3.1),
points=_f("So when someone",0.9),yourheel=_f("So when someone",1.5),remember=_f("So when someone",1.9))
