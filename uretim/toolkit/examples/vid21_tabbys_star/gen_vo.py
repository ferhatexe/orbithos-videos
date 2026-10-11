import subprocess, json, re, sherpa_onnx, soundfile as sf
from lines import L
d="/tmp/kokoro-en-v0_19"
tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=f"{d}/model.onnx",voices=f"{d}/voices.bin",tokens=f"{d}/tokens.txt",data_dir=f"{d}/espeak-ng-data"),num_threads=1),max_num_sentences=1))
R=[("KIC 8462852","K I C, eight four six two, eight five two"),("WTF","W T F"),("Boyajian","Boy-ah-jee-an"),("Tabetha","Ta-beth-a"),("Cygnus","Sig-nus"),("…",", ")]
out=[]
for i,(en,p,sc) in enumerate(L):
    t=en
    for a,b in R: t=t.replace(a,b)
    a=tts.generate(t,sid=1,speed=0.98); raw=f"vo/raw_{i:02d}.wav"; fin=f"vo/vo_{i:02d}.wav"
    sf.write(raw,a.samples,a.sample_rate)
    af="highpass=f=70,equalizer=f=220:t=q:w=1:g=2,equalizer=f=6000:t=q:w=1:g=1.5,silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse"
    subprocess.run(["ffmpeg","-y","-v","error","-i",raw,"-af",af,"-ar","44100","-ac","1",fin],check=True)
    out.append(float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",fin])))
t=0.9; T=[]
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
