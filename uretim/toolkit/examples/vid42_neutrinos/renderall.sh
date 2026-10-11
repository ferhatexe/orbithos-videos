#!/bin/bash
cd /home/claude/vid42
seq 0 300 4011 | xargs -P 2 -I{} sh -c 'python3 run42.py {} $(({}+300)) >> render.log 2>&1'
echo DONE >> render.log
