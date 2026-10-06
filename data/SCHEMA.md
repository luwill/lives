# 人生轨迹数据规范

每个人物一个目录：`data/<who>/`，`who` ∈ `mao` | `zhuge` | `sushi` | `libai` | `zhuyz` | `jiang`。坐标一律为 WGS84 十进制度。

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
    "note": "可选，例如今址存在争议"
  }
}
```

规则：
- 每个地点键都必须在 `places.json` 中存在。坐标通过 Nominatim（不超过 1 次/秒，带 User-Agent）或 Overpass 核验，古地名取学界公认的今址。
- 查不到确切今址时取所属县城，`confidence` 写 low 并在 `note` 中说明。不得臆造。
- 境外地点（如莫斯科）照常给坐标，`kind` 写 `foreign`。
