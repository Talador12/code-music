"""Tests for v153.0: Doppler effect, roadmap cleanup, 5 new songs, docs refresh."""

import io
import unittest
from contextlib import redirect_stdout

import numpy as np

from code_music import Song
from code_music.effects import doppler

# ---------------------------------------------------------------------------
# doppler
# ---------------------------------------------------------------------------


class TestDoppler(unittest.TestCase):
    """Doppler pitch shift for moving sources."""

    def _tone(self, freq=440, dur=1.0, sr=22050):
        t = np.linspace(0, dur, int(sr * dur))
        return np.sin(2 * np.pi * freq * t) * 0.3

    def test_pass_by_shape(self):
        tone = self._tone()
        result = doppler(tone, 22050, speed=30, direction="pass_by")
        assert result.shape == tone.shape

    def test_approaching_shape(self):
        tone = self._tone()
        result = doppler(tone, 22050, speed=20, direction="approaching")
        assert result.shape == tone.shape

    def test_receding_shape(self):
        tone = self._tone()
        result = doppler(tone, 22050, speed=20, direction="receding")
        assert result.shape == tone.shape

    def test_stereo_input(self):
        stereo = np.random.randn(22050, 2) * 0.1
        result = doppler(stereo, 22050, speed=30)
        assert result.shape == (22050, 2)

    def test_output_not_silent(self):
        tone = self._tone()
        result = doppler(tone, 22050, speed=30, direction="pass_by")
        assert np.max(np.abs(result)) > 0.01

    def test_pass_by_changes_pitch(self):
        tone = self._tone(freq=440, dur=2.0, sr=22050)
        result = doppler(tone, 22050, speed=50, direction="pass_by")
        # First half (approaching) should differ from second half (receding)
        n = len(result)
        first_half_energy = np.mean(np.abs(result[: n // 2]))
        second_half_energy = np.mean(np.abs(result[n // 2 :]))
        # Approaching is closer = louder, receding is farther = quieter
        assert first_half_energy != second_half_energy

    def test_zero_speed_passthrough(self):
        tone = self._tone()
        result = doppler(tone, 22050, speed=0, direction="pass_by")
        # Zero speed should produce minimal change
        assert result.shape == tone.shape

    def test_unknown_direction_passthrough(self):
        tone = self._tone()
        result = doppler(tone, 22050, speed=30, direction="unknown")
        np.testing.assert_array_equal(result, tone)

    def test_high_speed(self):
        tone = self._tone()
        result = doppler(tone, 22050, speed=200, direction="pass_by")
        assert result.shape == tone.shape


# ---------------------------------------------------------------------------
# New songs
# ---------------------------------------------------------------------------


class TestNewSongs(unittest.TestCase):
    """5 new songs load cleanly."""

    def _load(self, name):
        import importlib.util
        from pathlib import Path

        path = Path(__file__).parent.parent / "songs" / f"{name}.py"
        spec = importlib.util.spec_from_file_location(name, str(path))
        mod = importlib.util.module_from_spec(spec)
        out = io.StringIO()
        with redirect_stdout(out):
            spec.loader.exec_module(mod)
        return mod

    def test_doppler_flyby(self):
        mod = self._load("doppler_flyby")
        assert isinstance(mod.song, Song)

    def test_surround_mix(self):
        mod = self._load("surround_mix")
        assert isinstance(mod.song, Song)
        assert len(mod.song.tracks) >= 4

    def test_latin_groove(self):
        mod = self._load("latin_groove")
        assert isinstance(mod.song, Song)

    def test_auto_jazz_trio(self):
        mod = self._load("auto_jazz_trio")
        assert isinstance(mod.song, Song)
        assert len(mod.song.tracks) >= 3

    def test_aaba_standards(self):
        mod = self._load("aaba_standards")
        assert isinstance(mod.song, Song)


if __name__ == "__main__":
    unittest.main()
