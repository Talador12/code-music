"""Tests for v108.0 — fit_to_range, auto_octave."""

from code_music.engine import Note
from code_music.theory import auto_octave, fit_to_range


class TestFitToRange:
    def test_in_range_unchanged(self):
        notes = [Note("C", 4, 1.0)]  # C4 = 60, within default 48-72
        result = fit_to_range(notes)
        assert result[0].octave == 4

    def test_too_high_shifted_down(self):
        notes = [Note("C", 7, 1.0)]  # C7 = 84, above 72
        result = fit_to_range(notes, low=48, high=72)
        assert result[0].octave < 7

    def test_too_low_shifted_up(self):
        notes = [Note("C", 1, 1.0)]  # C1 = 12, below 48
        result = fit_to_range(notes, low=48, high=72)
        assert result[0].octave > 1

    def test_rest_passthrough(self):
        notes = [Note.rest(1.0)]
        result = fit_to_range(notes)
        assert result[0].pitch is None

    def test_preserves_pitch(self):
        notes = [Note("G", 6, 1.0)]
        result = fit_to_range(notes, low=48, high=72)
        assert result[0].pitch == "G"


class TestAutoOctave:
    def test_shifts_to_target(self):
        notes = [Note("C", 2, 1.0), Note("E", 2, 1.0)]
        result = auto_octave(notes, target_octave=5)
        assert result[0].octave > 2

    def test_already_at_target(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0)]
        result = auto_octave(notes, target_octave=4)
        assert result[0].octave == 4

    def test_rest_passthrough(self):
        notes = [Note("C", 4, 1.0), Note.rest(1.0)]
        result = auto_octave(notes)
        assert result[1].pitch is None

    def test_empty(self):
        assert auto_octave([]) == []
