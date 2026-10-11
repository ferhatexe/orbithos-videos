import json
T=json.load(open("/home/claude/vid59/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(holding=_f("This man",0.6),rod=_f("This man",1.1),head=_f("This man",2.8),lived=_f("This man",3.5),twelve=_f("This man",4.2),
y1848=_f("In 1848",0.1),gage=_f("In 1848",1.5),railroad=_f("In 1848",2.1),vermont=_f("In 1848",3.2),blasting=_f("In 1848",3.8),
tamping=_f("He was tamping",0.4),powder=_f("He was tamping",0.9),hole=_f("He was tamping",1.4),spark=_f("He was tamping",2.2),off=_f("He was tamping",2.7),
blast=_f("The blast",0.1),upward=_f("The blast",1.0),bullet=_f("The blast",1.7),
six=_f("The six-kilo",0.2),cheek=_f("The six-kilo",1.4),eye=_f("The six-kilo",2.4),flew=_f("The six-kilo",3.0),top=_f("The six-kilo",3.9),skull=_f("The six-kilo",4.7),
landed=_f("It landed",0.15),meters=_f("It landed",0.7),
minutes=_f("Minutes later",0.1),sitting=_f("Minutes later",0.9),cart=_f("Minutes later",1.4),talking=_f("Minutes later",2.1),
survived=_f("He survived",0.2),doctor=_f("He survived",0.9),friends=_f("He survived",1.8),nolonger=_f("He survived",2.5),
stage=_f("Yet he later",1.0),chile=_f("Yet he later",2.2),hint=_f("Yet he later",3.5),legend=_f("Yet he later",4.7),
hskull=_f("His skull",0.3),hiron=_f("His skull",0.9),harvard=_f("His skull",1.9),
century=_f("For a century",0.4),photo=_f("For a century",1.4),y2009=_f("For a century",3.0),turned=_f("For a century",3.9),init=_f("For a century",4.7))
