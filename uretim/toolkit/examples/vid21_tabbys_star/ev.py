import json, math
T=json.load(open("/home/claude/vid21/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
 flicker=wt("This star","flickering"), dropped=wt("Its light","dropped"), pct=wt("Its light","twenty-two percent"), days=wt("Its light","In a matter"),
 planet=wt("A planet can't","planet"), giant=wt("A planet can't","giant"),
 kepler=wt("It began with","Kepler"), four=wt("It began with","four years"), stars150=wt("It began with","hundred and fifty thousand"), dips=wt("It began with","tiny dips"),
 passes=wt("That's how planets","passes in front"), dims=wt("That's how planets","dims"), jupiter=wt("A giant like","Jupiter"), onepct=wt("A giant like","one percent"),
 volunteers=wt("But computers","volunteers"), ph=wt("But computers","Planet Hunters"), flagged=wt("And they flagged","flagged"),
 kic=wt("It's called KIC","KIC"), tabby=wt("Nicknamed","Tabby's Star"), boy=wt("Nicknamed","Tabetha"), wtf=wt("Nicknamed","WTF"), flux=wt("Nicknamed","Where's the flux"),
 ly=wt("It sits about","fourteen hundred"), cyg=wt("It sits about","Cygnus"), nopat=wt("And its dips","no pattern"), daysb=wt("And its dips","Some lasted days"), weeks=wt("And its dips","weeks"),
 comets=wt("Astronomers wondered","comets"), torn=wt("Astronomers wondered","torn apart"), dust=wt("Astronomers wondered","dust"),
 wright=wt("Then one astronomer","Jason Wright"), wilder=wt("Then one astronomer","wilder"), structure=wt("A giant structure","giant structure"), alien=wt("A giant structure","alien civilization"),
 collect=wt("A giant structure","collect"), headlines=wt("Headlines","Headlines"), longshot=wt("Wright himself","long shot"), testing=wt("Wright himself","testing"),
 unusual=wt("So Boyajian","unusual"), y2016=wt("So Boyajian","twenty sixteen"), help=wt("So Boyajian","help"),
 people=wt("Around seventeen","seventeen hundred"), dollars=wt("Around seventeen","hundred thousand dollars"), telescope=wt("Around seventeen","telescope time"), night=wt("Around seventeen","night after night"),
 simple=wt("The plan was","simple"), solid=wt("The plan was","solid object"), equally=wt("The plan was","equally"), grains=wt("But tiny dust","dust grains"), blue=wt("But tiny dust","blue light"), red=wt("But tiny dust","than red"),
 y2017=wt("In twenty seventeen","twenty seventeen"), dipped=wt("In twenty seventeen","dipped again"), watching=wt("In twenty seventeen","watching"),
 deeper=wt("The dips were","deeper"), blue2=wt("The dips were","blue light"), itdust=wt("It was dust","dust"), notsolid=wt("It was dust","Not a solid"), notalien=wt("It was dust","Not an alien"),
 notover=wt("But the mystery","isn't over"), where=wt("But the mystery","Where does"), shattered=wt("But the mystery","shattered planet"), storm=wt("But the mystery","storm of comets"),
 photos=wt("And old photographs","photographs"), fading=wt("And old photographs","slowly fading"), nobody=wt("And old photographs","Nobody knows"),
 message=wt("We looked at","is this a message"), checked=wt("We checked","checked"), wasnt=wt("We checked","It wasn't"), nextstar=wt("We checked","next strange star"),
)
# shared brightness model for the hook (renderer + sonified audio use the same curve)
_rng=__import__("numpy").random.default_rng(5); _N=__import__("numpy").random.default_rng(6).normal(0,1,4000)
def hook_b(t):
    b=1.0
    a=min(1.0,max(0.0,(t-EV["flicker"]+0.6)/1.2)); b+=0.012*math.sin(t*23)*math.sin(t*7.3)*a*(1 if t<EV["dropped"]-0.2 else 0.3)
    e=t-EV["dropped"]
    if e>0: b-=0.22*min(1.0,e/0.9)*(1 if e<1.9 else max(0.0,1-(e-1.9)/1.6))
    p=t-EV["planet"]
    if 0<p<3.2: b-=0.010*math.sin(math.pi*p/3.2)
    return b
