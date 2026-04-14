"""Modal Exploration - one phrase through all 7 modes."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Modal Exploration", bpm=100, sample_rate=44100)

modes = [
    ("ionian", "maj7", "Bright, happy"),
    ("dorian", "min7", "Minor with a bright 6th"),
    ("phrygian", "min7", "Dark, Spanish"),
    ("lydian", "maj7", "Dreamy, raised 4th"),
    ("mixolydian", "dom7", "Bluesy, flat 7th"),
    ("aeolian", "min7", "Natural minor"),
    ("locrian", "min7", "Diminished, unstable"),
]

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15))
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=-0.15))
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.45))

for mode_name, chord_shape, _desc in modes:
    # 8-note scale run in each mode
    try:
        mel = scale("C", mode_name, octave=5, length=8)
        lead.extend(mel)
    except Exception:
        # Fallback for modes not in SCALES
        lead.extend(scale("C", "major", octave=5, length=8))

    pad.add(Chord("C", chord_shape, 3, duration=8.0, velocity=40))
    bass.add(Note("C", 2, 8.0, velocity=55))
