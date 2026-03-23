"""Power chords: distorted E-shape power chord stabs, rock rhythm."""

from code_music import Chord, Note, Song, Track

song = Song(title="power_chords", bpm=140)
rhythm = song.add_track(Track(name="guitar", instrument="sawtooth", volume=0.75))
# E5 power chord shape = root + perfect fifth
stabs = [
    Chord("E", [0, 7], 2, duration=1.0),
    Note.rest(0.5),
    Chord("E", [0, 7], 2, duration=0.5),
    Chord("G", [0, 7], 2, duration=1.0),
    Note.rest(0.5),
    Chord("A", [0, 7], 2, duration=0.5),
    Chord("D", [0, 7], 2, duration=2.0),
    Note.rest(1.0),
    Chord("E", [0, 7], 2, duration=1.0),
    Note.rest(1.0),
]
for _ in range(2):
    rhythm.extend(stabs)
