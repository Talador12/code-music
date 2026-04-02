"""Wavetable Drift — ambient textures from morphing wavetables.

Slow-evolving pads built from custom harmonic wavetables with detuning,
morphed waveforms, and LFO-swept filters.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    SoundDesigner,
    Track,
    Wavetable,
    reverb,
)

# -- Wavetable instruments ---------------------------------------------------

# Soft organ-like pad
_wt_soft = Wavetable.from_harmonics([1.0, 0.3, 0.0, 0.15, 0.0, 0.08])
soft_pad = (
    SoundDesigner("soft_pad")
    .add_wavetable(_wt_soft, volume=0.4)
    .add_wavetable(_wt_soft, volume=0.3, detune_cents=4)
    .add_wavetable(_wt_soft, volume=0.3, detune_cents=-4)
    .envelope(attack=0.8, decay=0.3, sustain=0.5, release=1.2)
    .filter("lowpass", cutoff=1500, resonance=0.4)
    .lfo("filter_cutoff", rate=0.12, depth=0.4)
)

# Morphed saw-to-triangle for a warm drone
_wt_morph = Wavetable.from_wave("sawtooth").morph(Wavetable.from_wave("triangle"), 0.6)
warm_drone = (
    SoundDesigner("warm_drone")
    .add_wavetable(_wt_morph, volume=0.5)
    .add_wavetable(_wt_morph, volume=0.3, detune_cents=2)
    .add_wavetable(_wt_morph, volume=0.3, detune_cents=-2)
    .envelope(attack=1.5, decay=0.5, sustain=0.6, release=2.0)
    .filter("lowpass", cutoff=400, resonance=0.6)
)

# Bright harmonic lead
_wt_bright = Wavetable.from_harmonics([1.0, 0.7, 0.5, 0.4, 0.3, 0.2, 0.15, 0.1])
bright_lead = (
    SoundDesigner("bright_lead")
    .add_wavetable(_wt_bright, volume=0.5)
    .add_wavetable(_wt_bright, volume=0.3, detune_cents=7)
    .envelope(attack=0.01, decay=0.15, sustain=0.5, release=0.4)
    .filter("lowpass", cutoff=4000, resonance=0.8)
    .lfo("filter_cutoff", rate=1.5, depth=0.25)
)

# Glass texture: square morphed into sine
_wt_glass = Wavetable.from_wave("square").morph(Wavetable.from_wave("sine"), 0.7)
glass_chime = (
    SoundDesigner("glass_chime")
    .add_wavetable(_wt_glass, volume=0.6)
    .envelope(attack=0.005, decay=0.6, sustain=0.0, release=0.4)
    .filter("bandpass", cutoff=3000, resonance=1.5)
)

# -- Song --------------------------------------------------------------------

song = Song(title="Wavetable Drift", bpm=55, sample_rate=44100)

for name, designer in [
    ("soft_pad", soft_pad),
    ("warm_drone", warm_drone),
    ("bright_lead", bright_lead),
    ("glass_chime", glass_chime),
]:
    song.register_instrument(name, designer)

# Drone
tr_drone = song.add_track(Track(name="drone", instrument="warm_drone", volume=0.25))
tr_drone.add(Note("C", 2, 16.0))
tr_drone.add(Note("Eb", 2, 16.0))

# Soft pad chords
tr_pad = song.add_track(Track(name="pad", instrument="soft_pad", volume=0.35, pan=-0.15))
tr_pad.add(Chord("C", "min9", 3, duration=8.0))
tr_pad.add(Chord("Ab", "maj7", 3, duration=8.0))
tr_pad.add(Chord("Eb", "maj", 3, duration=8.0))
tr_pad.add(Chord("Bb", "sus4", 3, duration=8.0))

# Glass chime accents
tr_chime = song.add_track(Track(name="chime", instrument="glass_chime", volume=0.3, pan=0.2))
chime_melody = [
    ("C", 6, 2.0),
    ("Eb", 6, 1.5),
    ("G", 6, 2.5),
    ("Bb", 6, 2.0),
    ("Ab", 6, 1.5),
    ("G", 6, 1.5),
    ("Eb", 6, 2.5),
    ("C", 6, 2.5),
    ("Bb", 5, 2.0),
    ("Ab", 5, 3.0),
    ("G", 5, 2.0),
    ("Eb", 5, 3.5),
]
for note_name, oct, dur in chime_melody:
    tr_chime.add(Note(note_name, oct, dur))

# Bright lead (enters halfway)
tr_lead = song.add_track(Track(name="lead", instrument="bright_lead", volume=0.35, pan=0.1))
tr_lead.add(Note.rest(16.0))
lead_notes = [("C", 5), ("Eb", 5), ("G", 5), ("Bb", 5), ("Ab", 5), ("G", 5), ("Eb", 5), ("C", 5)]
for note_name, oct in lead_notes:
    tr_lead.add(Note(note_name, oct, 2.0))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "chime": EffectsChain().add(reverb, room_size=0.85, wet=0.45),
    "drone": EffectsChain().add(reverb, room_size=0.75, wet=0.3),
    "lead": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
}
