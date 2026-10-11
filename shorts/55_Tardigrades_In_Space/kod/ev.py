import json
T=json.load(open("/home/claude/vid55/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(animal=_f("One animal",0.3),survived=_f("One animal",0.8),vacuum0=_f("One animal",1.5),naked=_f("One animal",2.4),
suit=_f("No suit",0.2),ship=_f("No suit",0.9),tiny=_f("No suit",1.7),half=_f("No suit",2.6),how=_f("No suit",3.9),
tardi=_f("Meet the",0.6),bear=_f("Meet the",1.7),
legs=_f("Eight stubby",0.5),claws=_f("Eight stubby",1.3),everywhere=_f("Eight stubby",2.2),mountain=_f("Eight stubby",3.4),deepsea=_f("Eight stubby",4.2),
bad=_f("When things",0.5),dries=_f("When things",1.2),curls=_f("When things",2.0),tun=_f("When things",3.0),shuts=_f("When things",4.0),
y2007=_f("In 2007",0.5),orbit=_f("In 2007",3.0),opened=_f("In 2007",3.8),
tendays=_f("Ten days",0.2),vacuum=_f("Ten days",1.0),cosmic=_f("Ten days",1.7),
back=_f("Back on Earth",0.2),water=_f("Back on Earth",1.8),woke=_f("Back on Earth",2.6),eggs=_f("Back on Earth",3.2),
y2019=_f("In 2019",0.3),lander=_f("In 2019",1.2),crashed=_f("In 2019",1.9),thousands=_f("In 2019",3.6),
survive=_f("Did they",0.4),nobody=_f("Did they",1.1),without=_f("Did they",2.3),wake=_f("Did they",3.2),
whyis=_f("Which is why",0.2),farknow=_f("Which is why",0.9))
