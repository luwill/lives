#!/bin/zsh
# 渲染并总装：zsh tools/render_all.sh <who...>（每人 4 进程并行，逐人进行）
set -euo pipefail
cd "$(dirname "$0")/.."
# 成片来自哪个提交：开始渲染前记录（工作区有改动或未跟踪文件时标 dirty）
REV="$(git rev-parse --short HEAD)$([ -z "$(git status --porcelain -- src data narration music tools render.mjs tests)" ] || echo -dirty)"
for WHO in "$@"; do
  python3 tools/person.py name "$WHO" >/dev/null   # 校验人物键（[a-z0-9_]+ 且 person.json 可加载），先于任何删除
  mkdir -p "out/$WHO"
  python3 tools/build_timeline.py "$WHO"
  python3 music/score.py "$WHO" > "out/$WHO/score.log"
  rm -rf "out/$WHO/frames"
  T=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["total"])' "src/$WHO/timeline.json")
  for k in 0 1 2 3; do
    a=$(python3 -c 'import sys;T,k=float(sys.argv[1]),int(sys.argv[2]);print(round(T/4*k,3))' "$T" "$k"); b=$(python3 -c 'import sys;T,k=float(sys.argv[1]),int(sys.argv[2]);print(round(T/4*(k+1)+0.05,3))' "$T" "$k")
    node render.mjs "$WHO" frames "$a" "$b" > "out/$WHO/render_$k.log" 2>&1 &
  done
  wait
  N=$(ls "out/$WHO/frames" | wc -l | tr -d ' ')
  python3 -c 'import sys;n=int(sys.argv[1]);t=round(float(sys.argv[2])*30);sys.exit(0 if n>=t else f"{sys.argv[3]} frames {n} < {t}")' "$N" "$T" "$WHO"
  zsh tools/assemble.sh "$WHO"
  echo "$REV" > "out/$WHO/render_commit.txt"
done
