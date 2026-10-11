#!/bin/bash
cd /home/claude/vid38
seq 0 300 3655 | xargs -P 2 -I{} sh -c 'python3 run38.py {} $(({}+300)) >> render.log 2>&1'
echo DONE >> render.log
