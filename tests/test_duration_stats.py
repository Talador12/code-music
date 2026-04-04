"""Tests for v121.0 — duration_stats, total_duration."""

from code_music.engine import Note
from code_music.theory import duration_stats, total_duration


class TestDurationStats:
    def test_basic(self):
        notes = [Note("C", 5, 0.5), Note("E", 5, 1.0), Note("G", 5, 2.0)]
        s = duration_stats(notes)
        assert s["min"] == 0.5
        assert s["max"] == 2.0
        assert s["total"] == 3.5
        assert s["count"] == 3
        assert s["unique_durations"] == 3

    def test_empty(self):
        s = duration_stats([])
        assert s["count"] == 0

    def test_same_duration(self):
        notes = [Note("C", 5, 1.0)] * 4
        s = duration_stats(notes)
        assert s["unique_durations"] == 1


class TestTotalDuration:
    def test_basic(self):
        notes = [Note("C", 5, 1.0), Note("E", 5, 2.0)]
        assert total_duration(notes) == 3.0

    def test_with_rests(self):
        notes = [Note("C", 5, 1.0), Note.rest(0.5)]
        assert total_duration(notes) == 1.5

    def test_empty(self):
        assert total_duration([]) == 0.0
