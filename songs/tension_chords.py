"""Tension Chords — auto-extended chords with all available tensions."""

from code_music import EffectsChain, Song, Track, reverb
from code_music.theory import available_tensions, chord_extensions

song = Song(title="Tension Chords", bpm=85, sample_rate=44100)
tr = song.add_track(Track(name="piano", instrument="piano", volume=0.45))
for root, shape in [("C", "min7"), ("F", "dom7"), ("Bb", "maj7"), ("Eb", "maj7")]:
    tensions = available_tensions(root, shape)
    tr.extend(chord_extensions(root, shape, tensions[:2]))
    print(f"{root}{shape}: {tensions}")
song.effects = {"piano": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
