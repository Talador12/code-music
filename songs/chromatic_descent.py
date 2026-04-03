"""Chromatic Descent — chromatic run down + trill ornaments."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import chromatic_run, trill

song = Song(title="Chromatic Descent", bpm=100, sample_rate=44100)
song.add_track(Track(name="run", instrument="piano", volume=0.5)).extend(
    chromatic_run("C", 6, length=24, direction="down", duration=0.125)
)
song.add_track(Track(name="trill", instrument="piano", volume=0.4, pan=0.2)).extend(
    trill("E", 5, duration=3.0)
)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("C", "min", 3, duration=3.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
