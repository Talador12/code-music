"""Funk Pocket — syncopated funk bass with octave pops."""

from code_music import Chord, EffectsChain, Note, Song, Track, distortion, reverb
from code_music.theory import bass_line_funk

song = Song(title="Funk Pocket", bpm=100)

prog = [("E", "min7")] * 4 + [("A", "dom7")] * 2 + [("E", "min7")] * 2

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
bass.extend(bass_line_funk(prog, seed=42))

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
for _ in range(16):
    kick.extend([Note("C", 2, 0.5), Note.rest(0.25), Note("C", 2, 0.25)])

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25))
for _ in range(32):
    hat.add(Note("C", 5, 0.25))
    hat.add(Note("C", 5, 0.25, velocity=50))

chords = song.add_track(Track(name="chords", instrument="organ", volume=0.3, pan=-0.2))
for root, shape in prog:
    chords.add(Chord(root, shape, 3, duration=4.0))

song.effects = {
    "bass": EffectsChain().add(distortion, gain=1.5, wet=0.2),
    "chords": EffectsChain().add(reverb, room_size=0.3, wet=0.15),
}
