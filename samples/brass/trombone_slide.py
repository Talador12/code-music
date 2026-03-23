"""Trombone: slow jazz ballad lines, low register, wide vibrato feel."""

from code_music import Note, Song, Track

song = Song(title="trombone_slide", bpm=72)
tr = song.add_track(Track(name="trombone", instrument="trombone", volume=0.8))
phrase = [
    Note("B", 2, 2.0),
    Note("A", 2, 1.0),
    Note("G", 2, 1.0),
    Note("F", 2, 2.0),
    Note("E", 2, 1.0),
    Note.rest(1.0),
    Note("G", 2, 1.5),
    Note("A", 2, 0.5),
    Note("B", 2, 2.0),
    Note("C", 3, 4.0),
]
tr.extend(phrase)
