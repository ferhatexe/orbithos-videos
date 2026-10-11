# Orbithos Toolkit (hand-made video engine) — v2

Upload this zip in a NEW Claude Code session and say:
"Unzip the Orbithos toolkit and use it to produce the next video (topic: ...)."
A full step-by-step prompt is in the test package: 02_PROMPT_CLAUDE_CODE.txt

## Setup
unzip orbithos_toolkit.zip -d /home/claude/ && bash /home/claude/toolkit/setup.sh
- Kokoro TTS v1.0 multi-lang -> /tmp/kokoro-multi-lang-v1_0 (SID 3 = af_heart female, best; SID 2 = af_bella; SPD 0.95)
- Fonts: canvas-fonts if present, otherwise toolkit/assets/fonts (bundled, OFL)

## New project
mkdir /home/claude/vid42 && cp toolkit/examples/vid41_salem/* toolkit/core/{paper.py,Cinzel.ttf,cloud.npy,stars.npy,wm_orbithos.png} /home/claude/vid42/
cd /home/claude/vid42 && sed -i 's/vid41/vid42/g; s/r41/r42/g' *.py *.sh && mv r41.py r42.py && mv run41.py run42.py && mv audio41.py audio42.py

## Pipeline
1. lines.py   : L=[(text, pause_after, scene)], R=[(spelling, pronunciation)]
2. SID=3 SPD=0.95 python3 /home/claude/toolkit/gen_vo_v1.py   -> vo/*.wav + timeline.json (arg N = redo line N, 999 = timeline only)
3. ev.py      : word-level event times wt(line_part, word) -> EV dict
4. rNN.py     : renderer (540x960 float canvas -> 1080x1920), scenes s_<name>(t,sc), unique transition in compose(t)
               test frames: python3 rNN.py 6 22 30 ... -> t_*.jpg
5. audioNN.py : music + EV-synced SFX, then master.master(vo,bus,SR,"mix.wav",bus_gain=..)
               QA target: -14 LUFS, <= -1 dBTP, voice-over-bus 16-17 dB, harsh seconds []
6. renderall.sh (runNN.py chunks of 300 frames, 2 parallel) -> fin.sh (final mp4 + <30 MB mobile copy)
7. thumb.py -> thumbstd.make(...) 1080x1920 channel format (logo standard, never add a backing box)

## Channel rules
- Max 2:59 (aim 2:00-2:30). English narration + karaoke subtitles (current word orange)
- New visual style + topic-specific transition every video; no dark "code/hacker" look
- Word-synced cards & SFX; music/SFX under the voice; no crackle
- Facts verified by web search; hypotheses presented as hypotheses; sources in description
- Title / description / tags / pinned comment delivered as separate copyable blocks
