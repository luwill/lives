"""C1 数据完整性：半年步覆盖生卒区间、字段齐全、地点可解析。"""

from conftest import load
from person import HALF, half_idx, load_person

CONF = {'documented', 'inferred', 'traditional'}


def test_steps_cover_life_without_gaps(who):
    steps = load(who, 'steps.json')['steps']
    ids = [s['id'] for s in steps]
    assert all(HALF.match(i) for i in ids), [i for i in ids if not HALF.match(i)]
    a, b = load_person(who)['span']
    assert ids[0] == a and ids[-1] == b, (ids[0], ids[-1])
    want = list(range(half_idx(a), half_idx(b) + 1))
    got = [half_idx(i) for i in ids]
    missing = sorted(set(want) - set(got))
    assert got == want, f'gaps/dupes/disorder; missing={missing[:10]}'


def test_step_fields(who):
    d = load(who, 'steps.json')
    src_ids = {s['id'] for s in d['meta']['sources']}
    stage_ids = {s['id'] for s in d['stages']}
    for s in d['steps']:
        assert s['places'], s['id']
        assert s['event'].strip(), s['id']
        assert s['confidence'] in CONF, s['id']
        assert s['sources'] and set(s['sources']) <= src_ids, (s['id'], s['sources'])
        assert s['stage'] in stage_ids, s['id']


def test_places_resolve_with_coords(who):
    steps = load(who, 'steps.json')['steps']
    places = load(who, 'places.json')
    for s in steps:
        for k in s['places']:
            assert k in places, (s['id'], k)
    for k, p in places.items():
        assert p['name'] and p['modern'], k
        assert isinstance(p['lat'], (int, float)) and isinstance(p['lon'], (int, float)), k
        if p.get('kind') != 'foreign':
            assert 15 <= p['lat'] <= 54 and 73 <= p['lon'] <= 135, (k, p['lat'], p['lon'])


def test_stages_contiguous(who):
    d = load(who, 'steps.json')
    stages = d['stages']
    assert 4 <= len(stages) <= 8
    order = [s['stage'] for s in d['steps']]
    # 阶段按时间顺序连续出现，每个阶段至少一次
    seen = []
    for st in order:
        if not seen or seen[-1] != st:
            seen.append(st)
    assert seen == [s['id'] for s in stages], seen


def test_milestones(who):
    steps = load(who, 'steps.json')['steps']
    ms = [s for s in steps if s.get('milestone')]
    assert len(ms) >= load_person(who)['targets']['min_milestones'], len(ms)
    for s in ms:
        m = s['milestone']
        assert m['title'] and m['importance'] in (1, 2), s['id']
        assert m.get('place', s['places'][-1]) in s['places'], s['id']
        assert s['confidence'] != 'traditional' or s.get('note'), s['id']
        assert len(set(s['sources'])) >= 2, f"{s['id']}: milestone needs ≥2 sources, has {s['sources']}"
