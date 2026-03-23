"""Ambient chord stack: layered open voicings for drone/ambient textures."""

from code_music import Chord, Song, Track

song = Song(title="ambient_stack", bpm=60)
# Layer pad chords at different octaves, slow attack
for octave in [2, 3, 4]:
    tr = song.add_track(Track(name=f"pad_{octave}", instrument="pad", volume=0.4))
    tr.add(Chord("D", "sus2", octave, duration=8.0))
    tr.add(Chord("A", "sus2", octave, duration=8.0))
