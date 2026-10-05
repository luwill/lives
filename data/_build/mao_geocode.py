"""用 Nominatim 核验 mao_places_spec.P 中的地点坐标，写出 data/mao/places.json。

- curl 子进程请求（避免 urllib 证书问题），带 User-Agent，请求间隔 ≥1.1 秒；
- 响应缓存在 data/_build/cache/mao/nominatim/；
- 以 '!' 开头的查询是县城级兜底：先查兜底作参照，精确查询结果离参照 >100 km 视为误匹配丢弃；
- 次选查询命中或命中同名车站/景区时 confidence=medium；
- 结果中 class=place 的节点优先于行政边界质心（质心可能偏离城区数十公里）；
- 只写出 steps.json 中实际引用到的地点（steps.json 不存在时写出全部）。
用法：python3 data/_build/mao_geocode.py
"""
import hashlib
import json
import math
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mao_places_spec import P  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / 'data' / '_build' / 'cache' / 'mao' / 'nominatim'
OUT = ROOT / 'data' / 'mao' / 'places.json'
STEPS = ROOT / 'data' / 'mao' / 'steps.json'
UA = 'lives-documentary-data/0.1 (research; contact via project maintainer)'
MAX_DIST_KM = 100
SETTLEMENT_KINDS = {'city', 'town', 'village'}
_last_call = [0.0]


def nominatim(q: str, foreign: bool, settlement: bool = True) -> list[dict]:
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (hashlib.md5(f'{q}|{foreign}|5'.encode()).hexdigest() + '.json')
    if f.exists():
        data = json.loads(f.read_text())
        return prefer_place(data) if settlement else data
    params = {'format': 'json', 'q': q, 'limit': 5, 'accept-language': 'zh'}
    if not foreign:
        params['countrycodes'] = 'cn'
    # 不论是否命中缓存，都把 place 节点（城镇点位）排在行政区划边界质心之前
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(params)
    wait = 1.1 - (time.time() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    r = subprocess.run(['curl', '-s', '--max-time', '30', '-A', UA, url], capture_output=True, text=True)
    _last_call[0] = time.time()
    if r.returncode != 0:
        print(f'  ! curl 失败 {q}: rc={r.returncode}', file=sys.stderr)
        return []
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f'  ! 非 JSON 响应 {q}: {r.stdout[:120]}', file=sys.stderr)
        return []
    f.write_text(json.dumps(data, ensure_ascii=False))
    return prefer_place(data) if settlement else data


def prefer_place(hits: list[dict]) -> list[dict]:
    """行政区 relation 的坐标是边界质心，常偏离城区；同名 place 节点（城市/县城/镇）优先。"""
    return sorted(hits, key=lambda h: 0 if h.get('class') == 'place' else 1)


def km(a: dict, b: dict) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (float(a['lat']), float(a['lon']), float(b['lat']), float(b['lon'])))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def resolve(key: str) -> dict:
    name, modern, kind, queries, note = P[key]
    foreign = kind == 'foreign'
    precise = [q for q in queries if not q.startswith('!')]
    fallback = next((q[1:] for q in queries if q.startswith('!')), None)
    ref = None
    if fallback:
        hits = nominatim(fallback, foreign)
        ref = hits[0] if hits else None
    hit, used, conf = None, None, 'high'
    settle = kind in SETTLEMENT_KINDS or foreign
    for qi, q in enumerate(precise):
        for h in nominatim(q, foreign, settle):
            if ref is None or km(h, ref) <= MAX_DIST_KM:
                hit, used = h, q
                break
        if hit:
            # 退而用次选查询（如乡镇代替村）或命中的是同名车站/景区，精度降为 medium
            if qi > 0 or h.get('class') in ('railway', 'leisure'):
                conf = 'medium'
            break
    notes = [note] if note else []
    if hit is None and ref is not None:
        hit, used, conf = ref, fallback, 'low'
        notes.append(f'未查到场所级坐标，取所属县/市（{fallback}）')
    if hit is None:
        raise SystemExit(f'无法定位 {key} {queries}')
    if key == 'caodi':
        conf = 'medium' if conf == 'high' else conf
    rec = {
        'name': name, 'modern': modern,
        'lat': round(float(hit['lat']), 4), 'lon': round(float(hit['lon']), 4),
        'kind': kind, 'confidence': conf,
        'source': f"OSM Nominatim {hit.get('osm_type', '?')} {hit.get('osm_id', '?')}（查询：{used}）",
    }
    if notes:
        rec['note'] = '；'.join(notes)
    return rec


def used_keys() -> list[str]:
    if not STEPS.exists():
        return list(P)
    steps = json.loads(STEPS.read_text())['steps']
    seen: list[str] = []
    for s in steps:
        for k in s['places']:
            if k not in seen:
                seen.append(k)
    missing = [k for k in seen if k not in P]
    if missing:
        raise SystemExit(f'places spec 缺少：{missing}')
    return seen


def main() -> None:
    keys = used_keys()
    out = {}
    for k in keys:
        out[k] = resolve(k)
        r = out[k]
        print(f"{k:16s} {r['lat']:8.4f} {r['lon']:9.4f} {r['confidence']:6s} {r['source']}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f'wrote {OUT} ({len(out)} places)')


if __name__ == '__main__':
    main()
