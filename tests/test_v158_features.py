"""Tests for v158.0: spectrogram SVG, CLI viz flags, plugin example, 5 songs."""

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from code_music import Note, Song, Track, to_spectrogram


class TestSpectrogram(unittest.TestCase):
    def _song(self):
        song = Song(title="Test", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="sine"))
        tr.extend([Note("C", 4, 1.0)] * 4)
        return song

    def test_returns_svg(self):
        svg = to_spectrogram(self._song())
        assert "<svg" in svg
        assert "</svg>" in svg

    def test_contains_title(self):
        svg = to_spectrogram(self._song())
        assert "Test" in svg

    def test_contains_rects(self):
        svg = to_spectrogram(self._song())
        assert "<rect" in svg

    def test_custom_dimensions(self):
        svg = to_spectrogram(self._song(), width=600, height=300)
        assert 'width="600"' in svg

    def test_write_to_file(self):
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            to_spectrogram(self._song(), path=f.name)
            content = Path(f.name).read_text()
            assert "<svg" in content
            Path(f.name).unlink()

    def test_empty_song(self):
        song = Song(title="Empty", bpm=120, sample_rate=22050)
        song.add_track(Track())
        svg = to_spectrogram(song)
        assert "<svg" in svg

    def test_import(self):
        from code_music import to_spectrogram as ts

        assert callable(ts)


class TestCLIVizFlags(unittest.TestCase):
    def test_piano_roll_in_help(self):
        from code_music.cli import main

        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                main(["--help"])
            except SystemExit:
                pass
        assert "piano-roll" in (out.getvalue() + err.getvalue()).lower()

    def test_spectrogram_in_help(self):
        from code_music.cli import main

        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                main(["--help"])
            except SystemExit:
                pass
        assert "spectrogram" in (out.getvalue() + err.getvalue()).lower()


class TestPluginExample(unittest.TestCase):
    def test_example_runs(self):
        import importlib.util

        path = Path(__file__).parent.parent / "examples" / "17_plugins.py"
        spec = importlib.util.spec_from_file_location("ex17", str(path))
        mod = importlib.util.module_from_spec(spec)
        out = io.StringIO()
        with redirect_stdout(out):
            spec.loader.exec_module(mod)
        assert "chiptune_lead" in out.getvalue()


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

    def test_chiptune_adventure(self):
        assert isinstance(self._load("chiptune_adventure").song, Song)

    def test_lydian_dreams(self):
        assert isinstance(self._load("lydian_dreams").song, Song)

    def test_diminished_tension(self):
        assert isinstance(self._load("diminished_tension").song, Song)

    def test_bebop_run(self):
        assert isinstance(self._load("bebop_run").song, Song)


if __name__ == "__main__":
    unittest.main()
