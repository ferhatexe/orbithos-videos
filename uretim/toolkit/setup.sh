#!/bin/bash
# Orbithos toolkit kurulum (Claude Code bulut ortamı). Yollar /home/claude ve /mnt/user-data/outputs sabit.
set -e
SUDO=""; [ "$(id -u)" != "0" ] && command -v sudo >/dev/null && SUDO="sudo"
for d in /home/claude /mnt/user-data/outputs; do mkdir -p $d 2>/dev/null || { $SUDO mkdir -p $d && $SUDO chown -R $(id -u):$(id -g) $d; }; done
[ -d /home/claude/toolkit ] || cp -r "$(cd "$(dirname "$0")" && pwd)" /home/claude/toolkit
mkdir -p /home/claude/vid3 /home/claude/ep1 /home/claude/vid8
cp /home/claude/toolkit/core/* /home/claude/vid3/
cp /home/claude/toolkit/core/rep1.py /home/claude/ep1/
cp /home/claude/toolkit/core8/render8.py /home/claude/vid8/
cp /home/claude/toolkit/assets/logo.png /mnt/user-data/outputs/orbithos_logo_seffaf.png
command -v ffmpeg >/dev/null || { $SUDO apt-get update -qq && $SUDO apt-get install -y -qq ffmpeg; }
pip install -q numpy scipy opencv-python-headless pillow pedalboard pyloudnorm sherpa-onnx soundfile fonttools --break-system-packages 2>/dev/null || pip install -q numpy scipy opencv-python-headless pillow pedalboard pyloudnorm sherpa-onnx soundfile fonttools
if [ ! -f /tmp/kokoro-multi-lang-v1_0/model.onnx ]; then
  cd /tmp && curl -sSL -o k.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_0.tar.bz2 && tar xjf k.tar.bz2 && rm k.tar.bz2
fi
echo "Orbithos toolkit ready"
