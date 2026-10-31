# ElevenLabs version of gen_vo_v1.py: same outputs (vo/vo_XX.wav + timeline.json). Key from env ELEVENLABS_API_KEY (never stored).
import subprocess, json, os, sys, urllib.request
OUT=os.getcwd(); sys.path.insert(0,OUT)
from lines import L
KEY=os.environ["ELEVENLABS_API_KEY"]; VOICE=os.environ.get("EL_VOICE","hpp4J3VqNfWAUOO0d1Us"); MODEL=os.environ.get("EL_MODEL","eleven_multilingual_v2")
SPEED=float(os.environ.get("EL_SPEED","1.0"))
R=[("…",", ")]
try:
    from lines import R as R2; R=R2+R
except ImportError: pass
os.makedirs("vo",exist_ok=True); out=[]
only=set(map(int,sys.argv[1:]))
texts=[]
for en,p,sc in L:
    t=en
    for a,b in R:
        if not a.isalpha(): t=t.replace(a,b)   # keep names as written: ElevenLabs pronounces them well; numbers/years spelled
    texts.append(t)
for i,(en,p,sc) in enumerate(L):
    raw=f"vo/raw_{i:02d}.mp3"; fin=f"vo/vo_{i:02d}.wav"
    if (not only and not os.path.exists(fin)) or i in only:
        prev=" ".join(texts[max(0,i-2):i]); nxt=" ".join(texts[i+1:i+2])
        body=json.dumps({"text":texts[i],"model_id":MODEL,"previous_text":prev,"next_text":nxt,
              "voice_settings":{"stability":0.45,"similarity_boost":0.8,"style":0.25,"use_speaker_boost":True,"speed":SPEED}}).encode()
        req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",data=body,
              headers={"xi-api-key":KEY,"Content-Type":"application/json","Accept":"audio/mpeg","User-Agent":"curl/8.5.0"})
        open(raw,"wb").write(urllib.request.urlopen(req,timeout=120).read())
        af="highpass=f=70,silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse"
        subprocess.run(["ffmpeg","-y","-v","error","-i",raw,"-af",af,"-ar","44100","-ac","1","-c:a","pcm_s16le",fin],check=True)
    out.append(float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",fin])))
t=float(os.environ.get("START","0.15")); T=[]
for i,(en,p,sc) in enumerate(L):
    T.append(dict(i=i,en=en,s=round(t,3),e=round(t+out[i],3),scene=sc,kind="n")); t+=out[i]+p
total=round(t+0.2,2); scenes=[]
for x in T:
    if not scenes or scenes[-1]["name"]!=x["scene"]: scenes.append(dict(name=x["scene"],s=x["s"]-0.35 if scenes else 0.0))
for a,b in zip(scenes,scenes[1:]): a["e"]=b["s"]
scenes[-1]["e"]=total
json.dump(dict(lines=T,scenes=scenes,total=total),open("timeline.json","w"),indent=1)
print("TOTAL",total)
