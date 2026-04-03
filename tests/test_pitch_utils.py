"""Tests for normalize_notes, count_pitch_classes, melodic_interval_histogram."""

from code_music import Note
from code_music.theory import count_pitch_classes, melodic_interval_histogram, normalize_notes


class TestNormalizeNotes:
    def test_basic(self):
        notes = [Note("C", 3, 1.0), Note("E", 5, 1.0), Note("G", 6, 1.0)]
        n = normalize_notes(notes, target_octave=4)
        assert all(x.octave == 4 for x in n)

    def test_rests(self):
        notes = [Note.rest(1.0)]
        n = normalize_notes(notes)
        assert n[0].pitch is None

    def test_preserves_pitch(self):
        notes = [Note("C#", 3, 1.0)]
        n = normalize_notes(notes)
        assert n[0].pitch == "C#"


class TestCountPitchClasses:
    def test_basic(self):
        notes = [Note("C", 4, 1.0), Note("C", 5, 1.0), Note("E", 4, 1.0)]
        c = count_pitch_classes(notes)
        assert c["C"] == 2
        assert c["E"] == 1

    def test_empty(self):
        assert count_pitch_classes([]) == {}

    def test_sorted_by_freq(self):
        notes = [Note("E", 4, 1.0)] * 3 + [Note("C", 4, 1.0)]
        c = count_pitch_classes(notes)
        keys = list(c.keys())
        assert keys[0] == "E"


class TestMelodicIntervalHistogram:
    def test_basic(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)]
        h = melodic_interval_histogram(notes)
        assert len(h) > 0

    def test_single_note(self):
        assert melodic_interval_histogram([Note("C", 4, 1.0)]) == {}

    def test_returns_interval_names(self):
        notes = [Note("C", 4, 1.0), Note("G", 4, 1.0)]
        h = melodic_interval_histogram(notes)
        assert "perfect 5th" in h
