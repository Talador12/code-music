"""Tests for v51.0 — ear_training_intervals, ear_training_chords, scale_exercise."""

import pytest

from code_music.theory import ear_training_chords, ear_training_intervals, scale_exercise


class TestEarTrainingIntervals:
    def test_correct_count(self):
        exercises = ear_training_intervals(count=5, seed=42)
        assert len(exercises) == 5

    def test_exercise_structure(self):
        exercises = ear_training_intervals(count=1, seed=42)
        ex = exercises[0]
        assert "note_a" in ex
        assert "note_b" in ex
        assert "semitones" in ex
        assert "interval_name" in ex

    def test_interval_range(self):
        exercises = ear_training_intervals(count=20, max_semitones=7, seed=42)
        for ex in exercises:
            assert 1 <= ex["semitones"] <= 7

    def test_deterministic(self):
        a = ear_training_intervals(count=5, seed=99)
        b = ear_training_intervals(count=5, seed=99)
        assert [e["semitones"] for e in a] == [e["semitones"] for e in b]

    def test_notes_have_pitch(self):
        exercises = ear_training_intervals(count=3, seed=42)
        for ex in exercises:
            assert ex["note_a"].pitch is not None
            assert ex["note_b"].pitch is not None


class TestEarTrainingChords:
    def test_correct_count(self):
        exercises = ear_training_chords(count=8, seed=42)
        assert len(exercises) == 8

    def test_exercise_structure(self):
        exercises = ear_training_chords(count=1, seed=42)
        ex = exercises[0]
        assert "root" in ex
        assert "shape" in ex
        assert "notes" in ex

    def test_custom_types(self):
        exercises = ear_training_chords(count=10, types=["maj", "min"], seed=42)
        for ex in exercises:
            assert ex["shape"] in ("maj", "min")

    def test_deterministic(self):
        a = ear_training_chords(count=5, seed=77)
        b = ear_training_chords(count=5, seed=77)
        assert [e["shape"] for e in a] == [e["shape"] for e in b]


class TestScaleExercise:
    def test_ascending(self):
        notes = scale_exercise("C", "major", "ascending")
        assert len(notes) == 8  # 7 scale degrees + octave
        assert notes[0].pitch == "C"
        assert notes[-1].pitch == "C"

    def test_descending(self):
        notes = scale_exercise("C", "major", "descending")
        assert notes[0].pitch == "C"  # starts at octave
        assert notes[-1].pitch == "C"  # ends at root

    def test_both(self):
        notes = scale_exercise("C", "major", "both")
        assert len(notes) == 15  # 8 up + 7 down (no double top)

    def test_minor(self):
        notes = scale_exercise("A", "minor")
        assert notes[0].pitch == "A"

    def test_unknown_scale_raises(self):
        with pytest.raises(ValueError, match="Unknown scale"):
            scale_exercise("C", "unicorn_mode")

    def test_custom_duration(self):
        notes = scale_exercise("C", "major", duration=1.0)
        assert all(n.duration == 1.0 for n in notes)
