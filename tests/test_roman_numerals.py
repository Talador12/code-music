"""Tests for v44.0 — parse_roman, progression_from_roman."""

import pytest

from code_music.theory import parse_roman, progression_from_roman


class TestParseRoman:
    def test_major_I(self):
        assert parse_roman("I", "C") == ("C", "maj")

    def test_major_IV(self):
        assert parse_roman("IV", "C") == ("F", "maj")

    def test_major_V(self):
        assert parse_roman("V", "C") == ("G", "maj")

    def test_minor_ii(self):
        assert parse_roman("ii", "C") == ("D", "min")

    def test_minor_vi(self):
        assert parse_roman("vi", "C") == ("A", "min")

    def test_dom7(self):
        assert parse_roman("V7", "C") == ("G", "dom7")

    def test_maj7(self):
        assert parse_roman("Imaj7", "C") == ("C", "maj7")

    def test_min7(self):
        assert parse_roman("ii7", "C") == ("D", "min7")

    def test_diminished(self):
        assert parse_roman("viio", "C") == ("B", "dim")

    def test_diminished_7(self):
        assert parse_roman("viio7", "C") == ("B", "dim7")

    def test_augmented(self):
        assert parse_roman("III+", "C") == ("E", "aug")

    def test_flat_accidental(self):
        root, shape = parse_roman("bVI", "C")
        assert root == "Ab"
        assert shape == "maj"

    def test_sharp_accidental(self):
        root, shape = parse_roman("#IV", "C")
        assert root == "F#"
        assert shape == "maj"

    def test_applied_chord_v_of_v(self):
        root, shape = parse_roman("V/V", "C")
        assert root == "D"
        assert shape == "maj"  # V without 7 = major; use V7/V for dom7

    def test_applied_chord_v7_of_v(self):
        root, shape = parse_roman("V7/V", "C")
        assert root == "D"
        assert shape == "dom7"

    def test_applied_chord_v7_of_ii(self):
        root, shape = parse_roman("V7/ii", "C")
        assert root == "A"
        assert shape == "dom7"

    def test_different_key(self):
        assert parse_roman("I", "G") == ("G", "maj")
        assert parse_roman("V", "G") == ("D", "maj")

    def test_sus4(self):
        assert parse_roman("Vsus4", "C") == ("G", "sus4")

    def test_unknown_numeral_raises(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_roman("xyz", "C")


class TestProgressionFromRoman:
    def test_basic_progression(self):
        prog = progression_from_roman(["I", "IV", "V", "I"], "C")
        assert prog == [("C", "maj"), ("F", "maj"), ("G", "maj"), ("C", "maj")]

    def test_jazz_turnaround(self):
        prog = progression_from_roman(["Imaj7", "vi7", "ii7", "V7"], "C")
        assert prog[0] == ("C", "maj7")
        assert prog[1] == ("A", "min7")
        assert prog[2] == ("D", "min7")
        assert prog[3] == ("G", "dom7")

    def test_different_key(self):
        prog = progression_from_roman(["I", "V"], "Eb")
        assert prog[0] == ("Eb", "maj")
        assert prog[1] == ("Bb", "maj")

    def test_empty_list(self):
        assert progression_from_roman([], "C") == []

    def test_pop_progression(self):
        prog = progression_from_roman(["I", "V", "vi", "IV"], "G")
        assert prog[0] == ("G", "maj")
        assert prog[1] == ("D", "maj")
        assert prog[2] == ("E", "min")
        assert prog[3] == ("C", "maj")

    def test_neapolitan(self):
        root, shape = parse_roman("bII", "C")
        assert root == "C#"  # enharmonic; bII of C = Db = C#
        assert shape == "maj"
