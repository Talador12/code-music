"""Tests for v97.0 — harmonic_field, chord_relationships."""

from code_music.theory import chord_relationships, harmonic_field


class TestHarmonicField:
    def test_seven_chords(self):
        field = harmonic_field("C")
        assert len(field) == 7

    def test_first_is_tonic(self):
        field = harmonic_field("C")
        assert field[0]["roman"] == "I"
        assert field[0]["root"] == "C"
        assert field[0]["function"] == "T"

    def test_fifth_is_dominant(self):
        field = harmonic_field("C")
        assert field[4]["roman"] == "V"
        assert field[4]["function"] == "D"

    def test_minor_mode(self):
        field = harmonic_field("A", "minor")
        assert field[0]["roman"] == "i"
        assert field[0]["shape"] == "min"

    def test_different_key(self):
        field = harmonic_field("G")
        assert field[0]["root"] == "G"
        assert field[4]["root"] == "D"  # V of G

    def test_all_have_function(self):
        field = harmonic_field("C")
        for chord in field:
            assert chord["function"] in ("T", "S", "D")


class TestChordRelationships:
    def test_v_resolves_to_i(self):
        rels = chord_relationships("C")
        assert "I" in rels["V"]

    def test_tonic_resolves_nowhere(self):
        rels = chord_relationships("C")
        assert rels["I"] == []

    def test_all_seven_present(self):
        rels = chord_relationships("C")
        assert len(rels) == 7
