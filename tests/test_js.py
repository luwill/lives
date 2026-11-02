"""浏览器端纯函数（年龄、轨迹、回放）的通用检查：用 node 直接导入 src/*.js。"""
import json
import math

from conftest import ROOT, ages, node


def test_ages_never_negative(who):
    for sid, (age, _) in [(k, v) for k, v in ages(who).items() if k != 'birth']:
        n = int(''.join(c for c in age if c.isdigit()))
        assert n >= 0 and '-' not in age, (sid, age)


def test_trail_fade_monotonic_and_floored():
    v = node("""import { trailFade } from './journey.js';
console.log(JSON.stringify([0, 10, 90, 600, 1e5, -5].map(a => trailFade(a))));""")
    assert v[0] == 1 and v[5] == 1
    assert v[0] > v[1] > v[2] > v[3] > v[4] >= 0.3 - 1e-9 and v[4] < 0.31


def test_replay_time_covers_life_in_order(who):
    """片尾回放：f 从 0 到 1 时，时间轴时刻单调不减，起于第一步、止于最后一步的行程终点。"""
    tl = json.loads((ROOT / 'src' / who / 'timeline.json').read_text())
    ts = node(f"""import {{ replayTime }} from './journey.js';
import fs from 'node:fs';
const s = JSON.parse(fs.readFileSync('{who}/timeline.json')).steps;
console.log(JSON.stringify(Array.from({{ length: 2001 }}, (_, k) => replayTime(s, k / 2000))));""")
    assert all(b >= a - 1e-9 for a, b in zip(ts, ts[1:]))
    first, last = tl['steps'][0], tl['steps'][-1]
    assert ts[0] == first['t0']
    end = last['after']['t0'] + last['after']['move'] if 'after' in last else last['t0'] + last['move']
    assert math.isclose(ts[-1], end, abs_tol=1e-6)
