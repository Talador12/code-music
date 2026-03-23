"""Cello solo: Bach-inspired solo in C minor, expressive and singing."""

from code_music import Note, Song, Track

song = Song(title="cello_solo", bpm=68)
tr = song.add_track(Track(name="cello", instrument="cello", volume=0.82))
solo = [
    Note("C", 3, 1.0),
    Note("D", 3, 0.5),
    Note("D#", 3, 0.5),
    Note("F", 3, 1.0),
    Note("G", 3, 2.0),
    Note.rest(0.5),
    Note("A#", 3, 0.5),
    Note("A", 3, 0.5),
    Note("G", 3, 0.5),
    Note("F", 3, 0.5),
    Note("D#", 3, 1.0),
    Note("D", 3, 1.0),
    Note("C", 3, 4.0),
    Note("G", 2, 0.5),
    Note("A", 2, 0.5),
    Note("A#", 2, 1.0),
    Note("C", 3, 0.5),
    Note("D", 3, 0.5),
    Note("D#", 3, 0.5),
    Note("F", 3, 0.5),
    Note("G", 3, 4.0),
]
tr.extend(solo)
