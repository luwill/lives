"""管弦风格合成音色（纯 numpy/scipy，原创）：弦乐铺底、低音弦断奏、铜管、定音鼓、大鼓、军鼓、钢琴、钟、低频 drone。"""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
RNG = np.random.default_rng(7)


def mtof(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(dur: float) -> np.ndarray:
    return np.arange(int(dur * SR)) / SR


def lp(x: np.ndarray, fc: float, order: int = 2) -> np.ndarray:
    return sosfilt(butter(order, min(fc, SR * 0.45) / (SR / 2), 'low', output='sos'), x)


def hp(x: np.ndarray, fc: float, order: int = 2) -> np.ndarray:
    return sosfilt(butter(order, fc / (SR / 2), 'high', output='sos'), x)


def bp(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return sosfilt(butter(2, [lo / (SR / 2), hi / (SR / 2)], 'band', output='sos'), x)


def adsr(n: int, a: float, d: float, s: float, r: float) -> np.ndarray:
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rn = min(n, int(r * SR))
    if rn:
        e[-rn:] *= np.linspace(1, 0, rn) ** 1.5
    return e


def _saw_bl(f: np.ndarray | float, t: np.ndarray, phase: float = 0.0) -> np.ndarray:
    """简易抗混叠锯齿：有限谐波叠加（频率随时间变化时用相位积分）。"""
    f = np.broadcast_to(np.asarray(f, float), t.shape)
    ph = 2 * np.pi * (np.cumsum(f) / SR + phase)
    nh = int(min(40, SR / 2 / max(float(f.max()), 20)))
    return sum(np.sin(k * ph) / k for k in range(1, nh + 1)) * (2 / np.pi)


def strings(ms: list, dur: float, bright: float = 1.0, att: float = 0.8, rel: float = 1.2) -> np.ndarray:
    """弦乐铺底：每音 3 个失谐声部 + 颤音 + 慢起音。"""
    t = tt(dur + rel)
    x = np.zeros(len(t))
    for i, m in enumerate(ms):
        for det in (-0.07, 0.0, 0.08):
            vib = 1 + 0.004 * np.sin(2 * np.pi * (5.2 + 0.3 * i + det) * t + i)
            x += _saw_bl(mtof(m + det) * vib, t, (i * 0.37 + det) % 1)
    x = lp(x / len(ms), 900 + 2600 * bright, 2)
    return 0.16 * x * adsr(len(t), att, 1.0, 0.9, rel)


def cello_stac(m: float, dur: float = 0.28, vol: float = 1.0) -> np.ndarray:
    """低音弦断奏（ostinato 用）。"""
    t = tt(dur + 0.08)
    x = _saw_bl(mtof(m), t) + 0.6 * _saw_bl(mtof(m + 12.03), t)
    return vol * 0.2 * lp(x, 1400) * adsr(len(t), 0.012, 0.12, 0.45, 0.06)


def brass(ms: list, dur: float, vol: float = 1.0, swell: bool = False) -> np.ndarray:
    """铜管：滤波包络开合，模拟吹奏起音。"""
    t = tt(dur + 0.4)
    x = np.zeros(len(t))
    for m in ms:
        x += _saw_bl(mtof(m) * (1 + 0.003 * np.sin(2 * np.pi * 5 * t)), t)
    x /= len(ms)
    env = adsr(len(t), 0.9 if swell else 0.05, 0.4, 0.8, 0.35)
    # 起音时滤波器快速打开，模拟“嘟”的铜管质感
    seg = int(0.02 * SR)
    out = np.zeros_like(x)
    for i in range(0, len(x), seg):
        fc = 700 + 2600 * env[i] ** 1.5
        out[i:i + seg] = lp(x[max(0, i - 256):i + seg], fc)[-len(x[i:i + seg]):]
    return vol * 0.22 * np.tanh(1.6 * out) * env


def timpani(m: float = 38, vol: float = 1.0, dur: float = 2.2) -> np.ndarray:
    t = tt(dur)
    f = mtof(m) * (1 + 0.06 * np.exp(-t * 30))
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) + 0.5 * np.sin(1.5 * ph) * np.exp(-t * 3) + 0.25 * np.sin(1.98 * ph) * np.exp(-t * 4)
    hit = lp(RNG.standard_normal(len(t)), 2200) * np.exp(-t * 60) * 0.5
    return vol * 0.55 * (body * np.exp(-t * 2.2) + hit)


def timp_roll(m: float, dur: float, vol: float = 1.0) -> np.ndarray:
    t = tt(dur + 1.5)
    x = np.zeros(len(t))
    k, step = 0, 0.055
    while k * step < dur:
        a = (k * step / dur) ** 1.6
        s = timpani(m, 0.25 + 0.75 * a, 1.5)
        i = int(k * step * SR)
        n = min(len(s), len(x) - i)
        x[i:i + n] += s[:n] * (0.9 + 0.2 * RNG.random())
        k += 1
    return vol * 0.55 * x


def taiko(vol: float = 1.0) -> np.ndarray:
    t = tt(1.4)
    ph = 2 * np.pi * np.cumsum(55 + 70 * np.exp(-t * 25)) / SR
    body = np.tanh(2.2 * np.sin(ph)) * np.exp(-t * 4.5)
    skin = lp(RNG.standard_normal(len(t)), 900) * np.exp(-t * 40)
    return vol * 0.8 * (body + 0.6 * skin)


def snare(vol: float = 1.0) -> np.ndarray:
    t = tt(0.25)
    noise = bp(RNG.standard_normal(len(t)), 1500, 9000) * np.exp(-t * 22)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 35)
    return vol * 0.28 * (noise + 0.6 * body)


