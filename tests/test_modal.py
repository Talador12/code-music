"""Tests for lydian_run, mixolydian_lick, modal_interchange."""

from code_music.theory import lydian_run, mixolydian_lick, modal_interchange


class TestLydianRun:
    def test_basic(self):
        r = lydian_run("C", length=7)
        assert len(r) == 7
        assert r[0].pitch == "C"

    def test_sharp_four(self):
        r = lydian_run("C", length=4)
        assert r[3].pitch == "F#"  # #4


class TestMixolydianLick:
    def test_basic(self):
        lick = mixolydian_lick("G", seed=42)
        assert len(lick) >= 6
        assert lick[-1].pitch == "G"

    def test_reproducible(self):
        a = mixolydian_lick("C", seed=42)
        b = mixolydian_lick("C", seed=42)
        assert [n.pitch for n in a] == [n.pitch for n in b]


class TestModalInterchange:
    def test_basic(self):
        prog = [("C", "maj"), ("G", "maj"), ("A", "maj")]
        borrowed = modal_interchange(prog, key="C")
        assert isinstance(borrowed, list)
        assert len(borrowed) == 3

    def test_borrows_minor(self):
        prog = [("C", "maj"), ("Ab", "maj")]
        borrowed = modal_interchange(prog, key="C", target_mode="minor")
        # Ab in C minor should stay as-is or get minor shape
        assert len(borrowed) == 2
