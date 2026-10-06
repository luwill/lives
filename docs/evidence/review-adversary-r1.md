# Adversarial review r1: diff 8d63ddd..23f70a6

- reviewer: adversary (read-only), 2026-10-06
- scope: tools/build_timeline.py, src/{journey,camera,mapfx,hud,main,people}.js, narration/*/script.json against data/*/steps.json, tests/, contract red lines
- machine gate at 23f70a6: `python3 -m pytest -q tests` gave 42 passed. `node tools/smoke.mjs` ran with 0 errors on all three pages.
- Probes were read-only. Copies of the modules ran from the scratchpad: camera sampling, journey km totals and people.js labels. One Playwright `renderAt` probe read back the HUD text.

## Findings

### B1 (blocking): Mao's birth card and HUD show "-1 岁"
- **File:** src/people.js:23-26 (`zhousui`), used by src/hud.js:85 and :118
- **What goes wrong:** For 1893H2 the half-year midpoint is 10/1, which is before the birthday 12/26. The code computes `1893 - 1893 - 1` and gets −1. The first milestone of the film therefore shows a negative age for about 16 s (t≈27–43 s). This breaks C3, which requires the HUD to show 「…· 年龄」.
- **Reproduction:** Probe `renderAt(32)` on `?who=mao`. It returns `.age = "-1 岁"` and `.mscard .when = "1893 年下半年 · 清 · 光绪十九年 · -1 岁"`. The stills sheet skips 1893, which is why nobody saw it.
- **Fix:** Clamp the age to ≥0 and show the birth half-year as "出生" or "0 岁". Add a test that `age(y,h) >= 0` for every step of every person.

