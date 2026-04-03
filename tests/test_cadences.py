"""Tests for secondary_dominant, deceptive_cadence, plagal_cadence."""

from code_music.theory import deceptive_cadence, plagal_cadence, secondary_dominant


class TestSecondaryDominant:
    def test_v_of_ii(self):
        root, shape = secondary_dominant("D")  # V/ii in C
        assert root == "A" and shape == "dom7"

    def test_v_of_v(self):
        root, shape = secondary_dominant("G")  # V/V in C
        assert root == "D" and shape == "dom7"

    def test_returns_dom7(self):
        _, shape = secondary_dominant("C")
        assert shape == "dom7"


class TestDeceptiveCadence:
    def test_c_major(self):
        prog = deceptive_cadence("C")
        assert len(prog) == 2
        assert prog[0] == ("G", "dom7")
        assert prog[1] == ("A", "min")

    def test_g_major(self):
        prog = deceptive_cadence("G")
        assert prog[0][0] == "D"


class TestPlagalCadence:
    def test_c_major(self):
        prog = plagal_cadence("C")
        assert len(prog) == 2
        assert prog[0] == ("F", "maj")
        assert prog[1] == ("C", "maj")

    def test_returns_to_tonic(self):
        prog = plagal_cadence("A")
        assert prog[1][0] == "A"
