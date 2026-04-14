"""Tests for v155.0: technique gallery, scale gallery, 5 new songs."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from code_music import Song


class TestGalleryPages(unittest.TestCase):
    """Gallery HTML pages exist and contain expected content."""

    def test_techniques_html_exists(self):
        p = Path(__file__).parent.parent / "docs" / "techniques.html"
        assert p.exists()

    def test_techniques_has_all_methods(self):
        p = Path(__file__).parent.parent / "docs" / "techniques.html"
        content = p.read_text()
        for name in ["Subtractive", "FM Synthesis", "Wavetable", "Granular", "Bowed"]:
            assert name in content, f"{name} not in techniques.html"

    def test_scales_html_exists(self):
        p = Path(__file__).parent.parent / "docs" / "scales.html"
        assert p.exists()

    def test_scales_has_categories(self):
        p = Path(__file__).parent.parent / "docs" / "scales.html"
        content = p.read_text()
        for cat in ["Diatonic", "Modal", "Pentatonic"]:
            assert cat in content, f"{cat} not in scales.html"

    def test_scales_has_audio(self):
        p = Path(__file__).parent.parent / "docs" / "scales.html"
        content = p.read_text()
        assert "data:audio/wav" in content


class TestNewSongs(unittest.TestCase):
    """5 new songs load cleanly."""

    def _load(self, name):
        import importlib.util

        path = Path(__file__).parent.parent / "songs" / f"{name}.py"
        spec = importlib.util.spec_from_file_location(name, str(path))
        mod = importlib.util.module_from_spec(spec)
        out = io.StringIO()
        with redirect_stdout(out):
            spec.loader.exec_module(mod)
        return mod

    def test_fm_bells(self):
        mod = self._load("fm_bells")
        assert isinstance(mod.song, Song)

    def test_granular_clouds(self):
        mod = self._load("granular_clouds")
        assert isinstance(mod.song, Song)

    def test_rock_anthem(self):
        mod = self._load("rock_anthem")
        assert isinstance(mod.song, Song)
        assert len(mod.song.tracks) >= 5

    def test_modal_exploration(self):
        mod = self._load("modal_exploration")
        assert isinstance(mod.song, Song)

    def test_plugin_demo(self):
        mod = self._load("plugin_demo")
        assert isinstance(mod.song, Song)


if __name__ == "__main__":
    unittest.main()
