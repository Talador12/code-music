"""Markov Melody — AI-continued melody over chord changes."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import continue_melody

seed = [Note("A", 5, 0.5), Note("C", 6, 0.5), Note("E", 6, 0.5), Note("D", 6, 0.5)]
melody = continue_melody(seed, bars=4, key="A", mode="minor", seed_rng=42)

song = Song(title="Markov Melody", bpm=100, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15)).extend(melody)
song.add_track(Track(name="pad", instrument="pad", volume=0.4)).extend(
    [Chord("A", "min7", 3, duration=8.0), Chord("F", "maj7", 3, duration=8.0)]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    [Note("A", 2, 8.0), Note("F", 2, 8.0)]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
