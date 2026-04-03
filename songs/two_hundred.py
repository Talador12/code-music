"""Song #200 — a celebration of 200 songs, using every major feature.

FM synthesis, wavetable, patterns, euclidean drums, theory-generated bass,
Markov melody continuation, spectral freeze, mastering pipeline.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Pattern,
    Song,
    SoundDesigner,
    Track,
    Wavetable,
    euclid,
    reverb,
)
from code_music.composition import continue_melody
from code_music.mastering import master_audio, measure_lufs
from code_music.sound_design import spectral_freeze
from code_music.theory import generate_bass_line

# Custom instruments
supersaw = (
    SoundDesigner("supersaw")
    .add_osc("sawtooth", volume=0.3)
    .add_osc("sawtooth", detune_cents=10, volume=0.25)
    .add_osc("sawtooth", detune_cents=-10, volume=0.25)
    .envelope(attack=0.02, decay=0.1, sustain=0.7, release=0.4)
    .filter("lowpass", cutoff=4000, resonance=0.6)
)
frozen_pad = (
    SoundDesigner("frozen_pad")
    .add_osc("sawtooth", volume=0.3)
    .add_osc("triangle", detune_cents=3, volume=0.3)
    .spectral(spectral_freeze(0.85))
    .envelope(attack=0.5, decay=0.3, sustain=0.5, release=1.0)
)
fm_bell = (
    SoundDesigner("fm_bell")
    .fm("sine", mod_ratio=1.414, mod_index=6.0)
    .envelope(attack=0.001, decay=1.0, sustain=0.0, release=0.8)
)
_wt = Wavetable.from_harmonics([1.0, 0.5, 0.0, 0.25, 0.0, 0.125])
wt_organ = (
    SoundDesigner("wt_organ")
    .add_wavetable(_wt, volume=0.5)
    .add_wavetable(_wt, volume=0.4, detune_cents=5)
    .envelope(attack=0.02, decay=0.05, sustain=0.8, release=0.3)
)

song = Song(title="Two Hundred", bpm=120, sample_rate=44100, key_sig="C")
for name, d in [
    ("supersaw", supersaw),
    ("frozen_pad", frozen_pad),
    ("fm_bell", fm_bell),
    ("wt_organ", wt_organ),
]:
    song.register_instrument(name, d)

prog = [("C", "min7"), ("Ab", "maj7"), ("Eb", "maj"), ("Bb", "dom7")]

# Frozen pad bed
song.add_track(Track(name="pad", instrument="frozen_pad", volume=0.25)).add(Note("C", 3, 16.0))

# Wavetable organ chords
song.add_track(Track(name="organ", instrument="wt_organ", volume=0.35, pan=-0.1)).extend(
    [Chord(r, s, 3, duration=4.0) for r, s in prog]
)

# Theory-generated bass
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    generate_bass_line(prog, style="walking", seed=200)
)

# Euclidean drums
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7)).extend(
    euclid(4, 16, "C", 2, 0.5) * 2
)
song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3)).extend(
    [Note("F#", 6, 0.5) for _ in range(32)]
)

# Pattern-based supersaw lead
pat = Pattern("C5 Eb5 G5 Bb5 Ab5 G5 Eb5 C5")
song.add_track(Track(name="lead", instrument="supersaw", volume=0.45, pan=0.15)).extend(
    pat.to_notes(0.5)
)

# Markov continuation of a seed
seed = [Note("G", 5, 0.5), Note("Bb", 5, 0.5), Note("C", 6, 0.5)]
extended = continue_melody(seed, bars=2, key="C", mode="minor", seed_rng=200)
song.add_track(Track(name="melody2", instrument="fm_bell", volume=0.25, pan=0.2)).extend(extended)

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "organ": EffectsChain().add(reverb, room_size=0.6, wet=0.25),
}
