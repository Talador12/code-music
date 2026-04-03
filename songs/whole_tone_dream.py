"""Whole Tone Dream — ethereal whole tone scale textures."""

from code_music import Chord, EffectsChain, Song, Track, reverb
from code_music.theory import whole_tone_run

song = Song(title="Whole Tone Dream", bpm=80, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(
    whole_tone_run("C", 5, length=12)
)
song.add_track(Track(name="bass", instrument="bass", volume=0.4)).extend(
    whole_tone_run("C", 2, length=6, duration=0.5)
)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("C", "aug", 3, duration=6.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4)}
