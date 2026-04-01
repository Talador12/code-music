"""the_arc.py — Prog rock. Em, 124 BPM, 5/4 time. Third Teeth album track.

5/4 is what happens when prog rock musicians refuse to resolve the bar.
Dave Brubeck's Take Five, Pink Floyd's Money, Tool's Schism (7/8).
5/4 feels like a sentence that ends one word too late. You're always
slightly off-balance. The bass line has to work harder. The melody
never quite lands where you expect. That's the point.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Chord,
    Note,
    Song,
    Track,
    compress,
    crescendo,
    decrescendo,
    distortion,
    humanize,
    reverb,
)

song = Song(title="The Arc", bpm=124, time_sig=(5, 4))

# 5/4: one bar = 5 quarter notes = 5.0 beats
BAR = 5.0
E8 = EIGHTH
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Main riff — guitar in Em ───────────────────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_electric", volume=0.75, pan=-0.15))

# 5/4 riff: 2+3 or 3+2 grouping
riff_a = [
    Note("E", 3, EIGHTH),
    Note("G", 3, EIGHTH),  # group 2
    Note("E", 3, EIGHTH),
    Note("B", 3, EIGHTH),
    Note("A", 3, EIGHTH),
    Note("G", 3, QUARTER),  # group 3
    Note("E", 3, HALF),
]
riff_b = [
    Note("D", 3, EIGHTH),
    Note("F#", 3, EIGHTH),
    Note("A", 3, EIGHTH),  # group 3
    Note("G", 3, EIGHTH),
    Note("E", 3, QUARTER),  # group 2
    Note("D", 3, HALF),
]

gtr.extend(humanize(riff_a * 4, vel_spread=0.08))
gtr.extend(humanize(riff_b * 4, vel_spread=0.08))

# Chorus: chords
chorus_gtr = crescendo(
    [
        Chord("E", "min", 3, duration=HALF, velocity=0.78),
        Chord("C", "maj", 3, duration=HALF, velocity=0.75),
        Note("D", 3, QUARTER, velocity=0.72),
        Chord("G", "maj", 3, duration=HALF, velocity=0.80),
        Chord("D", "maj", 3, duration=HALF, velocity=0.78),
        Note("A", 2, QUARTER, velocity=0.75),
    ],
    0.6,
    0.95,
)
gtr.extend(chorus_gtr)
gtr.extend(chorus_gtr)

# Bridge: slower, more spacious
bridge = humanize(
    decrescendo(
        [
            Note("E", 4, HALF),
            Note("D", 4, QUARTER),
            r(QUARTER + EIGHTH),
            Note("C", 4, EIGHTH),
            Note("B", 3, HALF),
            Note("A", 3, HALF),
            r(QUARTER),
            Note("G", 3, HALF + QUARTER),
            Note("F#", 3, QUARTER),
            r(HALF),
            Note("E", 3, BAR),
        ],
        0.85,
        0.35,
    ),
    vel_spread=0.06,
    timing_spread=0.04,
)
gtr.extend(bridge)
gtr.extend(humanize(riff_a * 2, vel_spread=0.07))

# ── Organ — 5/4 comping ────────────────────────────────────────────────────
org = song.add_track(Track(name="organ", instrument="organ", volume=0.42, pan=0.2))
org.extend(bars(8))
comp = [
    Chord("E", "min7", 3, duration=HALF, velocity=0.55),
    Chord("C", "maj7", 3, duration=HALF, velocity=0.52),
    Note.rest(QUARTER),
] * 4
org.extend(comp)
org.extend(
    crescendo(
        [
            Chord("E", "min", 3, duration=HALF, velocity=0.65),
            Chord("C", "maj", 3, duration=HALF, velocity=0.62),
            Note.rest(QUARTER),
        ]
        * 4,
        0.45,
        0.82,
    )
)
org.extend(bars(4))
org.extend(bars(2))

# ── Bass — 5/4 walking ────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.78, pan=0.05))
bass_5 = humanize(
    [
        Note("E", 2, EIGHTH),
        Note("F#", 2, EIGHTH),
        Note("G", 2, EIGHTH),
        Note("A", 2, EIGHTH),
        Note("B", 2, QUARTER),
        Note("C", 3, EIGHTH),
        Note("B", 2, EIGHTH),
        Note("A", 2, QUARTER),
        Note("G", 2, HALF + QUARTER),
        Note("D", 2, EIGHTH),
        Note("E", 2, EIGHTH),
        Note("F#", 2, EIGHTH),
        Note("G", 2, EIGHTH),
        Note("A", 2, QUARTER),
        Note("B", 2, HALF + QUARTER),
    ]
    * 3,
    vel_spread=0.07,
    timing_spread=0.02,
)
bass.extend(bass_5)
bass.extend(bars(8))

# ── Drums — 5/4 kit ────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.92))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.80))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.40))

# 5/4 pattern: kick on 1, snare on 3, hat all 8ths = 10 per bar
drum_bar_kick = [Note("C", 2, EIGHTH), r(E8), r(E8 * 2), r(E8), r(E8), r(E8), r(E8), r(E8), r(E8)]
drum_bar_snare = [r(E8 * 4), Note("D", 3, EIGHTH), r(E8), r(E8), r(E8), r(E8), r(E8)]
drum_bar_hat = [Note("F", 5, EIGHTH)] * 10

for _ in range(15):
    kick.extend(drum_bar_kick)
    snare.extend(drum_bar_snare)
    hat.extend(drum_bar_hat)

kick.extend(bars(5))
snare.extend(bars(5))
hat.extend(bars(5))

song.effects = {
    "guitar": lambda s, sr: distortion(
        reverb(s, sr, room_size=0.35, wet=0.12),
        drive=1.8,
        tone=0.55,
        wet=0.35,
    ),
    "organ": lambda s, sr: reverb(s, sr, room_size=0.55, wet=0.2),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
