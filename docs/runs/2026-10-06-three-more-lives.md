# 三人人生轨迹视频（第二批）：李白 · 朱元璋 · 蒋介石

- status: landed
- final render commit: dd22653（三部 mp4 均由此提交渲染）；最终门禁 fddc945：docs/evidence/gate-batch2-final.md <!-- planned → flying → landed -->
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
| C1 | 每人一份半年粒度轨迹数据 `data/<who>/steps.json`，从出生所在半年到去世所在半年连续无缺：李白 701H1–762H2（生月不详，记为 inferred；出生地有争议，取碎叶，并在 contested 中列出“绵州昌隆”说）；朱元璋 1328H2–1398H1；蒋介石 1887H2–1975H1。每步含地点（古名+今名+坐标）、事件、来源、可信度 | pytest `test_data.py`（六人）；变异测试：删一步会变红 | proven | `docs/evidence/gate-batch2-final.md`（pytest 99 项全过，六人）；mutations（同一门禁第 4 条，18 个变异全部变红）：删一步、坐标越界会变红，第二批另有“删除李白 750H1”“溪口经度改为 10°”两项。步数：李白 124、朱元璋 140、蒋介石 176；李白 701H1 标 inferred，出生地两说列入 contested |
| C2 | 史料核验：李白、朱元璋各 ≥10 个里程碑，蒋介石 ≥15 个，每个都有 ≥2 个独立来源；有争议处列入 `contested`，旁白用审慎措辞 | 独立核查报告 `docs/evidence/factcheck-<who>.md`；分歧写入台账 | proven | 里程碑：李白 16、朱元璋 16、蒋介石 20，每个 ≥2 来源（test_milestones）。三份独立核查：`docs/evidence/factcheck-{libai,zhuyz,jiang}.md`，共 52 个里程碑：通过 40、存疑 12、错误 0；“需要修改”逐条落实（F1–F16）。蒋介石核查为每个里程碑补了至少一个非维基来源 |
| C3 | 视频逐个半年步推进：HUD 显示公元年、上/下半年、纪年与年龄（李白、朱元璋按虚岁，蒋介石按周岁），每步在画面中出现 ≥0.4 s，轨迹线随时间生长 | pytest `test_timeline.py`、`test_js.py`（年龄/纪年锚点）；抽样截图 | proven | gate-batch2-final.md（test_every_half_year_step_is_shown；test_age_and_era_anchors_second_batch：李白虚岁/天宝称载、朱元璋龙凤/洪武、蒋介石周岁与 1949H2 后无民国纪年）；三个纪年变异都会变红；截图 `docs/evidence/stills/sheet_{libai,zhuyz,jiang}.jpg`（tools/contact_sheet.sh，取自 dd22653 成片） |
| C4 | 轨迹在中国 3D 地形上展开，标注山河与人物到过的地点（古名与今名）；图外地点（如东京、莫斯科、开罗）用地图边缘代理点，片尾里程仍按真实坐标累计 | 截图拼板（每人 ≥6 张，取自最终 mp4）；`smoke.mjs` 六人无报错；`test_js.py` 代理点测试 | proven | `stills/sheet_{libai,zhuyz,jiang}.jpg`（由 tools/contact_sheet.sh 从 dd22653 成片每 30 秒取一帧，17–20 帧，脚本打印成片 sha256）；gate-batch2-final.md 中 smoke 六人 0 报错、整帧非空白；test_offmap_proxy_points_east_and_west（东京→东缘、开罗→西缘）；新增地名注记 8 个（D4） |
| C5 | 里程碑高亮：每个里程碑有镜头推近、光环、标题卡，停留 ≥3 s，停在事件发生地 | pytest（停留时长、停留地点）；截图 | proven | gate-batch2-final.md（test_milestones_hold、test_milestone_stays_at_its_place 六人）；截图中卡片、光环、星标可见；远途卡片显示“起点 → 事件地”（D6） |
| C6 | 分阶段 BGM：每人 ≥4 个人生阶段，情绪依性格与经历设定（`music/<who>_stages.json`），阶段间无空档，全部原创合成 | pytest（覆盖全片）；`docs/evidence/audio-<who>.md` 分阶段响度/频谱 | proven | `music/{libai,zhuyz,jiang}_stages.json`（8/8/8 个阶段，李白 8 种情绪、朱元璋 7 种、蒋介石 8 种）；`docs/evidence/audio-{libai,zhuyz,jiang}.md` 与 gate-batch2-final.md 第 5–7 条（由 run-gate 在 fddc945 生成；分阶段 dBFS、频谱质心、起音密度，阶段边界无静音）；`stills/spectrogram_*.png`。审美未经试听 |
| C7 | 讲解详略得当：每个里程碑有旁白；非里程碑旁白（概述+片头+片尾）占比 <40%；旁白、字幕都不重叠；字幕烧录 | pytest；变异测试 | proven | gate-batch2-final.md（test_narration_balance：非里程碑旁白占比 李白 0.373、朱元璋 0.333、蒋介石 0.325；旁白、字幕不重叠） |
| C8 | 交付 3 个 mp4：1920×1080、30 fps、H.264+AAC，时长在目标区间（李白 7–10 min，朱元璋 8–11 min，蒋介石 9–13 min），响度 −16±1.5 LUFS，无黑帧 | `check_outputs.py --require` | proven | gate-batch2-final.md 中 check_outputs --require：李白 480.1 s（8.0 min）、朱元璋 519.3 s（8.7 min）、蒋介石 593.0 s（9.9 min），1920×1080@30、h264+aac、−16.3/−16.1/−16.4 LUFS，抽样无黑帧。三部均由 dd22653 渲染（out/<who>/render_commit.txt，渲染开始前记录） |
| C9 | 不破坏第一批：毛泽东、诸葛亮、苏轼的数据和时间轴不变，六人测试、smoke 全部通过；三部旧成片不重渲染、不改动 | 机器门禁；`git diff 200f78a -- data/{mao,zhuge,sushi} src/{mao,zhuge,sushi}` 为空 | proven | `git diff 200f78a -- data/{mao,zhuge,sushi} src/{mao,zhuge,sushi} narration/{mao,zhuge,sushi} music/{mao,zhuge,sushi}_stages.json` 为空；test_timeline_is_fresh 对第一批三人仍通过；三部旧 mp4 未改动（修改时间仍为 10-06 09:02–09:13） |

