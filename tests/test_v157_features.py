"""Tests for v157.0: entry-point discovery, vintage pack, 5 new songs."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from code_music import Song, discover_plugins
from code_music.plugins import (
    clear_all,
    get_effect,
    get_instrument,
    list_effects,
    list_instruments,
)

# ---------------------------------------------------------------------------
# Entry-point discovery
# ---------------------------------------------------------------------------


class TestDiscoverPlugins(unittest.TestCase):
    """discover_plugins() scans entry points."""

    def test_returns_dict(self):
        result = discover_plugins()
        assert isinstance(result, dict)
        assert "discovered_count" in result
        assert "errors" in result

    def test_discovered_count_nonnegative(self):
        result = discover_plugins()
        assert result["discovered_count"] >= 0

    def test_import_from_top_level(self):
        from code_music import discover_plugins as dp

        assert callable(dp)


# ---------------------------------------------------------------------------
# Vintage pack
# ---------------------------------------------------------------------------


class TestVintagePack(unittest.TestCase):
    """Vintage preset pack registers instruments and effects."""

    def setUp(self):
        clear_all()
        # Re-import forces re-registration since clear_all wiped the registry
        import importlib

        import code_music.packs.vintage as v

        importlib.reload(v)

    def test_vintage_instruments_registered(self):
        names = list_instruments()
        for name in [
            "vintage_epiano",
            "vintage_strings",
            "vintage_organ",
            "vintage_bass",
            "vintage_lead",
            "vintage_pad",
        ]:
            assert name in names, f"{name} not registered"

    def test_vintage_effects_registered(self):
        names = list_effects()
        assert "tape_saturation" in names
        assert "wow_flutter" in names

    def test_epiano_renders(self):
        sd = get_instrument("vintage_epiano")()
        audio = sd.render(440.0, 0.5, 22050)
        assert len(audio) > 0

    def test_strings_renders(self):
        sd = get_instrument("vintage_strings")()
        audio = sd.render(440.0, 0.5, 22050)
        assert len(audio) > 0

    def test_tape_saturation_runs(self):
        import numpy as np

        fn = get_effect("tape_saturation")
        audio = np.random.randn(22050, 2) * 0.3
        result = fn(audio, 22050, drive=0.5, warmth=0.6, wet=0.7)
        assert result.shape == audio.shape

    def test_wow_flutter_runs(self):
        import numpy as np

        fn = get_effect("wow_flutter")
        audio = np.random.randn(22050, 2) * 0.3
        result = fn(audio, 22050)
        assert result.shape == audio.shape

    def test_direct_import(self):
        from code_music.packs.vintage import vintage_epiano, vintage_strings

        assert vintage_epiano is not None
        assert vintage_strings is not None


# ---------------------------------------------------------------------------
# New songs
# ---------------------------------------------------------------------------


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

    def test_vintage_keys(self):
        assert isinstance(self._load("vintage_keys").song, Song)

    def test_tape_dreams(self):
        assert isinstance(self._load("tape_dreams").song, Song)

    def test_analog_strings(self):
        assert isinstance(self._load("analog_strings").song, Song)

    def test_synth_pop(self):
        assert isinstance(self._load("synth_pop").song, Song)

    def test_prophet_ballad(self):
        assert isinstance(self._load("prophet_ballad").song, Song)


if __name__ == "__main__":
    unittest.main()
