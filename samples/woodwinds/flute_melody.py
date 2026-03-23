"""Flute: lyrical G major melody, high register, light touch."""

from code_music import Note, Song, Track

song = Song(title="flute_melody", bpm=96)
tr = song.add_track(Track(name="flute", instrument="flute", volume=0.75))
melody = [
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("B", 5, 1.0),
    Note("D", 6, 0.5),
    Note("C", 6, 0.5),
    Note("B", 5, 1.0),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F#", 5, 1.0),
    Note("G", 5, 2.0),
    Note.rest(1.0),
    Note("E", 5, 0.5),
    Note("F#", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("B", 5, 1.0),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("D", 6, 3.0),
    Note.rest(1.0),
]
tr.extend(melody)
