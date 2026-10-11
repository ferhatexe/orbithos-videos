import json
T=json.load(open("/home/claude/vid41/timeline.json")); LINES=T["lines"]; SC=T["scenes"]
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
y1692=("In 1692, a small","1692"),town=("In 1692, a small","small town"),hanged=("In 1692, a small","hanged nineteen"),witch=("In 1692, a small","witchcraft"),
girls=("It all began","two girls"),scream=("It all began","scream"),shake=("It all began","shake"),twist=("It all began","twist"),
scientist=("Almost three","scientist"),question=("Almost three","shocking question"),fungus=("Almost three","fungus"),
salem=("Salem Village","Salem Village"),betty=("Salem Village","Betty Parris"),abigail=("Salem Village","Abigail"),fits=("Salem Village","fits"),
screamed=("They screamed","screamed"),threw=("They screamed","threw things"),sounds=("They screamed","strange sounds"),doctor=("They screamed","doctor"),wc=("They screamed","Witchcraft"),
more=("Soon, more girls","more girls"),names=("Soon, more girls","name names"),
first=("The first accused","first accused"),edges=("The first accused","edges"),tituba=("The first accused","Tituba"),good=("The first accused","Sarah Good"),osborne=("The first accused","Sarah Osborne"),
confessed=("Tituba confessed","confessed"),devil=("Tituba confessed","Devil"),panic=("Tituba confessed","panic exploded"),
court=("A special court","special court"),spectral=("A special court","spectral evidence"),dream=("A special court","dream"),proof=("A special court","proof"),
k200=("More than two hundred","two hundred"),
burned=("No one was burned","No one was burned"),n19=("No one was burned","Nineteen were hanged"),corey=("No one was burned","Giles Corey"),plead=("No one was burned","refused to plead"),stones=("No one was burned","heavy stones"),
y1976=("In 1976","1976"),capo=("In 1976","Linnda"),journal=("In 1976","Science"),
rye=("Salem's farmers","rye"),infected=("Salem's farmers","infected"),ergotw=("Salem's farmers","ergot"),
bread=("Eat bread","bread"),ergotism=("Eat bread","ergotism"),spasms=("Eat bread","Spasms"),conv=("Eat bread","Convulsions"),crawl=("Eat bread","crawling"),hallu=("Eat bread","Hallucinations"),
lsd=("In fact, LSD","LSD"),compound=("In fact, LSD","compound"),
poisoned=("So, were the girls","poisoned"),ownbread=("So, were the girls","own bread"),
no=("Many historians","say no"),
families=("Families shared","Families"),oneortwo=("Families shared","one or two"),andover=("Families shared","Andover"),
witness=("One witness","witness"),sport=("One witness","for sport"),
fear=("Fear, old rivalries","Fear"),rival=("Fear, old rivalries","rivalries"),dreams=("Fear, old rivalries","dreams"),anyf=("Fear, old rivalries","any fungus"),
regret=("Within a few years","regretted"),unlawful=("Within a few years","unlawful"),
last=("And the last convicted","last convicted"),johnson=("And the last convicted","Elizabeth Johnson"),y2022=("And the last convicted","2022"),y330=("And the last convicted","Three hundred and thirty"),
scariest=("Maybe the scariest","scariest"),notw=("Maybe the scariest","not witches"),frightened=("Maybe the scariest","frightened people"))
EV={k:wt(*v) for k,v in _E.items()}
