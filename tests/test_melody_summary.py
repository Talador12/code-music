"""Tests for v130.0 — melody_summary."""

from code_music.engine import Note
from code_music.theory import melody_summary


class TestMelodySummary:
    def test_has_all_keys(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note.rest(0.5)]
        s = melody_summary(notes)
        assert "note_count" in s
        assert "sounding_count" in s
        assert "rest_count" in s
        assert "total_duration" in s
        assert "unique_pitches" in s
        assert "range_semitones" in s
        assert "rest_ratio" in s
        assert "leap_step_ratio" in s
        assert "repetition_ratio" in s
        assert "pitch_center" in s

    def test_counts(self):
        notes = [Note("C", 4, 1.0), Note.rest(1.0), Note("E", 4, 1.0)]
        s = melody_summary(notes)
        assert s["note_count"] == 3
        assert s["sounding_count"] == 2
        assert s["rest_count"] == 1

    def test_empty(self):
        s = melody_summary([])
        assert s["note_count"] == 0
        assert s["pitch_center"] is None

    def test_range(self):
        notes = [Note("C", 4, 1.0), Note("C", 5, 1.0)]
        s = melody_summary(notes)
        assert s["range_semitones"] == 12
