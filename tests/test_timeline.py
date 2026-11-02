"""C3/C5/C6/C7：时间轴约束（半年步逐步可见、里程碑停留、旁白不重叠且详略得当、配乐分段覆盖全片）。"""
import json
import sys

import pytest

from conftest import ROOT, load

sys.path.insert(0, str(ROOT / 'tools'))
import build_timeline as BT  # noqa: E402
from person import load_person, voice_of  # noqa: E402

MIN_STEP = 0.4
MIN_HOLD = 3.0


def timeline(who: str) -> dict:
    p = ROOT / 'src' / who / 'timeline.json'
    if not p.exists():
        pytest.fail(f'{p} missing; run tools/build_timeline.py {who}')
    return json.loads(p.read_text())


def test_timeline_is_fresh(who):
    """提交的 timeline.json 必须与当前数据、旁白一致（防止改了数据忘了重排）。"""
    assert BT.build(who) == timeline(who)


def test_every_half_year_step_is_shown(who):
    tl, steps = timeline(who), load(who, 'steps.json')['steps']
    assert [s['id'] for s in tl['steps']] == [s['id'] for s in steps]
    prev = 0.0
    for s in tl['steps']:
        assert s['t1'] - s['t0'] >= MIN_STEP - 1e-6, s
        assert s['t0'] >= prev - 1e-6, s
        prev = s['t1']


def test_milestones_hold(who):
    tl, steps = timeline(who), load(who, 'steps.json')['steps']
    ms_ids = {s['id'] for s in steps if s.get('milestone')}
    held = {s['id']: s['ms'] for s in tl['steps'] if 'ms' in s}
    assert set(held) == ms_ids
    for sid, m in held.items():
        assert m['t1'] - m['t0'] >= MIN_HOLD, sid
    # 远途里程碑：抵达终点后也要停够
    for s in tl['steps']:
        if 'ms' in s and s['ms']['travel']:
            assert s['ms']['t1'] - (s['t0'] + s['move']) >= MIN_HOLD - 1e-6, s['id']


def test_narration_no_overlap_and_inside(who):
    tl = timeline(who)
    segs = sorted(tl['narr'], key=lambda s: s['t0'])
    for a, b in zip(segs, segs[1:]):
        assert a['t1'] <= b['t0'] + 1e-6, (a['id'], b['id'])
    assert segs[0]['t0'] >= 0 and segs[-1]['t1'] <= tl['total']
    subs = tl['subs']
    for a, b in zip(subs, subs[1:]):
        assert a[0] <= b[0] and a[1] <= b[0] + 1e-6, (a, b)


def test_narration_balance(who):
    """C7 原文：非里程碑旁白（概述 + 片头 + 片尾）总时长占比 < 40%。"""
    tl = timeline(who)
    dur = lambda k: sum(s['t1'] - s['t0'] for s in tl['narr'] if s['kind'] == k)
    total = sum(s['t1'] - s['t0'] for s in tl['narr'])
    non_ms = dur('span') + dur('intro') + dur('outro')
    assert non_ms / total < 0.40, non_ms / total
    # 一级里程碑平均旁白比二级长
    steps = {s['id']: s for s in load(who, 'steps.json')['steps']}
    script = json.loads((ROOT / 'narration' / who / 'script.json').read_text())
    nd = {s['id']: s['t1'] - s['t0'] for s in tl['narr']}
    lv = {1: [], 2: []}
    for seg in script:
        if seg['kind'] == 'milestone':
            lv[steps[seg['step']]['milestone']['importance']].append(nd[seg['id']])
    assert lv[1] and lv[2]
    assert sum(lv[1]) / len(lv[1]) > sum(lv[2]) / len(lv[2])


def test_duration_in_target(who):
    lo, hi = load_person(who)['targets']['duration_min']
    assert lo * 60 <= timeline(who)['total'] <= hi * 60, timeline(who)['total'] / 60


def test_music_covers_film_by_stage(who):
    tl = timeline(who)
    m = tl['music']
    assert m[0]['t0'] == 0 and abs(m[-1]['t1'] - tl['total']) < 1e-6
    for a, b in zip(m, m[1:]):
        assert abs(a['t1'] - b['t0']) < 1e-6
    cfg = json.loads((ROOT / 'music' / f'{who}_stages.json').read_text())
    stages = [s['id'] for s in load(who, 'steps.json')['stages']]
    assert set(stages) | {'title', 'outro'} <= set(cfg), set(stages) - set(cfg)
    moods = {cfg[s]['mood'] for s in stages}
    assert len(moods) >= 4, moods


# ---------- 排程逻辑的单元测试（合成数据，不依赖真实素材） ----------
STEPS = [{'id': f'100{i // 2}H{i % 2 + 1}', 'places': ['a'], 'stage': 's1' if i < 4 else 's2',
          **({'milestone': {'importance': 1}} if i == 2 else {})} for i in range(6)]


def test_validate_rejects_span_over_milestone():
    script = [{'id': 'p', 'kind': 'span', 'from': '1000H1', 'to': '1001H1'}, {'id': 'm', 'kind': 'milestone', 'step': '1001H1'}]
    with pytest.raises(AssertionError, match='milestone'):
        BT.validate(script, STEPS)


def test_validate_rejects_missing_milestone_narration():
    with pytest.raises(AssertionError, match='without narration'):
        BT.validate([], STEPS)


def test_validate_rejects_span_across_stage():
    script = [{'id': 'm', 'kind': 'milestone', 'step': '1001H1'}, {'id': 'p', 'kind': 'span', 'from': '1001H2', 'to': '1002H1'}]
    with pytest.raises(AssertionError, match='stage boundary'):
        BT.validate(script, STEPS)


def test_milestone_stays_at_its_place(who):
    """指定了 place 的里程碑：只有 ≥8 个途经点才按远途处理；其余必须停在 place（防止庐山会议停到杭州）。"""
    tl, steps = timeline(who), load(who, 'steps.json')['steps']
    by = {s['id']: s for s in tl['steps']}
    for s in steps:
        m = s.get('milestone')
        if not m or not m.get('place'):
            continue
        ent = by[s['id']]
        assert ent['ms']['travel'] == (len(s['places']) >= 8), (s['id'], ent['ms']['travel'])
        if not ent['ms']['travel']:
            assert s['places'][ent['split'] - 1] == m['place'], (s['id'], s['places'][ent['split'] - 1], m['place'])


def test_narration_audio_matches_script(who):
    """每段旁白的配音都由当前文本和声线合成（TTS 失败时会留下旧音频，时间轴就会按旧时长排）。"""
    import hashlib
    voice, rate, pitch = voice_of(who)
    cache = json.loads((ROOT / 'narration' / who / 'tts.json').read_text())
    for seg in json.loads((ROOT / 'narration' / who / 'script.json').read_text()):
        h = hashlib.md5(f"{voice}{rate}{pitch}{seg['text']}".encode()).hexdigest()[:10]
        assert cache.get(seg['id'], {}).get('hash') == h, f"{who}/{seg['id']}: stale or missing TTS"
