"""Triangle wave flute-like tone: smooth highs, good for melodic fills."""

from code_music import Note, Song, Track

song = Song(title="triangle_flute", bpm=100)
tr = song.add_track(Track(name="flute", instrument="triangle", volume=0.75))
phrase = [
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("B", 5, 1.0),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("E", 5, 2.0),
    Note("F#", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 1.0),
    Note("D", 6, 2.0),
]
tr.extend(phrase)
