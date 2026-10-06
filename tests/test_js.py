"""浏览器端纯函数（年龄、纪年、行程里程）的检查：用 node 直接导入 src/*.js。"""
import json
import math
import subprocess

from conftest import ROOT, load


def node(code: str):
    out = subprocess.run(['node', '--input-type=module', '-e', code], cwd=ROOT / 'src', capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def ages(who: str) -> dict:
    ids = [s['id'] for s in load(who, 'steps.json')['steps']]
    return node(f"""import {{ PEOPLE }} from './people.js';
const p = PEOPLE['{who}'], out = {{}};
for (const id of {json.dumps(ids)}) {{ const [, y, h] = id.match(/^(\\d+)H(\\d)$/); out[id] = [p.age(+y, +h), p.era(+y, +h)]; }}
out.birth = p.birth || null;
console.log(JSON.stringify(out));""")


def test_ages_never_negative(who):
    for sid, (age, _) in [(k, v) for k, v in ages(who).items() if k != 'birth']:
        n = int(''.join(c for c in age if c.isdigit()))
        assert n >= 0 and '-' not in age, (sid, age)


def test_age_and_era_anchors():
    m, z, s = ages('mao'), ages('zhuge'), ages('sushi')
    assert m['1893H2'][0] == '0 岁' and m['1966H2'][0] == '72 岁' and m['1976H2'][0] == '82 岁'
    assert z['181H1'][0] == '虚岁 1' and z['234H2'][0] == '虚岁 54' and '章武元年' in z['221H1'][1]
    assert s['birth'] == {'era': '北宋 · 景祐三年', 'age': '虚岁 1'} and s['1101H2'][0] == '虚岁 66'


def test_mao_km_counts_real_moscow_distance():
    """图外代理点不能让里程少算：行程总里程与按真实坐标的折线距离一致（±2%）。"""
    km = node("""import { buildJourney } from './journey.js';
import fs from 'node:fs';
const d = JSON.parse(fs.readFileSync('../data/mao/steps.json')), p = JSON.parse(fs.readFileSync('../data/mao/places.json'));
const tl = JSON.parse(fs.readFileSync('mao/timeline.json'));
console.log(JSON.stringify(buildJourney(d.steps, tl.steps, p).totalKm));""")
    P = load('mao', 'places.json')
    seq = []
    for st in load('mao', 'steps.json')['steps']:
        seq += [k for k in st['places'] if not seq or k != seq[-1]]
    f = lambda a, b: math.hypot((b['lon'] - a['lon']) * 111.32 * math.cos(math.radians((a['lat'] + b['lat']) / 2)), (b['lat'] - a['lat']) * 110.57)
    true = sum(f(P[a], P[b]) for a, b in zip(seq, seq[1:]))
    assert abs(km - true) / true < 0.02, (km, true)


def test_offmap_proxy_points_toward_moscow():
    """莫斯科、列宁格勒的代理点要落在地图西北边缘，并朝真实方向（防止落在内蒙古、轨迹掉头）。"""
    pts = node("""import { proxyOf } from './journey.js';
console.log(JSON.stringify([proxyOf({lon: 37.62, lat: 55.75}), proxyOf({lon: 30.32, lat: 59.94})]));""")
    for lon, lat in pts:
        assert lon <= 80 and 44 <= lat <= 52, (lon, lat)


def test_age_and_era_anchors_second_batch():
    """第二批：李白（虚岁 701 起、天宝三载起称“载”）、朱元璋（虚岁、龙凤/洪武）、蒋介石（周岁、1949H2 起不用民国纪年）。"""
    l, z, j = ages('libai'), ages('zhuyz'), ages('jiang')
    assert l['701H1'][0] == '虚岁 1' and l['762H2'][0] == '虚岁 62'
    assert l['743H1'][1].endswith('天宝二年') and l['744H1'][1].endswith('天宝三载') and l['758H1'][1].endswith('乾元元年')
    assert z['1328H2'] == ['虚岁 1', '元 · 天历元年'] and z['1398H1'][0] == '虚岁 71'
    assert z['1355H1'][1].startswith('龙凤元年') and z['1368H1'][1] == '明 · 洪武元年'
    assert j['1887H2'][0] == '0 岁' and j['1975H1'][0] == '87 岁'
    assert j['1949H1'][1] == '民国三十八年' and all(v[1] == '' for k, v in j.items() if k != 'birth' and k >= '1949H2')


def test_offmap_proxy_points_east_and_west():
    """东京代理点在地图东缘、开罗在西缘（防止轨迹掉头或落在内陆）。"""
    tokyo, cairo = node("""import { proxyOf } from './journey.js';
console.log(JSON.stringify([proxyOf({lon: 139.69, lat: 35.69}), proxyOf({lon: 31.24, lat: 30.04})]));""")
    assert tokyo[0] >= 130 and 33 <= tokyo[1] <= 40, tokyo
    assert cairo[0] <= 80 and 30 <= cairo[1] <= 40, cairo


def test_era_edges_second_batch():
    """纪年分支的边界：龙凤元年起点、至德/乾元换称、蒋介石清末与民国元年。"""
    l, z, j = ages('libai'), ages('zhuyz'), ages('jiang')
    assert z['1354H2'][1] == '元 · 至正十四年' and z['1367H2'][1].startswith('吴元年')
    assert l['757H2'][1].endswith('至德二载') and l['758H2'][1].endswith('乾元元年') and l['705H1'][1].startswith('唐')
    assert j['1908H2'][1] == '清 · 光绪三十四年' and j['1909H1'][1] == '清 · 宣统元年' and j['1912H1'][1] == '民国元年'