`status` is `open`, `proven` or `parked`.

## Stages

1. [x] 骨架：建分支；测试、工具、people.js 扩展到六人 — 无（与第 2 阶段合并提交 48187df，避免提交红色测试）
2. [x] 史料数据（三人并行子代理）+ 独立事实核查 — owns C1, C2（48187df、573fd1a；核查报告 docs/evidence/factcheck-{libai,zhuyz,jiang}.md）
3. [x] 解说词、TTS、时间轴 — owns C3, C5, C7（48187df；评审修订 b9e5103、dd22653）
4. [x] 引擎适配：纪年/年龄、时代政权注记、图外代理点、新增地名标注 — owns C3, C4, C5
5. [x] 配乐：三人分阶段情绪设计与合成 — owns C6
6. [x] 渲染、混音、总装与审片 — owns C8（最终成片由 dd22653 渲染：out/<who>/render_commit.txt；拼板 sha256 李白 8bad098cc751、朱元璋 7ae8b7c3eb20、蒋介石 d10b9a0a1a8a）
7. [x] 落地：整体评审（两轮）、变异测试、验收清单 — owns C9

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
| R1 | 整体评审 r1 | 验收审计 | 本轮在 48187df 修改了合约，仓库里没有人类确认的证据 | rejected | 修订是起飞时人类在批量问题“起飞确认”中选定的（选项“照此起飞”，题干写明“合约只改一处：工作分支……改为每轮新建 autopilot/<slug>”）；合约第 5 行已注明 amended at takeoff。确认本身在对话中，不在仓库里 |
| R2 | 整体评审 r1 | 验收审计 | 拼板“取自最终 mp4”不可复现 | minor-fixed | 新增 `tools/contact_sheet.sh`，同时打印成片 sha256 与渲染提交；落地时用它重新生成（b9e5103） |
| R3 | 整体评审 r1 | 验收审计 | 渲染日志不记录提交，“由某提交渲染”只能从时间推断 | minor-fixed | render_all.sh 写 `out/<who>/render_commit.txt`（工作区有改动时标 dirty）；三部成片在 b9e5103 重渲染（b9e5103） |
| R4 | 整体评审 r1 | 验收审计 | C1 变异只改第一批数据 | minor-fixed | 新增“删除李白 750H1”“溪口经度改为 10°”两个变异（b9e5103） |
| R5 | 整体评审 r1 | 验收审计 | 阶段清单未更新、Not verified 为空、audio-*.md 不是 run-gate 生成 | minor-fixed | 落地时补齐；audio 指标改由 run-gate.sh 生成（见 gate 证据） |
| R6 | 整体评审 r1 | 对抗复查（Codex 替身） | A1 蒋介石 1949H2 卡片“草山 → 台北”，同城往返 | minor-fixed | 远途卡片起点与事件地相距 <50 km 时改显示停留地点（b9e5103） |
| R7 | 整体评审 r1 | 对抗复查 | A2 “武汉失守后国民政府迁到重庆”顺序错 | minor-fixed | 改为 1937 年底宣布移驻重庆，武汉失守后蒋到重庆（b9e5103） |
| R8 | 整体评审 r1 | 对抗复查 | A3 “回乡招兵，徐达、汤和都在其中”与汤和写信招他矛盾 | minor-fixed | 改为“少年伙伴徐达也来投奔”（b9e5103） |
| R9 | 整体评审 r1 | 对抗复查 | A4 刺杀陶成章旁白没有审慎措辞 | minor-fixed | 改为“陶成章在上海遇刺，一般认为由他主谋”（b9e5103） |
| R10 | 整体评审 r1 | 对抗复查 | A5 李白片头碎叶、黄鹤楼送孟浩然、梦游天姥、敬亭山，朱升九字策未加限定 | minor-fixed | 分别加“生于西域”“约在此时”“一般认为”“一说”“据《明史·朱升传》……也有学者存疑”（b9e5103）。752H2 有李白自述“十月到幽州”，未改 |
| R11 | 整体评审 r1 | 对抗复查 | A6 旁白“一住十年”与卡片引文“至移三霜”不一致 | minor-fixed | 改为“后来他自称，酒隐安陆，蹉跎十年”（李白《秋于敬亭送从侄耑游庐山序》语）（b9e5103） |
| R12 | 整体评审 r1 | 对抗复查 | A7 “长庚星入怀”的“入怀”无出处 | minor-fixed | 删“入怀”（b9e5103） |
| R13 | 整体评审 r1 | 对抗复查 | A8 761H2 显示上元二年、762H1 显示宝应元年，而 761 年九月至 762 年建巳月去年号 | rejected | 按 people.js 的既定规则“同一半年内改元时取占多数月份的年号”：761H2 七至九月仍为上元（去年号自建子月起，占少数）；762H1 去年号三个月与宝应三个月相当，取后者。规则与第一轮一致 |
| R14 | 整体评审 r1 | 对抗复查 | A9 1368H1 元、北元都不显示；张士诚在平江城破前已隐藏；“明玉珍”1366 年已死 | minor-fixed | 元显示到 1368H1；张士诚到 1367H2；改称“夏（明玉珍）”（b9e5103） |
| R15 | 整体评审 r1 | 对抗复查 | A10 `y<1355`→`y<1354` 变异存活；至德/乾元、蒋介石清末民初分支无测试 | minor-fixed | 新增 test_era_edges_second_batch（1354H2 仍为至正十四年等）（b9e5103） |
| R16 | 整体评审 r1 | 对抗复查 | A11 D6/F15 的卡片与星标改动没有测试；星标只按中心点判断遮挡 | minor-open | 属于 DOM 渲染逻辑，现有 pytest 不驱动浏览器；靠截图审片覆盖。留待人类验收第 3 步目视检查 |
| R17 | 整体评审 r1 | 对抗复查 | A12 同地异名（草山/阳明山、重庆/陪都、北京/北平）让“足迹所至”重复计数 | minor-fixed | b9e5103 先按坐标去重，r2 发现会误并共用县城坐标的不同地点（B1），改为 places.json 显式 `same_as`（蒋介石三对），第一批数据不动（C9）。孤庄村/皇觉寺是两处不同地点，共用明皇陵示意坐标，不合并 |
| R18 | 整体评审 r1 | 对抗复查 | A13 全国俯瞰时地名注记互相压叠（临潼华清池/归德、庐山牯岭/杭州） | minor-open | 去冲突逻辑是第一轮沿用的贪心放置，当前地点和里程碑星标优先；大幅修改会波及第一批。记为未修 |
| R19 | 整体评审 r1 | 对抗复查 | A14 朱元璋 1328H2 note 残留“本站所据史料未载” | minor-fixed | 改写为据《朱氏世德碑记》行第推得（b9e5103） |
| R20 | 整体评审 r1 | 对抗复查 | A15 蒋介石 1949H2 整个半年不显示纪年（含 10 月以前） | rejected | 与起飞时人类选定的 D1 一致（“1949 年下半年起只显示公元年”），列入人类知悉事项 |
| R21 | 整体评审 r1 | 主线程（复跑时发现） | TTS 单段失败时旧音频残留，时间轴按旧时长排而测试仍全绿 | minor-fixed | 新增 test_narration_audio_matches_script（按文本+声线哈希核对），并加变异“改旁白不重新配音”（b9e5103） |
| R22 | 整体评审 r2 | 对抗复查 | B1 按坐标去重会误并共用县城示意坐标的不同地点（毛泽东梁家岔/朱官寨/神泉堡等），并悄悄改变第一批片尾计数 | fixed-unreviewed | 改为显式 `same_as` 别名（SCHEMA.md 已加字段）；毛泽东、诸葛亮数据不变 |
| R23 | 整体评审 r2 | 对抗复查 | B2 陶成章一事只改了旁白，事件条与 contested.adopted 仍是定论口吻 | fixed-unreviewed | 事件条改“遇刺，一般认为由蒋主谋”，adopted 同步 |
| R24 | 整体评审 r2 | 对抗复查 | B3 汤和一事只改了旁白，1353H1 事件条仍写“徐达、汤和来归” | fixed-unreviewed | 改“徐达等来归” |
| R25 | 整体评审 r2 | 对抗复查 | B4 李白片头“生于西域”仍是单一说法 | rejected | contested.adopted 采碎叶说（任务书约定），701H1 里程碑旁白已并列“通行的说法……也有学者认为生在蜀中绵州”；片头 R10 已从“生于碎叶”收为“生于西域” |
| R26 | 整体评审 r2 | 对抗复查 | B5 仍有存活变异：乾元起点后移、701H1 武周前缀、761/762 年号 | fixed-unreviewed | 加锚点 701H1=武周 · 大足元年、761H2=上元二年、762H1=宝应元年（758H1=乾元元年 原测试已有） |
| R27 | 整体评审 r2 | 对抗复查 | B6 hud.js 的 50 km 规则与足迹去重没有测试 | minor-open | 同 R16：pytest 不驱动 DOM；靠截图审片与人类验收第 3 步 |
| R28 | 整体评审 r2 | 对抗复查 | B7 render_commit.txt 在渲染结束后才记录，期间若有提交会打错版本 | fixed-unreviewed | 改为开始渲染前记录，未跟踪文件也算 dirty |
| R29 | 整体评审 r2 | 对抗复查 | B8 测试模块级导入 tts 会连带导入 edge_tts | fixed-unreviewed | tts.py 改为在 synth() 内延迟导入 |
| R30 | 整体评审 r2 | 对抗复查 | B9 拼板格数按 floor(total/30) 算，比 fps=1/30 实际帧数少 1，可能丢掉最后一帧 | fixed-unreviewed | 改为 floor(total/30)+1 |

