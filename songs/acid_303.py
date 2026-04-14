"""Acid 303 - acid bass preset with resonant filter sweep."""

from code_music import Chord, EffectsChain, Note, Song, Track, distortion
from code_music.sound_design import acid_bass

song = Song(title="Acid 303", bpm=132, sample_rate=44100)
song.register_instrument("acid_bass", acid_bass)

acid = song.add_track(Track(name="acid", instrument="acid_bass", volume=0.55))
for note in ["A", "A", "C", "A", "D", "C", "A", "E"] * 4:
    acid.add(Note(note, 2, 0.5, velocity=75))
    acid.add(Note.rest(0.5))

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
for _ in range(32):
    kick.add(Note("C", 4, 1.0, velocity=85))

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25))
for _ in range(64):
    hat.add(Note("C", 6, 0.5, velocity=35))

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.25))
for root, shape in [("A", "min"), ("F", "maj"), ("G", "dom7"), ("A", "min")] * 4:
    pad.add(Chord(root, shape, 3, duration=2.0, velocity=35))

song.effects = {"acid": EffectsChain().add(distortion, drive=0.35, wet=0.3)}
