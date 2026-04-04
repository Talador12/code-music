"""Tests for v83.0 — dotted, double_dotted, tied, split_note."""

import pytest

from code_music.engine import Note
from code_music.theory import dotted, double_dotted, split_note, tied


class TestDotted:
    def test_quarter_to_dotted_quarter(self):
        n = dotted(Note("C", 5, 1.0))
        assert abs(n.duration - 1.5) < 1e-9

    def test_preserves_pitch(self):
        n = dotted(Note("G", 4, 2.0))
        assert n.pitch == "G"

    def test_rest(self):
        n = dotted(Note.rest(1.0))
        assert n.pitch is None
        assert abs(n.duration - 1.5) < 1e-9


class TestDoubleDotted:
    def test_quarter_to_double_dotted(self):
        n = double_dotted(Note("C", 5, 1.0))
        assert abs(n.duration - 1.75) < 1e-9


class TestTied:
    def test_same_pitch(self):
        a = Note("C", 5, 1.0)
        b = Note("C", 5, 2.0)
        t = tied(a, b)
        assert t.duration == 3.0
        assert t.pitch == "C"

    def test_rests(self):
        a = Note.rest(1.0)
        b = Note.rest(2.0)
        t = tied(a, b)
        assert t.pitch is None
        assert t.duration == 3.0

    def test_mismatch_raises(self):
        with pytest.raises(ValueError, match="Cannot tie"):
            tied(Note("C", 5, 1.0), Note("D", 5, 1.0))


class TestSplitNote:
    def test_split_in_two(self):
        n = Note("C", 5, 2.0)
        parts = split_note(n, 2)
        assert len(parts) == 2
        assert all(abs(p.duration - 1.0) < 1e-9 for p in parts)

    def test_split_in_four(self):
        n = Note("C", 5, 4.0)
        parts = split_note(n, 4)
        assert len(parts) == 4
        assert all(abs(p.duration - 1.0) < 1e-9 for p in parts)

    def test_preserves_pitch(self):
        parts = split_note(Note("E", 4, 2.0), 2)
        assert all(p.pitch == "E" for p in parts)

    def test_rest(self):
        parts = split_note(Note.rest(2.0), 4)
        assert all(p.pitch is None for p in parts)
