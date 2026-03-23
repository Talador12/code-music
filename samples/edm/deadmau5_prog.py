"""Deadmau5-style progressive house: slow chord evolution, no drums.

Deadmau5 signature: simple looping chord progression,
slowly filtering pad that builds tension over 8+ bars, minimal.
"""

from code_music import Chord, Note, Song, Track

song = Song(title="deadmau5_prog", bpm=128)
r = Note.rest

# Chord loop: Fm - Db - Ab - Eb  (classic mau5 key — Fm)
LOOP = [
    ("F", "min7"),
    ("C#", "maj7"),
    ("G#", "maj7"),
    ("D#", "dom7"),
]
# Supersaw pad — the main element
pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.55, pan=-0.1))
for root, shape in LOOP * 3:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=0.6))

# Subtle pluck arp over the top
arp = song.add_track(Track(name="arp", instrument="pluck", volume=0.35, pan=0.4))
for root, _ in LOOP * 3:
    # Simple root arpeggio
    for oct in [4, 5, 5, 4]:
        arp.add(Note(root, oct, 1.0, velocity=0.5))
