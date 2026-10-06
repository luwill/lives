# 配乐客观指标：zhuyz

命令：`python3 tools/audio_report.py zhuyz`（读 out/zhuyz/music.wav，提交 573fd1a 时生成）。每个阶段的响度、频谱质心、起音密度；阶段边界是否有静音。审美效果未经试听。

```
stage     mood                t0      t1    dBFS  centroid  onsets/s
title     title              0.0    21.3   -19.8       631      2.49
st1       elegy             21.3    83.4   -18.4      1014      1.34
st2       wander            83.4   118.9   -15.5      1489      3.16
st3       tension          118.9   153.4   -16.8       945      2.72
st4       aspire           153.4   205.1   -16.1      1342      2.23
st5       battle           205.1   336.1   -14.4       764      2.92
st6       grand            336.1   374.3   -15.8      1307      1.02
st7       contemplative    374.3   426.9   -18.5       478      1.27
st8       elegy            426.9   490.8   -18.3       886      1.38
outro     outro            490.8   513.0   -16.6      1172      2.34
silent boundaries: none
peak 0.862 nan False
```
