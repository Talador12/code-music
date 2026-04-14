"""Cinematic preset pack: orchestral hits, risers, impacts, epic textures.

Film score and trailer music essentials. Import to register::

    import code_music.packs.cinematic
"""

from __future__ import annotations

from ..plugins import register_effect, register_instrument
from ..sound_design import SoundDesigner


@register_instrument("epic_brass")
def _epic_brass():
    """Massive brass ensemble. Triple-stacked saw + FM for bite."""
    return (
        SoundDesigner("epic_brass")
        .add_osc("sawtooth", volume=0.3)
        .add_osc("sawtooth", detune_cents=8, volume=0.25)
        .add_osc("sawtooth", detune_cents=-8, volume=0.25)
        .fm("square", mod_ratio=1.0, mod_index=1.5, volume=0.2)
        .envelope(attack=0.06, decay=0.15, sustain=0.75, release=0.4)
        .filter("lowpass", cutoff=4500, resonance=0.5)
    )


epic_brass = _epic_brass()


@register_instrument("epic_strings")
def _epic_strings():
    """Lush string section. 6 detuned saws with slow filter sweep."""
    return (
        SoundDesigner("epic_strings")
        .add_osc("sawtooth", volume=0.15)
        .add_osc("sawtooth", detune_cents=10, volume=0.15)
        .add_osc("sawtooth", detune_cents=-10, volume=0.15)
        .add_osc("sawtooth", detune_cents=18, volume=0.1)
        .add_osc("sawtooth", detune_cents=-18, volume=0.1)
        .add_osc("triangle", volume=0.1)
        .envelope(attack=0.25, decay=0.2, sustain=0.85, release=0.8)
        .filter("lowpass", cutoff=3500, resonance=0.4)
        .lfo("filter_cutoff", rate=0.1, depth=0.3)
    )


epic_strings = _epic_strings()


@register_instrument("cinematic_pad")
def _cinematic_pad():
    """Atmospheric cinematic pad. Dark, evolving, huge."""
    return (
        SoundDesigner("cinematic_pad")
        .add_osc("sawtooth", volume=0.15)
        .add_osc("sawtooth", detune_cents=15, volume=0.15)
        .add_osc("sawtooth", detune_cents=-15, volume=0.15)
        .add_osc("square", detune_cents=-1200, volume=0.1)
        .envelope(attack=0.8, decay=0.3, sustain=0.7, release=1.5)
        .filter("lowpass", cutoff=1500, resonance=0.6)
        .lfo("filter_cutoff", rate=0.08, depth=0.5)
    )


cinematic_pad = _cinematic_pad()


@register_instrument("trailer_hit")
def _trailer_hit():
    """Massive trailer impact. Low boom + high transient."""
    return (
        SoundDesigner("trailer_hit")
        .add_osc("sine", volume=0.8)
        .fm("sine", mod_ratio=1.5, mod_index=5.0, volume=0.3)
        .envelope(attack=0.001, decay=0.6, sustain=0.0, release=0.8)
        .filter("lowpass", cutoff=300, resonance=0.5)
        .lfo("pitch", rate=0.3, depth=0.9)
    )


trailer_hit = _trailer_hit()


@register_instrument("tension_drone")
def _tension_drone():
    """Dark tension drone for suspense scenes."""
    return (
        SoundDesigner("tension_drone")
        .add_osc("sawtooth", volume=0.2)
        .add_osc("square", detune_cents=3, volume=0.2)
        .add_osc("sawtooth", detune_cents=-2400, volume=0.3)
        .envelope(attack=1.5, decay=0.5, sustain=0.9, release=2.0)
        .filter("lowpass", cutoff=400, resonance=0.8)
        .lfo("filter_cutoff", rate=0.03, depth=0.4)
    )


tension_drone = _tension_drone()


@register_instrument("choir_epic")
def _choir_epic():
    """Epic choir using dual formant layers."""
    return (
        SoundDesigner("choir_epic")
        .formant("ah", breathiness=0.15, vibrato_rate=5.5, vibrato_depth=0.025, volume=0.5)
        .formant("oh", breathiness=0.1, vibrato_rate=5.0, vibrato_depth=0.02, volume=0.4)
        .envelope(attack=0.15, decay=0.1, sustain=0.85, release=0.6)
        .filter("lowpass", cutoff=4500, resonance=0.3)
    )


choir_epic = _choir_epic()


@register_instrument("harp_pluck")
def _harp_pluck():
    """Concert harp pluck. Quick attack, shimmering decay."""
    return (
        SoundDesigner("harp_pluck")
        .physical_model("karplus_strong", volume=0.85, decay=0.997, brightness=0.7)
        .envelope(attack=0.001, decay=0.4, sustain=0.1, release=0.5)
        .filter("lowpass", cutoff=6000, resonance=0.3)
    )


harp_pluck = _harp_pluck()


@register_instrument("timpani")
def _timpani():
    """Orchestral timpani. Pitched drum with resonant body."""
    return (
        SoundDesigner("timpani")
        .physical_model("modal", volume=0.9)
        .add_osc("sine", volume=0.4)
        .envelope(attack=0.002, decay=0.5, sustain=0.1, release=0.6)
        .filter("lowpass", cutoff=1500, resonance=0.6)
    )


timpani = _timpani()


@register_instrument("celeste")
def _celeste():
    """Celeste / music box. Bell-like FM with quick decay."""
    return (
        SoundDesigner("celeste")
        .fm("sine", mod_ratio=3.0, mod_index=2.0, volume=0.7)
        .envelope(attack=0.001, decay=0.3, sustain=0.05, release=0.4)
        .filter("lowpass", cutoff=8000, resonance=0.2)
    )


celeste = _celeste()


@register_effect("cinematic_reverb")
def cinematic_reverb(samples, sample_rate, size=0.95, wet=0.4):
    """Large hall reverb for cinematic mixes."""
    from ..effects import room_reverb

    return room_reverb(samples, sample_rate, width=25, depth=35, height=15, absorption=0.1, wet=wet)
