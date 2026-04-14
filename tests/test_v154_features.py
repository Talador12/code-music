"""Tests for v154.0: plugin registry decorators."""

import unittest

from code_music.plugins import (
    clear_all,
    get_effect,
    get_generator,
    get_instrument,
    list_effects,
    list_generators,
    list_instruments,
    plugin_summary,
    register_effect,
    register_generator,
    register_instrument,
)


class TestRegisterInstrument(unittest.TestCase):
    def setUp(self):
        clear_all()

    def tearDown(self):
        clear_all()

    def test_register_and_get(self):
        @register_instrument("test_synth")
        def test_synth():
            return "fake_sd"

        assert get_instrument("test_synth") is not None
        assert get_instrument("test_synth")() == "fake_sd"

    def test_unknown_returns_none(self):
        assert get_instrument("nonexistent") is None

    def test_list(self):
        @register_instrument("alpha")
        def a():
            return None

        @register_instrument("beta")
        def b():
            return None

        assert list_instruments() == ["alpha", "beta"]

    def test_decorator_preserves_function(self):
        @register_instrument("preserved")
        def my_fn():
            return 42

        assert my_fn() == 42


class TestRegisterEffect(unittest.TestCase):
    def setUp(self):
        clear_all()

    def tearDown(self):
        clear_all()

    def test_register_and_get(self):
        @register_effect("my_reverb")
        def my_reverb(samples, sr, room=0.5):
            return samples

        assert get_effect("my_reverb") is not None

    def test_list(self):
        @register_effect("fx_a")
        def a(s, sr):
            return s

        @register_effect("fx_b")
        def b(s, sr):
            return s

        assert list_effects() == ["fx_a", "fx_b"]


class TestRegisterGenerator(unittest.TestCase):
    def setUp(self):
        clear_all()

    def tearDown(self):
        clear_all()

    def test_register_and_get(self):
        @register_generator("vaporwave")
        def vaporwave(key="C", bpm=80, seed=None):
            return "song"

        assert get_generator("vaporwave") is not None
        assert get_generator("vaporwave")() == "song"

    def test_list(self):
        @register_generator("gen_x")
        def x(**kw):
            pass

        assert list_generators() == ["gen_x"]


class TestPluginSummary(unittest.TestCase):
    def setUp(self):
        clear_all()

    def tearDown(self):
        clear_all()

    def test_empty_summary(self):
        s = plugin_summary()
        assert s["instrument_count"] == 0
        assert s["effect_count"] == 0
        assert s["generator_count"] == 0

    def test_populated_summary(self):
        register_instrument("i1")(lambda: None)
        register_effect("e1")(lambda s, sr: s)
        register_generator("g1")(lambda: None)

        s = plugin_summary()
        assert s["instrument_count"] == 1
        assert s["effect_count"] == 1
        assert s["generator_count"] == 1
        assert "i1" in s["instruments"]
        assert "e1" in s["effects"]
        assert "g1" in s["generators"]


class TestClearAll(unittest.TestCase):
    def test_clear(self):
        register_instrument("temp")(lambda: None)
        assert len(list_instruments()) == 1
        clear_all()
        assert len(list_instruments()) == 0


class TestTopLevelImports(unittest.TestCase):
    def test_imports(self):
        from code_music import (
            get_effect,
            get_generator,
            get_instrument,
            plugin_summary,
            register_effect,
            register_generator,
            register_instrument,
        )

        for fn in [
            get_effect,
            get_generator,
            get_instrument,
            plugin_summary,
            register_effect,
            register_generator,
            register_instrument,
        ]:
            assert callable(fn)


if __name__ == "__main__":
    unittest.main()
