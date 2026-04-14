"""Phrygian Metal - dark Phrygian mode with heavy drums."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Phrygian Metal", bpm=160, sample_rate=44100)

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.2))
lead.extend(scale("E", "phrygian", octave=4, length=32))

rhythm = song.add_track(Track(name="rhythm", instrument="sawtooth", volume=0.45, pan=-0.3))
for root in ["E", "F", "G", "E"] * 4:
    rhythm.add(Chord(root, "5", 3, duration=2.0, velocity=75))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for root in ["E", "F", "G", "E"] * 4:
    bass.add(Note(root, 1, 2.0, velocity=75))

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
for _ in range(32):
    kick.add(Note("C", 4, 0.5, velocity=90))
    kick.add(Note("C", 4, 0.5, velocity=70))

snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.6))
for _ in range(16):
    snare.add(Note.rest(1.0))
    snare.add(Note("C", 4, 1.0, velocity=80))
