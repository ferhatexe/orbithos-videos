#!/bin/bash
cd /home/claude/vid71
O=/mnt/user-data/outputs/orbithos_tunguska_no_crater_EN.mp4
ffmpeg -y -v error -f concat -safe 0 -i segs.txt -i mix.wav -c:v libx264 -preset veryfast -crf 18 -maxrate 8M -bufsize 16M -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart $O
ffmpeg -y -v error -i $O -c:v libx264 -preset medium -b:v 1500k -pass 1 -passlogfile /tmp/ffv71 -an -f null /dev/null
ffmpeg -y -v error -i $O -c:v libx264 -preset medium -b:v 1500k -pass 2 -passlogfile /tmp/ffv71 -c:a aac -b:a 128k -movflags +faststart /mnt/user-data/outputs/orbithos_tunguska_no_crater_EN_mobil.mp4
rm -f /tmp/ffv71*
echo FIN > fin.log
