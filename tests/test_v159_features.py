"""Tests for v159.0: per-track waveforms, make visualize-all, 5 new songs."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from code_music import Note, Song, Track, to_track_waveforms


class TestTrackWaveforms(unittest.TestCase):
    def _song(self):
        song = Song(title="Test", bpm=120, sample_rate=22050)
        lead = song.add_track(Track(name="lead", instrument="sine"))
        lead.extend([Note("C", 4, 1.0)] * 4)
        bass = song.add_track(Track(name="bass", instrument="bass"))
        bass.extend([Note("C", 2, 2.0)] * 2)
        return song

    def test_returns_svg(self):
        svg = to_track_waveforms(self._song())
        assert "<svg" in svg and "</svg>" in svg

    def test_contains_track_names(self):
        svg = to_track_waveforms(self._song())
        assert "lead" in svg
        assert "bass" in svg

    def test_contains_polygons(self):
        svg = to_track_waveforms(self._song())
        assert "<polygon" in svg

    def test_empty_song(self):
        song = Song(title="Empty", bpm=120, sample_rate=22050)
        svg = to_track_waveforms(song)
        assert "No tracks" in svg

    def test_single_track(self):
        song = Song(title="One", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(name="only", instrument="sine"))
        tr.add(Note("C", 4, 2.0))
        svg = to_track_waveforms(song)
        assert "only" in svg

    def test_write_to_file(self):
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            to_track_waveforms(self._song(), path=f.name)
            content = Path(f.name).read_text()
            assert "<svg" in content
            Path(f.name).unlink()

    def test_custom_height(self):
        svg = to_track_waveforms(self._song(), track_height=120)
        assert "<svg" in svg

    def test_import(self):
        from code_music import to_track_waveforms as ttw

        assert callable(ttw)


class TestMakefileVisualize(unittest.TestCase):
    def test_target_exists(self):
        content = Path(__file__).parent.parent.joinpath("Makefile").read_text()
        assert "visualize-all:" in content
        assert "dist/viz" in content


class TestNewSongs(unittest.TestCase):
    def _load(self, name):
        import importlib.util

        path = Path(__file__).parent.parent / "songs" / f"{name}.py"
        spec = importlib.util.spec_from_file_location(name, str(path))
        mod = importlib.util.module_from_spec(spec)
        out = io.StringIO()
        with redirect_stdout(out):
            spec.loader.exec_module(mod)
        return mod

    def test_phrygian_metal(self):
        assert isinstance(self._load("phrygian_metal").song, Song)

    def test_persian_night(self):
        assert isinstance(self._load("persian_night").song, Song)

    def test_japanese_garden(self):
        assert isinstance(self._load("japanese_garden").song, Song)

    def test_dorian_groove(self):
        assert isinstance(self._load("dorian_groove").song, Song)

    def test_arabic_nights(self):
        assert isinstance(self._load("arabic_nights").song, Song)


if __name__ == "__main__":
    unittest.main()
