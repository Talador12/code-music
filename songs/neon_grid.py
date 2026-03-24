"""neon_grid.py — Cosmic electro / disco. 124 BPM, Gb major. Second Neon Lollipop track.

That Mord Fustang euphoria again but different key and shape.
Gb major is the brightest, most open-sounding flat key.
Faster arp pattern (outside_in), funkier bass, choir pad enters at peak.
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    arp,
    chorus,
    compress,
    delay,
    reverb,
    stereo_width,
)

song = Song(title="Neon Grid", bpm=124)

BAR = 4.0
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# Gb major: Gbmaj7 - Ebm7 - Cbmaj7 - Db (bright, cosmic)
ROOTS = ["F#", "D#", "C#", "C#"]
SHAPES = ["maj7", "min7", "maj7", "dom7"]

# ── Kick + clap ───────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend(bars(4))
kick.extend([Note("C", 2, 1.0)] * (28 * 4))

clap = song.add_track(Track(name="clap", instrument="drums_clap", volume=0.78))
clap.extend(bars(4))
clap.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 28)

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.42))
hat.extend(bars(4))
hat.extend([r(0.5), Note("F", 5, 0.5)] * (28 * 4))

# ── Funky bass — Motown-disco feel ────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="moog_bass", volume=0.82))
bass.extend(bars(4))
bass_patterns = {
    "F#": [
        Note("F#", 2, 1.0, 0.88),
        Note("F#", 2, 0.5, 0.75),
        r(0.5),
        Note("F#", 3, 0.5, 0.7),
        r(0.5),
        Note("F#", 2, 0.5, 0.78),
        r(0.5),
    ],
    "D#": [
        Note("D#", 2, 1.0, 0.85),
        Note("D#", 2, 0.5, 0.72),
        r(0.5),
        Note("D#", 3, 0.5, 0.68),
        r(0.5),
        Note("D#", 2, 0.5, 0.75),
        r(0.5),
    ],
    "C#": [
        Note("C#", 2, 1.0, 0.88),
        Note("C#", 2, 0.5, 0.75),
        r(0.5),
        Note("C#", 3, 0.5, 0.7),
        r(0.5),
        Note("C#", 2, 0.5, 0.78),
        r(0.5),
    ],
}
for _ in range(7):
    for p in ["F#", "D#", "C#", "C#"]:
        bass.extend(bass_patterns[p])

# ── Pad — lush, wide ──────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=0.0))
for _ in range(8):
    for r_note, sh in zip(ROOTS, SHAPES):
        pad.add(Chord(r_note, sh, 3, duration=BAR, velocity=0.55))

# ── Laser arp — outside_in pattern, very cosmic ───────────────────────────
arp_tr = song.add_track(Track(name="laser", instrument="hoover", volume=0.52))
arp_tr.extend(bars(4))
for _ in range(7):
    for r_note, sh in zip(ROOTS, SHAPES):
        arp_tr.extend(arp(Chord(r_note, sh, 4), pattern="outside_in", rate=0.25, octaves=2))

# ── Choir — enters at bar 17, the euphoric peak ───────────────────────────
choir = song.add_track(Track(name="choir", instrument="choir_ooh", volume=0.38, pan=0.0))
choir.extend(bars(16))
for _ in range(3):
    for r_note, sh in zip(ROOTS, SHAPES):
        choir.add(Chord(r_note, sh, 3, duration=BAR, velocity=0.5))

# ── Lead melody — enters bar 13 ───────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="pluck", volume=0.6, pan=0.15))
lead.extend(bars(12))
lead_mel = [
    Note("F#", 5, 0.5),
    Note("G#", 5, 0.5),
    Note("A#", 5, 1.0),
    Note("C#", 6, 0.5),
    Note("A#", 5, 0.5),
    Note("G#", 5, 1.0),
    Note("F#", 5, 0.5),
    Note("G#", 5, 0.25),
    Note("A#", 5, 0.25),
    Note("C#", 6, 1.0),
    Note("F#", 5, 1.0),
    r(1.0),
    Note("D#", 5, 0.5),
    Note("F#", 5, 0.5),
    Note("G#", 5, 1.0),
    Note("A#", 5, 0.5),
    Note("G#", 5, 0.5),
    Note("F#", 5, 2.0),
]
lead.extend(lead_mel * 4)

song._effects = {
    "laser": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.5, wet=0.2), sr, rate_hz=1.0, depth_ms=2.5, wet=0.42
    ),
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.7, wet=0.3), width=1.8),
    "choir": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.45),
    "lead": lambda s, sr: delay(s, sr, delay_ms=484.0, feedback=0.3, wet=0.2, ping_pong=True),
    "bass": lambda s, sr: compress(s, sr, threshold=0.55, ratio=3.0, makeup_gain=1.1),
}
