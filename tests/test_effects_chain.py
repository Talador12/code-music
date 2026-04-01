"""Tests for the EffectsChain class."""

from __future__ import annotations

import numpy as np

from code_music.effects import EffectsChain, delay, reverb

SR = 22050


def _make_signal(seconds: float = 0.5) -> np.ndarray:
    """Short stereo sine wave for testing."""
    t = np.linspace(0, seconds, int(SR * seconds), endpoint=False)
    mono = np.sin(2 * np.pi * 440 * t) * 0.5
    return np.column_stack([mono, mono])


class TestEffectsChainBuild:
    def test_empty_chain(self):
        chain = EffectsChain()
        assert len(chain) == 0

    def test_add_returns_self(self):
        chain = EffectsChain()
        result = chain.add(reverb, room_size=0.5, wet=0.2)
        assert result is chain

    def test_add_increments_length(self):
        chain = EffectsChain().add(reverb, room_size=0.5).add(delay, delay_ms=200)
        assert len(chain) == 2

    def test_remove_decrements_length(self):
        chain = EffectsChain().add(reverb).add(delay, delay_ms=200)
        chain.remove(0)
        assert len(chain) == 1

    def test_steps_property_returns_copy(self):
        chain = EffectsChain().add(reverb)
        steps = chain.steps
        steps.clear()
        assert len(chain) == 1

    def test_repr_includes_step_info(self):
        chain = EffectsChain().add(reverb, room_size=0.5, label="verb")
        r = repr(chain)
        assert "verb" in r
        assert "EffectsChain" in r

    def test_iter_yields_steps(self):
        chain = EffectsChain().add(reverb).add(delay, delay_ms=100)
        steps = list(chain)
        assert len(steps) == 2


class TestEffectsChainProcess:
    def test_empty_chain_is_passthrough(self):
        chain = EffectsChain()
        sig = _make_signal()
        result = chain(sig, SR)
        np.testing.assert_array_equal(result, sig)

    def test_single_effect_modifies_signal(self):
        chain = EffectsChain().add(reverb, room_size=0.5, wet=0.3)
        sig = _make_signal()
        result = chain(sig, SR)
        assert not np.array_equal(result, sig)

    def test_bypass_skips_effect(self):
        chain = EffectsChain().add(reverb, room_size=0.5, wet=0.3, bypass=True)
        sig = _make_signal()
        result = chain(sig, SR)
        np.testing.assert_array_equal(result, sig)

    def test_set_bypass_toggles(self):
        chain = EffectsChain().add(reverb, room_size=0.5, wet=0.3)
        sig = _make_signal()

        processed = chain(sig.copy(), SR)
        assert not np.array_equal(processed, sig)

        chain.set_bypass(0, True)
        bypassed = chain(sig.copy(), SR)
        np.testing.assert_array_equal(bypassed, sig)

        chain.set_bypass(0, False)
        unblocked = chain(sig.copy(), SR)
        assert not np.array_equal(unblocked, sig)

    def test_wet_zero_is_passthrough(self):
        chain = EffectsChain().add(reverb, room_size=0.5, wet=0.0)
        sig = _make_signal()
        result = chain(sig, SR)
        np.testing.assert_array_equal(result, sig)

    def test_set_wet_changes_mix(self):
        chain = EffectsChain().add(reverb, room_size=0.5)
        sig = _make_signal()

        chain.set_wet(0, 1.0)
        full_wet = chain(sig.copy(), SR)

        chain.set_wet(0, 0.5)
        half_wet = chain(sig.copy(), SR)

        # Half-wet should be closer to dry signal than full-wet
        dry_dist_full = np.mean(np.abs(full_wet - sig))
        dry_dist_half = np.mean(np.abs(half_wet - sig))
        assert dry_dist_half < dry_dist_full

    def test_chain_ordering_matters(self):
        sig = _make_signal()

        chain_a = (
            EffectsChain().add(reverb, room_size=0.5, wet=0.3).add(delay, delay_ms=200, wet=0.2)
        )
        chain_b = (
            EffectsChain().add(delay, delay_ms=200, wet=0.2).add(reverb, room_size=0.5, wet=0.3)
        )

        result_a = chain_a(sig.copy(), SR)
        result_b = chain_b(sig.copy(), SR)

        # Different ordering should produce different output
        assert not np.array_equal(result_a, result_b)

    def test_callable_interface_matches_legacy_lambda(self):
        """EffectsChain is callable(samples, sr) just like the old lambda pattern."""
        chain = EffectsChain().add(reverb, room_size=0.5, wet=0.3)
        sig = _make_signal()
        result = chain(sig, SR)
        assert result.shape == sig.shape
        assert result.dtype == sig.dtype or result.dtype == np.float64


class TestEffectsChainWithSong:
    def test_song_effects_dict_uses_chain(self):
        from code_music import Note, Song, Track
        from code_music.synth import Synth

        song = Song(title="Chain Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="sine"))
        tr.add(Note("A", 4, 2.0))

        chain = EffectsChain().add(reverb, room_size=0.5, wet=0.3)
        song.effects["lead"] = chain

        samples = Synth(SR).render_song(song)
        assert samples.shape[0] > 0
        assert np.max(np.abs(samples)) > 0.0
