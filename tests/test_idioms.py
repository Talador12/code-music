"""Tests for whole_tone_run, blues_lick, arpeggio_pattern."""

from code_music.theory import arpeggio_pattern, blues_lick, whole_tone_run


class TestWholeToneRun:
    def test_basic(self):
        r = whole_tone_run("C", length=6)
        assert len(r) == 6
        assert r[0].pitch == "C"

    def test_whole_steps(self):
        r = whole_tone_run("C", length=3)
        assert r[1].pitch == "D"
        assert r[2].pitch == "E"


class TestBluesLick:
    def test_basic(self):
        lick = blues_lick("A", seed=42)
        assert len(lick) >= 6
        assert lick[-1].pitch == "A"  # ends on root

    def test_reproducible(self):
        a = blues_lick("C", seed=42)
        b = blues_lick("C", seed=42)
        assert [n.pitch for n in a] == [n.pitch for n in b]


class TestArpeggioPattern:
    def test_basic(self):
        a = arpeggio_pattern("C", "maj", pattern="123")
        assert len(a) == 3
        assert a[0].pitch == "C"

    def test_custom_pattern(self):
        a = arpeggio_pattern("C", "dom7", pattern="1234")
        assert len(a) == 4

    def test_unknown_raises(self):
        import pytest

        with pytest.raises(ValueError):
            arpeggio_pattern("C", "imaginary")
