"""fusion_flight.py — Jazz fusion. Fmaj7, 148 BPM. Electric, complex, fast.

Jazz fusion is when jazz musicians discovered rock electricity and
the result was mutual contamination of the best possible kind. Herbie
Hancock, Weather Report, Mahavishnu Orchestra, Return to Forever.
Complex time, fast lines, Rhodes + electric bass + heavy kit.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    SIXTEENTH,
    Chord,
    Note,
    Song,
    Track,
    chorus,
    compress,
    crescendo,
    delay,
    humanize,
    reverb,
)

song = Song(title="Fusion Flight", bpm=148)

BAR = 4.0
SWING = 0.45
r = Note.rest

# ── Electric bass — busy, melodic ────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.85, swing=SWING))
bass_line = humanize(
    [
        Note("F", 2, EIGHTH),
        Note("G", 2, EIGHTH),
        Note("A", 2, EIGHTH),
        Note("C", 3, EIGHTH),
        Note("A#", 2, QUARTER),
        Note("A", 2, EIGHTH),
        Note("G", 2, EIGHTH),
        Note("F", 2, EIGHTH),
        Note("A", 2, EIGHTH),
        Note("C", 3, EIGHTH),
        Note("F", 3, EIGHTH),
        Note("E", 3, QUARTER),
        Note("D", 3, EIGHTH),
        Note("C", 3, EIGHTH),
        Note("G", 2, EIGHTH),
        Note("A", 2, EIGHTH),
        Note("A#", 2, EIGHTH),
        Note("C", 3, EIGHTH),
        Note("D", 3, HALF),
    ],
    vel_spread=0.07,
    timing_spread=0.02,
)
bass.extend(bass_line * 4)

# ── Rhodes — jazz fusion comping ──────────────────────────────────────────
comp = song.add_track(Track(name="comp", instrument="rhodes", volume=0.62, swing=SWING, pan=-0.2))
comp_loop = [
    Chord("F", "maj7", 3, duration=QUARTER, velocity=0.7),
    r(QUARTER),
    Chord("E", "min7", 3, duration=EIGHTH, velocity=0.65),
    r(EIGHTH),
    Chord("D", "min7", 3, duration=QUARTER, velocity=0.68),
    r(QUARTER),
    Chord("G", "dom7", 3, duration=HALF, velocity=0.72),
    Chord("C", "maj7", 3, duration=QUARTER, velocity=0.68),
    r(QUARTER),
    Chord("A", "min7", 3, duration=EIGHTH, velocity=0.65),
    r(EIGHTH),
    Chord("D", "min7", 3, duration=QUARTER, velocity=0.7),
    r(QUARTER),
    Chord("G", "dom7", 3, duration=HALF, velocity=0.72),
]
comp.extend(comp_loop * 4)

# ── Kit — fusion drums: complex, fills everywhere ─────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.9))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.78))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.42, swing=SWING))
ride = song.add_track(Track(name="ride", instrument="drums_ride", volume=0.48, swing=SWING))

# Syncopated fusion pattern
for _ in range(16):
    kick.extend(
        [
            Note("C", 2, EIGHTH),
            r(EIGHTH),
            r(QUARTER),
            Note("C", 2, EIGHTH),
            r(EIGHTH),
            Note("C", 2, EIGHTH),
            r(EIGHTH),
        ]
    )
    snare.extend(
        [r(QUARTER), Note("D", 3, EIGHTH), r(EIGHTH), r(QUARTER), Note("D", 3, EIGHTH), r(EIGHTH)]
    )
    hat.extend([Note("F", 5, EIGHTH)] * 8)
    ride.extend(
        [Note("F", 5, EIGHTH), Note("F", 5, SIXTEENTH), Note("F", 5, SIXTEENTH)] * 3
        + [Note("F", 5, EIGHTH), r(EIGHTH)]
    )

# ── Lead synth — fast pentatonic runs ────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="lead_edm", volume=0.58, swing=SWING, pan=0.2))
lead.extend([r(BAR)] * 4)
run_up = humanize(
    crescendo(
        [
            Note("F", 5, SIXTEENTH),
            Note("G", 5, SIXTEENTH),
            Note("A", 5, SIXTEENTH),
            Note("C", 6, SIXTEENTH),
            Note("D", 6, SIXTEENTH),
            Note("F", 6, SIXTEENTH),
            Note("D", 6, EIGHTH),
            Note("C", 6, EIGHTH),
            Note("A", 5, EIGHTH),
            Note("G", 5, EIGHTH),
            Note("F", 5, QUARTER),
            r(QUARTER),
            Note("A", 5, SIXTEENTH),
            Note("C", 6, SIXTEENTH),
            Note("D", 6, SIXTEENTH),
            Note("F", 6, SIXTEENTH),
            Note("A", 6, SIXTEENTH),
            Note("G", 6, SIXTEENTH),
            Note("F", 6, EIGHTH),
            Note("E", 6, EIGHTH),
            Note("D", 6, QUARTER),
            Note("C", 6, QUARTER),
            r(HALF),
        ],
        0.55,
        0.92,
    ),
    vel_spread=0.07,
    timing_spread=0.015,
)
lead.extend(run_up * 3)

song.effects = {
    "comp": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.38, wet=0.12), sr, rate_hz=0.5, wet=0.15
    ),
    "lead": lambda s, sr: delay(s, sr, delay_ms=202.0, feedback=0.25, wet=0.15),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.15),
}
