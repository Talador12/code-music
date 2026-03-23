"""Organ sample: Hammond-style sustained chords with fast attack, zero decay."""

from code_music import Chord, Song, Track

song = Song(title="fm_organ", bpm=90)
tr = song.add_track(Track(name="organ", instrument="organ", volume=0.7))
progression = [
    Chord("C", "maj", 4, duration=2.0),
    Chord("F", "maj", 4, duration=2.0),
    Chord("G", "dom7", 4, duration=2.0),
    Chord("C", "maj", 4, duration=2.0),
]
for _ in range(2):
    tr.extend(progression)
