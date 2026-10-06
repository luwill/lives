# 三人人生轨迹视频：毛泽东 · 诸葛亮 · 苏轼

- status: flying <!-- planned → flying → landed -->
- workspace: lives/ (git, autopilot/three-lives)
- base: 8d63ddd
- contract: docs/autopilot.md

## Goal

> 我想做3个视频，分别动态展示毛泽东、诸葛亮、苏轼这三个人的人生动态轨迹图。需要满足下述条件：1.要充分结合史料，按照每个人的生卒年为区间，以半年为单位，展示其人生轨迹。2.所有轨迹需要在中国3D地形图上展开，并标注重要的地理名称等信息。3.每个人的人生里程碑节点需要highlight呈现。4.需要根据人物性格、生平和事迹，为每个人物的不同人生阶段配上不同的BGM。5.需要配上详略得当的讲解。

## Acceptance criteria

Frozen at takeoff. A run changes `status` and `evidence`, never the criterion.

| id | criterion | proven by | status | evidence |
|---|---|---|---|---|
| C1 | 每人一份半年粒度轨迹数据 `data/<who>/steps.json`：从出生所在半年到去世所在半年连续无缺（毛 1893H2–1976H2，诸葛 181–234H2，苏 1036H2/1037H1–1101H2，以史料为准）；每步含地点（古名+今名+坐标）、事件、来源、可信度（documented / inferred / traditional） | pytest `test_data.py`；故意删掉一步时测试变红 | proven | `docs/evidence/gate-final.md`（pytest 全过）；`docs/evidence/mutations.md`：删除 1935H1 一步、坐标越界两项都会让测试变红。诸葛亮生月不详，181H1 已标为 inferred |
| C2 | 史料核验：每人 ≥10 个里程碑，每个都有 ≥2 个独立来源；有争议处列入 `contested` 并在旁白中用审慎措辞 | 独立子代理的事实核查报告 `docs/evidence/factcheck-<who>.md`，分歧写入台账 | proven | 里程碑数：毛 22、诸葛 14、苏 16；每个里程碑 ≥2 个来源，由 `test_milestones` 检查（mutations.md 中“只留一个来源”会变红）。三份独立核查报告见 `docs/evidence/factcheck-*.md`，问题已逐条落实（F1–F11）。有争议的地方旁白用了“一说”“据《汉晋春秋》”“难以考证”等措辞 |
| C3 | 视频逐个半年步推进：HUD 显示「公元 X 年 上/下半年 · 年龄」，每一步都在画面中出现（≥0.4 s），轨迹线随时间生长，当前位置有标记 | pytest `test_timeline.py`（每步帧数、步序单调）；抽样截图 | proven | `docs/evidence/gate-final.md`（test_every_half_year_step_is_shown：每步 ≥0.4 s）；`test_js.py` 校验年龄与纪年（mutations.md：去掉年龄下限会变红）；截图见 `docs/evidence/stills/sheet_*.jpg`（取自最终 mp4） |
| C4 | 轨迹在中国 3D 地形上展开（DEM 晕渲 + 垂直夸张 + 倾斜相机，覆盖人物活动范围），标注重要地理名称：大江大河、主要山脉/高原，以及人物到过的地点（古名与今名） | 抽样截图（每人 ≥6 张）；`smoke.mjs` 无报错 | proven | `docs/evidence/stills/sheet_*.jpg`（每人 18–25 帧，取自最终 mp4）；`docs/evidence/gate-final.md` 中 smoke 三人 0 报错且整帧非空白。地形分 world/china/east 三级，垂直夸张 3.5–14 倍随镜头变化，标注 57 个地理名称并分层显示 |
| C5 | 里程碑高亮：每个里程碑有镜头推近、脉冲光环、标题卡，停留 ≥3 s | pytest（里程碑停留时长）；截图 | proven | `docs/evidence/gate-final.md`（test_milestones_hold；远途里程碑抵达后停留 ≥3 s；test_milestone_stays_at_its_place）；mutations.md 中停留 1 s、停留点改到杭州两项都会变红；截图见 `stills/mao_fixed.jpg` |
| C6 | 分阶段 BGM：每人 ≥4 个人生阶段，情绪依性格与经历设定（映射表写入 `music/<who>_stages.json`）；阶段切换时交叉淡化；全部原创合成，不含版权素材 | pytest（阶段覆盖全片、无空隙）；分阶段 RMS/频谱图 | proven | `music/<who>_stages.json`（毛 8 个阶段 8 种情绪、诸葛 6/6、苏 7/7）；`docs/evidence/audio-*.md` 记录分阶段响度、频谱质心、起音密度，阶段边界无静音；频谱图见 `stills/spectrogram_*.png`；`docs/evidence/gate-final.md`（test_music_covers_film_by_stage）。全部由 numpy 合成。审美效果未经试听 |
| C7 | 讲解详略得当：里程碑处详讲，平淡时期一两句带过或只给字幕；旁白段之间不重叠；字幕烧录 | pytest（旁白不重叠、每个里程碑有旁白、非里程碑旁白总时长占比 <40%）；脚本人工可读 | proven | `docs/evidence/gate-final.md`（按 C7 原文口径：非里程碑旁白 = 概述 + 片头 + 片尾，占比 <40%；旁白不重叠；字幕不重叠；一级里程碑旁白平均长于二级）；mutations.md 中三项变异都会变红。字幕烧录进画面，见截图 |
| C8 | 交付 3 个 mp4：1920×1080、30 fps、H.264 + AAC，时长在目标区间内（毛 9–13 min，诸葛 6–9 min，苏 7–10 min），响度 −16±1.5 LUFS，无黑帧 | `check_outputs.py`；成片抽帧拼板 | proven | `docs/evidence/gate-final.md` 中的 check_outputs --require（1920×1080@30、h264+aac、时长与时间轴一致且在目标区间内、−16±1.5 LUFS、抽样无黑帧） |

