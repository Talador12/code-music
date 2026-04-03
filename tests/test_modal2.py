"""Tests for dorian_lick, phrygian_run, tritone_sub."""

from code_music.theory import dorian_lick, phrygian_run, tritone_sub


class TestDorianLick:
    def test_basic(self):
        lick = dorian_lick("D", seed=42)
        assert len(lick) >= 6
        assert lick[-1].pitch == "D"

    def test_reproducible(self):
        a = dorian_lick("A", seed=42)
        b = dorian_lick("A", seed=42)
        assert [n.pitch for n in a] == [n.pitch for n in b]


class TestPhrygianRun:
    def test_basic(self):
        r = phrygian_run("E", length=7)
        assert len(r) == 7
        assert r[0].pitch == "E"

    def test_flat_two(self):
        r = phrygian_run("E", length=2)
        assert r[1].pitch == "F"  # b2


class TestTritoneSub:
    def test_dom7(self):
        prog = [("G", "dom7")]
        subbed = tritone_sub(prog)
        assert subbed[0][0] == "C#"  # tritone of G

    def test_non_dominant_unchanged(self):
        prog = [("C", "maj7"), ("A", "min7")]
        subbed = tritone_sub(prog)
        assert subbed == prog

    def test_mixed(self):
        prog = [("C", "maj7"), ("G", "dom7"), ("A", "min7")]
        subbed = tritone_sub(prog)
        assert subbed[0] == ("C", "maj7")
        assert subbed[1][0] == "C#"
        assert subbed[2] == ("A", "min7")
