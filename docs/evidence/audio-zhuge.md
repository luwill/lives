# 配乐分阶段指标 — zhuge

命令：`python3 tools/audio_report.py zhuge`（out/zhuge/music.wav，由 `music/score.py zhuge` 在 eb42007 生成）

```
stage     mood                t0      t1    dBFS  centroid  onsets/s
title     title              0.0    21.6   -21.4       703      2.41
st1       contemplative     21.6    76.1   -21.2       521      1.41
st2       pastoral          76.1   123.4   -18.7      1615      2.77
st3       battle           123.4   209.7   -17.1       785      2.91
st4       aspire           209.7   256.2   -18.5      1097      2.04
st5       grand            256.2   358.9   -18.7      1296      1.29
st6       epic             358.9   511.7   -18.0      1177      0.82
outro     outro            511.7   537.8   -19.0      1335      1.57
silent boundaries: none
peak 0.895 nan False
```

阶段→情绪映射与理由：music/zhuge_stages.json；频谱图：stills/spectrogram_zhuge.png（白线为阶段边界）
