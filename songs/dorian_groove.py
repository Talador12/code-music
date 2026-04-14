"""Dorian Groove - funky Dorian mode with tight rhythm section."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Dorian Groove", bpm=108, sample_rate=44100)

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.2, swing=0.08))
lead.extend(scale("D", "dorian", octave=5, length=32))

chords = song.add_track(Track(name="chords", instrument="piano", volume=0.35, pan=-0.15, swing=0.1))
for root, shape in [("D", "min7"), ("G", "dom7"), ("D", "min7"), ("A", "min7")] * 4:
    chords.add(Chord(root, shape, 4, duration=2.0, velocity=50))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55, swing=0.08))
for root in ["D", "D", "G", "G", "D", "D", "A", "A"] * 2:
    bass.add(Note(root, 2, 1.0, velocity=65))
    bass.add(Note(root, 3, 0.5, velocity=55))
    bass.add(Note.rest(0.5))

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
for _ in range(32):
    kick.add(Note("C", 4, 1.0, velocity=80))

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25, swing=0.1))
for _ in range(64):
    hat.add(Note("C", 6, 0.5, velocity=35))
