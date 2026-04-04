"""Tests for v79.0 — sforzando, dynamics_map (theory.py versions)."""

from code_music.engine import Note
from code_music.theory import dynamics_map, sforzando


class TestSforzando:
    def test_accents_position(self):
        notes = [Note("C", 5, 1.0, velocity=70)] * 4
        result = sforzando(notes, position=2, accent_vel=127)
        assert result[2].velocity == 127

    def test_other_notes_unchanged(self):
        notes = [Note("C", 5, 1.0, velocity=70)] * 4
        result = sforzando(notes, position=2)
        assert result[0].velocity == 70

    def test_out_of_bounds(self):
        notes = [Note("C", 5, 1.0)]
        result = sforzando(notes, position=5)
        assert result[0].velocity == notes[0].velocity

    def test_rest_skipped(self):
        notes = [Note.rest(1.0)]
        result = sforzando(notes, position=0)
        assert result[0].pitch is None


class TestDynamicsMap:
    def test_returns_velocities(self):
        notes = [Note("C", 5, 1.0, velocity=80), Note("E", 5, 1.0, velocity=100)]
        dm = dynamics_map(notes)
        assert dm == [80, 100]

    def test_rest_is_zero(self):
        notes = [Note.rest(1.0)]
        assert dynamics_map(notes) == [0]

    def test_empty(self):
        assert dynamics_map([]) == []
