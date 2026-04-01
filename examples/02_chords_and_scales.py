"""02 — Chords and scales: harmonic building blocks.

Run:  code-music examples/02_chords_and_scales.py --play
"""

from code_music import Chord, Song, Track, scale

song = Song(title="Chords and Scales", bpm=100)

# Chord progressions: Chord(root, shape, octave, duration)
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4))
pad.add(Chord("A", "min7", 3, duration=4.0))  # Am7
pad.add(Chord("D", "min7", 3, duration=4.0))  # Dm7
pad.add(Chord("G", "dom7", 3, duration=4.0))  # G7
pad.add(Chord("C", "maj7", 3, duration=4.0))  # Cmaj7

# scale() generates a list of notes in any scale/mode
# scale(root, mode, octave) — great for melodies
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.6))
lead.extend(scale("A", "pentatonic", octave=5, length=16))

# Available shapes: maj, min, dom7, maj7, min7, dim, aug, sus2, sus4, ...
# Available scales: major, minor, pentatonic, blues, dorian, mixolydian, ...
