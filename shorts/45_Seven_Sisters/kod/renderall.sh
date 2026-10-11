#!/bin/bash
cd /home/claude/vid45; rm -f render.log
seq 0 300 1390 | xargs -P 2 -I{} sh -c 'python3 run45.py {} $(({}+300)) >> render.log 2>&1'
ls seg_*.mp4 | sort | sed "s/^/file '/; s/$/'/" > segs.txt
echo DONE >> render.log
