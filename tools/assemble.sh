#!/bin/zsh
# 总装：逐帧 JPG + 混音 → 成片（H.264 CRF20 + AAC，响度归一到 -16 LUFS）
# 用法：zsh tools/assemble.sh <who>
set -euo pipefail
cd "$(dirname "$0")/.."
WHO=$1
NAME=$(python3 tools/person.py name "$WHO")
OUT="${NAME}_人生轨迹.mp4"
TOTAL=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["total"])' "src/$WHO/timeline.json")
python3 tools/mix.py "$WHO"
# Chrome 截图是全范围 BT.601 的 JPG：转成标准范围 BT.709 并写明色彩标签，否则成片被标为 pc 范围，部分播放器/平台会偏色
COLOR="scale=in_range=full:out_range=limited:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p,setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709"
ffmpeg -v error -y -framerate 30 -start_number 0 -i "out/$WHO/frames/%05d.jpg" -i "out/$WHO/mix.wav" \
  -t "$TOTAL" -vf "$COLOR" -c:v libx264 -preset slow -crf 20 -movflags +faststart \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 48000 "$OUT"
ffprobe -v error -show_entries format=duration,size -of compact "$OUT"
