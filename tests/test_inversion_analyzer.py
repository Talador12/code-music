"""Tests for v113.0 — detect_inversion, inversion_label."""

from code_music.engine import Note
from code_music.theory import detect_inversion, inversion_label


class TestDetectInversion:
    def test_root_position(self):
        notes = [Note("C", 3, 1.0), Note("E", 3, 1.0), Note("G", 3, 1.0)]
        assert detect_inversion(notes, "C", "maj") == 0

    def test_first_inversion(self):
        notes = [Note("E", 3, 1.0), Note("G", 3, 1.0), Note("C", 4, 1.0)]
        assert detect_inversion(notes, "C", "maj") == 1

    def test_second_inversion(self):
        notes = [Note("G", 3, 1.0), Note("C", 4, 1.0), Note("E", 4, 1.0)]
        assert detect_inversion(notes, "C", "maj") == 2

    def test_empty(self):
        assert detect_inversion([], "C", "maj") == 0

    def test_dom7_third_inversion(self):
        notes = [Note("F", 3, 1.0), Note("G", 3, 1.0), Note("B", 3, 1.0), Note("D", 4, 1.0)]
        assert detect_inversion(notes, "G", "dom7") == 3


class TestInversionLabel:
    def test_root(self):
        assert inversion_label(0) == "root position"

    def test_first(self):
        assert inversion_label(1) == "1st inversion"

    def test_second(self):
        assert inversion_label(2) == "2nd inversion"

    def test_third(self):
        assert inversion_label(3) == "3rd inversion"
