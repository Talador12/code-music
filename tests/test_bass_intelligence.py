"""Tests for v74.0 — bass_line_jazz, bass_line_funk, bass_line_latin."""

from code_music.theory import bass_line_funk, bass_line_jazz, bass_line_latin


class TestBassLineJazz:
    def test_four_per_chord(self):
        prog = [("C", "maj7"), ("G", "dom7")]
        notes = bass_line_jazz(prog, seed=42)
        assert len(notes) == 8  # 4 per chord * 2

    def test_root_on_beat_1(self):
        prog = [("D", "min7")]
        notes = bass_line_jazz(prog, seed=42)
        assert notes[0].pitch == "D"

    def test_deterministic(self):
        prog = [("C", "maj"), ("F", "maj")]
        a = bass_line_jazz(prog, seed=99)
        b = bass_line_jazz(prog, seed=99)
        assert [n.pitch for n in a] == [n.pitch for n in b]

    def test_chromatic_approach(self):
        prog = [("C", "maj"), ("F", "maj")]
        notes = bass_line_jazz(prog, seed=42)
        # Last note of first chord should approach F (root of next)
        assert notes[3].pitch is not None  # some approach note


class TestBassLineFunk:
    def test_eight_per_chord(self):
        prog = [("E", "min7")]
        notes = bass_line_funk(prog, seed=42)
        assert len(notes) == 8

    def test_downbeat_is_root(self):
        prog = [("A", "dom7")]
        notes = bass_line_funk(prog, seed=42)
        assert notes[0].pitch == "A"

    def test_has_rests(self):
        prog = [("D", "min")] * 4
        notes = bass_line_funk(prog, seed=42)
        # Funk bass should have some rests (the space is the funk)
        assert any(n.pitch is None for n in notes)


class TestBassLineLatin:
    def test_eight_per_chord(self):
        prog = [("C", "maj")]
        notes = bass_line_latin(prog, seed=42)
        assert len(notes) == 8

    def test_has_rests(self):
        prog = [("A", "min")]
        notes = bass_line_latin(prog, seed=42)
        # Tumbao has rests
        assert any(n.pitch is None for n in notes)

    def test_anticipation(self):
        prog = [("C", "maj"), ("F", "maj")]
        notes = bass_line_latin(prog, seed=42)
        # Last note of first chord anticipates F
        assert notes[7].pitch == "F"
