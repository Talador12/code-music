"""Tests for new synth presets: wobble, formant, taiko, moog_bass, fm_bell."""

import numpy as np
import pytest

from code_music.engine import Note, Song, Track
from code_music.synth import Synth

SR = 22050


def _render(instrument: str, note: Note = None) -> np.ndarray:
    if note is None:
        note = Note("A", 3, duration=0.5)
    song = Song(bpm=120, sample_rate=SR)
    tr = song.add_track(Track(instrument=instrument))
    tr.add(note)
    return Synth(SR).render_song(song)


class TestWobbleBass:
    def test_renders_without_error(self):
        samples = _render("wobble", Note("A", 2, 0.5))
        assert samples.shape[0] > 0

    def test_has_audio_content(self):
        samples = _render("wobble", Note("A", 2, 0.5))
        assert np.max(np.abs(samples)) > 0.0

    def test_output_clamped(self):
        samples = _render("wobble", Note("A", 2, 1.0))
        assert np.max(np.abs(samples)) <= 1.0 + 1e-6


class TestFormantPresets:
    @pytest.mark.parametrize("preset", ["formant_a", "formant_o", "formant_e"])
    def test_renders(self, preset):
        samples = _render(preset, Note("A", 3, 0.5))
        assert np.max(np.abs(samples)) > 0.0

    def test_formants_differ(self):
        a = _render("formant_a", Note("A", 3, 0.5))
        o = _render("formant_o", Note("A", 3, 0.5))
        # Different vowel shapes should produce different audio
        assert not np.allclose(a, o, atol=0.01)


class TestTaikoPreset:
    def test_renders(self):
        samples = _render("taiko", Note("C", 2, 0.5))
        assert np.max(np.abs(samples)) > 0.0

    def test_output_clamped(self):
        samples = _render("taiko", Note("C", 2, 0.5))
        assert np.max(np.abs(samples)) <= 1.0 + 1e-6


class TestFmBell:
    def test_renders(self):
        samples = _render("fm_bell", Note("C", 5, 0.5))
        assert np.max(np.abs(samples)) > 0.0


class TestMoogBass:
    def test_renders(self):
        samples = _render("moog_bass", Note("E", 2, 0.5))
        assert np.max(np.abs(samples)) > 0.0


class TestSubBass:
    def test_renders(self):
        samples = _render("sub_bass", Note("C", 1, 0.5))
        assert np.max(np.abs(samples)) > 0.0


class TestAllNewPresets:
    NEW_PRESETS = [
        "wobble",
        "portamento",
        "fm_bell",
        "formant_a",
        "formant_o",
        "formant_e",
        "taiko",
        "tabla",
        "djembe",
        "moog_bass",
        "sub_bass",
    ]

    def test_all_render(self):
        for preset in self.NEW_PRESETS:
            samples = _render(preset, Note("A", 3, 0.5))
            assert samples.shape[0] > 0, f"{preset} produced no output"
            assert np.max(np.abs(samples)) <= 1.0 + 1e-6, f"{preset} exceeded clip"
