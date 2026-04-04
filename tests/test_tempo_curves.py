"""Tests for v81.0 — ritardando, accelerando, rubato."""

from code_music.engine import Note
from code_music.theory import accelerando, ritardando, rubato


class TestRitardando:
    def test_durations_increase(self):
        notes = [Note("C", 5, 1.0)] * 8
        result = ritardando(notes, start_bpm=120, end_bpm=60)
        # Last note should be longer than first
        assert result[-1].duration > result[0].duration

    def test_first_unchanged(self):
        notes = [Note("C", 5, 1.0)] * 4
        result = ritardando(notes, start_bpm=120, end_bpm=60)
        assert abs(result[0].duration - 1.0) < 1e-9

    def test_empty(self):
        assert ritardando([], 120, 60) == []

    def test_preserves_pitch(self):
        notes = [Note("G", 5, 1.0)]
        result = ritardando(notes)
        assert result[0].pitch == "G"


class TestAccelerando:
    def test_durations_decrease(self):
        notes = [Note("C", 5, 1.0)] * 8
        result = accelerando(notes, start_bpm=60, end_bpm=120)
        assert result[-1].duration < result[0].duration

    def test_first_unchanged(self):
        notes = [Note("C", 5, 1.0)] * 4
        result = accelerando(notes, start_bpm=60, end_bpm=120)
        assert abs(result[0].duration - 1.0) < 1e-9


class TestRubato:
    def test_changes_durations(self):
        notes = [Note("C", 5, 1.0)] * 16
        result = rubato(notes, amount=0.15, seed=42)
        assert any(abs(n.duration - 1.0) > 0.01 for n in result)

    def test_deterministic(self):
        notes = [Note("C", 5, 1.0)] * 8
        a = rubato(notes, seed=99)
        b = rubato(notes, seed=99)
        assert [n.duration for n in a] == [n.duration for n in b]

    def test_empty(self):
        assert rubato([], seed=42) == []

    def test_rest_passthrough(self):
        notes = [Note.rest(1.0)]
        result = rubato(notes, seed=42)
        assert result[0].pitch is None
