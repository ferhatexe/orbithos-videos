import json
T=json.load(open("/home/claude/vid36/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
fell=("On Christmas","fell"),twomiles=("On Christmas","two miles"),sky=("On Christmas","sky"),landed=("She landed","landed"),amazon=("She landed","Amazon"),alone=("She landed","Alone"),buckled=("She landed","buckled"),eleven=("And eleven","eleven"),alive=("And eleven","alive"),
name=("Her name","Juliane"),grad=("Her name","graduated"),lima=("Her name","Lima"),parents=("Her parents","biologists"),station=("Her parents","research station"),flying=("Now she","flying"),andes=("Now she","Andes"),christmas=("Now she","Christmas"),flight=("LANSA","LANSA"),n92=("LANSA","Ninety-two"),
mins=("About twenty","twenty-five"),wall=("About twenty","wall"),shook=("The cabin","shook"),bags=("The cabin","Bags"),presents=("The cabin","presents"),tumbled=("The cabin","tumbled"),window=("Outside","window"),flash=("Outside","lightning"),again=("Outside","again"),mother=("Her mother said","mother"),theend=("Her mother said","That's the end"),allover=("Her mother said","It's all over"),struck=("Then lightning","struck"),wing=("Then lightning","wing"),broke=("Then lightning","broke apart"),
thrown=("Juliane was thrown","thrown"),row=("Juliane was thrown","row of three"),m3000=("She was about","three thousand"),ft=("She was about","Ten thousand"),forest=("She remembers","forest"),spinning=("She remembers","spinning"),black=("Then, everything","black"),
woke=("She woke","woke"),floor=("She woke","forest floor"),collar=("A broken","collarbone"),cuts=("A broken","Deep cuts"),conc=("A broken","concussion"),eye=("A broken","One eye"),glasses=("A broken","glasses"),shoe=("A broken","one shoe"),nobody=("Nobody knows","Nobody"),spinseats=("Nobody knows","spinning seats"),trees=("Nobody knows","thick trees"),called=("She called","called"),mom=("She called","mother"),noans=("She called","Nobody answered"),
knew=("But Juliane knew","knew"),father=("But Juliane knew","father"),lost=("If you are lost","lost"),water=("If you are lost","find water"),downhill=("If you are lost","Follow a stream"),rivers=("If you are lost","Streams lead"),people=("If you are lost","rivers lead to people"),creek=("So she found","creek"),walk=("So she found","walk"),
sweets=("Her only food","sweets"),day4=("On the fourth","fourth day"),seats=("On the fourth","row of seats"),notsurv=("On the fourth","had not survived"),notamong=("On the fourth","Her mother was not"),cut=("And the cut","cut on her arm"),worse=("And the cut","worse"),flies=("And the cut","Flies"),
dayafter=("Day after day","Day after"),creekb=("Day after day","The creek"),stream=("Day after day","became a stream"),riverw=("Day after day","became a river"),day10=("On the tenth","tenth day"),current=("On the tenth","current"),saw=("Then she saw","saw"),boat=("Then she saw","A boat"),path=("Then she saw","A path"),shelter=("Then she saw","small shelter"),
gas=("Inside, she found","gasoline"),remem=("Inside, she found","remembered"),dog=("Inside, she found","dog"),poured=("She poured","poured"),thirty=("She poured","thirty"),onebyone=("She poured","one by one"),lay=("Then she lay","lay down"),waited=("Then she lay","waited"),
voices=("The next day","voices"),workers=("The next day","Local workers"),fright=("At first","frightened"),spirit=("At first","water spirit"),cleaned=("They cleaned","cleaned"),byboat=("They cleaned","by boat"),doctor=("They cleaned","doctor"),of92=("Of the ninety","ninety-two"),only=("Of the ninety","only survivor"),mother2=("Of the ninety","Her mother had died"),
biology=("Juliane went","biology"),parents2=("Juliane went","parents"),leads=("Today, she","leads"),pang=("Today, she","Panguana"),protect=("Today, she","protecting"),saved=("Today, she","saved her"),
fellb=("She fell two","fell"),simple=("She fell two","one simple thing"),follow=("Follow the water","Follow"))
EV={k:wt(*v) for k,v in _E.items()}
