"""Tests for v152.0: ambisonics, spatial_mix, spatial example."""

import io
import unittest
from contextlib import redirect_stdout

import numpy as np

from code_music import (
    Note,
    Song,
    Track,
    decode_bformat,
    encode_bformat,
    spatial_mix,
    sum_bformat,
)

# ---------------------------------------------------------------------------
# encode_bformat
# ---------------------------------------------------------------------------


class TestEncodeBformat(unittest.TestCase):
    """Encode mono to first-order ambisonics B-format."""

    def test_output_shape(self):
        mono = np.random.randn(22050) * 0.1
        bf = encode_bformat(mono, azimuth=45)
        assert bf.shape == (22050, 4)

    def test_center_front(self):
        mono = np.ones(1000) * 0.5
        bf = encode_bformat(mono, azimuth=0, elevation=0)
        # Front-center: X should be positive, Y near zero
        assert np.mean(bf[:, 1]) > 0  # X (front)
        assert abs(np.mean(bf[:, 2])) < 0.01  # Y (left-right) near zero

    def test_hard_left(self):
        mono = np.ones(1000) * 0.5
        bf = encode_bformat(mono, azimuth=90)
        # Left: Y should be positive
        assert np.mean(bf[:, 2]) > 0

    def test_above(self):
        mono = np.ones(1000) * 0.5
        bf = encode_bformat(mono, azimuth=0, elevation=90)
        # Above: Z should be positive
        assert np.mean(bf[:, 3]) > 0

    def test_distance_attenuates(self):
        mono = np.ones(1000) * 0.5
        close = encode_bformat(mono, distance=1.0)
        far = encode_bformat(mono, distance=5.0)
        assert np.max(np.abs(far)) < np.max(np.abs(close))

    def test_stereo_input_converted(self):
        stereo = np.random.randn(1000, 2) * 0.1
        bf = encode_bformat(stereo, azimuth=30)
        assert bf.shape == (1000, 4)


# ---------------------------------------------------------------------------
# sum_bformat
# ---------------------------------------------------------------------------


class TestSumBformat(unittest.TestCase):
    """Sum multiple B-format signals."""

    def test_sum_two(self):
        a = np.random.randn(1000, 4) * 0.1
        b = np.random.randn(1000, 4) * 0.1
        result = sum_bformat(a, b)
        assert result.shape == (1000, 4)
        np.testing.assert_array_almost_equal(result, a + b)

    def test_sum_different_lengths(self):
        a = np.random.randn(1000, 4) * 0.1
        b = np.random.randn(800, 4) * 0.1
        result = sum_bformat(a, b)
        assert result.shape == (800, 4)  # truncates to shortest

    def test_sum_empty_raises(self):
        with self.assertRaises(ValueError):
            sum_bformat()


# ---------------------------------------------------------------------------
# decode_bformat
# ---------------------------------------------------------------------------


class TestDecodeBformat(unittest.TestCase):
    """Decode B-format to speaker layouts."""

    def _bformat(self, n=22050):
        mono = np.random.randn(n) * 0.1
        return encode_bformat(mono, azimuth=30)

    def test_binaural(self):
        result = decode_bformat(self._bformat(), "binaural")
        assert result.shape == (22050, 2)

    def test_stereo(self):
        result = decode_bformat(self._bformat(), "stereo")
        assert result.shape == (22050, 2)

    def test_quad(self):
        result = decode_bformat(self._bformat(), "quad")
        assert result.shape == (22050, 4)

    def test_surround_51(self):
        result = decode_bformat(self._bformat(), "5.1")
        assert result.shape == (22050, 6)

    def test_unknown_layout_raises(self):
        with self.assertRaises(ValueError):
            decode_bformat(self._bformat(), "7.1")

    def test_round_trip_not_silent(self):
        mono = np.sin(np.linspace(0, 440 * 2 * np.pi, 22050)) * 0.3
        bf = encode_bformat(mono, azimuth=45)
        decoded = decode_bformat(bf, "stereo")
        assert np.max(np.abs(decoded)) > 0.01


# ---------------------------------------------------------------------------
# spatial_mix
# ---------------------------------------------------------------------------


class TestSpatialMix(unittest.TestCase):
    """Render Song with spatial positioning."""

    def test_basic_render(self):
        song = Song(title="3D", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(spatial_azimuth=45))
        tr.add(Note("C", 4, 2.0))
        audio = spatial_mix(song, 22050)
        assert audio.shape[1] == 2
        assert np.max(np.abs(audio)) > 0.001

    def test_mixed_spatial_and_stereo(self):
        song = Song(title="Mix", bpm=120, sample_rate=22050)
        spatial_tr = song.add_track(Track(name="spatial", spatial_azimuth=-30))
        spatial_tr.add(Note("C", 4, 2.0))
        stereo_tr = song.add_track(Track(name="stereo", pan=0.5))
        stereo_tr.add(Note("E", 4, 2.0))
        audio = spatial_mix(song, 22050)
        assert audio.shape[1] == 2

    def test_quad_output(self):
        song = Song(title="Quad", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(spatial_azimuth=90))
        tr.add(Note("C", 4, 2.0))
        audio = spatial_mix(song, 22050, layout="quad")
        assert audio.shape[1] == 4

    def test_surround_output(self):
        song = Song(title="5.1", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(spatial_azimuth=0))
        tr.add(Note("C", 4, 2.0))
        audio = spatial_mix(song, 22050, layout="5.1")
        assert audio.shape[1] == 6

    def test_orbit_track(self):
        song = Song(title="Orbit", bpm=120, sample_rate=22050)
        tr = song.add_track(
            Track(
                spatial_azimuth=0,
                spatial_orbit_rate=0.5,
            )
        )
        tr.add(Note("C", 4, 2.0))
        audio = spatial_mix(song, 22050)
        assert audio.shape[1] == 2


# ---------------------------------------------------------------------------
# Spatial example
# ---------------------------------------------------------------------------


class TestSpatialExample(unittest.TestCase):
    """examples/16_spatial.py runs cleanly."""

    def test_example_runs(self):
        import importlib.util
        from pathlib import Path

        example = Path(__file__).parent.parent / "examples" / "16_spatial.py"
        spec = importlib.util.spec_from_file_location("example_16", str(example))
        mod = importlib.util.module_from_spec(spec)
        out = io.StringIO()
        with redirect_stdout(out):
            spec.loader.exec_module(mod)
        output = out.getvalue()
        assert "B-format" in output
        assert "binaural" in output.lower()


# ---------------------------------------------------------------------------
# Import verification
# ---------------------------------------------------------------------------


class TestSpatialImports(unittest.TestCase):
    """All spatial functions importable from top level."""

    def test_imports(self):
        from code_music import (
            decode_bformat,
            encode_bformat,
            orbit,
            spatial_mix,
            spatial_pan,
            sum_bformat,
        )

        for fn in [decode_bformat, encode_bformat, orbit, spatial_mix, spatial_pan, sum_bformat]:
            assert callable(fn)


if __name__ == "__main__":
    unittest.main()
