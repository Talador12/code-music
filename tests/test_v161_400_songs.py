"""Tests for v161.0: 13 new songs pushing to 400 total."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from code_music import Song


class TestNewSongs400(unittest.TestCase):
    """All 13 new songs load cleanly."""

    def _load(self, name):
        import importlib.util

        path = Path(__file__).parent.parent / "songs" / f"{name}.py"
        spec = importlib.util.spec_from_file_location(name, str(path))
        mod = importlib.util.module_from_spec(spec)
        out = io.StringIO()
        with redirect_stdout(out):
            spec.loader.exec_module(mod)
        return mod

    def test_reggae_riddim(self):
        assert isinstance(self._load("reggae_riddim").song, Song)

    def test_flamenco_fuego(self):
        assert isinstance(self._load("flamenco_fuego").song, Song)

    def test_indian_raga(self):
        assert isinstance(self._load("indian_raga").song, Song)

    def test_synthwave_neon(self):
        assert isinstance(self._load("synthwave_neon").song, Song)

    def test_gospel_choir(self):
        assert isinstance(self._load("gospel_choir").song, Song)

    def test_drum_and_bass(self):
        assert isinstance(self._load("drum_and_bass").song, Song)

    def test_baroque_prelude(self):
        assert isinstance(self._load("baroque_prelude").song, Song)

    def test_afrobeat_lagos(self):
        assert isinstance(self._load("afrobeat_lagos").song, Song)

    def test_shoegaze_wall(self):
        assert isinstance(self._load("shoegaze_wall").song, Song)

    def test_tango_passion(self):
        assert isinstance(self._load("tango_passion").song, Song)

    def test_desert_blues(self):
        assert isinstance(self._load("desert_blues").song, Song)

    def test_orchestral_waltz(self):
        assert isinstance(self._load("orchestral_waltz").song, Song)

    def test_fill_tracks_demo(self):
        mod = self._load("fill_tracks_demo")
        assert isinstance(mod.song, Song)
        # fill_tracks should have added tracks
        assert len(mod.song.tracks) >= 3


if __name__ == "__main__":
    unittest.main()
