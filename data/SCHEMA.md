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
    "birth": "1037-01-08",            // ISO 格式；只知年份时写 "181"，birth_note 说明
    "birth_note": "景祐三年十二月十九日",
    "death": "1101-08-24",
    "death_note": "建中靖国元年七月二十八日",
    "calendar_note": "…半年划分方法…",
    "sources": [ {"id": "S1", "title": "《宋史·苏轼传》", "url": "https://…", "kind": "primary|scholarly|secondary|popular"} ]
  },
  "stages": [ // 4–8 个人生阶段，配乐和章节卡按阶段切换
    {"id": "st1", "title": "眉山少年", "from": "1037H1", "to": "1056H1",
     "summary": "一句话概括", "mood_hint": "这一阶段的性格与处境，供配乐参考"}
  ],
  "steps": [
    {
      "id": "1079H2",                  // <year>H<1|2>，按时间顺序排列
      "places": ["huzhou", "kaifeng"], // 本半年依次到过的地点键（至少一个）；最后一个是半年结束时所在地
      "event": "七月在湖州被捕，八月押至汴京御史台狱（乌台诗案）",  // 简洁中文，≤60 字
      "confidence": "documented",      // documented=史料明载 | inferred=前后推断（如仍在任上）| traditional=传说或晚出记载
      "sources": ["S1", "S3"],         // meta.sources 中的 id
      "stage": "st4",
      "milestone": {                   // 可选，只有人生里程碑才有
        "title": "乌台诗案",
        "subtitle": "因诗获罪，下御史台狱一百三十天",
        "importance": 1,               // 1=人生转折（重点讲） 2=重要事件
        "place": "kaifeng",            // 可选：里程碑停留讲解的地点（默认 places 最后一个）；其后的地点在讲完后继续走
        "quote": {"text": "是处青山可埋骨，他年夜雨独伤神。", "source": "《狱中寄子由》"}  // 可选，必须是原文
      },
      "note": "可选：史料分歧说明"
    }
  ],
  "contested": [ {"topic": "…", "views": ["说法一（来源）", "说法二（来源）"], "adopted": "采用哪种以及理由"} ]
}
```

## `places.json`

```json
{
  "huzhou": {
    "name": "湖州",            // 画面上显示的主名（用当时的称谓）
    "modern": "浙江湖州",      // 今地名，与 name 相同时也要填
    "lat": 30.893, "lon": 120.088,
    "kind": "city|town|village|mountain|pass|river|battle|lake|foreign",
    "confidence": "high|medium|low",
    "source": "OSM Nominatim relation 123456 / 考证说明",
    "note": "可选，例如今址存在争议",
    "same_as": "可选：同一地点改名时指向原地点键（如 beiping → beijing），足迹计数只算一处"
  }
}
```

规则：
- 每个地点键都必须在 `places.json` 中存在。坐标通过 Nominatim（不超过 1 次/秒，带 User-Agent）或 Overpass 核验，古地名取学界公认的今址。
- 查不到确切今址时取所属县城，`confidence` 写 low 并在 `note` 中说明。不得臆造。
- 境外地点（如莫斯科）照常给坐标，`kind` 写 `foreign`。

## `person.json`

每个人物的配置，由 `src/person.js`（浏览器端）和 `tools/person.py`（`validate()`，严格校验：缺字段、未知字段、类型或顺序不对都会抛错）读取。半年键写作 `YYYYH1`/`YYYYH2`（如 `744H1`，负数表示公元前）。

```json
{
  "name": "苏轼",                       // 必填，非空字符串，片头与成片文件名使用
  "life": "1037–1101",                  // 必填，非空字符串，生卒年显示
  "tagline": "一句话概括",              // 必填，非空字符串
  "color": "#d4a24c",                   // 必填，#RRGGBB，轨迹主色
  "glow": "#ffd98a",                    // 必填，#RRGGBB，光晕色
  "age": {"kind": "xusui", "lunar_birth_year": 1037},   // 必填；或 {"kind": "zhousui", "birth": "1893-12-26"}
  "birth_override": {"era": "…", "age": "…"},           // 可选，出生步的纪年/年龄文字覆盖，两个字段都是字符串
  "eras": [["宋", "景祐", 1034, "1037H1"]],             // 必填，非空
  "era_overrides": [{"from": "1100H1", "to": null, "template": "元符三年"}],  // 可选
  "regions": [{"name": "…", "lon": 113.0, "lat": 34.0, "from": "1000H1", "to": null}],  // 可选
  "extra_levels": [["hi_north", 0]],    // 可选
  "voice": {"name": "zh-CN-YunjianNeural", "rate": "+0%", "pitch": "+0Hz"},   // 必填，edge-tts，三项均为字符串
  "span": ["1037H1", "1101H2"],         // 必填，[第一步, 最后一步]，必须等于 steps.json 首尾 id
  "targets": {"duration_min": [4.5, 6], "min_milestones": 8},   // 必填
  "_note": "自由备注，不参与校验"        // 可选
}
```

字段规则：
- `age`：`xusui`（虚岁，古人）显示 `虚岁 N`，N = 年 − `lunar_birth_year` + 1，`lunar_birth_year` 为整数且不晚于 span 起始年；`zhousui`（周岁，近人）要 `birth`（`YYYY-MM-DD`，不晚于 span 起始年），按半年中点 4/1 与 10/1 计算。
- `eras`：每行 `[前缀, 年号名, 元年(整数), 生效半年]`，显示为 `前缀+年号名+中文序数+年`，序数 = 年 − 元年 + 1（1 → 元，范围 1–199）。元年不得晚于生效半年所在年；第一行生效半年不得晚于 span 起点。取"最后一个已生效的行"。
- `era_overrides`：`{from, to, template}`，`from`/`to` 含端点，`null` 表示无界；命中时整串替换纪年。`template` 中的 `{n:Y}` 替换为 (年 − Y + 1) 的中文序数，在区间起点（`from` 为 null 时取 span 起点）处必须为正；各区间不得重叠，`from` 不晚于 `to`。
- `regions`：`{name, lon, lat, from, to}` 五项齐全，画面上在该时段内于地图上标注政权/地域名；`from`/`to` 可为 `null`。
- `extra_levels`：`[图层名, 偏移]`，插入到高清层之后、粗层之前的额外地形层（图层需存在于 `assets/terrain`）。
- `span`：`[first, last]`，first 不晚于 last。
- `targets.duration_min`：成片时长范围 `[lo, hi]`（分钟，lo < hi）；`targets.min_milestones`：里程碑最少个数（整数 ≥ 1）。

规则：
- 年号表按生效半年升序；特殊纪年（改称"载"、两个年号并列、不再显示纪年）一律用 `era_overrides` 表达，不改代码。
- 新增人物后先跑 `python3 -m pytest -q tests -k <who>`，校验不过不要渲染。
