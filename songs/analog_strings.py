"""Analog Strings - vintage string ensemble from the Solina era."""

import code_music.packs.vintage  # noqa: F401
from code_music import Chord, Note, Song, Track
from code_music.packs.vintage import vintage_strings

song = Song(title="Analog Strings", bpm=66, sample_rate=44100)
song.register_instrument("vintage_strings", vintage_strings)

strings = song.add_track(Track(name="strings", instrument="vintage_strings", volume=0.5))
for root, shape in [
    ("C", "maj7"),
    ("A", "min7"),
    ("F", "maj7"),
    ("G", "dom7"),
    ("E", "min7"),
    ("A", "min7"),
    ("D", "min7"),
    ("G", "dom7"),
]:
    strings.add(Chord(root, shape, 3, duration=4.0, velocity=45))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.4))
for root in ["C", "A", "F", "G", "E", "A", "D", "G"]:
    bass.add(Note(root, 2, 4.0, velocity=50))
