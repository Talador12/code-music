"""Trumpet fanfare — bright C major triadic figure, short articulations."""

from code_music import Note, Song, Track

song = Song(title="trumpet_fanfare", bpm=120)
tr = song.add_track(Track(name="trumpet", instrument="trumpet", volume=0.85))
fanfare = [
    Note("C", 4, 0.5),
    Note("E", 4, 0.5),
    Note("G", 4, 0.5),
    Note("C", 5, 1.0),
    Note("C", 5, 0.5),
    Note("G", 4, 0.25),
    Note("E", 4, 0.25),
    Note("C", 4, 1.0),
    Note("G", 4, 0.5),
    Note("A", 4, 0.5),
    Note("B", 4, 0.5),
    Note("C", 5, 2.0),
]
tr.extend(fanfare)
