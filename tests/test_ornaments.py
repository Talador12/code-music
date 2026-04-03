"""Tests for chromatic_run, trill, diminished_run."""

from code_music.theory import chromatic_run, diminished_run, trill


class TestChromaticRun:
    def test_up(self):
        r = chromatic_run("C", 4, length=5, direction="up")
        assert len(r) == 5
        assert r[0].pitch == "C"
        assert r[1].pitch == "C#"

    def test_down(self):
        r = chromatic_run("E", 4, length=3, direction="down")
        assert r[0].pitch == "E"

    def test_full_octave(self):
        r = chromatic_run("C", 4, length=12)
        assert len(r) == 12


class TestTrill:
    def test_basic(self):
        t = trill("C", 4, duration=1.0, speed=0.125)
        assert len(t) == 8
        assert t[0].pitch == "C"
        assert t[1].pitch == "C#"

    def test_lower(self):
        t = trill("E", 4, upper=False, duration=0.5, speed=0.125)
        assert t[1].pitch == "Eb"

    def test_alternates(self):
        t = trill("A", 4, duration=0.5, speed=0.125)
        assert t[0].pitch != t[1].pitch


class TestDiminishedRun:
    def test_basic(self):
        r = diminished_run("C", length=8)
        assert len(r) == 8
        assert r[0].pitch == "C"

    def test_half_whole(self):
        r = diminished_run("C", length=3)
        # C, C#, Eb (half-whole pattern)
        assert r[1].pitch == "C#"
        assert r[2].pitch == "Eb"
