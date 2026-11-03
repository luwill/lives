# lives

把中国历史人物的一生做成「人生轨迹」视频：在 3D 卫星地形上，按半年为一步，画出人物走过的路线，同时配上旁白、配乐和时间线 HUD。

已做好的人物有诸葛亮、李白、苏轼、朱元璋、毛泽东、蒋介石。

这套流程已经打包成 Claude Code skill：[luwill/lifetrail](https://github.com/luwill/lifetrail)。本仓库是 skill 模板的源项目。

## 目录

| 路径 | 内容 |
|---|---|
| `data/<who>/` | 人物配置 `person.json` 和半年一步的行程数据，格式见 `data/SCHEMA.md` |
| `src/` | three.js 地形引擎、相机、轨迹与 HUD |
| `tools/` | 地形与影像下载、时间线构建、TTS、混音、合成、输出检查 |
| `music/` | 程序合成的分段配乐 |
| `narration/<who>/` | 旁白文本（音频不入库） |
| `assets/terrain/` | 预处理好的地形网格和卫星贴图 |
| `docs/` | 设计、运行记录、A/B 评测报告 |

## 运行

```bash
npm ci
python3 tools/check_env.py
python3 -m pytest
tools/render_all.sh <who>     # 例如 zhuge，成片输出到仓库根目录
```

需要 Node 18+、Python 3、ffmpeg，以及 Chromium（会自动查找，也可以用 `LIFETRAIL_CHROME` 指定）。TTS 用 edge-tts；如果用 MiniMax，需要设置环境变量 `MINIMAX_API_KEY`。

## 许可与数据来源

- **代码**：MIT，见 `LICENSE`。
- **卫星贴图**（`assets/terrain/*_tex.jpg`）：EOxCloudless — https://cloudless.eox.at by EOX IT Services GmbH（Contains modified Copernicus Sentinel data 2022），许可为 CC BY-NC-SA 4.0，**仅限非商业使用**。商业使用需另向 EOX 购买授权。
- **高程**：AWS Terrain Tiles（Terrarium），数据源包括 SRTM、GMTED2010、ETOPO1 等。
- **旁白内容**：根据公开史料整理，仅供学习交流。涉及近现代人物的评价采用大陆通行表述。
