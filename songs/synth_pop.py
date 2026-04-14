"""Synth Pop - vintage lead + pad with modern drum programming."""

import code_music.packs.vintage  # noqa: F401
from code_music import Chord, Clip, Note, Song, Track, scale
from code_music.packs.vintage import vintage_lead, vintage_pad

song = Song(title="Synth Pop", bpm=118, sample_rate=44100)
song.register_instrument("vintage_lead", vintage_lead)
song.register_instrument("vintage_pad", vintage_pad)

# Pad
pad = song.add_track(Track(name="pad", instrument="vintage_pad", volume=0.35, pan=-0.15))
for root, shape in [("A", "min"), ("F", "maj"), ("C", "maj"), ("G", "maj")] * 4:
    pad.add(Chord(root, shape, 3, duration=2.0, velocity=45))

# Lead
lead = song.add_track(Track(name="lead", instrument="vintage_lead", volume=0.45, pan=0.2))
lead.extend(scale("A", "pentatonic_minor", octave=5, length=32))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["A", "F", "C", "G"] * 8:
    bass.add(Note(root, 2, 1.0, velocity=65))

# Drums from clip loop
kick_src = Track()
for _ in range(4):
    kick_src.add(Note("C", 4, 1.0, velocity=80))
kick_clip = Clip.from_track(kick_src)
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
kick.extend(kick_clip.loop(8).to_events())

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25))
for _ in range(64):
    hat.add(Note("C", 6, 0.5, velocity=35))
