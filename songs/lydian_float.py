"""Lydian Float — bright, floating lydian scale textures."""

from code_music import Chord, EffectsChain, Song, Track, reverb
from code_music.theory import lydian_run

song = Song(title="Lydian Float", bpm=85, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(
    lydian_run("C", 5, length=16)
)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("C", "maj7", 3, duration=8.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4)}
