"""Tests for v167.0: cinematic pack, electronic pack, album infrastructure."""

import importlib
import unittest
from pathlib import Path

from code_music.plugins import clear_all, list_effects, list_instruments


class TestCinematicPack(unittest.TestCase):
    def setUp(self):
        clear_all()
        import code_music.packs.cinematic as m

        importlib.reload(m)

    def test_instruments_registered(self):
        names = list_instruments()
        for name in [
            "epic_brass",
            "epic_strings",
            "cinematic_pad",
            "trailer_hit",
            "tension_drone",
            "choir_epic",
            "harp_pluck",
            "timpani",
            "celeste",
        ]:
            assert name in names, f"Missing: {name}"

    def test_effects_registered(self):
        assert "cinematic_reverb" in list_effects()

    def test_all_render(self):
        from code_music.plugins import get_instrument

        for name in ["epic_brass", "epic_strings", "trailer_hit", "celeste"]:
            sd = get_instrument(name)()
            audio = sd.render(440.0, 0.3, 22050)
            assert len(audio) > 0, f"{name} silent"


class TestElectronicPack(unittest.TestCase):
    def setUp(self):
        clear_all()
        import code_music.packs.electronic as m

        importlib.reload(m)

    def test_instruments_registered(self):
        names = list_instruments()
        for name in [
            "edm_supersaw",
            "edm_pluck",
            "wobble_bass",
            "neuro_bass",
            "trance_lead",
            "ambient_pad_deep",
            "future_bass_chord",
            "lofi_keys",
            "lofi_pad",
            "glitch_perc",
            "siren_lead",
        ]:
            assert name in names, f"Missing: {name}"

    def test_effects_registered(self):
        assert "sidechain_pump" in list_effects()

    def test_all_render(self):
        from code_music.plugins import get_instrument

        for name in ["edm_supersaw", "wobble_bass", "lofi_keys", "glitch_perc"]:
            sd = get_instrument(name)()
            audio = sd.render(440.0, 0.3, 22050)
            assert len(audio) > 0, f"{name} silent"


class TestAllPacksImport(unittest.TestCase):
    def test_import_all(self):
        clear_all()
        import code_music.packs.cinematic as c
        import code_music.packs.electronic as e
        import code_music.packs.vintage as v

        importlib.reload(v)
        importlib.reload(c)
        importlib.reload(e)
        names = list_instruments()
        assert len(names) >= 25, f"Only {len(names)} instruments"

    def test_total_preset_count(self):
        clear_all()
        import code_music.packs.cinematic as c
        import code_music.packs.electronic as e
        import code_music.packs.vintage as v

        importlib.reload(v)
        importlib.reload(c)
        importlib.reload(e)
        from code_music.sound_design import PRESETS

        total = len(PRESETS) + len(list_instruments())
        assert total >= 60, f"Only {total} presets, expected 60+"


class TestAlbumInfra(unittest.TestCase):
    def test_albums_directory_exists(self):
        assert Path(__file__).parent.parent.joinpath("albums").is_dir()

    def test_album_files_have_tracklists(self):
        for name in ["ambient_horizons", "electric_dreams", "world_fusion"]:
            path = Path(__file__).parent.parent / "albums" / f"{name}.py"
            assert path.exists(), f"Missing album: {name}"
            content = path.read_text()
            assert "TRACKLIST" in content
            assert "TITLE" in content

    def test_tracklists_reference_valid_songs(self):
        songs_dir = Path(__file__).parent.parent / "songs"
        for album_name in ["ambient_horizons", "electric_dreams", "world_fusion"]:
            import importlib.util

            path = Path(__file__).parent.parent / "albums" / f"{album_name}.py"
            spec = importlib.util.spec_from_file_location(album_name, str(path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for song_name in mod.TRACKLIST:
                song_file = songs_dir / f"{song_name}.py"
                assert song_file.exists(), (
                    f"Album {album_name} references missing song: {song_name}"
                )


if __name__ == "__main__":
    unittest.main()
