"""Tests for v118.0 — melodic_range, pitch_center."""

from code_music.engine import Note
from code_music.theory import melodic_range, pitch_center


class TestMelodicRange:
    def test_basic(self):
        notes = [Note("C", 4, 1.0), Note("G", 5, 1.0)]
        r = melodic_range(notes)
        assert r["range_semitones"] == 19  # C4 to G5

    def test_same_note(self):
        notes = [Note("C", 4, 1.0)] * 4
        r = melodic_range(notes)
        assert r["range_semitones"] == 0

    def test_empty(self):
        r = melodic_range([])
        assert r["lowest"] is None

    def test_has_all_keys(self):
        notes = [Note("A", 4, 1.0)]
        r = melodic_range(notes)
        assert "lowest" in r and "highest" in r
        assert "range_semitones" in r and "range_octaves" in r
        assert "avg_pitch" in r


class TestPitchCenter:
    def test_single_note(self):
        result = pitch_center([Note("C", 4, 1.0)])
        assert result == ("C", 4)

    def test_symmetric(self):
        notes = [Note("C", 4, 1.0), Note("C", 6, 1.0)]
        result = pitch_center(notes)
        assert result is not None
        assert result[1] == 5  # average octave

    def test_empty(self):
        assert pitch_center([]) is None

    def test_with_rests(self):
        notes = [Note("G", 5, 1.0), Note.rest(1.0)]
        result = pitch_center(notes)
        assert result is not None
        assert result[0] == "G"
