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
| C1 | 每人一份半年粒度轨迹数据 `data/<who>/steps.json`，从出生所在半年到去世所在半年连续无缺：李白 701H1–762H2（生月不详，记为 inferred；出生地有争议，取碎叶，并在 contested 中列出“绵州昌隆”说）；朱元璋 1328H2–1398H1；蒋介石 1887H2–1975H1。每步含地点（古名+今名+坐标）、事件、来源、可信度 | pytest `test_data.py`（六人）；变异测试：删一步会变红 | proven | `docs/evidence/gate-stage2.md`（pytest 92 项全过，六人）；mutations（同一门禁第 4 条）：删一步、坐标越界会变红。步数：李白 124、朱元璋 140、蒋介石 176；李白 701H1 标 inferred，出生地两说列入 contested |
| C2 | 史料核验：李白、朱元璋各 ≥10 个里程碑，蒋介石 ≥15 个，每个都有 ≥2 个独立来源；有争议处列入 `contested`，旁白用审慎措辞 | 独立核查报告 `docs/evidence/factcheck-<who>.md`；分歧写入台账 | proven | 里程碑：李白 16、朱元璋 16、蒋介石 20，每个 ≥2 来源（test_milestones）。三份独立核查：`docs/evidence/factcheck-{libai,zhuyz,jiang}.md`，共 52 个里程碑：通过 40、存疑 12、错误 0；“需要修改”逐条落实（F1–F16）。蒋介石核查为每个里程碑补了至少一个非维基来源 |
| C3 | 视频逐个半年步推进：HUD 显示公元年、上/下半年、纪年与年龄（李白、朱元璋按虚岁，蒋介石按周岁），每步在画面中出现 ≥0.4 s，轨迹线随时间生长 | pytest `test_timeline.py`、`test_js.py`（年龄/纪年锚点）；抽样截图 | proven | gate-stage2.md（test_every_half_year_step_is_shown；test_age_and_era_anchors_second_batch：李白虚岁/天宝称载、朱元璋龙凤/洪武、蒋介石周岁与 1949H2 后无民国纪年）；三个纪年变异都会变红；截图 `docs/evidence/stills/sheet_{libai,zhuyz,jiang}.jpg`（取自最终 mp4） |
| C4 | 轨迹在中国 3D 地形上展开，标注山河与人物到过的地点（古名与今名）；图外地点（如东京、莫斯科、开罗）用地图边缘代理点，片尾里程仍按真实坐标累计 | 截图拼板（每人 ≥6 张，取自最终 mp4）；`smoke.mjs` 六人无报错；`test_js.py` 代理点测试 | proven | `stills/sheet_{libai,zhuyz,jiang}.jpg`（每人 16–20 帧，取自最终 mp4）；gate-stage2.md 中 smoke 六人 0 报错、整帧非空白；test_offmap_proxy_points_east_and_west（东京→东缘、开罗→西缘）；新增地名注记 8 个（D4） |
| C5 | 里程碑高亮：每个里程碑有镜头推近、光环、标题卡，停留 ≥3 s，停在事件发生地 | pytest（停留时长、停留地点）；截图 | proven | gate-stage2.md（test_milestones_hold、test_milestone_stays_at_its_place 六人）；截图中卡片、光环、星标可见；远途卡片显示“起点 → 事件地”（D6） |
| C6 | 分阶段 BGM：每人 ≥4 个人生阶段，情绪依性格与经历设定（`music/<who>_stages.json`），阶段间无空档，全部原创合成 | pytest（覆盖全片）；`docs/evidence/audio-<who>.md` 分阶段响度/频谱 | proven | `music/{libai,zhuyz,jiang}_stages.json`（8/8/8 个阶段，李白 8 种情绪、朱元璋 7 种、蒋介石 8 种）；`docs/evidence/audio-{libai,zhuyz,jiang}.md`（分阶段 dBFS、频谱质心、起音密度，阶段边界无静音）；`stills/spectrogram_*.png`。审美未经试听 |
| C7 | 讲解详略得当：每个里程碑有旁白；非里程碑旁白（概述+片头+片尾）占比 <40%；旁白、字幕都不重叠；字幕烧录 | pytest；变异测试 | proven | gate-stage2.md（test_narration_balance：非里程碑旁白占比 李白 0.373、朱元璋 0.335、蒋介石 0.310；旁白、字幕不重叠） |
| C8 | 交付 3 个 mp4：1920×1080、30 fps、H.264+AAC，时长在目标区间（李白 7–10 min，朱元璋 8–11 min，蒋介石 9–13 min），响度 −16±1.5 LUFS，无黑帧 | `check_outputs.py --require` | proven | gate-stage2.md 中 check_outputs --require：李白 475.3 s（7.9 min）、朱元璋 513.0 s（8.6 min）、蒋介石 585.0 s（9.8 min），1920×1080@30、h264+aac、−16.3/−16.1/−16.4 LUFS，抽样无黑帧。朱元璋、蒋介石由 48187df 渲染，李白由 573fd1a 渲染（此后 src/ 与这三人的数据未变） |
| C9 | 不破坏第一批：毛泽东、诸葛亮、苏轼的数据和时间轴不变，六人测试、smoke 全部通过；三部旧成片不重渲染、不改动 | 机器门禁；`git diff 200f78a -- data/{mao,zhuge,sushi} src/{mao,zhuge,sushi}` 为空 | proven | `git diff 200f78a -- data/{mao,zhuge,sushi} src/{mao,zhuge,sushi} narration/{mao,zhuge,sushi} music/{mao,zhuge,sushi}_stages.json` 为空；test_timeline_is_fresh 对第一批三人仍通过；三部旧 mp4 未改动（修改时间仍为 10-06 09:02–09:13） |

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
| F1 | 史实核查 | fc-zhuyz | 1328H2 “名重八”无一手史料 | minor-fixed | 改为“按族中行第当为‘重八’”（据《朱氏世德碑记》行第推得），旁白不提（48187df） |
| F2 | 史实核查 | fc-zhuyz | 1380H1 “三万余人”是 1390 年李善长案以后的累计 | minor-fixed | 副标题与旁白改为“至洪武二十三年李善长案……”；note 记《明史》自身数字出入（48187df） |
| F3 | 史实核查 | fc-zhuyz | 出生地缺盱眙说；朱升九字策时间与史源有疑 | minor-fixed | contested 补两说与夏玉润质疑；东乡今址据陈梧桐 2010（48187df） |
| F4 | 史实核查 | fc-zhuyz | 1366H1 “至镇江而还”不准 | minor-fixed | 改“至镇江，士诚遁”（48187df） |
| F5 | 自查 | 主线程审片 | 1368H1 卡片“十五年而成帝业”与旁白“十六年”不一致 | minor-fixed | 统一为投军十六年（48187df） |
| F6 | 史实核查 | fc-jiang | 1954/1960/1966/1972 “续任”无宾语；1965H2 “台湾海军” | minor-fixed | 改为由所谓“国民大会”再次选为“总统”；“国民党海军”（48187df） |
| F7 | 史实核查 | fc-jiang | 1922H2 副标题误作“珠江舰”，引文出处易误解为孙中山著作 | minor-fixed | 改“永丰舰”；出处改为孙中山为蒋介石《孙大总统广州蒙难记》所作序（48187df） |
| F8 | 史实核查 | fc-jiang | 1943H2《开罗宣言》引文删了句首“在”字 | minor-fixed | 句首加“……”（48187df） |
| F9 | 史实核查 | fc-jiang | 1936H2 被扣细节；1937H2 谈话与发表日期；1908H1 “第十一期”仅维基 | minor-fixed | 按核查改写 event/note，删“第十一期”（48187df） |
| F10 | 史实核查 | fc-jiang | 1948H1 “总统”加引号、1975H1 注明周岁（可选） | minor-fixed | 已采纳（48187df） |
| F11 | 史实核查 | fc-libai | 736H2《将进酒》系年的学者归属写反，“秋”与再会孟浩然只有单一通俗网页 | minor-fixed | 改为郁贤皓/管士光/黄锡珪三说，note 标存疑（573fd1a） |
| F12 | 史实核查 | fc-libai | 730H1 “谒张说父子”依据不足 | minor-fixed | 改“欲谒张说未果，结识其子卫尉卿张垍”（573fd1a） |
| F13 | 史实核查 | fc-libai | 758H1《黄鹤楼上吹笛》系年有争议未列 | minor-fixed | contested 补两说；旁白改为“一说……王琦则认为是遇赦以后所作”（573fd1a） |
| F14 | 史实核查 | fc-libai | 701H1 “母梦长庚星”应标明为史载异兆 | minor-fixed | 前加“史载”（573fd1a） |
| F15 | 自查 | 主线程审片 | 蒋介石 1923H2 远途卡片写“广州 → 奉化溪口”，没体现莫斯科；星标压住朱元璋 1393 年号块 | minor-fixed | 卡片改为“起点 → 事件地”；星标进入 HUD 区时隐藏（48187df，D6） |
| F16 | 自查 | 主线程审片 | 李白 743H2 事件条在“史载”徽标下写“传有高力士脱靴之事” | rejected | 脱靴事见新旧《唐书》，event 已用“传有”限定、note 说明带传闻色彩；不改 |

### Parked

| id | needs | exact action | unblocks | verify afterward |
|---|---|---|---|---|

### Not verified

## Acceptance walk

| # | where | do | should see |
|---|---|---|---|
