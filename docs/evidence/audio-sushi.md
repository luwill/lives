# 配乐分阶段指标 — sushi

命令：`python3 tools/audio_report.py sushi`（out/sushi/music.wav，由 `music/score.py sushi` 生成）

```
stage     mood                t0      t1    dBFS  centroid  onsets/s
title     title              0.0    19.7   -17.2       584      1.47
st1       pastoral          19.7    60.6   -16.8      1586      2.64
st2       aspire            60.6   174.0   -17.3      1317      2.05
st3       wander           174.0   265.9   -17.0      1662      2.96
st4       contemplative    265.9   372.4   -19.8       506       1.2
st5       joyful           372.4   446.1   -17.2      1684      3.16
st6       elegy            446.1   523.1   -19.6      1013      0.82
st7       serene           523.1   566.3   -18.7       987      1.53
outro     outro            566.3   583.2   -16.8      1249      2.12
silent boundaries: none
peak 0.863 nan False
```

阶段→情绪映射与理由：music/sushi_stages.json；频谱图：stills/spectrogram_sushi.png（白线为阶段边界）