def piano(m: float, dur: float = 2.5, vol: float = 1.0) -> np.ndarray:
    t = tt(dur)
    f = mtof(m)
    x = np.zeros(len(t))
    for k, a in enumerate((1, 0.55, 0.3, 0.18, 0.1, 0.06), 1):
        fk = f * k * (1 + 0.0004 * k * k)   # 轻微非谐性
        x += a * np.sin(2 * np.pi * fk * t) * np.exp(-t * (1.2 + 0.9 * k))
    hammer = lp(RNG.standard_normal(len(t)), 3000) * np.exp(-t * 200) * 0.05
    return vol * 0.2 * (x + hammer) * adsr(len(t), 0.003, 1, 1, 0.2)


def bell(m: float, vol: float = 1.0) -> np.ndarray:
    t = tt(4.0)
    f = mtof(m)
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d)
            for r, a, d in ((1, 1, 0.9), (2.76, 0.5, 1.6), (5.4, 0.25, 2.8), (8.9, 0.12, 4)))
    return vol * 0.14 * x


def drone(m: float, dur: float, vol: float = 1.0) -> np.ndarray:
    t = tt(dur + 2)
    x = np.sin(2 * np.pi * mtof(m) * t) + 0.5 * np.sin(2 * np.pi * mtof(m + 12) * t + 1) \
        + 0.3 * lp(RNG.standard_normal(len(t)), 180)
    return vol * 0.18 * x * adsr(len(t), 2.0, 1, 1, 2.0)


def boom(vol: float = 1.0) -> np.ndarray:
    """电影式低频冲击。"""
    t = tt(4.0)
    ph = 2 * np.pi * np.cumsum(28 + 70 * np.exp(-t * 5)) / SR
    return vol * (0.9 * np.tanh(1.8 * np.sin(ph)) * np.exp(-t * 1.2) + 0.2 * lp(RNG.standard_normal(len(t)), 3000) * np.exp(-t * 4))


def riser(dur: float, vol: float = 1.0) -> np.ndarray:
    t = tt(dur)
    k = t / dur
    n = RNG.standard_normal(len(t))
    out = np.zeros(len(t))
    seg = int(0.04 * SR)
    for i in range(0, len(t), seg):
        fc = 300 + 5000 * k[i] ** 2
        out[i:i + seg] = bp(n[i:i + seg], fc * 0.7, min(fc * 1.4, 16000))
    return vol * 0.25 * out * k ** 2


# ---------- 民族乐器音色（原创合成） ----------
def pluck(m: float, dur: float = 2.5, vol: float = 1.0, bright: float = 0.6, decay: float = 0.996) -> np.ndarray:
    """Karplus-Strong 拨弦：古筝/琵琶。bright 越大音色越亮。"""
    f = mtof(m)
    n = int(dur * SR)
    p = max(2, int(SR / f))
    buf = RNG.uniform(-1, 1, p)
    buf = lp(buf, 1200 + 6000 * bright)
    out = np.empty(n)
    idx = 0
    for i in range(n):
        out[i] = buf[idx]
        nxt = (idx + 1) % p
        buf[idx] = decay * 0.5 * (buf[idx] + buf[nxt])
        idx = nxt
    env = adsr(n, 0.002, 1, 1, 0.08)
    return vol * 0.45 * out * env


