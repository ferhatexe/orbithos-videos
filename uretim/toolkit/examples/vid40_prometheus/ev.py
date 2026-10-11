import json
T=json.load(open("/home/claude/vid40/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
eagle=("Every day, an eagle","eagle"),liver=("Every day, an eagle","liver"),night=("Every day, an eagle","Every night"),grew=("Every day, an eagle","grew back"),
punish=("This was the punishment","punishment"),prom=("This was the punishment","Prometheus"),true=("This was the punishment","actually true"),
greek=("In Greek myth","Greek myth"),titan=("In Greek myth","Titan"),name=("In Greek myth","name means"),fore=("In Greek myth","forethought"),
friend=("He was humanity","friend"),zeus=("He was humanity","Zeus hid"),stole=("He was humanity","stole it back"),
spark=("He carried the spark","spark"),gods=("He carried the spark","gods"),fennel=("He carried the spark","fennel"),
withfire=("And with fire","with fire"),cook=("And with fire","cook"),forge=("And with fire","forge"),cold=("And with fire","cold nights"),
furious=("Zeus was furious","furious"),chained=("Zeus was furious","chained"),rock=("Zeus was furious","rock"),
everyday=("And every day, he sent","every day"),eagle2=("And every day, he sent","eagle"),eat=("And every day, he sent","eat his liver"),
immortal=("Prometheus was immortal","immortal"),regrow=("Prometheus was immortal","grew back"),returned=("Prometheus was immortal","returned"),
ages=("It went on for ages","ages"),heracles=("It went on for ages","Heracles"),arrow=("It went on for ages","arrow"),free=("It went on for ages","set him free"),
strange=("Now here is","strange part"),organs=("Now here is","organs"),chose=("Now here is","chose the liver"),
best=("And the liver is","best known"),growing=("And the liver is","growing back"),
surgeons=("Surgeons can","Surgeons"),twothirds=("Surgeons can","two thirds"),months=("Surgeons can","few months"),fullsize=("Surgeons can","full size"),
donor=("That is how","living donor"),part=("That is how","part of their liver"),both=("That is how","Both pieces"),
cells=("Liver cells","Liver cells"),rest=("Liver cells","rest"),divide=("Liver cells","dividing"),stop=("Liver cells","they stop"),
know=("So, did the ancient","know"),
priests=("Maybe. Greek priests","priests"),omens=("Maybe. Greek priests","omens"),doctors=("Maybe. Greek priests","Doctors"),wounds=("Maybe. Greek priests","battle wounds"),heal=("Maybe. Greek priests","livers heal"),
guess=("Or maybe it was","lucky guess"),nobody=("Or maybe it was","Nobody"),
another=("But there is another","another"),under=("But there is another","underworld"),tityus=("But there is another","Tityus"),vultures=("But there is another","vultures"),too=("But there is another","grew back too"),
atitan=("A Titan. A stolen","Titan"),sfire=("A Titan. A stolen","stolen fire"),organ=("A Titan. A stolen","organ"),refuses=("A Titan. A stolen","refuses to die"),
tell=("Maybe the myth","tell us"),along=("Maybe the myth","all along"))
EV={k:wt(*v) for k,v in _E.items()}
