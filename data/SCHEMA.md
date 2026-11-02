# 人生轨迹数据规范

每个人物一个目录：`data/<who>/`，`who` 为拼音小写键（`[a-z0-9_]+`，如 `sushi`）。坐标一律为 WGS84 十进制度。

## 半年步的定义

- `H1` = 该年 1–6 月，`H2` = 7–12 月，按公历计算（1582 年以前用儒略历换算的公元日期）。
- 古代人物的史料多为农历：农历日期能换算成公历就换算；只知月份时，按"农历 1–6 月 → H1、7–12 月 → H2"近似处理，并在 `event` 或 `note` 中注明。
- 第一步是出生所在的半年，最后一步是去世所在的半年，中间连续、不能有缺。


## `steps.json`

```json
{
  "meta": {
    "person": "苏轼",
    "birth": "1037-01-08",
    "birth_note": "景祐三年十二月十九日",
    "death": "1101-08-24",
    "death_note": "建中靖国元年七月二十八日",
    "calendar_note": "半年划分方法说明",
    "sources": [{"id": "S1", "title": "《宋史·苏轼传》", "url": "https://example.org", "kind": "primary"}]
  },
  "stages": [
    {"id": "st1", "title": "眉山少年", "from": "1037H1", "to": "1056H1",
     "summary": "一句话概括", "mood_hint": "这一阶段的性格与处境，供配乐参考"}
  ],
  "steps": [
    {
      "id": "1079H2",
      "places": ["huzhou", "kaifeng"],
      "event": "七月在湖州被捕，八月押至汴京御史台狱（乌台诗案）",
      "confidence": "documented",
      "sources": ["S1"],
      "stage": "st1",
      "milestone": {
        "title": "乌台诗案",
        "subtitle": "因诗获罪，下御史台狱一百三十天",
        "importance": 1,
        "place": "kaifeng",
        "quote": {"text": "是处青山可埋骨，他年夜雨独伤神。", "source": "《狱中寄子由》"}
      },
      "note": "史料分歧说明"
    }
  ],
  "contested": [{"topic": "争议点", "views": ["说法一（来源）", "说法二（来源）"], "adopted": "采用哪种以及理由"}]
}
```

字段说明（示例为合法 JSON，不含注释；下列可选项可省略）：

| 字段 | 说明 |
|---|---|
| `meta.birth` | ISO 日期；只知年份时写年份（如 `"181"`），并在 `birth_note` 说明 |
| `meta.sources[].kind` | `primary` / `scholarly` / `secondary` / `popular` 之一 |
| `stages` | 4–8 个人生阶段，配乐和章节卡按阶段切换；`mood_hint` 供配乐参考 |
| `steps[].id` | `<year>H<1\|2>`，按时间顺序排列 |
| `steps[].places` | 本半年依次到过的地点键（至少一个），最后一个是半年结束时所在地 |
| `steps[].event` | 简洁中文，≤60 字 |
| `steps[].confidence` | `documented`（史料明载）/ `inferred`（前后推断，如仍在任上）/ `traditional`（传说或晚出记载） |
| `steps[].sources` | `meta.sources` 中的 id |
| `steps[].milestone` | 可选，只有人生里程碑才有 |
| `milestone.importance` | `1` = 人生转折（重点讲），`2` = 重要事件 |
| `milestone.place` | 可选：里程碑停留讲解的地点（默认 `places` 最后一个）；其后的地点在讲完后继续走 |
| `milestone.quote` | 可选，必须是原文 |
| `steps[].note` | 可选：史料分歧说明 |

## `places.json`

```json
{
  "huzhou": {
    "name": "湖州",
    "modern": "浙江湖州",
    "lat": 30.893,
    "lon": 120.088,
    "kind": "city",
    "confidence": "high",
    "source": "OSM Nominatim relation 123456",
    "note": "例如今址存在争议",
    "same_as": "beijing"
  }
}
```

| 字段 | 说明 |
|---|---|
| `name` | 画面上显示的主名（用当时的称谓） |
| `modern` | 今地名，与 `name` 相同时也要填 |
| `kind` | `city` / `town` / `village` / `mountain` / `pass` / `river` / `battle` / `lake` / `foreign` 之一 |
| `confidence` | `high` / `medium` / `low` 之一 |
| `source` | Nominatim/Overpass 条目或考证说明 |
| `note` | 可选 |
| `same_as` | 可选：同一地点改名时指向原地点键（如 `beiping` → `beijing`），足迹计数只算一处 |

规则：
- 每个地点键都必须在 `places.json` 中存在。坐标通过 Nominatim（不超过 1 次/秒，带 User-Agent）或 Overpass 核验，古地名取学界公认的今址。
- 查不到确切今址时取所属县城，`confidence` 写 low 并在 `note` 中说明。不得臆造。
- 境外地点（如莫斯科）照常给坐标，`kind` 写 `foreign`。

## `person.json`

每个人物的配置，由 `src/person.js`（浏览器端）和 `tools/person.py`（`validate()`，严格校验：缺字段、未知字段、类型或顺序不对都会抛错）读取。半年键写作 `YYYYH1`/`YYYYH2`（如 `744H1`，负数表示公元前）。

