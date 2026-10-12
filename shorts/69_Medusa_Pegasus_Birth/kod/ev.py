import json
T=json.load(open("/home/claude/vid69/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(peg0=_f("Pegasus, the winged",0.1),born=_f("Pegasus, the winged",1.5),neck0=_f("Pegasus, the winged",2.4),
hesiod=_f("In Hesiod",0.3),three=_f("In Hesiod",1.8),onlydie=_f("In Hesiod",3.3),
sisters=_f("Her sisters",0.2),stheno=_f("Her sisters",0.8),eury=_f("Her sisters",1.3),immortal=_f("Her sisters",2.1),
perseus=_f("Perseus cut",0.1),slept=_f("Perseus cut",1.5),reflect=_f("Perseus cut",2.9),
hermes=_f("Hermes gave",0.1),blade=_f("Hermes gave",0.8),athena1=_f("Hermes gave",1.8),
sprang=_f("From her severed",0.6),poseidon=_f("From her severed",2.2),pegasus=_f("From her severed",3.3),chrysaor=_f("From her severed",4.4),
thunder=_f("Pegasus later",1.1),zeus=_f("Pegasus later",2.3),
dead=_f("Even dead",0.4),gaze=_f("Even dead",0.9),weapon=_f("Even dead",3.0),
ovid1=_f("In Ovid, he set",0.2),seaweed=_f("In Ovid, he set",1.3),coral=_f("In Ovid, he set",3.1),
athena2=_f("Later, Athena",0.6),shield=_f("Later, Athena",1.5),
greeks=_f("Greeks painted",0.1),evil=_f("Greeks painted",2.6),
ovid2=_f("Ovid also",0.2),beautiful=_f("Ovid also",1.5),cursed=_f("Ovid also",2.3),
picture=_f("So the next",1.2),remember=_f("So the next",1.8))
