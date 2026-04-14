"""Tape Dreams - lo-fi with tape saturation and wow/flutter."""

import code_music.packs.vintage  # noqa: F401
from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale
from code_music.packs.vintage import tape_saturation, vintage_pad, wow_flutter

song = Song(title="Tape Dreams", bpm=75, sample_rate=44100)
song.register_instrument("vintage_pad", vintage_pad)

# Lo-fi pad
pad = song.add_track(Track(name="pad", instrument="vintage_pad", volume=0.4))
for root, shape in [("F", "maj7"), ("A", "min7"), ("D", "min7"), ("G", "dom7")] * 2:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=40))

# Simple melody
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.4, pan=0.15))
lead.extend(scale("F", "major", octave=5, length=16))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.45))
for root in ["F", "A", "D", "G"] * 2:
    bass.add(Note(root, 2, 4.0, velocity=55))

# Apply tape effects
song.effects = {
    "pad": EffectsChain()
    .add(tape_saturation, drive=0.3, warmth=0.7, wet=0.6)
    .add(wow_flutter, wow_rate=0.4, wow_depth=0.001, wet=0.5)
    .add(reverb, room_size=0.7, wet=0.3),
    "lead": EffectsChain()
    .add(tape_saturation, drive=0.2, warmth=0.5, wet=0.4)
    .add(reverb, room_size=0.5, wet=0.2),
}
