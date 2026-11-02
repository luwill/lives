# 人生轨迹视频 skill 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `lives/` 的人生轨迹视频流水线打包成 `~/.claude/skills/life-trajectory-video`（仅限中国历史人物），并用粟裕做一次“裸 Opus vs 带 skill”的 A/B 评测。

**Architecture:** 先在 `lives/` 里做“去人物化”：人物配置从 `src/people.js` 和散落在工具、测试里的表，挪到每人一份 `data/<who>/person.json`，由 JS 的 `src/person.js` 和 Python 的 `tools/person.py` 读取。六人的年龄和纪年用迁移前导出的基线快照锁住。然后把通用代码复制成 skill 模板，配上 `new_project.sh`、`setup_terrain.sh`、环境检查和流程文档，用模板重建苏轼验收，最后跑 A/B 评测。

**Tech Stack:** three.js 0.170、playwright-core 1.63、Node ESM、Python 3（numpy、scipy、Pillow、edge-tts、pytest）、ffmpeg、zsh。

**设计文档:** `lives/docs/specs/2026-11-02-life-trajectory-skill-design.md`

**约定:** 所有命令默认在 `/Users/louwill/Vibing/daily-test/opus5.5-video-test/lives` 下运行。半年键写作 `"YYYYH1"`/`"YYYYH2"`，半年序号为 `idx = 年 × 2 + 半 − 1`。

---

## 文件结构

**lives/ 中新建**
- `data/<who>/person.json` ×6：人物配置（显示、年龄、年号、覆盖规则、政权注记、声线、生卒半年、指标）
- `src/person.js`：person.json → 运行时对象（`makePerson`、`cnNum`、`halfIdx`）
- `tools/person.py`：Python 侧读取配置（`people()`、`load_person()`、`voice_of()`）
- `tools/export_era_baseline.mjs`：迁移前导出年龄/纪年基线（一次性工具）
- `tests/fixtures/era_baseline.json`：六人基线快照
- `tests/test_person.py`：配置校验 + 基线比对
- `tests/test_lives_specific.py`：只属于这六人的锚点测试（不进模板）

**lives/ 中修改**
- `src/main.js`：改为读 person.json
- `src/people.js`：删除
- `render.mjs`：Chromium 路径自动查找
- `tools/tts.py`、`tools/check_outputs.py`、`tools/assemble.sh`、`tools/contact_sheet.sh`、`tools/smoke.mjs`：人名、声线、指标改读配置
- `tests/conftest.py`、`tests/test_data.py`、`tests/test_timeline.py`、`tests/test_js.py`：人物名单和指标改读配置；特定人物测试移走

**skill 新建（`~/.claude/skills/life-trajectory-video/`）**
- `SKILL.md`、`references/{schema,research-brief,factcheck-brief,narration,pitfalls}.md`
- `template/`（从 lives 复制的通用代码）
- `scripts/new_project.sh`、`scripts/setup_terrain.sh`、`template/tools/check_env.py`

**评测**
- `../ab/decisions-suyu.md`、`../ab/bare/`、`../ab/skill/`、`docs/evidence/ab-suyu.md`

---

### Task 0: 提交上一轮遗留改动

上一轮（HUD 减负、轨迹渐变、高清层、东京修复）还没提交。先提交，让后续每个任务的 diff 干净。

**Files:** 无新改动

- [ ] **Step 1: 确认测试全过**

Run: `python3 -m pytest -q tests`
Expected: `107 passed`

- [ ] **Step 2: 征得用户同意后提交**（用户规则：commit 前确认）

```bash
git add src tests tools/make_texture.py docs/runs/2026-11-02-polish.md docs/specs docs/plans assets/terrain/hi_*.json assets/terrain/hi_*_h.bin assets/terrain/hi_*_tex.jpg
git commit -m "feat: hi-res satellite layers for all lives, decluttered HUD, trail fade and life replay

Review of the six films: close-ups outside Zhuge's region were blurry, the
HUD showed six text zones at once, and old trail segments cut across close-ups.
Tokyo was projected into the Sea of Japan because the map box ignored the
world layer's real extent.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 1: 导出年龄/纪年基线快照

迁移会改写所有人的年龄和纪年逻辑，先把现状存成快照，迁移后要求逐字一致。

**Files:**
- Create: `tools/export_era_baseline.mjs`
- Create: `tests/fixtures/era_baseline.json`

- [ ] **Step 1: 写导出脚本**

```js
// 一次性工具：用迁移前的 src/people.js 导出六人每个半年步的 [年龄, 纪年] 与出生覆盖，存为基线
// 用法（在 lives/ 下）：node tools/export_era_baseline.mjs > tests/fixtures/era_baseline.json
import fs from 'node:fs';
import { PEOPLE } from '../src/people.js';

const out = {};
for (const who of Object.keys(PEOPLE)) {
  const p = PEOPLE[who];
  const steps = JSON.parse(fs.readFileSync(`data/${who}/steps.json`)).steps;
  const rows = {};
  for (const s of steps) {
    const [, y, h] = s.id.match(/^(\d+)H([12])$/);
    rows[s.id] = [p.age(+y, +h), p.era(+y, +h)];
  }
  out[who] = { rows, birth: p.birth || null };
}
console.log(JSON.stringify(out, null, 1));
```

- [ ] **Step 2: 运行导出**

Run: `mkdir -p tests/fixtures && node tools/export_era_baseline.mjs > tests/fixtures/era_baseline.json && python3 -c "import json;d=json.load(open('tests/fixtures/era_baseline.json'));print({k:len(v['rows']) for k,v in d.items()})"`
Expected: `{'mao': 167, 'zhuge': 108, 'sushi': 130, 'libai': 124, 'zhuyz': 140, 'jiang': 176}`

- [ ] **Step 3: 提交**

```bash
git add tools/export_era_baseline.mjs tests/fixtures/era_baseline.json
git commit -m "test: snapshot ages and eras of all six lives before config migration

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: 六人的 person.json

**Files:**
- Create: `data/mao/person.json`、`data/zhuge/person.json`、`data/sushi/person.json`、`data/libai/person.json`、`data/zhuyz/person.json`、`data/jiang/person.json`

字段说明（同时写进 `data/SCHEMA.md`，见 Task 7）：
- `age`：`{"kind":"xusui","lunar_birth_year":N}` 或 `{"kind":"zhousui","birth":"YYYY-MM-DD"}`
- `eras`：`[前缀, 年号, 元年, 生效半年]`，按生效半年升序；当前半年取最后一个已生效的行，显示为 `前缀 + 年号 + 中文序数 + 年`
- `era_overrides`：`{"from": 半年或 null, "to": 半年或 null（含）, "template": 文本}`，命中时整串替换；模板里的 `{n:Y}` 替换为 `cnNum(当年 − Y + 1)`
- `regions`：`{"name","lon","lat","from","to"}`，`from`/`to` 为半年或 null（含两端）
- `extra_levels`：插在共享高清层和粗层之间的额外地形层
- `voice`：edge-tts 的 `name`、`rate`、`pitch`
- `span`：首末半年；`targets`：`duration_min: [下限, 上限]`、`min_milestones`

