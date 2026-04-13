"""Tests for v142.0: cross-synthesis, wavetable scanning, bowed string model."""

import unittest

import numpy as np

from code_music.effects import cross_synthesis
from code_music.sound_design import PRESETS, SoundDesigner, Wavetable

# ---------------------------------------------------------------------------
# Cross-synthesis
# ---------------------------------------------------------------------------


class TestCrossSynthesis(unittest.TestCase):
    """FFT-based cross-synthesis: magnitude from target, phase from source."""

    def test_returns_same_shape(self):
        src = np.random.randn(22050, 2) * 0.1
        tgt = np.random.randn(22050, 2) * 0.1
        out = cross_synthesis(src, tgt, 22050)
        assert out.shape == src.shape

    def test_mono(self):
        src = np.random.randn(22050) * 0.1
        tgt = np.random.randn(22050) * 0.1
        out = cross_synthesis(src, tgt, 22050)
        assert out.ndim == 1
        assert out.shape[0] == src.shape[0]

    def test_blend_zero_is_source(self):
        src = np.random.randn(4096, 2) * 0.1
        tgt = np.random.randn(4096, 2) * 0.1
        out = cross_synthesis(src, tgt, 22050, blend=0.0, wet=1.0)
        # With blend=0, should be close to source (only phase, source magnitude)
        assert out.shape == src.shape

    def test_wet_zero_is_dry(self):
        src = np.random.randn(4096, 2) * 0.1
        tgt = np.random.randn(4096, 2) * 0.1
        out = cross_synthesis(src, tgt, 22050, wet=0.0)
        np.testing.assert_array_almost_equal(out, src, decimal=10)

    def test_different_lengths_truncates(self):
        src = np.random.randn(10000, 2) * 0.1
        tgt = np.random.randn(8000, 2) * 0.1
        out = cross_synthesis(src, tgt, 22050)
        assert out.shape[0] == 8000

    def test_output_not_silent(self):
        src = np.sin(np.linspace(0, 440 * 2 * np.pi, 22050))
        src = np.column_stack([src, src])
        tgt = np.random.randn(22050, 2) * 0.3
        out = cross_synthesis(src, tgt, 22050)
        assert np.max(np.abs(out)) > 0.001

    def test_custom_fft_size(self):
        src = np.random.randn(22050, 2) * 0.1
        tgt = np.random.randn(22050, 2) * 0.1
        out = cross_synthesis(src, tgt, 22050, fft_size=4096)
        assert out.shape == src.shape


# ---------------------------------------------------------------------------
# Wavetable scanning
# ---------------------------------------------------------------------------


class TestWavetableScan(unittest.TestCase):
    """LFO-modulated wavetable position for evolving timbres."""

    def test_scan_renders(self):
        bank = [
            Wavetable.from_wave("sine"),
            Wavetable.from_wave("sawtooth"),
            Wavetable.from_wave("square"),
        ]
        sd = SoundDesigner("scanner").wavetable_scan(bank, scan_rate=0.5)
        audio = sd.render(440.0, 1.0, 22050)
        assert len(audio) > 0
        assert np.max(np.abs(audio)) > 0.001

    def test_scan_different_rates(self):
        bank = [Wavetable.from_wave("sine"), Wavetable.from_wave("sawtooth")]
        slow = SoundDesigner("s").wavetable_scan(bank, scan_rate=0.1).render(440.0, 1.0, 22050)
        fast = SoundDesigner("f").wavetable_scan(bank, scan_rate=5.0).render(440.0, 1.0, 22050)
        # Should produce different audio
        assert not np.array_equal(slow, fast)

    def test_scan_requires_two_tables(self):
        with self.assertRaises(ValueError):
            SoundDesigner("x").wavetable_scan([Wavetable.from_wave("sine")])

    def test_scan_many_tables(self):
        bank = [Wavetable.from_harmonics([1.0 / (i + 1) for i in range(8)]) for _ in range(8)]
        sd = SoundDesigner("many").wavetable_scan(bank, scan_rate=1.0)
        audio = sd.render(220.0, 0.5, 22050)
        assert len(audio) > 0

    def test_scan_with_detune(self):
        bank = [Wavetable.from_wave("sine"), Wavetable.from_wave("square")]
        sd = SoundDesigner("d").wavetable_scan(bank, detune_cents=10)
        audio = sd.render(440.0, 1.0, 22050)
        assert len(audio) > 0

    def test_scan_chaining(self):
        bank = [Wavetable.from_wave("sine"), Wavetable.from_wave("sawtooth")]
        sd = (
            SoundDesigner("chain")
            .wavetable_scan(bank, scan_rate=0.5)
            .envelope(attack=0.01, decay=0.1, sustain=0.8, release=0.2)
            .filter("lowpass", cutoff=3000, resonance=0.5)
        )
        audio = sd.render(440.0, 1.0, 22050)
        assert len(audio) > 0


# ---------------------------------------------------------------------------
# Bowed string physical model
# ---------------------------------------------------------------------------


class TestBowedString(unittest.TestCase):
    """Bowed string physical model with sustained excitation."""

    def test_renders(self):
        sd = SoundDesigner("violin").physical_model("bowed_string")
        audio = sd.render(440.0, 1.0, 22050)
        assert len(audio) > 0
        assert np.max(np.abs(audio)) > 0.001

    def test_different_bow_pressures(self):
        gentle = (
            SoundDesigner("g")
            .physical_model("bowed_string", bow_pressure=0.1)
            .render(440.0, 0.5, 22050)
        )
        forceful = (
            SoundDesigner("f")
            .physical_model("bowed_string", bow_pressure=0.9)
            .render(440.0, 0.5, 22050)
        )
        # Different pressures should produce different audio
        assert not np.array_equal(gentle, forceful)

    def test_brightness_control(self):
        dark = (
            SoundDesigner("d")
            .physical_model("bowed_string", brightness=0.1)
            .render(440.0, 0.5, 22050)
        )
        bright = (
            SoundDesigner("b")
            .physical_model("bowed_string", brightness=0.9)
            .render(440.0, 0.5, 22050)
        )
        assert not np.array_equal(dark, bright)

    def test_different_pitches(self):
        low = SoundDesigner("l").physical_model("bowed_string").render(220.0, 0.5, 22050)
        high = SoundDesigner("h").physical_model("bowed_string").render(880.0, 0.5, 22050)
        assert not np.array_equal(low, high)

    def test_preset_exists(self):
        assert "pm_violin" in PRESETS
        audio = PRESETS["pm_violin"].render(440.0, 1.0, 22050)
        assert len(audio) > 0

    def test_in_physical_models_set(self):
        from code_music.sound_design import _PHYSICAL_MODELS

        assert "bowed_string" in _PHYSICAL_MODELS

    def test_invalid_model_rejected(self):
        with self.assertRaises(ValueError):
            SoundDesigner("x").physical_model("nonexistent_model")


if __name__ == "__main__":
    unittest.main()
