"""Quantized Groove — humanized notes snapped to 16th grid."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.composition import quantize_track

raw = [
    Note("C", 5, 0.48),
    Note("E", 5, 0.53),
    Note("G", 5, 0.47),
    Note("C", 6, 0.52),
    Note("G", 5, 0.49),
    Note("E", 5, 0.51),
    Note("D", 5, 0.48),
    Note("C", 5, 0.52),
]
quantized = quantize_track(raw, grid=0.5)
song = Song(title="Quantized Groove", bpm=120, sample_rate=44100)
song.add_track(Track(name="raw", instrument="piano", volume=0.4, pan=-0.2)).extend(raw)
song.add_track(Track(name="quantized", instrument="piano", volume=0.5, pan=0.2)).extend(quantized)
song.effects = {"quantized": EffectsChain().add(reverb, room_size=0.4, wet=0.15)}
