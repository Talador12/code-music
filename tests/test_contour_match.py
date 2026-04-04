"""Tests for v110.0 — contour_string, contour_match."""

from code_music.engine import Note
from code_music.theory import contour_match, contour_string


class TestContourString:
    def test_ascending(self):
        notes = [Note("C", 4, 1.0), Note("D", 4, 1.0), Note("E", 4, 1.0)]
        assert contour_string(notes) == "UU"

    def test_descending(self):
        notes = [Note("E", 4, 1.0), Note("D", 4, 1.0), Note("C", 4, 1.0)]
        assert contour_string(notes) == "DD"

    def test_repeated(self):
        notes = [Note("C", 4, 1.0), Note("C", 4, 1.0)]
        assert contour_string(notes) == "R"

    def test_mixed(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("D", 4, 1.0)]
        assert contour_string(notes) == "UD"

    def test_single_note(self):
        assert contour_string([Note("C", 4, 1.0)]) == ""


class TestContourMatch:
    def test_identical(self):
        a = [Note("C", 4, 1.0), Note("D", 4, 1.0), Note("E", 4, 1.0)]
        assert contour_match(a, a) == 1.0

    def test_transposed_same_contour(self):
        a = [Note("C", 4, 1.0), Note("D", 4, 1.0), Note("E", 4, 1.0)]
        b = [Note("G", 4, 1.0), Note("A", 4, 1.0), Note("B", 4, 1.0)]
        assert contour_match(a, b) == 1.0  # both ascending

    def test_opposite(self):
        a = [Note("C", 4, 1.0), Note("E", 4, 1.0)]
        b = [Note("E", 4, 1.0), Note("C", 4, 1.0)]
        assert contour_match(a, b) == 0.0  # up vs down

    def test_empty(self):
        assert contour_match([], [Note("C", 4, 1.0)]) == 0.0
