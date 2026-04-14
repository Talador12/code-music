"""Vintage preset pack: FM pianos, analog strings, tape effects.

Registers instruments and effects inspired by classic hardware synths
and recording equipment. Import this module to make them available::

    import code_music.packs.vintage
    # Now "vintage_epiano", "vintage_strings", etc. are registered

Or use individual presets directly::

    from code_music.packs.vintage import vintage_epiano
    song.register_instrument("epiano", vintage_epiano)
"""

from __future__ import annotations

import math

import numpy as np

from ..plugins import register_effect, register_instrument
from ..sound_design import SoundDesigner, Wavetable

# ---------------------------------------------------------------------------
# Instruments
# ---------------------------------------------------------------------------


@register_instrument("vintage_epiano")
def _make_vintage_epiano():
    """Rhodes-style FM electric piano. Warm, bell-like attack with bark."""
    return (
        SoundDesigner("vintage_epiano")
        .fm("sine", mod_ratio=1.0, mod_index=2.5, volume=0.6)
        .fm("sine", mod_ratio=7.0, mod_index=0.8, volume=0.2)
        .envelope(attack=0.005, decay=0.4, sustain=0.3, release=0.5)
        .filter("lowpass", cutoff=3500, resonance=0.3)
    )


# Expose the SoundDesigner directly for song.register_instrument()
vintage_epiano = _make_vintage_epiano()


@register_instrument("vintage_strings")
def _make_vintage_strings():
    """Analog string ensemble. Slow attack, chorus-like detuning."""
    return (
        SoundDesigner("vintage_strings")
        .add_osc("sawtooth", volume=0.25)
        .add_osc("sawtooth", detune_cents=8, volume=0.22)
        .add_osc("sawtooth", detune_cents=-8, volume=0.22)
        .add_osc("sawtooth", detune_cents=15, volume=0.18)
        .envelope(attack=0.15, decay=0.1, sustain=0.85, release=0.6)
        .filter("lowpass", cutoff=3000, resonance=0.4)
        .lfo("filter_cutoff", rate=0.2, depth=0.3)
    )


vintage_strings = _make_vintage_strings()


