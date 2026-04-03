"""Ornamental Theme — plain theme + ornamented version side by side."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_variation

theme = [Note(n, 4, 1.0) for n in ["D", "F", "A", "G", "F", "E", "D", "C"]]
ornamented = generate_variation(theme, "ornamental", seed=77)
song = Song(title="Ornamental Theme", bpm=85, sample_rate=44100)
song.add_track(Track(name="theme", instrument="piano", volume=0.5)).extend(theme)
song.add_track(Track(name="ornament", instrument="piano", volume=0.4, pan=0.15)).extend(ornamented)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("D", "min", 3, duration=8.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
