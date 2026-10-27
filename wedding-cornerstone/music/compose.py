"""Original background score for the cornerstone wedding film (38 s, 100 BPM, D major).

Everything is synthesized here (no samples), so the track is ours to use. Cues follow the
film's timeline in index.html: the cornerstone lands at 5.9 s, each block lands on an
eighth note from 11.4 s, the doors shut on the bar line at 24.0 s, the digits roll at 25 s.

usage: python compose.py out.wav [--hymn | --love]

--hymn sets AURELIA (S. S. Wesley, 1864, public domain; "The Church's One Foundation",
새찬송가 "교회의 참된 터는") as the melody instead of the original tune. Its eight lines of
two bars each fill the film's sixteen bars. Only the opening phrase was checked against a
published incipit (3-3-3-4-3-3-2-1-1-6-5-4-3-4-5); the rest is written from memory and
still needs checking against a printed score.

--love sets SANDRINGHAM (J. Barnby, 1889, public domain; "O Perfect Love", 결혼 찬송
"완전한 사랑") after a two-bar intro: four lines of three bars, then a two-bar coda.
Line one follows the published incipit (1-3-5-5-5-5-5-1-7-7-6-2-3-4-5); the rest is
written from memory and needs checking against a printed score.
"""
import sys
import wave

import numpy as np

HYMN = '--hymn' in sys.argv
LOVE = '--love' in sys.argv
SR = 44100
DUR = 38.0
BEAT = 0.6           # 100 BPM
BAR = 4 * BEAT
rng = np.random.default_rng(20270220)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def at(bar, beat=1.0):
    return (bar - 1) * BAR + (beat - 1) * BEAT


mix = {k: np.zeros(int(SR * (DUR + 4))) for k in ('piano', 'pad', 'bell', 'drum', 'fx')}


def add(bus, t, sig):
    i = int(t * SR)
    if i >= len(mix[bus]):
        return
    sig = sig[: len(mix[bus]) - i]
    mix[bus][i:i + len(sig)] += sig


# ---------- instruments ----------
def piano(m, dur, vel=0.5):
    f, n = hz(m), int(SR * (dur + 1.2))
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, 9):
        fk = k * f * np.sqrt(1 + 0.0004 * k * k)
        if fk > SR / 2.2:
            break
        out += np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t * (0.9 + 0.55 * k)) / k ** 1.25
    out *= np.minimum(1, t / 0.004)
    off = int(SR * dur)
    rel = np.ones(n)
    rel[off:] = np.exp(-(t[off:] - dur) / 0.18)
    hammer = rng.normal(0, 1, n) * np.exp(-t / 0.006) * 0.04
    return (out * rel + hammer) * vel * 0.32


def pad(notes, dur, vel=0.5):
    n = int(SR * (dur + 1.6))
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in notes:
        for d in (-0.07, 0, 0.07):
            f = hz(m + d)
            out += np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) + 0.18 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 0.9) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.6))
    trem = 1 + 0.06 * np.sin(2 * np.pi * 0.35 * t)
    return out * env * trem * vel * 0.035 / max(1, len(notes)) ** 0.5


def bell(m, vel=0.4, decay=1.4):
    f = hz(m)
    n = int(SR * (decay * 2.5))
    t = np.arange(n) / SR
    out = np.zeros(n)
    for r, a in ((1, 1), (2.756, .38), (5.404, .16), (8.933, .07)):
        if r * f < SR / 2.2:
            out += a * np.sin(2 * np.pi * r * f * t) * np.exp(-t * r ** 0.7 / decay)
    return out * np.minimum(1, t / 0.002) * vel * 0.22


def kick(vel=0.5):
    n = int(SR * 0.35)
    t = np.arange(n) / SR
    f = 48 + 70 * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.11) * vel * 0.5


def shaker(vel=0.3):
    n = int(SR * 0.09)
    t = np.arange(n) / SR
    x = np.diff(rng.normal(0, 1, n + 1))          # tilted toward highs
    return x * np.exp(-t / 0.025) * np.minimum(1, t / 0.008) * vel * 0.05


def swell(dur, vel=0.4):
    n = int(SR * dur)
    t = np.arange(n) / SR
    x = np.convolve(rng.normal(0, 1, n), np.ones(24) / 24, 'same')
    return x * (t / dur) ** 2.2 * vel * 0.25


