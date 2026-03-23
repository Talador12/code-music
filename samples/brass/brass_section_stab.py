"""Brass section stabs: tight big-band punches, Bb major, swing feel."""

from code_music import Chord, Note, Song, Track

song = Song(title="brass_section_stab", bpm=160)
tr = song.add_track(Track(name="brass", instrument="brass_section", volume=0.85, swing=0.45))
pattern = [
    Chord("A#", "maj", 3, duration=0.5),
    Note.rest(0.5),
    Chord("A#", "dom7", 3, duration=0.5),
    Note.rest(1.5),
    Chord("F", "maj", 3, duration=0.5),
    Note.rest(0.5),
    Chord("A#", "maj", 3, duration=1.0),
    Note.rest(1.0),
]
for _ in range(3):
    tr.extend(pattern)
