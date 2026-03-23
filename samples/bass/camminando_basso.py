"""Walking bass line: jazz-style quarter-note walk through Cm."""

from code_music import Note, Song, Track

song = Song(title="walking_bass", bpm=120)
tr = song.add_track(Track(name="bass", instrument="bass", volume=0.85))
# Two-bar walking pattern
pattern = [
    Note("C", 2, 1.0),
    Note("E", 2, 1.0),
    Note("G", 2, 1.0),
    Note("A#", 2, 1.0),
    Note("G", 2, 1.0),
    Note("F", 2, 1.0),
    Note("E", 2, 1.0),
    Note("C", 2, 1.0),
]
for _ in range(2):
    tr.extend(pattern)
