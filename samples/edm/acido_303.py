"""Acid 303: TB-303-style acid bassline, Gm, 130 BPM. Filter simulated by low notes."""

from code_music import Note, Song, Track

song = Song(title="acid_303", bpm=130)
tr = song.add_track(Track(name="acid", instrument="acid", volume=0.8, pan=0.0))
# Acid is all about rhythmic pattern + pitch glide feel
acid = [
    Note("G", 2, 0.25),
    Note("G", 2, 0.25),
    Note("D", 3, 0.25),
    Note("G", 2, 0.25),
    Note("A#", 2, 0.25),
    Note("G", 2, 0.25),
    Note("A", 2, 0.25),
    Note("G", 2, 0.25),
    Note("G", 2, 0.25),
    Note("F", 3, 0.25),
    Note("D#", 3, 0.25),
    Note("D", 3, 0.25),
    Note("C", 3, 0.5),
    Note("A#", 2, 0.5),
    Note("G", 2, 0.25),
    Note("G", 2, 0.25),
    Note("A", 2, 0.25),
    Note("A#", 2, 0.25),
    Note("D", 3, 0.5),
    Note("C", 3, 0.25),
    Note("A#", 2, 0.25),
    Note("G", 2, 2.0),
]
for _ in range(2):
    tr.extend(acid)
