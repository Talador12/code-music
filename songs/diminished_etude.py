"""Diminished Etude — diminished scale patterns."""

from code_music import Chord, EffectsChain, Song, Track, reverb
from code_music.theory import diminished_run

song = Song(title="Diminished Etude", bpm=130, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(
    diminished_run("C", octave=5, length=16, duration=0.25)
)
song.add_track(Track(name="bass", instrument="bass", volume=0.45)).extend(
    diminished_run("C", octave=2, length=8, duration=0.5)
)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("C", "dim7", 3, duration=4.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
