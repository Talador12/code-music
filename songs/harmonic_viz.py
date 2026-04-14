"""Harmonic Viz - generates a song and exports harmonic rhythm SVG."""

from code_music import Chord, Note, Song, Track, scale
from code_music.composition import to_harmonic_rhythm

song = Song(title="Harmonic Rhythm Demo", bpm=120, sample_rate=44100)

# Fast harmonic rhythm section (chord every beat)
fast = song.add_track(Track(name="fast_chords", instrument="piano", volume=0.45))
for root, shape in [
    ("C", "maj"),
    ("D", "min"),
    ("E", "min"),
    ("F", "maj"),
    ("G", "dom7"),
    ("A", "min"),
    ("B", "dim"),
    ("C", "maj"),
]:
    fast.add(Chord(root, shape, 4, duration=1.0, velocity=50))

# Slow harmonic rhythm section (chord every 4 beats)
slow = song.add_track(Track(name="slow_chords", instrument="pad", volume=0.35))
for root, shape in [("C", "maj7"), ("F", "maj7"), ("G", "dom7"), ("C", "maj")]:
    slow.add(Chord(root, shape, 3, duration=4.0, velocity=40))

# Melody
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.4, pan=0.2))
lead.extend(scale("C", "major", octave=5, length=16))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["C", "C", "F", "F", "G", "G", "C", "C"]:
    bass.add(Note(root, 2, 2.0, velocity=60))

svg = to_harmonic_rhythm(song)
print(f"  Harmonic rhythm SVG: {len(svg)} chars")
