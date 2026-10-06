# 配乐分阶段指标 — sushi

命令：`python3 tools/audio_report.py sushi`（out/sushi/music.wav，由 `music/score.py sushi` 在 eb42007 生成）

```
stage     mood                t0      t1    dBFS  centroid  onsets/s
title     title              0.0    15.7   -15.7       579      1.66
st1       pastoral          15.7    56.6   -15.2      1594      2.62
st2       aspire            56.6   161.5   -15.6      1315      2.11
st3       wander           161.5   250.4   -15.4      1665      2.96
st4       contemplative    250.4   349.0   -18.0       516      1.09
st5       joyful           349.0   413.5   -15.6      1685       3.3
st6       elegy            413.5   486.1   -17.9      1012      1.01
st7       serene           486.1   529.2   -17.1       986      1.55
outro     outro            529.2   546.2   -15.2      1250      2.36
silent boundaries: none
peak 0.897 nan False
```

阶段→情绪映射与理由：music/sushi_stages.json；频谱图：stills/spectrogram_sushi.png（白线为阶段边界）