`status` is `open`, `proven` or `parked`.

## Stages

1. [x] 骨架：git init、复制引擎和工具、合约生效、测试框架 — 无（8d63ddd）
2. [x] 史料数据（三人并行子代理）+ 事实核查 — owns C1, C2（zhuge a6d226c、sushi 7b8faa3、mao 54b2fb4；核查报告见 docs/evidence/factcheck-*.md，修正在 9cb1fac）
3. [x] 中国 DEM 与地形贴图（全国底图 + 各人活动区细节）、河流/山脉标注数据 — owns C4（数据部分）
4. [x] 解说词、TTS、时间轴（半年步 + 里程碑停留）— owns C3, C5, C7（时间轴部分）
5. [x] 引擎场景：轨迹生长、HUD、里程碑高亮、标注 — owns C3, C4, C5
6. [x] 配乐：三人分阶段情绪设计与合成 — owns C6
7. [x] 渲染、混音、总装与审片 — owns C8（最终成片对应提交 fc89e5b）
8. [x] 落地：整体评审、验收清单

## Ledger

### Decisions

| id | stage | chose | rejected | wrong if |
|---|---|---|---|---|
| D1 | 起飞 | 配音按人物分声线（人类在起飞时选定）：毛=云扬 -6%/-2Hz，诸葛=云健 -10%/-4Hz，苏=云希 -6%/-1Hz | 统一使用云扬 | 云健、云希的 WordBoundary 粒度不足以切分字幕（已测试：按短语返回，字幕切分按字数映射，可用） |
| D2 | 3 | 河流、湖泊烘焙进地形贴图（Natural Earth 10m） | 用 3D 线绘制河流 | 垂直夸张随镜头动态变化时，3D 线会浮离或钻入地面 |
| D3 | 3 | 垂直夸张随镜头距离变化：近景 3.5 倍，全国俯瞰 14 倍 | 固定夸张倍数 | 全国俯瞰时 4 倍看不出地形起伏，近景用 14 倍又过于夸张 |
| D4 | 3 | 三级地形：east z8（97–124E/17.5–42.5N）+ china z7（70–138E/15–55N）+ world z4 兜底 | 每人单独做细节层 | 里程碑近景（相机距离约 260 km）下 east 层的贴图明显发糊（审片时判断） |
| D5 | 5 | 境外地点（莫斯科）画在“出发点朝目的地方向 900 km 处”，标注“图外 · 距北京约 N 公里” | 扩大地图范围到欧洲 | 观众把代理点误认为真实位置（已用“图外”字样和箭头说明） |
| D6 | 5 | 不画国界和省界，只标注地形区、山脉、河流、海域和时代政权的文字（魏/蜀/吴、辽/西夏/大理），片尾注明“地图仅示意地形与行迹” | 使用 Natural Earth 国界 | 合约红线 |
| D7 | 4 | 时间轴由旁白驱动：普通半年步 0.55 s，跨越 500 km 以上的步 0.95 s；里程碑先推近 1.7 s，再停留到旁白结束，至少 3 s；概述旁白覆盖一段连续的非里程碑步，并把这些步均匀拉长 | 每步固定时长 | 详略关系由旁白长度决定，通过测试 test_narration_balance 约束 |
| D9 | 2 | 史料子代理改从已受信任的父目录启动，任务书落盘到 data/briefs/，并要求按阶段增量落盘 | 在 tmux 窗格里代你点“信任此目录” | 首轮三个子代理从 lives/（新目录、未受信任）启动，全部卡在 Claude Code 的“是否信任此文件夹”提示，30 分钟零产出（窗格截图已核实）；用户不在场时不应由运行代为确认安全提示 |
| D10 | 4 | 里程碑新增可选字段 `place`：讲解停在事件发生地（如开国大典停在北京，讲完再去莫斯科）；远途里程碑按整步“边走边讲”，place 只决定星标位置 | 一律停在该半年的终点 | 停留点与旁白或卡片不一致（经事实核查后修正了 1935H1/H2、1936H1） |
| D11 | 5 | 年龄口径：古人按虚岁（诸葛亮以 181 年为一岁，苏轼以农历出生年 1036 为一岁），毛泽东按周岁，以半年中点计算 | 一律用年份差 | 与史料中的“年五十四”“年六十六”对不上；毛泽东生于 12 月下旬，按年份差会多算一岁 |
| D12 | 2 | 事实核查发现的问题逐条落实到数据与旁白（见下方核查记录）；卡片引文保留繁体原文 | 统一转简体（本机没有 opencc，也不新增依赖） | 观众觉得繁简混排别扭 |
| D13 | 6 | 各阶段配乐按目标 RMS 统一响度（激烈情绪 +2 dB，安静情绪 −2 dB） | 不做处理 | 阶段之间响度跳变（最初 battle 段比其他段高约 8 dB） |
| D8 | 6 | 配乐全部用 numpy 原创合成，加入五声调式和民族音色（古筝/古琴/笛箫/二胡/锣/编钟） | 使用现成曲目 | 合约红线；本次运行无法试听，审美好坏列入“未验证” |

