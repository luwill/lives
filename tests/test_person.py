"""person.json 校验，以及迁移前后年龄/纪年逐字一致（tests/fixtures/era_baseline.json）。"""
import copy
import json
import re

import pytest

from conftest import ROOT, ages, load, node
from person import half_idx, load_person, validate

HALF = re.compile(r'^-?\d+H[12]$')
BASELINE = ROOT / 'tests' / 'fixtures' / 'era_baseline.json'

BASE = {
    'name': '测试', 'life': '181–234', 'tagline': '合成数据', 'color': '#aabbcc', 'glow': '#112233',
    'age': {'kind': 'xusui', 'lunar_birth_year': 181},
    'eras': [['东汉 · ', '光和', 178, '181H1'], ['东汉 · ', '建安', 196, '196H1'], ['蜀汉 · ', '章武', 221, '221H1']],
    'regions': [{'name': '某地', 'lon': 110.0, 'lat': 30.0, 'from': '200H1', 'to': '230H2'}],
    'voice': {'name': 'zh-CN-YunjianNeural', 'rate': '+0%', 'pitch': '+0Hz'},
    'span': ['181H1', '234H2'],
    'targets': {'duration_min': [3, 5], 'min_milestones': 1},
}


def test_person_config_valid(who):
    cfg = load_person(who)
    assert cfg['age']['kind'] in ('xusui', 'zhousui')
    keys = [r[3] for r in cfg['eras']]
    assert all(HALF.match(k) for k in keys)
    idx = [half_idx(k) for k in keys]
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


def test_base_config_is_valid():
    validate(copy.deepcopy(BASE), 'fake/person.json')


def _bad(mutate, match):
    cfg = copy.deepcopy(BASE)
    mutate(cfg)
    with pytest.raises(ValueError, match=match):
        validate(cfg, 'fake/person.json')


def test_validate_rejects_unknown_key():
    _bad(lambda c: c.update(colour='x'), 'unknown fields')


def test_validate_rejects_bad_birth_format():
    def m(c):
        c['age'] = {'kind': 'zhousui', 'birth': '1893/12/26'}
    _bad(m, 'age.birth')


def test_validate_rejects_to_before_from():
    _bad(lambda c: c['regions'][0].update({'from': '230H1', 'to': '225H1'}), 'regions.0.*after')


def test_validate_rejects_overlapping_overrides():
    def m(c):
        c['era_overrides'] = [{'from': '200H1', 'to': '210H2', 'template': 'a'}, {'from': '210H2', 'to': None, 'template': 'b'}]
    _bad(m, 'overlaps')


def test_validate_rejects_first_era_after_span_start():
    _bad(lambda c: c['eras'][0].__setitem__(3, '182H1'), 'after span start')


def test_validate_rejects_nonpositive_template_year():
    _bad(lambda c: c.update(era_overrides=[{'from': '200H1', 'to': None, 'template': 'x{n:300}'}]), 'non-positive')


def test_half_idx_rejects_bad_key():
    with pytest.raises(ValueError):
        half_idx('744H3')


def test_cn_num_range_and_hundreds():
    got = node("""import { cnNum } from './person.js';
const out = {};
for (const n of [0, 100, 101, 110, 115, 120, 199, 200, 1.5]) { try { out[n] = cnNum(n); } catch (e) { out[n] = 'ERR'; } }
console.log(JSON.stringify(out));""")
    assert got == {'0': 'ERR', '100': '一百', '101': '一百〇一', '110': '一百一十', '115': '一百一十五',
                   '120': '一百二十', '199': '一百九十九', '200': 'ERR', '1.5': 'ERR'}


def _msg(mutate) -> str:
    cfg = copy.deepcopy(BASE)
    mutate(cfg)
    with pytest.raises(ValueError) as e:
        validate(cfg, 'fake/person.json')
    return str(e.value)


def test_error_message_has_field_prefix_once():
    msg = _msg(lambda c: c['regions'][0].update({'from': 'oops'}))
    assert msg.count('regions[0]') == 1, msg
    msg = _msg(lambda c: c['regions'][0].update({'from': '230H1', 'to': '225H1'}))
    assert msg.count('regions[0]') == 1, msg
    msg = _msg(lambda c: c.update(era_overrides=[{'from': 'oops', 'to': None, 'template': 'a'}]))
    assert msg.count('era_overrides[0]') == 1, msg


def test_validate_rejects_nonpositive_template_year_when_from_is_null():
    # from=null 时最早显示的是 span 起点（181 年）：{n:300} 会得到负年
    _bad(lambda c: c.update(era_overrides=[{'from': None, 'to': '200H1', 'template': 'x{n:300}'}]), 'non-positive')


def test_validate_rejects_xusui_birth_after_span_start():
    def m(c):
        c['age'] = {'kind': 'xusui', 'lunar_birth_year': 182}
    _bad(m, 'age.lunar_birth_year')


def test_validate_rejects_zhousui_birth_after_span_start():
    def m(c):
        c['age'] = {'kind': 'zhousui', 'birth': '0182-01-01'}
    _bad(m, 'age.birth')


def test_validate_rejects_era_ordinal_over_199():
    _bad(lambda c: c['eras'][0].__setitem__(2, -100), r'eras\[0\].*199')


def test_validate_rejects_slash_in_name():
    _bad(lambda c: c.update(name='a/b'), 'name')
    _bad(lambda c: c.update(name='a\\b'), 'name')


@pytest.mark.parametrize('mutate', [
    lambda c: c.update(extra_levels=[['Bad-Layer', 1.0]]),
    lambda c: c['voice'].update(rate='fast'),
    lambda c: c['voice'].update(rate='6%'),
    lambda c: c['voice'].update(pitch='+0'),
    lambda c: c['voice'].update(pitch='+3hz'),
    lambda c: c['age'].update(birht='x'),
    lambda c: c['regions'][0].update(lon=190.0),
    lambda c: c['regions'][0].update(lat=-91),
], ids=['layer-name', 'rate-word', 'rate-nosign', 'pitch-nounit', 'pitch-case', 'age-unknown-key', 'lon-range', 'lat-range'])
def test_validate_rejects_bad_values(mutate):
    cfg = copy.deepcopy(BASE)
    mutate(cfg)
    with pytest.raises(ValueError):
        validate(cfg, 'x.json')


def test_cli_unknown_field_is_clean_error(who):
    """对项目里实际存在的人物检查（模板项目里不一定有某个固定人物）。"""
    import subprocess
    import sys
    r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'person.py'), 'nope', who], capture_output=True, text=True)
    assert r.returncode != 0 and 'Traceback' not in r.stderr and 'unknown field' in r.stderr
