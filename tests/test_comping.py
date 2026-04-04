"""Tests for v82.0 — comp_pattern."""

from code_music.theory import comp_pattern


class TestCompPattern:
    def test_rock_8ths(self):
        prog = [("A", "min")]
        notes = comp_pattern(prog, style="rock")
        assert len(notes) == 8  # 8 eighth notes per chord

    def test_swing_quarters(self):
        prog = [("C", "maj7")]
        notes = comp_pattern(prog, style="swing")
        assert len(notes) == 4

    def test_funk_16ths(self):
        prog = [("E", "min7")]
        notes = comp_pattern(prog, style="funk", seed=42)
        assert len(notes) == 16

    def test_bossa_syncopated(self):
        prog = [("D", "min7")]
        notes = comp_pattern(prog, style="bossa")
        assert len(notes) == 3  # three hits per chord

    def test_ballad_arpeggiated(self):
        prog = [("C", "maj")]
        notes = comp_pattern(prog, style="ballad")
        assert len(notes) == 3  # one per chord tone

    def test_multiple_chords(self):
        prog = [("C", "maj"), ("G", "dom7")]
        notes = comp_pattern(prog, style="rock")
        assert len(notes) == 16  # 8 per chord * 2

    def test_deterministic_funk(self):
        prog = [("E", "min7")]
        a = comp_pattern(prog, style="funk", seed=42)
        b = comp_pattern(prog, style="funk", seed=42)
        assert [n.pitch for n in a] == [n.pitch for n in b]
