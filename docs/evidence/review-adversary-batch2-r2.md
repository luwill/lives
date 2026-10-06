# Adversarial review — batch 2, round 2 (fix diff)

Reviewer: adversary (stand-in for the cross-model Codex review). Range: `git diff 3420567 b9e5103`. Date: 2026-10-06.
Gate re-run: `python3 -m pytest -q tests` → 99 passed. I did not touch out/, render.mjs or mutation_checks.py. I ran the mutants on a scratch copy of src/.

No blocking findings.

## Confirmed fixed

- **A1:** The 50 km rule changes only one travel card across all six lives: jiang 1949H2 (草山 → 台北, 13 km). That card now reads “台北 · 今台湾台北市”.
- **hud.js import:** hud.js already imported mapfx.js, which imports engine.js, so the new engine.js import adds no new dependency.
- **A2:** The new wording matches data 1938H2, which ends in 重庆 in December.
- **A6:** The narration now quotes “酒隐安陆，蹉跎十年”, so it no longer clashes with the card's 三霜.
- **A7:** “入怀” is removed.
- **A9:** Region `to` is inclusive. 元 now shows through 1368H1. 张士诚 shows through 1367H2. 北元 starts at 1368H2, so there is no gap.
- **A10 core mutants:** These are now killed: `y<1354`, 至德 without 载, `y<1908` in the jiang era, and `y<1368` for 吴元年.
- **A12:** The jiang duplicates are removed (70 → 67).
- **A14:** Fixed.
- **Rewritten narration:** 727H2 “约在此时” matches data 728H1 (安旗). 746H2, 753H2 and 1364H1 are now hedged.
- **TTS hash test:** It uses the same formula as tools/tts.py, and `test_timeline_is_fresh` already ties timeline.json to tts.json.

## Findings

| id | severity | file:line | finding | how to reproduce |
|---|---|---|---|---|
| B1 | minor | src/hud.js:64-65 | Counting places by rounded coordinate wrongly merges distinct places that share a county-level fallback coordinate. Mao: 梁家岔/朱官寨/神泉堡 are three villages, all `confidence: low`, “取所属县/市（佳县）”, now counted as 1. 文家市 is merged into 浏阳. Zhuyz: 皇觉寺 is merged into 孤庄村. Counts: mao 129→125 (only 北京/北平 is a real merge), zhuyz 33→32 (doubtful), zhuge 33→32 (correct), jiang 70→67 (correct). The change also quietly alters the first-batch mao and zhuge end cards on their next render. The code comment says “同一地点改名”, but the code does not check for that. Suggested fix: an explicit alias field in places.json (e.g. `"same_as"`) instead of coordinate equality. | In src/, call `buildJourney` for each person and compare `new Set(arrivals.map(a=>a.key)).size` with the rounded-coordinate set. Then check `data/mao/places.json` liangjiacha/zhuguanzhai/shenquanbao/wenjiashi. |
| B2 | minor | data/jiang/steps.json 1912H1 `event` and `contested[刺杀陶成章].adopted`, vs narration/jiang/script.json `p_1912H1` | A4 is fixed in one of the three texts only. The narration now says “一般认为由他主谋”. The event bar on screen at the same time still says “1月14日在上海刺杀光复会领袖陶成章”, and `adopted` still says “认定蒋为刺客之一”. Voice, bar and data now disagree on his role. | Read the 1912H1 event and contested entry next to `p_1912H1`. |
| B3 | minor | data/zhuyz/steps.json 1353H1 `event` | A3 is fixed in the narration only. The 1353H1 event bar still reads “还乡募兵七百人，徐达、汤和来归”. Per 《明史·汤和传》, 汤和 joined 郭子兴 earlier (the narration's own 1352H1 line agrees). | `python3 -c` print zhuyz 1353H1 event. |
| B4 | minor | narration/libai/script.json `intro` | A5 (intro) was reworded, not hedged. “生于西域” still states one side of the contested birthplace (碎叶 vs 绵州/蜀) flatly. This may be acceptable, because contested.adopted says “按任务约定采碎叶为主说”. If so, it should be recorded as rejected-with-reason, not as fixed. | Read the intro against `contested[出生地]`. |
| B5 | minor | tests/test_js.py:79-84 | `test_era_edges_second_batch` still lets these mutants survive. (a) 乾元 start `idx(758,1)`→`idx(758,2)`: 758H1 shows “唐 · 至德三载”. (b) `e[1] < 705`→`e[1] < 701`: 701H1 shows “唐 · 大足元年” instead of 武周. (c) 宝应 start moved: no 761/762 anchor (A8 territory). | Copy src/*.js to a temp dir, apply each replacement to people.js, and evaluate the test's 8 assertions with `node --input-type=module`. (a), (b) and (c) all pass. |
| B6 | minor | docs/runs/2026-10-06-three-more-lives.md “Review findings” | Round-1 findings A1–A15 have no rows in the run record. Only F1–F16 are listed. Several have no disposition. **A8:** unchanged (`PEOPLE.libai.era(761,2)` is still “唐 · 上元二年”). **A11:** still open. The new 50 km rule and the coordinate dedupe add two more untested hud.js behaviours: no test imports hud.js, so reverting the whole hud.js hunk keeps 99 green. **A13:** not addressed. **A15:** informational. | `grep -n 'A[0-9]' docs/runs/2026-10-06-three-more-lives.md` → nothing. `grep -rn hud tests/` → nothing. |
| B7 | minor | tools/render_all.sh:18-19 | `render_commit.txt` records HEAD and the dirty state **after** frames and assembly finish, not when the render started. A commit made during a long render, like b9e5103 landing while out/ is rendering now, stamps the video with a commit its frames did not come from. `git diff --quiet HEAD` also ignores untracked files. | Read the script. Capture `git rev-parse` and the dirty check before `build_timeline.py` and write the result at the end. |
| B8 | minor | tests/test_timeline.py:11 | `import tts` runs `import edge_tts` at module level (tools/tts.py:14). Without edge_tts installed, the whole test_timeline.py module fails at collection, not just the new test. Suggested fix: move `VOICES` and the hash function into an import-free module. | `python3 -c "import sys;sys.modules['edge_tts']=None;sys.path.insert(0,'tools');import tts"` → ImportError. |
| B9 | minor | tools/contact_sheet.sh:9-11 | `N=floor(total/30)`, but `fps=1/30` emits a frame at t=0, so about N+1 frames come out. When N is a multiple of 4 the grid is full and the last frame is dropped. For libai (480.05 s): N=16, a 4×4 grid, and the t=480 end-card frame is lost. Probable; I did not run ffmpeg because the CPU is busy. | After the render: `ffmpeg -i 李白_人生轨迹.mp4 -vf fps=1/30 -f null - 2>&1 \| grep frame=` → 17 vs 16 cells. |
