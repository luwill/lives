"""生成 data/zhuge/steps.json 与 places.json（诸葛亮 181H1—234H2 半年行踪）。
用法：python3 data/_build/build_zhuge.py
史料原文缓存在 data/_build/cache/zhuge/（维基文库 action=raw），地点坐标见 zhuge_places.py。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zhuge_places import PLACES  # noqa: E402
from zhuge_steps import CONTESTED, STAGES, STEPS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data' / 'zhuge'
WS = 'https://zh.wikisource.org/wiki/'
MAX_EVENT = 60

META = {
    'person': '诸葛亮',
    'birth': '181',
    'birth_note': '汉灵帝光和四年生，月份不详。由本传"其年八月，亮疾病，卒于军，时年五十四"（建兴十二年，234）逆推；按任务约定从 181H1 起。',
    'death': '234',
    'death_note': '蜀汉建兴十二年（魏青龙二年）八月卒于五丈原军中，日不详；农历八月约当公历 9—10 月，归入 234H2。',
    'calendar_note': ('H1=公历 1—6 月、H2=7—12 月（儒略历）。史料多只记农历季节或月份：'
                      '按"农历 1—6 月→H1、7—12 月→H2"近似；只记"春/夏"者归 H1，"秋/冬"者归 H2；'
                      '只记年份、无月份者按上下文推断并在 note 中说明。'),
    'sources': [
        {'id': 'S1', 'title': '陈寿《三国志·蜀书·诸葛亮传》及裴松之注', 'url': WS + '三國志/卷35', 'kind': 'primary'},
        {'id': 'S2', 'title': '陈寿《三国志·蜀书·先主传》及裴注', 'url': WS + '三國志/卷32', 'kind': 'primary'},
        {'id': 'S3', 'title': '陈寿《三国志·蜀书·后主传》', 'url': WS + '三國志/卷33', 'kind': 'primary'},
        {'id': 'S4', 'title': '陈寿《三国志·蜀书·马良传（附马谡）》及裴注引《襄阳记》', 'url': WS + '三國志/卷39',
         'kind': 'primary'},
        {'id': 'S5', 'title': '司马光《资治通鉴》卷六十至七十二', 'url': WS + '資治通鑑', 'kind': 'primary'},
        {'id': 'S6', 'title': '常璩《华阳国志·南中志》', 'url': WS + '華陽國志/卷四', 'kind': 'primary'},
        {'id': 'S7', 'title': '常璩《华阳国志·刘先主志》', 'url': WS + '華陽國志/卷六', 'kind': 'primary'},
        {'id': 'S8', 'title': '裴注引习凿齿《汉晋春秋》（东晋）', 'url': WS + '三國志/卷35', 'kind': 'secondary'},
        {'id': 'S9', 'title': '裴注引习凿齿《襄阳记》（东晋；见诸葛亮传、庞统传卷37、马谡传卷39 注）', 'url': WS + '三國志/卷35', 'kind': 'secondary'},
        {'id': 'S10', 'title': '裴注引鱼豢《魏略》（曹魏）', 'url': WS + '三國志/卷35', 'kind': 'secondary'},
        {'id': 'S11', 'title': '裴注引袁晔《献帝春秋》（东吴）', 'url': WS + '三國志/卷35', 'kind': 'secondary'},
        {'id': 'S12', 'title': '裴注引《零陵先贤传》', 'url': WS + '三國志/卷35', 'kind': 'secondary'},
        {'id': 'S13', 'title': 'OpenStreetMap Nominatim 今地名坐标（见 places.json 各条 source）',
         'url': 'https://nominatim.openstreetmap.org/', 'kind': 'secondary'},
    ],
}


def validate(steps: list[dict]) -> None:
    src = {s['id'] for s in META['sources']}
    for s in steps:
        if len(s['event']) > MAX_EVENT:
            raise ValueError(f"{s['id']} event too long ({len(s['event'])}): {s['event']}")
        missing = [p for p in s['places'] if p not in PLACES]
        if missing:
            raise ValueError(f"{s['id']} unknown places {missing}")
        if not set(s['sources']) <= src:
            raise ValueError(f"{s['id']} unknown sources {s['sources']}")


def main() -> None:
    validate(STEPS)
    used = {p for s in STEPS for p in s['places']}
    places = {k: v for k, v in PLACES.items() if k in used}
    stage_ids = {s['stage'] for s in STEPS}
    stages = [st for st in STAGES if st['id'] in stage_ids]
    OUT.mkdir(parents=True, exist_ok=True)
    data = {'meta': META, 'stages': stages, 'steps': STEPS, 'contested': CONTESTED}
    (OUT / 'steps.json').write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    (OUT / 'places.json').write_text(json.dumps(places, ensure_ascii=False, indent=1) + '\n')
    print(f'steps={len(STEPS)} {STEPS[0]["id"]}..{STEPS[-1]["id"]} places={len(places)} stages={len(stages)}')


if __name__ == '__main__':
    main()