@register_instrument("vintage_organ")
def _make_vintage_organ():
    """Hammond-style drawbar organ. Additive harmonics with key click."""
    # Drawbar registration: 888000000 (full 8', 4', 2-2/3')
    harmonics = [1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    wt = Wavetable.from_harmonics(harmonics)
    return (
        SoundDesigner("vintage_organ")
        .add_wavetable(wt, volume=0.6)
        .envelope(attack=0.003, decay=0.05, sustain=0.9, release=0.08)
        .filter("lowpass", cutoff=4500, resonance=0.2)
    )


vintage_organ = _make_vintage_organ()


@register_instrument("vintage_bass")
def _make_vintage_bass():
    """Minimoog-style bass. Fat saw with sub oscillator."""
    return (
        SoundDesigner("vintage_bass")
        .add_osc("sawtooth", volume=0.5)
        .add_osc("square", detune_cents=-1200, volume=0.35)  # sub octave
        .envelope(attack=0.005, decay=0.15, sustain=0.6, release=0.15)
        .filter("lowpass", cutoff=1200, resonance=0.7)
    )


vintage_bass = _make_vintage_bass()


@register_instrument("vintage_lead")
def _make_vintage_lead():
    """Prophet-5 style poly lead. Warm saw with PWM-like modulation."""
    return (
        SoundDesigner("vintage_lead")
        .add_osc("sawtooth", volume=0.4)
        .add_osc("square", detune_cents=3, volume=0.35)
        .envelope(attack=0.01, decay=0.2, sustain=0.65, release=0.3)
        .filter("lowpass", cutoff=4000, resonance=0.5)
        .lfo("filter_cutoff", rate=0.5, depth=0.4)
    )


vintage_lead = _make_vintage_lead()


@register_instrument("vintage_pad")
def _make_vintage_pad():
    """Juno-style lush pad. Detuned saws with slow filter sweep."""
    return (
        SoundDesigner("vintage_pad")
        .add_osc("sawtooth", volume=0.2)
        .add_osc("sawtooth", detune_cents=12, volume=0.2)
        .add_osc("sawtooth", detune_cents=-12, volume=0.2)
        .add_osc("triangle", volume=0.15)
        .envelope(attack=0.4, decay=0.2, sustain=0.8, release=0.8)
        .filter("lowpass", cutoff=2500, resonance=0.5)
        .lfo("filter_cutoff", rate=0.15, depth=0.5)
    )


vintage_pad = _make_vintage_pad()


# ---------------------------------------------------------------------------
# Effects
# ---------------------------------------------------------------------------


@register_effect("tape_saturation")
def tape_saturation(
    samples: np.ndarray,
    sample_rate: int,
    drive: float = 0.4,
    warmth: float = 0.6,
    wet: float = 0.7,
) -> np.ndarray:
    """Tape saturation: soft clipping with high-frequency roll-off.

    Emulates the warm compression of analog tape machines (Studer A800,
    Ampex ATR-102). Drive pushes into soft clip, warmth rolls off highs.

    Args:
        samples:     Stereo or mono audio.
        sample_rate: Sample rate.
        drive:       Saturation amount (0-1). 0.4 = warm, 0.8 = heavily driven.
        warmth:      High-frequency roll-off (0-1). 0.6 = natural tape warmth.
        wet:         Wet/dry mix.
    """
    # Soft clip via tanh with adjustable drive
    driven = np.tanh(samples * (1.0 + drive * 4.0))

    # Warmth: simple one-pole lowpass (tape head frequency response)
    if warmth > 0 and samples.ndim == 2:
        alpha = warmth * 0.15
        for ch in range(samples.shape[1]):
            for i in range(1, len(driven)):
                driven[i, ch] = (1 - alpha) * driven[i, ch] + alpha * driven[i - 1, ch]
    elif warmth > 0 and samples.ndim == 1:
        alpha = warmth * 0.15
        for i in range(1, len(driven)):
            driven[i] = (1 - alpha) * driven[i] + alpha * driven[i - 1]

    return wet * driven + (1 - wet) * samples


@register_effect("wow_flutter")
def wow_flutter(
    samples: np.ndarray,
    sample_rate: int,
    wow_rate: float = 0.5,
    wow_depth: float = 0.002,
    flutter_rate: float = 6.0,
    flutter_depth: float = 0.0005,
    wet: float = 0.8,
) -> np.ndarray:
    """Tape wow and flutter: pitch modulation from transport imperfections.

    Wow = slow pitch drift (capstan eccentricity). Flutter = fast pitch
    wobble (tape guide vibration). Together they create the organic,
    slightly imperfect character of vintage tape recordings.

    Args:
        samples:       Audio.
        sample_rate:   Sample rate.
        wow_rate:      Wow frequency in Hz (0.3-1.5).
        wow_depth:     Wow pitch deviation (fraction of sample rate).
        flutter_rate:  Flutter frequency in Hz (4-12).
        flutter_depth: Flutter pitch deviation.
        wet:           Wet/dry mix.
    """
    if samples.ndim == 2:
        mono = np.mean(samples, axis=1)
    else:
        mono = samples.copy()

    n = len(mono)
    t = np.arange(n) / sample_rate

    # Combined modulation signal
    mod = wow_depth * np.sin(2 * math.pi * wow_rate * t) + flutter_depth * np.sin(
        2 * math.pi * flutter_rate * t
    )

    # Variable delay via interpolation
    read_pos = np.arange(n) + mod * sample_rate
    read_pos = np.clip(read_pos, 0, n - 1)
    i0 = np.floor(read_pos).astype(np.intp)
    i1 = np.minimum(i0 + 1, n - 1)
    frac = read_pos - i0
    modulated = mono[i0] * (1 - frac) + mono[i1] * frac

    if samples.ndim == 2:
        result = np.column_stack([modulated, modulated])
        return wet * result + (1 - wet) * samples
    return wet * modulated + (1 - wet) * samples
