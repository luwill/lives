# Machine gate — landing

- commit: 8e033b7
- working tree: clean (the gate refuses to start otherwise)
- recorded by: /Users/louwill/.claude/skills/autopilot/scripts/run-gate.sh (sha256 f7df72490cb4216d)
- started: 2026-10-05T16:42:18Z
- workdir: /Users/louwill/Vibing/daily-test/opus5.5-video-test/lives

## 1. `python3 -m pytest -q tests`

exit 0 · 1 s

```
.......................................                                  [100%]Running teardown with pytest sessionfinish...

39 passed in 0.03s
```

## 2. `node tools/smoke.mjs`

exit 0 · 4 s

```
mao: total 715.3s, 24 samples, frame std 24.0, errors 0
zhuge: total 535.4s, 24 samples, frame std 14.0, errors 0
sushi: total 583.2s, 24 samples, frame std 15.7, errors 0
```

## 3. `python3 tools/check_outputs.py --require`

exit 0 · 8 s

```
mao: 715.3s (11.9 min) 1920x1080@30/1 h264+aac -16.2 LUFS, frame means 42-113
zhuge: 535.4s (8.9 min) 1920x1080@30/1 h264+aac -16.0 LUFS, frame means 75-111
sushi: 583.2s (9.7 min) 1920x1080@30/1 h264+aac -16.6 LUFS, frame means 71-114
```

- finished: 2026-10-05T16:42:31Z
- result: passed
