"""Cinematic Trailer - epic brass, strings, choir, and timpani."""

import code_music.packs.cinematic  # noqa: F401, E402
from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale
from code_music.packs.cinematic import (
    celeste,
    choir_epic,
    cinematic_pad,
    epic_brass,
    epic_strings,
    timpani,
    trailer_hit,
)

song = Song(title="Cinematic Trailer", bpm=72, sample_rate=44100)
song.register_instrument("epic_brass", epic_brass)
song.register_instrument("epic_strings", epic_strings)
song.register_instrument("cinematic_pad", cinematic_pad)
song.register_instrument("trailer_hit", trailer_hit)
song.register_instrument("choir_epic", choir_epic)
song.register_instrument("timpani", timpani)
song.register_instrument("celeste", celeste)

# Strings intro
strings = song.add_track(Track(name="strings", instrument="epic_strings", volume=0.5))
for root, shape in [("D", "min"), ("Bb", "maj"), ("C", "dom7"), ("D", "min")] * 2:
    strings.add(Chord(root, shape, 3, duration=4.0, velocity=50))

# Brass enters
brass = song.add_track(Track(name="brass", instrument="epic_brass", volume=0.45, pan=0.1))
brass.add(Note.rest(8.0))
for root in ["D", "F", "A", "D", "Bb", "C", "D", "D"]:
    brass.add(Note(root, 4, 2.0, velocity=65))

# Epic choir
choir = song.add_track(Track(name="choir", instrument="choir_epic", volume=0.4))
choir.add(Note.rest(16.0))
for root, shape in [("D", "min"), ("Bb", "maj"), ("C", "dom7"), ("D", "min")]:
    choir.add(Chord(root, shape, 4, duration=4.0, velocity=55))

# Timpani hits
timp = song.add_track(Track(name="timpani", instrument="timpani", volume=0.6))
timp.add(Note.rest(16.0))
for _ in range(8):
    timp.add(Note("D", 2, 2.0, velocity=75))

# Celeste top
cel = song.add_track(Track(name="celeste", instrument="celeste", volume=0.3, pan=-0.2))
cel.extend(scale("D", "minor", octave=6, length=32))

# Cinematic pad underneath
pad = song.add_track(Track(name="pad", instrument="cinematic_pad", volume=0.25))
pad.add(Chord("D", "min", 2, duration=32.0, velocity=30))

song.effects = {
    "strings": EffectsChain().add(reverb, room_size=0.8, wet=0.35),
    "brass": EffectsChain().add(reverb, room_size=0.7, wet=0.25),
    "choir": EffectsChain().add(reverb, room_size=0.9, wet=0.4),
}
