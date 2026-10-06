# 配乐客观指标：jiang

命令：`python3 tools/audio_report.py jiang`（读 out/jiang/music.wav，提交 573fd1a 时生成）。每个阶段的响度、频谱质心、起音密度；阶段边界是否有静音。审美效果未经试听。

```
stage     mood                t0      t1    dBFS  centroid  onsets/s
title     title              0.0    16.2   -22.6       640      2.78
st1       pastoral          16.2    52.6   -18.7      1578      2.75
st2       aspire            52.6   112.5   -18.8      1247      2.24
st3       wander           112.5   180.6   -18.8      1515      3.06
st4       march            180.6   300.2   -18.2      2172      2.96
st5       tension          300.2   378.0   -19.1       915      2.48
st6       epic             378.0   459.0   -17.7      1149      0.77
st7       battle           459.0   513.8   -17.0       745      2.57
st8       elegy            513.8   562.4   -20.7       965      1.21
outro     outro            562.4   585.0   -19.3      1161      2.61
silent boundaries: none
peak 0.898 nan False
```
