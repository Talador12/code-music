"""Tests for v88.0 — change_key, double_time, half_time."""

from code_music.engine import Note
from code_music.theory import change_key, double_time, half_time


class TestChangeKey:
    def test_c_to_g(self):
        notes = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        result = change_key(notes, "C", "G")
        assert result[0].pitch == "G"

    def test_preserves_intervals(self):
        notes = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        result = change_key(notes, "C", "D")
        assert result[0].pitch == "D"
        assert result[1].pitch == "F#"

    def test_rest_passthrough(self):
        notes = [Note.rest(1.0)]
        result = change_key(notes, "C", "G")
        assert result[0].pitch is None

    def test_identity(self):
        notes = [Note("A", 4, 1.0)]
        result = change_key(notes, "A", "A")
        assert result[0].pitch == "A"


class TestDoubleTime:
    def test_halves_durations(self):
        notes = [Note("C", 5, 2.0)]
        result = double_time(notes)
        assert result[0].duration == 1.0

    def test_preserves_pitch(self):
        result = double_time([Note("G", 4, 1.0)])
        assert result[0].pitch == "G"

    def test_rest(self):
        result = double_time([Note.rest(2.0)])
        assert result[0].duration == 1.0


class TestHalfTime:
    def test_doubles_durations(self):
        notes = [Note("C", 5, 1.0)]
        result = half_time(notes)
        assert result[0].duration == 2.0

    def test_rest(self):
        result = half_time([Note.rest(1.0)])
        assert result[0].duration == 2.0
