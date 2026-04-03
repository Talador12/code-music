"""Variation Suite — theme + 4 variations using different techniques."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_variation

theme = [Note(n, 5, 0.5) for n in ["C", "D", "E", "F", "G", "A", "B", "C"]]
inv = generate_variation(theme, "inversion")
retro = generate_variation(theme, "retrograde")
aug = generate_variation(theme, "augmentation")
orn = generate_variation(theme, "ornamental", seed=42)
song = Song(title="Variation Suite", bpm=100, sample_rate=44100)
song.add_track(Track(name="theme", instrument="piano", volume=0.5)).extend(theme)
song.add_track(Track(name="inversion", instrument="piano", volume=0.4, pan=-0.2)).extend(inv)
song.add_track(Track(name="retrograde", instrument="piano", volume=0.4, pan=0.2)).extend(retro)
song.effects = {"theme": EffectsChain().add(reverb, room_size=0.4, wet=0.15)}
