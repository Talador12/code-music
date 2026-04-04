"""Tests for v86.0 — enharmonic_equivalent, key_signature_accidentals, respell_note."""

from code_music.theory import enharmonic_equivalent, key_signature_accidentals, respell_note


class TestEnharmonicEquivalent:
    def test_c_sharp_to_db(self):
        assert enharmonic_equivalent("C#") == "Db"

    def test_db_to_c_sharp(self):
        assert enharmonic_equivalent("Db") == "C#"

    def test_natural_returns_self(self):
        assert enharmonic_equivalent("C") == "C"
        assert enharmonic_equivalent("D") == "D"

    def test_f_sharp_to_gb(self):
        assert enharmonic_equivalent("F#") == "Gb"


class TestKeySignatureAccidentals:
    def test_c_major_no_accidentals(self):
        assert key_signature_accidentals("C") == []

    def test_g_major_one_sharp(self):
        assert key_signature_accidentals("G") == ["F#"]

    def test_f_major_one_flat(self):
        assert key_signature_accidentals("F") == ["Bb"]

    def test_d_major_two_sharps(self):
        acc = key_signature_accidentals("D")
        assert "F#" in acc
        assert "C#" in acc

    def test_bb_major_two_flats(self):
        acc = key_signature_accidentals("Bb")
        assert "Bb" in acc
        assert "Eb" in acc

    def test_unknown_key(self):
        assert key_signature_accidentals("X#") == []


class TestRespellNote:
    def test_c_sharp_in_a_major(self):
        # A major has C# — keep it
        result = respell_note("C#", "A")
        assert result == "C#"

    def test_c_sharp_in_ab_major(self):
        # Ab major has Db — respell C# to Db
        result = respell_note("C#", "Ab")
        assert result == "Db"

    def test_natural_no_change(self):
        assert respell_note("C", "C") == "C"

    def test_f_sharp_in_g_major(self):
        assert respell_note("F#", "G") == "F#"
