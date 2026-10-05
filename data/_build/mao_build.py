"""把 mao_steps.py 中的数据组装为 data/mao/steps.json（可在中途按阶段落盘）。
用法：python3 data/_build/mao_build.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mao_steps as D  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data' / 'mao' / 'steps.json'


def to_step(row: tuple, stage: str) -> dict:
    sid, places, event, conf, srcs, *rest = row
    extra = rest[0] if rest else {}
    step = {'id': sid, 'places': list(places), 'event': event, 'confidence': conf,
            'sources': list(srcs), 'stage': stage}
    if 'ms' in extra:
        step['milestone'] = extra['ms']
    if 'note' in extra:
        step['note'] = extra['note']
    if len(event) > 60:
        print(f'  ! {sid} event 超过 60 字（{len(event)}）', file=sys.stderr)
    return step


def main() -> None:
    steps = []
    for st in D.STAGES:
        rows = D.STEPS.get(st['id'], [])
        steps.extend(to_step(r, st['id']) for r in rows)
    stages = [s for s in D.STAGES if D.STEPS.get(s['id'])]
    doc = {'meta': D.META, 'stages': stages, 'steps': steps, 'contested': D.CONTESTED}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    ms = [s for s in steps if 'milestone' in s]
    print(f'wrote {OUT}: {len(steps)} steps, {len(stages)} stages, {len(ms)} milestones')


if __name__ == '__main__':
    main()
