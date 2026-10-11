import json
T=json.load(open("/home/claude/vid49/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
def wt(line_sub,word):
    for ln in LINES:
        if line_sub in ln["en"]:
            i=ln["en"].index(word); return ln["s"]+(i/len(ln["en"]))*(ln["e"]-ln["s"])
    raise KeyError(line_sub+"|"+word)
_E=dict(
newstar=("A new star","new star"),blazed=("A new star","blazed"),daylight=("A new star","daylight"),
faded=("It faded","faded"),behind=("It faded","left behind"),spinning=("It faded","spinning"),thirty=("It faded","thirty"),
july=("July 4th","July"),y1054=("July 4th","1054"),china=("July 4th","China"),guest=("July 4th","guest star"),taurus=("July 4th","Taurus"),
venus=("It's as bright","Venus"),days23=("It's as bright","twenty-three"),daytime=("It's as bright","daytime"),
night=("At night","night"),twoyears=("At night","two years"),disappears=("At night","disappears"),
southwest=("In the American","Southwest"),painted=("In the American","painted"),rock=("In the American","rock"),
supernova=("It was a supernova","supernova"),giant=("It was a supernova","giant star"),exploding=("It was a supernova","exploding"),life=("It was a supernova","end of its life"),
weeks=("For a few weeks","few weeks"),outshine=("For a few weeks","outshine"),galaxy=("For a few weeks","whole galaxy"),
light=("Its light took","light"),years=("Its light took","six thousand"),earth=("Its light took","Earth"),
today=("Today, telescopes","Today"),wreck=("Today, telescopes","wreckage"),crab=("Today, telescopes","Crab Nebula"),expanding=("Today, telescopes","expanding"),
heart=("At its heart","heart"),neutron=("At its heart","neutron star"),city=("At its heart","city"),
spins=("It spins","spins"),thirty2=("It spins","thirty times"),lighthouse=("It spins","lighthouse"),
first=("We first saw","first saw"),thousand=("We first saw","thousand years"),suddenly=("We first saw","suddenly"))
EV={k:wt(*v) for k,v in _E.items()}
_f=lambda sub,o: Lx(sub)[0]+o
EV.update(spinning=_f("It faded",1.8),thirty=_f("It faded",2.7),china=_f("July 4th",2.6),guest=_f("July 4th",3.7),taurus=_f("July 4th",4.3),
venus=_f("It's as bright",0.9),days23=_f("It's as bright",2.0),daytime=_f("It's as bright",3.0),twoyears=_f("At night",1.5),disappears=_f("At night",2.6),
supernova=_f("It was a supernova",0.6),giant=_f("It was a supernova",1.4),exploding=_f("It was a supernova",2.3))
