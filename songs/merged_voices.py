"""Merged Voices — two melodies interleaved into one track."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import merge_tracks

melody_a = [Note(n, 5, 0.5) for n in ["C", "E", "G", "B"]]
melody_b = [Note(n, 4, 0.5) for n in ["A", "C", "E", "G"]]
merged = merge_tracks([melody_a, melody_b])
song = Song(title="Merged Voices", bpm=100, sample_rate=44100)
song.add_track(Track(name="merged", instrument="piano", volume=0.5)).extend(merged)
song.effects = {"merged": EffectsChain().add(reverb, room_size=0.4, wet=0.15)}
