"""Dorian Study — scale_info guides chord and melody choices."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale
from code_music.theory import scale_info

info = scale_info("dorian", "D")
print(f"Dorian: {' '.join(info['notes'])}")
song = Song(title="Dorian Study", bpm=100, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(
    scale("D", "dorian", octave=5, length=8)
)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).add(
    Chord("D", "min7", 3, duration=8.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
