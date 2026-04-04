"""Constrained Voicings — smooth voice-led chords under span constraints."""

from code_music import EffectsChain, Song, Track, reverb
from code_music.theory import smooth_voicings

song = Song(title="Constrained Voicings", bpm=72)

prog = [
    ("C", "maj7"),
    ("A", "min7"),
    ("D", "min7"),
    ("G", "dom7"),
    ("C", "maj7"),
    ("F", "maj7"),
    ("Bb", "dom7"),
    ("Eb", "maj7"),
]

voicings = smooth_voicings(prog, voices=4, max_span=18, octave=3, duration=4.0)

for i, voice_idx in enumerate(range(4)):
    tr = song.add_track(
        Track(
            name=f"v{i + 1}",
            instrument="organ" if i > 1 else "triangle",
            volume=0.4,
            pan=-0.3 + i * 0.2,
        )
    )
    for v in voicings:
        tr.add(v[voice_idx])

song.effects = {f"v{i + 1}": EffectsChain().add(reverb, room_size=0.6, wet=0.3) for i in range(4)}
