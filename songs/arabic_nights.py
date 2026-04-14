"""Arabic Nights - double harmonic scale (maqam hijaz) with ornamental melody."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Arabic Nights", bpm=85, sample_rate=44100)

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.15))
lead.extend(scale("D", "arabic", octave=5, length=14))
lead.extend(scale("D", "arabic", octave=5, length=14))

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=-0.1))
for root, shape in [("D", "min"), ("Eb", "maj"), ("A", "dom7"), ("D", "min")] * 2:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=40))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.45))
for root in ["D", "Eb", "A", "D"] * 2:
    bass.add(Note(root, 2, 4.0, velocity=55))

# Tambourine-like hat
hat = song.add_track(Track(name="tambourine", instrument="drums_hat", volume=0.2))
for _ in range(32):
    hat.add(Note("C", 6, 0.5, velocity=30))
    hat.add(Note("C", 6, 0.5, velocity=20))
