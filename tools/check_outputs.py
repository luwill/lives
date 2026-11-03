"""C8 成片检查：分辨率/帧率/编码、时长与时间轴一致、响度、抽样帧非黑。
用法：python3 tools/check_outputs.py [--require]   （--require：成片缺失视为失败；默认缺失时跳过）
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from person import load_person, people

ROOT = Path(__file__).resolve().parent.parent


def probe(p: Path) -> dict:
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,color_range,color_space:format=duration',
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
    person = load_person(who)
    p = ROOT / f'{person["name"]}_人生轨迹.mp4'
    if not p.exists():
        return [f'{p.name} missing'] if require else []
    errs = []
    info = probe(p)
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    a = [s for s in info['streams'] if s['codec_type'] == 'audio']
    if (v['codec_name'], v['width'], v['height'], v['r_frame_rate']) != ('h264', 1920, 1080, '30/1'):
        errs.append(f"video stream {v}")
    # 标准范围 BT.709：全范围（pc/yuvj420p）在部分播放器和平台上会偏色
    if (v.get('pix_fmt'), v.get('color_range'), v.get('color_space')) != ('yuv420p', 'tv', 'bt709'):
        errs.append(f"color {v.get('pix_fmt')}/{v.get('color_range')}/{v.get('color_space')} (want yuv420p/tv/bt709; re-run tools/assemble.sh)")
    if not a or a[0]['codec_name'] != 'aac':
        errs.append(f'audio stream {a}')
    dur = float(info['format']['duration'])
    total = json.loads((ROOT / 'src' / who / 'timeline.json').read_text())['total']
    if abs(dur - total) > 0.6:
        errs.append(f'duration {dur:.2f} != timeline {total:.2f}')
    lo, hi = person['targets']['duration_min']
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
    if require and not people():
        sys.exit('no people found (data/*/person.json)')
    for who in people():
        try:
            errs = check(who, require)
            rendered = (ROOT / f'{load_person(who)["name"]}_人生轨迹.mp4').exists()
        except (ValueError, FileNotFoundError) as e:
            print(f'{who}: FAIL {e}')
            failed = True
            continue
        if not errs and not rendered:
            print(f'{who}: skipped (not rendered yet)')
        for e in errs:
            print(f'  {who}: FAIL {e}')
            failed = True
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
