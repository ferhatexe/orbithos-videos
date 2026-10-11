import json
T=json.load(open("/home/claude/vid38/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
y1978=("In 1978","1978"),head=("In 1978","head inside"),acc=("In 1978","particle accelerator"),
protons=("A beam of protons","protons"),light=("A beam of protons","speed of light"),skull=("A beam of protons","skull"),
flash=("He saw a flash","flash"),suns=("He saw a flash","thousand suns"),nopain=("He saw a flash","no pain"),
expected=("Doctors expected","expected"),didnt=("Doctors expected","He didn't"),
name=("His name was","Anatoli"),age=("His name was","thirty-six"),inst=("His name was","Institute"),prot=("His name was","Protvino"),moscow=("His name was","Moscow"),
u70=("It was home","U-70"),ring=("It was home","ring"),km=("It was home","one and a half"),push=("It was home","pushes protons"),
july=("On July 13th","July 13th"),equip=("On July 13th","equipment"),leaned=("On July 13th","leaned"),
safety=("Several safety","safety systems"),failed=("Several safety","failed"),running=("Several safety","still running"),
path=("And his head was","path"),
entered=("The beam entered","entered"),back=("The beam entered","back of his head"),nose=("The beam entered","nose"),
five=("Five grays","Five grays"),kill=("Five grays","kill"),two=("Five grays","two thousand"),three=("Five grays","three thousand"),
yet=("And yet, he finished","finished his work"),doctor=("And yet, he finished","doctor"),
swollen=("By then","swollen"),peeled=("Over the next days","peeled"),burned=("Over the next days","burned a line"),bone=("Over the next days","bone"),
obs=("Doctors kept him","observation"),die=("Doctors kept him","die"),
butnot=("But he didn't die","didn't die"),
nobody=("Nobody can say","Nobody"),narrow=("Nobody can say","extremely narrow"),thin=("Nobody can say","thin line"),
price=("He did pay","price"),ear=("He did pay","hearing"),face=("He did pay","left side of his face"),paral=("He did pay","paralyzed"),
seiz=("He began to have","seizures"),tired=("He began to have","tired"),
smooth=("Over the years, the paralyzed","stayed smooth"),aged=("Over the years, the paralyzed","aged normally"),
mind=("But his mind","mind"),intact=("But his mind","intact"),
back2=("About a year","back at work"),phd=("About a year","PhD"),s77=("About a year","seventy-seven"),
only=("He is the only","only person"),lightb=("He saw a light","brighter"),lived=("He saw a light","he lived"))
EV={k:wt(*v) for k,v in _E.items()}
