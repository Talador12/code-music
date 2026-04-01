"""neon_cathedral.py — Cinematic / hybrid orchestral. Dbm, 88 BPM.

Full strings + taiko + choir + pad. That Hans Zimmer + electronic
hybrid sound that dominates film trailers. Dbm is an unusual key —
it's enharmonically C#m, which sits in a slightly alien harmonic
space. The flatted key signature makes even familiar movements
feel slightly off-center, which is exactly what thriller/sci-fi
scoring wants.
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    conv_reverb,
    crescendo,
    decrescendo,
    humanize,
    lowpass,
    stereo_width,
)

song = Song(title="Neon Cathedral", bpm=88, key_sig="C#")

BAR = 4.0
r = Note.rest

# ── Sub drone ─────────────────────────────────────────────────────────────
sub = song.add_track(Track(name="sub", instrument="sub_bass", volume=0.65))
for _ in range(24):
    sub.add(Note("C#", 1, BAR, velocity=0.6))

# ── String ostinato ───────────────────────────────────────────────────────
ostinato = song.add_track(Track(name="strings", instrument="violin", volume=0.58, pan=-0.25))
pattern = humanize(
    crescendo(
        [Note("C#", 5, 0.25)] * 4
        + [Note("E", 5, 0.25)] * 4
        + [Note("G#", 5, 0.25)] * 4
        + [Note("B", 5, 0.25)] * 4,
        start_vel=0.2,
        end_vel=0.85,
    ),
    vel_spread=0.06,
)
ostinato.extend(pattern)
ostinato.extend(crescendo(pattern, 0.85, 1.0))
ostinato.extend(decrescendo(pattern[: len(pattern) // 2], 0.85, 0.2))

# ── Cellos — sustained bass movement ──────────────────────────────────────
cello = song.add_track(Track(name="cello", instrument="cello", volume=0.68, pan=0.25))
cello.extend(
    crescendo(
        [
            Note("C#", 3, BAR * 2),
            Note("B", 2, BAR * 2),
            Note("A", 2, BAR * 2),
            Note("G#", 2, BAR * 2),
            Note("F#", 2, BAR * 2),
            Note("E", 2, BAR * 2),
            Note("C#", 2, BAR * 4),
        ],
        0.25,
        0.88,
    )
)

# ── Taiko — sparse hits ───────────────────────────────────────────────────
taiko = song.add_track(Track(name="taiko", instrument="taiko", volume=0.95))
taiko_hits = crescendo(
    [
        Note("C#", 2, 1.0, velocity=0.6),
        r(3.0),
        r(BAR),
        Note("C#", 2, 0.5, velocity=0.75),
        r(1.0),
        Note("C#", 2, 0.5, velocity=0.85),
        r(2.0),
        r(BAR * 2),
        Note("C#", 2, 0.5, velocity=0.9),
        Note("C#", 2, 0.25, velocity=0.85),
        Note("C#", 2, 0.25, velocity=0.95),
        r(BAR - 1.0),
        r(BAR * 2),
        Note("C#", 2, 2.0, velocity=1.0),
        r(2.0),
        r(BAR),
    ],
    0.4,
    1.0,
)
taiko.extend(taiko_hits)

# ── Choir swell ───────────────────────────────────────────────────────────
choir = song.add_track(Track(name="choir", instrument="choir_aah", volume=0.52, pan=0.0))
choir.extend([r(BAR)] * 8)
choir.extend(
    crescendo(
        [
            Chord("C#", "min", 3, duration=BAR * 2, velocity=0.3),
            Chord("A", "maj", 3, duration=BAR * 2, velocity=0.35),
            Chord("E", "maj", 3, duration=BAR * 2, velocity=0.42),
            Chord("B", "dom7", 3, duration=BAR * 2, velocity=0.5),
            Chord("C#", "min", 3, duration=BAR * 4, velocity=0.6),
        ],
        0.2,
        0.9,
    )
)

# ── Brass hits — climax ───────────────────────────────────────────────────
brass = song.add_track(Track(name="brass", instrument="brass_section", volume=0.78, pan=0.0))
brass.extend([r(BAR)] * 16)
brass.extend(
    crescendo(
        [
            Note("C#", 4, BAR, velocity=0.7),
            Note("E", 4, BAR, velocity=0.78),
            Note("G#", 4, BAR * 2, velocity=0.88),
            Note("A", 4, BAR, velocity=0.85),
            Note("G#", 4, BAR, velocity=0.82),
            Note("E", 4, BAR * 4, velocity=0.95),
        ],
        0.5,
        1.0,
    )
)

song.effects = {
    "sub": lambda s, sr: lowpass(s, sr, cutoff_hz=90.0),
    "strings": lambda s, sr: conv_reverb(s, sr, room="hall", wet=0.35),
    "cello": lambda s, sr: conv_reverb(s, sr, room="hall", wet=0.32),
    "taiko": lambda s, sr: conv_reverb(s, sr, room="cave", wet=0.4),
    "choir": lambda s, sr: stereo_width(conv_reverb(s, sr, room="hall", wet=0.5), width=1.8),
    "brass": lambda s, sr: conv_reverb(s, sr, room="hall", wet=0.28),
}
