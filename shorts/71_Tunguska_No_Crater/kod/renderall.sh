#!/bin/bash
cd /home/claude/vid71; rm -f render.log
seq 0 300 1650 | xargs -P 2 -I{} sh -c 'if [ {} -lt $(python3 -c "import json,math;print(math.ceil(json.load(open(\"timeline.json\"))[\"total\"]*30))") ]; then python3 run71.py {} $(({}+300)) >> render.log 2>&1; fi'
ls seg_*.mp4 | sort | sed "s/^/file '/; s/$/'/" > segs.txt
echo DONE >> render.log
