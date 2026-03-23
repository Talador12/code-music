"""Moonlit strings: string quartet, Cm Dorian, sul tasto (over fingerboard — soft).

Alluring. The Dorian mode is minor but with a raised 6th — it has
sadness with a sliver of hope in it. Slow, connected, tender.
Close your eyes.
"""

from code_music import Note, Song, Track, crescendo, decrescendo, humanize, reverb, stereo_width

song = Song(title="moonlit_strings", bpm=58)

# Violin 1: the lead voice, singing
vln1_line = humanize(
    crescendo(
        [
            Note("C", 5, 2.0),
            Note("D", 5, 1.0),
            Note("D#", 5, 1.0),
            Note("G", 5, 3.0),
            Note.rest(1.0),
            Note("F", 5, 1.5),
            Note("E", 5, 0.5),
            Note("D", 5, 1.0),
            Note("C", 5, 4.0),
        ],
        0.35,
        0.85,
    )
    + decrescendo(
        [
            Note("A", 5, 2.0),
            Note("G", 5, 1.0),
            Note("F", 5, 1.0),
            Note("D#", 5, 2.0),
            Note("D", 5, 1.0),
            Note.rest(1.0),
            Note("C", 5, 6.0),
        ],
        0.9,
        0.15,
    ),
    vel_spread=0.04,
    timing_spread=0.03,
)

# Violin 2: a third below, following
vln2_line = humanize(
    crescendo(
        [
            Note("G", 4, 2.0),
            Note("A", 4, 1.0),
            Note("A#", 4, 1.0),
            Note("D#", 5, 3.0),
            Note.rest(1.0),
            Note("D", 5, 1.0),
            Note("C", 5, 1.0),
            Note("A#", 4, 1.0),
            Note("A", 4, 1.0),
            Note("G", 4, 4.0),
        ],
        0.3,
        0.75,
    )
    + decrescendo(
        [
            Note("F", 5, 2.0),
            Note("D#", 5, 1.0),
            Note("D", 5, 1.0),
            Note("C", 5, 2.0),
            Note("A#", 4, 1.0),
            Note.rest(1.0),
            Note("G", 4, 6.0),
        ],
        0.8,
        0.1,
    ),
    vel_spread=0.04,
    timing_spread=0.03,
)

# Viola: middle voice, steady
viola_line = [
    Note("C", 4, 2.0),
    Note("D", 4, 2.0),
    Note("D#", 4, 4.0),
    Note("F", 4, 2.0),
    Note("D", 4, 2.0),
    Note("C", 4, 4.0),
    Note("D#", 4, 2.0),
    Note("D", 4, 2.0),
    Note("C", 4, 6.0),
]

# Cello: bass voice
cello_line = crescendo(
    [
        Note("C", 3, 4.0),
        Note("G", 3, 4.0),
        Note("A#", 2, 4.0),
        Note("G", 3, 4.0),
        Note("A#", 2, 4.0),
        Note("C", 3, 2.0),
        Note("C", 3, 6.0),
    ],
    0.3,
    0.75,
)

for name, inst, line, pan_v in [
    ("vln1", "violin", vln1_line, -0.45),
    ("vln2", "violin", vln2_line, -0.15),
    ("vla", "strings", viola_line, 0.15),
    ("vc", "cello", cello_line, 0.45),
]:
    tr = song.add_track(Track(name=name, instrument=inst, volume=0.68, pan=pan_v))
    tr.extend(line)

song._effects = {
    k: lambda s, sr: stereo_width(reverb(s, sr, room_size=0.85, damping=0.4, wet=0.35), width=1.4)
    for k in ("vln1", "vln2", "vla", "vc")
}