- [ ] **Step 1: 写 `data/mao/person.json`**

```json
{
 "name": "毛泽东", "life": "1893 — 1976", "tagline": "一个人的八十二年 · 半年一步",
 "color": "#e8473a", "glow": "#ff8a5c",
 "age": {"kind": "zhousui", "birth": "1893-12-26"},
 "eras": [["清 · ", "光绪", 1875, "1875H1"], ["清 · ", "宣统", 1909, "1909H1"], ["", "民国", 1912, "1912H1"]],
 "era_overrides": [{"from": "1949H2", "to": null, "template": "中华人民共和国"}],
 "regions": [],
 "voice": {"name": "zh-CN-YunyangNeural", "rate": "-6%", "pitch": "-2Hz"},
 "span": ["1893H2", "1976H2"],
 "targets": {"duration_min": [9, 13], "min_milestones": 15}
}
```

- [ ] **Step 2: 写 `data/zhuge/person.json`**

```json
{
 "name": "诸葛亮", "life": "181 — 234", "tagline": "鞠躬尽瘁 · 半年一步",
 "color": "#4fc1b0", "glow": "#9ff0e2",
 "age": {"kind": "xusui", "lunar_birth_year": 181},
 "eras": [["东汉 · ", "光和", 178, "181H1"], ["东汉 · ", "中平", 184, "185H1"], ["东汉 · ", "初平", 190, "190H1"],
          ["东汉 · ", "兴平", 194, "194H1"], ["东汉 · ", "建安", 196, "196H1"], ["蜀汉 · ", "章武", 221, "221H1"],
          ["蜀汉 · ", "建兴", 223, "223H2"]],
 "era_overrides": [],
 "regions": [{"name": "曹 魏", "lon": 114.2, "lat": 35.2, "from": "220H2", "to": null},
             {"name": "蜀 汉", "lon": 104.6, "lat": 30.9, "from": "221H1", "to": null},
             {"name": "孙 吴", "lon": 117.8, "lat": 28.4, "from": "222H2", "to": null}],
 "voice": {"name": "zh-CN-YunyangNeural", "rate": "-16%", "pitch": "-6Hz"},
 "span": ["181H1", "234H2"],
 "targets": {"duration_min": [13, 17], "min_milestones": 10}
}
```

- [ ] **Step 3: 写 `data/sushi/person.json`**

```json
{
 "name": "苏轼", "life": "1037 — 1101", "tagline": "一蓑烟雨任平生 · 半年一步",
 "color": "#f0b84a", "glow": "#ffe2a0",
 "age": {"kind": "xusui", "lunar_birth_year": 1036},
 "birth_override": {"era": "北宋 · 景祐三年", "age": "虚岁 1"},
 "eras": [["北宋 · ", "景祐", 1034, "1037H1"], ["北宋 · ", "宝元", 1038, "1039H1"], ["北宋 · ", "康定", 1040, "1040H1"],
          ["北宋 · ", "庆历", 1041, "1042H1"], ["北宋 · ", "皇祐", 1049, "1049H1"], ["北宋 · ", "至和", 1054, "1054H1"],
          ["北宋 · ", "嘉祐", 1056, "1056H2"], ["北宋 · ", "治平", 1064, "1064H1"], ["北宋 · ", "熙宁", 1068, "1068H1"],
          ["北宋 · ", "元丰", 1078, "1078H1"], ["北宋 · ", "元祐", 1086, "1086H1"], ["北宋 · ", "绍圣", 1094, "1094H2"],
          ["北宋 · ", "元符", 1098, "1098H2"], ["北宋 · ", "建中靖国", 1101, "1101H1"]],
 "era_overrides": [],
 "regions": [{"name": "辽", "lon": 118.5, "lat": 43.6, "from": null, "to": null},
             {"name": "西 夏", "lon": 105.6, "lat": 38.9, "from": null, "to": null},
             {"name": "大 理", "lon": 100.4, "lat": 25.4, "from": null, "to": null}],
 "voice": {"name": "zh-CN-YunxiNeural", "rate": "-6%", "pitch": "-1Hz"},
 "span": ["1037H1", "1101H2"],
 "targets": {"duration_min": [7, 10], "min_milestones": 12}
}
```

- [ ] **Step 4: 写 `data/libai/person.json`**

旧逻辑把 744H1–756H1 的“天宝X年”和 756H2–757H2 的“至德X年”改称“载”，这里用两条覆盖规则表达。

```json
{
 "name": "李白", "life": "701 — 762", "tagline": "仗剑去国 · 半年一步",
 "color": "#7aa8ff", "glow": "#c4d8ff",
 "age": {"kind": "xusui", "lunar_birth_year": 701},
 "eras": [["武周 · ", "大足", 701, "701H1"], ["武周 · ", "长安", 701, "702H1"], ["唐 · ", "神龙", 705, "705H1"],
          ["唐 · ", "景龙", 707, "707H2"], ["唐 · ", "景云", 710, "710H2"], ["唐 · ", "太极", 712, "712H1"],
          ["唐 · ", "先天", 712, "712H2"], ["唐 · ", "开元", 713, "714H1"], ["唐 · ", "天宝", 742, "742H1"],
          ["唐 · ", "至德", 756, "756H2"], ["唐 · ", "乾元", 758, "758H1"], ["唐 · ", "上元", 760, "760H2"],
          ["唐 · ", "宝应", 762, "762H1"]],
 "era_overrides": [{"from": "744H1", "to": "756H1", "template": "唐 · 天宝{n:742}载"},
                   {"from": "756H2", "to": "757H2", "template": "唐 · 至德{n:756}载"}],
 "regions": [{"name": "突 厥", "lon": 104.0, "lat": 46.0, "from": null, "to": "744H1"},
             {"name": "回 纥", "lon": 104.0, "lat": 46.0, "from": "744H2", "to": null},
             {"name": "吐 蕃", "lon": 91.0, "lat": 31.5, "from": null, "to": null},
             {"name": "南 诏", "lon": 100.2, "lat": 25.6, "from": "738H1", "to": null}],
 "voice": {"name": "zh-CN-YunxiNeural", "rate": "-4%", "pitch": "+0Hz"},
 "span": ["701H1", "762H2"],
 "targets": {"duration_min": [7, 10], "min_milestones": 10}
}
```

- [ ] **Step 5: 写 `data/zhuyz/person.json`**

