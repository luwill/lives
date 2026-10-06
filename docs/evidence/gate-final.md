# Machine gate — final

- commit: 1bc5029
- working tree: clean (the gate refuses to start otherwise)
- recorded by: /Users/louwill/.claude/skills/autopilot/scripts/run-gate.sh (sha256 f7df72490cb4216d)
- started: 2026-10-06T01:14:18Z
- workdir: /Users/louwill/Vibing/daily-test/opus5.5-video-test/lives

## 1. `python3 -m pytest -q tests`

exit 0 · 1 s

```
................................................                         [100%]Running teardown with pytest sessionfinish...

48 passed in 0.21s
```

## 2. `node tools/smoke.mjs`

exit 0 · 4 s

```
mao: total 648.9s, 24 samples, frame std 30.8, errors 0
zhuge: total 537.8s, 24 samples, frame std 14.0, errors 0
sushi: total 546.2s, 24 samples, frame std 15.7, errors 0
```

## 3. `python3 tools/check_outputs.py --require`

exit 0 · 7 s

```
mao: 648.9s (10.8 min) 1920x1080@30/1 h264+aac -16.3 LUFS, frame means 28-116
zhuge: 537.8s (9.0 min) 1920x1080@30/1 h264+aac -16.0 LUFS, frame means 75-113
sushi: 546.2s (9.1 min) 1920x1080@30/1 h264+aac -16.8 LUFS, frame means 26-106
```

## 4. `python3 tools/mutation_checks.py docs/evidence/mutations.md`

exit 0 · 17 s

```
| 准则 | 注入的缺陷 | pytest 结果 | 变红的测试 |
|---|---|---|---|
| — | 未注入缺陷（对照） | green | — |
| C1 | 删除毛泽东 1935H1 一步 | red ✔ | tests/test_data.py::test_steps_cover_life_without_gaps[mao]; tests/test_timeline.py::test_timeline_is_fresh[mao]; tests/test_timeline.py::test_every_half_year_step_is_shown[mao] |
| C1 | 黄州经度改为 10° | red ✔ | tests/test_data.py::test_places_resolve_with_coords[sushi]; tests/test_timeline.py::test_timeline_is_fresh[sushi] |
| C2 | 五丈原星落只留一个来源 | red ✔ | tests/test_data.py::test_milestones[zhuge] |
| C3 | 苏轼第 41 步只显示 0.1 s | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[sushi]; tests/test_timeline.py::test_every_half_year_step_is_shown[sushi] |
| C5 | 诸葛亮首个里程碑只停 1 s | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[zhuge]; tests/test_timeline.py::test_milestones_hold[zhuge] |
| C5 | 庐山会议停留点改到杭州 | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[mao]; tests/test_timeline.py::test_milestone_stays_at_its_place[mao] |
| C6 | 苏轼第 4 段配乐前移出 5 s 空档 | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[sushi]; tests/test_timeline.py::test_music_covers_film_by_stage[sushi] |
| C7 | 毛泽东第 5、6 段旁白重叠 2 s | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[mao]; tests/test_timeline.py::test_narration_no_overlap_and_inside[mao] |
| C7 | 苏轼 6 段里程碑旁白改记为概述 | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[sushi]; tests/test_timeline.py::test_narration_balance[sushi] |
| C7 | 诸葛亮第 11、12 条字幕重叠 | red ✔ | tests/test_timeline.py::test_timeline_is_fresh[zhuge]; tests/test_timeline.py::test_narration_no_overlap_and_inside[zhuge] |
| C3 | 去掉周岁下限（出生时 −1 岁） | red ✔ | tests/test_js.py::test_ages_never_negative[mao]; tests/test_js.py::test_age_and_era_anchors |
| C8 | 片尾里程按图外代理点累计 | red ✔ | tests/test_js.py::test_mao_km_counts_real_moscow_distance |
```

- note: the gate itself changed tracked files:

```
 M docs/evidence/gate-final.md
```

- finished: 2026-10-06T01:14:47Z
- result: passed
