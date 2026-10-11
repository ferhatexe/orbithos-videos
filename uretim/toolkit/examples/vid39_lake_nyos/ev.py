import json
T=json.load(open("/home/claude/vid39/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
night=("On the night","night"),date=("On the night","August"),lake=("On the night","lake in Cameroon"),killed=("On the night","killed"),n1750=("On the night","1,750"),
noexp=("There was no explosion","explosion"),nofire=("There was no explosion","No fire"),nosound=("There was no explosion","No sound"),
morning=("By morning","morning"),silent=("By morning","silent"),
nyos=("Lake Nyos sits","Lake Nyos"),crater=("Lake Nyos sits","crater"),volcano=("Lake Nyos sits","volcano"),camer=("Lake Nyos sits","northwest Cameroon"),
magma=("Deep below","magma"),co2=("Deep below","carbon dioxide"),water=("Deep below","water"),
bottom=("At the bottom","bottom"),pressure=("At the bottom","pressure"),dissolved=("At the bottom","dissolved"),soda=("At the bottom","soda"),fizzier=("At the bottom","fizzier"),
nine=("Then, around nine","nine at night"),disturbed=("Then, around nine","disturbed"),
landslide=("Maybe a landslide","landslide"),rain=("Maybe a landslide","heavy rain"),quake=("Maybe a landslide","earthquake"),nobody=("Maybe a landslide","Nobody knows"),
rose=("Deep water rose","rose"),dropped=("Deep water rose","pressure dropped"),allonce=("Deep water rose","all at once"),
fountain=("A fountain of water","fountain"),m90=("A fountain of water","ninety meters"),wave=("A fountain of water","wave"),
cloudw=("And a huge, invisible","huge"),invisible=("And a huge, invisible","invisible"),rolled=("And a huge, invisible","rolled"),rim=("And a huge, invisible","rim"),
heavier=("Carbon dioxide is heavier","heavier than air"),sank=("Carbon dioxide is heavier","It sank"),poured=("Carbon dioxide is heavier","poured down"),
km25=("It spread as far","twenty-five"),m50=("It spread as far","fifty meters"),oxygen=("It spread as far","oxygen"),
villages=("In the villages","villages"),vnyos=("In the villages","Nyos"),kam=("In the villages","Kam"),cha=("In the villages","Cha"),subum=("In the villages","Subum"),home=("In the villages","at home"),asleep=("In the villages","asleep"),
never=("Most of them","never woke"),cattle=("Most of them","cattle"),insects=("Most of them","insects"),
survivor=("One survivor","survivor"),speak=("One survivor","unable to speak"),smell=("One survivor","smell"),
blue=("And the lake, once blue","once blue"),red=("And the lake, once blue","rusty red"),iron=("And the lake, once blue","Iron"),
limnic=("Scientists call it","limnic eruption"),rarest=("Scientists call it","rarest"),
before=("And it had happened","happened before"),y1984=("And it had happened","1984"),monoun=("And it had happened","Lake Monoun"),k37=("And it had happened","thirty-seven"),
clever=("So engineers","clever"),y2001=("So engineers","2001"),pipe=("So engineers","pipe"),
rising=("Once the gassy","started rising"),pushed=("Once the gassy","pushed itself"),keeps=("Once the gassy","fountain that keeps"),slowly=("Once the gassy","slowly"),
more=("More pipes","More pipes"),y2011=("More pipes","2011"),less=("More pipes","far less gas"),
another=("But there is another","another lake"),kivu=("But there is another","Lake Kivu"),bigger=("But there is another","far bigger"),full=("But there is another","full of dissolved"),millions=("But there is another","Millions"),
quiet=("The quietest","quietest"),deadliest=("The quietest","deadliest"))
EV={k:wt(*v) for k,v in _E.items()}
