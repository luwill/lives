"""反向验证：在仓库副本里逐个注入缺陷，确认对应测试会变红（检查本身能失败）。
用法：python3 tools/mutation_checks.py [out.md]   → 打印结果表，可写入 markdown
不改动工作区：每个变异在临时目录里的一份数据副本上进行。
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def jload(p: Path):
    return json.loads(p.read_text())


def jsave(p: Path, d) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False))


def m_delete_step(r: Path) -> None:          # C1：删掉一个半年步
    p = r / 'data/mao/steps.json'; d = jload(p)
    d['steps'] = [s for s in d['steps'] if s['id'] != '1935H1']
    jsave(p, d)


def m_bad_coord(r: Path) -> None:            # C1：坐标越界
    p = r / 'data/sushi/places.json'; d = jload(p)
    d['huangzhou']['lon'] = 10.0
    jsave(p, d)


def m_single_source(r: Path) -> None:        # C2：里程碑只剩一个来源
    p = r / 'data/zhuge/steps.json'; d = jload(p)
    next(s for s in d['steps'] if s['id'] == '234H2')['sources'] = ['S1']
    jsave(p, d)


def m_short_step(r: Path) -> None:           # C3：某个半年步几乎不出现
    p = r / 'src/sushi/timeline.json'; d = jload(p)
    s = d['steps'][40]; s['t1'] = s['t0'] + 0.1
    jsave(p, d)


def m_short_hold(r: Path) -> None:           # C5：里程碑停留不足 3 秒
    p = r / 'src/zhuge/timeline.json'; d = jload(p)
    s = next(s for s in d['steps'] if 'ms' in s); s['ms']['t1'] = s['ms']['t0'] + 1.0
    jsave(p, d)


def m_overlap(r: Path) -> None:              # C7：两段旁白重叠
    p = r / 'src/mao/timeline.json'; d = jload(p)
    d['narr'][5]['t0'] = d['narr'][4]['t1'] - 2.0
    jsave(p, d)


def m_music_gap(r: Path) -> None:            # C6：配乐分段出现空档
    p = r / 'src/sushi/timeline.json'; d = jload(p)
    d['music'][3]['t0'] += 5.0
    jsave(p, d)


def m_wrong_stop(r: Path) -> None:           # C5：里程碑停在半年终点而非事件地（庐山会议→杭州）
    p = r / 'src/mao/timeline.json'; d = jload(p)
    s = next(s for s in d['steps'] if s['id'] == '1959H2'); s['split'] = 3
    jsave(p, d)


def m_negative_age(r: Path) -> None:        # 年龄口径：去掉周岁下限
    p = r / 'src/person.js'
    p.write_text(p.read_text().replace('Math.max(0, y - by', '(y - by'))


def m_proxy_km(r: Path) -> None:            # C8 片尾里程：按代理点而非真实坐标累计
    p = r / 'src/journey.js'
    p.write_text(p.read_text().replace('kmTrue.push(lens[j] / n * scale[j]);', 'kmTrue.push(lens[j] / n);'))


def m_ratio(r: Path) -> None:               # C7：非里程碑旁白占比超标
    p = r / 'src/sushi/timeline.json'; d = jload(p)
    ms = [s for s in d['narr'] if s['kind'] == 'milestone']
    for s in ms[:6]:
        s['kind'] = 'span'
    jsave(p, d)


def m_sub_overlap(r: Path) -> None:         # C7：字幕重叠
    p = r / 'src/zhuge/timeline.json'; d = jload(p)
    d['subs'][10][1] = d['subs'][11][0] + 0.5
    jsave(p, d)


def m_jiang_minguo(r: Path) -> None:      # D1：蒋介石 1949H2 以后仍显示民国纪年
    p = r / 'data/jiang/person.json'; d = jload(p)
    d['era_overrides'] = []
    jsave(p, d)


def m_libai_zai(r: Path) -> None:          # C3：天宝三载起不改称“载”
    p = r / 'data/libai/person.json'; d = jload(p)
    d['era_overrides'] = [o for o in d['era_overrides'] if '天宝' not in o['template']]
    jsave(p, d)


def m_zhuyz_longfeng(r: Path) -> None:     # C3：龙凤纪年晚一年开始
    p = r / 'data/zhuyz/person.json'; d = jload(p)
    d['era_overrides'][0]['from'] = '1356H1'
    jsave(p, d)


def m_delete_step_libai(r: Path) -> None:   # C1：第二批也逐步覆盖（删李白 750H1）
    p = r / 'data/libai/steps.json'; d = jload(p)
    d['steps'] = [s for s in d['steps'] if s['id'] != '750H1']
    jsave(p, d)


def m_bad_coord_jiang(r: Path) -> None:     # C1：第二批坐标越界（溪口经度改为 10°）
    p = r / 'data/jiang/places.json'; d = jload(p)
    d['xikou']['lon'] = 10.0
    jsave(p, d)


def m_stale_tts(r: Path) -> None:           # C7：改了旁白却没重新配音
    p = r / 'narration/zhuyz/script.json'; d = jload(p)
    d[3]['text'] += '据《明史》。'
    jsave(p, d)


MUTANTS = [
    ('C1', '删除毛泽东 1935H1 一步', m_delete_step, 'test_data.py'),
    ('C1', '黄州经度改为 10°', m_bad_coord, 'test_data.py'),
    ('C2', '五丈原星落只留一个来源', m_single_source, 'test_data.py'),
    ('C3', '苏轼第 41 步只显示 0.1 s', m_short_step, 'test_timeline.py'),
    ('C5', '诸葛亮首个里程碑只停 1 s', m_short_hold, 'test_timeline.py'),
    ('C5', '庐山会议停留点改到杭州', m_wrong_stop, 'test_timeline.py'),
    ('C6', '苏轼第 4 段配乐前移出 5 s 空档', m_music_gap, 'test_timeline.py'),
    ('C7', '毛泽东第 5、6 段旁白重叠 2 s', m_overlap, 'test_timeline.py'),
    ('C7', '苏轼 6 段里程碑旁白改记为概述', m_ratio, 'test_timeline.py'),
    ('C7', '诸葛亮第 11、12 条字幕重叠', m_sub_overlap, 'test_timeline.py'),
    ('C3', '去掉周岁下限（出生时 −1 岁）', m_negative_age, 'test_js.py'),
    ('C8', '片尾里程按图外代理点累计', m_proxy_km, 'test_lives_specific.py'),
    ('C3', '蒋介石 1949H2 后仍用民国纪年', m_jiang_minguo, 'test_lives_specific.py'),
    ('C3', '李白天宝三载不改称“载”', m_libai_zai, 'test_lives_specific.py'),
    ('C3', '朱元璋龙凤纪年晚一年', m_zhuyz_longfeng, 'test_lives_specific.py'),
    ('C1', '删除李白 750H1 一步', m_delete_step_libai, 'test_data.py'),
    ('C1', '溪口经度改为 10°', m_bad_coord_jiang, 'test_data.py'),
    ('C7', '朱元璋旁白改了文本未重新配音', m_stale_tts, 'test_timeline.py'),
]


def run(mutate) -> tuple[int, str]:
    """在临时副本上注入缺陷后跑 pytest（不含 env 标记的测试）；返回 (退出码, 失败的测试 id 列表)。"""
    with tempfile.TemporaryDirectory() as tmp:
        r = Path(tmp)
        for d in ('data', 'src', 'tests', 'tools', 'narration', 'music'):
            shutil.copytree(ROOT / d, r / d, ignore=shutil.ignore_patterns('audio', '_build', '*.mp3', '__pycache__'))
        for f in ('pytest.ini', 'render.mjs'):
            shutil.copy2(ROOT / f, r / f)
        mutate(r)
        out = subprocess.run([sys.executable, '-m', 'pytest', '-q', 'tests', '-m', 'not env', '-p', 'no:cacheprovider'], cwd=r, capture_output=True, text=True)
        failed = [ln.split(' - ')[0].replace('FAILED ', '') for ln in out.stdout.splitlines() if ln.startswith('FAILED')]
        return out.returncode, '; '.join(failed)


def is_red_for(code: int, failed: str, expected: str) -> bool:
    """变异被捕获 = pytest 失败，且失败项包含预期的测试文件（防止因无关原因变红）。"""
    return code != 0 and any(f.split('::')[0].endswith(expected) for f in failed.split('; ') if f)


def main() -> None:
    rows, ok = [], True
    base, failed = run(lambda r: None)
    if base != 0:
        sys.exit(f'对照组（未注入缺陷）不是绿色，无法做变异检查，失败项：{failed or "（pytest 非零退出，无 FAILED 行）"}')
    rows.append('| — | 未注入缺陷（对照） | green | — |')
    for crit, desc, fn, expected in MUTANTS:
        code, failed = run(fn)
        red = is_red_for(code, failed, expected)
        short = '; '.join(failed.split('; ')[:3])
        rows.append(f'| {crit} | {desc} | {"red ✔" if red else "GREEN/未命中 ✘"} | {short} |')
        ok &= red
    table = '| 准则 | 注入的缺陷 | pytest 结果 | 变红的测试 |\n|---|---|---|---|\n' + '\n'.join(rows)
    print(table)
    print(f'\n{sum(r.count("red ✔") for r in rows)}/{len(MUTANTS)} 个变异被预期的测试捕获')
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text('# 反向验证（变异测试）\n\n每行在仓库数据副本上注入一个缺陷，期望预期的测试文件变红。命令：`python3 tools/mutation_checks.py`\n\n' + table + '\n')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
