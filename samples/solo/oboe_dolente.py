"""Oboe elegy: solo oboe, D minor, adagio, 48 BPM.

Alluring. The oboe is the most vocal instrument — it sounds
like a human voice with all the words taken out. Just the feeling.
Grief that hasn't collapsed yet. Still upright.
"""

from code_music import Note, Song, Track, crescendo, decrescendo, humanize, reverb

song = Song(title="oboe_elegy", bpm=48)

ob = song.add_track(Track(name="oboe", instrument="oboe", volume=0.8, pan=0.0))

elegy = humanize(
    crescendo(
        [
            Note("D", 5, 2.0),
            Note("F", 5, 1.0),
            Note.rest(1.0),
            Note("A", 5, 3.0),
            Note.rest(1.0),
            Note("G", 5, 1.0),
            Note("F", 5, 0.5),
            Note("E", 5, 0.5),
            Note("D", 5, 2.0),
            Note.rest(2.0),
        ],
        0.3,
        0.85,
    )
    + decrescendo(
        [
            Note("C", 5, 1.5),
            Note("D", 5, 0.5),
            Note("F", 5, 2.0),
            Note("E", 5, 1.0),
            Note.rest(0.5),
            Note("D", 5, 0.5),
            Note("A", 4, 2.0),
            Note("F", 4, 1.0),
            Note("D", 4, 6.0),
        ],
        0.9,
        0.15,
    ),
    vel_spread=0.05,
    timing_spread=0.05,
)
ob.extend(elegy)

song._effects = {
    "oboe": lambda s, sr: reverb(s, sr, room_size=0.8, damping=0.35, wet=0.35),
}
