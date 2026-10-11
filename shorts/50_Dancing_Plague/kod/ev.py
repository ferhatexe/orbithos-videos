import json
T=json.load(open("/home/claude/vid50/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(woman=_f("A woman",0.1),dancing=_f("A woman",0.8),stop=_f("A woman",1.9),
month=_f("Within a month",0.0),hundreds=_f("Within a month",0.9),what=_f("Within a month",2.1),
july=_f("It's July",0.1),troffea=_f("It's July",1.0),alone=_f("It's July",2.1),week=_f("It's July",2.9),
others=_f("Then others",0.1),dozens=_f("Then others",1.1),four=_f("Then others",2.2),
daynight=_f("They dance day",0.5),heat=_f("They dance day",1.4),
doctors=_f("Doctors",0.1),hot=_f("Doctors",1.2),cure=_f("Doctors",2.2),more=_f("Doctors",2.6),
guild=_f("The city clears",0.9),stage=_f("The city clears",2.0),musicians=_f("The city clears",3.1),
worse=_f("It only makes",1.0),collapsed=_f("It only makes",2.9),
fin_=_f("Finally",0.1),shrine=_f("Finally",2.0),redshoes=_f("Finally",3.3),prayed=_f("Finally",4.2),
slowly=_f("Slowly",0.2),stops=_f("Slowly",1.0),
similar=_f("Similar",0.2),centuries=_f("Similar",1.9),
historians=_f("Historians",0.2),hysteria=_f("Historians",1.4),famine=_f("Historians",3.3),
fear=_f("Fear spread",0.1),person=_f("Fear spread",1.1),bodies=_f("Fear spread",2.4),
began=_f("It all began",0.3),strasbourg=_f("It all began",1.0),y1518=_f("It all began",1.8))
