"""person.json 校验，以及迁移前后年龄/纪年逐字一致（tests/fixtures/era_baseline.json）。"""
import json
import re

import pytest

from conftest import ROOT, ages, load
from person import load_person

HALF = re.compile(r'^-?\d+H[12]$')
BASELINE = ROOT / 'tests' / 'fixtures' / 'era_baseline.json'


def test_person_config_valid(who):
    cfg = load_person(who)
    assert cfg['age']['kind'] in ('xusui', 'zhousui')
    keys = [r[3] for r in cfg['eras']]
    assert all(HALF.match(k) for k in keys)
    idx = [int(k[:-2]) * 2 + int(k[-1]) - 1 for k in keys]
    assert idx == sorted(idx), 'eras 必须按生效半年升序'
    for o in cfg.get('era_overrides', []):
        assert all(v is None or HALF.match(v) for v in (o['from'], o['to']))
    for r in cfg.get('regions', []):
        assert all(v is None or HALF.match(v) for v in (r['from'], r['to']))
    steps = load(who, 'steps.json')['steps']
    assert [steps[0]['id'], steps[-1]['id']] == cfg['span']


def test_ages_and_eras_match_baseline(who):
    if not BASELINE.exists():
        pytest.skip('no baseline in this project')
    base = json.loads(BASELINE.read_text()).get(who)
    if base is None:
        pytest.skip(f'{who} not in baseline')
    got = ages(who)
    assert got.pop('birth') == base['birth']
    diff = {k: (got.get(k), v) for k, v in base['rows'].items() if got.get(k) != v}
    assert not diff, dict(list(diff.items())[:5])
