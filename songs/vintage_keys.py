"""Vintage Keys - Rhodes piano + Hammond organ jazz combo."""

import code_music.packs.vintage  # noqa: F401 - registers vintage instruments
from code_music import Chord, Note, Song, Track, scale

song = Song(title="Vintage Keys", bpm=120, sample_rate=44100)

# Rhodes electric piano
from code_music.packs.vintage import vintage_epiano

song.register_instrument("vintage_epiano", vintage_epiano)

epiano = song.add_track(Track(name="epiano", instrument="vintage_epiano", volume=0.5, pan=0.15))
for root, shape in [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "dom7")] * 4:
    epiano.add(Chord(root, shape, 4, duration=2.0, velocity=55))

# Hammond organ
from code_music.packs.vintage import vintage_organ

song.register_instrument("vintage_organ", vintage_organ)

organ = song.add_track(Track(name="organ", instrument="vintage_organ", volume=0.35, pan=-0.2))
for root, shape in [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "dom7")] * 4:
    organ.add(Chord(root, shape, 3, duration=2.0, velocity=40))

# Bass
from code_music.packs.vintage import vintage_bass

song.register_instrument("vintage_bass", vintage_bass)

bass = song.add_track(Track(name="bass", instrument="vintage_bass", volume=0.5))
for root in ["D", "G", "C", "A"] * 8:
    bass.add(Note(root, 2, 1.0, velocity=65))

# Lead
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.4, pan=0.2))
lead.extend(scale("D", "dorian", octave=5, length=32))
