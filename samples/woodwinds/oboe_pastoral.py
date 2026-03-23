"""Oboe: pastoral solo in D major, slow and singing."""

from code_music import Note, Song, Track

song = Song(title="oboe_pastoral", bpm=80)
tr = song.add_track(Track(name="oboe", instrument="oboe", volume=0.72))
solo = [
    Note("D", 5, 1.5),
    Note("E", 5, 0.5),
    Note("F#", 5, 1.0),
    Note("A", 5, 2.0),
    Note.rest(1.0),
    Note("G", 5, 0.5),
    Note("F#", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C#", 5, 1.0),
    Note("B", 4, 1.0),
    Note.rest(1.0),
    Note("A", 4, 0.5),
    Note("B", 4, 0.5),
    Note("C#", 5, 1.0),
    Note("D", 5, 4.0),
]
tr.extend(solo)