### Parked

In the order the human should do them.

| id | needs | exact action | unblocks | verify afterward |
|---|---|---|---|---|
| P1 | 人类决定是否保留第一轮遗留的 Python 包 `lunar_python`（合约未预授权安装；本轮三个研究代理和朱元璋核查都用它做农历换算，但没有新装） | 不想保留：`pip3 uninstall lunar_python` | 合约合规；卸载后已提交的数据与成片不受影响，只是 `data/_build/*_lunar.py`、`zhuyz_lunar.py` 无法重跑 | `python3 -c "import lunar_python"` 报 ModuleNotFoundError；`python3 -m pytest -q tests` 仍全过 |
| P2 | 跨模型 Codex 评审（`~/.codex/config.toml` 的 `model = "gpt-6.1-sol"` 在 ChatGPT 账号登录下不可用，与第一轮相同） | 把该文件的 model 改成账号可用的模型，然后运行：`CODEX_REVIEW_HEAD=$(git -C lives rev-parse HEAD) bash ~/.claude/skills/autopilot/scripts/codex-review.sh lives 200f78a lives/docs/runs/2026-10-06-three-more-lives.md lives/docs/evidence/review-codex-batch2.md` | 真正的跨模型对抗评审（本轮用同模型对抗代理顶替，两轮报告见 docs/evidence/review-adversary-batch2-r{1,2}.md） | 输出文件非空，且对其中发现逐条分诊 |

