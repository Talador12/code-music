"""Tests for v119.0 — pitch_histogram, pitch_class_histogram."""

from code_music.engine import Note
from code_music.theory import pitch_class_histogram, pitch_histogram


class TestPitchHistogram:
    def test_basic(self):
        notes = [Note("C", 5, 1.0), Note("C", 5, 1.0), Note("E", 5, 1.0)]
        h = pitch_histogram(notes)
        assert h["C"] == 2
        assert h["E"] == 1

    def test_sorted_by_freq(self):
        notes = [Note("E", 5, 1.0)] * 3 + [Note("C", 5, 1.0)]
        h = pitch_histogram(notes)
        keys = list(h.keys())
        assert keys[0] == "E"  # most frequent first

    def test_empty(self):
        assert pitch_histogram([]) == {}

    def test_rests_excluded(self):
        notes = [Note("C", 5, 1.0), Note.rest(1.0)]
        assert len(pitch_histogram(notes)) == 1


class TestPitchClassHistogram:
    def test_twelve_bins(self):
        h = pitch_class_histogram([Note("C", 4, 1.0)])
        assert len(h) == 12

    def test_c_in_bin_0(self):
        h = pitch_class_histogram([Note("C", 4, 1.0)])
        assert h[0] == 1

    def test_empty(self):
        h = pitch_class_histogram([])
        assert sum(h) == 0
