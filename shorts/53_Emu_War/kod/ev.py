import json
T=json.load(open("/home/claude/vid53/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(war=_f("Australia went",0.9),birds=_f("Australia went",1.6),lost=_f("Australia went",2.2),
meta=_f("Not a metaphor",0.1),soldiers=_f("Not a metaphor",1.04),mguns=_f("Not a metaphor",1.89),emus0=_f("Not a metaphor",2.89),
wa=_f("Western Australia",0.1),y1932=_f("Western Australia",1.2),twenty=_f("Western Australia",2.4),emus=_f("Western Australia",3.2),wheat=_f("Western Australia",4.2),
farmers=_f("Many farmers",0.3),veterans=_f("Many farmers",1.2),help=_f("Many farmers",3.0),
major=_f("The army sends",0.8),two=_f("The army sends",1.3),guns=_f("The army sends",2.2),bullets=_f("The army sends",3.3),
scatter=_f("But the emus",0.8),groups=_f("But the emus",1.4),jams=_f("But the emus",3.0),
truck=_f("They mount",0.9),outrun=_f("They mount",2.0),
sprint=_f("An emu can",0.5),kmh=_f("An emu can",1.8),
said=_f("The major said",0.5),face=_f("The major said",1.4),tanks=_f("The major said",3.6),
rounds=_f("Nearly ten",0.8),pulled=_f("Nearly ten",1.9),
again=_f("Farmers asked",1.3),three=_f("Farmers asked",1.8),no=_f("Farmers asked",3.2),
won=_f("The emus won",0.5),because=_f("The emus won",1.1))
