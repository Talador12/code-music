"""Reese bass: detuned dual-saw bass, classic DnB/techno, Cm, 174 BPM."""

from code_music import Note, Song, Track

song = Song(title="reese_bass", bpm=174)
tr = song.add_track(Track(name="reese", instrument="reese_bass", volume=0.9, pan=0.0))
pattern = [
    Note("C", 2, 0.5),
    Note("C", 2, 0.5),
    Note("C", 2, 0.25),
    Note("D#", 2, 0.25),
    Note("G", 2, 0.5),
    Note("A#", 1, 0.5),
    Note("G", 1, 0.5),
    Note("C", 2, 0.5),
    Note.rest(0.5),
]
for _ in range(4):
    tr.extend(pattern)
