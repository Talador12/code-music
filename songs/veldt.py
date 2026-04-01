"""veldt.py — Progressive house. 128 BPM, Dm. Slow build, massive patience.

Named after the Ray Bradbury story — technology that consumes you slowly,
so gradually you don't notice until it's done. The filter opens over
8 full minutes of loop. The drop is the filter, not new elements.
Second progressive house track for Machine Dreams album.
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    arp,
    chord_prog,
    compress,
    delay,
    lfo_filter,
    reverb,
    stereo_width,
)

song = Song(title="Veldt", bpm=128)

BAR = 4.0
r = Note.rest

TOTAL_BARS = 64  # 8 minutes at 128 BPM


def bars(n):
    return [r(BAR)] * n


# Chord loop: Dm - Bb - F - C (minor feel, familiar)
PROG = chord_prog(
    ["D", "A#", "F", "C"], ["min7", "maj7", "maj7", "dom7"], octave=3, duration=BAR * 2
)

# ── Kick — enters bar 9, never stops after ────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend(bars(8))
kick.extend([Note("C", 2, 1.0)] * (56 * 4))

# ── Hat — enters bar 17 ───────────────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.38))
hat.extend(bars(16))
hat.extend([r(0.5), Note("F", 5, 0.5)] * (48 * 4))

# ── Snare — enters bar 25 ─────────────────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.62))
snare.extend(bars(24))
snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * (40))

# ── Supersaw pad — filter slowly opens (the whole point) ─────────────────
pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.5))
for _ in range(TOTAL_BARS // 8):
    pad.extend(PROG)

# ── Bass — root only, enters bar 9 ───────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.65))
bass.extend(bars(8))
bass_roots = [("D", 2), ("A#", 1), ("F", 2), ("C", 2)]
for _ in range(7):
    for p, o in bass_roots:
        bass.extend([Note(p, o, BAR * 2, velocity=0.7)])

# ── Pluck arp — enters bar 33, very quiet, grows ─────────────────────────
arp_tr = song.add_track(Track(name="arp", instrument="pluck", volume=0.32, pan=0.2))
arp_tr.extend(bars(32))
for bar_i in range(32):
    vol = 0.15 + bar_i * (0.55 / 32)
    ch_i = (bar_i // 2) % 4
    p, shape = [("D", "min7"), ("A#", "maj7"), ("F", "maj7"), ("C", "dom7")][ch_i]
    for n in arp(Chord(p, shape, 4), pattern="up", rate=0.25, octaves=2):
        arp_tr.add(Note(n.pitch, duration=0.25, velocity=vol))

# ── Lead — enters at bar 49, the emotional payoff ────────────────────────
lead = song.add_track(Track(name="lead", instrument="lead_edm", volume=0.58, pan=-0.1))
lead.extend(bars(48))
lead_mel = [
    Note("D", 5, 0.5),
    Note("F", 5, 0.5),
    Note("A", 5, 1.0),
    Note("C", 6, 0.5),
    Note("A", 5, 0.5),
    Note("F", 5, 1.0),
    Note("D", 5, 0.5),
    Note("F", 5, 0.25),
    Note("A", 5, 0.25),
    Note("C", 6, 1.0),
    Note("D", 5, 1.0),
    r(1.0),
    Note("A#", 4, 0.5),
    Note("D", 5, 0.5),
    Note("F", 5, 1.0),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F", 5, 2.0),
]
lead.extend(lead_mel * 4)

song.effects = {
    "pad": lambda s, sr: stereo_width(
        lfo_filter(
            reverb(s, sr, room_size=0.55, wet=0.18),
            sr,
            rate_hz=0.004,
            min_cutoff=150.0,
            max_cutoff=9000.0,
        ),
        width=1.75,
    ),
    "lead": lambda s, sr: delay(s, sr, delay_ms=234.0, feedback=0.38, wet=0.22, ping_pong=True),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
    "arp": lambda s, sr: reverb(s, sr, room_size=0.45, wet=0.18),
}
