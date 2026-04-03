"""Tritone Jazz — ii-V-I with tritone substitutions."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_bass_line, tritone_sub

prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "min7")]
subbed = tritone_sub(prog)
print(f"Original: {prog}")
print(f"Tritone sub: {subbed}")
song = Song(title="Tritone Jazz", bpm=130, sample_rate=44100)
song.add_track(Track(name="pad", instrument="piano", volume=0.45)).extend(
    [Chord(r, s, 4, duration=4.0) for r, s in subbed]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    generate_bass_line(subbed, style="walking", seed=42)
)
song.add_track(Track(name="lead", instrument="piano", volume=0.4, pan=0.15)).extend(
    [Note(n, 5, 1.0) for n in "D F A C B D G F E G C B A C E G".split()]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
