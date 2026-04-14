"""Bebop Run - fast bebop dominant scale over ii-V-I changes."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Bebop Run", bpm=200, sample_rate=44100)

# Fast bebop lead
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.2, swing=0.1))
lead.extend(scale("C", "bebop_dominant", octave=5, length=32))

# ii-V-I comping
chords = song.add_track(
    Track(name="chords", instrument="piano", volume=0.35, pan=-0.15, swing=0.15)
)
for root, shape in [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("C", "maj7")] * 4:
    chords.add(Chord(root, shape, 4, duration=2.0, velocity=45))

# Walking bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5, swing=0.1))
for root in ["D", "F", "G", "B", "C", "E", "C", "G"] * 2:
    bass.add(Note(root, 2, 1.0, velocity=65))

# Ride cymbal
hat = song.add_track(Track(name="ride", instrument="drums_hat", volume=0.2, swing=0.15))
for _ in range(32):
    hat.add(Note("C", 6, 0.5, velocity=30))
    hat.add(Note("C", 6, 0.5, velocity=25))
