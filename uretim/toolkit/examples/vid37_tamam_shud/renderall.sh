#!/bin/bash
cd /home/claude/vid37
seq 0 300 5366 | xargs -P 2 -I{} sh -c 'python3 run37.py {} $(({}+300)) >> render.log 2>&1'
echo DONE >> render.log
