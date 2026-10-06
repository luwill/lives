# Adversarial review r2: fix diff 23f70a6..fc89e5b

- reviewer: adversary (read-only), 2026-10-06
- scope: `git diff 23f70a6 fc89e5b`, checked against review-adversary-r1.md (B1, B2, M1–M5) and run-record rows R1–R13
- HEAD at review time: 0ccacdd. It adds only docs and evidence over fc89e5b; none of the reviewed code changed.
- machine gate: `python3 -m pytest -q tests` gave **47 passed**.
- The committed `src/*/timeline.json` equals a fresh `tools/build_timeline.build(who)` for all three people.
- For every segment, the tts.json words match script.json once punctuation is stripped, so the timeline is not stale.

Probes (all read-only):
- Node imports of `src/journey.js`, `src/camera.js` and `src/people.js` from the scratchpad.
- A rebuild of the timelines in Python.
- Reads of the subtitle, hold and narration-ratio values from the timelines.

## Round-1 findings: are they resolved?

| r1 | run-record row | status | evidence |
|---|---|---|---|
| B1: "-1 岁" at birth | R5 | **resolved** | `zhousui` now applies `Math.max(0, …)` (people.js:25), so `age(1893,2)` = "0 岁" and `age(1894,1)` = "0 岁". `test_ages_never_negative` covers every step of every person and turns red under mutation (mutations.md). |
| B2: C7 measured span-only | R6 | **resolved** | test_timeline.py:63-69 now measures `(span+intro+outro)/total`. Measured values: mao **0.341**, zhuge 0.352, sushi **0.378**. Su Shi has 2.2 points of headroom. |
| M1: camera dives during the first chapter card | R7 | **resolved** | camera.js:69 clamps k to ≥0. Mao's distance from the intro to the end of the 1893H2 hold now falls steadily (… 1086 → 754 → 623 → 566 → 538 → 522 → 506 → 484 → 447 → 392 → 334 → 295 → 276 → 264 → 260). Zhuge and Su Shi also have no overshoot and no westward shift. |
| M2: narration not updated with the fact-check | R8 | **resolved** | zhuge m_225H1 now reads 「由水路至安上，转入越巂」. m_228H1 now reads 「马谡下狱而死，诸葛亮为之流涕」, which follows 《马谡传》 「谡下狱物故，亮为之流涕」. In Su Shi's narration, 郑州 and 渑池 moved to `p_1062` as 「次年初…」. The new 1061H2 claim 「只有吴育与他」 is backed by the 《宋史》 quote in steps.json. |
| M3: birth-card era/age, 章武, 十八岁 | R9 | **resolved** | The HUD and card now show `北宋 · 景祐三年 · 虚岁 1` for step 0 (hud.js:82,85,118-119). `era(221,1)` = `蜀汉 · 章武元年`, and the narration now says 十九岁. |
| M4: Moscow proxy | R10 | **resolved (km and anchor)** | `totalKm` = **141,415**, which matches the real straight-line sum. The drawn geometry is 121,262 km, so the end card is no longer understated. Every proxy is now anchored at 北京, so the 1949, 1950 and 1957 trips end at the same point as the 「莫斯科 ➚」 label: moscow → (106.20, 41.95). The test turns red under mutation. *A new side effect is listed as N1.* |
| M5a: test_milestone_stays_at_its_place restates the constant | R12 | dispute accepted | mutations.md shows the test turning red when the 庐山 milestone place is moved to 杭州. Treating "≥8 places" as part of the spec is a reasonable position. |
| M5b: travel hold included the moving phase | R11 | **resolved** | The builder floor is now `t+move+MS_MIN_HOLD`, and the test checks `ms.t1-(t0+move) ≥ 3`. The current minimum is 3.30 s (sushi 1100H2). |
| M5c: subtitles overlap | R11 | **resolved in the data, partly on screen** | The `subs` data no longer overlaps. However, hud.js:151 still shows each line until `b + 0.1`, so the displayed windows still overlap. See N2. |
| R1–R4 | — | not re-audited in depth | The ≥2-sources test exists (test_data.py:77) and turns red under mutation. Zhuge 181H1 is now `inferred`. audio-*.md and mutations.md are present. gate-final.md is untracked in the working tree. |
| R13 | — | still open by choice | No change. |

## New problems introduced by the fixes

### N1 (minor): the Beijing-anchored Moscow proxy sits inside Inner Mongolia, so the 1949 trail turns back south-west from 满洲里
- **File:** src/journey.js:11-17
- **What goes wrong:**
  - With `ANCHOR = 北京` and `OFF_KM = 900`, both 「莫斯科 ➚」 (106.20, 41.95) and 「列宁格勒 ➚」 (106.31, 42.25) land about 50 km south of the Sino-Mongolian border, in western Inner Mongolia, well inside MAP_BOX.
  - 1949H2's route is 北京→沈阳→哈尔滨→满洲里→moscow. The trail now runs about 1,200 km **south-west** from 满洲里 back across Inner Mongolia, although Moscow lies to the west-north-west.
  - 1950H1 then retraces that line back to 满洲里.
  - The old `lastIn` anchor put the 1949/50 proxy west of 满洲里, at (105.1, 50.5) in Mongolia. That location was more plausible and was dropped as a side effect.
  - The label is placed inside Chinese territory and reads 「莫斯科」. The film disclaims boundaries, so this is not a red line, but it looks wrong cartographically.
