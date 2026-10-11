import subprocess, math, time, sys, r48 as render
N=int(math.ceil(render.TOTAL*30)); a=int(sys.argv[1]); b=min(int(sys.argv[2]),N)
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920","-r","30","-i","-",
 "-c:v","libx264","-preset","ultrafast","-crf","20","-pix_fmt","yuv420p",f"seg_{a:05d}.mp4"],stdin=subprocess.PIPE)
t0=time.time()
for f in range(a,b): p.stdin.write(render.compose(f/30).tobytes())
p.stdin.close(); p.wait(); print(a,b,N,round(time.time()-t0))
