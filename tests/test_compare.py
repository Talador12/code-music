"""Tests for v85.0 — compare_progressions."""

from code_music.theory import compare_progressions


class TestCompareProgressions:
    def test_identical(self):
        prog = [("C", "maj"), ("G", "dom7")]
        result = compare_progressions(prog, prog)
        assert result["shared_count"] == 2
        assert result["same_key"] is True

    def test_different(self):
        a = [("C", "maj"), ("F", "maj")]
        b = [("A", "min"), ("D", "min")]
        result = compare_progressions(a, b)
        assert result["shared_count"] == 0

    def test_partial_overlap(self):
        a = [("C", "maj"), ("G", "dom7")]
        b = [("G", "dom7"), ("D", "min")]
        result = compare_progressions(a, b)
        assert result["shared_count"] == 1

    def test_complexity_delta(self):
        simple = [("C", "maj"), ("G", "maj")]
        complex_ = [("C", "maj7"), ("Eb", "dim7"), ("Ab", "aug"), ("G", "dom7")]
        result = compare_progressions(simple, complex_, key="C")
        assert result["complexity_delta"] > 0  # complex is higher

    def test_root_overlap(self):
        a = [("C", "maj"), ("G", "dom7")]
        b = [("C", "min"), ("G", "min7")]
        result = compare_progressions(a, b)
        assert result["root_overlap"] == 1.0  # same roots

    def test_empty(self):
        result = compare_progressions([], [("C", "maj")])
        assert result["length_a"] == 0