def boom(vel=0.6):
    n = int(SR * 1.6)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * (36 + 20 * np.exp(-t / 0.08)) * t) * np.exp(-t / 0.45) * vel * 0.45


# ---------- harmony ----------
CH = {  # bass, upper voicing
    'D': (38, [62, 66, 69]), 'Dmaj9': (38, [57, 62, 64, 66, 69]), 'A/C#': (37, [61, 64, 69]),
    'Bm': (35, [62, 66, 71]), 'G': (43, [62, 67, 71]), 'Em7': (40, [62, 64, 67, 71]),
    'A': (45, [61, 64, 69]), 'D/F#': (42, [62, 66, 69]), 'Gmaj7': (43, [66, 67, 71, 74]),
    'A/G': (43, [61, 64, 69]), 'F#m7': (42, [64, 66, 69, 73]), 'Asus': (45, [62, 64, 69]),
    'Em': (40, [64, 67, 71]), 'A7': (45, [61, 64, 67]),
}
# (bar, beat, chord, beats)
PROG = [
    (1, 1, 'Dmaj9', 8),
    (3, 1, 'D', 4), (4, 1, 'A/C#', 4), (5, 1, 'Bm', 4), (6, 1, 'G', 4),
    (7, 1, 'Em7', 2), (7, 3, 'Asus', 1), (7, 4, 'A', 1), (8, 1, 'D', 4),
    (9, 1, 'G', 4), (10, 1, 'A', 4),
    (11, 1, 'D', 4), (12, 1, 'Bm', 2), (12, 3, 'G', 2),
    (13, 1, 'G', 4), (14, 1, 'A/G', 2), (14, 3, 'F#m7', 2),
    (15, 1, 'Gmaj7', 4), (16, 1, 'A', 2), (16, 3, 'D', 3),
]
if HYMN:
    PROG = [
        (1, 1, 'D', 6), (2, 3, 'A', 2),                      # The church's one foundation
        (3, 1, 'D', 2), (3, 3, 'G', 2), (4, 1, 'Em', 2), (4, 3, 'D', 2),   # Is Jesus Christ her Lord
        (5, 1, 'G', 4), (6, 1, 'A7', 2), (6, 3, 'D', 2),     # She is His new creation
        (7, 1, 'D', 2), (7, 3, 'Bm', 2), (8, 1, 'A', 2), (8, 3, 'D', 2),  # By water and the word
        (9, 1, 'D', 2), (9, 3, 'G', 2), (10, 1, 'D', 2), (10, 3, 'A', 2),  # From heav'n He came...
        (11, 1, 'G', 4), (12, 1, 'D', 2), (12, 3, 'A', 2),   # To be His holy bride
        (13, 1, 'D', 2), (13, 3, 'Bm', 2), (14, 1, 'A', 2), (14, 3, 'D', 2),  # With His own blood...
        (15, 1, 'G', 2), (15, 3, 'D/F#', 2), (16, 1, 'A', 2), (16, 3, 'D', 3),  # And for her life He died
    ]
if LOVE:
    line = [(1, 'D', 4), (2, 'D', 2), (2.5, 'Bm', 2), (3, 'A', 2), (3.5, 'G', 2)]   # O perfect Love...
    PROG = [(1, 1, 'Dmaj9', 8)]
    for start in (3, 9):                                    # lines 1 and 3 share their music
        PROG += [(start + int(o) - 1, 1 if o == int(o) else 3, c, b) for o, c, b in line]
    PROG += [
        (6, 1, 'Em', 2), (6, 3, 'A', 2), (7, 1, 'G', 2), (7, 3, 'D', 2), (8, 1, 'D/F#', 1), (8, 2, 'A', 3),
        (12, 1, 'Em', 2), (12, 3, 'A', 2), (13, 1, 'G', 2), (13, 3, 'A', 2), (14, 1, 'A', 1), (14, 2, 'D', 3),
        (15, 1, 'G', 2), (15, 3, 'A', 2), (16, 1, 'A', 2), (16, 3, 'D', 3),
    ]
