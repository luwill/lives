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


def test_parse_step_id_accepts_negative_years():
    got = node("""import { parseStepId, halfIdx } from './person.js';
const bad = [];
for (const s of ['x', '12H3', '-H1', '1.5H1']) { try { parseStepId(s); bad.push(s); } catch (e) {} }
console.log(JSON.stringify([parseStepId('-221H2'), parseStepId('744H1'), halfIdx('-221H2'), bad]));""")
    assert got == [[-221, 2], [744, 1], -221 * 2 + 1, []]


def test_step_index_matches_half_idx_for_negative_years():
    import sys
    sys.path.insert(0, str(ROOT / 'tools'))
    import build_timeline as BT
    from person import half_idx
    for sid in ('-221H1', '-221H2', '-1H2', '1H1', '744H2'):
        assert BT.step_index(sid) == half_idx(sid)
    assert BT.step_index('-221H1') < BT.step_index('-221H2') < BT.step_index('-220H1')


def test_trail_floor_dims_old_trail_in_close_ups():
    """近景（zoom=0）旧轨迹压到 0.08，全景（zoom=1）回到 0.3；随镜头拉远单调增加，越界时截断。"""
    v = node("""import { trailFloor } from './journey.js';
console.log(JSON.stringify([-1, 0, 0.5, 1, 2].map(trailFloor)));""")
    assert v[0] == v[1] == 0.08 and abs(v[3] - 0.3) < 1e-9 and v[4] == v[3]
    assert v[1] < v[2] < v[3]


def test_journey_flags_steps_that_go_off_map():
    """到过图外地点（如莫斯科）的半年步要被标记，镜头据此拉远；图内步不标记。"""
    flags = node("""import { buildJourney } from './journey.js';
const places = { nj: { lon: 118.8, lat: 32.1 }, msk: { lon: 37.6, lat: 55.8 } };
const steps = [{ places: ['nj'] }, { places: ['nj', 'msk'] }, { places: ['msk', 'nj'] }, { places: ['nj'] }];
const tl = steps.map((_, i) => ({ t0: i * 2, move: 1 }));
console.log(JSON.stringify(buildJourney(steps, tl, places).offSteps));""")
    assert flags == [False, True, True, False]


def test_trail_tau_shorter_in_close_ups():
    """旧轨迹按半年步衰减：近景 3 步、全景 12 步，单调增加并截断。"""
    v = node("""import { trailTau } from './journey.js';
console.log(JSON.stringify([-1, 0, 0.5, 1, 3].map(trailTau)));""")
    assert v[0] == v[1] == 3 and v[3] == v[4] == 12 and v[1] < v[2] < v[3]
