"""Square wave lead: classic hollow 8-bit style melodic lead."""

from code_music import Note, Song, Track

song = Song(title="lead_square", bpm=120)
tr = song.add_track(Track(name="square_lead", instrument="square", volume=0.65))
melody = [
    Note("C", 5, 0.5),
    Note("E", 5, 0.5),
    Note("G", 5, 0.5),
    Note("E", 5, 0.5),
    Note("F", 5, 0.5),
    Note("D", 5, 0.5),
    Note("E", 5, 1.0),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("B", 4, 0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 2.0),
]
tr.extend(melody)
