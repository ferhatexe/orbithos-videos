#!/bin/bash
cd /home/claude/vid41
seq 0 300 4210 | xargs -P 2 -I{} sh -c 'python3 run41.py {} $(({}+300)) >> render.log 2>&1'
echo DONE >> render.log
