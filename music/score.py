"""按人生阶段生成配乐（全部原创合成，无采样、无版权素材）。
用法：python3 music/score.py <who>   → out/<who>/music.wav
阶段 → 情绪映射见 music/<who>_stages.json：{stage: {mood, root, mode, why}}。
每段情绪在自身节拍网格上生成，阶段之间交叉淡化；章节卡配锣与编钟，里程碑配钟声。
"""
import json
import zlib
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import orch as O  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SR = O.SR

# 五声调式（相对主音的半音）
MODES = {'gong': [0, 2, 4, 7, 9], 'shang': [0, 2, 5, 7, 10], 'jue': [0, 3, 5, 8, 10], 'zhi': [0, 2, 5, 7, 9], 'yu': [0, 3, 5, 7, 10]}
BPM = {'pastoral': 76, 'contemplative': 58, 'aspire': 88, 'tension': 84, 'march': 100, 'epic': 76, 'elegy': 56, 'triumph': 96,
       'grand': 66, 'wander': 92, 'joyful': 104, 'battle': 112, 'serene': 60, 'title': 70, 'outro': 62}
MOODS = set(BPM)
STAGE_DB = -21.0
MOOD_DB = {'battle': 2, 'epic': 2, 'triumph': 2, 'march': 1, 'contemplative': -2, 'elegy': -2, 'serene': -2, 'title': -1}


class Buf:
    def __init__(self, n: int):
        self.x = np.zeros((2, n))

    def put(self, sig: np.ndarray, t: float, vol: float = 1.0, pan: float = 0.0) -> None:
        i = int(t * SR)
        if i < 0 or i >= self.x.shape[1]:
            return
        n = min(len(sig), self.x.shape[1] - i)
        self.x[0, i:i + n] += sig[:n] * vol * (1 - 0.6 * pan)
        self.x[1, i:i + n] += sig[:n] * vol * (1 + 0.6 * pan)


def scale_notes(root: int, mode: str, lo: int, hi: int) -> list[int]:
    out = []
    for octv in range(-3, 5):
        for s in MODES[mode]:
            m = root + 12 * octv + s
            if lo <= m <= hi:
                out.append(m)
    return sorted(out)


def melody(rng: np.random.Generator, notes: list[int], beats: int, rhythm: list[list[float]]) -> list[tuple]:
    """五声音阶上的随机游走旋律：[(拍位, 时值拍数, 音高)]，乐句末落在主音或属音附近。"""
    out, b, i = [], 0.0, len(notes) // 2
    while b < beats - 1e-6:
        pat = rhythm[rng.integers(len(rhythm))]
        for d in pat:
            if b >= beats - 1e-6:
                break
            step = rng.choice([-2, -1, -1, 0, 1, 1, 2], p=[.08, .25, .1, .04, .25, .2, .08])
            i = int(np.clip(i + step, 0, len(notes) - 1))
            d = min(d, beats - b)
            out.append((b, d, notes[i]))
            b += d
    # 乐句收尾：最后一个音拉长并落到最近的主音
    if out:
        b0, d0, m0 = out[-1]
        tonic = min((m for m in notes if (m - notes[0]) % 12 == 0), key=lambda m: abs(m - m0))
        out[-1] = (b0, d0, tonic)
    return out


