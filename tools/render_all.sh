#!/bin/zsh
# 渲染并总装：zsh tools/render_all.sh <who...>（每人 4 进程并行，逐人进行）
set -euo pipefail
cd "$(dirname "$0")/.."
for WHO in "$@"; do
  python3 tools/build_timeline.py "$WHO"
  python3 music/score.py "$WHO" > "out/$WHO/score.log"
  rm -rf "out/$WHO/frames"
  T=$(python3 -c "import json;print(json.load(open('src/$WHO/timeline.json'))['total'])")
  for k in 0 1 2 3; do
    a=$(python3 -c "print(round($T/4*$k,3))"); b=$(python3 -c "print(round($T/4*($k+1)+0.05,3))")
    node render.mjs "$WHO" frames "$a" "$b" > "out/$WHO/render_$k.log" 2>&1 &
  done
  wait
  N=$(ls "out/$WHO/frames" | wc -l | tr -d ' ')
  python3 -c "import sys;n=$N;t=round($T*30);sys.exit(0 if n>=t else f'$WHO frames {n} < {t}')"
  zsh tools/assemble.sh "$WHO"
done