def guqin(m: float, dur: float = 4.0, vol: float = 1.0) -> np.ndarray:
    """古琴：低沉、长余音，带轻微滑音（吟猱）。"""
    t = tt(dur)
    f = mtof(m) * (1 + 0.006 * np.sin(2 * np.pi * 4.5 * t) * np.clip(t - 0.4, 0, 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(a * np.sin(k * ph) * np.exp(-t * (0.8 + 0.7 * k)) for k, a in enumerate((1, 0.45, 0.3, 0.12, 0.08), 1))
    thump = lp(RNG.standard_normal(len(t)), 900) * np.exp(-t * 80) * 0.15
    return vol * 0.32 * (x + thump) * adsr(len(t), 0.004, 1, 1, 0.3)


def flute(m: float, dur: float, vol: float = 1.0, breath: float = 0.12) -> np.ndarray:
    """笛/箫：正弦为主 + 气声 + 渐入颤音。"""
    t = tt(dur + 0.25)
    vib = 1 + 0.007 * np.sin(2 * np.pi * 5.3 * t) * np.clip(t / 0.5, 0, 1)
    ph = 2 * np.pi * np.cumsum(mtof(m) * vib) / SR
    tone = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    air = bp(RNG.standard_normal(len(t)), mtof(m) * 0.8, min(mtof(m) * 4, 16000)) * breath
    return vol * 0.2 * (tone + air) * adsr(len(t), 0.07, 0.3, 0.85, 0.25)


def erhu(m: float, dur: float, vol: float = 1.0, slide_from: float | None = None) -> np.ndarray:
    """二胡：锯齿 + 共鸣峰滤波 + 揉弦，可从前一音滑入。"""
    t = tt(dur + 0.3)
    mm = np.full(len(t), float(m))
    if slide_from is not None:
        k = np.clip(t / 0.12, 0, 1)
        mm = slide_from + (m - slide_from) * (1 - (1 - k) ** 2)
    vib = 0.18 * np.sin(2 * np.pi * 6 * t) * np.clip((t - 0.15) / 0.4, 0, 1)
    f = 440.0 * 2 ** ((mm + vib - 69) / 12)
    x = _saw_bl(f, t)
    x = bp(x, 400, 3500) + 0.4 * bp(x, 900, 1400)
    return vol * 0.16 * np.tanh(1.3 * x) * adsr(len(t), 0.08, 0.5, 0.85, 0.25)


def gong(vol: float = 1.0, dur: float = 6.0) -> np.ndarray:
    """锣：非谐分音 + 慢起的“嗡”声。"""
    t = tt(dur)
    x = sum(a * np.sin(2 * np.pi * f * t + RNG.random() * 6) * np.exp(-t * d)
            for f, a, d in ((92, 1, 0.5), (147, 0.7, 0.7), (211, 0.5, 0.9), (287, 0.4, 1.1), (433, 0.3, 1.5), (611, 0.2, 2.0)))
    shimmer = bp(RNG.standard_normal(len(t)), 1500, 6000) * np.exp(-t * 1.5) * np.clip(t / 0.3, 0, 1) * 0.15
    hit = lp(RNG.standard_normal(len(t)), 2500) * np.exp(-t * 40) * 0.3
    return vol * 0.35 * (x + shimmer + hit)


def woodblock(vol: float = 1.0, m: float = 79) -> np.ndarray:
    t = tt(0.18)
    return vol * 0.35 * np.sin(2 * np.pi * mtof(m) * t) * np.exp(-t * 45)


def chimes(m: float, vol: float = 1.0) -> np.ndarray:
    """编钟：两个相距小三度左右的分音。"""
    t = tt(5.0)
    f = mtof(m)
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in ((1, 1, 0.7), (1.19, 0.6, 0.9), (2.9, 0.3, 2.2), (5.1, 0.12, 3.5)))
    hit = lp(RNG.standard_normal(len(t)), 4000) * np.exp(-t * 90) * 0.1
    return vol * 0.16 * (x + hit)
