# 三人人生轨迹视频（第二批）：李白 · 朱元璋 · 蒋介石

- status: flying <!-- planned → flying → landed -->
- workspace: lives/ (git, autopilot/three-more-lives，从 autopilot/three-lives 的 200f78a 分出)
- base: 200f78a
- contract: docs/autopilot.md

## Goal

> 按照同样的方式，新增李白、朱元璋、蒋介石三个人的人生轨迹。

“同样的方式”指上一轮（`docs/runs/2026-10-05-three-lives.md`）的五项要求：半年一步、结合史料；在中国 3D 地形上展开并标注地名；里程碑高亮；按人生阶段配不同的 BGM；讲解详略得当。流程沿用上一轮：数据规范 → 并行史料代理 → 独立核查 → 旁白驱动时间轴 → 渲染 → 审片 → 变异测试。

## Acceptance criteria

Frozen at takeoff. A run changes `status` and `evidence`, never the criterion.

| id | criterion | proven by | status | evidence |
|---|---|---|---|---|
| C1 | 每人一份半年粒度轨迹数据 `data/<who>/steps.json`，从出生所在半年到去世所在半年连续无缺：李白 701H1–762H2（生月不详，记为 inferred；出生地有争议，取碎叶，并在 contested 中列出“绵州昌隆”说）；朱元璋 1328H2–1398H1；蒋介石 1887H2–1975H1。每步含地点（古名+今名+坐标）、事件、来源、可信度 | pytest `test_data.py`（六人）；变异测试：删一步会变红 | open | |
| C2 | 史料核验：李白、朱元璋各 ≥10 个里程碑，蒋介石 ≥15 个，每个都有 ≥2 个独立来源；有争议处列入 `contested`，旁白用审慎措辞 | 独立核查报告 `docs/evidence/factcheck-<who>.md`；分歧写入台账 | open | |
| C3 | 视频逐个半年步推进：HUD 显示公元年、上/下半年、纪年与年龄（李白、朱元璋按虚岁，蒋介石按周岁），每步在画面中出现 ≥0.4 s，轨迹线随时间生长 | pytest `test_timeline.py`、`test_js.py`（年龄/纪年锚点）；抽样截图 | open | |
| C4 | 轨迹在中国 3D 地形上展开，标注山河与人物到过的地点（古名与今名）；图外地点（如东京、莫斯科、开罗）用地图边缘代理点，片尾里程仍按真实坐标累计 | 截图拼板（每人 ≥6 张，取自最终 mp4）；`smoke.mjs` 六人无报错；`test_js.py` 代理点测试 | open | |
| C5 | 里程碑高亮：每个里程碑有镜头推近、光环、标题卡，停留 ≥3 s，停在事件发生地 | pytest（停留时长、停留地点）；截图 | open | |
| C6 | 分阶段 BGM：每人 ≥4 个人生阶段，情绪依性格与经历设定（`music/<who>_stages.json`），阶段间无空档，全部原创合成 | pytest（覆盖全片）；`docs/evidence/audio-<who>.md` 分阶段响度/频谱 | open | |
| C7 | 讲解详略得当：每个里程碑有旁白；非里程碑旁白（概述+片头+片尾）占比 <40%；旁白、字幕都不重叠；字幕烧录 | pytest；变异测试 | open | |
| C8 | 交付 3 个 mp4：1920×1080、30 fps、H.264+AAC，时长在目标区间（李白 7–10 min，朱元璋 8–11 min，蒋介石 9–13 min），响度 −16±1.5 LUFS，无黑帧 | `check_outputs.py --require` | open | |
| C9 | 不破坏第一批：毛泽东、诸葛亮、苏轼的数据和时间轴不变，六人测试、smoke 全部通过；三部旧成片不重渲染、不改动 | 机器门禁；`git diff 200f78a -- data/{mao,zhuge,sushi} src/{mao,zhuge,sushi}` 为空 | open | |

`status` is `open`, `proven` or `parked`.

## Stages

1. [ ] 骨架：建分支；测试、工具、people.js 扩展到六人（新人数据先留空，测试先红）— 无
2. [ ] 史料数据（三人并行子代理）+ 独立事实核查 — owns C1, C2
3. [ ] 解说词、TTS、时间轴 — owns C3, C5, C7
4. [ ] 引擎适配：纪年/年龄、时代政权注记、图外代理点、新增地名标注 — owns C3, C4, C5
5. [ ] 配乐：三人分阶段情绪设计与合成 — owns C6
6. [ ] 渲染、混音、总装与审片 — owns C8
7. [ ] 落地：整体评审、变异测试、验收清单 — owns C9

## Ledger

### Decisions

| id | stage | chose | rejected | wrong if |
|---|---|---|---|---|
| D1 | 起飞 | 人类选定：配音 李白=云希 -4%/+0Hz，朱元璋=云健 -8%/-5Hz，蒋介石=云扬 -6%/-3Hz；蒋介石措辞采用大陆通行史学表述，1949H2 起 HUD 不用民国纪年（只显示公元年）；允许删除第一批的逐帧 JPG（18 GB） | 蒋介石用台湾口音云哲；两岸并陈；放宽磁盘上限 | — （人类决定） |
| D2 | 起飞 | 合约修订一处（人类确认）：每轮新建分支 `autopilot/<slug>` | 继续在 three-lives 分支上做 | — |
| D3 | 1 | 纪年：李白 武周（大足、长安）→ 唐，天宝三载至至德二载称“载”；朱元璋 1355—1366 显示“龙凤X年 · 元至正X年”，1367 吴元年，1368 起洪武；时代政权注记新增可选 `to`（如陈友谅 1360—1363） | 只显示元朝年号 | 朱元璋集团奉龙凤年号的起止年有误（以《明史·太祖本纪》为准，1355 二月韩林儿称帝改元龙凤） |
| D4 | 1 | 新增地名注记 8 个（台湾海峡、中央山脉、庐山、峨眉山、泰山、巢湖、洪泽湖、伊塞克湖），写在共用的 labels.json | 每人单独一份注记 | 新注记出现在第一批成片里——第一批不重渲染（C9），只在将来重渲染时出现 |
| D5 | 2 | 研究代理用了第一轮遗留的 `lunar_python`（P1，第一轮停放项）做农历换算，没有新装包 | 让代理不用它、手工查历表 | 用户决定卸载 lunar_python：只影响 `data/_build/*_lunar.py` 重新生成，不影响已提交的数据和成片 |
| D6 | 5 | 远途里程碑卡片显示“起点 → 事件地”（原为“起点 → 终点”）；星标落在 HUD 区时隐藏 | 保持原样 | 审片时看到蒋介石 1923H2 卡片写“广州 → 奉化溪口”，没有体现莫斯科；朱元璋 1393 年号块被星标压住 |

### Review findings

| id | round | reviewer | finding | status | note |
|---|---|---|---|---|---|

### Parked

| id | needs | exact action | unblocks | verify afterward |
|---|---|---|---|---|

### Not verified

## Acceptance walk

| # | where | do | should see |
|---|---|---|---|
