"""Tests for v111.0 — rhythm_string, rhythm_match."""

from code_music.engine import Note
from code_music.theory import rhythm_match, rhythm_string


class TestRhythmString:
    def test_all_notes(self):
        notes = [Note("C", 5, 0.25)] * 4
        assert rhythm_string(notes) == "XXXX"

    def test_with_rests(self):
        notes = [Note("C", 5, 0.25), Note.rest(0.25)]
        assert rhythm_string(notes) == "X."

    def test_longer_notes(self):
        notes = [Note("C", 5, 0.5)]  # 2 grid slots
        assert rhythm_string(notes, grid=0.25) == "X."

    def test_empty(self):
        assert rhythm_string([]) == ""


class TestRhythmMatch:
    def test_identical(self):
        a = [Note("C", 5, 0.25)] * 4
        assert rhythm_match(a, a) == 1.0

    def test_different_pitch_same_rhythm(self):
        a = [Note("C", 5, 0.25), Note.rest(0.25)]
        b = [Note("G", 4, 0.25), Note.rest(0.25)]
        assert rhythm_match(a, b) == 1.0

    def test_different_rhythm(self):
        a = [Note("C", 5, 0.25)] * 4
        b = [Note.rest(0.25)] * 4
        score = rhythm_match(a, b)
        assert score < 1.0

    def test_empty(self):
        assert rhythm_match([], [Note("C", 5, 0.25)]) == 0.0
