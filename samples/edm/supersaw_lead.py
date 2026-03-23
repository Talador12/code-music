"""Supersaw lead: Zedd/trance-style detuned saw wall, Am, 128 BPM.

The supersaw is the defining sound of big-room EDM — 7 detuned saws.
"""

from code_music import Note, Song, Track

song = Song(title="supersaw_lead", bpm=128)
tr = song.add_track(Track(name="supersaw", instrument="supersaw", volume=0.65, pan=0.0))
melody = [
    Note("A", 4, 0.5),
    Note("C", 5, 0.5),
    Note("E", 5, 1.0),
    Note("G", 5, 0.5),
    Note("F", 5, 0.5),
    Note("E", 5, 1.0),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("A", 4, 0.5),
    Note("B", 4, 0.5),
    Note("C", 5, 2.0),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 2.0),
]
for _ in range(2):
    tr.extend(melody)
