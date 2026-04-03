"""Harmony Chain — each chord suggests the next, melody harmonized in thirds."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import parallel_motion, suggest_next_chord

prog = [("A", "min")]
for _ in range(7):
    prog.append(suggest_next_chord(prog[-1][0], prog[-1][1], key="C")[0])
melody = [Note(r, 5, 1.0) for r, _ in prog]
thirds = parallel_motion(melody, interval=3)
song = Song(title="Harmony Chain", bpm=95, sample_rate=44100)
song.add_track(Track(name="melody", instrument="piano", volume=0.5)).extend(melody)
song.add_track(Track(name="thirds", instrument="piano", volume=0.4, pan=0.15)).extend(thirds)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).extend(
    [Chord(r, s, 3, duration=1.0) for r, s in prog]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
