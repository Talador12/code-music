"""Tuba: Oompah bass pattern, waltz feel in F."""

from code_music import Note, Song, Track

song = Song(title="tuba_low", bpm=138)
tr = song.add_track(Track(name="tuba", instrument="tuba", volume=0.85))
oompah = [
    Note("F", 1, 1.0),
    Note("C", 2, 0.5),
    Note("C", 2, 0.5),
    Note("F", 1, 1.0),
    Note("C", 2, 0.5),
    Note("C", 2, 0.5),
    Note("D#", 1, 1.0),
    Note("A#", 1, 0.5),
    Note("A#", 1, 0.5),
    Note("C", 2, 1.0),
    Note("G", 2, 0.5),
    Note("G", 2, 0.5),
]
for _ in range(2):
    tr.extend(oompah)
