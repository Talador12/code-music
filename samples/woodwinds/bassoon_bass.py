"""Bassoon: deep walking bass in C minor, Baroque-feel."""

from code_music import Note, Song, Track

song = Song(title="bassoon_bass", bpm=92)
tr = song.add_track(Track(name="bassoon", instrument="bassoon", volume=0.8))
walk = [
    Note("C", 3, 1.0),
    Note("D", 3, 1.0),
    Note("D#", 3, 1.0),
    Note("F", 3, 1.0),
    Note("G", 3, 1.0),
    Note("F", 3, 1.0),
    Note("D#", 3, 1.0),
    Note("C", 3, 1.0),
    Note("A#", 2, 1.0),
    Note("C", 3, 1.0),
    Note("D", 3, 1.0),
    Note("D#", 3, 1.0),
    Note("G", 2, 2.0),
    Note.rest(2.0),
]
for _ in range(2):
    tr.extend(walk)
