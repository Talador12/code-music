"""Tests for v117.0 — chord_tones, is_chord_tone, filter_chord_tones."""

from code_music.engine import Note
from code_music.theory import chord_tones, filter_chord_tones, is_chord_tone


class TestChordTones:
    def test_c_major(self):
        tones = chord_tones("C", "maj")
        assert "C" in tones and "E" in tones and "G" in tones

    def test_d_min7(self):
        tones = chord_tones("D", "min7")
        assert len(tones) == 4


class TestIsChordTone:
    def test_in_chord(self):
        assert is_chord_tone("E", "C", "maj") is True

    def test_not_in_chord(self):
        assert is_chord_tone("F", "C", "maj") is False

    def test_root(self):
        assert is_chord_tone("C", "C", "maj") is True


class TestFilterChordTones:
    def test_keeps_chord_tones(self):
        notes = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]
        result = filter_chord_tones(notes, "C", "maj")
        assert all(n.pitch is not None for n in result)

    def test_replaces_non_chord_tones(self):
        notes = [Note("C", 5, 1.0), Note("D", 5, 1.0)]  # D is not in C major triad
        result = filter_chord_tones(notes, "C", "maj")
        assert result[0].pitch == "C"
        assert result[1].pitch is None  # D replaced with rest

    def test_preserves_duration(self):
        notes = [Note("D", 5, 2.0)]
        result = filter_chord_tones(notes, "C", "maj")
        assert result[0].duration == 2.0
