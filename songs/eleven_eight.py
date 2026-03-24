"""eleven_eight.py — Math rock. Fm, 155 BPM, 11/8 time. Precision chaos.

Math rock is what happens when punk musicians learn music theory and
decide complexity IS the aesthetic. TTNG, Hella, toe, Tera Melos.
11/8 = 4+4+3 or 3+3+3+2 or any other ungodly grouping. The drums
have to work twice as hard. The guitar taps. The bass is melodic.
Nothing repeats where you expect it to.
"""

from code_music import (
    EIGHTH,
    QUARTER,
    Chord,
    Note,
    Song,
    Track,
    compress,
    crescendo,
    delay,
    distortion,
    humanize,
)

song = Song(title="Eleven Eight", bpm=155, time_sig=(11, 8), key_sig="F")

# 11/8: one bar = 11 eighth notes = 5.5 quarter beats
BAR = 5.5
E8 = EIGHTH
r = Note.rest

# ── Guitar — tapping pattern in 11/8 ──────────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_electric", volume=0.72, pan=-0.15))

# 11/8 grouped as 4+4+3: riff hits harder on the 3-group
tap_riff = humanize(
    [
        # Group of 4
        Note("F", 4, E8),
        Note("G#", 4, E8),
        Note("C", 5, E8),
        Note("G#", 4, E8),
        # Group of 4
        Note("D#", 4, E8),
        Note("F", 4, E8),
        Note("G#", 4, E8),
        Note("C", 5, E8),
        # Group of 3 (accent)
        Note("D#", 5, E8, velocity=0.9),
        Note("C", 5, E8),
        Note("G#", 4, E8),
    ],
    vel_spread=0.08,
    timing_spread=0.015,
)
gtr.extend(tap_riff * 8)

# Chorus: chords, still 11/8
chorus_gtr = crescendo(
    [
        Chord("F", "min", 3, duration=E8 * 4, velocity=0.75),
        Chord("D#", "maj", 3, duration=E8 * 4, velocity=0.73),
        Chord("C", "min", 3, duration=E8 * 3, velocity=0.78),
    ]
    * 4,
    0.6,
    0.95,
)
gtr.extend(chorus_gtr)

# Outro: slow down the tapping
gtr.extend(
    humanize(
        [
            Note("F", 4, QUARTER),
            Note("G#", 4, QUARTER),
            Note("C", 5, QUARTER),
            Note("D#", 5, QUARTER),
            Note("C", 5, E8),
            Note("G#", 4, E8),
            Note("F", 4, E8),
            Note("F", 4, BAR),
        ]
        * 2,
        vel_spread=0.07,
    )
)

# ── Bass — melodic, independent voice ─────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.8))
bass_line = humanize(
    [
        # 11/8: bass plays a different grouping (3+3+3+2)
        Note("F", 2, E8),
        Note("G#", 2, E8),
        Note("A#", 2, E8),
        Note("C", 3, E8),
        Note("D#", 3, E8),
        Note("C", 3, E8),
        Note("A#", 2, E8),
        Note("G#", 2, E8),
        Note("F", 2, E8),
        Note("D#", 2, E8),
        Note("F", 2, E8),
    ],
    vel_spread=0.07,
    timing_spread=0.02,
)
bass.extend(bass_line * 12)
bass.extend([Note("F", 2, BAR * 2)])

# ── Drums — the hardest part of math rock ─────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.92))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.82))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.42))

# 11/8 kit: kick on 1, 5, 9; snare on 3, 7, 10
for _ in range(12):
    kick.extend(
        [
            Note("C", 2, E8),
            r(E8 * 3),
            Note("C", 2, E8),
            r(E8 * 3),
            Note("C", 2, E8),
            r(E8),
            r(E8),
        ]
    )
    snare.extend(
        [
            r(E8 * 2),
            Note("D", 3, E8),
            r(E8 * 3),
            Note("D", 3, E8),
            r(E8 * 2),
            Note("D", 3, E8),
            r(E8),
        ]
    )
    hat.extend([Note("F", 5, E8)] * 11)

# Outro: half-time feel
for _ in range(2):
    kick.extend([Note("C", 2, E8 * 4), r(E8 * 3), Note("C", 2, E8 * 4)])
    snare.extend([r(E8 * 4), Note("D", 3, E8 * 3), r(E8 * 4)])
    hat.extend([Note("F", 5, E8)] * 11)

song._effects = {
    "guitar": lambda s, sr: distortion(
        delay(s, sr, delay_ms=96.0, feedback=0.15, wet=0.08),
        drive=1.6,
        tone=0.6,
        wet=0.3,
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.15),
}
