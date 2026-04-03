"""Transposed Blues — same progression in two keys."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_bass_line, transpose_progression

prog_a = [("A", "dom7"), ("D", "dom7"), ("E", "dom7"), ("A", "dom7")]
prog_e = transpose_progression(prog_a, semitones=7)
song = Song(title="Transposed Blues", bpm=95, sample_rate=44100)
song.add_track(Track(name="pad_a", instrument="pad", volume=0.35)).extend(
    [Chord(r, s, 3, duration=4.0) for r, s in prog_a]
)
song.add_track(Track(name="pad_e", instrument="pad", volume=0.35, pan=0.2)).extend(
    [Chord(r, s, 3, duration=4.0) for r, s in prog_e]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    generate_bass_line(prog_a, style="root_fifth")
)
song.effects = {"pad_a": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
