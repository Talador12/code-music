"""Tests for v120.0 — velocity_stats, velocity_curve."""

from code_music.engine import Note
from code_music.theory import velocity_curve, velocity_stats


class TestVelocityStats:
    def test_basic(self):
        notes = [Note("C", 5, 1.0, velocity=60), Note("E", 5, 1.0, velocity=100)]
        s = velocity_stats(notes)
        assert s["min"] == 60
        assert s["max"] == 100
        assert s["avg"] == 80.0
        assert s["range"] == 40
        assert s["count"] == 2

    def test_empty(self):
        s = velocity_stats([])
        assert s["count"] == 0

    def test_rests(self):
        s = velocity_stats([Note.rest(1.0)])
        assert s["count"] == 0


class TestVelocityCurve:
    def test_returns_list(self):
        notes = [Note("C", 5, 1.0, velocity=80), Note.rest(1.0)]
        vc = velocity_curve(notes)
        assert vc == [80, 0]

    def test_empty(self):
        assert velocity_curve([]) == []
