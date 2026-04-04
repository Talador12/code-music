"""Tests for v109.0 — interval_sequence, common_intervals."""

from code_music.engine import Note
from code_music.theory import common_intervals, interval_sequence


class TestIntervalSequence:
    def test_ascending(self):
        notes = [Note("C", 4, 1.0), Note("D", 4, 1.0), Note("E", 4, 1.0)]
        seq = interval_sequence(notes)
        assert seq == [2, 2]  # C→D = +2, D→E = +2

    def test_descending(self):
        notes = [Note("E", 4, 1.0), Note("C", 4, 1.0)]
        seq = interval_sequence(notes)
        assert seq == [-4]  # E→C = -4 semitones

    def test_rests_skipped(self):
        notes = [Note("C", 4, 1.0), Note.rest(1.0), Note("E", 4, 1.0)]
        seq = interval_sequence(notes)
        assert len(seq) == 0  # both pairs have a rest

    def test_single_note(self):
        assert interval_sequence([Note("C", 4, 1.0)]) == []

    def test_octave_jump(self):
        notes = [Note("C", 4, 1.0), Note("C", 5, 1.0)]
        seq = interval_sequence(notes)
        assert seq == [12]


class TestCommonIntervals:
    def test_basic(self):
        notes = [Note("C", 4, 1.0), Note("D", 4, 1.0)] * 5 + [Note("C", 4, 1.0), Note("E", 4, 1.0)]
        result = common_intervals(notes)
        # +2 (C→D) should be most common
        assert result[0][0] == 2

    def test_top_n(self):
        notes = [Note("C", 4, 1.0), Note("D", 4, 1.0), Note("C", 4, 1.0)]
        result = common_intervals(notes, top_n=1)
        assert len(result) <= 1

    def test_empty(self):
        assert common_intervals([]) == []
