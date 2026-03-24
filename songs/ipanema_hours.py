"""ipanema_hours.py — Bossa nova / Latin jazz. Fm, 120 BPM. Guitar + bass + brushes.

Bossa nova is samba rhythm squeezed through cool jazz harmony. João Gilberto
played rhythm guitar with his thumb doing the bass and fingers doing the chord —
all one instrument. Here that's split across two tracks. The jazz chord
voicings (9ths, maj7s) are the key — bossa is never just triads.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Chord,
    Note,
    Song,
    Track,
    chorus,
    humanize,
    reverb,
)

song = Song(title="Ipanema Hours", bpm=120)

BAR = 4.0
SWING = 0.42  # gentle bossa swing, lighter than jazz
r = Note.rest

# ── Bossa nova rhythm guitar — the thumb-finger split ────────────────────
comp = song.add_track(
    Track(name="comp", instrument="guitar_acoustic", volume=0.68, pan=-0.2, swing=SWING)
)


# Classic bossa pattern: bass note on 1, chord on 2-and, chord on 3-and, etc.
def bossa_bar(bass_note, bass_oct, chord_root, chord_shape):
    return [
        Note(bass_note, bass_oct, QUARTER, velocity=0.72),  # thumb: bass
        Chord(chord_root, chord_shape, 3, duration=EIGHTH, velocity=0.58),
        r(EIGHTH),
        Chord(chord_root, chord_shape, 3, duration=EIGHTH, velocity=0.55),
        r(EIGHTH),
        Chord(chord_root, chord_shape, 3, duration=EIGHTH, velocity=0.6),
        r(EIGHTH),
        Chord(chord_root, chord_shape, 3, duration=EIGHTH, velocity=0.55),
        r(EIGHTH),
    ]


# Progression: Fm9 - Db maj7 - Gm7b5 - C7alt  (minor ii-V-i variants)
prog_bars = [
    bossa_bar("F", 2, "F", "min9"),
    bossa_bar("C#", 2, "C#", "maj7"),
    bossa_bar("G", 2, "G", "min7"),
    bossa_bar("C", 2, "C", "dom7"),
]
for _ in range(8):
    for bar in prog_bars:
        comp.extend(bar)

# ── Walking bass ──────────────────────────────────────────────────────────
bass = song.add_track(
    Track(name="bass", instrument="contrabass", volume=0.75, pan=0.1, swing=SWING)
)
walk = [
    Note("F", 2, 1.0),
    Note("G", 2, 1.0),
    Note("G#", 2, 1.0),
    Note("A#", 2, 1.0),
    Note("C#", 2, 1.0),
    Note("D#", 2, 1.0),
    Note("F", 2, 1.0),
    Note("G#", 2, 1.0),
    Note("G", 2, 1.0),
    Note("A", 2, 1.0),
    Note("A#", 2, 1.0),
    Note("D", 3, 1.0),
    Note("C", 2, 1.0),
    Note("D", 2, 1.0),
    Note("E", 2, 1.0),
    Note("G", 2, 1.0),
]
for _ in range(8):
    bass.extend(walk)

# ── Brushed drums — very light ─────────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.28, swing=SWING))
snare = song.add_track(Track(name="brush", instrument="drums_snare", volume=0.32, swing=SWING))
for _ in range(32):
    hat.extend([Note("F", 5, EIGHTH, velocity=0.3)] * 8)
    snare.extend(
        [r(1.0), Note("D", 3, 1.0, velocity=0.28), r(1.0), Note("D", 3, 1.0, velocity=0.25)]
    )

# ── Vibraphone melody — enters at bar 9 ──────────────────────────────────
vib = song.add_track(
    Track(name="vibes", instrument="vibraphone", volume=0.6, pan=0.25, swing=SWING)
)
vib.extend([r(BAR)] * 8)

melody = humanize(
    [
        Note("F", 5, QUARTER),
        r(EIGHTH),
        Note("G#", 5, EIGHTH),
        Note("A#", 5, HALF),
        Note("G", 5, QUARTER),
        r(EIGHTH),
        Note("F", 5, EIGHTH),
        Note("D#", 5, HALF),
        r(QUARTER),
        Note("C", 5, EIGHTH),
        Note("D", 5, EIGHTH),
        Note("D#", 5, QUARTER),
        Note("F", 5, QUARTER),
        Note("F", 5, HALF),
        r(HALF),
        r(QUARTER),
        Note("D#", 5, EIGHTH),
        Note("F", 5, EIGHTH),
        Note("G", 5, QUARTER),
        Note("A#", 5, QUARTER),
        Note("A", 5, QUARTER),
        Note("G", 5, QUARTER),
        Note("F", 5, WHOLE := 4.0),
    ],
    vel_spread=0.07,
    timing_spread=0.04,
)
for _ in range(4):
    vib.extend(melody)

song._effects = {
    "comp": lambda s, sr: reverb(s, sr, room_size=0.45, wet=0.15),
    "vibes": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.6, wet=0.28), sr, rate_hz=0.35, wet=0.18
    ),
    "bass": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.1),
}
