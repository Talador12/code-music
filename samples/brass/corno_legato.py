"""French horn: hunting call figure, legato, wide dynamic range."""

from code_music import Note, Song, Track

song = Song(title="french_horn_call", bpm=88)
tr = song.add_track(Track(name="horn", instrument="french_horn", volume=0.75))
call = [
    Note("C", 3, 1.0),
    Note("G", 3, 1.0),
    Note("C", 4, 2.0),
    Note("E", 4, 1.0),
    Note("D", 4, 0.5),
    Note("C", 4, 0.5),
    Note("G", 3, 2.0),
    Note("F", 3, 1.0),
    Note("A", 3, 1.0),
    Note("C", 4, 4.0),
]
tr.extend(call)
