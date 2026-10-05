"""总混音：旁白 + 电影原声 + 配乐（旁白/电影出现时自动压低配乐）。
用法：python3 tools/mix.py → out/mix.wav
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.ndimage import maximum_filter1d, uniform_filter1d

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
NARR_GAIN = 1.0
MUSIC_BED = 0.62          # 无旁白时配乐电平
DUCK_NARR = 0.36          # 旁白时配乐相对电平
DUCK_FILM = {'film_main': 0.0, 'film_tashan': 0.35}   # 其余电影段默认 0.2


def load(path: Path) -> np.ndarray:
    """任意音频 → 2×N float（ffmpeg 解码）。"""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 's16le', '-ac', '2', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, '<i2').reshape(-1, 2).T.astype(np.float32) / 32768


def place(dst: np.ndarray, src: np.ndarray, t: float, gain: float = 1.0) -> None:
    i = int(round(t * SR))
    n = min(src.shape[1], dst.shape[1] - i)
    if n > 0:
        dst[:, i:i + n] += src[:, :n] * gain


def smooth_env(mask: np.ndarray, attack: float, release: float) -> np.ndarray:
    """0/1 掩码 → 平滑包络（先扩张 release，再均值平滑 attack）。"""
    grown = maximum_filter1d(mask, int(release * SR))
    return uniform_filter1d(grown.astype(np.float32), int(attack * SR))


def main() -> None:
    tl = json.loads((ROOT / 'src' / 'timeline.json').read_text())
    N = int(tl['total'] * SR)
    narr, film = np.zeros((2, N), np.float32), np.zeros((2, N), np.float32)
    narr_mask, film_gain = np.zeros(N, np.float32), np.ones(N, np.float32)
    for s in tl['segs']:
        a, b = int(s['t0'] * SR), int(s['t1'] * SR)
        if s['type'] == 'narr':
            x = load(ROOT / 'narration' / 'audio' / f"{s['id']}.mp3")
            place(narr, x, s['t0'], NARR_GAIN)
            narr_mask[a:a + x.shape[1]] = 1
        elif s['type'] == 'film':
            x = load(ROOT / 'assets' / 'film' / 'clips' / f"{s['id']}.wav")
            n = x.shape[1]
            fade = np.ones(n, np.float32)
            k = int(0.35 * SR)
            fade[:k] = np.linspace(0, 1, k)
            fade[-k:] = np.linspace(1, 0, k)
            place(film, x * fade, s['t0'], s.get('vol', 1.0))
            film_gain[a:b] = np.minimum(film_gain[a:b], DUCK_FILM.get(s['id'], 0.2))
    music = load(ROOT / 'out' / 'music.wav')[:, :N]
    music = np.pad(music, ((0, 0), (0, N - music.shape[1])))
    duck = 1 - (1 - DUCK_NARR) * smooth_env(narr_mask, 0.25, 0.5)
    fg = uniform_filter1d(film_gain, int(0.4 * SR))
    mix = narr + film + music * MUSIC_BED * duck * fg
    # 母带：峰值归一 + 软限幅
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 1.25
    mix = np.tanh(mix) / np.tanh(1.25) * 0.92
    out = ROOT / 'out' / 'mix.wav'
    with wave.open(str(out), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix.T * 32767).astype('<i2').tobytes())
    print('mix', out, round(N / SR, 1), 's')


if __name__ == '__main__':
    main()
