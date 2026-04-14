"""Tests for v156.0: chord gallery, progression gallery, 5 new songs."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from code_music import Song


class TestGalleryPages(unittest.TestCase):
    def test_chords_html_exists(self):
        assert (Path(__file__).parent.parent / "docs" / "chords.html").exists()

    def test_chords_has_shapes(self):
        content = (Path(__file__).parent.parent / "docs" / "chords.html").read_text()
        for shape in ["Cmaj", "Cmin", "Cdim", "Caug", "Cmaj7", "Cdom7"]:
            assert shape in content, f"{shape} not in chords.html"

    def test_progressions_html_exists(self):
        assert (Path(__file__).parent.parent / "docs" / "progressions.html").exists()

    def test_progressions_has_names(self):
        content = (Path(__file__).parent.parent / "docs" / "progressions.html").read_text()
        for name in ["I-IV-V-I", "ii-V-I", "12-bar blues"]:
            assert name in content, f"{name} not in progressions.html"

    def test_progressions_has_audio(self):
        content = (Path(__file__).parent.parent / "docs" / "progressions.html").read_text()
        assert "data:audio/wav" in content


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

    def test_pachelbel_canon(self):
        assert isinstance(self._load("pachelbel_canon").song, Song)

    def test_pentatonic_jam(self):
        assert isinstance(self._load("pentatonic_jam").song, Song)

    def test_hungarian_minor(self):
        assert isinstance(self._load("hungarian_minor").song, Song)

    def test_neapolitan(self):
        assert isinstance(self._load("neapolitan").song, Song)

    def test_enigmatic_scale(self):
        assert isinstance(self._load("enigmatic_scale").song, Song)


if __name__ == "__main__":
    unittest.main()
