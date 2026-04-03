"""Phrygian Flame — Spanish/flamenco phrygian textures."""

from code_music import Chord, EffectsChain, Song, Track, reverb
from code_music.theory import phrygian_run

song = Song(title="Phrygian Flame", bpm=120, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(
    phrygian_run("E", 5, length=16)
)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("E", "min", 3, duration=8.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
