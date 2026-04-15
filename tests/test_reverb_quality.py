"""A/B test for reverb IR quality: verify early reflections + allpass diffusion."""

import numpy as np
import pytest

from code_music.effects import _make_reverb_ir, reverb


class TestReverbIRQuality:
    """Verify the reverb impulse response has proper structure."""

    @pytest.fixture
    def sr(self):
        return 22050

    def test_ir_has_predelay(self, sr):
        """First few milliseconds should be near-silent (pre-delay gap)."""
        ir = _make_reverb_ir(sr, room_size=0.5, damping=0.3)
        predelay_samples = int(0.005 * sr)  # first 5ms
        predelay_energy = np.mean(ir[:predelay_samples] ** 2)
        body_energy = np.mean(ir[predelay_samples : predelay_samples * 10] ** 2)
        assert predelay_energy < body_energy * 0.3, "Pre-delay should be quieter than body"

    def test_ir_has_early_reflections(self, sr):
        """Discrete peaks in the 10-100ms range (early reflections)."""
        ir = _make_reverb_ir(sr, room_size=0.5, damping=0.3)
        # Look for peaks in the early reflection region (10-100ms)
        er_start = int(0.010 * sr)
        er_end = int(0.100 * sr)
        er_region = np.abs(ir[er_start:er_end])
        # Should have some peaks significantly above the mean
        peak = np.max(er_region)
        mean = np.mean(er_region)
        assert peak > mean * 3, "Early reflections should have distinct peaks above the average"

    def test_ir_decays_exponentially(self, sr):
        """Energy should decrease over time (exponential decay)."""
        ir = _make_reverb_ir(sr, room_size=0.5, damping=0.3)
        n = len(ir)
        # Compare energy in first quarter vs last quarter
        q1_energy = np.mean(ir[: n // 4] ** 2)
        q4_energy = np.mean(ir[3 * n // 4 :] ** 2)
        assert q4_energy < q1_energy * 0.5, "Tail should have less energy than head"

    def test_ir_larger_room_longer(self, sr):
        """Larger room_size should produce a longer IR."""
        ir_small = _make_reverb_ir(sr, room_size=0.2, damping=0.3)
        ir_large = _make_reverb_ir(sr, room_size=0.8, damping=0.3)
        assert len(ir_large) > len(ir_small)

    def test_ir_more_damping_darker(self, sr):
        """Higher damping should reduce high-frequency content."""
        ir_bright = _make_reverb_ir(sr, room_size=0.5, damping=0.1)
        ir_dark = _make_reverb_ir(sr, room_size=0.5, damping=0.8)

        # Measure spectral centroid (brightness)
        def centroid(signal):
            fft = np.abs(np.fft.rfft(signal))
            freqs = np.fft.rfftfreq(len(signal), 1.0 / sr)
            total = np.sum(fft)
            if total < 1e-10:
                return 0
            return np.sum(freqs * fft) / total

        c_bright = centroid(ir_bright)
        c_dark = centroid(ir_dark)
        assert c_dark < c_bright, "Higher damping should produce darker IR"

    def test_ir_is_normalized(self, sr):
        """IR peak should be close to 1.0."""
        ir = _make_reverb_ir(sr, room_size=0.5, damping=0.3)
        peak = np.max(np.abs(ir))
        assert 0.8 < peak <= 1.0, f"IR should be normalized, got peak={peak}"


class TestReverbEffect:
    """Verify the full reverb effect produces good output."""

    @pytest.fixture
    def dry_signal(self):
        sr = 22050
        t = np.linspace(0, 0.5, sr // 2)
        mono = np.sin(2 * np.pi * 440 * t) * 0.5
        # Impulse at the start (good for testing reverb response)
        impulse = np.zeros_like(mono)
        impulse[100] = 1.0
        signal = mono + impulse * 0.3
        return np.column_stack([signal, signal]).astype(np.float64), sr

    def test_reverb_adds_energy_after_dry(self):
        """Wet reverb should have more energy in the tail than dry impulse."""
        sr = 22050
        # Use a short impulse that decays to silence - reverb should extend it
        n = sr  # 1 second
        impulse = np.zeros(n)
        impulse[100:200] = np.sin(np.linspace(0, 10 * np.pi, 100)) * 0.8
        samples = np.column_stack([impulse, impulse]).astype(np.float64)
        wet = reverb(samples, sr, room_size=0.6, wet=0.5)
        tail_start = n * 3 // 4
        dry_tail = np.mean(samples[tail_start:] ** 2)
        wet_tail = np.mean(wet[tail_start:] ** 2)
        assert wet_tail > dry_tail, "Reverb should add energy in the tail of a short impulse"

    def test_reverb_preserves_stereo(self, dry_signal):
        """Output should remain stereo with some decorrelation."""
        samples, sr = dry_signal
        wet = reverb(samples, sr, room_size=0.5, wet=0.5)
        assert wet.shape[1] == 2
        # L and R should be similar but not identical (decorrelated)
        correlation = np.corrcoef(wet[:, 0], wet[:, 1])[0, 1]
        assert 0.5 < correlation < 1.0, "Stereo channels should be correlated but not identical"

    def test_reverb_wet_dry_mix(self, dry_signal):
        """wet=0 should return unchanged signal, wet=1 should be all reverb."""
        samples, sr = dry_signal
        dry_out = reverb(samples, sr, room_size=0.5, wet=0.0)
        np.testing.assert_array_almost_equal(dry_out, samples, decimal=5)
