"""Tests for retrograde_rhythm, stretch_melody."""

from code_music import Note
from code_music.theory import retrograde_rhythm, stretch_melody


class TestRetrogradeRhythm:
    def test_basic(self):
        notes = [Note("C", 4, 0.5), Note("E", 4, 1.0), Note("G", 4, 2.0)]
        r = retrograde_rhythm(notes)
        assert r[0].pitch == "C" and r[0].duration == 2.0
        assert r[2].pitch == "G" and r[2].duration == 0.5

    def test_preserves_pitch_order(self):
        notes = [Note("A", 4, 1.0), Note("B", 4, 0.5)]
        r = retrograde_rhythm(notes)
        assert [n.pitch for n in r] == ["A", "B"]

    def test_rests(self):
        notes = [Note.rest(1.0), Note("C", 4, 2.0)]
        r = retrograde_rhythm(notes)
        assert r[0].pitch is None and r[0].duration == 2.0


class TestStretchMelody:
    def test_double(self):
        notes = [Note("C", 4, 1.0)]
        s = stretch_melody(notes, 2.0)
        assert s[0].duration == 2.0

    def test_half(self):
        notes = [Note("C", 4, 1.0)]
        s = stretch_melody(notes, 0.5)
        assert s[0].duration == 0.5

    def test_preserves_pitch(self):
        notes = [Note("E", 5, 1.0)]
        s = stretch_melody(notes, 3.0)
        assert s[0].pitch == "E"

    def test_minimum_duration(self):
        notes = [Note("C", 4, 0.1)]
        s = stretch_melody(notes, 0.01)
        assert s[0].duration >= 0.0625
