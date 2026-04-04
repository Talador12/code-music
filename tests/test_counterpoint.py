"""Tests for v46.0 — classify_interval, species_counterpoint."""

import pytest

from code_music.engine import Note
from code_music.theory import classify_interval, species_counterpoint


class TestClassifyInterval:
    def test_unison_perfect(self):
        assert classify_interval(0) == "perfect"

    def test_fifth_perfect(self):
        assert classify_interval(7) == "perfect"

    def test_major_third_imperfect(self):
        assert classify_interval(4) == "imperfect"

    def test_minor_third_imperfect(self):
        assert classify_interval(3) == "imperfect"

    def test_major_sixth_imperfect(self):
        assert classify_interval(9) == "imperfect"

    def test_minor_second_dissonant(self):
        assert classify_interval(1) == "dissonant"

    def test_tritone_dissonant(self):
        assert classify_interval(6) == "dissonant"

    def test_major_seventh_dissonant(self):
        assert classify_interval(11) == "dissonant"

    def test_octave_wraps(self):
        assert classify_interval(12) == "perfect"  # 12 % 12 = 0

    def test_negative_handled(self):
        assert classify_interval(-7) == "perfect"


class TestSpeciesCounterpoint:
    def test_species_1_same_length(self):
        cf = [Note("C", 4, 4.0), Note("D", 4, 4.0), Note("E", 4, 4.0)]
        cp = species_counterpoint(cf, species=1, seed=42)
        assert len(cp) == len(cf)

    def test_species_1_all_consonant(self):
        cf = [Note("C", 4, 4.0), Note("E", 4, 4.0)]
        cp = species_counterpoint(cf, species=1, seed=42)
        for note in cp:
            assert note.pitch is not None

    def test_species_1_preserves_duration(self):
        cf = [Note("C", 4, 4.0)]
        cp = species_counterpoint(cf, species=1, seed=42)
        assert cp[0].duration == 4.0

    def test_species_2_double_length(self):
        cf = [Note("C", 4, 4.0), Note("D", 4, 4.0)]
        cp = species_counterpoint(cf, species=2, seed=42)
        assert len(cp) == 4  # 2 notes per CF note

    def test_species_2_half_duration(self):
        cf = [Note("C", 4, 4.0)]
        cp = species_counterpoint(cf, species=2, seed=42)
        assert cp[0].duration == 2.0

    def test_rest_passthrough(self):
        cf = [Note.rest(4.0)]
        cp = species_counterpoint(cf, species=1, seed=42)
        assert cp[0].pitch is None

    def test_deterministic_with_seed(self):
        cf = [Note("C", 4, 4.0), Note("E", 4, 4.0), Note("G", 4, 4.0)]
        cp1 = species_counterpoint(cf, species=1, seed=99)
        cp2 = species_counterpoint(cf, species=1, seed=99)
        assert [n.pitch for n in cp1] == [n.pitch for n in cp2]

    def test_invalid_species_raises(self):
        with pytest.raises(ValueError, match="species 1 and 2"):
            species_counterpoint([Note("C", 4, 4.0)], species=5)

    def test_below(self):
        cf = [Note("C", 5, 4.0)]
        cp = species_counterpoint(cf, species=1, above=False, seed=42)
        assert len(cp) == 1