for bar, beat, name, beats in PROG:
    b, up = CH[name]
    t0, d = at(bar, beat), beats * BEAT
    add('pad', t0, pad([b + 12] + up, d, 0.55 if bar < 3 else 0.7))
    if bar >= 3:
        add('piano', t0, piano(b, d, 0.42))
        if 13 <= bar <= 14:                       # the venue: half-time, open
            for i, m in enumerate([b + 12, up[0], up[-1], up[1]][: int(beats)]):
                add('piano', t0 + i * BEAT, piano(m, BEAT * 1.6, 0.22))
        elif bar in (9, 10, 11, 12, 15, 16):      # names, date, finale: pulse
            for i in range(int(beats)):
                if (beat + i) % 2 == 0:
                    for m in up:
                        add('piano', t0 + i * BEAT, piano(m, BEAT * 0.9, 0.16))
        else:                                     # building: eighth-note arpeggio
            pat = [b + 12, up[0], up[1], up[-1], up[1], up[0], up[1], up[-1]]
            for i in range(int(beats * 2)):
                add('piano', t0 + i * BEAT / 2, piano(pat[i % 8], BEAT * 0.7, 0.16))

# ---------- melody (bar: [(beat, midi, beats)]) ----------
MEL = {
    3: [(1, 74, 1.5), (2.5, 76, .5), (3, 78, 2)],
    4: [(1, 76, 1), (2, 74, 1), (3, 73, 1), (4, 74, 1)],
    5: [(1, 78, 1.5), (2.5, 76, .5), (3, 74, 1), (4, 71, 1)],
    6: [(1, 71, 2), (3, 74, 1), (4, 79, 1)],
    7: [(1, 78, 1.5), (2.5, 76, .5), (3, 76, 1), (4, 73, 1)],
    8: [(1, 74, 3)],
    9: [(1, 71, .5), (1.5, 74, .5), (2, 79, 1.5), (3.5, 78, .5), (4, 76, 1)],
    10: [(1, 76, 1.5), (2.5, 78, .5), (3, 81, 2)],
    11: [(1, 81, 1.5), (2.5, 78, .5), (3, 74, 1), (4, 78, 1)],
    12: [(1, 76, 1.5), (2.5, 74, .5), (3, 71, 1), (4, 74, 1)],
    13: [(1, 79, 2), (3, 78, 1), (4, 76, 1)],
    14: [(1, 76, 2), (3, 73, 1), (4, 76, 1)],
    15: [(1, 78, 1.5), (2.5, 79, .5), (3, 81, 2)],
    16: [(1, 79, 1), (2, 76, 1), (3, 78, 3)],
}
if HYMN:
    # AURELIA in D: 1=D4(62) 2=64 3=66 4=67 5=69 6=71 7=73 8=74
    q = lambda *ms: [(1 + i, m, 1) for i, m in enumerate(ms)]
    MEL = {
        1: q(66, 66, 66, 67), 2: [(1, 66, 1), (2, 66, 1), (3, 64, 2)],
        3: q(62, 62, 71, 69), 4: [(1, 67, 2), (3, 66, 2)],
        5: q(67, 69, 71, 69), 6: [(1, 69, 1), (2, 67, 1), (3, 66, 2)],
        7: q(66, 66, 64, 62), 8: [(1, 61, 2), (3, 62, 2)],
        9: q(69, 69, 69, 71), 10: [(1, 69, 1), (2, 74, 1), (3, 73, 2)],
        11: q(71, 71, 69, 67), 12: [(1, 66, 2), (3, 64, 2)],
        13: q(66, 67, 69, 74), 14: [(1, 73, 1), (2, 71, 1), (3, 69, 2)],
        15: q(71, 69, 67, 66), 16: [(1, 64, 2), (3, 62, 3)],
    }
if LOVE:
    # SANDRINGHAM in D: 7.=61 1=62 2=64 3=66 4=67 5=69 6=71 7=73 8=74
    q = lambda *ms: [(1 + i, m, 1) for i, m in enumerate(ms)]
    L1 = [q(62, 66, 69, 69), q(69, 69, 69, 74), [(1, 73, 1), (2, 73, 1), (3, 71, 2)]]
    MEL = {
        3: L1[0], 4: L1[1], 5: L1[2],                                   # O perfect Love, all human thought transcending
        6: q(64, 66, 67, 69), 7: q(71, 69, 67, 66), 8: [(1, 66, 1), (2, 64, 3)],   # Lowly we kneel in prayer before Thy throne
        9: L1[0], 10: L1[1], 11: L1[2],                                 # That theirs may be the love which knows no ending
        12: q(64, 66, 67, 69), 13: q(67, 66, 64, 62), 14: [(1, 61, 1), (2, 62, 3)],  # Whom Thou forevermore dost join in one
        15: q(67, 66, 64, 62), 16: [(1, 61, 2), (3, 62, 3)],            # coda: ...join in one
    }
