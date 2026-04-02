"""Example 11: Sound Design — build instruments from raw oscillators.

No WAV files, no external libraries. Design sounds from sine/saw/square/triangle
oscillators, noise generators, filters, LFOs, and envelopes. Then use them in
any song at any pitch, just like built-in presets.

Run:
    code-music examples/11_sound_design.py --play
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
    scale,
)

# ---------------------------------------------------------------------------
# Step 1: Design a supersaw lead — 5 detuned sawtooths through a lowpass
# ---------------------------------------------------------------------------

my_supersaw = (
    SoundDesigner("my_supersaw")
    .add_osc("sawtooth", detune_cents=0, volume=0.3)
    .add_osc("sawtooth", detune_cents=10, volume=0.25)
    .add_osc("sawtooth", detune_cents=-10, volume=0.25)
    .add_osc("sawtooth", detune_cents=20, volume=0.15)
    .add_osc("sawtooth", detune_cents=-20, volume=0.15)
    .envelope(attack=0.02, decay=0.1, sustain=0.7, release=0.4)
    .filter("lowpass", cutoff=4000, resonance=0.6)
)

# ---------------------------------------------------------------------------
# Step 2: Design a sub bass — pitch-dropping sine (808-style)
# ---------------------------------------------------------------------------

my_808 = (
    SoundDesigner("my_808")
    .add_osc("sine", volume=1.0)
    .envelope(attack=0.001, decay=0.5, sustain=0.0, release=0.3)
    .pitch_envelope(start_multiplier=3.5, end_multiplier=1.0, duration=0.04)
    .filter("lowpass", cutoff=180, resonance=0.9)
)

# ---------------------------------------------------------------------------
# Step 3: Design a wobble pad — filtered saw with LFO on cutoff
# ---------------------------------------------------------------------------

my_wobble = (
    SoundDesigner("my_wobble")
    .add_osc("sawtooth", detune_cents=0, volume=0.4)
    .add_osc("sawtooth", detune_cents=5, volume=0.3)
    .add_osc("sawtooth", detune_cents=-5, volume=0.3)
    .envelope(attack=0.2, decay=0.1, sustain=0.6, release=0.5)
    .filter("lowpass", cutoff=2000, resonance=1.5)
    .lfo("filter_cutoff", rate=0.4, depth=0.6)
)

# ---------------------------------------------------------------------------
# Step 4: Register instruments and build a song
# ---------------------------------------------------------------------------

song = Song(title="Sound Design Demo", bpm=128, sample_rate=22050)

# Register our custom instruments — now usable as Track(instrument="my_supersaw")
song.register_instrument("my_supersaw", my_supersaw)
song.register_instrument("my_808", my_808)
song.register_instrument("my_wobble", my_wobble)

# Sub bass
bass = song.add_track(Track(name="bass", instrument="my_808", volume=0.7))
for _ in range(4):
    bass.add(Note("C", 2, 2.0))
    bass.add(Note("C", 2, 2.0))

# Wobble pad
pad = song.add_track(Track(name="pad", instrument="my_wobble", volume=0.4, pan=-0.2))
pad.add(Chord("C", "min7", 3, duration=8.0))
pad.add(Chord("Ab", "maj7", 3, duration=8.0))

# Supersaw lead
lead = song.add_track(Track(name="lead", instrument="my_supersaw", volume=0.5, pan=0.2))
lead.extend(scale("C", "pentatonic_minor", octave=5, length=8))
lead.extend(scale("Ab", "pentatonic", octave=5, length=8))

# Effects on the built-in effects chain
song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.35),
    "lead": EffectsChain().add(delay, delay_ms=375, feedback=0.25, wet=0.2),
}

# ---------------------------------------------------------------------------
# Step 5: Serialization — save your design as JSON and reload it
# ---------------------------------------------------------------------------

# SoundDesigner supports full round-trip serialization:
#   data = my_supersaw.to_dict()       # → JSON-compatible dict
#   restored = SoundDesigner.from_dict(data)
#
# You can also render directly to a WAV file:
#   my_supersaw.to_wav("supersaw_c4.wav", freq=261.63, duration=2.0)
