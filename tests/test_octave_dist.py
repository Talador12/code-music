"""Tests for v128.0 — octave_distribution, register_spread."""

from code_music.engine import Note
from code_music.theory import octave_distribution, register_spread


class TestOctaveDistribution:
    def test_basic(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 5, 1.0)]
        d = octave_distribution(notes)
        assert d[4] == 2
        assert d[5] == 1

    def test_empty(self):
        assert octave_distribution([]) == {}

    def test_sorted(self):
        notes = [Note("C", 5, 1.0), Note("C", 3, 1.0)]
        d = octave_distribution(notes)
        assert list(d.keys()) == [3, 5]


class TestRegisterSpread:
    def test_one_octave(self):
        assert register_spread([Note("C", 4, 1.0)] * 4) == 1

    def test_three_octaves(self):
        notes = [Note("C", 3, 1.0), Note("C", 4, 1.0), Note("C", 5, 1.0)]
        assert register_spread(notes) == 3

    def test_empty(self):
        assert register_spread([]) == 0
