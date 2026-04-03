"""Suggested Progression — auto-suggested chord sequence."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_bass_line, suggest_next_chord

prog = [("C", "maj")]
for _ in range(7):
    suggestions = suggest_next_chord(prog[-1][0], prog[-1][1], key="C")
    prog.append(suggestions[0])
print("Progression:", " → ".join(f"{r}{s}" for r, s in prog))
song = Song(title="Suggested Progression", bpm=110, sample_rate=44100)
song.add_track(Track(name="pad", instrument="pad", volume=0.4)).extend(
    [Chord(r, s, 3, duration=2.0) for r, s in prog]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    generate_bass_line(prog, style="root")
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
