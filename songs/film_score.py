"""film_score.py - Cinematic orchestral feel with strings and brass. Epic arc."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Film Score", bpm=72, sample_rate=44100)

r = Note.rest

# Strings - sustained chords, building
strings = song.add_track(Track(name="strings", instrument="pad", volume=0.5, pan=-0.1))
for root, shape, vel in [
    ("D", "min", 30),
    ("Bb", "maj", 35),
    ("G", "min", 40),
    ("A", "dom7", 50),
    ("D", "min", 45),
    ("F", "maj", 55),
    ("Bb", "maj", 60),
    ("A", "dom7", 65),
] * 2:
    strings.add(Chord(root, shape, 3, duration=8.0, velocity=vel))

# Brass - bold melody, enters halfway
brass = song.add_track(Track(name="brass", instrument="square", volume=0.4, pan=0.15))
brass.extend([r(64.0)])  # silence for first half
theme = [
    Note("D", 4, 2.0),
    Note("F", 4, 1.0),
    Note("A", 4, 3.0),
    r(2.0),
    Note("Bb", 4, 2.0),
    Note("A", 4, 1.0),
    Note("G", 4, 2.0),
    Note("F", 4, 1.0),
    r(2.0),
    Note("D", 4, 1.0),
    Note("E", 4, 1.0),
    Note("F", 4, 2.0),
    Note("A", 4, 4.0),
]
brass.extend(theme * 4)

# Cello bass - low sustained roots
cello = song.add_track(Track(name="cello", instrument="bass", volume=0.45))
for root in ["D", "Bb", "G", "A", "D", "F", "Bb", "A"] * 2:
    cello.add(Note(root, 2, 8.0, velocity=55))

# Timpani hits on key moments
timp = song.add_track(Track(name="timpani", instrument="drums_kick", volume=0.6))
timp.extend([r(64.0)])  # silence for first half
for _ in range(8):
    timp.extend([Note("D", 2, 1.0, velocity=80), r(7.0)])

song.effects = {
    "strings": EffectsChain().add(reverb, room_size=0.85, wet=0.45),
    "brass": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
    "cello": EffectsChain().add(reverb, room_size=0.6, wet=0.25),
}
