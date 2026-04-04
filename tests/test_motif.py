"""Tests for v54.0 — augment, diminish, fragment, motif_similarity."""

from code_music.engine import Note
from code_music.theory import augment, diminish, fragment, motif_similarity


class TestAugment:
    def test_doubles_duration(self):
        motif = [Note("C", 5, 1.0), Note("E", 5, 0.5)]
        result = augment(motif)
        assert result[0].duration == 2.0
        assert result[1].duration == 1.0

    def test_custom_factor(self):
        motif = [Note("C", 5, 1.0)]
        result = augment(motif, factor=3.0)
        assert result[0].duration == 3.0

    def test_preserves_pitch(self):
        motif = [Note("D", 4, 1.0)]
        result = augment(motif)
        assert result[0].pitch == "D"
        assert result[0].octave == 4

    def test_rest_passthrough(self):
        motif = [Note.rest(1.0)]
        result = augment(motif)
        assert result[0].pitch is None
        assert result[0].duration == 2.0


class TestDiminish:
    def test_halves_duration(self):
        motif = [Note("C", 5, 2.0)]
        result = diminish(motif)
        assert result[0].duration == 1.0

    def test_custom_factor(self):
        motif = [Note("C", 5, 4.0)]
        result = diminish(motif, factor=4.0)
        assert result[0].duration == 1.0

    def test_preserves_pitch(self):
        motif = [Note("G", 5, 2.0)]
        result = diminish(motif)
        assert result[0].pitch == "G"


class TestFragment:
    def test_extracts_first_n(self):
        motif = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]
        result = fragment(motif, 2)
        assert len(result) == 2
        assert result[0].pitch == "C"
        assert result[1].pitch == "E"

    def test_length_exceeds_motif(self):
        motif = [Note("C", 5, 1.0)]
        result = fragment(motif, 5)
        assert len(result) == 1

    def test_zero_length(self):
        motif = [Note("C", 5, 1.0)]
        result = fragment(motif, 0)
        assert len(result) == 0


class TestMotifSimilarity:
    def test_identical_motifs(self):
        m = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]
        assert motif_similarity(m, m) == 1.0

    def test_completely_different(self):
        a = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        b = [Note("G", 3, 0.25), Note("C", 3, 0.25)]
        score = motif_similarity(a, b)
        assert 0.0 <= score < 1.0

    def test_empty_motif(self):
        assert motif_similarity([], [Note("C", 5, 1.0)]) == 0.0

    def test_range(self):
        a = [Note("C", 5, 1.0), Note("D", 5, 1.0)]
        b = [Note("E", 4, 0.5), Note("F", 4, 0.5)]
        score = motif_similarity(a, b)
        assert 0.0 <= score <= 1.0

    def test_similar_contour(self):
        # Both ascending — should be reasonably similar
        a = [Note("C", 5, 1.0), Note("D", 5, 1.0), Note("E", 5, 1.0)]
        b = [Note("G", 4, 1.0), Note("A", 4, 1.0), Note("B", 4, 1.0)]
        score = motif_similarity(a, b)
        assert score > 0.7
