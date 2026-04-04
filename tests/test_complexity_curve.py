"""Tests for v112.0 — complexity_curve, complexity_contrast."""

from code_music.theory import complexity_contrast, complexity_curve


class TestComplexityCurve:
    def test_length_matches(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]
        curve = complexity_curve(prog, key="C")
        assert len(curve) == 4

    def test_empty(self):
        assert complexity_curve([]) == []

    def test_values_in_range(self):
        prog = [("C", "maj")] * 8
        curve = complexity_curve(prog)
        assert all(0 <= v <= 100 for v in curve)

    def test_chromatic_higher(self):
        simple = [("C", "maj")] * 4
        complex_ = [("C", "maj7"), ("Eb", "dim7"), ("F#", "aug"), ("Bb", "dom7")]
        c_simple = complexity_curve(simple, key="C")
        c_complex = complexity_curve(complex_, key="C")
        assert max(c_complex) >= max(c_simple)


class TestComplexityContrast:
    def test_steady(self):
        prog = [("C", "maj")] * 8
        ratio = complexity_contrast(prog)
        assert abs(ratio - 1.0) < 0.5

    def test_single_chord(self):
        assert complexity_contrast([("C", "maj")]) == 1.0

    def test_returns_float(self):
        prog = [("C", "maj"), ("G", "dom7"), ("F#", "dim"), ("Eb", "aug")]
        assert isinstance(complexity_contrast(prog), float)
