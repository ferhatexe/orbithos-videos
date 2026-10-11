import json
T=json.load(open("/home/claude/vid43/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
signal=("A signal","signal"),deep=("A signal","deep space"),hit=("A signal","hit Earth"),s72=("A signal","seventy-two"),vanished=("A signal","vanished"),forever=("A signal","forever"),
who=("So who","who sent"),
aug=("August","August"),bigear=("August","Big Ear"),ohio=("August","Ohio"),scanning=("August","scanning"),
ehman=("Astronomer","Jerry Ehman"),printout=("Astronomer","printout"),finds=("Astronomer","finds this"),
c0=("Six, E","Six"),c1=("Six, E","E,"),c2=("Six, E","Q,"),c3=("Six, E","U,"),c4=("Six, E","J,"),c5=("Six, E","five"),
umeans=("Six, E","The U"),thirty=("Six, E","thirty"),noise=("Six, E","noise"),
circles=("He circles","circles"),red=("He circles","red"),oneword=("He circles","one word"),wow=("He circles","Wow"),
hline=("It sat","hydrogen line"),freq=("It sat","frequency"),notx=("It sat","no Earth"),
went=("Telescopes","went back"),spot=("Telescopes","that spot"),dozens=("Telescopes","dozens"),nothing=("Telescopes","Nothing"),
y2024=("In 2024","2024"),cause=("In 2024","proposed"),cloud=("In 2024","hydrogen cloud"),litup=("In 2024","lit up"),flaring=("In 2024","flaring"),dead=("In 2024","dead star"),
laser=("A natural","space laser"),aimed=("A natural","aimed at Earth"),moment=("A natural","one moment"),
hypo=("Still just","hypothesis"),bigear2=("Still just","Big Ear"),torn=("Still just","torn down"),golf=("Still just","golf course"),
sheet=("So all we","one sheet"),proof=("So all we","Proof"),once=("So all we","once"),y1977b=("So all we","1977"))
EV={k:wt(*v) for k,v in _E.items()}
# manual fixes from audio gaps (toolkit/gaps.py)
_s4=Lx("Six, E")[0]
for k,v in dict(c0=0.02,c1=0.26,c2=0.5,c3=0.74,c4=0.97,c5=1.36,umeans=1.88,thirty=2.47).items(): EV[k]=_s4+v
EV["wow"]=Lx("He circles")[0]+2.22
