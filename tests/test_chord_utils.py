"""Tests for invert_chord, rotate_voicing, pedal_point."""

from code_music import Note
from code_music.theory import invert_chord, pedal_point, rotate_voicing


class TestInvertChord:
    def test_first_inversion(self):
        chord = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)]
        inv = invert_chord(chord, 1)
        assert inv[0].pitch == "E"
        assert inv[-1].pitch == "C"
        assert inv[-1].octave == 5

    def test_second_inversion(self):
        chord = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)]
        inv = invert_chord(chord, 2)
        assert inv[0].pitch == "G"

    def test_preserves_length(self):
        chord = [Note("C", 4, 1.0), Note("E", 4, 1.0)]
        assert len(invert_chord(chord)) == 2


class TestRotateVoicing:
    def test_basic(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)]
        r = rotate_voicing(notes, 1)
        assert r[0].pitch == "E"

    def test_empty(self):
        assert rotate_voicing([]) == []

    def test_full_rotation(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0)]
        r = rotate_voicing(notes, 2)
        assert r[0].pitch == "C"


class TestPedalPoint:
    def test_basic(self):
        melody = [Note("E", 4, 1.0), Note("G", 4, 1.0)]
        p = pedal_point("C", 3, melody)
        assert len(p) == 4
        assert p[0].pitch == "C"
        assert p[1].pitch == "E"

    def test_alternates(self):
        melody = [Note("D", 4, 0.5)]
        p = pedal_point("A", 2, melody)
        assert p[0].pitch == "A"
        assert p[1].pitch == "D"
