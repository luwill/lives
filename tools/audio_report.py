"""配乐分段客观指标：每个阶段的响度、频谱质心、起音密度，以及阶段边界处的交叉淡化检查。
用法：python3 tools/audio_report.py <who> [wav]  （默认 out/<who>/music.wav）→ 打印表格并输出 out/<who>/spectrogram.png
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def load(p: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(p)) as w:
        sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
        x = np.frombuffer(w.readframes(n), '<i2').astype(np.float32).reshape(-1, ch).mean(1) / 32768
    return x, sr


def metrics(x: np.ndarray, sr: int) -> dict:
    rms = float(np.sqrt(np.mean(x ** 2)) + 1e-12)
    hop = 1024
    frames = np.lib.stride_tricks.sliding_window_view(x, 2048)[::hop] * np.hanning(2048)
    mag = np.abs(np.fft.rfft(frames, axis=1))
    freqs = np.fft.rfftfreq(2048, 1 / sr)
    centroid = float(np.sum(mag * freqs, 1).mean() / (mag.sum(1).mean() + 1e-9))
    flux = np.maximum(0, np.diff(mag, axis=0)).sum(1)
    thr = flux.mean() + 1.5 * flux.std()
    onsets = int(np.sum((flux[1:-1] > thr) & (flux[1:-1] >= flux[:-2]) & (flux[1:-1] >= flux[2:])))
    return dict(dbfs=round(20 * np.log10(rms), 1), centroid_hz=round(centroid), onsets_per_s=round(onsets / (len(x) / sr), 2))


def spectrogram(x: np.ndarray, sr: int, out: Path, marks: list[float]) -> None:
    hop = max(512, len(x) // 1800)
    frames = np.lib.stride_tricks.sliding_window_view(x, 2048)[::hop] * np.hanning(2048)
    mag = 20 * np.log10(np.abs(np.fft.rfft(frames, axis=1))[:, :400] + 1e-6)
    img = np.clip((mag - mag.max() + 80) / 80, 0, 1).T[::-1]
    im = (np.stack([img ** 0.7, img ** 1.4, img ** 2.5], -1) * 255).astype(np.uint8)
    for t in marks:
        c = int(t * sr / hop)
        if 0 <= c < im.shape[1]:
            im[:, c] = (255, 255, 255)
    Image.fromarray(im).resize((1800, 400)).save(out)


def main(who: str, wav: str | None) -> None:
    tl = json.loads((ROOT / 'src' / who / 'timeline.json').read_text())
    cfg = json.loads((ROOT / 'music' / f'{who}_stages.json').read_text())
    x, sr = load(Path(wav) if wav else ROOT / 'out' / who / 'music.wav')
    print(f"{'stage':<10}{'mood':<14}{'t0':>8}{'t1':>8}{'dBFS':>8}{'centroid':>10}{'onsets/s':>10}")
    for seg in tl['music']:
        a, b = int(seg['t0'] * sr), int(seg['t1'] * sr)
        m = metrics(x[a:b], sr)
        print(f"{seg['stage']:<10}{cfg[seg['stage']]['mood']:<14}{seg['t0']:>8.1f}{seg['t1']:>8.1f}{m['dbfs']:>8}{m['centroid_hz']:>10}{m['onsets_per_s']:>10}")
    # 边界交叉淡化：边界前后 0.5 s 内不应出现静音（< -50 dBFS）
    gaps = []
    for seg in tl['music'][1:]:
        a = int((seg['t0'] - 0.5) * sr)
        w = x[a:a + sr]
        if 20 * np.log10(np.sqrt(np.mean(w ** 2)) + 1e-12) < -50:
            gaps.append(seg['t0'])
    print('silent boundaries:', gaps or 'none')
    print('peak', round(float(np.abs(x).max()), 3), 'nan', bool(np.isnan(x).any()))
    spectrogram(x, sr, ROOT / 'out' / who / 'spectrogram.png', [s['t0'] for s in tl['music']])


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None)
