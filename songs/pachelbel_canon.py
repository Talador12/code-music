"""Pachelbel Canon - the most famous progression in classical music."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Pachelbel Canon", bpm=72, sample_rate=44100)

progression = [
    ("C", "maj"),
    ("G", "maj"),
    ("A", "min"),
    ("E", "min"),
    ("F", "maj"),
    ("C", "maj"),
    ("F", "maj"),
    ("G", "maj"),
]

# Strings (pad)
strings = song.add_track(Track(name="strings", instrument="pad", volume=0.4))
for root, shape in progression * 2:
    strings.add(Chord(root, shape, 3, duration=4.0, velocity=45))

# Cello bass
cello = song.add_track(Track(name="cello", instrument="bass", volume=0.45))
for root, _ in progression * 2:
    cello.add(Note(root, 2, 4.0, velocity=55))

# Violin 1 (lead melody)
v1 = song.add_track(Track(name="violin1", instrument="triangle", volume=0.4, pan=0.2))
v1.extend(scale("C", "major", octave=5, length=32))
v1.extend(scale("C", "major", octave=5, length=32))

# Violin 2 (canon - delayed by 8 beats)
v2 = song.add_track(Track(name="violin2", instrument="triangle", volume=0.35, pan=-0.2))
v2.add(Note.rest(8.0))
v2.extend(scale("C", "major", octave=5, length=32))
v2.extend(scale("C", "major", octave=5, length=24))
