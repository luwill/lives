# Autopilot contract — lives（人物人生轨迹视频）

Standing rules for unattended runs (the `autopilot` skill). The human owns this file: a run reads it and never edits it.

Status: in force since 2026-10-05 (confirmed by human at takeoff); amended 2026-10-06 at takeoff of run three-more-lives (per-run branch)

## Workspace

`opus5.5-video-test/` 本身不是 git 仓库。运行只拥有新目录 `opus5.5-video-test/lives/`，在其中 `git init`；每轮运行新建分支 `autopilot/<slug>`（第一轮 `autopilot/three-lives`，第二轮 `autopilot/three-more-lives` 从其末端分出）。
不改动同级的 `sidu/`、`liaoshen/`、`src/`、`promo/` 等目录（只读，引擎和工具代码复制过来再改）。
没有任何服务从该目录对外运行。大文件（`assets/terrain/tiles`、`out/`、`*.mp4`、`node_modules`、`narration/audio`）进 `.gitignore`。

## Preflight

| check | command | ready when |
|---|---|---|
| ffmpeg | `ffmpeg -version` | exit 0 |
| Python 依赖 | `python3 -c "import edge_tts, numpy, scipy, PIL"` | exit 0 |
| pytest | `python3 -m pytest --version` | exit 0 |
| TTS 联网 | `edge-tts --voice zh-CN-YunyangNeural --text 测试 --write-media t.mp3` | 生成非空 mp3 |
| Chromium | `python3 tools/check_env.py` | 输出“环境就绪” |
| DEM 瓦片 | `curl -o /dev/null -w %{http_code} https://s3.amazonaws.com/elevation-tiles-prod/terrarium/4/12/6.png` | 200 |
| Nominatim | `curl … nominatim.openstreetmap.org/search?q=Meishan&format=json` | 200 |
| codex | `codex --version` | exit 0 |

## Machine gate

| command | proves | rerun |
|---|---|---|
| `python3 -m pytest -q tests` | 数据完整性（半年步逐一覆盖生卒区间、坐标在范围内、来源与可信度字段齐全、里程碑数量）、时间轴约束（每个半年步的停留帧数达标、旁白不重叠、里程碑停留时长达标、BGM 段覆盖全片） | safe |
| `node tools/smoke.mjs` | 三个人物页面都能加载，并按抽样时间点 `renderAt(t)`，过程中无 pageerror 或 console error | safe |
| `python3 tools/check_outputs.py` | （成片存在后）mp4 为 1920×1080/30fps/H.264+AAC，时长与时间轴一致，响度在 −16±1.5 LUFS，抽样帧不是黑帧 | safe |

## Pre-authorized

- 在 `lives/` 内创建、修改、提交文件；`git init` 并建分支。
- 访问公开资源：AWS Terrarium DEM 瓦片、OSM Nominatim/Overpass（不超过 1 次/秒）、Natural Earth、维基百科及其他公开史料网页、edge-tts。
- 用本机 CPU/GPU 渲染（Playwright + 本地 Chromium），最多 4 个并行进程；磁盘占用不超过 30 GB。
- `npm install` 仅限 `three` 和 `playwright-core`（与同级项目相同的版本）。
- 落地 = 把三个 mp4 写入 `lives/`，并把运行记录设为 landed。不需要合并，也没有发布步骤。

## Red lines

| red line | prepare instead |
|---|---|
| 把视频上传或发布到任何平台 | 只在本地交付成片，并写明公开发布前要注意的地图合规事项 |
| 使用受版权保护的音乐或影视素材 | BGM 全部由程序原创合成（numpy） |
| 绘制国界线、省界线（存在“问题地图”风险） | 只展示地形晕渲、海岸（由 DEM 得出）、河流、山脉，以及古今地名标注 |
| 删除或修改 `lives/` 之外的任何文件 | 需要的代码复制进 `lives/` |
| 付费 API 或账号登录 | 停放，并写明需要人去做的动作 |

## Evidence

`lives/docs/evidence/<stage>-<label>.md`，由 `run-gate.sh` 生成，内容包括命令、退出码、时间和 commit。审片截图放在 `lives/docs/evidence/stills/`，同样提交。

## Review heuristics

- 史实：每个里程碑至少两个来源；有争议处在旁白里使用“约”“一说”等措辞，不捏造精确数字；查不到的地点写 null 或标 inferred，不臆造。
- 参考 `../learnings/2026-09-29-3d-terrain-history-documentary.md`（已知坑：`hideAt:null`、贴图暗角、地图黑边）。

## Run records

`lives/docs/runs/<YYYY-MM-DD>-<slug>.md`
