# 三人人生轨迹视频：毛泽东 · 诸葛亮 · 苏轼

- status: planned <!-- planned → flying → landed -->
- workspace: lives/ (git, autopilot/three-lives)
- base: <待 git init 后填写>
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

1. [ ] 骨架：git init、复制引擎和工具、合约生效、测试框架 — 无
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
