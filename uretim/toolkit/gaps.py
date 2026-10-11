import soundfile as sf, numpy as np, sys
# print silent gaps (>=MIN s) inside vo lines: python3 gaps.py 4 5 ...
MIN=0.06
for i in map(int,sys.argv[1:]):
    a,sr=sf.read(f"vo/vo_{i:02d}.wav"); n=int(0.02*sr); e=np.sqrt(np.convolve(a**2,np.ones(n)/n,'same'))
    thr=max(0.004,0.06*np.percentile(e,95)); q=e<thr; out=[]; k=0
    while k<len(q):
        if q[k]:
            j=k
            while j<len(q) and q[j]: j+=1
            if (j-k)/sr>=MIN: out.append((round(k/sr,2),round(j/sr,2)))
            k=j
        else: k+=1
    print(i,round(len(a)/sr,2),out)
