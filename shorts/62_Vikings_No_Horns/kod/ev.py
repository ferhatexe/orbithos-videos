import json
T=json.load(open("/home/claude/vid62/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(never=_f("Vikings never",0.6),horned=_f("Vikings never",0.9),image=_f("Vikings never",2.2),y150=_f("Vikings never",3.2),
onlyone=_f("Only one nearly",0.2),complete=_f("Only one nearly",1.0),found=_f("Only one nearly",2.7),
norway=_f("It was dug up",1.0),y1943=_f("It was dug up",1.5),farm=_f("It was dug up",2.5),gjer=_f("It was dug up",3.1),
rounded=_f("It's a rounded",0.4),guard=_f("It's a rounded",1.7),nohorns=_f("It's a rounded",2.85),
battle=_f("And in battle",0.3),horns=_f("And in battle",0.7),blade=_f("And in battle",2.1),catch=_f("And in battle",2.8),
where=_f("So where did",0.2),c19=_f("So where did",1.6),painters=_f("So where did",3.2),
y1876=_f("Then in 1876",0.2),costume=_f("Then in 1876",1.7),doepler=_f("Then in 1876",2.9),stage=_f("Then in 1876",4.4),wagner=_f("Then in 1876",5.3),
sensation=_f("The opera was",0.8),stuck=_f("The opera was",1.8),
exist=_f("Horned helmets did",0.9),scand=_f("Horned helmets did",1.5),bronze=_f("Horned helmets did",2.5),y1700=_f("Horned helmets did",3.5),vik=_f("Horned helmets did",5.2),
cerem=_f("They were probably",0.7),war=_f("They were probably",1.8),
see=_f("So next time",0.6),remember=_f("So next time",2.0))
