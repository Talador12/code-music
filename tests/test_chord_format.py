"""Tests for v107.0 — format_chord, format_progression."""

from code_music.theory import format_chord, format_progression


class TestFormatChord:
    def test_major(self):
        assert format_chord("C", "maj") == "C"

    def test_minor(self):
        assert format_chord("A", "min") == "Am"

    def test_dom7(self):
        assert format_chord("G", "dom7") == "G7"

    def test_maj7(self):
        assert format_chord("C", "maj7") == "Cmaj7"

    def test_min7(self):
        assert format_chord("D", "min7") == "Dm7"

    def test_dim(self):
        assert format_chord("B", "dim") == "Bdim"

    def test_aug(self):
        assert format_chord("E", "aug") == "E+"

    def test_sus4(self):
        assert format_chord("G", "sus4") == "Gsus4"

    def test_sharp_root(self):
        assert format_chord("F#", "min") == "F#m"


class TestFormatProgression:
    def test_basic(self):
        prog = [("C", "maj"), ("G", "dom7")]
        result = format_progression(prog)
        assert result == "C | G7"

    def test_custom_separator(self):
        prog = [("C", "maj7"), ("D", "min7")]
        result = format_progression(prog, separator=" - ")
        assert result == "Cmaj7 - Dm7"

    def test_single_chord(self):
        assert format_progression([("A", "min")]) == "Am"
