import json
T=json.load(open("/home/claude/vid47/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
y1816=("In 1816","1816"),snow=("In 1816","snowed"),june=("In 1816","June"),frank=("In 1816","Frankenstein"),
how=("How did","How"),volcano=("How did","volcano"),world=("How did","other side"),monster=("How did","monster"),
april=("April 1815","April"),tambora=("April 1815","Tambora"),indonesia=("April 1815","Indonesia"),explodes=("April 1815","explodes"),
largest=("It's the largest","largest"),recorded=("It's the largest","recorded"),tens=("It's the largest","Tens"),
ash=("Its ash","ash"),circles=("Its ash","circles"),dims=("Its ash","dims"),
nextyear=("The next year","next year"),snows=("The next year","snows"),england=("The next year","New England"),june2=("The next year","June"),
frost=("Frost kills","Frost"),crops=("Frost kills","crops"),europe=("Frost kills","Europe"),froze=("Frost kills","eighteen hundred"),
sunsets=("Sunsets glow","Sunsets"),red=("Sunsets glow","fiery red"),
swiss=("In Switzerland","Switzerland"),storms=("In Switzerland","storms"),writers=("In Switzerland","young writers"),villa=("In Switzerland","villa"),
byron=("Lord Byron","Lord Byron"),challenge=("Lord Byron","challenges"),ghost=("Lord Byron","ghost story"),
mary=("Eighteen-year-old","Mary Shelley"),dreams=("Eighteen-year-old","dreams"),scientist=("Eighteen-year-old","scientist"),builds=("Eighteen-year-old","builds a man"),
contest=("The same contest","contest"),vampire=("The same contest","vampire"),
avol=("A volcano helped","volcano"),create=("A volcano helped","create"),themonster=("A volcano helped","monster"),because=("A volcano helped","Because"))
EV={k:wt(*v) for k,v in _E.items()}
_f=lambda sub,o: Lx(sub)[0]+o
EV.update(snow=_f("In 1816",1.3),june=_f("In 1816",1.95),frank=_f("In 1816",3.3),tens=_f("It's the largest",2.55),europe=_f("Frost kills",1.4),froze=_f("Frost kills",3.2),because=_f("A volcano helped",2.06))
