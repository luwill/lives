"""C8 成片检查：分辨率/帧率/编码、时长与时间轴一致、响度、抽样帧非黑。
用法：python3 tools/check_outputs.py [--require]   （--require：成片缺失视为失败；默认缺失时跳过）
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAMES = {'mao': '毛泽东', 'zhuge': '诸葛亮', 'sushi': '苏轼', 'libai': '李白', 'zhuyz': '朱元璋', 'jiang': '蒋介石'}
TARGET_MIN = {'mao': (9, 13), 'zhuge': (13, 17), 'sushi': (7, 10), 'libai': (7, 10), 'zhuyz': (8, 11), 'jiang': (9, 13)}


def probe(p: Path) -> dict:
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate:format=duration',
                          '-of', 'json', str(p)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudness(p: Path) -> float:
    err = subprocess.run(['ffmpeg', '-nostats', '-i', str(p), '-vn', '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', err)[-1])


def frame_means(p: Path, total: float, n: int = 16) -> list[float]:
    means = []
    for k in range(n):
        t = total * (k + 0.5) / n
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', str(p), '-frames:v', '1', '-vf', 'scale=64:36,format=gray',
                              '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
        means.append(sum(raw) / max(1, len(raw)))
    return means


def check(who: str, require: bool) -> list[str]:
    p = ROOT / f'{NAMES[who]}_人生轨迹.mp4'
    if not p.exists():
        return [f'{p.name} missing'] if require else []
    errs = []
    info = probe(p)
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    a = [s for s in info['streams'] if s['codec_type'] == 'audio']
    if (v['codec_name'], v['width'], v['height'], v['r_frame_rate']) != ('h264', 1920, 1080, '30/1'):
        errs.append(f"video stream {v}")
    if not a or a[0]['codec_name'] != 'aac':
        errs.append(f'audio stream {a}')
    dur = float(info['format']['duration'])
    total = json.loads((ROOT / 'src' / who / 'timeline.json').read_text())['total']
    if abs(dur - total) > 0.6:
        errs.append(f'duration {dur:.2f} != timeline {total:.2f}')
    lo, hi = TARGET_MIN[who]
    if not lo * 60 <= dur <= hi * 60:
        errs.append(f'duration {dur / 60:.1f} min outside {lo}-{hi}')
    lufs = loudness(p)
    if abs(lufs + 16) > 1.5:
        errs.append(f'loudness {lufs} LUFS')
    means = frame_means(p, dur)
    dark = [round(m, 1) for m in means if m < 12]
    if dark:
        errs.append(f'black frames sampled: {dark}')
    print(f"{who}: {dur:.1f}s ({dur / 60:.1f} min) {v['width']}x{v['height']}@{v['r_frame_rate']} {v['codec_name']}+{a[0]['codec_name'] if a else '-'} "
          f"{lufs} LUFS, frame means {min(means):.0f}-{max(means):.0f}")
    return errs


def main() -> None:
    require = '--require' in sys.argv
    failed = False
    for who in NAMES:
        errs = check(who, require)
        if not errs and not (ROOT / f'{NAMES[who]}_人生轨迹.mp4').exists():
            print(f'{who}: skipped (not rendered yet)')
        for e in errs:
            print(f'  {who}: FAIL {e}')
            failed = True
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
