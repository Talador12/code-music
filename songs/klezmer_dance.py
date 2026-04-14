"""Klezmer Dance - Eastern European folk with augmented second intervals."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Klezmer Dance", bpm=140, sample_rate=44100)

# Clarinet (sawtooth)
clarinet = song.add_track(Track(name="clarinet", instrument="sawtooth", volume=0.45, pan=0.15))
clarinet.extend(scale("D", "harmonic_minor", octave=5, length=16))
clarinet.extend(scale("D", "harmonic_minor", octave=5, length=16))

# Accordion chords
accordion = song.add_track(Track(name="accordion", instrument="organ", volume=0.35, pan=-0.15))
for root, shape in [("D", "min"), ("A", "dom7"), ("D", "min"), ("G", "min")] * 4:
    accordion.add(Chord(root, shape, 4, duration=2.0, velocity=50))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["D", "A", "D", "G"] * 4:
    bass.add(Note(root, 2, 1.0, velocity=65))
    bass.add(Note(root, 3, 0.5, velocity=55))
    bass.add(Note.rest(0.5))

# Drums: fast 2-beat
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
for _ in range(32):
    kick.add(Note("C", 4, 1.0, velocity=75))
