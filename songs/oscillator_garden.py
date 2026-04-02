"""Oscillator Garden — ambient textures from custom-designed instruments.

Slow, evolving pad layers with LFO-modulated filters, gentle noise beds,
and a delicate sine lead. Every sound designed from scratch.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    SoundDesigner,
    Track,
    reverb,
)

# -- Custom instruments ------------------------------------------------------

warm_pad = (
    SoundDesigner("warm_pad")
    .add_osc("sine", detune_cents=0, volume=0.4)
    .add_osc("triangle", detune_cents=3, volume=0.3)
    .add_osc("triangle", detune_cents=-3, volume=0.3)
    .envelope(attack=0.8, decay=0.3, sustain=0.5, release=1.0)
    .filter("lowpass", cutoff=1200, resonance=0.5)
    .lfo("filter_cutoff", rate=0.15, depth=0.3)
)

breathy_noise = (
    SoundDesigner("breathy")
    .noise("pink", volume=0.6, seed=99)
    .add_osc("sine", volume=0.15)
    .envelope(attack=1.0, decay=0.5, sustain=0.3, release=1.5)
    .filter("bandpass", cutoff=600, resonance=1.0)
    .lfo("filter_cutoff", rate=0.1, depth=0.5)
)

glass_bell = (
    SoundDesigner("glass_bell")
    .add_osc("sine", volume=0.6)
    .add_osc("triangle", detune_cents=1200, volume=0.2)  # octave harmonic
    .add_osc("sine", detune_cents=1902, volume=0.1)  # 5th above octave
    .envelope(attack=0.005, decay=0.8, sustain=0.0, release=0.6)
    .filter("lowpass", cutoff=6000, resonance=0.3)
)

deep_drone = (
    SoundDesigner("deep_drone")
    .add_osc("sawtooth", volume=0.4)
    .add_osc("sawtooth", detune_cents=2, volume=0.3)
    .add_osc("sawtooth", detune_cents=-2, volume=0.3)
    .noise("brown", volume=0.1, seed=33)
    .envelope(attack=1.5, decay=0.5, sustain=0.6, release=2.0)
    .filter("lowpass", cutoff=300, resonance=0.8)
)

# -- Song --------------------------------------------------------------------

song = Song(title="Oscillator Garden", bpm=60, sample_rate=44100)

for name, designer in [
    ("warm_pad", warm_pad),
    ("breathy", breathy_noise),
    ("glass_bell", glass_bell),
    ("deep_drone", deep_drone),
]:
    song.register_instrument(name, designer)

# Deep drone: single sustained note
tr_drone = song.add_track(Track(name="drone", instrument="deep_drone", volume=0.3, pan=0.0))
tr_drone.add(Note("C", 2, 16.0))

# Warm pad: slow chords
tr_pad = song.add_track(Track(name="pad", instrument="warm_pad", volume=0.4, pan=-0.2))
tr_pad.add(Chord("C", "min9", 3, duration=8.0))
tr_pad.add(Chord("Ab", "maj7", 3, duration=8.0))

# Breathy texture
tr_breath = song.add_track(Track(name="breath", instrument="breathy", volume=0.2, pan=0.3))
tr_breath.add(Note("C", 4, 8.0))
tr_breath.add(Note("Eb", 4, 8.0))

# Glass bell: sparse melody
tr_bell = song.add_track(Track(name="bell", instrument="glass_bell", volume=0.5, pan=0.1))
bell_melody = [
    ("C", 5, 2.0),
    ("Eb", 5, 1.0),
    ("G", 5, 3.0),
    ("Bb", 5, 2.0),
    ("Ab", 5, 1.5),
    ("G", 5, 1.5),
    ("Eb", 5, 2.0),
    ("C", 5, 3.0),
]
for note, oct, dur in bell_melody:
    tr_bell.add(Note(note, oct, dur))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "bell": EffectsChain().add(reverb, room_size=0.85, wet=0.4),
    "breath": EffectsChain().add(reverb, room_size=0.95, wet=0.6),
    "drone": EffectsChain().add(reverb, room_size=0.7, wet=0.25),
}
