import json
T=json.load(open("/home/claude/vid45/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
greeks=("Ancient Greeks","Greeks"),abor=("Ancient Greeks","Aboriginal"),same=("Ancient Greeks","same story"),stars0=("Ancient Greeks","stars"),
seven=("Seven sisters","Seven"),hunter=("Seven sisters","hunter"),missing=("Seven sisters","missing"),
how=("How could","How"),never=("How could","never met"),samestar=("How could","same star"),
greece=("In Greece","Greece"),pleiades=("In Greece","Pleiades"),daughters=("In Greece","daughters"),atlas=("In Greece","Atlas"),
orion=("The hunter Orion","Orion"),chased=("The hunter Orion","chased"),gods=("The hunter Orion","gods"),madestars=("The hunter Orion","stars"),
merope=("But Merope","Merope"),mortal=("But Merope","mortal"),hid=("But Merope","hid"),shame=("But Merope","shame"),faint=("But Merope","faint"),
aus=("In Australia","Australia"),orion2=("In Australia","Orion"),man=("In Australia","a man"),chasing=("In Australia","chasing"),
again=("And again","again"),hiding=("And again","hiding"),six=("And again","Only six"),
look=("Look tonight","Look"),most=("Look tonight","Most people"),see6=("Look tonight","see six"),
y2021=("In 2021","2021"),astro=("In 2021","astronomers"),backward=("In 2021","backward"),
hundred=("A hundred","hundred thousand"),two=("A hundred","two of them"),atlas2=("A hundred","Atlas and"),apart=("A hundred","further apart"),seven2=("A hundred","see seven"),
hypo=("It's only","hypothesis"),oldest=("It's only","oldest story"),maybe=("It's only","Maybe"))
EV={k:wt(*v) for k,v in _E.items()}
EV["missing"]=Lx("Seven sisters")[0]+2.9; EV["hunter"]=Lx("Seven sisters")[0]+1.5; EV["seven2"]=Lx("A hundred")[0]+4.25; EV["maybe"]=Lx("It's only")[0]+3.41
