"""Synth Lab — all instruments designed from scratch with SoundDesigner.

A dark, pulsing electronic track built entirely from raw oscillators,
noise, and filters. Zero built-in presets used.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    SoundDesigner,
    Track,
    delay,
    reverb,
)

# -- Custom instruments designed from scratch --------------------------------

kick = (
    SoundDesigner("sd_kick")
    .add_osc("sine", volume=1.0)
    .envelope(attack=0.001, decay=0.3, sustain=0.0, release=0.15)
    .pitch_envelope(start_multiplier=6.0, end_multiplier=1.0, duration=0.03)
    .filter("lowpass", cutoff=250, resonance=0.6)
)

snare = (
    SoundDesigner("sd_snare")
    .add_osc("triangle", volume=0.5)
    .noise("white", volume=0.7, seed=77)
    .envelope(attack=0.001, decay=0.12, sustain=0.0, release=0.08)
    .filter("bandpass", cutoff=2500, resonance=1.2)
)

hat = (
    SoundDesigner("sd_hat")
    .noise("white", volume=0.8, seed=13)
    .envelope(attack=0.001, decay=0.04, sustain=0.0, release=0.02)
    .filter("highpass", cutoff=7000, resonance=0.8)
)

bass = (
    SoundDesigner("sd_bass")
    .add_osc("sawtooth", volume=0.7)
    .add_osc("square", detune_cents=-12, volume=0.3)
    .envelope(attack=0.005, decay=0.2, sustain=0.5, release=0.2)
    .filter("lowpass", cutoff=400, resonance=1.0)
)

pad = (
    SoundDesigner("sd_pad")
    .add_osc("sawtooth", detune_cents=0, volume=0.3)
    .add_osc("sawtooth", detune_cents=5, volume=0.25)
    .add_osc("sawtooth", detune_cents=-5, volume=0.25)
    .add_osc("triangle", detune_cents=0, volume=0.2)
    .envelope(attack=0.3, decay=0.2, sustain=0.5, release=0.8)
    .filter("lowpass", cutoff=2500, resonance=0.7)
    .lfo("filter_cutoff", rate=0.25, depth=0.4)
)

lead = (
    SoundDesigner("sd_lead")
    .add_osc("sawtooth", volume=0.5)
    .add_osc("square", detune_cents=7, volume=0.3)
    .envelope(attack=0.01, decay=0.08, sustain=0.6, release=0.3)
    .filter("lowpass", cutoff=3500, resonance=1.5)
    .lfo("filter_cutoff", rate=3.0, depth=0.3)
)

# -- Song --------------------------------------------------------------------

song = Song(title="Synth Lab", bpm=130, sample_rate=44100)

for name, designer in [
    ("sd_kick", kick),
    ("sd_snare", snare),
    ("sd_hat", hat),
    ("sd_bass", bass),
    ("sd_pad", pad),
    ("sd_lead", lead),
]:
    song.register_instrument(name, designer)

# Kick: four-on-the-floor
tr_kick = song.add_track(Track(name="kick", instrument="sd_kick", volume=0.8))
for _ in range(16):
    tr_kick.add(Note("C", 2, 1.0))

# Snare: beats 2 and 4
tr_snare = song.add_track(Track(name="snare", instrument="sd_snare", volume=0.6))
for _ in range(8):
    tr_snare.add(Note.rest(1.0))
    tr_snare.add(Note("D", 4, 1.0))

# Hi-hat: eighth notes
tr_hat = song.add_track(Track(name="hat", instrument="sd_hat", volume=0.35))
for _ in range(32):
    tr_hat.add(Note("F#", 6, 0.5))

# Bass line
tr_bass = song.add_track(Track(name="bass", instrument="sd_bass", volume=0.65, pan=0.0))
bass_notes = ["C", "C", "Eb", "F", "C", "C", "Ab", "G"]
for n in bass_notes:
    tr_bass.add(Note(n, 2, 2.0))

# Pad: slow chords
tr_pad = song.add_track(Track(name="pad", instrument="sd_pad", volume=0.35, pan=-0.15))
tr_pad.add(Chord("C", "min7", 3, duration=8.0))
tr_pad.add(Chord("Ab", "maj7", 3, duration=8.0))

# Lead melody
tr_lead = song.add_track(Track(name="lead", instrument="sd_lead", volume=0.45, pan=0.2))
melody = [
    ("C", 5),
    ("Eb", 5),
    ("G", 5),
    ("Bb", 5),
    ("Ab", 5),
    ("G", 5),
    ("Eb", 5),
    ("C", 5),
    ("Bb", 4),
    ("G", 4),
    ("Ab", 4),
    ("Bb", 4),
    ("C", 5),
    ("Eb", 5),
    ("F", 5),
    ("G", 5),
]
for note, oct in melody:
    tr_lead.add(Note(note, oct, 1.0))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
    "lead": EffectsChain().add(delay, delay_ms=230, feedback=0.3, wet=0.2),
}
