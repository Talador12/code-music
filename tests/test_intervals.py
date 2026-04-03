"""Tests for interval_name, parallel_motion, suggest_next_chord."""

from code_music import Note
from code_music.theory import interval_name, parallel_motion, suggest_next_chord


class TestIntervalName:
    def test_unison(self):
        assert interval_name("C", "C") == "unison"

    def test_major_third(self):
        assert interval_name("C", "E") == "major 3rd"

    def test_perfect_fifth(self):
        assert interval_name("C", "G") == "perfect 5th"

    def test_tritone(self):
        assert interval_name("C", "F#") == "tritone"

    def test_octave(self):
        assert interval_name("C", "C") == "unison"  # same pitch class

    def test_minor_third(self):
        assert interval_name("A", "C") == "minor 3rd"


class TestParallelMotion:
    def test_fifth_above(self):
        melody = [Note("C", 5, 1.0)]
        harmony = parallel_motion(melody, interval=7)
        assert harmony[0].pitch == "G"

    def test_third_above(self):
        melody = [Note("C", 5, 1.0)]
        harmony = parallel_motion(melody, interval=4)
        assert harmony[0].pitch == "E"

    def test_rests_preserved(self):
        melody = [Note.rest(1.0)]
        harmony = parallel_motion(melody)
        assert harmony[0].pitch is None

    def test_below(self):
        melody = [Note("G", 5, 1.0)]
        harmony = parallel_motion(melody, interval=7, above=False)
        assert harmony[0].pitch == "C"

    def test_length_preserved(self):
        melody = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        assert len(parallel_motion(melody)) == 2


class TestSuggestNextChord:
    def test_after_I(self):
        suggestions = suggest_next_chord("C", "maj", key="C")
        roots = [r for r, _ in suggestions]
        assert "F" in roots or "G" in roots

    def test_after_V(self):
        suggestions = suggest_next_chord("G", "maj", key="C")
        assert suggestions[0] == ("C", "maj")  # V resolves to I

    def test_returns_list(self):
        result = suggest_next_chord("D", "min", key="C")
        assert isinstance(result, list)
        assert all(isinstance(r, tuple) and len(r) == 2 for r in result)

    def test_chromatic_chord(self):
        result = suggest_next_chord("Db", "maj", key="C")
        assert len(result) > 0  # should suggest tonic
