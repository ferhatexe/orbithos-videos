#!/bin/bash
cd /home/claude/vid40
seq 0 300 3225 | xargs -P 2 -I{} sh -c 'python3 run40.py {} $(({}+300)) >> render.log 2>&1'
echo DONE >> render.log
