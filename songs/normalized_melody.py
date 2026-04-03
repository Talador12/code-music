"""Normalized Melody — same melody at original octaves vs normalized to one."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import normalize_notes

wide = [
    Note(n, o, 0.5)
    for n, o in [("C", 3), ("E", 4), ("G", 5), ("C", 6), ("G", 5), ("E", 4), ("C", 3), ("C", 3)]
]
flat = normalize_notes(wide, target_octave=4)
song = Song(title="Normalized Melody", bpm=100, sample_rate=44100)
song.add_track(Track(name="wide", instrument="piano", volume=0.5, pan=-0.2)).extend(wide)
song.add_track(Track(name="flat", instrument="piano", volume=0.5, pan=0.2)).extend(flat)
song.effects = {"wide": EffectsChain().add(reverb, room_size=0.4, wet=0.15)}
