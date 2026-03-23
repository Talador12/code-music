"""Tests for LFO modulation and sidechain compression."""

import numpy as np

from code_music.effects import lfo_filter, sidechain, tremolo, vibrato

SR = 22050


def _sine(freq=440.0, dur=1.0):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    mono = np.sin(2 * np.pi * freq * t) * 0.5
    return np.column_stack([mono, mono]).astype(np.float64)


class TestTremolo:
    def test_output_shape(self):
        s = _sine()
        out = tremolo(s, SR)
        assert out.shape == s.shape

    def test_depth_zero_passthrough(self):
        s = _sine()
        out = tremolo(s, SR, depth=0.0)
        np.testing.assert_allclose(out, s, atol=1e-6)

    def test_depth_one_modulates(self):
        s = _sine()
        out = tremolo(s, SR, depth=1.0, rate_hz=5.0)
        assert not np.allclose(out, s)

    def test_reduces_average_energy(self):
        s = _sine()
        out = tremolo(s, SR, depth=0.8)
        assert np.mean(np.abs(out)) < np.mean(np.abs(s))


class TestVibrato:
    def test_output_shape(self):
        s = _sine()
        out = vibrato(s, SR)
        assert out.shape == s.shape

    def test_modifies_signal(self):
        s = _sine()
        out = vibrato(s, SR, depth_cents=50.0)
        assert not np.allclose(out, s)

    def test_zero_depth_near_passthrough(self):
        s = _sine()
        out = vibrato(s, SR, depth_cents=0.0)
        np.testing.assert_allclose(out, s, atol=1e-6)


class TestLfoFilter:
    def test_output_shape(self):
        s = _sine()
        out = lfo_filter(s, SR)
        assert out.shape == s.shape

    def test_modifies_signal(self):
        s = _sine()
        out = lfo_filter(s, SR, rate_hz=1.0)
        assert not np.allclose(out, s)

    def test_highpass_variant(self):
        s = _sine(freq=100.0)
        out = lfo_filter(s, SR, filter_type="high", min_cutoff=500.0, max_cutoff=5000.0)
        # A 100Hz tone through a HP filter sweeping 500-5000 should lose energy
        assert np.mean(np.abs(out)) < np.mean(np.abs(s))


class TestSidechain:
    def _kick_pattern(self, dur=2.0):
        """Synthesize a simple kick-like trigger signal."""
        n = int(SR * dur)
        kick = np.zeros(n)
        # Hit every beat (0.5s at SR samples)
        beat = SR // 2
        for i in range(0, n, beat):
            end = min(i + int(SR * 0.1), n)
            kick[i:end] = np.exp(-np.linspace(0, 10, end - i))
        return np.column_stack([kick, kick]).astype(np.float64)

    def test_output_shape(self):
        target = _sine(dur=2.0)
        trigger = self._kick_pattern(dur=2.0)
        out = sidechain(target, trigger, SR)
        assert out.shape == target.shape

    def test_depth_zero_passthrough(self):
        target = _sine(dur=2.0)
        trigger = self._kick_pattern(dur=2.0)
        out = sidechain(target, trigger, SR, depth=0.0)
        np.testing.assert_allclose(out, target, atol=1e-6)

    def test_depth_one_ducks_target(self):
        # Use a short 4410-sample trigger burst well above threshold
        n = SR * 2
        target = np.ones((n, 2)) * 0.5
        # Strong sustained trigger (not decaying) so envelope definitely exceeds threshold
        trigger = np.zeros((n, 2))
        trigger[: SR // 4] = 1.0  # 0.25s burst at full volume
        out = sidechain(
            target, trigger, SR, depth=1.0, threshold=0.1, ratio=10.0, attack_ms=1.0, release_ms=5.0
        )
        # The burst region should show ducking
        burst_out = out[: SR // 8]
        assert np.mean(np.abs(burst_out)) < 0.5

    def test_output_clamped(self):
        target = _sine(dur=2.0) * 0.9
        trigger = self._kick_pattern(dur=2.0)
        out = sidechain(target, trigger, SR, depth=1.0)
        assert np.max(np.abs(out)) <= 1.0 + 1e-6
