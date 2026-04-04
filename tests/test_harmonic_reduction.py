"""Tests for v68.0 — reduce_to_chords, harmonic_skeleton, complexity_score."""

from code_music.engine import Note
from code_music.theory import complexity_score, harmonic_skeleton, reduce_to_chords


class TestReduceToChords:
    def test_c_major_arpeggio(self):
        notes = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0), Note("C", 6, 1.0)]
        chords = reduce_to_chords(notes, beats_per_chord=4)
        assert len(chords) == 1
        assert chords[0] == ("C", "maj")

    def test_multiple_groups(self):
        notes = [Note("C", 5, 1.0)] * 4 + [Note("F", 5, 1.0)] * 4
        chords = reduce_to_chords(notes, beats_per_chord=4)
        assert len(chords) == 2

    def test_rests_handled(self):
        notes = [Note.rest(1.0)] * 4
        chords = reduce_to_chords(notes, beats_per_chord=4)
        assert len(chords) == 1  # fallback to C maj


class TestHarmonicSkeleton:
    def test_i_iv_v_i(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]
        skel = harmonic_skeleton(prog, key="C")
        roots = [r for r, _ in skel]
        assert roots == ["C", "F", "G", "C"]

    def test_secondary_dom_becomes_tonic_or_dom(self):
        prog = [("C", "maj"), ("A", "dom7"), ("D", "min"), ("G", "dom7")]
        skel = harmonic_skeleton(prog, key="C")
        assert len(skel) == 4
        # A is degree 9 → tonic group; D is degree 2 → subdominant
        assert skel[2][0] == "F"  # subdominant


class TestComplexityScore:
    def test_simple_low(self):
        prog = [("C", "maj"), ("G", "maj"), ("C", "maj")]
        score = complexity_score(prog, key="C")
        assert score < 50

    def test_coltrane_high(self):
        prog = [
            ("C", "maj7"),
            ("Eb", "dom7"),
            ("Ab", "maj7"),
            ("B", "dom7"),
            ("E", "maj7"),
            ("G", "dom7"),
        ]
        score = complexity_score(prog, key="C")
        assert score > 50

    def test_empty(self):
        assert complexity_score([], key="C") == 0

    def test_range(self):
        prog = [("C", "maj")] * 20
        score = complexity_score(prog, key="C")
        assert 0 <= score <= 100
