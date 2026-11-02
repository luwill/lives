"""把半年步 + 旁白排成全片时间轴。
用法：python3 tools/build_timeline.py <who>
输入：data/<who>/steps.json、places.json；narration/<who>/script.json、tts.json
输出：src/<who>/timeline.json

script.json 的段落类型：
  intro     片头总述（全国俯瞰）
  milestone 绑定某一步（step），在该步停留讲完
  span      覆盖一段连续的非里程碑步（from..to），这些步按旁白时长拉伸
  outro     片尾
章节卡在每个人生阶段的第一步之前自动插入。
"""
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LEAD = 0.6            # 片头黑场
TITLE = 4.5           # 片名卡
INTRO_PAD = 0.8
CHAPTER = 3.4         # 章节卡
BASE = 0.55           # 普通半年步
FAR_STEP = 0.95       # 跨越远距离的半年步
FAR_KM = 500
MS_APPROACH = 1.7     # 里程碑：推镜头、抵达
MS_LEAD = 0.5         # 抵达后到旁白开始
MS_TAIL = 1.0         # 旁白结束后到离开
MS_MIN_HOLD = 3.0
TRAVEL_MIN_PLACES = 6  # 途经点多或路程远的里程碑按“边走边讲”处理
TRAVEL_KM = 1200
TRAVEL_PLACE_SET_MIN = 8
TRAVEL_SPEED = 450    # km/s
TRAVEL_MIN, TRAVEL_MAX = 3.0, 30.0
SPAN_PAD = 0.7
OUTRO_PAD = 1.0
END_CARD = 6.0
PUNCT = '，。；：！？、'


def step_index(sid: str) -> int:
    y, h = re.match(r'^(-?\d+)H([12])$', sid).groups()
    return int(y) * 2 + int(h) - 1


def km(a: dict, b: dict) -> float:
    dx = (b['lon'] - a['lon']) * 111.32 * math.cos(math.radians((a['lat'] + b['lat']) / 2))
    dy = (b['lat'] - a['lat']) * 110.57
    return math.hypot(dx, dy)


def path_km(prev_end: str | None, places: list, P: dict) -> float:
    seq = ([prev_end] if prev_end else []) + places
    return sum(km(P[a], P[b]) for a, b in zip(seq, seq[1:]))


def split_subs(text: str, words: list, t0: float) -> list:
    """按标点切成字幕短句，用逐词时间戳对齐（同 liaoshen/tools/timeline.py）。"""
    clauses = [c for c in re.split(f'(?<=[{PUNCT}])', text) if c.strip()]
    for i in range(1, len(clauses)):
        if clauses[i].startswith('”'):
            clauses[i - 1] += '”'
            clauses[i] = clauses[i][1:]
    clauses = [c for c in clauses if c]
    marks, n = [], 0
    for w, a, b in words:
        marks.append((n, a, b))
        n += len(w)

    def time_at(ci: int, end: bool) -> float:
        best = None
        for c, a, b in marks:
            if c <= ci:
                best = (c, a, b)
        return 0.0 if best is None else (best[2] if end else best[1])

    strip = f'[{PUNCT}“”「」《》·—…（）()]'
    subs, pos, buf, bstart = [], 0, '', None
    for c in clauses:
        body = re.sub(strip, '', c)
        if bstart is None:
            bstart = pos
        buf += c
        pos += len(body)
        if len(re.sub(strip, '', buf)) >= 8 or c is clauses[-1] or buf[-1] in '。！？':
            a, b = time_at(bstart, False), time_at(max(bstart, pos - 1), True)
            subs.append([round(t0 + a, 3), round(t0 + b + 0.15, 3), buf.rstrip('，。；：、')])
            buf, bstart = '', None
    return subs


def validate(script: list, steps: list) -> None:
    ids = [s['id'] for s in steps]
    pos = {s: i for i, s in enumerate(ids)}
    ms = {s['id'] for s in steps if s.get('milestone')}
    stage_start = {i for i in range(len(steps)) if i == 0 or steps[i]['stage'] != steps[i - 1]['stage']}
    covered = set()
    for seg in script:
        k = seg['kind']
        if k == 'milestone':
            assert seg['step'] in ms, f"{seg['id']}: {seg['step']} is not a milestone"
            assert seg['step'] not in covered, f"{seg['id']}: step narrated twice"
            covered.add(seg['step'])
        elif k == 'span':
            a, b = pos[seg['from']], pos[seg['to']]
            assert a <= b, seg['id']
            for i in range(a, b + 1):
                assert ids[i] not in ms, f"{seg['id']}: span covers milestone {ids[i]}"
                assert ids[i] not in covered, f"{seg['id']}: overlaps at {ids[i]}"
                assert i == a or i not in stage_start, f"{seg['id']}: span crosses a stage boundary at {ids[i]}"
                covered.add(ids[i])
        else:
            assert k in ('intro', 'outro'), seg['id']
    missing = ms - covered
    assert not missing, f'milestones without narration: {sorted(missing)}'


