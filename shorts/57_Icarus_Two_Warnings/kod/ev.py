import json
T=json.load(open("/home/claude/vid57/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
def S(n): return [s for s in SC if s["name"]==n][0]
def Lx(sub):
    for ln in LINES:
        if sub in ln["en"]: return ln["s"],ln["e"]
    raise KeyError(sub)
_f=lambda sub,o: Lx(sub)[0]+o
EV=dict(icarus=_f("Everyone knows",0.8),sun0=_f("Everyone knows",2.0),father=_f("Everyone knows",3.0),two=_f("Everyone knows",3.7),
daed=_f("Daedalus, a genius",0.1),genius=_f("Daedalus, a genius",0.8),crete=_f("Daedalus, a genius",2.5),minos=_f("Daedalus, a genius",3.5),
built=_f("So he built",0.3),feathers=_f("So he built",1.5),rows=_f("So he built",2.0),short=_f("So he built",2.4),long=_f("So he built",2.8),pipes=_f("So he built",3.6),
thread=_f("bound them",0.5),wax=_f("bound them",1.7),
before=_f("Before they flew",0.1),high=_f("Before they flew",1.6),sun=_f("Before they flew",2.5),melt=_f("Before they flew",3.0),
low=_f("And not too low",0.6),sea=_f("And not too low",1.1),soak=_f("And not too low",1.5),drag=_f("And not too low",2.2),
middle=_f("Fly the middle",0.3),
below=_f("Below, a fisherman",0.05),fisher=_f("Below, a fisherman",0.6),shepherd=_f("Below, a fisherman",1.25),gods=_f("Below, a fisherman",2.5),
climb=_f("But Icarus, thrilled",1.2),higher=_f("But Icarus, thrilled",1.7),soft=_f("But Icarus, thrilled",2.7),slip=_f("But Icarus, thrilled",3.5),
fell=_f("and he fell",0.3),name=_f("and he fell",1.3),icarian=_f("and he fell",2.1),
buried=_f("His father buried",0.7),island=_f("His father buried",1.7),icaria=_f("His father buried",2.5),
remember=_f("We remember",0.1),warning=_f("We remember",0.9),toohigh=_f("We remember",2.0),
ovid=_f("But in Ovid",0.4),toolow=_f("But in Ovid",1.2),deadly=_f("But in Ovid",1.9),yet=_f("But in Ovid",2.6))
