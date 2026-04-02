"""Example 12: FM Synthesis, Wavetable Synthesis, and Euclidean Rhythms.

Three advanced techniques in one example:
- FM synthesis: frequency modulation creates complex timbres from simple sines
- Wavetable synthesis: custom single-cycle waveforms for unique timbres
- Euclidean rhythms: algorithmically-perfect beat distribution

Run:
    code-music examples/12_fm_and_wavetables.py --play
"""

from code_music import (
    Chord,
    EffectsChain,
    Song,
    SoundDesigner,
    Track,
    Wavetable,
    delay,
    euclid,
    reverb,
)

# ---------------------------------------------------------------------------
# Step 1: FM synthesis — electric piano (DX7-style)
# ---------------------------------------------------------------------------

# Two FM operators: carrier:modulator ratio of 2:1 creates even harmonics
epiano = (
    SoundDesigner("epiano")
    .fm("sine", mod_ratio=2.0, mod_index=3.5, volume=0.8)
    .fm("sine", mod_ratio=1.0, mod_index=0.5, volume=0.2)  # subtle warmth
    .envelope(attack=0.005, decay=0.4, sustain=0.2, release=0.5)
    .filter("lowpass", cutoff=4000, resonance=0.3)
)

# FM bell — inharmonic ratio (sqrt(2)) creates metallic partials
bell = (
    SoundDesigner("bell")
    .fm("sine", mod_ratio=1.414, mod_index=8.0, volume=0.7)
    .envelope(attack=0.001, decay=1.0, sustain=0.0, release=0.8)
)

# ---------------------------------------------------------------------------
# Step 2: Wavetable synthesis — build custom waveforms from harmonics
# ---------------------------------------------------------------------------

# Organ-like wavetable: fundamental + odd harmonics
organ_table = Wavetable.from_harmonics([1.0, 0.5, 0.0, 0.25, 0.0, 0.125])

organ = (
    SoundDesigner("organ")
    .add_wavetable(organ_table, volume=0.5)
    .add_wavetable(organ_table, volume=0.4, detune_cents=5)
    .add_wavetable(organ_table, volume=0.4, detune_cents=-5)
    .envelope(attack=0.02, decay=0.05, sustain=0.8, release=0.3)
)

# Morph between two wave shapes for a unique pad
saw_wt = Wavetable.from_wave("sawtooth")
square_wt = Wavetable.from_wave("square")
hybrid = saw_wt.morph(square_wt, 0.4)  # 40% toward square

morph_pad = (
    SoundDesigner("morph_pad")
    .add_wavetable(hybrid, volume=0.4)
    .add_wavetable(hybrid, volume=0.3, detune_cents=3)
    .add_wavetable(hybrid, volume=0.3, detune_cents=-3)
    .envelope(attack=0.3, decay=0.2, sustain=0.5, release=0.6)
    .filter("lowpass", cutoff=2500, resonance=0.6)
    .lfo("filter_cutoff", rate=0.3, depth=0.3)
)

# ---------------------------------------------------------------------------
# Step 3: Build a song with Euclidean rhythms
# ---------------------------------------------------------------------------

song = Song(title="FM & Wavetables", bpm=110, sample_rate=22050)

# Register custom instruments
for name, designer in [
    ("epiano", epiano),
    ("bell", bell),
    ("organ", organ),
    ("morph_pad", morph_pad),
]:
    song.register_instrument(name, designer)

# Morph pad: sustained chords
pad = song.add_track(Track(name="pad", instrument="morph_pad", volume=0.35, pan=-0.15))
pad.add(Chord("D", "min7", 3, duration=8.0))
pad.add(Chord("G", "dom7", 3, duration=8.0))

# FM electric piano: chords with Euclidean rhythm
keys = song.add_track(Track(name="keys", instrument="epiano", volume=0.5))
# 5 hits in 8 slots — a syncopated groove
keys.extend(euclid(5, 8, "D", 4, 1.0))
keys.extend(euclid(5, 8, "G", 4, 1.0))

# Organ: bass line with tresillo rhythm (3 in 8)
bass = song.add_track(Track(name="bass", instrument="organ", volume=0.5))
bass.extend(euclid(3, 8, "D", 2, 1.0))
bass.extend(euclid(3, 8, "G", 2, 1.0))

# FM bell: sparse accents
bells = song.add_track(Track(name="bells", instrument="bell", volume=0.3, pan=0.2))
bells.extend(euclid(2, 8, "D", 6, 1.0))
bells.extend(euclid(2, 8, "B", 5, 1.0))

# Effects
song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
    "bells": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "keys": EffectsChain().add(delay, delay_ms=272, feedback=0.2, wet=0.15),
}