def build(who: str) -> dict:
    D = json.loads((ROOT / 'data' / who / 'steps.json').read_text())
    P = json.loads((ROOT / 'data' / who / 'places.json').read_text())
    script = json.loads((ROOT / 'narration' / who / 'script.json').read_text())
    tts = json.loads((ROOT / 'narration' / who / 'tts.json').read_text())
    steps = D['steps']
    validate(script, steps)
    by_ms = {s['step']: s for s in script if s['kind'] == 'milestone'}
    span_at = {s['from']: s for s in script if s['kind'] == 'span'}
    pos = {s['id']: i for i, s in enumerate(steps)}

    narr, subs, out_steps, chapters = [], [], [], []

    def say(seg: dict, t0: float) -> float:
        info = tts[seg['id']]
        narr.append(dict(id=seg['id'], kind=seg['kind'], t0=round(t0, 3), t1=round(t0 + info['dur'], 3)))
        subs.extend(split_subs(seg['text'], info['words'], t0))
        return t0 + info['dur']

    t = LEAD
    title = dict(t0=round(t, 3), t1=round(t + TITLE, 3))
    t += TITLE
    intro = next((s for s in script if s['kind'] == 'intro'), None)
    intro_t0 = t
    if intro:
        t = say(intro, t + 0.3) + INTRO_PAD
    intro_span = dict(t0=round(intro_t0, 3), t1=round(t, 3))

    prev_end, i = None, 0
    while i < len(steps):
        st = steps[i]
        if i == 0 or st['stage'] != steps[i - 1]['stage']:
            chapters.append(dict(stage=st['stage'], t0=round(t, 3), t1=round(t + CHAPTER, 3)))
            t += CHAPTER
        if st['id'] in by_ms:
            m = st['milestone']
            seg = by_ms[st['id']]
            t0 = t
            # 远途判定看整步：途经点多或路程远的里程碑（如长征）整步边走边讲，place 只决定星标位置
            # 指定了 place 的，只有真正的长途行军（≥8 个途经点，如长征）才整步边走边讲
            if m.get('place'):
                is_travel = len(st['places']) >= TRAVEL_PLACE_SET_MIN
            else:
                is_travel = len(st['places']) >= TRAVEL_MIN_PLACES or path_km(prev_end, st['places'], P) > TRAVEL_KM
            cut = len(st['places']) if is_travel or not m.get('place') else st['places'].index(m['place']) + 1
            pre, post = st['places'][:cut], st['places'][cut:]
            km_pre = path_km(prev_end, pre, P)
            if is_travel:
                # 远途里程碑（如长征）：边走边讲，走完再定格
                move = min(TRAVEL_MAX, max(TRAVEL_MIN, tts[seg['id']]['dur'] * 0.85, km_pre / TRAVEL_SPEED))
                ms0 = t + 0.6
                end = say(seg, ms0 + 0.4)
                ms1 = max(end + MS_TAIL, t + move + MS_MIN_HOLD, ms0 + MS_MIN_HOLD)
                travel = True
            else:
                move = min(4.0, max(MS_APPROACH * 0.85, km_pre / 600))
                ms0 = t + move + 0.25
                end = say(seg, ms0 + MS_LEAD)
                ms1 = max(end + MS_TAIL, ms0 + MS_MIN_HOLD)
                travel = False
            ent = dict(id=st['id'], t0=round(t0, 3), move=round(move, 3),
                       ms=dict(t0=round(ms0, 3), t1=round(ms1, 3), travel=travel), split=cut)
            t = ms1 + 0.3
            if post:
                amove = min(6.0, max(1.2, path_km(pre[-1], post, P) / 700))
                ent['after'] = dict(t0=round(ms1 + 0.2, 3), move=round(amove, 3))
                t = ms1 + 0.2 + amove + 0.4
            ent['t1'] = round(t, 3)
            out_steps.append(ent)
            prev_end = st['places'][-1]
            i += 1
            continue
        if st['id'] in span_at:
            seg = span_at[st['id']]
            j = pos[seg['to']]
            n = j - i + 1
            dur = max(n * BASE, tts[seg['id']]['dur'] + SPAN_PAD + 0.3)
            per = dur / n
            say(seg, t + 0.3)
            for k in range(i, j + 1):
                out_steps.append(dict(id=steps[k]['id'], t0=round(t, 3), t1=round(t + per, 3), move=round(min(per * 0.8, 1.6), 3)))
                t += per
            prev_end = steps[j]['places'][-1]
            i = j + 1
            continue
        d = FAR_STEP if path_km(prev_end, st['places'], P) > FAR_KM else BASE
        out_steps.append(dict(id=st['id'], t0=round(t, 3), t1=round(t + d, 3), move=round(d * 0.8, 3)))
        t += d
        prev_end = st['places'][-1]
        i += 1

    outro = next((s for s in script if s['kind'] == 'outro'), None)
    outro_t0 = t + 0.4
    if outro:
        t = say(outro, outro_t0 + 0.4) + OUTRO_PAD
    end_card = dict(t0=round(t, 3), t1=round(t + END_CARD, 3))
    t += END_CARD
    total = round(t + 0.5, 3)

    # 配乐分段：按阶段（片头、片尾单独成段）
    bounds = [0.0] + [c['t0'] for c in chapters] + [round(outro_t0, 3), total]
    names = ['title'] + [c['stage'] for c in chapters] + ['outro']
    music = [dict(stage=n, t0=a, t1=b) for n, a, b in zip(names, bounds, bounds[1:])]
    # 字幕：后一条开始前，前一条必须结束
    for a, b2 in zip(subs, subs[1:]):
        a[1] = round(min(a[1], b2[0] - 0.02), 3)
    return dict(who=who, total=total, title=title, intro=intro_span, steps=out_steps, narr=narr, subs=subs,
                chapters=chapters, outro=dict(t0=round(outro_t0, 3), t1=end_card['t0']), end=end_card, music=music)


def main(who: str) -> None:
    tl = build(who)
    out = ROOT / 'src' / who / 'timeline.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(tl, ensure_ascii=False, indent=0))
    print(f"{who}: total {tl['total']:.1f}s ({tl['total'] / 60:.1f} min)  steps {len(tl['steps'])}  narr {len(tl['narr'])}  subs {len(tl['subs'])}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
