"""Jazz piano trio: walking bass + comp chords + brushed ride, Cm jazz."""

from code_music import Chord, Note, Song, Track

song = Song(title="jazz_piano_trio", bpm=176)
r = Note.rest

# Piano comping — Rhodes feel, swung 8ths
comp = song.add_track(Track(name="piano", instrument="rhodes", volume=0.65, swing=0.5, pan=-0.2))
for chord, shape, oct in [
    ("C", "min7", 3),
    ("F", "dom7", 3),
    ("A#", "maj7", 3),
    ("G", "dom7", 3),
] * 2:
    comp.add(Chord(chord, shape, oct, duration=2.0, velocity=0.65))

# Walking bass
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.8, pan=0.1))
walk = [
    Note("C", 2, 1.0),
    Note("D#", 2, 1.0),
    Note("G", 2, 1.0),
    Note("A#", 2, 1.0),
    Note("F", 2, 1.0),
    Note("A", 2, 1.0),
    Note("C", 3, 1.0),
    Note("D#", 3, 1.0),
    Note("A#", 1, 1.0),
    Note("D", 2, 1.0),
    Note("F", 2, 1.0),
    Note("A#", 2, 1.0),
    Note("G", 1, 1.0),
    Note("B", 1, 1.0),
    Note("D", 2, 1.0),
    Note("G", 2, 1.0),
]
bass.extend(walk * 2)

# Ride cymbal — swing pattern
ride = song.add_track(Track(name="ride", instrument="drums_ride", volume=0.45, swing=0.5))
pat = [Note("F", 5, 0.5), Note("F", 5, 0.25), Note("F", 5, 0.25)] * 4  # swing triplet feel
ride.extend(pat * 4)