- **Reproduction:**

  ```
  node -e "import('./src/journey.js').then(j=>console.log(j.proxyOf({lon:37.6175,lat:55.7505})))"
  ```

  This prints `[106.20, 41.95]`. Watch `?who=mao` around 1949H2's `after` leg.
- **Suggested change:** Keep one fixed anchor, but extend the ray from 北京 until it reaches the MAP_BOX edge: lon 72 gives about (72, 48.8). Alternatively, put an explicit `proxy: [lon, lat]` for each off-map place in places.json, e.g. moscow ≈ (88, 49) to the west. Both options keep a single point for every trip, and from both 北京 and 满洲里 the trail then heads west or north-west. The km accounting already uses real coordinates, so it is unaffected.

### N2 (minor, cosmetic): subtitle de-overlap is defeated by the HUD's +0.1 s tail
- **File:** src/hud.js:151,154 together with tools/build_timeline.py:223-225
- **What goes wrong:**
  - The builder clips `a.end` to `b.start − 0.02`.
  - The HUD keeps a line visible while `t < b + 0.1`, and `find` takes the first match.
  - At every boundary with a gap under 0.1 s, the previous line therefore still wins for up to 0.08 s. The next line then pops in at about 50% opacity instead of fading in.
- **Reproduction:** Displayed windows `a[1]+0.1 > b[0]`:

  | who | overlaps | max |
  |---|---|---|
  | mao | 61 | 0.08 s |
  | zhuge | 38 | 0.08 s |
  | sushi | 15 | 0.077 s |

  Before the fix, Mao had 77 overlaps with a max of 0.157 s. That is better, but not gone. `test_narration_no_overlap_and_inside` checks only the data, so it cannot see this.
- **Suggested change:** In hud.js, use `findLast` or prefer the sub whose start is latest, or drop the `+0.1` tail and let the builder's pad do the job. Optionally, assert in the test that `a[1] + 0.1 <= b[0]` (the displayed window).

### N3 (minor, test gap): no test catches removing the birth-step HUD override
- **File:** tests/test_js.py:28-32; src/hud.js:82,85,118-119
- **What goes wrong:**
  - `test_age_and_era_anchors` asserts `s['birth'] == {'era': '北宋 · 景祐三年', 'age': '虚岁 1'}`. That restates the constant in people.js.
  - Delete the `i === 0 && person.birth ? …` branches in hud.js, and the birth card goes back to 「景祐四年 · 虚岁 2」 (r1 M3) with all 47 tests still green.
  - The B1 fix differs: it lives in `age()` itself and is covered.
- **Suggested change:** Add a Playwright or smoke assertion on `.mscard .when` at `renderAt(steps[0].ms.t0 + 1)` for sushi. Alternatively, move the override into a pure helper, e.g. `labelFor(person, i, y, h)` in people.js, use it from hud.js, and test that.

### N4 (nit): two small inconsistencies after the 章武 / 马谡 edits
- **蜀汉 label (src/people.js:51-53):**
  - At 221H1 the HUD now reads 「蜀汉 · 章武元年」.
  - The map's 「蜀 汉」 regional label still starts at `idx(221, 2)`, so for one half-year the HUD names a state the map does not show.
  - **Fix:** change `from` to `idx(221, 1)`.
- **zhuge 228H1 (data/zhuge/steps.json milestone.subtitle):**
  - The milestone card's subtitle says 「戮谡以谢众」 (killed), while the voice and burned-in subtitle now say 「马谡下狱而死」.
  - Both are sourced (《诸葛亮传》 vs 《马谡传》), but they appear on screen together.
  - **Fix:** either hedge the narration 「下狱而死（本传作“戮谡以谢众”）」 or change the card to 「谡下狱物故」.
- **data/zhuge/steps.json 181H1 `note`:**
  - The note repeats itself, with an 「。；」 join: the old note plus the new one.
  - It is not shown on screen.
  - **Fix:** keep only the second sentence.

## Trimmed narration: checked and found OK
- **Mao:**
  - I read all 19 edited segments. There are no broken sentences and no new factual errors.
  - 「次年写成《湖南农民运动考察报告》」 (span 1926H1–1927H1, report dated 1927-03): OK.
  - 「七千人大会上他作了自我批评」: OK.
  - 「一九七五年春回京后，他再没有离开北京」: OK.
  - The outro quotes the 1981 resolution's exact clause 「他的功绩是主要的，错误是次要的」.
  - 「一百六十七个半年」 is unchanged.
- **Su Shi:**
  - 「次年初，他在郑州西门与弟弟作别，过渑池写下…」 matches 1062H1 data.
  - 「年底携家西行赴任」 matches 「十一月中携家离京西行」 (lunar).
  - 「神宗去世后，他被起用，很快召回朝廷」 and 「元祐四年出知杭州」 are fine.
- **Zhuge:** both edits match the corrected data.

## Verdict
**approve**: every r1 blocking item (B1, B2) is fixed, and the tests that cover them turn red under mutation. M1–M5 are fixed or reasonably disputed. N1–N4 are minor or cosmetic and do not block C3, C5, C7 or C8. I recommend fixing N1 and N2 if another render pass happens.
