"""Piano phrase: lyrical right-hand phrase in F major with natural decay."""

from code_music import Note, Song, Track

song = Song(title="piano_phrase", bpm=88)
tr = song.add_track(Track(name="piano", instrument="piano", volume=0.8))
phrase = [
    Note("F", 4, 0.5),
    Note("G", 4, 0.5),
    Note("A", 4, 1.0),
    Note("C", 5, 0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 1.0),
    Note("F", 4, 0.5),
    Note("E", 4, 0.5),
    Note("D", 4, 1.0),
    Note("C", 4, 2.0),
    Note("G", 4, 0.5),
    Note("A", 4, 0.5),
    Note("A#", 4, 1.0),
    Note("A", 4, 0.5),
    Note("G", 4, 0.5),
    Note("F", 4, 2.0),
]
tr.extend(phrase)
