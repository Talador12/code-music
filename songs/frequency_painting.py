"""Frequency Painting — spectral shift and smear create an evolving soundscape."""

from code_music import EffectsChain, Note, Pattern, Song, SoundDesigner, Track, euclid, reverb
from code_music.sound_design import spectral_shift, spectral_smear

layer_up = (
    SoundDesigner("layer_up")
    .add_osc("sawtooth", volume=0.4)
    .spectral(spectral_shift(12.0))
    .envelope(attack=0.2, decay=0.1, sustain=0.5, release=0.5)
    .filter("lowpass", cutoff=3000, resonance=0.6)
)
layer_down = (
    SoundDesigner("layer_down")
    .add_osc("sawtooth", volume=0.4)
    .spectral(spectral_shift(-12.0))
    .envelope(attack=0.2, decay=0.1, sustain=0.5, release=0.5)
    .filter("lowpass", cutoff=1500, resonance=0.6)
)
smear_pad = (
    SoundDesigner("smear_pad")
    .add_osc("triangle", volume=0.4)
    .add_osc("sine", volume=0.3)
    .spectral(spectral_smear(0.8))
    .envelope(attack=0.6, decay=0.3, sustain=0.4, release=1.0)
)

song = Song(title="Frequency Painting", bpm=75, sample_rate=44100)
for name, d in [("layer_up", layer_up), ("layer_down", layer_down), ("smear_pad", smear_pad)]:
    song.register_instrument(name, d)

# Shifted layers create octave doubling effect
tr_up = song.add_track(Track(name="up", instrument="layer_up", volume=0.35, pan=0.15))
tr_down = song.add_track(Track(name="down", instrument="layer_down", volume=0.35, pan=-0.15))
pat = Pattern("A4 C5 E5 G5 F5 E5 C5 D5")
for _ in range(2):
    tr_up.extend(pat.to_notes(1.0))
    tr_down.extend(pat.to_notes(1.0))

# Smeared pad bed
tr_pad = song.add_track(Track(name="pad", instrument="smear_pad", volume=0.25))
tr_pad.add(Note("A", 3, 16.0))

# Euclidean kick
tr_kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.5))
for _ in range(4):
    tr_kick.extend(euclid(3, 8, "C", 2, 0.5))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "up": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
}
