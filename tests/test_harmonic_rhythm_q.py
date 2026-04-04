"""Tests for v127.0 — chords_per_bar, quantize_harmonic_rhythm."""

from code_music.theory import chords_per_bar, quantize_harmonic_rhythm


class TestChordsPerBar:
    def test_basic(self):
        assert chords_per_bar([("C", "maj")] * 4, total_bars=4) == 1.0

    def test_two_per_bar(self):
        assert chords_per_bar([("C", "maj")] * 8, total_bars=4) == 2.0

    def test_zero_bars(self):
        assert chords_per_bar([("C", "maj")], total_bars=0) == 0.0

    def test_fractional(self):
        result = chords_per_bar([("C", "maj")] * 3, total_bars=2)
        assert result == 1.5


class TestQuantizeHarmonicRhythm:
    def test_contract(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]
        result = quantize_harmonic_rhythm(prog, target_chords_per_bar=2)
        assert len(result) == 2

    def test_expand(self):
        prog = [("C", "maj"), ("G", "dom7")]
        result = quantize_harmonic_rhythm(prog, target_chords_per_bar=4)
        assert len(result) >= 4

    def test_empty(self):
        assert quantize_harmonic_rhythm([], target_chords_per_bar=2) == []

    def test_single_chord(self):
        result = quantize_harmonic_rhythm([("C", "maj")], target_chords_per_bar=1)
        assert len(result) >= 1
