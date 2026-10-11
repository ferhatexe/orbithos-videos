import subprocess, json, os, sys, sherpa_onnx, soundfile as sf
OUT=os.getcwd(); sys.path.insert(0,OUT)
from lines import L
SID=int(os.environ.get("SID","3")); SPD=float(os.environ.get("SPD","0.95"))
d="/tmp/kokoro-multi-lang-v1_0"
tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
    model=f"{d}/model.onnx",voices=f"{d}/voices.bin",tokens=f"{d}/tokens.txt",data_dir=f"{d}/espeak-ng-data",dict_dir=f"{d}/dict",
    lexicon=f"{d}/lexicon-us-en.txt,{d}/lexicon-zh.txt"),num_threads=4),max_num_sentences=1))
R=[("…",", ")]
try:
    from lines import R as R2; R=R2+R
except ImportError: pass
os.makedirs("vo",exist_ok=True); out=[]
only=set(map(int,sys.argv[1:]))
for i,(en,p,sc) in enumerate(L):
    raw=f"vo/raw_{i:02d}.wav"; fin=f"vo/vo_{i:02d}.wav"
    if not only or i in only or not os.path.exists(fin):
        t=en
        for a,b in R: t=t.replace(a,b)
        a=tts.generate(t,sid=SID,speed=SPD); sf.write(raw,a.samples,a.sample_rate)
        af="highpass=f=70,silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse"
        subprocess.run(["ffmpeg","-y","-v","error","-i",raw,"-af",af,"-ar","44100","-ac","1",fin],check=True)
    out.append(float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",fin])))
t=float(os.environ.get("START","0.9")); T=[]
for i,(en,p,sc) in enumerate(L):
    T.append(dict(i=i,en=en,s=round(t,3),e=round(t+out[i],3),scene=sc,kind="n")); t+=out[i]+p
total=round(t+0.2,2); scenes=[]
for x in T:
    if not scenes or scenes[-1]["name"]!=x["scene"]: scenes.append(dict(name=x["scene"],s=x["s"]-0.35 if scenes else 0.0))
for a,b in zip(scenes,scenes[1:]): a["e"]=b["s"]
scenes[-1]["e"]=total
json.dump(dict(lines=T,scenes=scenes,total=total),open("timeline.json","w"),indent=1)
for s in scenes: print(s["name"],round(s["s"],1),round(s["e"],1))
print("TOTAL",total)
