"""Tests for v41.0 — twelve_bar_blues, rhythm_changes, coltrane_changes, andalusian_cadence."""

from code_music.theory import (
    andalusian_cadence,
    coltrane_changes,
    rhythm_changes,
    twelve_bar_blues,
)


class TestTwelveBarBlues:
    def test_twelve_bars(self):
        prog = twelve_bar_blues("C")
        assert len(prog) == 12

    def test_all_dom7(self):
        prog = twelve_bar_blues("C")
        assert all(shape == "dom7" for _, shape in prog)

    def test_starts_on_tonic(self):
        prog = twelve_bar_blues("A")
        assert prog[0][0] == "A"

    def test_bar_5_is_iv(self):
        prog = twelve_bar_blues("C")
        assert prog[4][0] == "F"  # IV of C

    def test_bar_9_is_v(self):
        prog = twelve_bar_blues("C")
        assert prog[8][0] == "G"  # V of C

    def test_g_key(self):
        prog = twelve_bar_blues("G")
        assert prog[0][0] == "G"  # I
        assert prog[4][0] == "C"  # IV
        assert prog[8][0] == "D"  # V


class TestRhythmChanges:
    def test_eight_bars(self):
        prog = rhythm_changes("Bb")
        assert len(prog) == 8

    def test_starts_on_tonic_maj7(self):
        prog = rhythm_changes("Bb")
        assert prog[0] == ("Bb", "maj7")

    def test_bar_2_is_vi_min7(self):
        prog = rhythm_changes("Bb")
        assert prog[1][1] == "min7"

    def test_bar_4_is_v_dom7(self):
        prog = rhythm_changes("Bb")
        assert prog[3][1] == "dom7"

    def test_c_key(self):
        prog = rhythm_changes("C")
        assert prog[0] == ("C", "maj7")
        assert prog[2] == ("D", "min7")  # ii
        assert prog[3] == ("G", "dom7")  # V


class TestColtraneChanges:
    def test_twelve_chords(self):
        prog = coltrane_changes("C")
        assert len(prog) == 12

    def test_three_tonal_centers(self):
        prog = coltrane_changes("C")
        roots = [r for r, _ in prog]
        # C, E, Ab are the three centers (major thirds apart)
        assert "C" in roots
        assert "E" in roots
        assert "Ab" in roots

    def test_starts_on_tonic(self):
        prog = coltrane_changes("Eb")
        assert prog[0][0] == "Eb"

    def test_has_dom7_resolutions(self):
        prog = coltrane_changes("C")
        dom7_count = sum(1 for _, s in prog if s == "dom7")
        assert dom7_count == 6  # V7 of each of the 3 centers, twice each


class TestAndalusianCadence:
    def test_four_chords(self):
        prog = andalusian_cadence("A")
        assert len(prog) == 4

    def test_starts_on_minor_tonic(self):
        prog = andalusian_cadence("A")
        assert prog[0] == ("A", "min")

    def test_descending_pattern(self):
        prog = andalusian_cadence("A")
        assert prog[0] == ("A", "min")
        assert prog[1] == ("G", "maj")  # bVII
        assert prog[2] == ("F", "maj")  # bVI
        assert prog[3] == ("E", "maj")  # V

    def test_d_minor(self):
        prog = andalusian_cadence("D")
        assert prog[0] == ("D", "min")
        assert prog[1] == ("C", "maj")  # bVII
        assert prog[2] == ("Bb", "maj")  # bVI
        assert prog[3] == ("A", "maj")  # V

    def test_e_minor(self):
        prog = andalusian_cadence("E")
        assert prog[0] == ("E", "min")
        assert prog[3] == ("B", "maj")  # V
