"""Harmonic X-Ray — play a complex progression then its skeleton."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import harmonic_skeleton

song = Song(title="Harmonic X-Ray", bpm=90)

# Complex jazz progression
complex_prog = [
    ("C", "maj7"),
    ("A", "dom7"),
    ("D", "min7"),
    ("G", "dom7"),
    ("E", "min7"),
    ("Eb", "dim"),
    ("D", "min7"),
    ("Db", "dom7"),
]

# Its functional skeleton
skeleton = harmonic_skeleton(complex_prog, key="C")

# Play the complex version first
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.1))
for root, shape in complex_prog:
    pad.add(Chord(root, shape, 3, duration=4.0))

# Then the skeleton
for root, shape in skeleton:
    pad.add(Chord(root, shape, 3, duration=4.0))

# Bass following both
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root, _ in complex_prog + skeleton:
    bass.add(Note(root, 2, 4.0))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
