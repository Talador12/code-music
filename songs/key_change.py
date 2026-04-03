"""Key Change — progression modulates up by a major third."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_bass_line, transpose_progression

prog = [("C", "maj7"), ("A", "min7"), ("F", "maj7"), ("G", "dom7")]
prog_up = transpose_progression(prog, semitones=4)
song = Song(title="Key Change", bpm=110, sample_rate=44100)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord(r, s, 3, duration=4.0) for r, s in prog + prog_up]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    generate_bass_line(prog + prog_up, style="root")
)
song.add_track(Track(name="lead", instrument="piano", volume=0.45)).extend(
    [Note(n, 5, 1.0) for n in "C E G B A C E G E Ab C Eb B Eb Ab Bb".split()]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
