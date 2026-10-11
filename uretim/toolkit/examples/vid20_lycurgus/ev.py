import json
T=json.load(open("/home/claude/vid20/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
def wt(line_sub,word):
    for ln in LINES:
        if line_sub in ln["en"]:
            i=ln["en"].index(word); return ln["s"]+(i/len(ln["en"]))*(ln["e"]-ln["s"])
    raise KeyError(line_sub)
EV=dict(
 lighton=0.35, green=wt("This Roman cup","green"), light=wt("Until you shine","light"), through=wt("Until you shine","through"),
 turns=wt("Then it turns","turns"), blood=wt("Then it turns","blood red"), sixteen=wt("It was made about","sixteen hundred"), nobody=wt("It was made about","nobody"),
 name=wt("It's called the Lycurgus","Lycurgus Cup"), rome=wt("It's called","Rome"), museum=wt("It's called","British Museum"),
 myth=wt("Carved around","Greek myth"), lyc=wt("Carved around","King Lycurgus"), dio=wt("Carved around","Dionysus"),
 amb=wt("But the nymph","Ambrosia"), vine=wt("But the nymph","vine"), wraps=wt("But the nymph","wraps"), traps=wt("But the nymph","traps"),
 deep=wt("The figures are cut","so deeply"), floatw=wt("The figures are cut","float"), bridges=wt("The figures are cut","tiny bridges"),
 secret=wt("But the real secret","real secret"), inside=wt("But the real secret","inside the glass"),
 y1990=wt("In nineteen ninety","nineteen ninety"), em=wt("In nineteen ninety","electron microscope"),
 gold=wt("They found particles","gold and silver"), nm=wt("They found particles","fifty to a hundred"),
 thousand=wt("About a thousand","thousand"), hair=wt("About a thousand","human hair"),
 front=wt("Shine light on","front"), scatter=wt("Shine light on","scatter green"), back=wt("Shine light from behind","behind"),
 absorbed=wt("Shine light from behind","absorbed"), red=wt("Shine light from behind","Only red"), nano=wt("Nanotechnology","Nanotechnology"), word=wt("Nanotechnology","a word"),
 q=Lx("Did the Romans")[0], precise=wt("The mix is","precise"), ppm=wt("The mix is","parts per million"), less=wt("The mix is","even less gold"),
 luck=wt("Some researchers","luck"), recipe=wt("Some researchers","guarded recipe"), noone=Lx("No one knows")[0],
 cracked=wt("The cup is cracked","cracked"), rim=wt("The cup is cracked","metal rim"),
 borrow=wt("Today, scientists","borrow"), illinois=wt("At the University","Illinois"), stamp=wt("At the University","stamp-sized"), billion=wt("At the University","a billion"), sprayed=wt("At the University","sprayed"),
 mini=wt("Each dent","miniature"), changes=wt("Each dent","changes color"), liquid=wt("Each dent","liquid"),
 hundred=wt("It could detect","hundred times"), diseases=wt("It could detect","diseases"),
 sixteenc=wt("Sixteen centuries ago","Sixteen centuries"), unknown=wt("Sixteen centuries ago","unknown artisan"), trapped=wt("Sixteen centuries ago","trapped light"), learning=wt("And we are only","learning"),
)
