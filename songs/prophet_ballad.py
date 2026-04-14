"""Prophet Ballad - slow, emotional piece with vintage lead and strings."""

import code_music.packs.vintage  # noqa: F401
from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale
from code_music.packs.vintage import vintage_lead, vintage_strings

song = Song(title="Prophet Ballad", bpm=68, sample_rate=44100)
song.register_instrument("vintage_lead", vintage_lead)
song.register_instrument("vintage_strings", vintage_strings)

# Strings
strings = song.add_track(Track(name="strings", instrument="vintage_strings", volume=0.4))
for root, shape in [
    ("D", "min7"),
    ("Bb", "maj7"),
    ("C", "dom7"),
    ("F", "maj7"),
    ("D", "min7"),
    ("G", "min7"),
    ("A", "dom7"),
    ("D", "min"),
]:
    strings.add(Chord(root, shape, 3, duration=4.0, velocity=40))

# Lead melody
lead = song.add_track(Track(name="lead", instrument="vintage_lead", volume=0.45, pan=0.15))
lead.extend(scale("D", "dorian", octave=5, length=16))
lead.extend(scale("D", "minor", octave=5, length=16))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.45))
for root in ["D", "Bb", "C", "F", "D", "G", "A", "D"]:
    bass.add(Note(root, 2, 4.0, velocity=55))

song.effects = {
    "strings": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
}
