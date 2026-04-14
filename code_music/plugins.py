"""Plugin registry for extending code-music with third-party instruments, effects, and generators.

Provides decorator-based registration so plugins are auto-discovered when imported.
No configuration files, no entry_points magic - just import and use.

Example - register a custom instrument::

    from code_music.plugins import register_instrument
    from code_music.sound_design import SoundDesigner

    @register_instrument("my_synth")
    def my_synth():
        return (
            SoundDesigner("my_synth")
            .oscillator("sawtooth", volume=0.7)
            .filter("lowpass", cutoff=2000, resonance=0.8)
            .envelope(attack=0.01, decay=0.1, sustain=0.6, release=0.3)
        )

Example - register a custom effect::

    from code_music.plugins import register_effect

    @register_effect("my_chorus")
    def my_chorus(samples, sample_rate, depth=0.5, rate=1.5):
        # ... process audio ...
        return processed

Example - register a custom generator::

    from code_music.plugins import register_generator

    @register_generator("my_genre")
    def my_genre(key="C", bpm=120, seed=None):
        # ... build a Song ...
        return song
"""

from __future__ import annotations

from typing import Callable

# ---------------------------------------------------------------------------
# Registry storage
# ---------------------------------------------------------------------------

_instruments: dict[str, Callable] = {}
_effects: dict[str, Callable] = {}
_generators: dict[str, Callable] = {}


# ---------------------------------------------------------------------------
# Decorator: register_instrument
# ---------------------------------------------------------------------------


def register_instrument(name: str) -> Callable:
    """Register a SoundDesigner factory as a named instrument.

    The decorated function should take no args and return a SoundDesigner.
    Once registered, the instrument can be used by name in Track(instrument=name)
    and will be auto-discovered by the synth engine.

    Args:
        name: Instrument name (used in Track.instrument).

    Returns:
        Decorator that registers the factory function.

    Example::

        @register_instrument("wobble_bass")
        def wobble_bass():
            return SoundDesigner("wobble_bass").oscillator("sawtooth").lfo(...)
    """

    def decorator(fn: Callable) -> Callable:
        _instruments[name] = fn
        return fn

    return decorator


# ---------------------------------------------------------------------------
# Decorator: register_effect
# ---------------------------------------------------------------------------


def register_effect(name: str) -> Callable:
    """Register an audio effect function.

    The decorated function should accept (samples, sample_rate, **kwargs)
    and return processed samples. Once registered, the effect can be
    referenced by name in EffectsChain and CLI.

    Args:
        name: Effect name.

    Returns:
        Decorator that registers the effect function.

    Example::

        @register_effect("shimmer_verb")
        def shimmer_verb(samples, sr, shimmer=0.5, room=0.8):
            ...
            return processed
    """

    def decorator(fn: Callable) -> Callable:
        _effects[name] = fn
        return fn

    return decorator


# ---------------------------------------------------------------------------
# Decorator: register_generator
# ---------------------------------------------------------------------------


def register_generator(name: str) -> Callable:
    """Register a song generator function.

    The decorated function should accept (key, bpm, seed, **kwargs)
    and return a Song. Once registered, the generator can be invoked
    via compose() or the CLI.

    Args:
        name: Generator name (used as genre/style name).

    Returns:
        Decorator that registers the generator function.

    Example::

        @register_generator("vaporwave")
        def vaporwave(key="C", bpm=80, seed=None):
            song = Song(title="Vaporwave", bpm=bpm)
            ...
            return song
    """

    def decorator(fn: Callable) -> Callable:
        _generators[name] = fn
        return fn

    return decorator


# ---------------------------------------------------------------------------
# Lookup functions
# ---------------------------------------------------------------------------


def get_instrument(name: str) -> Callable | None:
    """Look up a registered instrument factory by name.

    Returns None if no instrument is registered with that name.
    """
    return _instruments.get(name)


def get_effect(name: str) -> Callable | None:
    """Look up a registered effect function by name."""
    return _effects.get(name)


def get_generator(name: str) -> Callable | None:
    """Look up a registered song generator by name."""
    return _generators.get(name)


def list_instruments() -> list[str]:
    """List all registered instrument names."""
    return sorted(_instruments.keys())


def list_effects() -> list[str]:
    """List all registered effect names."""
    return sorted(_effects.keys())


def list_generators() -> list[str]:
    """List all registered generator names."""
    return sorted(_generators.keys())


def clear_all() -> None:
    """Clear all registries. Useful for testing."""
    _instruments.clear()
    _effects.clear()
    _generators.clear()


def plugin_summary() -> dict:
    """Return a summary of all registered plugins.

    Returns:
        Dict with instrument_count, effect_count, generator_count,
        and lists of names for each category.
    """
    return {
        "instrument_count": len(_instruments),
        "effect_count": len(_effects),
        "generator_count": len(_generators),
        "instruments": list_instruments(),
        "effects": list_effects(),
        "generators": list_generators(),
    }
