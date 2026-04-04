"""Tests for v126.0 — smooth_melody, fill_leaps."""

from code_music.engine import Note
from code_music.theory import fill_leaps, smooth_melody


class TestSmoothMelody:
    def test_no_leaps_unchanged(self):
        notes = [Note("C", 4, 1.0), Note("D", 4, 1.0)]
        result = smooth_melody(notes, max_leap=4)
        assert len(result) == 2

    def test_large_leap_adds_note(self):
        notes = [Note("C", 4, 1.0), Note("C", 5, 1.0)]  # octave = 12 semitones
        result = smooth_melody(notes, max_leap=4)
        assert len(result) > 2  # passing tone inserted

    def test_preserves_endpoints(self):
        notes = [Note("C", 4, 2.0), Note("G", 5, 1.0)]
        result = smooth_melody(notes, max_leap=3)
        assert result[-1].pitch == "G"

    def test_single_note(self):
        assert len(smooth_melody([Note("C", 4, 1.0)])) == 1

    def test_rest_passthrough(self):
        notes = [Note("C", 4, 1.0), Note.rest(1.0), Note("G", 5, 1.0)]
        result = smooth_melody(notes, max_leap=3)
        assert any(n.pitch is None for n in result)


class TestFillLeaps:
    def test_fills_octave(self):
        notes = [Note("C", 4, 12.0), Note("C", 5, 1.0)]  # 12 semitone leap
        result = fill_leaps(notes, threshold=5)
        assert len(result) > 2  # chromatic steps inserted

    def test_small_interval_unchanged(self):
        notes = [Note("C", 4, 1.0), Note("D", 4, 1.0)]
        result = fill_leaps(notes, threshold=5)
        assert len(result) == 2

    def test_preserves_last_note(self):
        notes = [Note("C", 4, 6.0), Note("F#", 4, 1.0)]
        result = fill_leaps(notes, threshold=5)
        assert result[-1].pitch == "F#"
