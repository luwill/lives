# 配乐分阶段指标 — zhuge

命令：`python3 tools/audio_report.py zhuge`（out/zhuge/music.wav，由 `music/score.py zhuge` 生成）

```
stage     mood                t0      t1    dBFS  centroid  onsets/s
title     title              0.0    21.6   -21.5       703      2.41
st1       contemplative     21.6    76.1   -21.2       521      1.41
st2       pastoral          76.1   123.4   -18.8      1615      2.77
st3       battle           123.4   209.7   -17.1       785      2.91
st4       aspire           209.7   256.2   -18.6      1097      2.04
st5       grand            256.2   358.1   -18.7      1294       1.3
st6       epic             358.1   509.3   -18.0      1178      0.81
outro     outro            509.3   535.4   -19.1      1340      2.37
silent boundaries: none
peak 0.895 nan False
```

阶段→情绪映射与理由：music/zhuge_stages.json；频谱图：stills/spectrogram_zhuge.png（白线为阶段边界）
