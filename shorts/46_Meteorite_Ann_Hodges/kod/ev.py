import json
T=json.load(open("/home/claude/vid46/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
rock=("A rock from","rock"),space=("A rock from","space"),roof=("A rock from","roof"),hit=("A rock from","hit"),couch0=("A rock from","couch"),
survived=("She survived","survived"),strangest=("She survived","strangest"),
nov=("November","November"),y1954=("November","1954"),syl=("November","Sylacauga"),ann=("November","Ann Hodges"),napping=("November","napping"),
across=("Across","Across"),fireball=("Across","fireball"),boom=("Across","boom"),
stone=("An eight","eight"),ceiling=("An eight","ceiling"),radio=("An eight","radio"),hip=("An eight","hip"),
wakes=("She wakes","wakes"),bruise=("She wakes","huge bruise"),floor=("She wakes","meteorite"),
officials=("Officials","Officials"),airforce=("Officials","Air Force"),
comes=("When it comes","comes back"),landlady=("When it comes","landlady"),sues=("When it comes","sues"),landowner=("When it comes","landowner"),
public=("The public","public"),keeps=("The public","keeps"),
farmer=("A farmer","farmer"),second=("A farmer","second piece"),road=("A farmer","road"),sold=("A farmer","sold"),farm=("A farmer","a farm"),car=("A farmer","a car"),
nobuyer=("Ann found","no buyer"),doorstop=("Ann found","doorstop"),museum=("Ann found","museum"),
allb=("All because","All because"),quiet=("All because","quiet afternoon"),y1954b=("All because","1954"))
EV={k:wt(*v) for k,v in _E.items()}
_f=lambda sub,o: Lx(sub)[0]+o
EV.update(y1954=_f("November",1.15),syl=_f("November",2.3),ann=_f("November",3.7),napping=_f("November",4.5),fireball=_f("Across",1.5),boom=_f("Across",2.55),
ceiling=_f("An eight",2.4),radio=_f("An eight",3.55),hip=_f("An eight",5.0),airforce=_f("Officials",1.75),doorstop=_f("Ann found",2.15),museum=_f("Ann found",3.1))
