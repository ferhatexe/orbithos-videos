import json
T=json.load(open("/home/claude/vid44/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
wave=("A wave of","wave"),molasses=("A wave of","molasses"),boston=("A wave of","Boston"),killed=("A wave of","killed"),n21=("A wave of","twenty-one"),
how=("How can","How"),syrup=("How can","syrup"),kill=("How can","kill"),
jan=("January","January"),tank=("January","giant tank"),gallons=("January","2.3 million"),mol2=("January","molasses"),
meant=("It was meant","meant"),alcohol=("It was meant","alcohol"),explosives=("It was meant","explosives"),
warm=("It's oddly","oddly warm"),sound=("It's oddly","sound"),gun=("It's oddly","machine-gun"),rivets=("It's oddly","rivets"),popping=("It's oddly","popping"),
burst=("And the whole","bursts"),
brown=("A brown wave","brown wave"),ft25=("A brown wave","25 feet"),rushes=("A brown wave","rushes"),mph=("A brown wave","35 miles"),
crush=("It crushes","crushes"),buildings=("It crushes","buildings"),bends=("It crushes","bends"),railway=("It crushes","steel railway"),
real=("But the real","real killer"),next=("But the real","came next"),
cooled=("The molasses cooled","cooled"),winter=("The molasses cooled","winter air"),thick=("The molasses cooled","thickened"),glue=("The molasses cooled","glue"),
half=("About half","About half"),died=("About half","died"),stuck=("About half","stuck"),cleanup=("About half","cleanup"),weeks=("About half","weeks"),
company=("The company","company"),anarch=("The company","anarchists"),court=("The company","court"),weak=("The company","too weak"),
locals=("Locals said","Locals"),harbor=("Locals said","harbor"),sweet=("Locals said","smelled sweet"),decades=("Locals said","decades"),allb=("Locals said","All because"),warmday=("Locals said","warm day"),y1919=("Locals said","1919"))
EV={k:wt(*v) for k,v in _E.items()}
_s=Lx("It's oddly")[0]
for k,v in dict(sound=1.6,gun=2.1,rivets=3.45,popping=3.8).items(): EV[k]=_s+v
EV["gallons"]=Lx("January")[0]+2.04