```json
{
 "name": "朱元璋", "life": "1328 — 1398", "tagline": "布衣天子 · 半年一步",
 "color": "#e0a030", "glow": "#ffd27a",
 "age": {"kind": "xusui", "lunar_birth_year": 1328},
 "eras": [["元 · ", "天历", 1328, "1328H2"], ["元 · ", "至顺", 1330, "1330H2"], ["元 · ", "元统", 1333, "1334H1"],
          ["元 · ", "至元", 1335, "1336H1"], ["元 · ", "至正", 1341, "1341H1"], ["明 · ", "洪武", 1368, "1368H1"]],
 "era_overrides": [{"from": "1355H1", "to": "1366H2", "template": "龙凤{n:1355}年 · 元至正{n:1341}年"},
                   {"from": "1367H1", "to": "1367H2", "template": "吴元年 · 元至正二十七年"}],
 "regions": [{"name": "元", "lon": 112.5, "lat": 41.2, "from": null, "to": "1368H1"},
             {"name": "陈友谅", "lon": 115.0, "lat": 30.3, "from": "1360H1", "to": "1363H2"},
             {"name": "张士诚", "lon": 120.3, "lat": 32.1, "from": "1356H1", "to": "1367H2"},
             {"name": "方国珍", "lon": 121.3, "lat": 28.8, "from": "1356H1", "to": "1367H2"},
             {"name": "夏（明玉珍）", "lon": 106.6, "lat": 30.2, "from": "1362H1", "to": "1371H1"},
             {"name": "北 元", "lon": 110.5, "lat": 44.5, "from": "1368H2", "to": null}],
 "voice": {"name": "zh-CN-YunjianNeural", "rate": "-8%", "pitch": "-5Hz"},
 "span": ["1328H2", "1398H1"],
 "targets": {"duration_min": [8, 11], "min_milestones": 10}
}
```

- [ ] **Step 6: 写 `data/jiang/person.json`**

```json
{
 "name": "蒋介石", "life": "1887 — 1975", "tagline": "一个人的八十七年 · 半年一步",
 "color": "#5b8fd8", "glow": "#a9c6f0",
 "age": {"kind": "zhousui", "birth": "1887-10-31"},
 "eras": [["清 · ", "光绪", 1875, "1875H1"], ["清 · ", "宣统", 1909, "1909H1"], ["", "民国", 1912, "1912H1"]],
 "era_overrides": [{"from": "1949H2", "to": null, "template": ""}],
 "regions": [],
 "extra_levels": [["hi_japan", 0]],
 "voice": {"name": "zh-CN-YunyangNeural", "rate": "-6%", "pitch": "-3Hz"},
 "span": ["1887H2", "1975H1"],
 "targets": {"duration_min": [9, 13], "min_milestones": 15}
}
```

- [ ] **Step 7: 确认六个文件都是合法 JSON**

Run: `for w in mao zhuge sushi libai zhuyz jiang; do python3 -m json.tool data/$w/person.json > /dev/null && echo "$w ok"; done`
Expected: 六行 `ok`

（这一步不提交，和 Task 3 一起提交。）

---

### Task 3: `src/person.js` 并通过基线比对

**Files:**
- Create: `src/person.js`
- Create: `tests/test_person.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: 把 node 调用与人物名单挪进 conftest**

把 `tests/conftest.py` 改为：

```python
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from person import load_person, people  # noqa: E402

PEOPLE = people()


def load(who: str, name: str):
    return json.loads((ROOT / 'data' / who / name).read_text())


