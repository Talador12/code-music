"""Octave Doubling — melody doubled at the octave for orchestral weight."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import double_at_octave

song = Song(title="Octave Doubling", bpm=90)

melody = [
    Note("C", 5, 1.0),
    Note("E", 5, 1.0),
    Note("G", 5, 1.0),
    Note("C", 6, 1.0),
    Note("B", 5, 1.0),
    Note("A", 5, 1.0),
    Note("G", 5, 1.0),
    Note("E", 5, 1.0),
    Note("F", 5, 2.0),
    Note("E", 5, 2.0),
    Note("D", 5, 1.0),
    Note("E", 5, 1.0),
    Note("C", 5, 2.0),
]

# Original melody
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.1))
lead.extend(melody)

# Doubled one octave below
doubled = double_at_octave(melody, direction=-1)
low = song.add_track(Track(name="low", instrument="organ", volume=0.35, pan=-0.1))
low.extend(doubled)

# Pad
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=0.0))
pad.add(Chord("C", "maj", 3, duration=8.0))
pad.add(Chord("F", "maj", 3, duration=8.0))

song.effects = {
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
    "low": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
