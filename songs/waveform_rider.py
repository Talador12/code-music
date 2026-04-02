"""Waveform Rider — aggressive electronic track, all custom-designed sounds.

Hard-hitting drums, growling bass, and a searing lead. Every instrument
built from oscillators and noise in SoundDesigner.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    SoundDesigner,
    Track,
    delay,
    distortion,
    reverb,
)

# -- Custom instruments ------------------------------------------------------

heavy_kick = (
    SoundDesigner("heavy_kick")
    .add_osc("sine", volume=1.0)
    .add_osc("triangle", detune_cents=-1200, volume=0.3)  # sub octave
    .envelope(attack=0.001, decay=0.35, sustain=0.0, release=0.15)
    .pitch_envelope(start_multiplier=8.0, end_multiplier=1.0, duration=0.025)
    .filter("lowpass", cutoff=200, resonance=0.7)
)

clap = (
    SoundDesigner("clap")
    .noise("white", volume=0.9, seed=55)
    .add_osc("square", volume=0.15, harmonics=3)
    .envelope(attack=0.001, decay=0.08, sustain=0.0, release=0.06)
    .filter("bandpass", cutoff=1800, resonance=1.5)
)

ride = (
    SoundDesigner("ride")
    .noise("white", volume=0.6, seed=21)
    .noise("pink", volume=0.3, seed=22)
    .envelope(attack=0.001, decay=0.15, sustain=0.05, release=0.1)
    .filter("highpass", cutoff=8000, resonance=0.5)
)

growl_bass = (
    SoundDesigner("growl_bass")
    .add_osc("sawtooth", volume=0.5)
    .add_osc("square", detune_cents=-5, volume=0.4)
    .add_osc("sawtooth", detune_cents=7, volume=0.3)
    .envelope(attack=0.005, decay=0.15, sustain=0.6, release=0.15)
    .filter("lowpass", cutoff=600, resonance=2.5)
    .lfo("filter_cutoff", rate=4.0, depth=0.5)
)

stab = (
    SoundDesigner("stab")
    .add_osc("sawtooth", volume=0.4)
    .add_osc("sawtooth", detune_cents=12, volume=0.3)
    .add_osc("sawtooth", detune_cents=-12, volume=0.3)
    .add_osc("square", detune_cents=7, volume=0.2)
    .envelope(attack=0.005, decay=0.1, sustain=0.3, release=0.2)
    .filter("lowpass", cutoff=3000, resonance=1.0)
)

screech_lead = (
    SoundDesigner("screech")
    .add_osc("sawtooth", volume=0.5)
    .add_osc("square", detune_cents=5, volume=0.4)
    .envelope(attack=0.01, decay=0.05, sustain=0.8, release=0.25)
    .filter("bandpass", cutoff=2000, resonance=3.0)
    .lfo("filter_cutoff", rate=6.0, depth=0.4)
)

# -- Song --------------------------------------------------------------------

song = Song(title="Waveform Rider", bpm=150, sample_rate=44100)

for name, designer in [
    ("heavy_kick", heavy_kick),
    ("clap", clap),
    ("ride", ride),
    ("growl_bass", growl_bass),
    ("stab", stab),
    ("screech", screech_lead),
]:
    song.register_instrument(name, designer)

# Kick: four-on-the-floor
tr_kick = song.add_track(Track(name="kick", instrument="heavy_kick", volume=0.85))
for _ in range(16):
    tr_kick.add(Note("C", 1, 1.0))

# Clap: 2 and 4
tr_clap = song.add_track(Track(name="clap", instrument="clap", volume=0.55))
for _ in range(8):
    tr_clap.add(Note.rest(1.0))
    tr_clap.add(Note("E", 5, 1.0))

# Ride: offbeat eighth notes
tr_ride = song.add_track(Track(name="ride", instrument="ride", volume=0.3))
for _ in range(16):
    tr_ride.add(Note.rest(0.5))
    tr_ride.add(Note("C", 7, 0.5))

# Growl bass
tr_bass = song.add_track(Track(name="bass", instrument="growl_bass", volume=0.6))
bass_pattern = [("E", 2, 1.5), ("E", 2, 0.5), ("G", 2, 1.0), ("A", 2, 1.0)]
for _ in range(4):
    for note, oct, dur in bass_pattern:
        tr_bass.add(Note(note, oct, dur))

# Chord stabs
tr_stab = song.add_track(Track(name="stab", instrument="stab", volume=0.4, pan=-0.15))
tr_stab.add(Chord("E", "min", 4, duration=0.5))
tr_stab.add(Note.rest(1.5))
tr_stab.add(Chord("E", "min", 4, duration=0.5))
tr_stab.add(Note.rest(1.5))
tr_stab.add(Chord("C", "maj", 4, duration=0.5))
tr_stab.add(Note.rest(1.5))
tr_stab.add(Chord("D", "maj", 4, duration=0.5))
tr_stab.add(Note.rest(1.5))
for _ in range(2):
    tr_stab.add(Chord("E", "min", 4, duration=0.5))
    tr_stab.add(Note.rest(1.5))
    tr_stab.add(Chord("E", "min", 4, duration=0.5))
    tr_stab.add(Note.rest(1.5))

# Screech lead
tr_lead = song.add_track(Track(name="lead", instrument="screech", volume=0.4, pan=0.15))
lead_notes = [
    ("E", 5),
    ("G", 5),
    ("B", 5),
    ("A", 5),
    ("G", 5),
    ("E", 5),
    ("D", 5),
    ("E", 5),
    ("B", 4),
    ("D", 5),
    ("E", 5),
    ("G", 5),
    ("A", 5),
    ("B", 5),
    ("G", 5),
    ("E", 5),
]
for note, oct in lead_notes:
    tr_lead.add(Note(note, oct, 1.0))

song.effects = {
    "bass": EffectsChain().add(distortion, drive=2.0, tone=0.4, wet=0.3),
    "stab": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
    "lead": EffectsChain().add(delay, delay_ms=200, feedback=0.25, wet=0.15),
}
