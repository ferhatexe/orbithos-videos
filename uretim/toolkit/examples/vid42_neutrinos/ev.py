import json
T=json.load(open("/home/claude/vid42/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
rightnow=("Right now","Right now"),trillion=("Right now","hundred trillion"),ghost=("Right now","ghost particles"),body=("Right now","your body"),
second=("Every second","Every second"),skin=("Every second","skin"),bones=("Every second","bones"),earth=("Every second","entire Earth"),
neutrinos=("They're called","neutrinos"),noone=("They're called","no one"),catch1=("They're called","catch one"),
y1930=("In 1930","1930"),pauli=("In 1930","Wolfgang Pauli"),problem=("In 1930","problem"),decay=("In 1930","radioactive decay"),energy=("In 1930","some energy"),vanish=("In 1930","vanish"),
letter=("So he wrote","letter"),dear=("So he wrote","Dear Radioactive"),
tiny=("He proposed","tiny"),invisible=("He proposed","invisible particle"),carries=("He proposed","carries"),missing=("He proposed","missing energy"),desperate=("He proposed","desperate remedy"),
person=("And he didn't","in person"),skipped=("And he didn't","skipped"),ball=("And he didn't","a ball"),
named=("The particle was","named the neutrino"),italian=("The particle was","Italian"),little=("The particle was","little neutral one"),
charge=("It has no electric","electric charge"),mass=("It has no electric","almost no mass"),barely=("It has no electric","barely touches"),
sun=("Most of the neutrinos","core of the Sun"),night=("Most of the neutrinos","At night"),upearth=("Most of the neutrinos","up through the Earth"),bed=("Most of the neutrinos","your bed"),
lifetime=("In your whole","lifetime"),onehit=("In your whole","maybe one"),atom=("In your whole","an atom"),
catchg=("So how do you","catch a ghost"),trap=("So how do you","giant trap"),
y1956=("In 1956","1956"),cowan=("In 1956","Clyde Cowan"),reines=("In 1956","Frederick Reines"),detector=("In 1956","detector"),reactor=("In 1956","nuclear reactor"),carolina=("In 1956","South Carolina"),caught=("In 1956","caught them"),
telegram=("They sent Pauli","telegram"),replied=("They sent Pauli","replied"),wait=("They sent Pauli","how to wait"),
japan=("Today, Japan","Japan"),superk=("Today, Japan","Super-Kamiokande"),tank=("Today, Japan","giant tank"),mountain=("Today, Japan","mountain"),tons=("Today, Japan","fifty thousand tons"),water=("Today, Japan","ultra-pure water"),
walls=("Its walls","walls"),eleven=("Its walls","eleven thousand"),sensors=("Its walls","golden light sensors"),
hits=("When a neutrino","finally hits"),ring=("When a neutrino","ring of blue light"),
y2001=("In 2001","2001"),cracked=("In 2001","cracked"),imploded=("In 2001","imploded"),shock=("In 2001","shockwave"),chain=("In 2001","chain reaction"),thousands=("In 2001","Thousands"),burst=("In 2001","burst"),
y1987=("Then there was","1987"),
exploded=("A star exploded","star exploded"),ly=("A star exploded","light-years"),detectors=("A star exploded","Detectors on Earth"),n25=("A star exploded","twenty-five"),
arrived=("And they arrived","arrived"),hours=("And they arrived","hours before"),
escaped=("The neutrinos escaped","escaped"),first=("The neutrinos escaped","first"),later=("The neutrinos escaped","broke out later"),
y2023=("In 2023","2023"),med=("In 2023","Mediterranean"),powerful=("In 2023","most powerful"),
nobody=("Where it came","nobody knows"),
watched=("So while you","watched this"),quad=("So while you","ten quadrillion"),passed=("So while you","passed through you"),never=("So while you","never felt"))
EV={k:wt(*v) for k,v in _E.items()}
