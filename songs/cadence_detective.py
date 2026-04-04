"""Cadence Detective — a progression designed to showcase all four cadence types."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import detect_cadences, functional_analysis

song = Song(title="Cadence Detective", bpm=80)

# Progression with authentic, plagal, half, and deceptive cadences
prog = [
    ("C", "maj"),
    ("F", "maj"),
    ("G", "dom7"),
    ("C", "maj"),  # authentic
    ("F", "maj"),
    ("C", "maj"),  # plagal
    ("D", "min"),
    ("G", "dom7"),  # half
    ("G", "dom7"),
    ("A", "min"),  # deceptive
    ("F", "maj"),
    ("G", "dom7"),
    ("C", "maj"),  # authentic
]

# Pad
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.1))
for root, shape in prog:
    pad.add(Chord(root, shape, 3, duration=4.0))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root, _ in prog:
    bass.add(Note(root, 2, 4.0))

# Melody
lead = song.add_track(Track(name="lead", instrument="triangle", volume=0.45, pan=0.15))
melody = [
    Note("E", 5, 2.0),
    Note("C", 5, 2.0),
    Note("F", 5, 2.0),
    Note("E", 5, 2.0),
    Note("G", 5, 2.0),
    Note("C", 5, 2.0),
    Note("E", 5, 2.0),
    Note("C", 5, 2.0),
    Note("F", 5, 2.0),
    Note("A", 5, 2.0),
    Note("D", 5, 2.0),
    Note("F", 5, 2.0),
    Note("B", 4, 2.0),
    Note("C", 5, 2.0),
    Note("A", 4, 2.0),
    Note("E", 5, 2.0),
    Note("F", 5, 2.0),
    Note("D", 5, 2.0),
    Note("B", 4, 2.0),
    Note("C", 5, 2.0),
    Note("E", 5, 2.0),
    Note("D", 5, 2.0),
    Note("E", 5, 2.0),
    Note("C", 5, 2.0),
    Note("C", 5, 4.0),
]
lead.extend(melody)

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
    "lead": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
