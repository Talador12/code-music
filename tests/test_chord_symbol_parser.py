"""Tests for v125.0 — parse_chord_symbol, parse_chord_symbols."""

import pytest

from code_music.theory import parse_chord_symbol, parse_chord_symbols


class TestParseChordSymbol:
    def test_major(self):
        assert parse_chord_symbol("C") == ("C", "maj")

    def test_minor(self):
        assert parse_chord_symbol("Am") == ("A", "min")

    def test_dom7(self):
        assert parse_chord_symbol("G7") == ("G", "dom7")

    def test_maj7(self):
        assert parse_chord_symbol("Cmaj7") == ("C", "maj7")

    def test_min7(self):
        assert parse_chord_symbol("Dm7") == ("D", "min7")

    def test_dim(self):
        assert parse_chord_symbol("Bdim") == ("B", "dim")

    def test_dim7(self):
        assert parse_chord_symbol("Bbdim7") == ("Bb", "dim7")

    def test_aug(self):
        assert parse_chord_symbol("E+") == ("E", "aug")

    def test_sus4(self):
        assert parse_chord_symbol("Asus4") == ("A", "sus4")

    def test_sharp_root(self):
        assert parse_chord_symbol("F#m") == ("F#", "min")

    def test_flat_root(self):
        assert parse_chord_symbol("Bbmaj7") == ("Bb", "maj7")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            parse_chord_symbol("")


class TestParseChordSymbols:
    def test_basic(self):
        result = parse_chord_symbols("Cmaj7 Dm7 G7 Cmaj7")
        assert len(result) == 4
        assert result[0] == ("C", "maj7")
        assert result[2] == ("G", "dom7")

    def test_single(self):
        assert parse_chord_symbols("Am") == [("A", "min")]

    def test_empty(self):
        assert parse_chord_symbols("") == []
