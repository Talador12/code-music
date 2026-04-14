"""Tests for v165.0: formant vocal synthesis, 20 new presets, album builder, 5 songs."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

from code_music import Song
from code_music.sound_design import PRESETS, SoundDesigner


class TestFormantSynthesis(unittest.TestCase):
    """Formant vocal synthesis produces vowel-like sounds."""

    def test_choir_ah_renders(self):
        sd = SoundDesigner("test").formant("ah", volume=0.8)
        audio = sd.render(440.0, 0.5, 22050)
        assert len(audio) > 0
        assert np.max(np.abs(audio)) > 0.001

    def test_choir_oo_renders(self):
        sd = SoundDesigner("test").formant("oo", volume=0.8)
        audio = sd.render(440.0, 0.5, 22050)
        assert len(audio) > 0

    def test_all_vowels(self):
        for vowel in ["ah", "ee", "oh", "oo", "eh", "ih"]:
            sd = SoundDesigner(f"v_{vowel}").formant(vowel, volume=0.8)
            audio = sd.render(440.0, 0.3, 22050)
            assert len(audio) > 0, f"Vowel {vowel} produced empty audio"

    def test_breathiness(self):
        breathy = (
            SoundDesigner("b").formant("ah", breathiness=0.9, volume=0.8).render(440.0, 0.3, 22050)
        )
        clean = (
            SoundDesigner("c").formant("ah", breathiness=0.0, volume=0.8).render(440.0, 0.3, 22050)
        )
        assert not np.array_equal(breathy, clean)

    def test_vibrato(self):
        with_vib = (
            SoundDesigner("v")
            .formant("ah", vibrato_depth=0.05, volume=0.8)
            .render(440.0, 0.5, 22050)
        )
        no_vib = (
            SoundDesigner("n")
            .formant("ah", vibrato_depth=0.0, volume=0.8)
            .render(440.0, 0.5, 22050)
        )
        assert not np.array_equal(with_vib, no_vib)

    def test_multiple_formants(self):
        sd = SoundDesigner("dual").formant("ah", volume=0.5).formant("oo", volume=0.3)
        audio = sd.render(440.0, 0.3, 22050)
        assert len(audio) > 0

    def test_formant_with_envelope(self):
        sd = (
            SoundDesigner("env")
            .formant("ee", volume=0.8)
            .envelope(attack=0.1, decay=0.1, sustain=0.7, release=0.3)
        )
        audio = sd.render(440.0, 0.5, 22050)
        assert len(audio) > 0

    def test_formant_with_filter(self):
        sd = (
            SoundDesigner("filt")
            .formant("oh", volume=0.8)
            .filter("lowpass", cutoff=3000, resonance=0.5)
        )
        audio = sd.render(440.0, 0.3, 22050)
        assert len(audio) > 0


class TestNewPresets(unittest.TestCase):
    """All 38 presets render correctly."""

    def test_preset_count(self):
        assert len(PRESETS) >= 38

    def test_all_presets_render(self):
        for name, sd in PRESETS.items():
            audio = sd.render(440.0, 0.3, 22050)
            assert len(audio) > 0, f"Preset {name} produced empty audio"

    def test_vocal_presets_exist(self):
        for name in ["choir_ah", "choir_oo", "ethereal_voice", "whisper_pad", "vocal_lead"]:
            assert name in PRESETS, f"Missing vocal preset: {name}"

    def test_synth_presets_exist(self):
        for name in [
            "acid_bass",
            "detuned_pad",
            "reese_bass",
            "hoover",
            "pluck_synth",
            "ice_pad",
            "dark_drone",
        ]:
            assert name in PRESETS, f"Missing synth preset: {name}"

    def test_orchestral_presets_exist(self):
        for name in [
            "pm_cello",
            "pm_viola",
            "pm_bass_guitar",
            "fm_clarinet",
            "fm_marimba",
            "pm_kalimba",
        ]:
            assert name in PRESETS, f"Missing orchestral preset: {name}"

    def test_drum_presets_exist(self):
        for name in ["trap_808", "clap", "rimshot"]:
            assert name in PRESETS, f"Missing drum preset: {name}"


class TestAlbumMakefile(unittest.TestCase):
    def test_album_target_exists(self):
        content = Path(__file__).parent.parent.joinpath("Makefile").read_text()
        assert "album:" in content
        assert "ALBUM" in content
        assert "mastering" in content.lower() or "master" in content.lower()


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

    def test_choir_processional(self):
        assert isinstance(self._load("choir_processional").song, Song)

    def test_ethereal_drift(self):
        assert isinstance(self._load("ethereal_drift").song, Song)

    def test_acid_303(self):
        assert isinstance(self._load("acid_303").song, Song)

    def test_string_quartet_v2(self):
        assert isinstance(self._load("string_quartet_v2").song, Song)

    def test_dark_cathedral(self):
        assert isinstance(self._load("dark_cathedral").song, Song)


if __name__ == "__main__":
    unittest.main()
