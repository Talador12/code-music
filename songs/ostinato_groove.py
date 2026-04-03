"""Ostinato Groove — repeating bass pattern with subtle variation."""

from code_music import Chord, EffectsChain, Note, Song, Track, euclid, reverb
from code_music.theory import ostinato

pattern = [Note(n, 3, 0.5) for n in ["A", "C", "E", "A"]]
bass = ostinato(pattern, repeats=4, variation=0.15, seed=42)
song = Song(title="Ostinato Groove", bpm=100, sample_rate=44100)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(bass)
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6)).extend(
    euclid(3, 8, "C", 2, 0.5) * 4
)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("A", "min7", 3, duration=8.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
