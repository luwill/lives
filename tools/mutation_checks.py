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
    p = r / 'src/people.js'
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
    ('C8', '片尾里程按图外代理点累计', m_proxy_km, 'test_js.py'),
]


def run(mutate) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        r = Path(tmp)
        for d in ('data', 'src', 'tests', 'tools', 'narration', 'music'):
            shutil.copytree(ROOT / d, r / d, ignore=shutil.ignore_patterns('audio', '_build', '*.mp3', '__pycache__'))
        mutate(r)
        out = subprocess.run([sys.executable, '-m', 'pytest', '-q', 'tests', '-p', 'no:cacheprovider'], cwd=r, capture_output=True, text=True)
        failed = [ln for ln in out.stdout.splitlines() if ln.startswith('FAILED')]
        return out.returncode, '; '.join(f.split(' - ')[0].replace('FAILED ', '') for f in failed[:3])


def main() -> None:
    rows, ok = [], True
    base, _ = run(lambda r: None)
    rows.append(f'| — | 未注入缺陷（对照） | {"green" if base == 0 else "RED"} | — |')
    ok &= base == 0
    for crit, desc, fn, _ in MUTANTS:
        code, failed = run(fn)
        rows.append(f'| {crit} | {desc} | {"red ✔" if code else "GREEN ✘"} | {failed} |')
        ok &= code != 0
    table = '| 准则 | 注入的缺陷 | pytest 结果 | 变红的测试 |\n|---|---|---|---|\n' + '\n'.join(rows)
    print(table)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text('# 反向验证（变异测试）\n\n每行在仓库数据副本上注入一个缺陷，期望测试变红。命令：`python3 tools/mutation_checks.py`\n\n' + table + '\n')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
