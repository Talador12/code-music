"""Violin longing: G string, Am, largo. The sound of wanting something.

Alluring. The G string is the violin's darkest, most intimate voice.
This melody stays low. It doesn't reach for resolution. It just
sits in the feeling and stays there.
"""

from code_music import Note, Song, Track, crescendo, decrescendo, humanize, reverb, vibrato

song = Song(title="violin_longing", bpm=52)

vln = song.add_track(Track(name="violin", instrument="violin", volume=0.82, pan=0.0))

longing = humanize(
    crescendo(
        [
            Note("A", 3, 2.5),
            Note.rest(0.5),
            Note("G", 3, 1.5),
            Note("A", 3, 0.5),
            Note("C", 4, 3.0),
            Note.rest(1.0),
            Note("B", 3, 1.0),
            Note("A", 3, 1.0),
            Note("G", 3, 2.0),
        ],
        0.3,
        0.82,
    )
    + decrescendo(
        [
            Note("F", 3, 2.0),
            Note("G", 3, 1.0),
            Note.rest(1.0),
            Note("E", 3, 1.5),
            Note("F", 3, 0.5),
            Note("A", 3, 2.0),
            Note("E", 3, 1.0),
            Note("D", 3, 1.0),
            Note("A", 2, 6.0),
        ],
        0.85,
        0.12,
    ),
    vel_spread=0.04,
    timing_spread=0.04,
)
vln.extend(longing)

song._effects = {
    "violin": lambda s, sr: vibrato(
        reverb(s, sr, room_size=0.82, damping=0.38, wet=0.38),
        sr,
        rate_hz=5.2,
        depth_cents=22.0,
    ),
}