def node(code: str):
    """在 src/ 下用 node 执行 ESM 片段，返回其 stdout 的 JSON。"""
    out = subprocess.run(['node', '--input-type=module', '-e', code], cwd=ROOT / 'src', capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def ages(who: str) -> dict:
    """每个半年步的 [年龄, 纪年]，以及出生覆盖（由 person.json 经 makePerson 计算）。"""
    ids = [s['id'] for s in load(who, 'steps.json')['steps']]
    return node(f"""import {{ makePerson }} from './person.js';
import fs from 'node:fs';
const p = makePerson(JSON.parse(fs.readFileSync('../data/{who}/person.json'))), out = {{}};
for (const id of {json.dumps(ids)}) {{ const [, y, h] = id.match(/^(\\d+)H(\\d)$/); out[id] = [p.age(+y, +h), p.era(+y, +h)]; }}
out.birth = p.birth || null;
console.log(JSON.stringify(out));""")


@pytest.fixture(params=PEOPLE)
def who(request):
    if not (ROOT / 'data' / request.param / 'steps.json').exists():
        pytest.fail(f'data/{request.param}/steps.json missing')
    return request.param
```

- [ ] **Step 2: 写 `tools/person.py`**

```python
"""人物配置读取：data/<who>/person.json（测试、TTS、总装、成片检查共用）。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ('name', 'life', 'tagline', 'color', 'glow', 'age', 'eras', 'voice', 'span', 'targets')


def people() -> list[str]:
    """data/ 下所有带 person.json 的人物键，按字母排序。"""
    return sorted(p.parent.name for p in (ROOT / 'data').glob('*/person.json'))


def load_person(who: str) -> dict:
    p = ROOT / 'data' / who / 'person.json'
    if not p.exists():
        raise FileNotFoundError(f'{p} missing')
    cfg = json.loads(p.read_text())
    missing = [k for k in REQUIRED if k not in cfg]
    if missing:
        raise ValueError(f'{p}: missing fields {missing}')
    return cfg


def voice_of(who: str) -> tuple[str, str, str]:
    v = load_person(who)['voice']
    return v['name'], v['rate'], v['pitch']
```

- [ ] **Step 3: 写失败测试 `tests/test_person.py`**

```python
"""person.json 校验，以及迁移前后年龄/纪年逐字一致（tests/fixtures/era_baseline.json）。"""
import json
import re

import pytest

from conftest import ROOT, ages, load
from person import load_person

HALF = re.compile(r'^-?\d+H[12]$')
BASELINE = ROOT / 'tests' / 'fixtures' / 'era_baseline.json'


def test_person_config_valid(who):
    cfg = load_person(who)
    assert cfg['age']['kind'] in ('xusui', 'zhousui')
    keys = [r[3] for r in cfg['eras']]
    assert all(HALF.match(k) for k in keys)
    idx = [int(k[:-2]) * 2 + int(k[-1]) - 1 for k in keys]
    assert idx == sorted(idx), 'eras 必须按生效半年升序'
    for o in cfg.get('era_overrides', []):
        assert all(v is None or HALF.match(v) for v in (o['from'], o['to']))
    for r in cfg.get('regions', []):
        assert all(v is None or HALF.match(v) for v in (r['from'], r['to']))
    steps = load(who, 'steps.json')['steps']
    assert [steps[0]['id'], steps[-1]['id']] == cfg['span']


def test_ages_and_eras_match_baseline(who):
    if not BASELINE.exists():
        pytest.skip('no baseline in this project')
    base = json.loads(BASELINE.read_text()).get(who)
    if base is None:
        pytest.skip(f'{who} not in baseline')
    got = ages(who)
    assert got.pop('birth') == base['birth']
    diff = {k: (got.get(k), v) for k, v in base['rows'].items() if got.get(k) != v}
    assert not diff, dict(list(diff.items())[:5])
```

- [ ] **Step 4: 运行，确认失败**

Run: `python3 -m pytest -q tests/test_person.py`
Expected: FAIL，报错含 `Cannot find module` 或 `person.js`（文件还不存在）

- [ ] **Step 5: 写 `src/person.js`**

```js
// 人物配置（data/<who>/person.json）→ 运行时对象：年龄、纪年、政权注记、地形层
const NUM = '〇一二三四五六七八九';
export function cnNum(n) {
  if (n === 1) return '元';
  if (n < 10) return NUM[n];
  if (n < 20) return '十' + (n % 10 ? NUM[n % 10] : '');
  return NUM[Math.floor(n / 10)] + '十' + (n % 10 ? NUM[n % 10] : '');
}

// "744H1" → 半年序号 744*2+0
export function halfIdx(key) {
  const m = /^(-?\d+)H([12])$/.exec(key);
  if (!m) throw new Error(`bad half-year key: ${key}`);
  return +m[1] * 2 + +m[2] - 1;
}

// 共享高清层（z10，约 150 m/像素，卫星底色），同级按先后让位；再往下是粗层
const HI = [['zhuge_hi', 0], ['hi_north', 0], ['hi_east', 0], ['hi_south', 0]];
const BASE = [['east', -0.03], ['china', -0.06], ['world', -0.15]];

// 年龄：古人按虚岁（农历出生年记为一岁），近人按周岁（以半年中点 4/1、10/1 计）
function ageFn(a) {
  if (a.kind === 'xusui') return y => `虚岁 ${y - a.lunar_birth_year + 1}`;
  if (a.kind === 'zhousui') {
    const [by, bm, bd] = a.birth.split('-').map(Number);
    return (y, h) => {
      const [m, d] = h === 1 ? [4, 1] : [10, 1];
      return `${Math.max(0, y - by - (m < bm || (m === bm && d < bd) ? 1 : 0))} 岁`;
    };
  }
  throw new Error(`unknown age kind: ${a.kind}`);
}

// 纪年：年号表取最后一个已生效的行；覆盖规则命中时整串替换，{n:Y} → cnNum(当年 − Y + 1)
function eraFn(rows, overrides = []) {
  const table = rows.map(([prefix, name, first, eff]) => ({ prefix, name, first, k: halfIdx(eff) }));
  const ovs = overrides.map(o => ({ a: o.from ? halfIdx(o.from) : -Infinity, b: o.to ? halfIdx(o.to) : Infinity, t: o.template }));
  return (y, h) => {
    const k = y * 2 + h - 1;
    const o = ovs.find(v => k >= v.a && k <= v.b);
    if (o) return o.t.replace(/\{n:(-?\d+)\}/g, (_, base) => cnNum(y - +base + 1));
    let e = null;
    for (const r of table) if (k >= r.k) e = r;
    return e ? `${e.prefix}${e.name}${cnNum(y - e.first + 1)}年` : '';
  };
}

export function makePerson(cfg) {
  return {
    name: cfg.name, life: cfg.life, tagline: cfg.tagline, color: cfg.color, glow: cfg.glow,
    birth: cfg.birth_override || undefined,
    age: ageFn(cfg.age),
    era: eraFn(cfg.eras, cfg.era_overrides),
    regions: (cfg.regions || []).map(r => ({
      name: r.name, lon: r.lon, lat: r.lat,
      from: r.from ? halfIdx(r.from) : -Infinity, to: r.to ? halfIdx(r.to) : Infinity,
    })),
    levels: [...HI, ...(cfg.extra_levels || []), ...BASE],
  };
}
```

- [ ] **Step 6: 运行，确认通过**

Run: `python3 -m pytest -q tests/test_person.py`
Expected: `12 passed`（6 人 × 2 项）。如果基线比对失败，按报错里的半年步核对对应 person.json 的年号行或覆盖规则，不要改基线。

- [ ] **Step 7: 提交**

```bash
git add data/*/person.json src/person.js tools/person.py tests/conftest.py tests/test_person.py
git commit -m "refactor: move per-person config into data/<who>/person.json

A new person used to need edits in six places (people.js, tts voices,
assemble names, test lists and targets). Config is now data, checked by a
baseline snapshot that pins every age and era string of the six lives.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: 页面改读 person.json，删除 people.js

**Files:**
- Modify: `src/main.js:1-25`
- Delete: `src/people.js`

- [ ] **Step 1: 改 main.js 的导入与人物加载**

把

```js
import { PEOPLE } from './people.js';
```

替换为

```js
import { makePerson } from './person.js';
```

把

```js
const who = new URLSearchParams(location.search).get('who');
const person = PEOPLE[who] || (who === 'demo' ? PEOPLE.sushi : null);
if (!person) throw new Error(`unknown person: ${who}`);
```

替换为

```js
const who = new URLSearchParams(location.search).get('who');
if (!who || !/^[a-z0-9_]+$/.test(who)) throw new Error(`bad person key: ${who}`);
```

把 `Promise.all` 那一段改为同时读 person.json：

```js
const [cfg, data, places, tl, geo] = await Promise.all([
  getJson(`../data/${who}/person.json`),
  getJson(`../data/${who}/steps.json`), getJson(`../data/${who}/places.json`),
  getJson(`${who}/timeline.json`), getJson('../data/common/labels.json'),
]);
const person = makePerson(cfg);
```

- [ ] **Step 2: 删除 people.js，确认没有残留引用**

Run: `git rm src/people.js && grep -rn "people.js\|PEOPLE\[" src tools tests render.mjs`
Expected: 只剩 `tests/` 里待 Task 5 改的几处，`src/` 无输出

- [ ] **Step 3: 像素级回归：渲染前后静帧一致**

迁移不应改变任何画面。用 Task 0 提交时的代码渲染一组静帧作为参照，再与当前代码对比：

```bash
git stash -u && node render.mjs sushi still 23.8 287.7 && node render.mjs zhuyz still 242.2 && \
  for f in out/sushi/still_23.8 out/sushi/still_287.7 out/zhuyz/still_242.2; do cp $f.jpg $f.ref.jpg; done && git stash pop
node render.mjs sushi still 23.8 287.7 && node render.mjs zhuyz still 242.2
for f in out/sushi/still_23.8 out/sushi/still_287.7 out/zhuyz/still_242.2; do
  python3 -c "from PIL import Image, ImageChops; a=Image.open('$f.jpg'); b=Image.open('$f.ref.jpg'); print('$f', ImageChops.difference(a,b).getbbox())"; done
```

Expected: 三行都以 `None` 结尾（没有差异）。苏轼 23.8 s 是出生覆盖，287.7 s 是黄州；朱元璋 242.2 s 是龙凤与至正并列。

- [ ] **Step 4: 提交**

```bash
git add src/main.js
git commit -m "refactor: page builds the person from person.json

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: 测试与工具改读配置，拆出特定人物测试

**Files:**
- Modify: `tests/test_js.py`、`tests/test_data.py`、`tests/test_timeline.py`
- Create: `tests/test_lives_specific.py`
- Modify: `tools/tts.py`、`tools/check_outputs.py`、`tools/assemble.sh`、`tools/contact_sheet.sh`、`tools/smoke.mjs`

- [ ] **Step 1: 建 `tests/test_lives_specific.py`，把只属于六人的测试移进来**

从 `tests/test_js.py` 原样剪切这些函数到新文件：`test_age_and_era_anchors`、`test_mao_km_counts_real_moscow_distance`、`test_offmap_proxy_points_toward_moscow`、`test_age_and_era_anchors_second_batch`、`test_japan_on_map_and_cairo_at_west_edge`、`test_era_edges_second_batch`。从 `tests/test_data.py` 剪切 `TRAD` 常量和 `test_zhuge_quotes_simplified`。新文件开头：

```python
"""只属于 lives/ 六人的锚点测试（不进 skill 模板）：具体年龄、纪年、图外代理点、引文简体。"""
import json
import math

from conftest import ROOT, ages, load, node
```

在 `tests/test_js.py` 里删除本地的 `node`、`ages` 定义，开头改为：

```python
"""浏览器端纯函数（年龄、轨迹、回放）的通用检查：用 node 直接导入 src/*.js。"""
import json
import math

from conftest import ROOT, ages, load, node
```

- [ ] **Step 2: test_data 与 test_timeline 改读配置**

`tests/test_data.py`：删除 `SPAN`、`MIN_MILESTONES` 两个字典，导入 `from person import load_person`；`test_steps_cover_life_without_gaps` 里把 `a, b = SPAN[who]` 改为 `a, b = load_person(who)['span']`；`test_milestones` 里把 `MIN_MILESTONES[who]` 改为 `load_person(who)['targets']['min_milestones']`。

`tests/test_timeline.py`：删除 `TARGET_MIN` 字典，导入 `from person import load_person, voice_of`；`test_duration_in_target` 改为 `lo, hi = load_person(who)['targets']['duration_min']`；`test_narration_audio_matches_script` 里把 `voice, rate, pitch = TTS.VOICES[who]` 改为 `voice, rate, pitch = voice_of(who)`。

- [ ] **Step 3: tts.py 改用配置里的声线**

删除 `VOICES` 字典；在 import 区加 `from person import people, voice_of`（`tools/` 已在 sys.path，脚本直接运行时同目录可导入）。`main()` 第一行改为 `VOICE, RATE, PITCH = voice_of(who)`；入口的参数检查改为 `if len(args) != 1 or args[0] not in people():`。

- [ ] **Step 4: check_outputs.py 改读配置**

删除 `NAMES`、`TARGET_MIN`；加 `from person import load_person, people`。`check()` 里 `p = ROOT / f'{NAMES[who]}_人生轨迹.mp4'` 改为 `p = ROOT / f"{load_person(who)['name']}_人生轨迹.mp4"`，`lo, hi = TARGET_MIN[who]` 改为 `lo, hi = load_person(who)['targets']['duration_min']`。主循环 `for who in NAMES:` 改为 `for who in people():`，其中的 `NAMES[who]` 同样换成 `load_person(who)['name']`。

- [ ] **Step 5: 两个 zsh 脚本改读姓名**

`tools/assemble.sh` 和 `tools/contact_sheet.sh` 都删除 `typeset -A NAME=(...)` 这一行，换成：

```zsh
NAME=$(python3 -c "import sys; sys.path.insert(0, 'tools'); from person import load_person; print(load_person('$WHO')['name'])")
```

并把后面的 `${NAME[$WHO]}` 换成 `$NAME`。

- [ ] **Step 6: smoke.mjs 默认人物名单改为扫描 data/**

把第 5 行改为：

```js
import fs from 'node:fs';
const all = fs.readdirSync('data').filter(d => fs.existsSync(`data/${d}/person.json`)).sort();
const people = process.argv.slice(2).length ? process.argv.slice(2) : all;
```

（`import` 放到文件顶部，和已有的 import 放在一起。）

- [ ] **Step 7: 全量测试 + smoke + 一个人的总装演练**

Run: `python3 -m pytest -q tests && node tools/smoke.mjs && python3 tools/check_outputs.py --require | tail -6`
Expected: 测试全部通过（107 原有 + 12 新增，数量以输出为准，不应有 skip 以外的失败）；smoke 六行 `errors 0`；check_outputs 六行规格正常

- [ ] **Step 8: 提交**

```bash
git add tests tools
git commit -m "refactor: tools and tests read names, voices and targets from person.json

Person-specific anchors move to test_lives_specific.py so the generic
tests can ship in the skill template.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Chromium 自动查找与环境检查

**Files:**
- Modify: `render.mjs:11`
- Create: `tools/check_env.py`
- Test: `tests/test_env.py`

- [ ] **Step 1: render.mjs 的 CHROME 改为查找函数**

把

```js
export const CHROME = path.join(process.env.HOME, 'Library/Caches/ms-playwright/chromium-1243/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing');
```

替换为

```js
// Chromium：优先环境变量 LTV_CHROME，否则在 Playwright 缓存里取版本号最大的 chromium-*
export function findChrome() {
  if (process.env.LTV_CHROME) {
    if (!fs.existsSync(process.env.LTV_CHROME)) throw new Error(`LTV_CHROME not found: ${process.env.LTV_CHROME}`);
    return process.env.LTV_CHROME;
  }
  const cache = path.join(process.env.HOME, 'Library/Caches/ms-playwright');
  const rel = ['chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
    'chrome-mac/Chromium.app/Contents/MacOS/Chromium', 'chrome-linux/chrome'];
  const dirs = fs.existsSync(cache) ? fs.readdirSync(cache).filter(d => /^chromium-\d+$/.test(d))
    .sort((a, b) => +b.split('-')[1] - +a.split('-')[1]) : [];
  for (const d of dirs) for (const r of rel) { const p = path.join(cache, d, r); if (fs.existsSync(p)) return p; }
  throw new Error('Chromium not found: set LTV_CHROME or run `npx playwright install chromium`');
}
export const CHROME = findChrome();
```

- [ ] **Step 2: 写 `tools/check_env.py`**

```python
"""环境检查：一次列出所有缺失项（不自动安装）。用法：python3 tools/check_env.py；全部就绪时退出码 0。"""
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = ['numpy', 'scipy', 'PIL', 'edge_tts', 'pytest']
OPTIONAL_PY = {'lunar_python': '农历换算（研究阶段可用查表代替）'}


def missing() -> list[str]:
    out = [f'命令 {c}' for c in ('ffmpeg', 'ffprobe', 'node', 'curl') if not shutil.which(c)]
    out += [f'Python 包 {m}' for m in PY if importlib.util.find_spec(m) is None]
    for pkg in ('three', 'playwright-core'):
        if not (ROOT / 'node_modules' / pkg / 'package.json').exists():
            out.append(f'npm 包 {pkg}（在项目根目录运行 npm install）')
    r = subprocess.run(['node', '-e', "import('./render.mjs').then(m=>console.log(m.CHROME)).catch(e=>{console.error(e.message);process.exit(1)})"],
                       cwd=ROOT, capture_output=True, text=True) if shutil.which('node') else None
    if r is None or r.returncode != 0:
        out.append(f"Chromium（{r.stderr.strip() if r else 'node 缺失'}）")
    if not (ROOT / 'assets' / 'terrain' / 'world.json').exists():
        out.append('地形缓存（运行 scripts/setup_terrain.sh）')
    return out


def main() -> int:
    miss = missing()
    for m in miss:
        print('缺失：', m)
    for m, why in OPTIONAL_PY.items():
        if importlib.util.find_spec(m) is None:
            print(f'可选：{m} 未安装（{why}）')
    print('环境就绪' if not miss else f'共 {len(miss)} 项缺失')
    return 1 if miss else 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 3: 写测试 `tests/test_env.py`**

```python
"""check_env 在当前项目上应报告就绪（lives/ 是完整环境）。"""
import subprocess
import sys

from conftest import ROOT


def test_check_env_ready():
    r = subprocess.run([sys.executable, 'tools/check_env.py'], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert '环境就绪' in r.stdout
```

- [ ] **Step 4: 运行**

Run: `python3 -m pytest -q tests/test_env.py && LTV_CHROME=/nope node -e "import('./render.mjs')" 2>&1 | grep -c "LTV_CHROME not found"`
Expected: `1 passed`，随后输出 `1`

- [ ] **Step 5: 提交**

```bash
git add render.mjs tools/check_env.py tests/test_env.py
git commit -m "feat: locate Chromium automatically and check the environment up front

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: 搭建 skill 目录与模板

**Files:**
- Create: `~/.claude/skills/life-trajectory-video/template/...`（复制）
- Create: `~/.claude/skills/life-trajectory-video/scripts/new_project.sh`
- Create: `~/.claude/skills/life-trajectory-video/scripts/setup_terrain.sh`
- Modify: `data/SCHEMA.md`（加 person.json 一节，随后复制进模板）

- [ ] **Step 1: 在 `data/SCHEMA.md` 末尾追加 person.json 规范**

内容为 Task 2 开头“字段说明”的列表，加上两句规则：“年号表按生效半年升序；特殊纪年（改称‘载’、两个年号并列、不再显示纪年）一律用 era_overrides 表达，不改代码。”提交到 lives：

```bash
git add data/SCHEMA.md && git commit -m "docs: document person.json in the data schema

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 2: 复制模板**

```bash
S=~/.claude/skills/life-trajectory-video; T=$S/template
mkdir -p $T/{src,tools,music,tests,data/common,docs/runs,docs/evidence/stills,narration} $S/scripts $S/references
cp src/{camera,engine,hud,journey,main,mapfx,person}.js src/{style.css,index.html,package.json} $T/src/
cp tools/{build_timeline,tts,mix,check_outputs,audio_report,fetch_dem,fetch_imagery,make_texture,person,check_env}.py \
   tools/{assemble,render_all,contact_sheet}.sh tools/smoke.mjs $T/tools/
cp music/{score,orch}.py $T/music/
cp tests/{conftest,test_data,test_timeline,test_js,test_person,test_env}.py $T/tests/
cp data/SCHEMA.md $T/data/ && cp data/common/{labels.json,lakes.geojson,rivers.geojson} $T/data/common/
cp render.mjs .gitignore $T/
```

- [ ] **Step 3: 模板的 package.json（锁定版本）**

写 `$T/package.json`：

```json
{
  "name": "life-trajectory-project",
  "private": true,
  "type": "commonjs",
  "dependencies": { "three": "0.170.0", "playwright-core": "1.63.0" }
}
```

- [ ] **Step 4: 确认模板里没有人物特定内容**

Run: `grep -rnE "mao|zhuge|sushi|libai|zhuyz|jiang|毛泽东|诸葛|苏轼|李白|朱元璋|蒋介石" ~/.claude/skills/life-trajectory-video/template --include=*.py --include=*.js --include=*.mjs --include=*.sh | grep -v "zhuge_hi"`
Expected: 无输出。如有，属于注释里的举例可以保留但要改成泛称；属于逻辑的必须改掉。

- [ ] **Step 5: 写 `scripts/setup_terrain.sh`**

```zsh
#!/bin/zsh
# 准备共享地形缓存 ~/.cache/life-trajectory-video/terrain：
#   有种子目录（默认 lives/assets/terrain，或 LTV_TERRAIN_SEED）就复制成品层；否则下载生成（约 30–60 分钟）
# 用法：zsh setup_terrain.sh <项目目录>    （项目内 tools/ 提供 fetch_dem/fetch_imagery/make_texture）
set -euo pipefail
PROJ=${1:?usage: setup_terrain.sh <project-dir>}
CACHE=${LTV_TERRAIN_CACHE:-$HOME/.cache/life-trajectory-video/terrain}
SEED=${LTV_TERRAIN_SEED:-$HOME/Vibing/daily-test/opus5.5-video-test/lives/assets/terrain}
LAYERS=(world china east zhuge_hi hi_north hi_east hi_south hi_japan)
mkdir -p "$CACHE"
have() { [[ -f "$CACHE/$1.json" && -f "$CACHE/$1_h.bin" && -f "$CACHE/$1_tex.jpg" ]] }
for L in $LAYERS; do
  have $L && continue
  if [[ -f "$SEED/$L.json" && -f "$SEED/${L}_h.bin" && -f "$SEED/${L}_tex.jpg" ]]; then
    cp "$SEED/$L.json" "$SEED/${L}_h.bin" "$SEED/${L}_tex.jpg" "$CACHE/"; echo "seeded $L"
  fi
done
# 种子缺失的层：下载生成。参数：名称 经度0 经度1 纬度0 纬度1 缩放级 贴图宽 网格宽
gen() {
  have $1 && return
  ( cd "$PROJ" && ln -sfn "$CACHE" assets/terrain && \
    python3 tools/fetch_dem.py $1 $2 $3 $4 $5 $6 $7 && python3 tools/fetch_imagery.py $1 $6 && \
    python3 tools/make_texture.py $1 $8 --sat )
  echo "generated $1"
}
mkdir -p "$PROJ/assets"
gen world 35 178 -8 70 5 2400 600
gen china 70 138 15 55 7 6144 1536
gen east 97 124 17.5 42.5 9 6144 1536
gen zhuge_hi 102 118 26 36 10 10240 2048
gen hi_north 108 122.5 34 41.5 10 8600 1860
gen hi_east 118 123 26 34 10 3300 660
gen hi_south 105 122.5 18 26 10 11600 2300
gen hi_japan 135.5 141.5 34 38.5 10 3600 720
ln -sfn "$CACHE" "$PROJ/assets/terrain"
echo "terrain ready: $CACHE"
```

- [ ] **Step 6: 写 `scripts/new_project.sh`**

```zsh
#!/bin/zsh
# 从模板生成工作目录：复制模板 → npm install → 地形缓存 → 环境检查 → git init
# 用法：zsh new_project.sh <目标目录>
set -euo pipefail
DEST=${1:?usage: new_project.sh <dest-dir>}
SKILL=${0:A:h:h}
[[ -e "$DEST" && -n "$(ls -A "$DEST" 2>/dev/null)" ]] && { echo "目标目录非空：$DEST"; exit 1; }
mkdir -p "$DEST" && cp -R "$SKILL/template/." "$DEST/"
( cd "$DEST" && npm install --no-audit --no-fund )
zsh "$SKILL/scripts/setup_terrain.sh" "$DEST"
( cd "$DEST" && python3 tools/check_env.py ) || echo "环境未就绪：按上面的缺失项处理后再继续"
( cd "$DEST" && git init -q && git add -A && git commit -qm "chore: start from life-trajectory-video template" )
echo "项目已生成：$DEST"
```

- [ ] **Step 7: 冒烟：从模板生成一个空项目**

Run: `zsh ~/.claude/skills/life-trajectory-video/scripts/new_project.sh /private/tmp/claude-501/ltv-smoke && cd /private/tmp/claude-501/ltv-smoke && python3 -m pytest -q tests`
Expected: 输出 `seeded ...` 八行、`环境就绪`、`项目已生成`；pytest 显示 `no tests ran` 或只有不依赖人物的测试通过（`test_env`），没有失败

---

### Task 8: 编写 SKILL.md 与 references

**Files:**
- Create: `~/.claude/skills/life-trajectory-video/SKILL.md`
- Create: `references/{schema,research-brief,factcheck-brief,narration,pitfalls}.md`

内容来源（逐条取材，不凭空写）：`docs/runs/2026-10-05-three-lives.md`、`docs/runs/2026-10-06-three-more-lives.md`、`docs/runs/2026-11-02-polish.md`、`../learnings/2026-10-06-*.md`、`../learnings/2026-11-02-trail-gradient-and-replay.md`、`data/briefs/{_common,factcheck}.md`、设计文档第 2 节。

- [ ] **Step 1: SKILL.md**

必须包含以下几节，标题原样使用：
1. frontmatter：`name: life-trajectory-video`；`description` 写明触发场景（“给某位历史人物做人生轨迹/生平行迹视频”“半年一步”“3D 地形上的一生”），以及不适用的情形（主要活动在中国以外的人物、只要文字年表、只要静态地图）。
2. `## 适用范围`：仅限中国历史人物；20%/10% 阈值规则（取自设计文档）。
3. `## 开工问清单`：设计文档阶段 0 的全部问题，每题给默认值。
4. `## 流程`：阶段 0–8 的表格（做什么、通过标准、失败时怎么办），并写明每个阶段该运行的确切命令（`new_project.sh`、`pytest -k <who>`、`tools/tts.py <who>`、`tools/build_timeline.py <who>`、`music/score.py <who>`、`render.mjs <who> still ...`、`tools/render_all.sh <who>`、`tools/check_outputs.py --require`）。
5. `## 审片缺陷清单`：设计文档 2.1 节原文。
6. `## 交付物`：mp4、运行记录模板（做了什么 / 未验证 / 验收时间点）、经验笔记。
7. `## 参考文件`：每个 references 文件一行，写明什么时候读。

- [ ] **Step 2: references/schema.md**

复制 `data/SCHEMA.md` 全文（含 person.json 一节）。

- [ ] **Step 3: references/research-brief.md 与 factcheck-brief.md**

以 `data/briefs/_common.md`、`data/briefs/factcheck.md` 为底本，把人物名换成 `{人物}`、`{生卒}` 等占位符（这些占位符是给使用 skill 的模型填的模板变量，不是计划留白）。追加前两批核查教训：禁用演义说法、农历换算后跨半年、里程碑停在事件发生地（`place` 字段）、引文逐字核对并标出处、地名同地异名用 `same_as`、不得安装新包、研究代理交付前必须 `pytest -k <who>` 全过。

- [ ] **Step 4: references/narration.md**

从 `tools/build_timeline.py` 的文档字符串和 `docs/runs/2026-10-05-three-lives.md` 的 C7 条款提取：里程碑旁白、概述段、片头片尾的写法；非里程碑旁白占比 < 40%；远途里程碑边走边讲；数据、旁白、卡片三处同步。

- [ ] **Step 5: references/pitfalls.md**

每条格式为“**规则** —— 原因（出处）”，至少覆盖：年份差不等于年龄；远途判定看停留点；TTS 失败留下旧音频（按哈希核对）；zsh `$var` 不分词（用 `${=var}`）；后台任务用 run_in_background；渲染中途杀进程会留下坏 mp4；渲染提交号在开始时记录；子代理继承 cwd，要从受信任目录派发；图外判定以底图实际覆盖为准（东京落海）；DEM 单像素尖峰（去尖峰规则）；顶点色是线性空间（^2.2）；按时间截取的窗口先确认有数据；改一处事实要三处同步；测试只看数据看不到画面，必须出静帧审片。

- [ ] **Step 6: 检查文档完整性**

Run: `cd ~/.claude/skills/life-trajectory-video && for h in "## 适用范围" "## 开工问清单" "## 流程" "## 审片缺陷清单" "## 交付物" "## 参考文件"; do grep -q "$h" SKILL.md && echo "ok $h" || echo "MISSING $h"; done; ls references; grep -c "——" references/pitfalls.md`
Expected: 六行 `ok`；references 下五个文件；pitfalls 规则数 ≥ 14

---

### Task 9: 验收——用模板重建苏轼

**Files:** 新工作目录 `/private/tmp/claude-501/ltv-sushi`

- [ ] **Step 1: 生成项目并放入苏轼的输入数据**

```bash
zsh ~/.claude/skills/life-trajectory-video/scripts/new_project.sh /private/tmp/claude-501/ltv-sushi
L=/Users/louwill/Vibing/daily-test/opus5.5-video-test/lives; P=/private/tmp/claude-501/ltv-sushi
mkdir -p $P/data/sushi $P/narration/sushi $P/src/sushi
cp $L/data/sushi/{person,steps,places}.json $P/data/sushi/
cp $L/narration/sushi/{script,tts}.json $P/narration/sushi/ && cp -R $L/narration/sushi/audio $P/narration/sushi/
cp $L/music/sushi_stages.json $P/music/
```

- [ ] **Step 2: 时间轴与原项目一致**

Run: `cd /private/tmp/claude-501/ltv-sushi && python3 tools/build_timeline.py sushi && cmp src/sushi/timeline.json /Users/louwill/Vibing/daily-test/opus5.5-video-test/lives/src/sushi/timeline.json && echo SAME`
Expected: `SAME`

- [ ] **Step 3: 测试、smoke、全片渲染、成片检查**

Run: `python3 -m pytest -q tests && node tools/smoke.mjs sushi && zsh tools/render_all.sh sushi && python3 tools/check_outputs.py --require`
Expected: 测试全过；smoke `errors 0`；`苏轼_人生轨迹.mp4` 546.2 s、1920×1080、−16±1.5 LUFS

- [ ] **Step 4: 与原成片抽帧比对**

```bash
for t in 23.8 287.7 533; do
  ffmpeg -v error -y -ss $t -i 苏轼_人生轨迹.mp4 -frames:v 1 /private/tmp/claude-501/new_$t.png
  ffmpeg -v error -y -ss $t -i /Users/louwill/Vibing/daily-test/opus5.5-video-test/lives/苏轼_人生轨迹.mp4 -frames:v 1 /private/tmp/claude-501/old_$t.png
  python3 -c "from PIL import Image, ImageChops, ImageStat; d=ImageChops.difference(Image.open('/private/tmp/claude-501/new_$t.png'), Image.open('/private/tmp/claude-501/old_$t.png')); print($t, max(ImageStat.Stat(d).mean))"
done
```

Expected: 每行均值差 < 1.0（两次 x264 编码之间只有编码噪声）

- [ ] **Step 5: 删除临时项目（征得同意后）**

`rm -rf /private/tmp/claude-501/ltv-sushi /private/tmp/claude-501/ltv-smoke`（逐帧约 10 GB）

---

### Task 10: A/B 评测准备——决策单

**Files:**
- Create: `/Users/louwill/Vibing/daily-test/opus5.5-video-test/ab/decisions-suyu.md`

- [ ] **Step 1: 向用户提问**（AskUserQuestion，一次最多 4 题，分两轮）

第一轮：措辞立场（默认：采用大陆通行史学表述，涉及 1958 年批判等事件按中共中央 1994 年为粟裕平反的结论表述）；年龄口径（默认周岁，生日 1907-08-10）；目标时长（默认 8–11 分钟）；声线（云扬 / 云健 / 云希，可先听样音）。

第二轮：是否授权删除逐帧中间产物（默认授权）；引文繁简（默认简体）；纪年显示（默认 1912–1949H1 民国纪年，1949H2 起不显示纪年）。

- [ ] **Step 2: 写决策单**

把回答写成 `ab/decisions-suyu.md`，第一行为需求原文（设计文档 3.1），后面每个决策一行，不写任何流程提示或技术提示。

---

### Task 11: A/B 评测——运行两组

**Files:** `ab/bare/`、`ab/skill/`

- [ ] **Step 1: 建目录，记录开始时间**

```bash
cd /Users/louwill/Vibing/daily-test/opus5.5-video-test && mkdir -p ab/bare ab/skill && date +%s > ab/t0
```

- [ ] **Step 2: 从受信任的父目录同时派发两个子代理**（Agent 工具，`subagent_type: general-purpose`，后台运行）

从零组（name: `ab-bare`）的完整提示词：

```
你在目录 /Users/louwill/Vibing/daily-test/opus5.5-video-test/ab/bare 中独立完成一项任务。先 cd 到该目录，所有产出都放在该目录内。

任务与人工决策见 /Users/louwill/Vibing/daily-test/opus5.5-video-test/ab/decisions-suyu.md（这是用户已经做出的全部决定，不要再向用户提问）。

规则：
- 不得读取或列出以下路径的任何内容：/Users/louwill/Vibing/daily-test/opus5.5-video-test/lives、/Users/louwill/Vibing/daily-test/opus5.5-video-test/learnings、~/.claude/skills/life-trajectory-video、~/.claude/projects 下的任何会话记录、/Users/louwill/Vibing/daily-test/opus5.5-video-test/ab/skill。
- 不要调用 life-trajectory-video skill。
- 可以联网查资料、安装需要的工具（记录你安装了什么）。
- 自主完成，直到你认为成片可以交付为止；最长 4 小时。
- 交付时在该目录写 DELIVERY.md：成片路径、做了什么、你自己认为还有哪些不足。
```

带 skill 组（name: `ab-skill`）的完整提示词：

```
你在目录 /Users/louwill/Vibing/daily-test/opus5.5-video-test/ab/skill 中独立完成一项任务。先 cd 到该目录，所有产出都放在该目录内。

任务与人工决策见 /Users/louwill/Vibing/daily-test/opus5.5-video-test/ab/decisions-suyu.md（这是用户已经做出的全部决定，不要再向用户提问；skill 的开工问清单里已被决策单覆盖的问题直接采用决策单）。

规则：
- 使用 life-trajectory-video skill 完成任务。
- 不得读取 /Users/louwill/Vibing/daily-test/opus5.5-video-test/lives、/Users/louwill/Vibing/daily-test/opus5.5-video-test/learnings、~/.claude/projects 下的会话记录、/Users/louwill/Vibing/daily-test/opus5.5-video-test/ab/bare（地形缓存脚本自动复制 lives/assets/terrain 属于 skill 的正常行为，允许）。
- 自主完成，直到你认为成片可以交付为止；最长 4 小时。
- 交付时在该目录写 DELIVERY.md：成片路径、做了什么、你自己认为还有哪些不足。
```

- [ ] **Step 3: 等待两组完成通知**，记录每组的耗时、工具调用数、token（取自 Agent 结果里的统计）到 `ab/costs.md`。到 4 小时仍未完成的组，用 TaskStop 停止并记“未完成”。

- [ ] **Step 4: 越界检查**

从两个子代理的会话记录（`~/.claude/projects/-Users-louwill-Vibing-daily-test-opus5-5-video-test/` 下对应子代理的 jsonl）中搜索禁止路径：

Run: `grep -lE "opus5.5-video-test/(lives|learnings)|skills/life-trajectory-video|ab/skill" <从零组 jsonl>`
Expected: 无输出（带 skill 组只检查 `lives/` 下除 `assets/terrain` 以外的路径、`learnings`、`ab/bare`）。有命中则该组作废，按 Step 2 重跑。

---

### Task 12: A/B 评测——评审与报告

**Files:**
- Create: `ab/blind/甲/`、`ab/blind/乙/`（符号链接，映射关系写在 `ab/blind/key.txt`，不告诉评审代理）
- Create: `lives/docs/evidence/ab-suyu.md`

- [ ] **Step 1: 匿名化**

用 `python3 -c "import random;print(random.choice(['bare','skill']))"` 决定谁是“甲”，建立符号链接，把映射写进 `ab/blind/key.txt`。

- [ ] **Step 2: 史实核查**（新子代理，提示词以 `references/factcheck-brief.md` 为底本）

提示词要点：只读 `ab/blind/甲`、`ab/blind/乙`；分别找出两组的里程碑数据和旁白（结构可能不同，需要自己定位）；逐个里程碑按“正确 / 存疑 / 错误”分级，并给出来源；输出 `ab/blind/factcheck.md`，表格列为“组、里程碑、结论、依据”。

- [ ] **Step 3: 画面审片**

对两部成片分别做两件事：每 30 秒抽一帧拼板；按各自数据中的里程碑时间各抽一帧。数据格式不同时，从零组按其旁白音频的段落起点抽帧。用设计文档 2.1 的清单逐张标注缺陷，统计每组缺陷数和每类缺陷数。

- [ ] **Step 4: 写报告 `lives/docs/evidence/ab-suyu.md`**

包含：能否交付（规格检查结果）、史实（各级数量及每个里程碑的错误率）、画面（缺陷总数与分类）、成本（耗时、工具调用、token）、两组的 DELIVERY.md 摘要、局限（n=1；记忆索引无法屏蔽）、揭盲映射。最后留一节“用户主观评分”，请用户填写。

- [ ] **Step 5: 向用户汇报并请其观看两部成片打分**

---

## 自查记录

- **设计覆盖**：1 skill 结构 → Task 7、8；1.1 去人物化 → Task 1–5；1.2 环境依赖 → Task 6；1.3 地形缓存 → Task 7 Step 5；2 流程与缺陷清单 → Task 8；3 A/B → Task 10–12；4 打包验收（重建苏轼）→ Task 9。
- **超出现有高清层时自动补层**（设计 1.3）：写进 SKILL.md 阶段 1 的说明，用的是现有 `fetch_dem/fetch_imagery/make_texture` 三条命令，参数按地点范围计算（规则与 `hi_japan` 相同：z10，约 150 m/像素，贴图宽 = 经度跨度 × 111.32 × cos(中纬) ÷ 0.15）。不单独写脚本，YAGNI。
- **命名一致**：`makePerson`、`halfIdx`、`cnNum`（JS）；`people`、`load_person`、`voice_of`（Python）；全文统一。