def gen_mood(mood: str, dur: float, root: int, mode: str, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    b = Buf(int((dur + 5) * SR))
    beat = 60 / BPM[mood]
    bar = beat * 4
    nbars = int(np.ceil(dur / bar)) + 1
    sc = MODES[mode]
    deg = lambda k, base=root: base + sc[k % 5] + 12 * (k // 5)   # 第 k 级音
    # 和声：五声里取根-五度-八度的空心和弦，按级数轮换
    prog = [0, 3, 4, 0, 2, 3, 1, 4] if mode != 'yu' else [0, 2, 3, 0, 4, 2, 1, 0]
    mel_hi = scale_notes(root + 12, mode, root + 10, root + 28)
    mel_mid = scale_notes(root, mode, root - 2, root + 17)
    phrase = 4  # 小节
    mel = []
    for k in range(0, nbars, phrase):
        notes = mel_hi if mood in ('pastoral', 'joyful', 'wander', 'aspire', 'serene') else mel_mid
        rhythm = {'joyful': [[0.5, 0.5, 1], [0.5, 0.5, 0.5, 0.5], [1, 1]], 'wander': [[0.5, 0.5, 1], [1.5, 0.5], [1, 0.5, 0.5]],
                  'march': [[1, 0.5, 0.5], [1, 1], [2]], 'battle': [[0.5, 0.5, 1], [1, 1]]}.get(mood, [[2], [1, 1], [3, 1], [1.5, 0.5, 2]])
        mel += [(bb + k * 4, d, m) for bb, d, m in melody(rng, notes, phrase * 4 - 2, rhythm)]
    rest = mood in ('contemplative', 'elegy', 'serene')

    for k in range(nbars):
        t0 = k * bar
        if t0 > dur + bar:
            break
        c = prog[k % len(prog)]
        r0 = deg(c, root - 12)
        pad = [r0, r0 + 7, r0 + 12]
        if mood == 'pastoral':
            b.put(O.strings(pad, bar, 0.25, 1.0, 1.4), t0, 0.6)
            arp = [deg(c), deg(c + 1), deg(c + 2), deg(c + 4), deg(c + 2), deg(c + 1), deg(c), deg(c + 2)]
            for i, m in enumerate(arp):
                b.put(O.pluck(m, 1.8, bright=0.5), t0 + i * beat / 2, 0.42, 0.35 * np.sin(i))
        elif mood == 'contemplative':
            b.put(O.drone(root - 24, bar), t0, 0.35)
            b.put(O.strings([r0, r0 + 7], bar, 0.12, 1.6, 1.6), t0, 0.35)
            if k % 2 == 0:
                b.put(O.guqin(deg(c, root - 12), 4.0), t0, 0.7, -0.2)
                b.put(O.guqin(deg(c + 2, root - 12), 3.0), t0 + beat * 2.5, 0.5, -0.2)
        elif mood == 'aspire':
            e = min(1.0, 0.6 + 0.4 * k / max(1, nbars - 1))
            b.put(O.strings(pad + [r0 + 16 if 4 in sc else r0 + 15], bar, 0.5 * e, 0.5, 0.8), t0, 0.7)
            for i in range(8):
                b.put(O.piano(deg(c + (i % 4), root), 1.0), t0 + i * beat / 2, 0.4 * e, 0.3)
            b.put(O.timpani(root - 24 + 12, 0.4), t0, 0.5)
        elif mood == 'tension':
            b.put(O.strings([r0, r0 + 1 + 12, r0 + 7], bar, 0.25, 0.6, 1.0), t0, 0.6)
            for i in range(8):
                b.put(O.cello_stac(root - 24 + (1 if i == 6 else 0)), t0 + i * beat / 2, 0.75, -0.2)
            b.put(O.timpani(root - 24 + 12, 0.7), t0, 0.6)
            if k % 4 == 3:
                b.put(O.timp_roll(root - 12, bar * 0.9, 0.5), t0, 0.8)
        elif mood == 'march':
            b.put(O.strings(pad, bar, 0.45, 0.3, 0.8), t0, 0.6)
            for i in range(8):
                b.put(O.cello_stac(r0 - 12 if i % 2 == 0 else r0 - 5, 0.22), t0 + i * beat / 2, 0.75, -0.2)
            for i, v in enumerate([1, .35, .6, .35, .9, .35, .6, .5]):
                b.put(O.snare(v), t0 + i * beat / 2, 0.5, 0.25)
            b.put(O.timpani(root - 12, 0.6), t0, 0.5)
        elif mood == 'epic':
            b.put(O.strings(pad + [r0 + 19], bar, 0.75, 0.5, 1.0), t0, 0.85)
            b.put(O.taiko(0.9), t0, 0.7)
            b.put(O.taiko(0.6), t0 + 2 * beat, 0.5)
            b.put(O.timpani(root - 12, 0.9), t0, 0.7)
            if k % 4 == 0:
                b.put(O.gong(0.6), t0, 0.5)
        elif mood == 'elegy':
            b.put(O.strings(pad, bar, 0.2, 1.4, 1.6), t0, 0.55)
            b.put(O.drone(root - 24, bar), t0, 0.3)
            if k % 2 == 1:
                b.put(O.guqin(deg(c, root - 12), 4.0), t0 + beat, 0.45, -0.3)
        elif mood == 'triumph':
            b.put(O.strings(pad + [r0 + 16, r0 + 19], bar, 0.85, 0.3, 0.8), t0, 0.8)
            b.put(O.brass([r0 + 12, r0 + 19, r0 + 24], bar * 0.95, swell=k % 2 == 1), t0, 0.7)
            b.put(O.timpani(root - 12, 0.9), t0, 0.8)
            for i in range(4):
                b.put(O.snare(0.5), t0 + i * beat, 0.35, 0.3)
            if k % 2 == 0:
                b.put(O.chimes(deg(c, root + 12)), t0, 0.5, 0.2)
        elif mood == 'grand':
            b.put(O.strings(pad + [r0 + 16 if 4 in sc else r0 + 15, r0 + 19], bar, 0.7, 0.8, 1.4), t0, 0.85)
            b.put(O.brass([r0 + 12, r0 + 19], bar * 0.98, swell=True), t0, 0.45)
            if k % 2 == 0:
                b.put(O.chimes(deg(c, root + 12)), t0, 0.55)
                b.put(O.timpani(root - 12, 0.6), t0, 0.6)
            if k % 8 == 0:
                b.put(O.gong(0.5), t0, 0.4)
        elif mood == 'wander':
            b.put(O.strings(pad, bar, 0.35, 0.6, 1.0), t0, 0.5)
            for i in range(8):
                m = deg(c + [0, 2, 1, 2, 0, 2, 4, 2][i])
                b.put(O.pluck(m, 0.9, bright=0.85, decay=0.993), t0 + i * beat / 2, 0.38, -0.35)
            for i in (0, 1.5, 2, 3):
                b.put(O.taiko(0.25), t0 + i * beat, 0.35)
        elif mood == 'joyful':
            b.put(O.strings(pad, bar, 0.4, 0.4, 0.8), t0, 0.45)
            for i in range(8):
                b.put(O.pluck(deg(c + [0, 2, 4, 2, 1, 2, 3, 4][i]), 1.2, bright=0.7), t0 + i * beat / 2, 0.38, 0.3)
            for i, v in enumerate([1, 0, .5, .7, 0, .5, 1, .4]):
                if v:
                    b.put(O.woodblock(v, 81 if i % 3 else 76), t0 + i * beat / 2, 0.5, -0.4)
        elif mood == 'battle':
            b.put(O.strings(pad + [r0 + 15], bar, 0.8, 0.1, 0.6), t0, 0.65)
            for i in range(8):
                b.put(O.taiko(1.0 if i in (0, 3, 6) else 0.5), t0 + i * beat / 2, 0.7)
                b.put(O.cello_stac(r0 - 12, 0.18), t0 + i * beat / 2, 0.9, -0.2)
            b.put(O.brass([r0 + 12, r0 + 19], beat * 0.6), t0, 0.7, 0.1)
            b.put(O.brass([r0 + 12, r0 + 19], beat * 1.4), t0 + beat * 2.5, 0.6, 0.1)
            if k % 4 == 0:
                b.put(O.gong(0.7), t0, 0.5)
        elif mood == 'serene':
            b.put(O.strings(pad + [r0 + 19], bar, 0.3, 1.5, 1.8), t0, 0.55)
            if k % 2 == 0:
                b.put(O.chimes(deg(c + 2, root + 12)), t0, 0.35, 0.3)
            for i in (0, 3, 5):
                b.put(O.pluck(deg(c + i % 5), 3.0, bright=0.4), t0 + i * beat / 2, 0.3, -0.3)
        elif mood == 'title':
            if k == 0:
                b.put(O.gong(1.0, 8.0), 0, 0.8)
                b.put(O.drone(root - 24, dur), 0, 0.7)
                b.put(O.strings([root - 12, root - 5, root], dur, 0.3, 2.5, 3.0), 0, 0.8)
            b.put(O.chimes(deg(k * 2, root + 12)), t0 + beat, 0.4, 0.3 * np.sin(k))
        elif mood == 'outro':
            b.put(O.strings(pad + [r0 + 16 if 4 in sc else r0 + 15], bar, 0.5, 1.0, 1.6), t0, 0.8)
            if k % 2 == 0:
                b.put(O.chimes(deg(c, root + 12)), t0, 0.45)
    # 主旋律声部
    lead = {'pastoral': 'flute', 'contemplative': 'xiao', 'aspire': 'flute', 'tension': 'erhu', 'march': 'brass', 'epic': 'brass',
            'elegy': 'erhu', 'triumph': 'brass', 'grand': 'brass', 'wander': 'flute', 'joyful': 'flute', 'battle': None,
            'serene': 'xiao', 'title': None, 'outro': 'erhu'}[mood]
    prev = None
    for bb, d, m in mel:
        t = bb * beat
        if t > dur or lead is None:
            break
        if rest and rng.random() < 0.25:
            continue
        if lead == 'flute':
            b.put(O.flute(m, d * beat * 0.95), t, 0.55, 0.15)
        elif lead == 'xiao':
            b.put(O.flute(m - 12, d * beat * 0.98, breath=0.25), t, 0.6, 0.1)
        elif lead == 'erhu':
            b.put(O.erhu(m, d * beat * 0.98, slide_from=prev if prev and abs(prev - m) <= 5 else None), t, 0.6, 0.1)
        elif lead == 'brass':
            b.put(O.brass([m, m - 12], d * beat * 0.95, swell=d >= 2), t, 0.45, 0.1)
        prev = m
    return b.x[:, :int((dur + 2.5) * SR)]


def fade_env(n: int, fin: float, fout: float) -> np.ndarray:
    e = np.ones(n)
    a, r = int(fin * SR), int(fout * SR)
    if a:
        e[:a] = np.linspace(0, 1, a) ** 1.5
    if r:
        e[-r:] *= np.linspace(1, 0, r) ** 1.5
    return e


def reverb(x: np.ndarray, wet: float = 0.25, decay: float = 1.6) -> np.ndarray:
    n = int(3.0 * SR)
    t = np.arange(n) / SR
    out = np.empty_like(x)
    for ch in range(2):
        ir = np.random.default_rng(11 + ch).standard_normal(n) * np.exp(-t / (decay / 3))
        ir = O.lp(ir, 5000)
        size = 1 << int(np.ceil(np.log2(x.shape[1] + n)))
        y = np.fft.irfft(np.fft.rfft(x[ch], size) * np.fft.rfft(ir, size), size)[:x.shape[1]]
        out[ch] = x[ch] + wet * y / np.sqrt(np.sum(ir ** 2))
    return out


def main(who: str) -> None:
    tl = json.loads((ROOT / 'src' / who / 'timeline.json').read_text())
    cfg = json.loads((ROOT / 'music' / f'{who}_stages.json').read_text())
    total = tl['total']
    N = int((total + 3) * SR)
    mix = Buf(N)
    for k, seg in enumerate(tl['music']):
        c = cfg[seg['stage']]
        assert c['mood'] in MOODS, c
        dur = seg['t1'] - seg['t0']
        x = gen_mood(c['mood'], dur + 1.5, c['root'], c['mode'], seed=zlib.crc32(f"{who}:{seg['stage']}".encode()))
        # 段间响度统一：目标 RMS（激烈情绪 +2 dB，安静情绪 -2 dB）
        rms = np.sqrt(np.mean(x[:, :int(dur * SR)] ** 2)) + 1e-9
        x = x * (10 ** ((STAGE_DB + MOOD_DB.get(c['mood'], 0)) / 20) / rms)
        env = fade_env(x.shape[1], 1.2 if k else 0.3, 2.4)
        i = int(max(0.0, seg['t0'] - 0.6) * SR)
        n = min(x.shape[1], N - i)
        mix.x[:, i:i + n] += x[:, :n] * env[:n]
        print(f"{seg['t0']:7.1f}–{seg['t1']:7.1f}  {seg['stage']:<8} {c['mood']}")
    root = cfg['title']['root']
    for ch in tl['chapters']:
        mix.put(O.gong(0.8), ch['t0'] + 0.1, 0.55)
        mix.put(O.chimes(root + 12), ch['t0'] + 0.15, 0.6, -0.2)
        mix.put(O.chimes(root + 19), ch['t0'] + 0.65, 0.45, 0.2)
    for s in tl['steps']:
        if 'ms' in s:
            mix.put(O.bell(root + 24), s['ms']['t0'], 0.55, 0.2)
            mix.put(O.timpani(root - 12, 0.5), s['ms']['t0'], 0.45)
    y = reverb(mix.x)
    y = y / (np.max(np.abs(y)) + 1e-9)
    y = np.tanh(y * 1.3) / np.tanh(1.3) * 0.9
    out = ROOT / 'out' / who / 'music.wav'
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y[:, :int(total * SR)].T * 32767).astype('<i2').tobytes())
    print('music', out, round(total, 1), 's')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
