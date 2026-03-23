"""Trumpet solo: Miles Davis-style cool jazz solo, Dm, muted feel."""

from code_music import Note, Song, Track

song = Song(title="trumpet_solo", bpm=112)
r = Note.rest
tr = song.add_track(Track(name="trumpet", instrument="trumpet", volume=0.7, pan=0.0))
# Lots of space — cool jazz is about what you DON'T play
solo = [
    Note("D", 5, 0.5),
    Note("F", 5, 0.5),
    r(0.5),
    Note("A", 5, 1.5),
    r(1.0),
    Note("C", 5, 0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 1.0),
    r(2.0),
    Note("F", 4, 0.25),
    Note("G", 4, 0.25),
    Note("A", 4, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 1.0),
    r(0.5),
    Note("E", 5, 0.5),
    Note("F", 5, 2.0),
    r(2.0),
    Note("A", 4, 0.5),
    Note("C", 5, 0.25),
    Note("D", 5, 0.25),
    Note("F", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    r(0.5),
    Note("C", 5, 4.0),
]
tr.extend(solo)
