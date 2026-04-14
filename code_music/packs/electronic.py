"""Electronic / EDM preset pack: leads, plucks, basses, arps, risers.

Club and festival essentials. Import to register::

    import code_music.packs.electronic
"""

from __future__ import annotations

import numpy as np

from ..plugins import register_effect, register_instrument
from ..sound_design import SoundDesigner


@register_instrument("edm_supersaw")
def _edm_supersaw():
    """Festival supersaw. 7 detuned saws, massive and wide."""
    return (
        SoundDesigner("edm_supersaw")
        .add_osc("sawtooth", volume=0.15)
        .add_osc("sawtooth", detune_cents=8, volume=0.14)
        .add_osc("sawtooth", detune_cents=-8, volume=0.14)
        .add_osc("sawtooth", detune_cents=16, volume=0.12)
        .add_osc("sawtooth", detune_cents=-16, volume=0.12)
        .add_osc("sawtooth", detune_cents=24, volume=0.1)
        .add_osc("sawtooth", detune_cents=-24, volume=0.1)
        .envelope(attack=0.01, decay=0.15, sustain=0.7, release=0.3)
        .filter("lowpass", cutoff=5000, resonance=0.5)
    )


edm_supersaw = _edm_supersaw()


@register_instrument("edm_pluck")
def _edm_pluck():
    """Short pluck lead for melodies and arps."""
    return (
        SoundDesigner("edm_pluck")
        .add_osc("sawtooth", volume=0.5)
        .add_osc("square", detune_cents=7, volume=0.3)
        .envelope(attack=0.002, decay=0.12, sustain=0.0, release=0.08)
        .filter("lowpass", cutoff=6000, resonance=0.5)
    )


edm_pluck = _edm_pluck()


@register_instrument("wobble_bass")
def _wobble_bass():
    """Dubstep wobble bass. LFO on filter cutoff."""
    return (
        SoundDesigner("wobble_bass")
        .add_osc("sawtooth", volume=0.5)
        .add_osc("square", detune_cents=-1200, volume=0.3)
        .envelope(attack=0.005, decay=0.1, sustain=0.8, release=0.15)
        .filter("lowpass", cutoff=1000, resonance=0.85)
        .lfo("filter_cutoff", rate=2.0, depth=0.8)
    )


wobble_bass = _wobble_bass()


@register_instrument("neuro_bass")
def _neuro_bass():
    """Neuro/DnB reese bass. Detuned saws with movement."""
    return (
        SoundDesigner("neuro_bass")
        .add_osc("sawtooth", volume=0.4)
        .add_osc("sawtooth", detune_cents=5, volume=0.4)
        .add_osc("sawtooth", detune_cents=-5, volume=0.3)
        .envelope(attack=0.005, decay=0.1, sustain=0.8, release=0.15)
        .filter("lowpass", cutoff=800, resonance=0.7)
        .lfo("filter_cutoff", rate=0.3, depth=0.6)
    )


neuro_bass = _neuro_bass()


@register_instrument("trance_lead")
def _trance_lead():
    """Classic trance lead. Saw + square with filter sweep."""
    return (
        SoundDesigner("trance_lead")
        .add_osc("sawtooth", volume=0.4)
        .add_osc("square", detune_cents=3, volume=0.3)
        .envelope(attack=0.01, decay=0.2, sustain=0.6, release=0.3)
        .filter("lowpass", cutoff=3500, resonance=0.6)
        .lfo("filter_cutoff", rate=0.2, depth=0.5)
    )


trance_lead = _trance_lead()


@register_instrument("ambient_pad_deep")
def _ambient_pad_deep():
    """Deep ambient pad. Very slow attack, evolving filter."""
    return (
        SoundDesigner("ambient_pad_deep")
        .add_osc("triangle", volume=0.25)
        .add_osc("sawtooth", detune_cents=12, volume=0.15)
        .add_osc("sawtooth", detune_cents=-12, volume=0.15)
        .add_osc("sine", detune_cents=1200, volume=0.08)
        .envelope(attack=1.5, decay=0.5, sustain=0.7, release=2.0)
        .filter("lowpass", cutoff=1500, resonance=0.4)
        .lfo("filter_cutoff", rate=0.05, depth=0.4)
    )


