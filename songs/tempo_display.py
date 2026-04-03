"""Tempo Display — shows tempo map for a song."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import tempo_map

song = Song(title="Tempo Display", bpm=120, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(
    [Note(n, 5, 1.0) for n in ["A", "C", "E", "G", "F", "E", "C", "A"]]
)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).add(
    Chord("A", "min7", 3, duration=8.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
print(tempo_map(song))