### B2 (blocking for the C7 claim): the test does not measure what C7 says
- **File:** tests/test_timeline.py:59-64
- **What goes wrong:** C7 is frozen as 「非里程碑旁白总时长占比 <40%」. The test measures only `span / total`, so the intro and outro, which are also non-milestone narration, drop out of the numerator. The docstring quietly redefines them as part of the milestone body.
- **Reproduction:** Measured from src/*/timeline.json:

  | who | span ratio (what the test checks) | all non-milestone narration (literal C7) |
  |---|---|---|
  | mao | 0.384 | **0.445** |
  | zhuge | 0.275 | 0.354 |
  | sushi | 0.369 | **0.418** |

  By the frozen wording, Mao and Su Shi fail C7. Mao's span ratio is also within 1.6 points of the test's own limit.
- **Fix:** Either test `(total - milestone) / total < 0.40` and trim the span or intro/outro text, or record in the ledger the decision to read C7 as span-only. A criterion that is frozen should not be reinterpreted silently.

### M1 (minor): the camera dives below milestone distance during the first chapter card
- **File:** src/camera.js:66-72
- **What goes wrong:** In the window `[chapters[0].t0, steps[0].t0)`, the 3.4 s first chapter card, `i = 0`. Step 0 is a milestone in all three films (the birth), so the milestone branch runs with `t < s.t0`. That makes `k = (t - s.t0)/(ms.t0 - s.t0)` negative, down to about −2, so `k*k` reaches about 4. The result is a large overshoot, plus a westward `CARD_SHIFT` because k is negative.
- **Reproduction:** Sample the camera at 0.5 s intervals.
  - Mao: 1234 → 811 → 370 → **201 → 195** → 236 → 300 → 368 → 418 → **435** → 413 → 366 → 316 → 286 km. It zooms in past MS_DIST (260), pulls back out, then zooms in again.
  - Zhuge and Su Shi do the same, with minimums of 193 km and 197 km.
- **Fix:** In `raw()`, return `first`/overview framing while `t < steps[0].t0`, or use `k = clamp01(...)`.

### M2 (minor): narration still carries text the fact-check fixes moved or rejected
The data and card fields were corrected, but the voice-over and burned-in subtitles were not.
- **narration/zhuge/script.json `m_228H1`:**
  - The narration says 「诸葛亮**斩**马谡以谢众」. F1 changed the subtitle to 「戮谡以谢众」, and factcheck-zhuge.md:28 notes that 《马谡传》 has 「谡下狱物故」. How Ma Su died is contested: 斩 (beheaded) versus 下狱 (died in prison). 「斩」 is the 《演义》 picture that F1 was blocking.
  - **Fix:** use 「戮谡以谢众」 or 「马谡下狱而死（一说被杀）」.
- **narration/zhuge/script.json `m_225H1`:**
  - The narration says 「经水路进入越巂」. This is the uncorrected 《华阳国志》 reading that factcheck-zhuge.md:26/58 flagged. The data event was fixed to 「由水路至安上，转陆入越巂」, but the narration was not.
- **narration/sushi/script.json `m_1061H2`:**
  - The narration says 「与弟弟在郑州西门分别。他写道：人生到处知何似……」. F4 (blocking) moved the 郑州 parting and the 渑池 poem to 1062H1, because the parting was on 1062-01-02.
  - In the film, the 1061H2 card sits at 汴京 (places = ['kaifeng']) while the voice describes 郑州 and 渑池 in the next half-year.
  - **Fix:** say 「次年初…」 or move the sentence into the `p_1062` span.

### M3 (minor): age and era labels contradict the narration on two cards
- **Su Shi 1037H1:**
  - The birth card reads `1037 年上半年 · 北宋 · 景祐四年 · 虚岁 2`, confirmed by the probe at t=28.
  - The narration says he was born on 景祐三年十二月十九日. At birth he was 虚岁 1 under D11's convention.
  - **Fix:** special-case the birth step, or compute the age from the step's start rather than its end.
- **Zhuge 221H1 (刘备称帝·拜丞相):**
  - `era(221,1)` gives `东汉 · 建安二十六年` (people.js:47 starts 章武 at 221H2).
  - The card's own subtitle says 「章武元年」, and 东汉 had already ended in 220.
  - **Fix:** start 章武 at idx(221,1). The 4月 accession is a 3/3 tie, so the tie can go to the event. Alternatively, show 「蜀汉」 from 221.
- **narration/sushi `p_1037`:**
  - 「十八岁，娶青神王弗」 is wrong. In 1054 Su Shi was 虚岁 19 (17 周岁), and the usual account is 「十九岁」.
  - **Fix:** change it to 十九岁.

### M4 (minor): the off-map Moscow proxy understates the distance total and puts the label in a different place
- **File:** src/journey.js:11-17, 33; src/hud.js:64; src/mapfx.js:84-89
- **What goes wrong:**
  - The trail, `kmAt` and the end-card total use the proxy points, not Moscow. Mao's end card reads **120,661 km (直线距离累计)**, but the real straight-line sum over the same places is **141,415 km**, about 15% understated.
  - The proxy depends on `lastIn`:
    - 1949H2 and 1950H1 are projected from 满洲里 to (105.1, 50.5).
    - 1957H2 is projected from 北京 to (106.2, 42.0), about 950 km away.
  - The 「莫斯科 ➚」 label stays at the first proxy. During the 1957 visit, the trail and current dot end about 950 km from the label, near the 42°N line.
- **Fix:** compute `cum`/`totalKm` from real coordinates. Anchor every proxy to one fixed point, e.g. always from 北京 or always from 满洲里, so the label and trail agree.

### M5 (minor): two tests cannot catch their target regressions
- **tests/test_timeline.py:117-128 (`test_milestone_stays_at_its_place`):**
  - It re-encodes the implementation constant (`>= 8` ≡ `TRAVEL_PLACE_SET_MIN`) and re-derives `split` the same way the builder does.
  - Change the constant in both places, or misplace the camera for a travel milestone, and it still passes.
  - For travel milestones with a `place` (1935H1 zunyi, 1935H2 wuqi), the camera finishes zoomed on the **last** place (两河口, 瓦窑堡), not on the place the card and star name. Nothing checks this.
- **tests/test_timeline.py:39-45 (`test_milestones_hold`):**
  - It checks `ms.t1 - ms.t0 ≥ 3`. For travel milestones that window includes the whole moving phase, so the test proves nothing about C5's 「镜头推近…停留 ≥3 s」.
  - Today the post-arrival hold is 3.30–6.38 s (min: sushi 1100H2 3.30 s, mao 1948H1 3.36 s). The builder only guarantees `t + move + 1.5`, so the hold could legally fall to 1.5 s.
  - **Fix:** assert `ms.t1 - (t0 + move) ≥ 3` for travel milestones, and raise the builder floor from 1.5 to 3.0.
- **tests/test_timeline.py:55-56:**
  - It checks only that subtitle starts are monotonic, not that subtitles do not overlap.
  - Mao has 22 overlapping subtitles (`end + 0.15` pad, max 0.057 s). `hud.js:150` picks the first match, so the next line is delayed by up to ~0.16 s. This is cosmetic.

## Checked and found OK
- **build_timeline.py:**
  - No zero or negative step durations; the minimum step is 0.55 s.
  - The `ms`/`after` windows stay inside each step.
  - Narration segments do not overlap.
  - `split` is always ≥1, and `place ∈ places` is now enforced by test_data.py:75.
  - Spans are validated against milestones and stage boundaries.
  - tts.json words match the script text exactly for every segment, so the TTS is not stale.
- **`renderAt(t)` is deterministic:**
  - The HUD/marker caches (`lastStep`, `lastMs`, `lastCh`, `dataset.k`) are keyed and idempotent.
  - The camera is a precomputed lookup, and two calls with the same t gave identical output.
- **Mao narration:**
  - Checked line by line (dates, places, quotes, the 1981 resolution wording, 「七十二岁」 under D11, 167 half-years). No contradictions with steps.json.
  - The politically sensitive passages (庐山, 文革, 林彪, 历史决议) follow the official wording.
  - Small compressions:
    - 「会后…任中共湘区委员会书记」: 湘区委 dates from 1922.
    - 「与斯大林会谈两个月」: the stay lasted two months, not the talks.
    - 「一九六六年夏，他发动了文化大革命」: the official start is May 1966.
- **Zhuge narration:**
  - 《演义》 material is explicitly marked as fiction (草船借箭, 借东风, 七擒孟获).
  - 卤城 is hedged.
  - 隆中对 paraphrase 「荆州与益州，正是用武之地」: the source calls only 荆州 「用武之国」. This is a nit.
- **Red lines:**
  - make_texture.py and labels.json contain no admin or boundary layers, and the end card disclaims boundaries.
  - No audio or video media are tracked in git, and music/score.py only synthesizes.
  - There is no publish step.

## Verdict
**needs-attention**: B1 (negative age on screen) and B2 (the C7 evidence does not measure the frozen criterion) must be resolved before C3 and C7 can be marked proven. M1–M5 are recommended fixes.
