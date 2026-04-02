"""Tests for mastering pipeline: LUFS, true peak limiting, dithering, stereo analysis."""

from __future__ import annotations

import numpy as np

from code_music.mastering import (
    dither,
    master_audio,
    measure_lufs,
    normalize_lufs,
    stereo_analysis,
    true_peak_limit,
)

SR = 22050


def _sine_stereo(
    freq: float = 440.0, duration: float = 1.0, sr: int = SR, amp: float = 0.5
) -> np.ndarray:
    """Generate a stereo sine wave for testing."""
    t = np.arange(int(duration * sr)) / sr
    mono = amp * np.sin(2 * np.pi * freq * t)
    return np.column_stack([mono, mono])


class TestLUFS:
    def test_measure_lufs_returns_float(self):
        audio = _sine_stereo()
        lufs = measure_lufs(audio, SR)
        assert isinstance(lufs, float)

    def test_silence_is_very_quiet(self):
        audio = np.zeros((SR, 2))
        lufs = measure_lufs(audio, SR)
        assert lufs <= -60.0

    def test_louder_is_higher_lufs(self):
        quiet = _sine_stereo(amp=0.1)
        loud = _sine_stereo(amp=0.8)
        assert measure_lufs(loud, SR) > measure_lufs(quiet, SR)

    def test_mono_input(self):
        mono = np.sin(2 * np.pi * 440 * np.arange(SR) / SR) * 0.5
        lufs = measure_lufs(mono, SR)
        assert isinstance(lufs, float)


class TestNormalizeLUFS:
    def test_normalize_changes_level(self):
        audio = _sine_stereo(amp=0.1)
        before = measure_lufs(audio, SR)
        normalized = normalize_lufs(audio, SR, target_lufs=-14.0)
        after = measure_lufs(normalized, SR)
        # Should be closer to -14 than before
        assert abs(after - (-14.0)) < abs(before - (-14.0))

    def test_normalize_silence(self):
        audio = np.zeros((SR, 2))
        result = normalize_lufs(audio, SR, target_lufs=-14.0)
        assert np.allclose(result, 0.0)


class TestTruePeakLimit:
    def test_limits_peaks(self):
        # Create audio with a peak > 1.0
        audio = _sine_stereo(amp=1.5)
        limited = true_peak_limit(audio, SR, ceiling_db=-1.0)
        ceiling = 10 ** (-1.0 / 20.0)
        # Most samples should be at or below ceiling (allow small overshoot from smoothing)
        assert np.max(np.abs(limited)) < ceiling * 1.1

    def test_quiet_audio_mostly_unchanged(self):
        audio = _sine_stereo(amp=0.1)
        limited = true_peak_limit(audio, SR, ceiling_db=-1.0)
        # Quiet signal (peak=0.1) well below ceiling (0.89) — energy should be similar
        orig_rms = np.sqrt(np.mean(audio**2))
        lim_rms = np.sqrt(np.mean(limited**2))
        assert abs(orig_rms - lim_rms) / (orig_rms + 1e-10) < 0.5  # within 50% energy

    def test_returns_correct_shape(self):
        audio = _sine_stereo()
        limited = true_peak_limit(audio, SR)
        assert limited.shape == audio.shape


class TestDither:
    def test_dither_adds_noise(self):
        audio = _sine_stereo(amp=0.5)
        dithered = dither(audio, bit_depth=16, seed=42)
        # Should not be identical
        assert not np.allclose(audio, dithered)

    def test_dither_noise_is_small(self):
        audio = _sine_stereo(amp=0.5)
        dithered = dither(audio, bit_depth=16, seed=42)
        diff = np.max(np.abs(audio - dithered))
        # TPDF noise for 16-bit should be tiny
        assert diff < 0.001

    def test_dither_24bit(self):
        audio = _sine_stereo(amp=0.5)
        dithered = dither(audio, bit_depth=24, seed=42)
        diff = np.max(np.abs(audio - dithered))
        assert diff < 0.0001  # 24-bit dither is even smaller

    def test_dither_reproducible(self):
        audio = _sine_stereo()
        a = dither(audio, seed=42)
        b = dither(audio, seed=42)
        np.testing.assert_array_equal(a, b)


class TestStereoAnalysis:
    def test_mono_signal(self):
        t = np.arange(SR) / SR
        mono = np.sin(2 * np.pi * 440 * t) * 0.5
        stereo = np.column_stack([mono, mono])
        result = stereo_analysis(stereo)
        assert abs(result["correlation"] - 1.0) < 0.01
        assert result["width"] < 0.01
        assert abs(result["balance"]) < 0.01

    def test_wide_signal(self):
        t = np.arange(SR) / SR
        left = np.sin(2 * np.pi * 440 * t) * 0.5
        right = np.sin(2 * np.pi * 660 * t) * 0.5  # different freq
        stereo = np.column_stack([left, right])
        result = stereo_analysis(stereo)
        assert result["width"] > 0.1  # should have some width

    def test_panned_signal(self):
        t = np.arange(SR) / SR
        mono = np.sin(2 * np.pi * 440 * t) * 0.5
        stereo = np.column_stack([mono * 0.8, mono * 0.2])  # panned left
        result = stereo_analysis(stereo)
        assert result["balance"] < -0.1  # left-heavy

    def test_1d_input(self):
        mono = np.sin(2 * np.pi * 440 * np.arange(SR) / SR) * 0.5
        result = stereo_analysis(mono)
        assert result["correlation"] == 1.0

    def test_returns_all_keys(self):
        audio = _sine_stereo()
        result = stereo_analysis(audio)
        for key in ["correlation", "width", "balance", "mid_rms", "side_rms"]:
            assert key in result


class TestMasterAudio:
    def test_full_chain(self):
        audio = _sine_stereo(amp=0.3)
        mastered = master_audio(audio, SR, target_lufs=-14.0, ceiling_db=-1.0)
        assert mastered.shape == audio.shape
        assert np.max(np.abs(mastered)) <= 1.0

    def test_mastered_louder_than_quiet_input(self):
        quiet = _sine_stereo(amp=0.05)
        mastered = master_audio(quiet, SR, target_lufs=-14.0)
        assert np.max(np.abs(mastered)) > np.max(np.abs(quiet))

    def test_mastered_with_song(self):
        from code_music import Note, Song, Track

        song = Song(title="Master Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(instrument="piano", volume=0.5))
        tr.add(Note("C", 4, 2.0))
        audio = song.render()
        mastered = master_audio(audio, SR)
        assert mastered.shape == audio.shape
        assert np.max(np.abs(mastered)) <= 1.0
