"""Tests for v149.0: piano roll visualizer, API docs refresh, 5 new songs."""

import io
import unittest
from contextlib import redirect_stdout

from code_music import Chord, Note, Song, Track, to_piano_roll

# ---------------------------------------------------------------------------
# to_piano_roll
# ---------------------------------------------------------------------------


class TestPianoRoll(unittest.TestCase):
    """Piano roll SVG visualizer."""

    def _song(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.extend([Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)])
        return song

    def test_returns_svg_string(self):
        svg = to_piano_roll(self._song())
        assert "<svg" in svg
        assert "</svg>" in svg

    def test_contains_note_rects(self):
        svg = to_piano_roll(self._song())
        assert "<rect" in svg

    def test_contains_title(self):
        svg = to_piano_roll(self._song())
        assert "Test" in svg

    def test_contains_track_legend(self):
        svg = to_piano_roll(self._song())
        assert "lead" in svg

    def test_multi_track(self):
        song = Song(title="Multi", bpm=120)
        lead = song.add_track(Track(name="lead", instrument="piano"))
        lead.add(Note("C", 5, 1.0))
        bass = song.add_track(Track(name="bass", instrument="bass"))
        bass.add(Note("C", 2, 1.0))
        svg = to_piano_roll(song)
        assert "lead" in svg
        assert "bass" in svg

    def test_with_chords(self):
        song = Song(title="Chords", bpm=120)
        tr = song.add_track(Track(name="chords", instrument="piano"))
        tr.add(Chord("C", "maj", 4, duration=2.0))
        svg = to_piano_roll(song)
        assert "<rect" in svg

    def test_empty_song(self):
        song = Song(title="Empty", bpm=120)
        song.add_track(Track())
        svg = to_piano_roll(song)
        assert "No notes" in svg

    def test_custom_dimensions(self):
        svg = to_piano_roll(self._song(), width=600, height=300)
        assert 'width="600"' in svg
        assert 'height="300"' in svg

    def test_write_to_file(self):
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            to_piano_roll(self._song(), path=f.name)
            content = Path(f.name).read_text()
            assert "<svg" in content
            Path(f.name).unlink()

    def test_grid_lines(self):
        svg = to_piano_roll(self._song())
        assert "<line" in svg  # grid lines

    def test_import_from_top_level(self):
        from code_music import to_piano_roll as tpr

        assert callable(tpr)


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

    def test_jazz_waltz(self):
        mod = self._load("jazz_waltz")
        assert isinstance(mod.song, Song)
        assert len(mod.song.tracks) >= 3

    def test_ambient_drone(self):
        mod = self._load("ambient_drone")
        assert isinstance(mod.song, Song)

    def test_funk_groove(self):
        mod = self._load("funk_groove")
        assert isinstance(mod.song, Song)
        assert len(mod.song.tracks) >= 5

    def test_rondo_in_g(self):
        mod = self._load("rondo_in_g")
        assert isinstance(mod.song, Song)

    def test_theme_vars(self):
        mod = self._load("theme_vars")
        assert isinstance(mod.song, Song)


if __name__ == "__main__":
    unittest.main()
