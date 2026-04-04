"""Tests for v129.0 — reverse_progression, rotate_progression."""

from code_music.theory import reverse_progression, rotate_progression


class TestReverseProgression:
    def test_basic(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7")]
        result = reverse_progression(prog)
        assert result == [("G", "dom7"), ("F", "maj"), ("C", "maj")]

    def test_empty(self):
        assert reverse_progression([]) == []

    def test_single(self):
        assert reverse_progression([("C", "maj")]) == [("C", "maj")]


class TestRotateProgression:
    def test_rotate_1(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7")]
        result = rotate_progression(prog, 1)
        assert result == [("F", "maj"), ("G", "dom7"), ("C", "maj")]

    def test_rotate_0(self):
        prog = [("C", "maj"), ("F", "maj")]
        assert rotate_progression(prog, 0) == prog

    def test_full_rotation(self):
        prog = [("C", "maj"), ("F", "maj")]
        assert rotate_progression(prog, 2) == prog

    def test_empty(self):
        assert rotate_progression([], 3) == []
