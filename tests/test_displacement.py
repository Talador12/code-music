"""Tests for v45.0 — displace, phase_shift, hemiola, additive_rhythm, aksak."""

import pytest

from code_music.engine import Note
from code_music.theory import additive_rhythm, aksak, displace, hemiola, phase_shift


class TestDisplace:
    def test_adds_leading_rest(self):
        notes = [Note("C", 5, 1.0)]
        result = displace(notes, 0.5)
        assert len(result) == 2
        assert result[0].pitch is None  # rest
        assert result[0].duration == 0.5
        assert result[1].pitch == "C"

    def test_zero_offset_no_change(self):
        notes = [Note("C", 5, 1.0)]
        result = displace(notes, 0)
        assert len(result) == 1

    def test_empty_input(self):
        assert displace([], 1.0) == []

    def test_preserves_original(self):
        notes = [Note("E", 4, 0.5), Note("G", 4, 0.5)]
        result = displace(notes, 1.0)
        assert result[1].pitch == "E"
        assert result[2].pitch == "G"


class TestPhaseShift:
    def test_pattern_a_unchanged(self):
        a = [Note("C", 5, 1.0)]
        b = [Note("E", 5, 1.0)]
        ra, rb = phase_shift(a, b, 0.25)
        assert len(ra) == 1
        assert ra[0].pitch == "C"

    def test_pattern_b_displaced(self):
        a = [Note("C", 5, 1.0)]
        b = [Note("E", 5, 1.0)]
        _, rb = phase_shift(a, b, 0.25)
        assert len(rb) == 2  # rest + original
        assert rb[0].pitch is None


class TestHemiola:
    def test_voice_counts(self):
        v3, v2 = hemiola("C", bars=2)
        assert len(v3) == 6  # 3 beats * 2 bars
        assert len(v2) == 4  # 2 groups * 2 bars

    def test_total_duration_matches(self):
        v3, v2 = hemiola("D", bars=1, duration=1.0)
        total3 = sum(n.duration for n in v3)
        total2 = sum(n.duration for n in v2)
        assert abs(total3 - total2) < 1e-9

    def test_octave_offset(self):
        v3, v2 = hemiola("C", octave=3)
        assert v3[0].octave == 3
        assert v2[0].octave == 4


class TestAdditiveRhythm:
    def test_tresillo(self):
        result = additive_rhythm([3, 3, 2])
        assert len(result) == 8  # 3+3+2 = 8 beats

    def test_accents(self):
        result = additive_rhythm([2, 3])
        assert result[0].velocity == 100  # first of group 1
        assert result[1].velocity == 60  # fill
        assert result[2].velocity == 100  # first of group 2

    def test_single_group(self):
        result = additive_rhythm([4])
        assert len(result) == 4


class TestAksak:
    def test_7_8(self):
        result = aksak("7/8")
        assert len(result) == 7  # 2+2+3

    def test_9_8(self):
        result = aksak("9/8")
        assert len(result) == 9

    def test_11_8(self):
        result = aksak("11/8")
        assert len(result) == 11

    def test_multiple_bars(self):
        result = aksak("7/8", bars=3)
        assert len(result) == 21  # 7 * 3

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown aksak"):
            aksak("13/8")

    def test_5_8(self):
        result = aksak("5/8")
        assert len(result) == 5
