"""Neapolitan - the bII chord and its dramatic resolution."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Neapolitan Resolution", bpm=80, sample_rate=44100)

progression = [
    ("C", "min"),
    ("Db", "maj"),
    ("G", "dom7"),
    ("C", "min"),
    ("C", "min"),
    ("Db", "maj"),
    ("G", "dom7"),
    ("C", "maj"),  # picardy third
]

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4))
for root, shape in progression:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=45))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root, _ in progression:
    bass.add(Note(root, 2, 4.0, velocity=60))

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.45, pan=0.1))
lead.extend(scale("C", "harmonic_minor", octave=5, length=16))
lead.extend(scale("C", "major", octave=5, length=16))
