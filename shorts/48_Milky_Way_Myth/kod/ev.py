import json
T=json.load(open("/home/claude/vid48/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
every=("Every galaxy","Every"),galaxy=("Every galaxy","galaxy"),universe=("Every galaxy","universe"),spilled=("Every galaxy","spilled milk"),
goddess=("The milk of","angry goddess"),how=("The milk of","How"),sky=("The milk of","sky"),
zeus=("Zeus, king","Zeus"),king=("Zeus, king","king"),mortal=("Zeus, king","mortal woman"),heracles=("Zeus, king","Heracles"),
ironic=("Ironically","Ironically"),glory=("Ironically","glory"),
immortal=("Zeus wanted","immortal"),divine=("Zeus wanted","divine milk"),
placed=("So the baby","placed"),hera=("So the baby","Hera"),wife=("So the baby","wife"),slept=("So the baby","slept"),
woke=("Hera woke","woke"),notchild=("Hera woke","not her child"),
pushed=("She pushed","pushed"),milk=("She pushed","milk"),sprayed=("She pushed","sprayed"),
drops=("The drops","drops"),stars=("The drops","stars"),river=("The drops","glowing river"),
centuries=("Centuries","Centuries"),tintoretto=("Centuries","Tintoretto"),rubens=("Centuries","Rubens"),
greeks=("The Greeks","Greeks"),kyklos=("The Greeks","galaxias"),milky=("The Greeks","milky circle"),
romans=("The Romans","Romans"),lactea=("The Romans","Via Lactea"),mw=("The Romans","Milky Way"),
astro=("And when","astronomers"),other=("And when","other star"),galaxies=("And when","galaxies"),
billions=("Billions","Billions"),means=("Billions","means"))
EV={k:wt(*v) for k,v in _E.items()}
_f=lambda sub,o: Lx(sub)[0]+o
EV.update(how=_f("The milk of",1.73),milky=_f("The Greeks",2.29),glory=_f("Ironically",1.72),heracles=_f("Zeus, king",3.24),divine=_f("Zeus wanted",2.6),river=_f("The drops",1.48),mw=_f("The Romans",1.91))
