"""Tests for v123.0 — leap_count, step_count, leap_step_ratio."""

from code_music.engine import Note
from code_music.theory import leap_count, leap_step_ratio, step_count


class TestLeapCount:
    def test_ascending_scale(self):
        notes = [Note("C", 4, 1.0), Note("D", 4, 1.0), Note("E", 4, 1.0)]
        assert leap_count(notes) == 0  # all steps (2 semitones)

    def test_octave_jump(self):
        notes = [Note("C", 4, 1.0), Note("C", 5, 1.0)]
        assert leap_count(notes) == 1

    def test_empty(self):
        assert leap_count([]) == 0


class TestStepCount:
    def test_scale(self):
        notes = [Note("C", 4, 1.0), Note("D", 4, 1.0), Note("E", 4, 1.0)]
        assert step_count(notes) == 2

    def test_leap_not_counted(self):
        notes = [Note("C", 4, 1.0), Note("C", 5, 1.0)]
        assert step_count(notes) == 0


class TestLeapStepRatio:
    def test_all_steps(self):
        notes = [Note("C", 4, 1.0), Note("D", 4, 1.0)]
        assert leap_step_ratio(notes) == 0.0

    def test_all_leaps(self):
        notes = [Note("C", 4, 1.0), Note("C", 5, 1.0)]
        assert leap_step_ratio(notes) > 0
