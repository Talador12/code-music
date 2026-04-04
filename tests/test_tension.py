"""Tests for v52.0 — tension_curve, tension_at."""

from code_music.theory import tension_at, tension_curve


class TestTensionCurve:
    def test_correct_length(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]
        curve = tension_curve(prog, key="C")
        assert len(curve) == 4

    def test_tonic_lowest(self):
        prog = [("C", "maj"), ("G", "dom7")]
        curve = tension_curve(prog, key="C")
        assert curve[0] < curve[1]  # tonic < dominant

    def test_dominant_higher(self):
        prog = [("C", "maj"), ("G", "dom7"), ("C", "maj")]
        curve = tension_curve(prog, key="C")
        assert curve[1] > curve[0]  # V is more tense than I

    def test_range_0_to_1(self):
        prog = [("C", "maj"), ("F#", "dim7"), ("G", "dom7"), ("C", "maj")]
        curve = tension_curve(prog, key="C")
        for val in curve:
            assert 0.0 <= val <= 1.0

    def test_chromatic_chord_high(self):
        prog = [("C", "maj"), ("Eb", "maj")]
        curve = tension_curve(prog, key="C")
        assert curve[1] > curve[0]  # chromatic = high tension

    def test_empty_progression(self):
        assert tension_curve([], key="C") == []


class TestTensionAt:
    def test_valid_index(self):
        prog = [("C", "maj"), ("G", "dom7")]
        assert tension_at(prog, 0, key="C") >= 0.0

    def test_out_of_bounds(self):
        prog = [("C", "maj")]
        assert tension_at(prog, 5, key="C") == 0.0

    def test_matches_curve(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7")]
        curve = tension_curve(prog, key="C")
        for i, val in enumerate(curve):
            assert tension_at(prog, i, key="C") == val
