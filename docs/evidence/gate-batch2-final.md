# Machine gate — batch2-final

- commit: fddc945
- working tree: clean (the gate refuses to start otherwise)
- recorded by: /Users/louwill/.claude/skills/autopilot/scripts/run-gate.sh (sha256 f7df72490cb4216d)
- started: 2026-10-06T10:55:50Z
- workdir: /Users/louwill/Vibing/daily-test/opus5.5-video-test/lives

## 1. `python3 -m pytest -q tests`

exit 0 · 2 s

```
........................................................................ [ 72%]
...........................                                              [100%]Running teardown with pytest sessionfinish...

99 passed in 0.51s
```

## 2. `node tools/smoke.mjs`

exit 0 · 8 s

```
mao: total 648.9s, 24 samples, frame std 30.8, errors 0
zhuge: total 537.8s, 24 samples, frame std 14.0, errors 0
sushi: total 546.2s, 24 samples, frame std 15.7, errors 0
libai: total 480.1s, 24 samples, frame std 16.1, errors 0
zhuyz: total 519.3s, 24 samples, frame std 16.4, errors 0
jiang: total 593.0s, 24 samples, frame std 18.6, errors 0
```

## 3. `python3 tools/check_outputs.py --require`

exit 0 · 13 s

```
mao: 648.9s (10.8 min) 1920x1080@30/1 h264+aac -16.3 LUFS, frame means 28-116
zhuge: 537.8s (9.0 min) 1920x1080@30/1 h264+aac -16.0 LUFS, frame means 75-113
sushi: 546.2s (9.1 min) 1920x1080@30/1 h264+aac -16.8 LUFS, frame means 26-106
libai: 480.1s (8.0 min) 1920x1080@30/1 h264+aac -16.3 LUFS, frame means 23-129
zhuyz: 519.3s (8.7 min) 1920x1080@30/1 h264+aac -16.1 LUFS, frame means 70-101
jiang: 593.0s (9.9 min) 1920x1080@30/1 h264+aac -16.4 LUFS, frame means 21-160
```

## 4. `python3 tools/mutation_checks.py`

exit 0 · 30 s

```
| C3 | 苏轼第 41 步只显示 0.1 s | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[sushi]; tests/test_timeline.py::test_every_half_year_step_is_shown[sushi] |
| C5 | 诸葛亮首个里程碑只停 1 s | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[zhuge]; tests/test_timeline.py::test_milestones_hold[zhuge] |
| C5 | 庐山会议停留点改到杭州 | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[mao]; tests/test_timeline.py::test_milestone_stays_at_its_place[mao] |
| C6 | 苏轼第 4 段配乐前移出 5 s 空档 | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[sushi]; tests/test_timeline.py::test_music_covers_film_by_stage[sushi] |
| C7 | 毛泽东第 5、6 段旁白重叠 2 s | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[mao]; tests/test_timeline.py::test_narration_no_overlap_and_inside[mao] |
| C7 | 苏轼 6 段里程碑旁白改记为概述 | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[sushi]; tests/test_timeline.py::test_narration_balance[sushi] |
| C7 | 诸葛亮第 11、12 条字幕重叠 | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[zhuge]; tests/test_timeline.py::test_narration_no_overlap_and_inside[zhuge] |
| C3 | 去掉周岁下限（出生时 −1 岁） | red ✔ | tests/test_js.py::test_ages_never_negative[mao]; tests/test_js.py::test_ages_never_negative[jiang]; tests/test_js.py::test_age_and_era_anchors |
| C8 | 片尾里程按图外代理点累计 | red ✔ | tests/test_js.py::test_mao_km_counts_real_moscow_distance |
| C3 | 蒋介石 1949H2 后仍用民国纪年 | red ✔ | tests/test_js.py::test_age_and_era_anchors_second_batch |
| C3 | 李白天宝三载不改称“载” | red ✔ | tests/test_js.py::test_age_and_era_anchors_second_batch; tests/test_js.py::test_era_edges_second_batch |
| C3 | 朱元璋龙凤纪年晚一年 | red ✔ | tests/test_js.py::test_age_and_era_anchors_second_batch |
| C1 | 删除李白 750H1 一步 | red ✔ | tests/test_data.py::test_steps_cover_life_without_gaps[libai]; tests/test_timeline.py::test_timeline_is_fresh[libai]; tests/test_timeline.py::test_every_half_year_step_is_shown[libai] |
| C1 | 溪口经度改为 10° | red ✔ | tests/test_data.py::test_places_resolve_with_coords[jiang]; tests/test_timeline.py::test_timeline_is_fresh[jiang] |
| C7 | 朱元璋旁白改了文本未重新配音 | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[zhuyz]; tests/test_timeline.py::test_narration_audio_matches_script[zhuyz] |
```

## 5. `python3 tools/audio_report.py libai`

exit 0 · 0 s

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

## 6. `python3 tools/audio_report.py zhuyz`

exit 0 · 1 s

```
stage     mood                t0      t1    dBFS  centroid  onsets/s
title     title              0.0    21.3   -20.1       632      2.49
st1       elegy             21.3    83.4   -18.7      1013      1.27
st2       wander            83.4   118.9   -15.8      1489      3.13
st3       tension          118.9   154.8   -17.1       946      2.84
st4       aspire           154.8   206.5   -16.4      1339      2.17
st5       battle           206.5   342.4   -14.7       763      2.91
st6       grand            342.4   380.6   -16.1      1310      0.97
st7       contemplative    380.6   433.2   -18.7       478      1.26
st8       elegy            433.2   497.1   -18.5       886      1.46
outro     outro            497.1   519.3   -16.9      1172      2.29
silent boundaries: none
peak 0.846 nan False
```

## 7. `python3 tools/audio_report.py jiang`

exit 0 · 0 s

```
stage     mood                t0      t1    dBFS  centroid  onsets/s
title     title              0.0    16.2   -22.6       640      2.78
st1       pastoral          16.2    52.6   -18.7      1581      2.88
st2       aspire            52.6   115.3   -18.7      1250      2.17
st3       wander           115.3   183.4   -18.8      1509      3.04
st4       march            183.4   302.9   -18.1      2171      2.98
st5       tension          302.9   380.8   -19.1       917       2.5
st6       epic             380.8   466.9   -17.6      1147      0.77
st7       battle           466.9   521.8   -16.9       739      2.79
st8       elegy            521.8   570.4   -20.7       965      1.24
outro     outro            570.4   593.0   -19.3      1161      2.61
silent boundaries: none
peak 0.893 nan False
```

- finished: 2026-10-06T10:56:44Z
- result: passed
