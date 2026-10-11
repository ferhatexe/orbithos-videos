#!/bin/bash
cd /home/claude/vid36
seq 0 300 5379 | xargs -P 2 -I{} sh -c 'python3 run36.py {} $(({}+300)) >> render.log 2>&1'
echo DONE >> render.log
