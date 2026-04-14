"""Tests for v150.0: Song.analyze(), generate_full_song bridge modulation, 5 new songs."""

import io
import unittest
from contextlib import redirect_stdout

from code_music import Note, Song, Track
from code_music.theory import generate_full_song

# ---------------------------------------------------------------------------
# Song.analyze()
# ---------------------------------------------------------------------------


class TestSongAnalyze(unittest.TestCase):
    """Song.analyze() returns comprehensive musical analysis."""

    def _song(self):
        from code_music import Chord

        song = Song(title="Test", bpm=120, key_sig="C")
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.extend([Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)])
        ch = song.add_track(Track(name="chords", instrument="pad"))
        ch.add(Chord("C", "maj", 4, duration=3.0))
        return song

    def test_returns_dict(self):
        result = self._song().analyze()
        assert isinstance(result, dict)

    def test_has_info(self):
        result = self._song().analyze()
        assert "info" in result
        assert result["info"]["title"] == "Test"

    def test_has_harmonic(self):
        result = self._song().analyze()
        assert "harmonic" in result
        assert result["harmonic"]["chord_count"] >= 1

    def test_has_melodic(self):
        result = self._song().analyze()
        assert "melodic" in result
        assert result["melodic"]["note_count"] >= 3

    def test_has_rhythmic(self):
        result = self._song().analyze()
        assert "rhythmic" in result

    def test_has_arrangement(self):
        result = self._song().analyze()
        assert "arrangement" in result

    def test_has_fingerprint(self):
        result = self._song().analyze()
        assert "fingerprint" in result

    def test_empty_song(self):
        song = Song(title="Empty", bpm=120)
        song.add_track(Track())
        result = song.analyze()
        assert result["melodic"]["note_count"] == 0
        assert result["harmonic"]["chord_count"] == 0

    def test_generated_song(self):
        song = generate_full_song("pop", key="C", bpm=120, seed=42)
        result = song.analyze()
        assert result["info"]["tracks"] >= 3
        assert result["harmonic"]["chord_count"] > 0


# ---------------------------------------------------------------------------
# generate_full_song bridge modulation
# ---------------------------------------------------------------------------


class TestBridgeModulation(unittest.TestCase):
    """generate_full_song modulates bridge to related key."""

    def test_modulate_bridge_default(self):
        song = generate_full_song(
            "pop",
            key="C",
            bpm=120,
            sections=["verse", "chorus", "bridge", "chorus"],
            modulate_bridge=True,
            seed=42,
        )
        assert isinstance(song, Song)
        assert len(song.tracks) >= 3

    def test_no_modulate(self):
        song = generate_full_song(
            "pop",
            key="C",
            bpm=120,
            sections=["verse", "chorus", "bridge", "chorus"],
            modulate_bridge=False,
            seed=42,
        )
        assert isinstance(song, Song)

    def test_modulate_parameter_accepted(self):
        import inspect

        sig = inspect.signature(generate_full_song)
        assert "modulate_bridge" in sig.parameters


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

    def test_modulating_pop(self):
        mod = self._load("modulating_pop")
        assert isinstance(mod.song, Song)

    def test_piano_roll_demo(self):
        mod = self._load("piano_roll_demo")
        assert isinstance(mod.song, Song)

    def test_electronic_build(self):
        mod = self._load("electronic_build")
        assert isinstance(mod.song, Song)

    def test_blues_shuffle(self):
        mod = self._load("blues_shuffle")
        assert isinstance(mod.song, Song)

    def test_analyzed_jazz_v2(self):
        mod = self._load("analyzed_jazz_v2")
        assert isinstance(mod.song, Song)


if __name__ == "__main__":
    unittest.main()
