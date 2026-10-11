import json
T=json.load(open("/home/claude/vid37/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
dec1=("December first","December first"),dead=("December first","found dead"),beachw=("December first","beach"),
wallet=("No wallet","No wallet"),noname=("No wallet","No name"),labels=("No wallet","label cut"),
secret=("And hidden","secret pocket"),twowords=("And hidden","two words"),tamam=("And hidden","Tamam"),
y74=("It would take","seventy-four"),who=("It would take","who he was"),
somerton=("Somerton Beach","Somerton"),dawn=("Somerton Beach","Just after dawn"),swim=("Somerton Beach","back from a swim"),slumped=("Somerton Beach","slumped"),
suit=("A neat suit","neat suit"),shoes=("A neat suit","Brand new"),legs=("A neat suit","Legs"),crossed=("A neat suit","feet crossed"),cig=("A neat suit","cigarette"),
cold=("He's cold","cold"),noviol=("He's cold","no signs"),
evening=("The evening before","evening before"),raised=("The evening before","raised his arm"),drop=("The evening before","let it drop"),asleep=("The evening before","asleep"),
train=("In his pockets","train ticket"),bus=("In his pockets","bus ticket"),gum=("In his pockets","chewing gum"),matches=("In his pockets","matches"),combs=("In his pockets","two combs"),pack=("In his pockets","pack of cigarettes"),brand=("In his pockets","different brand"),
nomoney=("No money","No money"),noid=("No money","No ID"),cut=("No money","carefully cut"),
spleen=("The autopsy","spleen"),three=("The autopsy","three times"),liver=("The autopsy","liver"),
poison=("It looked like","poison"),clean=("It looked like","came back clean"),
expert=("One expert","expert"),rare=("One expert","rare poison"),court=("One expert","In court"),wrote=("One expert","wrote it down"),
suitcase=("Weeks later","brown suitcase"),station=("Weeks later","railway station"),daybefore=("Weeks later","the day before"),
again=("Again, the labels","labels were gone"),thread=("Again, the labels","orange thread"),mend=("Again, the labels","mend his pocket"),
items=("Only three items","three items"),keane=("Only three items","Keane."),nokeane=("Only three items","no missing"),
april=("Then, in April","April"),pathologist=("Then, in April","pathologist"),tiny=("Then, in April","tiny pocket"),waist=("Then, in April","waistband"),
rolled=("Inside was a tightly","rolled scrap"),twowords2=("Inside was a tightly","two words"),tamam2=("Inside was a tightly","Tamam"),
persian=("It's Persian","Persian"),finished=("It's Persian","it is finished"),final=("It's Persian","final words"),rubaiyat=("It's Persian","Rubaiyat"),
july=("In July","July"),copy=("In July","copy of that book"),car=("In July","car"),
matched=("The torn piece","matched"),phone=("The torn piece","phone number"),five=("The torn piece","five faint lines"),
naval=("Naval intelligence","Naval"),amateurs=("Naval intelligence","Amateurs"),nobody=("Nobody has ever","Nobody"),cracked=("Nobody has ever","cracked"),
nurse=("The phone number led","young nurse"),castf=("The phone number led","cast of the dead"),shaken=("The phone number led","shaken"),didnt=("The phone number led","didn't know him"),
buried=("He was buried","buried"),theories=("He was buried","theories"),spy=("He was buried","A spy"),suicide=("He was buried","A suicide"),lover=("He was buried","heartbroken lover"),
y2021=("Then, in 2021","2021"),exhumed=("Then, in 2021","exhumed"),
abbott=("Professor Derek","Derek Abbott"),fitz=("Professor Derek","Colleen"),dnaw=("Professor Derek","DNA"),hairs=("Professor Derek","hairs"),plaster=("Professor Derek","plaster cast"),
tree=("They built","family tree"),k4=("They built","four thousand"),y2022=("They built","July 2022"),announced=("They built","announced a name"),
webb=("Carl Webb","Carl Webb"),engineer=("Carl Webb","electrical engineer"),melb=("Carl Webb","Melbourne"),b1905=("Carl Webb","born"),
notconf=("Police have not","not officially"),how=("Police have not","how he died"),codew=("Police have not","what the code"),
noname2=("A man with no name","no name"),secret2=("A man with no name","secret pocket"),poetry=("A man with no name","Two words"),
tamam3=("Tamam Shud. It is","Tamam"),finished3=("Tamam Shud. It is","It is finished"),mystery=("Tamam Shud. It is","But the mystery"))
EV={k:wt(*v) for k,v in _E.items()}
