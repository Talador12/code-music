"""Tests for v39.0 — neapolitan_chord, augmented_sixth, picardy_third."""

import pytest

from code_music.theory import augmented_sixth, neapolitan_chord, picardy_third


class TestNeapolitanChord:
    def test_c_key_returns_three_notes(self):
        notes = neapolitan_chord("C")
        assert len(notes) == 3

    def test_c_key_root_is_db_major(self):
        notes = neapolitan_chord("C")
        # bII in C = Db major. First inversion: F in bass, Db, Ab
        pitches = [n.pitch for n in notes]
        assert "F" in pitches  # bass note (3rd of Db)
        assert "C#" in pitches or "Db" in pitches  # root of bII

    def test_a_key(self):
        notes = neapolitan_chord("A")
        # bII in A = Bb major
        assert len(notes) == 3
        pitches = [n.pitch for n in notes]
        assert "Bb" in pitches or "D" in pitches  # notes of Bb major

    def test_custom_duration(self):
        notes = neapolitan_chord("C", duration=2.0)
        assert all(n.duration == 2.0 for n in notes)

    def test_custom_octave(self):
        notes = neapolitan_chord("C", octave=4)
        assert notes[0].octave == 4


class TestAugmentedSixth:
    def test_italian_three_notes(self):
        notes = augmented_sixth("C", "italian")
        assert len(notes) == 3

    def test_french_four_notes(self):
        notes = augmented_sixth("C", "french")
        assert len(notes) == 4

    def test_german_four_notes(self):
        notes = augmented_sixth("C", "german")
        assert len(notes) == 4

    def test_italian_contains_b6_and_sharp4(self):
        notes = augmented_sixth("C", "italian")
        pitches = [n.pitch for n in notes]
        assert "Ab" in pitches  # b6 in C
        assert "F#" in pitches  # #4 in C

    def test_french_contains_major_2nd(self):
        notes = augmented_sixth("C", "french")
        pitches = [n.pitch for n in notes]
        assert "D" in pitches  # major 2nd above C

    def test_german_contains_minor_3rd(self):
        notes = augmented_sixth("C", "german")
        pitches = [n.pitch for n in notes]
        assert "Eb" in pitches  # minor 3rd above C

    def test_unknown_variety_raises(self):
        with pytest.raises(ValueError, match="Unknown variety"):
            augmented_sixth("C", "spanish")

    def test_custom_duration(self):
        notes = augmented_sixth("C", "italian", duration=2.0)
        assert all(n.duration == 2.0 for n in notes)

    def test_g_key_italian(self):
        notes = augmented_sixth("G", "italian")
        pitches = [n.pitch for n in notes]
        assert "Eb" in pitches  # b6 in G
        assert "C#" in pitches  # #4 in G


class TestPicardyThird:
    def test_returns_three_notes(self):
        notes = picardy_third("C")
        assert len(notes) == 3

    def test_c_minor_context_major_chord(self):
        notes = picardy_third("C")
        pitches = [n.pitch for n in notes]
        assert "C" in pitches
        assert "E" in pitches  # major 3rd (not Eb)
        assert "G" in pitches

    def test_a_minor_context(self):
        notes = picardy_third("A")
        pitches = [n.pitch for n in notes]
        assert "A" in pitches
        assert "C#" in pitches  # major 3rd (not C)

    def test_custom_duration(self):
        notes = picardy_third("D", duration=8.0)
        assert all(n.duration == 8.0 for n in notes)
