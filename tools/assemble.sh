#!/bin/zsh
# 总装：逐帧 JPG + 混音 → 成片（H.264 CRF20 + AAC，响度归一到 -16 LUFS）
# 用法：zsh tools/assemble.sh <who>
set -euo pipefail
cd "$(dirname "$0")/.."
WHO=$1
typeset -A NAME=(mao 毛泽东 zhuge 诸葛亮 sushi 苏轼 libai 李白 zhuyz 朱元璋 jiang 蒋介石)
OUT="${NAME[$WHO]}_人生轨迹.mp4"
TOTAL=$(python3 -c "import json;print(json.load(open('src/$WHO/timeline.json'))['total'])")
python3 tools/mix.py "$WHO"
ffmpeg -v error -y -framerate 30 -start_number 0 -i "out/$WHO/frames/%05d.jpg" -i "out/$WHO/mix.wav" \
  -t "$TOTAL" -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -movflags +faststart \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 48000 "$OUT"
ffprobe -v error -show_entries format=duration,size -of compact "$OUT"
