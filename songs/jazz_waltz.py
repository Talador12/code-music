"""Jazz Waltz - 3/4 time with walking bass and brushes feel."""

from code_music import Chord, Note, Song, Track, scale
from code_music.theory import generate_bass_line

song = Song(title="Jazz Waltz", bpm=140, time_sig=(3, 4), sample_rate=44100)

progression = [
    ("D", "min7"),
    ("G", "dom7"),
    ("C", "maj7"),
    ("A", "dom7"),
    ("D", "min7"),
    ("G", "dom7"),
    ("C", "maj7"),
    ("C", "maj7"),
]

# Piano comping (waltz pattern: bass note + chord + chord)
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.5, pan=0.1, swing=0.15))
for root, shape in progression:
    piano.add(Note(root, 3, 1.0, velocity=55))
    piano.add(Chord(root, shape, 4, duration=1.0, velocity=40))
    piano.add(Chord(root, shape, 4, duration=1.0, velocity=35))

# Walking bass in 3/4
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55, swing=0.12))
try:
    bass_notes = generate_bass_line(progression, style="walking", seed=42)
    bass.extend(bass_notes)
except Exception:
    for root, _ in progression:
        bass.add(Note(root, 2, 1.0, velocity=65))
        bass.add(Note(root, 2, 1.0, velocity=55))
        bass.add(Note(root, 2, 1.0, velocity=50))

# Melody
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.4, pan=0.2, swing=0.1))
lead.extend(scale("D", "dorian", octave=5, length=24))

# Brushes (light hat)
hat = song.add_track(Track(name="brushes", instrument="drums_hat", volume=0.25, swing=0.2))
for _ in range(24):
    hat.add(Note("C", 6, 1.0, velocity=30))
