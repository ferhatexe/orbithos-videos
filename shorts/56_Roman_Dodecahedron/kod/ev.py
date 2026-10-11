import json
T=json.load(open("/home/claude/vid56/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(bronze=_f("This bronze",0.3),twelve=_f("This bronze",1.1),hole=_f("This bronze",1.65),nobody=_f("This bronze",3.1),
call=_f("Archaeologists call",0.1),roman=_f("Archaeologists call",1.0),
hundred=_f("About a hundred",0.3),england=_f("About a hundred",2.3),hungary=_f("About a hundred",3.1),second=_f("About a hundred",4.4),fourth=_f("About a hundred",5.2),
every=_f("Every one is",0.1),holes=_f("Every one is",1.65),sizes=_f("Every one is",2.7),corner=_f("Every one is",3.7),knob=_f("Every one is",4.6),
graves=_f("Some were buried",0.6),hoards=_f("Some were buried",2.2),treasure=_f("Some were buried",3.0),
text=_f("But no surviving",0.9),picture=_f("But no surviving",1.6),mentions=_f("But no surviving",2.4),
pile=_f("So the guesses",0.2),candle=_f("So the guesses",1.25),die=_f("So the guesses",2.2),tool=_f("So the guesses",3.2),charm=_f("So the guesses",4.15),
y2023=_f("In 2023",0.1),diggers=_f("In 2023",1.2),norton=_f("In 2023",3.3),found=_f("In 2023",4.3),intact=_f("In 2023",5.3),
solve=_f("It didn't",0.3),deep=_f("It didn't",1.4),
eighteen=_f("Eighteen",0.1),know=_f("Eighteen",1.5),this=_f("Eighteen",2.1))
