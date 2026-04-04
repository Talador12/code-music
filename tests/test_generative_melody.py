"""Tests for v47.0 — generate_scale_melody, generate_rhythm_pattern."""

import pytest

from code_music.theory import generate_rhythm_pattern, generate_scale_melody


class TestGenerateScaleMelody:
    def test_correct_length(self):
        melody = generate_scale_melody(length=16, seed=42)
        assert len(melody) == 16

    def test_all_notes_have_pitch(self):
        melody = generate_scale_melody(length=8, seed=42)
        for n in melody:
            assert n.pitch is not None

    def test_duration_preserved(self):
        melody = generate_scale_melody(duration=0.25, length=4, seed=42)
        assert all(n.duration == 0.25 for n in melody)

    def test_deterministic_with_seed(self):
        m1 = generate_scale_melody(seed=123, length=8)
        m2 = generate_scale_melody(seed=123, length=8)
        assert [n.pitch for n in m1] == [n.pitch for n in m2]

    def test_different_seeds_differ(self):
        m1 = generate_scale_melody(seed=1, length=16)
        m2 = generate_scale_melody(seed=2, length=16)
        pitches1 = [n.pitch for n in m1]
        pitches2 = [n.pitch for n in m2]
        assert pitches1 != pitches2

    def test_minor_scale(self):
        melody = generate_scale_melody(key="A", scale_name="minor", length=8, seed=42)
        assert len(melody) == 8

    def test_dorian_scale(self):
        melody = generate_scale_melody(key="D", scale_name="dorian", length=8, seed=42)
        assert len(melody) == 8

    def test_unknown_scale_raises(self):
        with pytest.raises(ValueError, match="Unknown scale"):
            generate_scale_melody(scale_name="unicorn", seed=42)

    def test_arch_contour(self):
        melody = generate_scale_melody(contour="arch", length=20, seed=42)
        assert len(melody) == 20

    def test_descending_contour(self):
        melody = generate_scale_melody(contour="descending", length=12, seed=42)
        assert len(melody) == 12

    def test_wave_contour(self):
        melody = generate_scale_melody(contour="wave", length=16, seed=42)
        assert len(melody) == 16

    def test_flat_contour(self):
        melody = generate_scale_melody(contour="flat", length=8, seed=42)
        assert len(melody) == 8


class TestGenerateRhythmPattern:
    def test_correct_slot_count(self):
        result = generate_rhythm_pattern(hits=4, slots=16, seed=42)
        assert len(result) == 16

    def test_correct_hit_count(self):
        result = generate_rhythm_pattern(hits=6, slots=16, seed=42)
        hit_count = sum(1 for n in result if n.pitch is not None)
        assert hit_count == 6

    def test_rest_count(self):
        result = generate_rhythm_pattern(hits=4, slots=8, seed=42)
        rest_count = sum(1 for n in result if n.pitch is None)
        assert rest_count == 4

    def test_deterministic(self):
        r1 = generate_rhythm_pattern(hits=5, slots=16, seed=77)
        r2 = generate_rhythm_pattern(hits=5, slots=16, seed=77)
        p1 = [n.pitch for n in r1]
        p2 = [n.pitch for n in r2]
        assert p1 == p2

    def test_all_hits(self):
        result = generate_rhythm_pattern(hits=8, slots=8, seed=42)
        assert all(n.pitch is not None for n in result)

    def test_duration(self):
        result = generate_rhythm_pattern(duration_per_slot=0.5, slots=4, seed=42)
        assert all(n.duration == 0.5 for n in result)
