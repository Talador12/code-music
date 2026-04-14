"""Tests for v168.0: 15 new core presets, 5 songs, 2 albums."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from code_music import Song
from code_music.sound_design import PRESETS


class TestNewCorePresets(unittest.TestCase):
    def test_preset_count(self):
        assert len(PRESETS) >= 51, f"Only {len(PRESETS)} core presets"

    def test_granular_presets(self):
        for name in ["grain_texture", "grain_stutter", "grain_rain"]:
            assert name in PRESETS, f"Missing: {name}"

    def test_wavetable_presets(self):
        for name in ["wt_glass", "wt_vocal_formant", "wt_digital"]:
            assert name in PRESETS, f"Missing: {name}"

    def test_ethnic_presets(self):
        for name in ["sitar", "shamisen", "didgeridoo"]:
            assert name in PRESETS, f"Missing: {name}"

    def test_percussion_presets(self):
        for name in ["tabla", "shaker", "taiko"]:
            assert name in PRESETS, f"Missing: {name}"

    def test_all_new_render(self):
        new_names = [
            "grain_texture",
            "grain_stutter",
            "grain_rain",
            "wt_glass",
            "wt_vocal_formant",
            "wt_digital",
            "sitar",
            "shamisen",
            "didgeridoo",
            "tabla",
            "shaker",
            "taiko",
        ]
        for name in new_names:
            audio = PRESETS[name].render(440.0, 0.3, 22050)
            assert len(audio) > 0, f"{name} silent"


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

    def test_taiko_thunder(self):
        assert isinstance(self._load("taiko_thunder").song, Song)

    def test_sitar_raga(self):
        assert isinstance(self._load("sitar_raga").song, Song)

    def test_granular_meditation(self):
        assert isinstance(self._load("granular_meditation").song, Song)

    def test_glass_music_box(self):
        assert isinstance(self._load("glass_music_box").song, Song)

    def test_cinematic_trailer(self):
        assert isinstance(self._load("cinematic_trailer").song, Song)


class TestNewAlbums(unittest.TestCase):
    def test_albums_exist(self):
        for name in ["classical_portraits", "jazz_sessions"]:
            path = Path(__file__).parent.parent / "albums" / f"{name}.py"
            assert path.exists(), f"Missing: {name}"

    def test_tracklists_valid(self):
        import importlib.util

        songs_dir = Path(__file__).parent.parent / "songs"
        for album_name in ["classical_portraits", "jazz_sessions"]:
            path = Path(__file__).parent.parent / "albums" / f"{album_name}.py"
            spec = importlib.util.spec_from_file_location(album_name, str(path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for song_name in mod.TRACKLIST:
                assert (songs_dir / f"{song_name}.py").exists(), (
                    f"{album_name} references missing: {song_name}"
                )


if __name__ == "__main__":
    unittest.main()
