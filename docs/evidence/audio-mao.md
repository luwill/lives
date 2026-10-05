# 配乐分阶段指标 — mao

命令：`python3 tools/audio_report.py mao`（out/mao/music.wav，由 `music/score.py mao` 生成）

```
stage     mood                t0      t1    dBFS  centroid  onsets/s
title     title              0.0    23.6   -22.5       642      2.16
st1       pastoral          23.6    62.4   -18.2      1425      2.76
st2       aspire            62.4   111.5   -18.7      1327      1.95
st3       tension          111.5   210.5   -19.8       917      2.72
st4       march            210.5   312.6   -18.1      2166      2.98
st5       epic             312.6   386.0   -17.9      1193      0.79
st6       contemplative    386.0   466.1   -20.2       431      1.17
st7       triumph          466.1   527.2   -16.5      1619      1.52
st8       grand            527.2   705.9   -18.7      1334      1.09
outro     outro            705.9   731.0   -18.9      1213      2.35
silent boundaries: none
peak 0.88 nan False
```

阶段→情绪映射与理由：music/mao_stages.json；频谱图：stills/spectrogram_mao.png（白线为阶段边界）
