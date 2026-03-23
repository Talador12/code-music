"""Tests for the effects module."""

import numpy as np

from code_music.effects import (
    bandpass,
    chorus,
    compress,
    delay,
    distortion,
    highpass,
    lowpass,
    pan,
    reverb,
)


def _sine(sr=22050, freq=440.0, dur_sec=1.0) -> np.ndarray:
    """Generate a short stereo sine test signal."""
    n = int(sr * dur_sec)
    t = np.linspace(0, dur_sec, n, endpoint=False)
    mono = np.sin(2 * np.pi * freq * t) * 0.5
    return np.column_stack([mono, mono]).astype(np.float64)


SR = 22050


class TestReverb:
    def test_output_shape(self):
        s = _sine(SR)
        out = reverb(s, SR)
        assert out.shape == s.shape

    def test_wet_zero_is_dry(self):
        s = _sine(SR)
        out = reverb(s, SR, wet=0.0)
        np.testing.assert_allclose(out, s, atol=1e-6)

    def test_wet_adds_energy(self):
        s = _sine(SR)
        out = reverb(s, SR, wet=0.4)
        # wet signal should differ from dry
        assert not np.allclose(out, s)


class TestDelay:
    def test_output_shape(self):
        s = _sine(SR)
        out = delay(s, SR)
        assert out.shape == s.shape

    def test_zero_feedback_low_wet_near_passthrough(self):
        # feedback=0 means no echo taps beyond the first; wet=0 means no first echo
        # so output should equal input exactly
        s = _sine(SR)
        out = delay(s, SR, wet=0.0, feedback=0.0)
        np.testing.assert_allclose(out, s, atol=1e-9)

    def test_ping_pong_asymmetric(self):
        # Feed an asymmetric stereo input so the ping-pong crosses channels
        n = int(SR * 2.0)
        left = np.sin(2 * np.pi * 440 * np.linspace(0, 2, n)) * 0.5
        right = np.zeros(n)  # silent right → ping-pong will put echo only on right
        s = np.column_stack([left, right]).astype(np.float64)
        out = delay(s, SR, delay_ms=100.0, feedback=0.6, wet=0.8, ping_pong=True)
        # After one delay cycle the echo should appear on the R channel
        delay_samples = int(0.1 * SR)
        assert np.max(np.abs(out[delay_samples:, 1])) > 0.05


class TestChorus:
    def test_output_shape(self):
        s = _sine(SR)
        out = chorus(s, SR)
        assert out.shape == s.shape

    def test_modifies_signal(self):
        s = _sine(SR)
        out = chorus(s, SR, wet=0.5)
        assert not np.allclose(out, s)


class TestDistortion:
    def test_output_shape(self):
        s = _sine(SR)
        out = distortion(s)
        assert out.shape == s.shape

    def test_hard_drive_clips(self):
        s = _sine(SR) * 0.9
        out = distortion(s, drive=10.0, wet=1.0)
        # heavy drive + wet=1 should produce a flatter (clipped) waveform
        assert np.max(np.abs(out)) <= 1.0 + 1e-6


class TestFilters:
    def test_lowpass_shape(self):
        s = _sine(SR)
        out = lowpass(s, SR, cutoff_hz=1000.0)
        assert out.shape == s.shape

    def test_highpass_shape(self):
        s = _sine(SR)
        out = highpass(s, SR, cutoff_hz=100.0)
        assert out.shape == s.shape

    def test_bandpass_shape(self):
        s = _sine(SR)
        out = bandpass(s, SR, center_hz=440.0)
        assert out.shape == s.shape

    def test_lowpass_attenuates_high_freq(self):
        # 4kHz sine filtered through 200Hz LP should lose most energy
        high = _sine(SR, freq=4000.0)
        out = lowpass(high, SR, cutoff_hz=200.0)
        assert np.mean(np.abs(out)) < np.mean(np.abs(high)) * 0.2

    def test_highpass_attenuates_low_freq(self):
        low = _sine(SR, freq=50.0)
        out = highpass(low, SR, cutoff_hz=1000.0)
        assert np.mean(np.abs(out)) < np.mean(np.abs(low)) * 0.2


class TestCompress:
    def test_output_shape(self):
        s = _sine(SR)
        out = compress(s, SR)
        assert out.shape == s.shape

    def test_output_clamped(self):
        s = _sine(SR) * 0.9
        out = compress(s, SR, ratio=8.0, makeup_gain=2.0)
        assert np.max(np.abs(out)) <= 1.0 + 1e-6

    def test_reduces_peaks(self):
        # Use a signal that clearly exceeds threshold and makeup_gain < ratio effect
        s = _sine(SR, freq=440.0, dur_sec=2.0) * 0.9
        out = compress(s, SR, threshold=0.1, ratio=20.0, makeup_gain=0.5)
        assert np.max(np.abs(out)) < np.max(np.abs(s))


class TestPan:
    def test_center_is_equal(self):
        s = _sine(SR)
        out = pan(s, 0.0)
        # equal-power center: L and R equal
        np.testing.assert_allclose(out[:, 0], out[:, 1], atol=1e-6)

    def test_hard_left(self):
        s = _sine(SR)
        out = pan(s, -1.0)
        # left channel should have all the energy
        assert np.mean(np.abs(out[:, 0])) > np.mean(np.abs(out[:, 1])) * 10

    def test_hard_right(self):
        s = _sine(SR)
        out = pan(s, 1.0)
        assert np.mean(np.abs(out[:, 1])) > np.mean(np.abs(out[:, 0])) * 10


class TestEffectChain:
    def test_chain_does_not_crash(self):
        """Chaining multiple effects shouldn't blow up."""
        s = _sine(SR)
        out = compress(distortion(lowpass(reverb(s, SR, wet=0.3), SR, cutoff_hz=3000.0)), SR)
        assert out.shape == s.shape
        assert np.max(np.abs(out)) <= 1.0 + 1e-6
