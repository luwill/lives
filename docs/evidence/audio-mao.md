# 配乐分阶段指标 — mao

命令：`python3 tools/audio_report.py mao`（out/mao/music.wav，由 `music/score.py mao` 在 eb42007 生成）

```
stage     mood                t0      t1    dBFS  centroid  onsets/s
title     title              0.0    15.8   -21.9       637      2.73
st1       pastoral          15.8    53.8   -17.7      1426      2.89
st2       aspire            53.8    96.9   -18.1      1306      1.95
st3       tension           96.9   185.1   -19.1       916      2.72
st4       march            185.1   272.4   -17.5      2161       2.9
st5       epic             272.4   342.0   -17.3      1193       0.9
st6       contemplative    342.0   416.4   -19.5       437      1.33
st7       triumph          416.4   475.4   -16.0      1621      1.56
st8       grand            475.4   630.8   -18.1      1337      1.14
outro     outro            630.8   648.9   -18.3      1216      2.48
silent boundaries: none
peak 0.89 nan False
```

阶段→情绪映射与理由：music/mao_stages.json；频谱图：stills/spectrogram_mao.png（白线为阶段边界）
