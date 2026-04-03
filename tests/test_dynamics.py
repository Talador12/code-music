"""Tests for swing_notes, accent_pattern, dynamics_curve."""

from code_music import Note
from code_music.theory import accent_pattern, dynamics_curve, swing_notes


class TestSwingNotes:
    def test_basic(self):
        notes = [Note("C", 4, 0.5), Note("E", 4, 0.5)]
        s = swing_notes(notes, amount=0.67)
        assert len(s) == 2
        assert s[0].duration > s[1].duration

    def test_straight(self):
        notes = [Note("C", 4, 0.5), Note("E", 4, 0.5)]
        s = swing_notes(notes, amount=0.5)
        assert abs(s[0].duration - s[1].duration) < 0.01

    def test_odd_count(self):
        notes = [Note("C", 4, 0.5), Note("E", 4, 0.5), Note("G", 4, 0.5)]
        s = swing_notes(notes, amount=0.6)
        assert len(s) == 3


class TestAccentPattern:
    def test_basic(self):
        notes = [Note("C", 4, 1.0, velocity=0.5)] * 4
        a = accent_pattern(notes, [True, False, True, False])
        assert a[0].velocity > a[1].velocity

    def test_cycles(self):
        notes = [Note("C", 4, 1.0, velocity=0.5)] * 6
        a = accent_pattern(notes, [True, False])
        assert a[4].velocity > a[5].velocity

    def test_empty_pattern(self):
        notes = [Note("C", 4, 1.0)]
        assert len(accent_pattern(notes, [])) == 1


class TestDynamicsCurve:
    def test_crescendo(self):
        notes = [Note("C", 4, 1.0, velocity=0.5)] * 8
        d = dynamics_curve(notes, start_vel=0.3, end_vel=0.9)
        assert d[0].velocity < d[-1].velocity

    def test_decrescendo(self):
        notes = [Note("C", 4, 1.0, velocity=0.5)] * 8
        d = dynamics_curve(notes, start_vel=0.9, end_vel=0.3)
        assert d[0].velocity > d[-1].velocity

    def test_empty(self):
        assert dynamics_curve([]) == []
