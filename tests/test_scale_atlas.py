"""Tests for v56.0 — list_scales, scale_search, scale_brightness, scale_modes."""

import pytest

from code_music.theory import list_scales, scale_brightness, scale_modes, scale_search


class TestListScales:
    def test_returns_list(self):
        scales = list_scales()
        assert isinstance(scales, list)

    def test_includes_standard(self):
        scales = list_scales()
        assert "major" in scales
        assert "dorian" in scales
        assert "pentatonic" in scales

    def test_includes_exotic(self):
        scales = list_scales()
        assert "hungarian_minor" in scales
        assert "hirajoshi" in scales
        assert "bebop_dominant" in scales

    def test_at_least_40(self):
        assert len(list_scales()) >= 40

    def test_sorted(self):
        scales = list_scales()
        assert scales == sorted(scales)


class TestScaleSearch:
    def test_major_triad_in_major(self):
        results = scale_search(["C", "E", "G"])
        assert "major" in results

    def test_blues_notes(self):
        results = scale_search(["C", "Eb", "F", "Gb", "G", "Bb"])
        assert "blues" in results

    def test_narrow_search(self):
        # All 12 chromatic tones — only chromatic-like scales should match
        all_notes = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
        results = scale_search(all_notes)
        # Very few scales contain all 12 pitch classes
        assert len(results) == 0  # no scale has all 12

    def test_empty_search(self):
        results = scale_search([])
        # Every scale contains the empty set
        assert len(results) == len(list_scales())


class TestScaleBrightness:
    def test_lydian_brighter_than_locrian(self):
        assert scale_brightness("lydian") > scale_brightness("locrian")

    def test_range(self):
        for name in ["major", "dorian", "phrygian", "lydian"]:
            b = scale_brightness(name)
            assert 0.0 <= b <= 1.0

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown scale"):
            scale_brightness("nonexistent_scale")

    def test_major_middle(self):
        b = scale_brightness("major")
        assert 0.3 < b < 0.8


class TestScaleModes:
    def test_major_has_7_modes(self):
        modes = scale_modes("major")
        assert len(modes) == 7

    def test_pentatonic_has_5_modes(self):
        modes = scale_modes("pentatonic")
        assert len(modes) == 5

    def test_first_mode_starts_at_0(self):
        modes = scale_modes("major")
        assert modes[0][1][0] == 0

    def test_all_modes_start_at_0(self):
        modes = scale_modes("dorian")
        for _, intervals in modes:
            assert intervals[0] == 0

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown scale"):
            scale_modes("fake_scale")

    def test_mode_labels(self):
        modes = scale_modes("major")
        assert modes[0][0] == "major_mode_1"
        assert modes[6][0] == "major_mode_7"
