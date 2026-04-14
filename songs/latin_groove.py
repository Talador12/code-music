"""Latin Groove - bossa nova with walking bass and latin drums."""

from code_music import Chord, Note, Song, Track, scale
from code_music.theory import generate_bass_line

song = Song(title="Latin Groove", bpm=130, sample_rate=44100)

progression = [
    ("A", "min7"),
    ("D", "dom7"),
    ("G", "maj7"),
    ("C", "maj7"),
    ("F", "maj7"),
    ("B", "min7"),
    ("E", "dom7"),
    ("A", "min7"),
]

# Bossa rhythm guitar
guitar = song.add_track(Track(name="guitar", instrument="pluck", volume=0.4, pan=0.15, swing=0.1))
for root, shape in progression * 2:
    guitar.add(Note.rest(0.5))
    guitar.add(Chord(root, shape, 4, duration=0.5, velocity=45))
    guitar.add(Note.rest(0.5))
    guitar.add(Chord(root, shape, 4, duration=0.5, velocity=40))

# Walking bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
try:
    bass_notes = generate_bass_line(progression * 2, style="walking", seed=42)
    bass.extend(bass_notes)
except Exception:
    for root, _ in progression * 2:
        bass.add(Note(root, 2, 2.0, velocity=65))

# Lead
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.4, pan=-0.2))
lead.extend(scale("A", "dorian", octave=5, length=32))

# Hat pattern (bossa-style)
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25, swing=0.12))
for _ in range(64):
    hat.add(Note("C", 6, 0.5, velocity=30))
