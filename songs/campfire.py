"""campfire.py — Folk. D major, 76 BPM. Guitar, harmonica, night air.

Third track for Open Tuning album. The simplest song in the library.
Just a guitar and a harmonica and the feeling of sitting outside
after dark. Karplus-Strong guitar fingerpicking, flute approximating
harmonica, minimal bass. Nothing clever. Just good.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Note,
    Song,
    Track,
    crescendo,
    delay,
    humanize,
    reverb,
)

song = Song(title="Campfire", bpm=76, key_sig="D")

BAR = 4.0
r = Note.rest

# ── Guitar — simple D major shapes ───────────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_ks", volume=0.80, pan=-0.1))

# Open D fingerpicking — thumb covers bass, fingers cover melody
d_pick = humanize(
    [
        Note("D", 3, EIGHTH),
        Note("F#", 4, EIGHTH),
        Note("A", 4, EIGHTH),
        Note("F#", 4, EIGHTH),
        Note("D", 3, EIGHTH),
        Note("A", 4, EIGHTH),
        Note("F#", 4, EIGHTH),
        Note("D", 5, EIGHTH),
    ],
    vel_spread=0.10,
    timing_spread=0.04,
)
g_pick = humanize(
    [
        Note("G", 3, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("D", 5, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("G", 3, EIGHTH),
        Note("D", 5, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("G", 4, EIGHTH),
    ],
    vel_spread=0.10,
    timing_spread=0.04,
)
a_pick = humanize(
    [
        Note("A", 2, EIGHTH),
        Note("E", 4, EIGHTH),
        Note("A", 4, EIGHTH),
        Note("E", 4, EIGHTH),
        Note("A", 2, EIGHTH),
        Note("A", 4, EIGHTH),
        Note("C#", 5, EIGHTH),
        Note("E", 5, EIGHTH),
    ],
    vel_spread=0.09,
    timing_spread=0.04,
)

# Verse: D D G D A D
for _ in range(2):
    gtr.extend(d_pick * 2)
    gtr.extend(g_pick)
    gtr.extend(d_pick)
    gtr.extend(a_pick)
    gtr.extend(d_pick)

# Melody verse
mel_verse = humanize(
    [
        Note("D", 5, DOTTED_QUARTER),
        Note("E", 5, EIGHTH),
        Note("F#", 5, HALF),
        Note("E", 5, QUARTER),
        Note("D", 5, QUARTER),
        Note("A", 4, HALF),
        Note("B", 4, DOTTED_QUARTER),
        Note("A", 4, EIGHTH),
        Note("G", 4, HALF),
        Note("A", 4, WHOLE),
        r(HALF),
        Note("D", 5, QUARTER),
        Note("E", 5, QUARTER),
        Note("F#", 5, HALF),
        Note("G", 5, HALF),
        Note("A", 5, WHOLE),
        r(BAR),
    ],
    vel_spread=0.08,
    timing_spread=0.05,
)
gtr.extend(mel_verse)
gtr.extend(d_pick * 4)

# ── Harmonica (flute approximation) ───────────────────────────────────────
harp = song.add_track(Track(name="harmonica", instrument="flute", volume=0.55, pan=0.2))
harp.extend([r(BAR)] * 8)

harmonica = humanize(
    crescendo(
        [
            Note("D", 5, DOTTED_QUARTER),
            Note("C#", 5, EIGHTH),
            Note("B", 4, HALF),
            Note("A", 4, QUARTER),
            r(QUARTER),
            Note("F#", 4, HALF),
            r(HALF),
            Note("G", 4, HALF),
            Note("A", 4, WHOLE),
            r(HALF),
            Note("B", 4, DOTTED_QUARTER),
            Note("A", 4, EIGHTH),
            Note("G", 4, HALF),
            Note("F#", 4, QUARTER),
            Note("E", 4, QUARTER),
            Note("D", 4, HALF),
            Note("A", 4, WHOLE),
            r(BAR),
        ],
        0.3,
        0.75,
    ),
    vel_spread=0.07,
    timing_spread=0.06,
)
harp.extend(harmonica)
harp.extend([r(BAR)] * 4)

# ── Bass — walking, gentle ────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.58, pan=0.05))
bass_walk = humanize(
    [
        Note("D", 2, 1.0),
        Note("F#", 2, 1.0),
        Note("A", 2, 1.0),
        Note("D", 3, 1.0),
        Note("D", 2, 1.0),
        Note("E", 2, 1.0),
        Note("F#", 2, 1.0),
        Note("A", 2, 1.0),
        Note("G", 2, 1.0),
        Note("A", 2, 1.0),
        Note("B", 2, 1.0),
        Note("D", 3, 1.0),
        Note("A", 1, 1.0),
        Note("C#", 2, 1.0),
        Note("E", 2, 1.0),
        Note("A", 2, 1.0),
    ]
    * 3,
    vel_spread=0.06,
    timing_spread=0.02,
)
bass.extend(bass_walk)
bass.extend([r(BAR)] * 4)

song._effects = {
    "guitar": lambda s, sr: reverb(s, sr, room_size=0.5, damping=0.5, wet=0.14),
    "harmonica": lambda s, sr: delay(
        reverb(s, sr, room_size=0.55, wet=0.2), sr, delay_ms=394.0, feedback=0.2, wet=0.12
    ),
    "bass": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.1),
}
