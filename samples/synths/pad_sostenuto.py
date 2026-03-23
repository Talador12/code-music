"""Lush pad: slow-attack sine pad in F major, layered chords for atmosphere."""

from code_music import Chord, Song, Track

song = Song(title="pad_lush", bpm=70)
tr = song.add_track(Track(name="pad", instrument="pad", volume=0.6))
progression = [
    Chord("F", "maj7", 3, duration=4.0),
    Chord("C", "maj7", 3, duration=4.0),
    Chord("A", "min7", 3, duration=4.0),
    Chord("G", "dom7", 3, duration=4.0),
]
tr.extend(progression)
