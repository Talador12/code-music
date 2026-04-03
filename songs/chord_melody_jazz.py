"""Chord Melody Jazz — melody generated from chord tones with arch contour."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import generate_chord_melody

prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "min7")]
melody = generate_chord_melody(prog, contour="arch", octave=5, seed=42)
song = Song(title="Chord Melody Jazz", bpm=120, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15)).extend(melody)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord(r, s, 3, duration=4.0) for r, s in prog]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    [Note(r, 2, 4.0) for r, _ in prog]
)
song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25),
    "lead": EffectsChain().add(delay, delay_ms=200, feedback=0.15, wet=0.1),
}