### Review findings

| id | round | reviewer | finding | status | note |
|---|---|---|---|---|---|
| F1 | 史实核查 | fc-zhuge | 228H1 副标题“挥泪斩谡”出自《三国演义》 | blocking-fixed | 改为本传“戮谡以谢众”（9cb1fac） |
| F2 | 史实核查 | fc-zhuge | 231H1 卤城之胜只有《汉晋春秋》一个来源，副标题前后矛盾 | minor-fixed | 改写副标题，补 note 与 contested，旁白注明“据《汉晋春秋》……《晋书》记为魏胜”（9cb1fac） |
| F3 | 史实核查 | fc-zhuge | 223H1 梓宫还成都在五月；225H1“由水路入越巂”沿用未校本；228H2 实际在公历 229 年 1—2 月 | minor-fixed | 修改 event 和 note（9cb1fac） |
| F4 | 史实核查 | fc-sushi | 1061H2 郑州西门之别换算为公历 1062-01-02，渑池、长安两地不应出现在 1061H2 | blocking-fixed | 拆分到 1062H1，引文换成《宋史》“制策入三等”（9cb1fac） |
| F5 | 史实核查 | fc-sushi | 1086H2 “奇才”一语出自元祐二年（1087）的召对 | minor-fixed | 出处改为注明元祐二年（9cb1fac） |
| F6 | 史实核查 | fc-sushi | 1090H1 四月只是上状请款，筑堤在夏秋 | minor-fixed | 修改 event 和旁白（9cb1fac） |
| F7 | 史实核查 | fc-sushi | 1094H2 “不辞”有异文“不妨”；1076H2 副标题误用 1075 年事；1100H2 行程不准；汴京坐标偏离 26 km | minor-fixed | 9cb1fac |
| F8 | 史实核查 | fc-mao | 1935H1、1935H2、1936H1 的里程碑地点默认取了半年终点，与标题和引文不符 | blocking-fixed | 分别加 place = zunyi、wuqi、yuanjiagou（9cb1fac） |
| F9 | 史实核查 | fc-mao | 袁家沟坐标取的是清涧县城，偏差约 30 km | minor-fixed | 改用 OSM 高杰村镇驻地（9cb1fac） |
| F10 | 史实核查 | fc-mao | 1937H1 写《矛盾论》（8 月作，属 H2）；1966H2 应为“畅游”而非“横渡” | minor-fixed | 修改 event 和副标题（9cb1fac） |
| F11 | 史实核查 | fc-mao | 1966H2 建议写“七十三岁（虚岁）” | rejected | 毛泽东按周岁计算（D11），1966 年 7 月周岁为 72，与旁白一致 |
| R1 | 整体评审 r1 | 验收审计 | 毛泽东成片过时（715 s ≠ 731 s），机器门禁复跑失败 | blocking-fixed | 当时正在重新渲染；最终门禁见 docs/evidence/gate-final.md |
| R2 | 整体评审 r1 | 验收审计 | 运行记录中各准则没有证据 | blocking-fixed | 本次落地补齐 |
| R3 | 整体评审 r1 | 验收审计 | 有两个里程碑只挂一个来源，且没有测试检查来源数量；诸葛亮 181H1 不应标为 documented | minor-fixed | 086d970（补来源，新增测试检查 ≥2 来源，181H1 改为 inferred） |
| R4 | 整体评审 r1 | 验收审计 | 缺少 C6 的 RMS/频谱证据，“删一步就变红”也没有记录 | minor-fixed | 086d970（audio-*.md，mutations.md） |
| R5 | 整体评审 r1 | 对抗复查（Codex 替身） | 毛泽东出生时显示“−1 岁” | blocking-fixed | fc89e5b（周岁下限取 0，新增 test_js 检查） |
| R6 | 整体评审 r1 | 对抗复查 | C7 测试只计概述，与冻结的条款口径不符；按条款计算毛 0.445、苏 0.418，都超过 40% | blocking-fixed | fc89e5b（测试改为按条款口径；删减毛约 68 s、苏约 35 s 旁白） |
| R7 | 整体评审 r1 | 对抗复查 | 片头第一章节卡期间镜头先猛推再拉回 | minor-fixed | fc89e5b（camera.js 限制 k ≥ 0） |
| R8 | 整体评审 r1 | 对抗复查 | 三段旁白没有随事实核查一起修改（斩马谡、水路入越巂、郑州西门） | minor-fixed | fc89e5b |
| R9 | 整体评审 r1 | 对抗复查 | 苏轼出生卡显示“景祐四年·虚岁 2”；诸葛亮 221H1 显示建安；苏轼娶王弗写成“十八岁” | minor-fixed | fc89e5b（出生步特判，章武从 221H1 起算，改为十九岁） |
| R10 | 整体评审 r1 | 对抗复查 | 莫斯科段用代理点计算，里程少算约 15%；1957 年的代理点偏离约 950 km | minor-fixed | fc89e5b（代理点固定按北京方向，里程按真实坐标累计，新增 test_js 检查） |
| R11 | 整体评审 r1 | 对抗复查 | 远途里程碑的停留时长把行进时间也算了进去；字幕有 22 处重叠（最长 0.06 s） | minor-fixed | fc89e5b（抵达后至少停 3 s，字幕去重叠，两项都有测试） |
| R12 | 整体评审 r1 | 对抗复查 | test_milestone_stays_at_its_place 只是照抄实现里的常量 8 | dispute | 审查方：测试复述了实现。我方：“≥8 个途经点才按远途处理”本身就是规格，测试的作用是锁住规格；mutations.md 证明停留点被改到杭州时它会变红 |
| R13 | 自查·审片 | 主线程 | 远途镜头期间，事件条的 📍 显示星标所在地（遵义），而不是标记当前所在的位置 | minor-open | 1935H1 本身就是“遵义会议”这一步，这样显示也说得通；未改 |
| F12 | 自查·审片 | 主线程 | 年龄按年份差计算，毛泽东多算一岁；卡片上写“七十三岁” | blocking-fixed | 85cd963 |

