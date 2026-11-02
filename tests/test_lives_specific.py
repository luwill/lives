"""只属于 lives/ 六人的锚点测试（不进 skill 模板）：具体年龄、纪年、图外代理点、引文简体。"""
import json
import math

from conftest import ROOT, ages, load, node

# 用户要求诸葛亮卡片引文全部用简体；这些是原引文里出现过的繁体字
TRAD = set('諸陽於亂聞誠則業漢興請將無輔闕節繼瀘駑鈍姦還舊孫勝遺墳塚斂須')


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


def test_japan_on_map_and_cairo_at_west_edge():
    """日本在底图范围内（世界层铺到 178°E）：东京、高田按真实坐标标注，不能被投到日本海上；开罗仍投到西缘。"""
    tokyo, takada, cairo, off = node("""import { proxyOf, isOffMap } from './journey.js';
const t = {lon: 139.69, lat: 35.69}, k = {lon: 138.242, lat: 37.1152};
console.log(JSON.stringify([proxyOf(t), proxyOf(k), proxyOf({lon: 31.24, lat: 30.04}), [isOffMap(t), isOffMap(k)]]));""")
    assert tokyo == [139.69, 35.69] and takada == [138.242, 37.1152]
    assert off == [False, False]
    assert cairo[0] <= 80 and 30 <= cairo[1] <= 40, cairo


def test_era_edges_second_batch():
    """纪年分支的边界：龙凤元年起点、至德/乾元换称、蒋介石清末与民国元年。"""
    l, z, j = ages('libai'), ages('zhuyz'), ages('jiang')
    assert z['1354H2'][1] == '元 · 至正十四年' and z['1367H2'][1].startswith('吴元年')
    assert l['757H2'][1].endswith('至德二载') and l['758H2'][1].endswith('乾元元年') and l['705H1'][1].startswith('唐')
    assert l['701H1'][1] == '武周 · 大足元年' and l['761H2'][1] == '唐 · 上元二年' and l['762H1'][1] == '唐 · 宝应元年'
    assert j['1908H2'][1] == '清 · 光绪三十四年' and j['1909H1'][1] == '清 · 宣统元年' and j['1912H1'][1] == '民国元年'


def test_zhuge_quotes_simplified():
    for s in load('zhuge', 'steps.json')['steps']:
        q = (s.get('milestone') or {}).get('quote')
        if q:
            assert not set(q['text']) & TRAD, (s['id'], set(q['text']) & TRAD)
