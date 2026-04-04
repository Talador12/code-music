"""Tests for v122.0 — rest_ratio, longest_rest."""

from code_music.engine import Note
from code_music.theory import longest_rest, rest_ratio


class TestRestRatio:
    def test_no_rests(self):
        assert rest_ratio([Note("C", 5, 1.0)] * 4) == 0.0

    def test_all_rests(self):
        assert rest_ratio([Note.rest(1.0)] * 4) == 1.0

    def test_half(self):
        notes = [Note("C", 5, 1.0), Note.rest(1.0)]
        assert abs(rest_ratio(notes) - 0.5) < 0.01

    def test_empty(self):
        assert rest_ratio([]) == 0.0


class TestLongestRest:
    def test_basic(self):
        notes = [Note.rest(0.5), Note("C", 5, 1.0), Note.rest(2.0)]
        assert longest_rest(notes) == 2.0

    def test_no_rests(self):
        assert longest_rest([Note("C", 5, 1.0)]) == 0.0

    def test_empty(self):
        assert longest_rest([]) == 0.0
