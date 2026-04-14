"""Tests for v147.0: 5 new showcase songs."""

import io
import unittest
from contextlib import redirect_stdout

from code_music import Song


class TestNewSongs(unittest.TestCase):
    """All new songs define a `song` variable and load cleanly."""

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

    def test_bowed_quartet(self):
        mod = self._load("bowed_quartet")
        assert isinstance(mod.song, Song)
        assert len(mod.song.tracks) >= 4

    def test_wavetable_morphing(self):
        mod = self._load("wavetable_morphing")
        assert isinstance(mod.song, Song)
        assert len(mod.song.tracks) >= 3

    def test_auto_band(self):
        mod = self._load("auto_band")
        assert isinstance(mod.song, Song)
        assert len(mod.song.tracks) >= 3

    def test_spectral_blend(self):
        mod = self._load("spectral_blend")
        assert isinstance(mod.song, Song)
        assert len(mod.song.tracks) >= 3

    def test_form_showcase(self):
        mod = self._load("form_showcase")
        assert isinstance(mod.song, Song)
        assert len(mod.song.tracks) >= 2


if __name__ == "__main__":
    unittest.main()
