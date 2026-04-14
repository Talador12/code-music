"""Tests for v164.0: examples 18-19, README update, 5 new songs."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from code_music import Song


class TestExamples(unittest.TestCase):
    """New examples run without errors."""

    def _run_example(self, name):
        import importlib.util

        path = Path(__file__).parent.parent / "examples" / f"{name}.py"
        spec = importlib.util.spec_from_file_location(name, str(path))
        mod = importlib.util.module_from_spec(spec)
        out = io.StringIO()
        with redirect_stdout(out):
            spec.loader.exec_module(mod)
        return out.getvalue()

    def test_18_structure(self):
        output = self._run_example("18_structure")
        assert "Sonata" in output
        assert "fill_tracks" in output.lower() or "Before" in output

    def test_19_visualization(self):
        output = self._run_example("19_visualization")
        assert "Piano Roll" in output
        assert "Spectrogram" in output
        assert "Sheet Music" in output


class TestReadme(unittest.TestCase):
    """README has updated stats."""

    def test_readme_has_400_songs(self):
        readme = Path(__file__).parent.parent.joinpath("README.md").read_text()
        assert "400" in readme

    def test_readme_has_19_examples(self):
        readme = Path(__file__).parent.parent.joinpath("README.md").read_text()
        assert "19" in readme


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

    def test_west_african_kora(self):
        assert isinstance(self._load("west_african_kora").song, Song)

    def test_nordic_folk(self):
        assert isinstance(self._load("nordic_folk").song, Song)

    def test_carnival_samba(self):
        assert isinstance(self._load("carnival_samba").song, Song)

    def test_space_ambient_v2(self):
        assert isinstance(self._load("space_ambient_v2").song, Song)

    def test_klezmer_dance(self):
        assert isinstance(self._load("klezmer_dance").song, Song)


if __name__ == "__main__":
    unittest.main()
