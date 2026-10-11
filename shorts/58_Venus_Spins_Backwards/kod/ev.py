import json
T=json.load(open("/home/claude/vid58/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(venus=_f("On Venus",0.1),rises=_f("On Venus",1.0),west=_f("On Venus",1.6),months=_f("On Venus",2.5),set=_f("On Venus",3.2),
back=_f("Venus spins",0.8),slow=_f("Venus spins",1.7),
turn=_f("One full turn",0.4),d243=_f("One full turn",1.0),days=_f("One full turn",2.4),
trip=_f("But one trip",0.6),sunorb=_f("But one trip",1.3),d225=_f("But one trip",1.9),
spin=_f("So a single",0.5),longer=_f("So a single",1.0),year=_f("So a single",2.1),
twist=_f("Now the twist",0.5),backorb=_f("Now the twist",1.8),orbits=_f("Now the twist",2.5),sunrise=_f("Now the twist",3.3),d117=_f("Now the twist",4.6),
almost=_f("So Venus still",0.9),two=_f("So Venus still",1.4),
clouds=_f("Meanwhile",0.9),race=_f("Meanwhile",1.3),four=_f("Meanwhile",2.6),
beneath=_f("And beneath",0.5),ground=_f("And beneath",1.2),d460=_f("And beneath",2.0),lead=_f("And beneath",4.5),
why=_f("Why does it",0.1),nobody=_f("Why does it",1.6),impact=_f("Why does it",2.9),tides=_f("Why does it",3.9),flip=_f("Why does it",5.2),
sunset=_f("So if you're",1.5),patient=_f("So if you're",2.2))
