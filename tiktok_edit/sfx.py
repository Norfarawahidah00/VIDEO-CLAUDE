"""Cute, copyright-free sound effects synthesised from scratch with numpy.

Every effect is a function returning a mono float32 array at SR Hz.
`mix_timeline` places effects on a timeline and writes a stereo WAV.
"""
import wave

import numpy as np

SR = 48000
_rng = np.random.default_rng(7)


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def _env(t, attack, decay):
    """Fast linear attack, exponential decay."""
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-np.maximum(t - attack, 0) / decay)


def _sweep(f0, f1, t, curve="exp"):
    """Sine with frequency gliding from f0 to f1 over len(t)."""
    dur = t[-1] if len(t) else 1
    if curve == "exp":
        f = f0 * (f1 / f0) ** (t / dur)
    else:
        f = f0 + (f1 - f0) * (t / dur)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def _bandpass(x, lo, hi):
    """Brick-wall band-pass in the frequency domain (fine for short noise)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def _norm(x, peak=0.9):
    m = np.max(np.abs(x)) or 1
    return (x / m * peak).astype(np.float32)


def pop():
    t = _t(0.09)
    body = _sweep(950, 260, t) * _env(t, 0.002, 0.03)
    click = _bandpass(_rng.standard_normal(len(t)), 2000, 7000) * _env(t, 0.0005, 0.004)
    return _norm(body + 0.25 * click)


def bubble():
    t = _t(0.14)
    s = _sweep(320, 1300, t) * _env(t, 0.004, 0.045)
    return _norm(s)


def tick():
    """Bright 'tick' for each checklist item."""
    t = _t(0.07)
    s = (np.sin(2 * np.pi * 2600 * t) + 0.5 * np.sin(2 * np.pi * 5200 * t)) * _env(t, 0.0008, 0.012)
    n = _bandpass(_rng.standard_normal(len(t)), 3000, 9000) * _env(t, 0.0003, 0.003)
    return _norm(s + 0.3 * n, 0.8)


def sparkle(dur=0.7, n=9):
    t = _t(dur)
    out = np.zeros_like(t)
    for i in range(n):
        start = int((i / n) * dur * 0.7 * SR + _rng.integers(0, 800))
        f = _rng.uniform(2800, 6500)
        tt = _t(0.18)
        ping = np.sin(2 * np.pi * f * tt) * _env(tt, 0.002, 0.05) * _rng.uniform(0.4, 1.0)
        end = min(len(out), start + len(ping))
        out[start:end] += ping[: end - start]
    return _norm(out, 0.7)


def ding():
    t = _t(1.1)
    f0 = 1568.0
    s = np.zeros_like(t)
    for ratio, amp, dec in [(1, 1, 0.45), (2.0, 0.45, 0.3), (2.76, 0.3, 0.22), (5.4, 0.15, 0.12)]:
        s += amp * np.sin(2 * np.pi * f0 * ratio * t) * _env(t, 0.002, dec)
    return _norm(s, 0.75)


def whoosh(dur=0.45):
    n = int(dur * SR)
    noise = _rng.standard_normal(n)
    # sweep a resonant band-pass upward by processing in short overlapping blocks
    out = np.zeros(n)
    blk = 1024
    win = np.hanning(blk)
    for i, start in enumerate(range(0, n - blk, blk // 2)):
        p = start / n
        centre = 400 + 3500 * p
        seg = _bandpass(noise[start:start + blk] * win, centre * 0.6, centre * 1.6)
        out[start:start + blk] += seg
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return _norm(out * env, 0.7)


def pen_write(dur=0.9):
    """Scratchy marker-on-paper sound: band-passed noise in stroke bursts."""
    n = int(dur * SR)
    noise = _bandpass(_rng.standard_normal(n), 2500, 7500)
    t = np.arange(n) / SR
    strokes = np.zeros(n)
    pos = 0.0
    while pos < dur:
        length = _rng.uniform(0.06, 0.14)
        a, b = int(pos * SR), int(min(dur, pos + length) * SR)
        seg_t = np.linspace(0, 1, b - a)
        strokes[a:b] = np.sin(np.pi * seg_t) * _rng.uniform(0.5, 1.0)
        pos += length + _rng.uniform(0.01, 0.04)
    wobble = 0.7 + 0.3 * np.sin(2 * np.pi * 23 * t)
    return _norm(noise * strokes * wobble, 0.5)


def shimmer(dur=1.0):
    """Magic shimmer: rising arpeggio with tremolo + airy noise."""
    t = _t(dur)
    out = np.zeros_like(t)
    notes = [1046.5, 1318.5, 1568.0, 2093.0, 2637.0, 3136.0, 4186.0]
    for i, f in enumerate(notes):
        start = int(i * 0.055 * SR)
        tt = _t(dur - i * 0.055)
        trem = 0.75 + 0.25 * np.sin(2 * np.pi * 14 * tt)
        tone = np.sin(2 * np.pi * f * tt) * _env(tt, 0.004, 0.22) * trem
        out[start:start + len(tone)] += tone[: len(out) - start]
    air = _bandpass(_rng.standard_normal(len(t)), 6000, 12000) * np.sin(np.pi * t / dur) ** 2
    return _norm(out + 0.15 * air, 0.6)


def kaching():
    """Cash register: short mechanical 'ka' then a bright metallic 'ching'."""
    t = _t(1.2)
    ka = _bandpass(_rng.standard_normal(len(t)), 1500, 5000) * _env(t, 0.001, 0.015)
    off = int(0.07 * SR)
    tc = _t(1.2 - 0.07)
    ching = np.zeros_like(tc)
    for f, amp in [(2093, 1), (2637, 0.8), (3136, 0.7), (4186, 0.5), (5274, 0.35), (2120, 0.6)]:
        ching += amp * np.sin(2 * np.pi * f * tc) * _env(tc, 0.002, 0.35)
    out = 0.8 * ka
    out[off:off + len(ching)] += ching
    # a few coin jingles
    for k in range(4):
        st = int((0.12 + 0.07 * k) * SR)
        tt = _t(0.12)
        out[st:st + len(tt)] += 0.35 * np.sin(2 * np.pi * _rng.uniform(5000, 7000) * tt) * _env(tt, 0.001, 0.03)
    return _norm(out, 0.85)


LIBRARY = {
    "pop": pop,
    "bubble": bubble,
    "tick": tick,
    "sparkle": sparkle,
    "ding": ding,
    "whoosh": whoosh,
    "pen": pen_write,
    "shimmer": shimmer,
    "kaching": kaching,
}


def mix_timeline(events, total_dur, path, master_peak=0.89):
    """events: list of (time_sec, name, gain, pan[-1..1]). Writes 16-bit stereo WAV."""
    n = int(total_dur * SR) + SR
    L = np.zeros(n)
    R = np.zeros(n)
    cache = {}
    for t0, name, gain, pan in events:
        if name not in cache:
            cache[name] = LIBRARY[name]()
        s = cache[name] * gain
        a = int(t0 * SR)
        b = min(n, a + len(s))
        lg, rg = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
        L[a:b] += s[: b - a] * lg * 1.414
        R[a:b] += s[: b - a] * rg * 1.414
    st = np.stack([L, R], 1)[: int(total_dur * SR)]
    peak = np.max(np.abs(st)) or 1
    st = st / peak * master_peak
    pcm = (st * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
