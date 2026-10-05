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
| C1 | 每人一份半年粒度轨迹数据 `data/<who>/steps.json`：从出生所在半年到去世所在半年连续无缺（毛 1893H2–1976H2，诸葛 181–234H2，苏 1036H2/1037H1–1101H2，以史料为准）；每步含地点（古名+今名+坐标）、事件、来源、可信度（documented / inferred / traditional） | pytest `test_data.py`；故意删掉一步时测试变红 | open | |
| C2 | 史料核验：每人 ≥10 个里程碑，每个都有 ≥2 个独立来源；有争议处列入 `contested` 并在旁白中用审慎措辞 | 独立子代理的事实核查报告 `docs/evidence/factcheck-<who>.md`，分歧写入台账 | open | |
| C3 | 视频逐个半年步推进：HUD 显示「公元 X 年 上/下半年 · 年龄」，每一步都在画面中出现（≥0.4 s），轨迹线随时间生长，当前位置有标记 | pytest `test_timeline.py`（每步帧数、步序单调）；抽样截图 | open | |
| C4 | 轨迹在中国 3D 地形上展开（DEM 晕渲 + 垂直夸张 + 倾斜相机，覆盖人物活动范围），标注重要地理名称：大江大河、主要山脉/高原，以及人物到过的地点（古名与今名） | 抽样截图（每人 ≥6 张）；`smoke.mjs` 无报错 | open | |
| C5 | 里程碑高亮：每个里程碑有镜头推近、脉冲光环、标题卡，停留 ≥3 s | pytest（里程碑停留时长）；截图 | open | |
| C6 | 分阶段 BGM：每人 ≥4 个人生阶段，情绪依性格与经历设定（映射表写入 `music/<who>_stages.json`）；阶段切换时交叉淡化；全部原创合成，不含版权素材 | pytest（阶段覆盖全片、无空隙）；分阶段 RMS/频谱图 | open | |
| C7 | 讲解详略得当：里程碑处详讲，平淡时期一两句带过或只给字幕；旁白段之间不重叠；字幕烧录 | pytest（旁白不重叠、每个里程碑有旁白、非里程碑旁白总时长占比 <40%）；脚本人工可读 | open | |
| C8 | 交付 3 个 mp4：1920×1080、30 fps、H.264 + AAC，时长在目标区间内（毛 9–13 min，诸葛 6–9 min，苏 7–10 min），响度 −16±1.5 LUFS，无黑帧 | `check_outputs.py`；成片抽帧拼板 | open | |

`status` is `open`, `proven` or `parked`.

## Stages

1. [x] 骨架：git init、复制引擎和工具、合约生效、测试框架 — 无（8d63ddd）
2. [ ] 史料数据（三人并行子代理）+ 事实核查 — owns C1, C2
3. [ ] 中国 DEM 与地形贴图（全国底图 + 各人活动区细节）、河流/山脉标注数据 — owns C4（数据部分）
4. [ ] 解说词、TTS、时间轴（半年步 + 里程碑停留）— owns C3, C5, C7（时间轴部分）
5. [ ] 引擎场景：轨迹生长、HUD、里程碑高亮、标注 — owns C3, C4, C5
6. [ ] 配乐：三人分阶段情绪设计与合成 — owns C6
7. [ ] 渲染、混音、总装与审片 — owns C8
8. [ ] 落地：整体评审、验收清单

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
| D8 | 6 | 配乐全部用 numpy 原创合成，加入五声调式和民族音色（古筝/古琴/笛箫/二胡/锣/编钟） | 使用现成曲目 | 合约红线；本次运行无法试听，审美好坏列入“未验证” |

### Review findings

| id | round | reviewer | finding | status | note |
|---|---|---|---|---|---|

### Parked

| id | needs | exact action | unblocks | verify afterward |
|---|---|---|---|---|
| P1 | 你决定是否保留 | 苏轼史料子代理在 23:06 执行了 `pip install lunar_python`（1.4.8，安装到 ~/Library/Python/3.14 的用户 site-packages），合约未预授权这一操作。只有 `data/_build/sushi_lunar.py`（农历→公历换算）用到它，渲染、测试、成片管线都不依赖它。不想保留就执行 `pip3 uninstall lunar_python` | 无（成片不依赖） | `python3 -c "import lunar_python"` 报 ModuleNotFoundError，且 `python3 -m pytest -q tests` 结果不变 |

### Not verified

## Acceptance walk

| # | where | do | should see |
|---|---|---|---|
