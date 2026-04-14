"""Pentatonic Jam - minor pentatonic improvisation over a blues backing."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Pentatonic Jam", bpm=96, sample_rate=44100)

# 12-bar blues backing
blues_prog = (
    [("A", "dom7")] * 4
    + [("D", "dom7")] * 2
    + [("A", "dom7")] * 2
    + [
        ("E", "dom7"),
        ("D", "dom7"),
        ("A", "dom7"),
        ("E", "dom7"),
    ]
)

chords = song.add_track(Track(name="chords", instrument="piano", volume=0.4, pan=-0.15))
for root, shape in blues_prog:
    chords.add(Chord(root, shape, 3, duration=2.0, velocity=50))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root, _ in blues_prog:
    bass.add(Note(root, 2, 2.0, velocity=65))

# Lead: pentatonic minor runs
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.2))
lead.extend(scale("A", "pentatonic_minor", octave=5, length=24))

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
for _ in range(24):
    kick.add(Note("C", 4, 1.0, velocity=75))