### Not verified

- **配乐与配音没有试听**：只检查了响度、频谱质心、起音密度，以及阶段边界有没有静音（audio-*.md）。好不好听、情绪对不对，都要人来听。
- **完整成片没有逐帧看过**：只审了每 30 秒一帧的拼板，加上约 12 张定点截图。
- **地名注记偶有压叠**（R18）：全国俯瞰时，临潼华清池与归德、庐山牯岭与杭州的注记会挤在一起。
- **HUD 的部分改动没有自动测试**（R16、R27）：远途卡片“起点 → 事件地”、50 km 规则、足迹去重、星标避让 HUD 都只靠截图验证。
- **第 2 轮修复无人复审**（R22–R26、R28–R30 标 fixed-unreviewed）：没有第三轮评审。
- **蒋介石的史源偏弱**：研究代理没读到任何一部大陆专著原书，主干年表依赖中、英文维基。核查代理为每个里程碑补了至少一个非维基来源，但非里程碑的半年步大多仍只有维基依据。另有 7 处无法核实，见 factcheck-jiang.md 文末，其中孙中山序的引文只找到一个独立载录。
- **李白的系年骨架**：取自安旗年谱的网页转录（通俗级来源）；詹锳、郁贤皓、安旗的原书都没读到。731–739 年、747–751 年两段推定成分最重。
- **朱元璋**：《明太祖实录》没有可读的在线全文；朱升九字策的年月与真伪仍未定；孤庄村、皇觉寺今址只取了明皇陵的示意坐标。
- **蒋介石部分的措辞**：按起飞时选定的大陆通行史学表述撰写，并经核查代理逐条检查立场措辞。是否适合公开发布，需要人来把关。
- **蒋介石 1949H2 整个半年不显示纪年**，包括 7—9 月（R20，与 D1 一致）。如果希望从 10 月起才不显示，需要人来定。
- **地图合规**：在中国大陆公开发布含地图的视频，可能需要送审取得审图号。本轮没有判断这一点，与第一轮相同。
- **第一批三部成片没有重渲染**（C9）：本轮引擎的改动（远途卡片、星标避让、same_as 足迹计数）只体现在新三部里。

