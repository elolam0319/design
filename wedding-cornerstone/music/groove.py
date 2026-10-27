"""Upbeat original score for the cornerstone wedding film (38 s, 100 BPM, D major).

Written in the spirit of the reference edit (a driving, percussive track with a hit on every
cut) but sharing none of its material. All sounds are synthesized here. Hits sit on the
film's own cuts from index.html: seal 0.2 s, circle fills 4.5 s, cornerstone 5.9 s, blocks
from 11.4 s every eighth, dome 16.35 s, wipe 18.2 s, cards 18.7/19.9 s, doors 24.0/24.6 s,
digits 25-26.3 s, arch 29.6 s, poster 33.6 s, last chord 37.2 s.

usage: python groove.py out.wav
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 38.0
BEAT = 0.6
BAR = 4 * BEAT
S16 = BEAT / 4
rng = np.random.default_rng(220)
buses = {k: np.zeros(int(SR * (DUR + 3))) for k in ('drums', 'bass', 'keys', 'lead', 'fx')}


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def at(bar, beat=1.0):
    return (bar - 1) * BAR + (beat - 1) * BEAT


def add(bus, t, sig, gain=1.0):
    i = int(round(t * SR))
    if 0 <= i < len(buses[bus]):
        sig = sig[: len(buses[bus]) - i]
        buses[bus][i:i + len(sig)] += sig * gain


def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, 'same')


# ---------- drums ----------
def kick(v=1.0):
    n = int(SR * 0.4)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    click = rng.normal(0, 1, n) * np.exp(-t / 0.002) * 0.25
    return np.tanh((body + click) * 1.6) * v * 0.55


def clap(v=1.0):
    n = int(SR * 0.3)
    t = np.arange(n) / SR
    noise = np.diff(rng.normal(0, 1, n + 1))
    e = sum(np.exp(-np.maximum(0, t - o) / 0.006) * (t >= o) for o in (0, 0.011, 0.022))
    e += np.exp(-np.maximum(0, t - 0.033) / 0.09) * (t >= 0.033)
    return noise * e * v * 0.16


def hat(v=1.0, open_=False):
    n = int(SR * (0.25 if open_ else 0.05))
    x = np.diff(np.diff(rng.normal(0, 1, n + 2)))
    return x * env(n, 0.001, 0.08 if open_ else 0.012) * v * 0.05


def tick(v=1.0):
    n = int(SR * 0.03)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2200 * t) * np.exp(-t / 0.006) * v * 0.18


# ---------- tonal ----------
def pluck(m, dur=0.5, v=1.0, bright=0.5):
    """Karplus-Strong, run a period at a time so it stays vectorized."""
    p = max(2, int(round(SR / hz(m))))
    n = int(SR * (dur + 0.3))
    y = np.zeros(n + p)
    y[:p] = lowpass(rng.uniform(-1, 1, p), max(1, int(4 * (1 - bright))))
    damp = 0.996 if m < 60 else 0.992
    for s in range(p, n + p, p):
        prev = y[s - p:s]
        prev1 = y[s - p - 1:s - 1] if s > p else np.concatenate([[0.0], y[:p - 1]])
        e = min(s + p, n + p)
        nxt = 0.5 * (prev + prev1) * damp
        y[s:e] = nxt[: e - s]
    y = y[:n]
    rel = np.ones(n)
    k = int(SR * dur)
    rel[k:] = np.exp(-np.arange(n - k) / SR / 0.06)
    return y * rel * v * 0.35


def marimba(m, v=1.0):
    n = int(SR * 0.9)
    t = np.arange(n) / SR
    f = hz(m)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.35) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.05)
    return x * np.minimum(1, t / 0.001) * v * 0.22


def bass(m, dur, v=1.0):
    n = int(SR * (dur + 0.05))
    t = np.arange(n) / SR
    f = hz(m)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    e = np.minimum(1, t / 0.004) * np.where(t < dur, np.exp(-t / 0.5), 0)
    return np.tanh(x * e * 1.5) * v * 0.32


def stab(notes, dur, v=1.0):
    n = int(SR * (dur + 0.25))
    t = np.arange(n) / SR
    x = np.zeros(n)
    for m in notes:
        for d in (-0.08, 0.08):
            f = hz(m + d)
            for k in range(1, 7):                      # band-limited saw, a few partials
                x += np.sin(2 * np.pi * k * f * t) / k * np.exp(-t * k * 3)
    e = np.minimum(1, t / 0.003) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.08))
    return x * e * v * 0.05 / len(notes) ** 0.5


def pad(notes, dur, v=1.0):
    n = int(SR * (dur + 1.0))
    t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * hz(m) * t + 0.004 * hz(m) * np.sin(2 * np.pi * 4.5 * t) / 4.5) for m in notes)
    e = np.minimum(1, t / 0.5) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.4))
    return x * e * v * 0.022 / len(notes) ** 0.5


# ---------- fx ----------
def riser(dur, v=1.0):
    n = int(SR * dur)
    t = np.arange(n) / SR
    k = t / dur
    noise = rng.normal(0, 1, n)
    out = np.zeros(n)
    seg = n // 16
    for i in range(16):                               # brighter as it rises
        a, b = i * seg, n if i == 15 else (i + 1) * seg
        out[a:b] = lowpass(noise, max(1, 40 - i * 2))[a:b]
    sweep = np.sin(2 * np.pi * np.cumsum(300 + 1500 * k ** 2) / SR) * 0.15
    return (out + sweep) * k ** 2 * v * 0.11


def impact(v=1.0):
    n = int(SR * 1.8)
    t = np.arange(n) / SR
    low = np.sin(2 * np.pi * (34 + 60 * np.exp(-t / 0.05)) * t) * np.exp(-t / 0.5)
    hit = lowpass(rng.normal(0, 1, n), 14) * np.exp(-t / 0.06) * 0.3
    return np.tanh((low + hit) * 1.3) * v * 0.5


def whoosh(dur=0.5, v=1.0):
    n = int(SR * dur)
    t = np.arange(n) / SR
    e = np.sin(np.pi * t / dur) ** 2
    return lowpass(rng.normal(0, 1, n), 20) * e * v * 0.07


# ---------- harmony ----------
CH = {'D': (38, [62, 66, 69]), 'Bm': (35, [62, 66, 71]), 'G': (43, [62, 67, 71]),
      'A': (45, [61, 64, 69]), 'Em': (40, [64, 67, 71]), 'F#m': (42, [61, 66, 69])}
LOOP = ['D', 'Bm', 'G', 'A']
chords = {b: LOOP[(b - 1) % 4] for b in range(1, 17)}
chords.update({13: 'G', 14: 'A', 15: 'G', 16: 'A'})

# sections: intro 1-2, cornerstone 3-4, build 5-7, full 8.5-12, venue 13-14, finale 15-16
for b in range(1, 17):
    root, up = CH[chords[b]]
    t0 = at(b)
    full = 9 <= b <= 12 or b == 15 or (b == 16)
    # pads under everything, a little louder in the open sections
    add('keys', t0, pad([root + 24] + up, BAR, 1.0 if b in (3, 4, 13, 14) else 0.6))
    # plucked chord rhythm (the "dotted" figure: 1, 1a, 2&, 3&, 4)
    if b >= 2:
        for off in (0, 0.75, 1.5, 2.5, 3.5):
            for m in up:
                add('keys', t0 + off * BEAT, pluck(m + 12, 0.28, 0.5 if full else 0.45 if b in (3, 4) else 0.35, 0.6))
    if b in (3, 4):                                   # verse: keep a soft pulse under the words
        for i in range(8):
            add('drums', t0 + i * BEAT / 2, hat(0.6 if i % 2 else 0.35))
        add('drums', t0, kick(0.6))
        add('drums', t0 + 2 * BEAT, kick(0.5))
        if b == 4:
            add('drums', t0 + 3 * BEAT, clap(0.5))
    if b >= 5:
        # bass: root on eighths with an octave lift on the "and" of 4
        for i in range(8):
            if b == 16 and i >= 4:
                break
            m = root + (12 if i == 7 else 0)
            add('bass', t0 + i * BEAT / 2, bass(m, BEAT / 2 * 0.8, 1.0 if full else 0.7))
    if full:
        for i in range(4):
            if b == 16 and i >= 2:
                break
            add('drums', t0 + i * BEAT, kick())
            if i in (1, 3):
                add('drums', t0 + i * BEAT, clap())
        for i in range(16):
            if b == 16 and i >= 8:
                break
            add('drums', t0 + i * S16, hat(0.9 if i % 2 else 0.5, open_=(i % 4 == 2)))
        add('keys', t0, stab([m + 12 for m in up], BEAT * 0.4, 0.8))
    elif 5 <= b <= 8:                                 # build: kick on the beat, hats on eighths
        for i in range(4):
            add('drums', t0 + i * BEAT, kick(0.8))
        for i in range(8):
            add('drums', t0 + i * BEAT / 2, hat(0.7 if i % 2 else 0.4))
        if b == 8:                                    # snare-roll style clap build into the drop
            for i in range(8):
                add('drums', t0 + 2 * BEAT + i * S16, clap(0.3 + i * 0.08))
    elif b in (13, 14):                               # venue: half-time
        add('drums', t0, kick(0.8))
        add('drums', t0 + 2 * BEAT, clap(0.8))
        for i in range(4):
            add('drums', t0 + i * BEAT + BEAT / 2, hat(0.6))
    elif b == 1 or b == 2:
        for i in range(4):
            add('drums', t0 + i * BEAT + BEAT / 2, hat(0.35))

# hook: a short bright motif on marimba, answered each time it returns
HOOK = [(0, 74), (0.75, 76), (1.5, 78), (2.5, 81), (3, 78)]
for b in (2, 9, 11, 15):
    for off, m in HOOK:
        add('lead', at(b) + off * BEAT, marimba(m + 12, 0.9))
for b in (10, 12):
    for off, m in [(0, 81), (0.75, 78), (1.5, 76), (2.5, 74), (3, 73)]:
        add('lead', at(b) + off * BEAT, marimba(m + 12, 0.8))

# ---------- hits on the picture's cuts ----------
add('fx', 0.2, impact(0.5))                                   # seal pops
add('fx', 3.6, riser(0.9, 1.0)); add('fx', 4.5, impact(0.7))  # circle fills the frame
add('fx', 5.9, impact(1.0))                                   # cornerstone lands
add('bass', 5.9, bass(26, 1.2, 1.0))
scale = [74, 76, 78, 81, 83, 86, 88, 90, 93, 95, 98, 100, 102, 105, 107]
for i in range(15):                                           # each block lands
    add('lead', 11.4 + i * 0.3, marimba(scale[i] - 12, 0.75))
add('fx', 16.35, impact(0.6))                                 # dome
for i, m in enumerate([93, 97, 100, 105]):                    # doves
    add('lead', 16.7 + i * 0.1, marimba(m, 0.4))
add('fx', 17.3, riser(0.9, 1.1)); add('fx', 18.2, impact(0.9))   # wipe -> names drop
add('fx', 18.55, whoosh(0.4)); add('fx', 19.75, whoosh(0.4))     # cards slide in
add('fx', 20.6, impact(0.4))                                     # & pops
add('fx', 23.2, riser(0.8, 1.0)); add('fx', 24.0, impact(1.0))   # doors shut
add('fx', 24.6, whoosh(0.7, 1.2))                                # doors fold open
for i in range(9):                                               # digits roll
    add('fx', 25.0 + i * S16 * 2.33, tick(0.8))
add('fx', 26.3, impact(0.5))
add('fx', 28.8, whoosh(0.9, 1.2)); add('fx', 29.6, impact(0.6))  # arch rises
add('fx', 32.8, riser(0.8, 1.0)); add('fx', 33.6, impact(0.9))   # poster
for i in range(10):                                              # little house
    add('lead', 35.1 + i * 0.1, marimba([86, 88, 90, 93, 95, 90, 93, 95, 98, 102][i], 0.35))
add('fx', 37.2, impact(1.0))                                     # last chord
for m in [62, 66, 69, 74, 78]:
    add('keys', 37.2, pluck(m + 12, 0.8, 0.6, 0.7))
add('keys', 37.2, pad([50, 62, 66, 69, 74], 0.8, 1.2))
add('bass', 37.2, bass(38, 0.8, 1.0))


# ---------- mix ----------
def room(x, secs=1.2, wet=0.18):
    n = int(SR * secs)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, n) * np.exp(-t / (secs / 6.5))
    ir[0] = 0
    nfft = 1 << (len(x) + n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
    return x + wet * y / (np.max(np.abs(y)) + 1e-9) * np.max(np.abs(x))


# keep the low end clear of the kick: duck bass and pads a little on each kick
duck = np.ones(len(buses['bass']))
kick_times = [at(b) + i * BEAT for b in range(5, 17) for i in range(4)]
for kt in kick_times:
    i = int(kt * SR)
    n = int(SR * 0.18)
    if i + n < len(duck):
        duck[i:i + n] = np.minimum(duck[i:i + n], 0.55 + 0.45 * np.linspace(0, 1, n))

out = (buses['drums'] * 1.0 + buses['bass'] * duck * 0.9 + room(buses['keys']) * duck * 0.9 +
       room(buses['lead'], 1.6, 0.3) * 0.8 + room(buses['fx'], 1.5, 0.2) * 0.8)
out = out[: int(SR * DUR)]
out -= np.convolve(out, np.ones(int(SR / 30)) / int(SR / 30), 'same')     # clear DC and sub-rumble
t = np.arange(len(out)) / SR
out *= np.minimum(1, t / 0.01) * np.where(t > DUR - 0.6, np.clip((DUR - t) / 0.6, 0, 1), 1)
out = np.tanh(out * 1.6) / np.tanh(1.6)
out *= 0.89 / np.max(np.abs(out))

# width: hats and plucks feel wider with a short opposite-side delay
d = int(SR * 0.011)
right = np.concatenate([np.zeros(d), out[:-d]]) * 0.35 + out * 0.65
pcm = (np.stack([out, right], 1) * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote', sys.argv[1], f'{len(out) / SR:.2f}s')
