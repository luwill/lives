# 配乐客观指标：libai

命令：`python3 tools/audio_report.py libai`（读 out/libai/music.wav，提交 573fd1a 时生成）。每个阶段的响度、频谱质心、起音密度；阶段边界是否有静音。审美效果未经试听。

```
stage     mood                t0      t1    dBFS  centroid  onsets/s
title     title              0.0    16.9   -17.2       576      1.48
st1       pastoral          16.9    70.5   -16.8      1447      2.63
st2       joyful            70.5   103.6   -16.5      1733      3.26
st3       wander           103.6   176.9   -16.5      1543      2.99
st4       serene           176.9   197.3   -17.2      1083      1.62
st5       triumph          197.3   251.2   -15.4      1649      1.58
st6       aspire           251.2   341.3   -16.7      1048      2.17
st7       tension          341.3   424.4   -17.3       879      2.54
st8       elegy            424.4   454.7   -18.1       881      1.42
outro     outro            454.7   475.2   -17.4      1173      2.09
silent boundaries: none
peak 0.869 nan False
```
