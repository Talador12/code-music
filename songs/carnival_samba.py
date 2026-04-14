"""Carnival Samba - Brazilian samba rhythm with brass stabs."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Carnival Samba", bpm=108, sample_rate=44100)

# Surdo (bass drum pattern)
surdo = song.add_track(Track(name="surdo", instrument="drums_kick", volume=0.75))
pattern = [1, 0, 0, 1, 0, 0, 1, 0]
for _ in range(4):
    for hit in pattern:
        if hit:
            surdo.add(Note("C", 4, 0.5, velocity=80))
        else:
            surdo.add(Note.rest(0.5))

# Tamborim (hat)
tamb = song.add_track(Track(name="tamborim", instrument="drums_hat", volume=0.3))
for _ in range(32):
    tamb.add(Note("C", 6, 0.5, velocity=35))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55, swing=0.08))
for root in ["A", "D", "G", "A"] * 4:
    bass.add(Note(root, 2, 1.0, velocity=65))
    bass.add(Note(root, 3, 0.5, velocity=55))
    bass.add(Note.rest(0.5))

# Brass stabs
brass = song.add_track(Track(name="brass", instrument="square", volume=0.35, pan=0.2))
for root, shape in [("A", "min7"), ("D", "dom7"), ("G", "maj7"), ("A", "min")] * 2:
    brass.add(Note.rest(1.0))
    brass.add(Chord(root, shape, 4, duration=1.0, velocity=55))

# Melody
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.4, pan=-0.2))
lead.extend(scale("A", "pentatonic_minor", octave=5, length=16))
