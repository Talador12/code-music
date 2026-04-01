"""mountain_road.py — Folk / Americana. G major, 96 BPM. Banjo + guitar KS.

Third track for Open Tuning album. Where porch_song.py is intimate
and still, this one moves. Banjo Karplus-Strong over walking bass,
driving rhythm — the kind of music that goes with long drives through
mountains. Appalachian bluegrass feel without being corny about it.
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
    compress,
    crescendo,
    humanize,
    reverb,
)

song = Song(title="Mountain Road", bpm=96, key_sig="G")

BAR = 4.0
r = Note.rest

# ── Banjo KS — the driving voice ─────────────────────────────────────────
banjo = song.add_track(Track(name="banjo", instrument="banjo_ks", volume=0.82, pan=-0.15))

# Classic rolls: forward roll (thumb-index-middle)
roll = humanize(
    [
        Note("G", 3, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("D", 5, EIGHTH),
        Note("G", 4, EIGHTH),
        Note("D", 5, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("G", 3, EIGHTH),
        Note("D", 5, EIGHTH),
    ],
    vel_spread=0.1,
    timing_spread=0.02,
)
c_roll = humanize(
    [
        Note("C", 3, EIGHTH),
        Note("E", 4, EIGHTH),
        Note("G", 4, EIGHTH),
        Note("C", 4, EIGHTH),
        Note("G", 4, EIGHTH),
        Note("E", 4, EIGHTH),
        Note("C", 3, EIGHTH),
        Note("G", 4, EIGHTH),
    ],
    vel_spread=0.1,
    timing_spread=0.02,
)
d_roll = humanize(
    [
        Note("D", 3, EIGHTH),
        Note("F#", 4, EIGHTH),
        Note("A", 4, EIGHTH),
        Note("D", 4, EIGHTH),
        Note("A", 4, EIGHTH),
        Note("F#", 4, EIGHTH),
        Note("D", 3, EIGHTH),
        Note("A", 4, EIGHTH),
    ],
    vel_spread=0.1,
    timing_spread=0.02,
)

# Verse: G G C G D G
for _ in range(2):
    banjo.extend(roll * 2)
    banjo.extend(c_roll)
    banjo.extend(roll)
    banjo.extend(d_roll)
    banjo.extend(roll)

# Melody break — melody on top string
melody = crescendo(
    humanize(
        [
            Note("G", 5, DOTTED_QUARTER),
            Note("A", 5, EIGHTH),
            Note("B", 5, HALF),
            Note("D", 6, QUARTER),
            Note("B", 5, QUARTER),
            Note("A", 5, HALF),
            Note("G", 5, DOTTED_QUARTER),
            Note("F#", 5, EIGHTH),
            Note("E", 5, HALF),
            Note("D", 5, WHOLE),
        ],
        vel_spread=0.07,
        timing_spread=0.03,
    ),
    0.55,
    0.92,
)
banjo.extend(melody)
banjo.extend(roll * 2)

# ── Rhythm guitar KS — strummed chords ───────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_ks", volume=0.58, pan=0.2))
strum_g = humanize([Note("G", 3, QUARTER, velocity=0.72)] * 4, vel_spread=0.1)
strum_c = humanize([Note("C", 3, QUARTER, velocity=0.68)] * 4, vel_spread=0.1)
strum_d = humanize([Note("D", 3, QUARTER, velocity=0.70)] * 4, vel_spread=0.1)

for _ in range(2):
    gtr.extend(strum_g * 2 + strum_c + strum_g + strum_d + strum_g)
gtr.extend([r(BAR)] * 4)  # rest during melody
gtr.extend(strum_g * 2)

# ── Contrabass — walking ──────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.72, pan=0.05))
walk = [
    Note("G", 2, 1.0),
    Note("A", 2, 1.0),
    Note("B", 2, 1.0),
    Note("D", 3, 1.0),
    Note("G", 2, 1.0),
    Note("F#", 2, 1.0),
    Note("G", 2, 1.0),
    Note("D", 2, 1.0),
    Note("C", 2, 1.0),
    Note("D", 2, 1.0),
    Note("E", 2, 1.0),
    Note("G", 2, 1.0),
    Note("G", 2, 1.0),
    Note("A", 2, 1.0),
    Note("B", 2, 1.0),
    Note("D", 3, 1.0),
    Note("D", 2, 1.0),
    Note("E", 2, 1.0),
    Note("F#", 2, 1.0),
    Note("A", 2, 1.0),
    Note("G", 2, 4.0),
]
bass.extend(walk * 2 + [r(BAR)] * 4 + walk[:8])

song.effects = {
    "banjo": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.12),
    "guitar": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.1),
    "bass": lambda s, sr: compress(s, sr, threshold=0.55, ratio=3.0, makeup_gain=1.1),
}
