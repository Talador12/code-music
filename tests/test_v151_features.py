"""Tests for v151.0: spatial audio, harmonic rhythm SVG, 5 new songs."""

import io
import unittest
from contextlib import redirect_stdout

import numpy as np

from code_music import Chord, Song, Track, to_harmonic_rhythm
from code_music.effects import orbit, spatial_pan

# ---------------------------------------------------------------------------
# spatial_pan
# ---------------------------------------------------------------------------


class TestSpatialPan(unittest.TestCase):
    """Binaural 3D panning via ITD + ILD."""

    def test_returns_stereo(self):
        mono = np.random.randn(22050) * 0.1
        result = spatial_pan(mono, 22050, azimuth=45)
        assert result.shape == (22050, 2)

    def test_center_balanced(self):
        mono = np.ones(22050) * 0.5
        result = spatial_pan(mono, 22050, azimuth=0)
        # Center should have roughly equal power in both channels
        left_rms = np.sqrt(np.mean(result[:, 0] ** 2))
        right_rms = np.sqrt(np.mean(result[:, 1] ** 2))
        assert abs(left_rms - right_rms) < 0.1

    def test_right_panned_has_level_diff(self):
        mono = np.ones(22050) * 0.5
        result = spatial_pan(mono, 22050, azimuth=90)
        left_rms = np.sqrt(np.mean(result[:, 0] ** 2))
        right_rms = np.sqrt(np.mean(result[:, 1] ** 2))
        # Hard right panning should create a level difference
        assert abs(left_rms - right_rms) > 0.01

    def test_distance_attenuates(self):
        mono = np.ones(22050) * 0.5
        close = spatial_pan(mono, 22050, distance=1.0)
        far = spatial_pan(mono, 22050, distance=5.0)
        assert np.max(np.abs(far)) < np.max(np.abs(close))

    def test_stereo_input(self):
        stereo = np.random.randn(22050, 2) * 0.1
        result = spatial_pan(stereo, 22050, azimuth=-30)
        assert result.shape == (22050, 2)

    def test_elevation(self):
        mono = np.random.randn(22050) * 0.1
        result = spatial_pan(mono, 22050, elevation=45)
        assert result.shape == (22050, 2)

    def test_behind(self):
        mono = np.random.randn(22050) * 0.1
        result = spatial_pan(mono, 22050, azimuth=150)
        assert result.shape == (22050, 2)


# ---------------------------------------------------------------------------
# orbit
# ---------------------------------------------------------------------------


class TestOrbit(unittest.TestCase):
    """Sound orbits the listener's head."""

    def test_returns_stereo(self):
        mono = np.random.randn(22050) * 0.1
        result = orbit(mono, 22050, rate=0.5, radius=2.0)
        assert result.shape == (22050, 2)

    def test_stereo_input(self):
        stereo = np.random.randn(22050, 2) * 0.1
        result = orbit(stereo, 22050, rate=0.25)
        assert result.shape == (22050, 2)

    def test_different_rates(self):
        mono = np.random.randn(22050) * 0.1
        slow = orbit(mono, 22050, rate=0.1)
        fast = orbit(mono, 22050, rate=2.0)
        assert not np.array_equal(slow, fast)


# ---------------------------------------------------------------------------
# Track spatial attributes
# ---------------------------------------------------------------------------


class TestTrackSpatial(unittest.TestCase):
    """Track has spatial audio attributes."""

    def test_default_no_spatial(self):
        tr = Track()
        assert tr.spatial_azimuth is None

    def test_set_spatial(self):
        tr = Track(spatial_azimuth=45, spatial_elevation=10, spatial_distance=2.0)
        assert tr.spatial_azimuth == 45
        assert tr.spatial_elevation == 10
        assert tr.spatial_distance == 2.0

    def test_orbit_rate(self):
        tr = Track(spatial_orbit_rate=0.5)
        assert tr.spatial_orbit_rate == 0.5


# ---------------------------------------------------------------------------
# to_harmonic_rhythm
# ---------------------------------------------------------------------------


class TestHarmonicRhythm(unittest.TestCase):
    """Harmonic rhythm SVG timeline."""

    def test_returns_svg(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track())
        tr.add(Chord("C", "maj", 4, duration=4.0))
        svg = to_harmonic_rhythm(song)
        assert "<svg" in svg

    def test_contains_chord_label(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track())
        tr.add(Chord("C", "maj", 4, duration=8.0))
        svg = to_harmonic_rhythm(song)
        assert "Cmaj" in svg

    def test_multiple_chords(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track())
        for root in ["C", "F", "G"]:
            tr.add(Chord(root, "maj", 4, duration=4.0))
        svg = to_harmonic_rhythm(song)
        assert svg.count("<rect") >= 4  # bg + 3 chord rects

    def test_empty_song(self):
        song = Song(title="Empty", bpm=120)
        song.add_track(Track())
        svg = to_harmonic_rhythm(song)
        assert "No chords" in svg

    def test_import(self):
        from code_music import to_harmonic_rhythm as thr

        assert callable(thr)


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

    def test_spatial_orbit(self):
        mod = self._load("spatial_orbit")
        assert isinstance(mod.song, Song)

    def test_binaural_jazz(self):
        mod = self._load("binaural_jazz")
        assert isinstance(mod.song, Song)

    def test_harmonic_viz(self):
        mod = self._load("harmonic_viz")
        assert isinstance(mod.song, Song)

    def test_classical_fugue(self):
        mod = self._load("classical_fugue")
        assert isinstance(mod.song, Song)

    def test_verse_chorus_pop(self):
        mod = self._load("verse_chorus_pop")
        assert isinstance(mod.song, Song)


if __name__ == "__main__":
    unittest.main()
