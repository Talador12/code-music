"""Modal Borrow — major progression with borrowed minor chords."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import modal_interchange

prog = [("C", "maj"), ("F", "maj"), ("G", "maj"), ("C", "maj")]
borrowed = modal_interchange(prog, key="C", target_mode="minor")
print(f"Original: {prog}")
print(f"Borrowed: {borrowed}")
song = Song(title="Modal Borrow", bpm=100, sample_rate=44100)
song.add_track(Track(name="pad", instrument="pad", volume=0.4)).extend(
    [Chord(r, s, 3, duration=4.0) for r, s in borrowed]
)
song.add_track(Track(name="lead", instrument="piano", volume=0.45)).extend(
    [Note(n, 5, 1.0) for n in ["C", "E", "G", "B", "A", "F", "C", "E"]]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
