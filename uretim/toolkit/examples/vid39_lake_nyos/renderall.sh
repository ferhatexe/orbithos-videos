#!/bin/bash
cd /home/claude/vid39
seq 0 300 4069 | xargs -P 2 -I{} sh -c 'python3 run39.py {} $(({}+300)) >> render.log 2>&1'
echo DONE >> render.log
