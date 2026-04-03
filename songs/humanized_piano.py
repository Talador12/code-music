"""Humanized Piano — velocity variation for natural feel."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import humanize_velocity

raw = [Note(n, 5, 0.5, velocity=0.7) for n in ["C", "E", "G", "B", "A", "G", "E", "C"]]
humanized = humanize_velocity(raw, amount=0.2, seed=42)
song = Song(title="Humanized Piano", bpm=100, sample_rate=44100)
song.add_track(Track(name="piano", instrument="piano", volume=0.5)).extend(humanized)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("C", "maj7", 3, duration=4.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
