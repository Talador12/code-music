"""wrong_side_of_the_scale.py — World / Experimental. Arabic double harmonic, Am, 96 BPM.

The Arabic double harmonic scale has two augmented seconds (b2 and b6).
Those intervals don't exist in Western diatonic music — they feel exotic,
tense, ancient. This track uses koto_ks (Karplus-Strong koto) for the
melody, a contrabass drone, and hand drums. Sparse. Let the scale do the work.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    Note,
    Song,
    Track,
    crescendo,
    decrescendo,
    delay,
    humanize,
    lowpass,
    reverb,
    scale,
)

song = Song(title="Wrong Side of the Scale", bpm=96)

BAR = 4.0
r = Note.rest

# ── Drone — contrabass, A, very sustained ────────────────────────────────
drone = song.add_track(Track(name="drone", instrument="contrabass", volume=0.55))
for _ in range(16):
    drone.add(Note("A", 1, BAR, velocity=0.55))

# ── Hand drum — tabla, sparse ─────────────────────────────────────────────
tabla = song.add_track(Track(name="tabla", instrument="tabla", volume=0.72))
tabla_pat = [
    Note("A", 4, EIGHTH, velocity=0.85),
    r(EIGHTH),
    Note("A", 4, EIGHTH, velocity=0.65),
    r(EIGHTH),
    r(EIGHTH),
    Note("A", 4, EIGHTH, velocity=0.78),
    Note("A", 4, EIGHTH, velocity=0.7),
    Note("A", 4, EIGHTH, velocity=0.6),
]
for _ in range(16):
    tabla.extend(humanize(tabla_pat, vel_spread=0.12))

# ── Koto — Arabic double harmonic melody ──────────────────────────────────
# A Arabic / Double Harmonic: A Bb C# D E F G#
koto = song.add_track(Track(name="koto", instrument="koto_ks", volume=0.78, pan=-0.15))

arab_scale = scale("A", "arabic", octave=4)  # A Bb C# D E F G#

# Opening: scale exploration, very sparse
opening = humanize(
    [
        Note("A", 4, HALF),
        r(HALF),
        Note("A#", 4, QUARTER),
        Note("C#", 5, QUARTER),
        r(HALF),
        Note("D", 5, HALF),
        r(HALF),
        Note("E", 5, QUARTER),
        Note("F", 5, QUARTER),
        r(HALF),
        Note("G#", 5, HALF),
        r(QUARTER),
        Note("A", 5, QUARTER),
        Note("A", 5, WHOLE := 4.0),
        r(BAR),
    ],
    vel_spread=0.09,
    timing_spread=0.05,
)
koto.extend(opening)

# Main melody — uses those augmented 2nds deliberately
main = humanize(
    crescendo(
        [
            Note("A", 4, DOTTED_QUARTER),
            Note("A#", 4, EIGHTH),  # half-step
            Note("C#", 5, HALF),  # aug 2nd jump
            Note("D", 5, QUARTER),
            Note("E", 5, QUARTER),
            Note("F", 5, HALF),
            Note("G#", 5, QUARTER),
            Note("A", 5, QUARTER),  # aug 2nd up
            Note("A", 5, HALF),
            r(HALF),
            Note("G#", 5, QUARTER),
            Note("F", 5, QUARTER),  # back down
            Note("E", 5, HALF),
            Note("D", 5, QUARTER),
            Note("C#", 5, QUARTER),
            Note("A#", 4, HALF),  # aug 2nd down
            Note("A", 4, WHOLE),
        ],
        start_vel=0.45,
        end_vel=0.88,
    ),
    vel_spread=0.06,
    timing_spread=0.04,
)
for _ in range(3):
    koto.extend(main)

# Outro: fade
koto.extend(decrescendo(humanize(opening[:8], vel_spread=0.08), start_vel=0.7, end_vel=0.1))

# ── Second voice — sitar, higher ──────────────────────────────────────────
sitar = song.add_track(Track(name="sitar", instrument="sitar_ks", volume=0.42, pan=0.3))
sitar.extend([r(BAR)] * 6)
sitar.extend(
    humanize(
        [
            Note("A", 5, HALF),
            r(HALF),
            Note("C#", 6, QUARTER),
            Note("A#", 5, QUARTER),
            r(HALF),
            Note("E", 5, DOTTED_QUARTER),
            Note("F", 5, EIGHTH),
            r(HALF),
            Note("A", 5, WHOLE),
            r(BAR),
        ]
        * 2,
        vel_spread=0.1,
        timing_spread=0.05,
    )
)

song.effects = {
    "drone": lambda s, sr: lowpass(reverb(s, sr, room_size=0.85, wet=0.4), sr, cutoff_hz=200.0),
    "koto": lambda s, sr: reverb(s, sr, room_size=0.65, damping=0.45, wet=0.22),
    "sitar": lambda s, sr: delay(
        reverb(s, sr, room_size=0.7, wet=0.3), sr, delay_ms=625.0, feedback=0.35, wet=0.25
    ),
}
