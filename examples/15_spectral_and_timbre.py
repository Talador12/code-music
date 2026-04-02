"""Example 15: Spectral Processing and Timbre Analysis.

Two advanced techniques:
- Spectral: FFT-based manipulation (freeze, shift, smear) for otherworldly sounds
- Timbre: analyze, compare, and morph sound designs based on their spectral fingerprint

Run:
    code-music examples/15_spectral_and_timbre.py --play
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
from code_music.sound_design import spectral_freeze, spectral_shift, spectral_smear

# ---------------------------------------------------------------------------
# Step 1: Spectral freeze — sustain spectral content (drone-like)
# ---------------------------------------------------------------------------

frozen_saw = (
    SoundDesigner("frozen_saw")
    .add_osc("sawtooth", volume=0.5)
    .add_osc("sawtooth", detune_cents=5, volume=0.3)
    .spectral(spectral_freeze(0.85))
    .envelope(attack=0.3, decay=0.2, sustain=0.5, release=0.8)
    .filter("lowpass", cutoff=3000, resonance=0.5)
)

# ---------------------------------------------------------------------------
# Step 2: Spectral shift — transpose spectrum by semitones
# ---------------------------------------------------------------------------

shifted_pad = (
    SoundDesigner("shifted_pad")
    .add_osc("sawtooth", volume=0.4)
    .add_osc("triangle", detune_cents=3, volume=0.3)
    .spectral(spectral_shift(7.0))  # shift up a fifth
    .envelope(attack=0.4, decay=0.2, sustain=0.5, release=0.6)
    .filter("lowpass", cutoff=2500, resonance=0.4)
)

# ---------------------------------------------------------------------------
# Step 3: Spectral smear — blur frequencies for ghostly textures
# ---------------------------------------------------------------------------

smeared = (
    SoundDesigner("smeared")
    .add_osc("square", volume=0.4)
    .noise("pink", volume=0.1, seed=33)
    .spectral(spectral_smear(0.6))
    .envelope(attack=0.5, decay=0.3, sustain=0.4, release=1.0)
)

# ---------------------------------------------------------------------------
# Step 4: Timbre analysis — compare sounds
# ---------------------------------------------------------------------------

t_frozen = frozen_saw.analyze()
t_shifted = shifted_pad.analyze()
t_smeared = smeared.analyze()

print(f"Frozen saw:  {t_frozen}")
print(f"Shifted pad: {t_shifted}")
print(f"Smeared sq:  {t_smeared}")
print(f"Distance frozen↔shifted: {t_frozen.distance(t_shifted):.3f}")
print(f"Distance frozen↔smeared: {t_frozen.distance(t_smeared):.3f}")

# ---------------------------------------------------------------------------
# Step 5: Build a song
# ---------------------------------------------------------------------------

song = Song(title="Spectral & Timbre", bpm=70, sample_rate=22050)

for name, designer in [
    ("frozen_saw", frozen_saw),
    ("shifted_pad", shifted_pad),
    ("smeared", smeared),
]:
    song.register_instrument(name, designer)

# Frozen saw drone
tr_drone = song.add_track(Track(name="drone", instrument="frozen_saw", volume=0.35))
tr_drone.add(Note("C", 3, 16.0))

# Shifted pad chords
tr_pad = song.add_track(Track(name="pad", instrument="shifted_pad", volume=0.3, pan=-0.15))
tr_pad.add(Chord("C", "min7", 3, duration=8.0))
tr_pad.add(Chord("Ab", "maj7", 3, duration=8.0))

# Smeared texture accents
tr_smear = song.add_track(Track(name="smear", instrument="smeared", volume=0.25, pan=0.2))
smear_notes = [
    ("C", 5, 3.0),
    ("Eb", 5, 2.0),
    ("G", 5, 3.0),
    ("Bb", 5, 2.0),
    ("Ab", 5, 3.0),
    ("G", 5, 3.0),
]
for n, o, d in smear_notes:
    tr_smear.add(Note(n, o, d))

song.effects = {
    "drone": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
    "smear": EffectsChain().add(reverb, room_size=0.95, wet=0.6),
}
