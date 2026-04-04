"""Tests for v116.0 — scale_degree, scale_degree_name."""

from code_music.theory import scale_degree, scale_degree_name


class TestScaleDegree:
    def test_tonic(self):
        assert scale_degree("C", "C") == 0

    def test_fifth(self):
        assert scale_degree("G", "C") == 7

    def test_minor_third(self):
        assert scale_degree("Eb", "C") == 3

    def test_different_key(self):
        assert scale_degree("D", "G") == 7  # D is the 5th of G


class TestScaleDegreeName:
    def test_tonic(self):
        assert "tonic" in scale_degree_name("C", "C")

    def test_fifth(self):
        assert "5" in scale_degree_name("G", "C")

    def test_tritone(self):
        assert "tritone" in scale_degree_name("F#", "C")