ambient_pad_deep = _ambient_pad_deep()


@register_instrument("future_bass_chord")
def _future_bass_chord():
    """Future bass / kawaii chord stab."""
    return (
        SoundDesigner("future_bass_chord")
        .add_osc("sawtooth", volume=0.3)
        .add_osc("sawtooth", detune_cents=12, volume=0.25)
        .add_osc("sawtooth", detune_cents=-12, volume=0.25)
        .add_osc("square", detune_cents=7, volume=0.15)
        .envelope(attack=0.01, decay=0.3, sustain=0.4, release=0.2)
        .filter("lowpass", cutoff=4000, resonance=0.6)
        .lfo("filter_cutoff", rate=4.0, depth=0.5)
    )


future_bass_chord = _future_bass_chord()


@register_instrument("lofi_keys")
def _lofi_keys():
    """Lo-fi piano/keys. Warm, slightly detuned, filtered."""
    return (
        SoundDesigner("lofi_keys")
        .fm("sine", mod_ratio=2.0, mod_index=1.5, volume=0.5)
        .add_osc("triangle", detune_cents=-8, volume=0.2)
        .envelope(attack=0.005, decay=0.3, sustain=0.2, release=0.3)
        .filter("lowpass", cutoff=2500, resonance=0.3)
    )


lofi_keys = _lofi_keys()


@register_instrument("lofi_pad")
def _lofi_pad():
    """Lo-fi pad. Warm, muffled, nostalgic."""
    return (
        SoundDesigner("lofi_pad")
        .add_osc("triangle", volume=0.3)
        .add_osc("sawtooth", detune_cents=10, volume=0.15)
        .add_osc("sawtooth", detune_cents=-10, volume=0.15)
        .envelope(attack=0.3, decay=0.2, sustain=0.6, release=0.5)
        .filter("lowpass", cutoff=1800, resonance=0.4)
    )


lofi_pad = _lofi_pad()


@register_instrument("glitch_perc")
def _glitch_perc():
    """Glitch percussion. Granular burst with filter."""
    return (
        SoundDesigner("glitch_perc")
        .granular(grain_size=0.003, density=100, scatter=0.8, seed=42)
        .envelope(attack=0.001, decay=0.05, sustain=0.0, release=0.03)
        .filter("bandpass", cutoff=3000, resonance=0.9)
    )


glitch_perc = _glitch_perc()


@register_instrument("siren_lead")
def _siren_lead():
    """Siren lead. Pitch-swept sine for drops and risers."""
    return (
        SoundDesigner("siren_lead")
        .add_osc("sine", volume=0.7)
        .add_osc("sawtooth", detune_cents=1200, volume=0.2)
        .envelope(attack=0.01, decay=0.1, sustain=0.8, release=0.2)
        .filter("lowpass", cutoff=6000, resonance=0.4)
        .lfo("pitch", rate=3.0, depth=0.3)
    )


siren_lead = _siren_lead()


@register_effect("sidechain_pump")
def sidechain_pump_effect(samples, sample_rate, rate=4.0, depth=0.7, wet=0.8):
    """Fake sidechain pump without needing a kick track. LFO-based volume duck."""
    import math

    n = len(samples) if samples.ndim == 1 else samples.shape[0]
    t = np.arange(n) / sample_rate
    # Envelope: quick attack, slow release (simulates kick sidechain)
    env = 1.0 - depth * np.maximum(0, np.cos(2 * math.pi * rate * t)) ** 4
    if samples.ndim == 2:
        return wet * (samples * env[:, np.newaxis]) + (1 - wet) * samples
    return wet * (samples * env) + (1 - wet) * samples
