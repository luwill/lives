"""人物配置读取与校验：data/<who>/person.json（测试、TTS、总装、成片检查共用）。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ('name', 'life', 'tagline', 'color', 'glow', 'age', 'eras', 'voice', 'span', 'targets')
OPTIONAL = ('era_overrides', 'regions', 'extra_levels', 'birth_override', '_note')
HALF = re.compile(r'^(-?\d+)H([12])$')
COLOR = re.compile(r'^#[0-9a-fA-F]{6}$')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
N_REF = re.compile(r'\{n:(-?\d+)\}')


def half_idx(key) -> int:
    """'744H1' → 744*2+0；非法键抛 ValueError。"""
    m = HALF.match(key) if isinstance(key, str) else None
    if not m:
        raise ValueError(f'bad half-year key: {key!r}')
    return int(m[1]) * 2 + int(m[2]) - 1


def people() -> list[str]:
    """data/ 下所有带 person.json 的人物键，按字母排序。"""
    return sorted(p.parent.name for p in (ROOT / 'data').glob('*/person.json'))


def _is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _half_or_none(v):
    if v is None:
        return None
    try:
        return half_idx(v)
    except ValueError:
        raise ValueError(f'bad half-year key {v!r}') from None


def _check_range(a, b):
    if a is not None and b is not None and a > b:
        raise ValueError('from is after to')


def validate(cfg: dict, path) -> dict:
    """纯函数：校验配置，非法时抛 ValueError（含文件路径与出错字段）。"""
    def bad(field, msg):
        raise ValueError(f'{path}: {field}: {msg}')

    if not isinstance(cfg, dict):
        bad('<root>', 'must be an object')
    missing = [k for k in REQUIRED if k not in cfg]
    if missing:
        bad('<root>', f'missing fields {missing}')
    unknown = [k for k in cfg if k not in REQUIRED + OPTIONAL]
    if unknown:
        bad('<root>', f'unknown fields {unknown}')
    for k in ('name', 'life', 'tagline'):
        if not isinstance(cfg[k], str) or not cfg[k]:
            bad(k, 'must be a non-empty string')
    for k in ('color', 'glow'):
        if not isinstance(cfg[k], str) or not COLOR.match(cfg[k]):
            bad(k, f'must match #RRGGBB, got {cfg[k]!r}')

    span = cfg['span']
    if not (isinstance(span, list) and len(span) == 2):
        bad('span', 'must be [first, last]')
    try:
        s0, s1 = half_idx(span[0]), half_idx(span[1])
    except ValueError as e:
        bad('span', str(e))
    if s0 > s1:
        bad('span', 'first is after last')

    age = cfg['age']
    kind = age.get('kind') if isinstance(age, dict) else None
    if kind == 'xusui':
        if not _is_int(age.get('lunar_birth_year')):
            bad('age.lunar_birth_year', 'must be an int')
        if age['lunar_birth_year'] > s0 // 2:
            bad('age.lunar_birth_year', 'is after the first year of span')
    elif kind == 'zhousui':
        if not (isinstance(age.get('birth'), str) and DATE.match(age['birth'])):
            bad('age.birth', 'must match YYYY-MM-DD')
        if int(age['birth'][:4]) > s0 // 2:
            bad('age.birth', 'is after the first year of span')
    else:
        bad('age.kind', f'must be xusui or zhousui, got {kind!r}')

    _check_eras(cfg['eras'], s0, bad)
    _check_overrides(cfg.get('era_overrides', []), s0, bad)
    _check_regions(cfg.get('regions', []), bad)

    for i, lv in enumerate(cfg.get('extra_levels', [])):
        if not (isinstance(lv, list) and len(lv) == 2 and isinstance(lv[0], str) and _is_num(lv[1])):
            bad(f'extra_levels[{i}]', 'must be [str, number]')
    if 'birth_override' in cfg:
        b = cfg['birth_override']
        if not (isinstance(b, dict) and set(b) == {'era', 'age'} and all(isinstance(v, str) for v in b.values())):
            bad('birth_override', 'must be {era: str, age: str}')
    v = cfg['voice']
    if not (isinstance(v, dict) and all(isinstance(v.get(k), str) for k in ('name', 'rate', 'pitch'))):
        bad('voice', 'needs string name/rate/pitch')
    t = cfg['targets']
    d = t.get('duration_min') if isinstance(t, dict) else None
    if not (isinstance(d, list) and len(d) == 2 and all(_is_num(x) for x in d) and d[0] < d[1]):
        bad('targets.duration_min', 'must be [lo, hi] numbers with lo < hi')
    if not (_is_int(t.get('min_milestones')) and t['min_milestones'] >= 1):
        bad('targets.min_milestones', 'must be an int >= 1')
    return cfg


def _check_eras(eras, span_start, bad):
    if not (isinstance(eras, list) and eras):
        bad('eras', 'must be a non-empty list')
    prev = None
    for i, r in enumerate(eras):
        w = f'eras[{i}]'
        if not (isinstance(r, list) and len(r) == 4 and isinstance(r[0], str) and isinstance(r[1], str) and _is_int(r[2])):
            bad(w, 'must be [prefix:str, name:str, firstYear:int, effectiveHalf]')
        try:
            k = half_idx(r[3])
        except ValueError as e:
            bad(w, str(e))
        if r[2] > k // 2:
            bad(w, 'firstYear is after the effective half')
        if prev is not None and k < prev:
            bad(w, 'rows must ascend by effective half')
        prev = k
    if half_idx(eras[0][3]) > span_start:
        bad('eras[0]', 'first era takes effect after span start')


def _check_overrides(ovs, span_start, bad):
    if not isinstance(ovs, list):
        bad('era_overrides', 'must be a list')
    spans = []
    for i, o in enumerate(ovs):
        w = f'era_overrides[{i}]'
        if not (isinstance(o, dict) and set(o) == {'from', 'to', 'template'} and isinstance(o['template'], str)):
            bad(w, 'must be {from, to, template:str}')
        try:
            a, b = _half_or_none(o['from']), _half_or_none(o['to'])
            _check_range(a, b)
        except ValueError as e:
            bad(w, str(e))
        lo = span_start if a is None else a   # from=null：最早显示的是 span 起点
        for m in N_REF.finditer(o['template']):
            if lo // 2 - int(m[1]) + 1 < 1:
                bad(w, f'{m[0]} gives a non-positive year at its start')
        spans.append((float('-inf') if a is None else a, float('inf') if b is None else b, i))
    spans.sort()
    for (a1, b1, i1), (a2, b2, i2) in zip(spans, spans[1:]):
        if a2 <= b1:
            bad(f'era_overrides[{i2}]', f'overlaps era_overrides[{i1}]')


def _check_regions(regions, bad):
    if not isinstance(regions, list):
        bad('regions', 'must be a list')
    for i, r in enumerate(regions):
        w = f'regions[{i}]'
        if not (isinstance(r, dict) and set(r) == {'name', 'lon', 'lat', 'from', 'to'}
                and isinstance(r['name'], str) and _is_num(r['lon']) and _is_num(r['lat'])):
            bad(w, 'must be {name:str, lon, lat, from, to}')
        try:
            _check_range(_half_or_none(r['from']), _half_or_none(r['to']))
        except ValueError as e:
            bad(w, str(e))


def load_person(who: str) -> dict:
    p = ROOT / 'data' / who / 'person.json'
    if not p.exists():
        raise FileNotFoundError(f'{p} missing')
    return validate(json.loads(p.read_text()), p)


def voice_of(who: str) -> tuple[str, str, str]:
    v = load_person(who)['voice']
    return v['name'], v['rate'], v['pitch']


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3 or not re.fullmatch(r'[a-z0-9_]+', sys.argv[2]):
        sys.exit('usage: python3 tools/person.py <field> <who>   (who: [a-z0-9_]+)')
    print(load_person(sys.argv[2])[sys.argv[1]])
