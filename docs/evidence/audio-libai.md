# 配乐客观指标：libai

命令：`python3 tools/audio_report.py libai`（读 out/libai/music.wav，由 dd22653 渲染时合成；同一输出也在 gate-batch2-final.md 中由 run-gate 记录）。审美效果未经试听。

```
stage     mood                t0      t1    dBFS  centroid  onsets/s
title     title              0.0    16.8   -18.7       577      1.55
st1       pastoral          16.8    69.8   -18.3      1442      2.64
st2       joyful            69.8   103.0   -18.0      1732      3.23
st3       wander           103.0   178.6   -17.9      1542       3.0
st4       serene           178.6   199.0   -18.5      1090      2.06
st5       triumph          199.0   252.9   -16.8      1647      1.56
st6       aspire           252.9   346.1   -18.1      1050      2.17
st7       tension          346.1   429.2   -18.7       878       2.5
st8       elegy            429.2   459.5   -19.6       881      1.52
outro     outro            459.5   480.1   -18.9      1172      2.09
silent boundaries: none
peak 0.886 nan False
```
