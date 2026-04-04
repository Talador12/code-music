"""Tests for v124.0 — repetition_ratio, unique_pitches."""

from code_music.engine import Note
from code_music.theory import repetition_ratio, unique_pitches


class TestRepetitionRatio:
    def test_all_same(self):
        notes = [Note("C", 4, 1.0)] * 4
        assert repetition_ratio(notes) == 1.0

    def test_all_different(self):
        notes = [Note("C", 4, 1.0), Note("D", 4, 1.0), Note("E", 4, 1.0)]
        assert repetition_ratio(notes) == 0.0

    def test_empty(self):
        assert repetition_ratio([]) == 0.0

    def test_single(self):
        assert repetition_ratio([Note("C", 4, 1.0)]) == 0.0


class TestUniquePitches:
    def test_basic(self):
        notes = [Note("C", 4, 1.0), Note("C", 4, 1.0), Note("E", 4, 1.0)]
        assert unique_pitches(notes) == 2

    def test_octave_matters(self):
        notes = [Note("C", 4, 1.0), Note("C", 5, 1.0)]
        assert unique_pitches(notes) == 2

    def test_rests_excluded(self):
        notes = [Note("C", 4, 1.0), Note.rest(1.0)]
        assert unique_pitches(notes) == 1

    def test_empty(self):
        assert unique_pitches([]) == 0
