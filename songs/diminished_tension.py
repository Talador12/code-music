"""Diminished Tension - suspenseful piece using diminished scale and chords."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Diminished Tension", bpm=100, sample_rate=44100)

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.15))
lead.extend(scale("C", "diminished", octave=5, length=16))

chords = song.add_track(Track(name="chords", instrument="piano", volume=0.4))
for root, shape in [("C", "dim7"), ("Db", "dim7"), ("D", "dim7"), ("Eb", "dim7")] * 2:
    chords.add(Chord(root, shape, 4, duration=2.0, velocity=55))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.45))
for root in ["C", "Db", "D", "Eb"] * 2:
    bass.add(Note(root, 2, 2.0, velocity=60))

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
for _ in range(16):
    kick.add(Note("C", 4, 1.0, velocity=70))