```json
{
  "name": "苏轼",
  "life": "1037 — 1101",
  "tagline": "一蓑烟雨任平生 · 半年一步",
  "color": "#f0b84a",
  "glow": "#ffe2a0",
  "age": {"kind": "xusui", "lunar_birth_year": 1036},
  "birth_override": {"era": "北宋 · 景祐三年", "age": "虚岁 1"},
  "eras": [["北宋 · ", "景祐", 1034, "1037H1"], ["北宋 · ", "宝元", 1038, "1039H1"]],
  "era_overrides": [{"from": "1100H1", "to": null, "template": "北宋 · 元符三年"}],
  "regions": [{"name": "辽", "lon": 118.5, "lat": 43.6, "from": null, "to": null}],
  "extra_levels": [["hi_japan", 0]],
  "voice": {"name": "zh-CN-YunxiNeural", "rate": "-6%", "pitch": "-1Hz"},
  "span": ["1037H1", "1101H2"],
  "targets": {"duration_min": [7, 10], "min_milestones": 12},
  "_note": "自由备注，不参与校验"
}
```

必填：`name` `life` `tagline` `color` `glow` `age` `eras` `voice` `span` `targets`；可选：`birth_override` `era_overrides` `regions` `extra_levels` `_note`；出现其他字段会报错。

| 字段 | 规则 |
|---|---|
| `name` | 非空字符串，片头显示，并用于输出文件名 `<name>_人生轨迹.mp4`，**不得含 `/` 或 `\`** |
| `life` `tagline` | 非空字符串 |
| `color` `glow` | `#RRGGBB`，轨迹主色与光晕色 |
| `age` | `{"kind":"xusui","lunar_birth_year":整数}`（虚岁，古人，显示 `虚岁 N`，N = 年 − 出生年 + 1）；或 `{"kind":"zhousui","birth":"YYYY-MM-DD"}`（周岁，近人，按半年中点 4/1、10/1 计算）。出生年不得晚于 span 起始年 |
| `birth_override` | 可选，`{"era":字符串,"age":字符串}`，两项都要，覆盖出生步的纪年/年龄文字 |
| `eras` | 非空；每行 `[前缀, 年号名, 元年(整数), 生效半年]`。显示文字 = 前缀 + 年号名 + 中文序数 + `年`，**四段逐字拼接**，所以有朝代前缀时要带分隔符，写成 `"北宋 · "`（含空格和间隔点）；不需要前缀时写空字符串 `""`（如民国：`["", "民国", 1912, "1912H1"]` 显示“民国三十八年”）。序数 = 年 − 元年 + 1（1 显示为"元"），**校验保证每行在其生效期内（到下一行生效前，最后一行到 span 末）序数不超过 199**（序数只支持 1–199，不考虑 `era_overrides`）。元年不得晚于生效半年所在年；第一行生效半年不得晚于 span 起点；取"最后一个已生效的行" |
| `era_overrides` | 可选，`{from, to, template}`，`from`/`to` 为半年键或 `null`（无界），含端点；命中时整串替换纪年。`template` 中 `{n:Y}` → (年 − Y + 1) 的中文序数，在区间起点（`from` 为 null 时取 span 起点）处必须为正；区间不得重叠，`from` 不晚于 `to` |
| `regions` | 可选，`{name, lon, lat, from, to}` 五项齐全，该时段内在地图上标注政权/地域名；`from`/`to` 可为 `null` |
| `extra_levels` | 可选，`[图层名, 偏移]`，插在高清层之后、粗层之前的额外地形层 |
| `voice` | edge-tts：`name`、`rate`、`pitch` 均为字符串 |
| `span` | `[第一步, 最后一步]`，必须等于 `steps.json` 首尾 id |
| `targets` | `duration_min`: `[lo, hi]` 分钟，lo < hi；`min_milestones`: 整数 ≥ 1 |
| `_note` | 自由文本，不参与校验 |

规则：
- 年号表按生效半年升序；特殊纪年（改称"载"、两个年号并列、不再显示纪年）一律用 `era_overrides` 表达，不改代码。
- 新增人物后先跑 `python3 -m pytest -q tests/test_data.py tests/test_person.py -k <who>`（数据与配置）；全量 `python3 -m pytest -q tests -k <who>` 要等旁白、时间轴和配乐配置都写好后才能通过，通过后才渲染。

## 需要新的高清地形层时

共享高清层（`zhuge_hi` `hi_north` `hi_east` `hi_south` `hi_japan`）覆盖不到某人的地点时，生成一层新的，再写进 `person.json` 的 `extra_levels`。在项目根目录依次运行（`assets/terrain` 是通过符号链接指向的共享缓存）：

```
python3 tools/fetch_dem.py <name> <lon0> <lon1> <lat0> <lat1> 10 <tex_w>
python3 tools/fetch_imagery.py <name> 10
python3 tools/make_texture.py <name> <grid_w> --sat
touch assets/terrain/<name>.ok
```

尺寸规则：`tex_w ≈ lon_span × 111.32 × cos(mid_lat) ÷ 0.15`，`grid_w ≈ tex_w ÷ 5`。

范例 `hi_japan`：经度 135.5–141.5，纬度 34–38.5，即 `fetch_dem.py hi_japan 135.5 141.5 34 38.5 10 3600`，`make_texture.py hi_japan 720 --sat`。

最后在 `person.json` 里加 `"extra_levels": [["hi_japan", 0]]`（图层名，偏移）。