for bar, notes in MEL.items():
    for beat, m, beats in notes:
        if HYMN and bar <= 2:                       # the opening line rings out on bells
            add('bell', at(bar, beat), bell(m + 12, 0.32, 1.6))
        else:
            add('piano', at(bar, beat), piano(m + (12 if HYMN or LOVE else 0), beats * BEAT, 0.5 if bar >= 15 and LOVE else 0.62))

# ---------- drums: names, date, finale ----------
for bar in (9, 10, 11, 12, 15, 16):
    for i in range(8):
        t = at(bar) + i * BEAT / 2
        if bar == 16 and i >= 4:
            break
        add('drum', t, shaker(0.5 if i % 2 else 0.3))
        if i in (0, 4):
            add('drum', t, kick(0.55))
add('drum', at(8, 3), kick(0.4))                  # pickup into the names

# ---------- cues locked to the picture ----------
for i, m in enumerate([] if HYMN else [74, 78, 81, 85, 81, 86]):   # seal pops in
    add('bell', 0.25 + i * 0.3, bell(m, 0.35))
add('fx', 3.5, swell(1.0, 0.5))                           # circle fills the frame
add('fx', 5.9, boom(0.7))                                 # cornerstone lands
add('piano', 5.9, piano(26, 2.0, 0.5))
rows = [[74, 76, 78, 81, 83], [78, 81, 83, 86, 88], [81, 83, 86, 88, 90]]
for i in range(15):                                       # each block lands
    add('bell', 11.4 + i * 0.3, bell(rows[i // 5][i % 5], 0.3, 1.0))
for m in (86, 90, 93):                                    # dome settles
    add('bell', 16.35, bell(m, 0.28, 2.0))
for i, m in enumerate([93, 95, 98, 95, 98, 102]):         # doves flutter in
    add('bell', 16.7 + i * 0.09, bell(m, 0.14, 0.6))
add('fx', 17.3, swell(0.9, 0.5))                          # navy wipe
add('fx', 23.2, swell(0.8, 0.5))                          # doors close...
add('fx', 24.0, boom(0.6))                                # ...on the bar line
for m in (74, 81, 86, 90):
    add('bell', 24.6, bell(m, 0.22, 2.2))                 # doors open
for i in range(9):                                        # digits roll
    add('bell', 25.0 + i * 0.15, bell([74, 78, 81, 86, 90, 93, 90, 86, 81][i], 0.16, 0.7))
for i in range(10):                                       # small house on the poster
    add('bell', 35.1 + i * 0.1, bell([86, 88, 90, 93, 95, 90, 93, 95, 98, 102][i], 0.12, 0.7))
for m in (86, 90, 93, 98):
    add('bell', 37.2, bell(m, 0.2, 2.5))                  # final chord


# ---------- mix ----------
def reverb(x, secs=2.2, wet=0.25):
    n = int(SR * secs)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, n) * np.exp(-t / (secs / 6.5))
    ir[0] = 0
    L = len(x) + n
    nfft = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
    y /= np.max(np.abs(y)) + 1e-9
    return x + wet * y * np.max(np.abs(x))


out = (reverb(mix['piano'], 2.0, 0.22) * 1.0 + reverb(mix['pad'], 3.0, 0.35) * 0.9 +
       reverb(mix['bell'], 2.6, 0.4) * 0.8 + mix['drum'] * 0.7 + reverb(mix['fx'], 2.0, 0.3) * 0.8)
out = out[: int(SR * DUR)]
t = np.arange(len(out)) / SR
out *= np.minimum(1, t / 0.05) * np.where(t > DUR - 1.4, np.clip((DUR - t) / 1.4, 0, 1) ** 1.5, 1)
out = np.tanh(out * 1.4) / np.tanh(1.4)                  # gentle soft clip
out *= 0.89 / np.max(np.abs(out))                         # peak about -1 dBFS

# slight stereo: piano a touch left, bells a touch right, via short delay on one side
d = int(SR * 0.012)
left = out
right = np.concatenate([np.zeros(d), out[:-d]]) * 0.9 + out * 0.1
pcm = (np.stack([left, right], 1) * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote', sys.argv[1], f'{len(out) / SR:.2f}s')
