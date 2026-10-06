#!/bin/zsh
# 审片拼板：从成片每 30 秒取一帧，拼成 4 列网格 → docs/evidence/stills/sheet_<who>.jpg
# 用法：zsh tools/contact_sheet.sh <who>   （同时打印成片的渲染提交与 sha256 前 12 位，便于核对拼板来自哪一版成片）
set -euo pipefail
cd "$(dirname "$0")/.."
WHO=$1
typeset -A NAME=(mao 毛泽东 zhuge 诸葛亮 sushi 苏轼 libai 李白 zhuyz 朱元璋 jiang 蒋介石)
MP4="${NAME[$WHO]}_人生轨迹.mp4"
N=$(python3 -c "import json;print(int(json.load(open('src/$WHO/timeline.json'))['total']//30))")
ROWS=$(( (N + 3) / 4 ))
ffmpeg -v error -y -i "$MP4" -vf "fps=1/30,scale=480:270,tile=4x${ROWS}" -frames:v 1 -q:v 4 "docs/evidence/stills/sheet_$WHO.jpg"
echo "$WHO sheet from $MP4 sha256=$(shasum -a 256 "$MP4" | cut -c1-12) render=$(cat "out/$WHO/render_commit.txt" 2>/dev/null || echo unknown)"