## Acceptance walk

Riskiest first.

| # | where | do | should see |
|---|---|---|---|
| 1 | `lives/蒋介石_人生轨迹.mp4` | 戴耳机看 4:09（1927 四一二）、6:01—6:50（1936 西安事变、1937 庐山谈话）、8:09—8:50（1949H2 退往台湾、1950 起） | 措辞是你能接受的立场：四一二称反革命政变；西安事变写和平解决；1949H2 卡片标题为“国民党政权退往台湾”，地点显示台北；1949 年下半年起，左上年份块不再出现民国纪年；1950 年后的“总统”一律带引号或加“所谓” |
| 2 | 三部新成片的开头 1 分钟和任意一次章节切换 | 听配乐和配音 | 配乐在章节卡处有锣和编钟收束，并切换情绪；三种声线能区分开（李白明快，朱元璋低沉，蒋介石庄重）；没有爆音，也没有长段静音 |
| 3 | `lives/蒋介石_人生轨迹.mp4` 2:30（1923 访苏）、7:06（1943 开罗） | 看里程碑卡片和地图 | 卡片写“广州 → 莫斯科（今俄罗斯莫斯科）”；开罗、莫斯科画在地图边缘，并标“图外 · 距北京约 N 公里”；右上角“足迹所至”不会因为北平/北京这类改名而跳两次 |
| 4 | `lives/朱元璋_人生轨迹.mp4` 0:59（1344 父母双亡）、3:59（1363 鄱阳湖）、6:33（1380 胡惟庸案） | 看卡片与旁白 | 引文为繁体原文，并注明出处；胡惟庸案副标题写“至洪武二十三年李善长案……三万余人”，与旁白一致；年份块在 1355—1366 显示“龙凤X年 · 元至正X年” |
| 5 | `lives/李白_人生轨迹.mp4` 开头（碎叶）和 6:46（759 白帝城） | 看地图 | 碎叶位于天山北麓、伊塞克湖附近；年份块 701 年显示“武周 · 大足元年”，744 年起显示“天宝三载”；白帝城处卡片引《早发白帝城》 |
| 6 | `lives/docs/evidence/stills/sheet_{libai,zhuyz,jiang}.jpg` | 浏览拼板 | 每 30 秒一帧，没有黑帧，也没有空白地形 |