### Parked

| id | needs | exact action | unblocks | verify afterward |
|---|---|---|---|---|
| P2 | 修正 Codex 配置（你的账号） | `~/.codex/config.toml` 中设置的 `model = "gpt-6.1-sol"` 不能用于 ChatGPT 账号登录（返回 400），所以没有运行 Codex 对抗评审，改用同一模型族的对抗复查子代理代替（不是跨模型）。改成你账号可用的模型后，执行 `cd lives && CODEX_REVIEW_HEAD=fc89e5b bash ~/.claude/skills/autopilot/scripts/codex-review.sh . 8d63ddd docs/runs/2026-10-05-three-lives.md docs/evidence/review-codex-r1.md` | 跨模型评审 | 生成 `docs/evidence/review-codex-r1.md`，且 verdict 字段有值 |
| P1 | 你决定是否保留 | 苏轼史料子代理在 23:06 执行了 `pip install lunar_python`（1.4.8，安装到 ~/Library/Python/3.14 的用户 site-packages），合约未预授权这一操作。只有 `data/_build/sushi_lunar.py`（农历→公历换算）用到它，渲染、测试、成片管线都不依赖它。不想保留就执行 `pip3 uninstall lunar_python` | 无（成片不依赖） | `python3 -c "import lunar_python"` 报 ModuleNotFoundError，且 `python3 -m pytest -q tests` 结果不变 |

### Not verified

| 项目 | 原因 |
|---|---|
| 配乐与配音的听感（旋律是否好听、情绪是否贴合、TTS 断句与读音，例如“鞠躬”“谡”“巂”“儋”等字） | 运行中无法试听，只用客观指标（响度、频谱、起音密度、边界无静音）代替 |
| 完整逐帧观看三部成片 | 只看了每 30 s 一帧的拼板，以及约 60 张定点截图 |
| 史料来源本身的真伪与网页原文 | 核查代理抓取了维基文库、党史网站等；两部《毛泽东年谱》和孔凡礼《苏轼年谱》没有拿到原文 |
| 古地名今址的精度 | 有 11 个毛泽东相关地点、6 个诸葛亮相关地点只能定位到县城或示意点（places.json 中标为 low） |
| 公开发布前的地图合规（审图号） | 片中没有画国界或省界，片尾注明“地图仅示意地形与行迹”；但在中国大陆公开发布含地图的视频是否需要送审，运行中没有判断 |
| 毛泽东晚年段落的措辞 | 依据 1981 年《历史决议》的官方表述撰写，表述是否得当仍需你判断 |

## Acceptance walk

| # | where | do | should see |
|---|---|---|---|
