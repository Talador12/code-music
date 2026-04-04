"""Tests for v115.0 — progression_similarity, find_similar_progressions."""

from code_music.theory import find_similar_progressions, progression_similarity


class TestProgressionSimilarity:
    def test_identical(self):
        prog = [("C", "maj"), ("G", "dom7")]
        assert progression_similarity(prog, prog) == 1.0

    def test_different(self):
        a = [("C", "maj")]
        b = [("F#", "dim")]
        score = progression_similarity(a, b)
        assert score < 1.0

    def test_empty(self):
        assert progression_similarity([], [("C", "maj")]) == 0.0

    def test_range(self):
        a = [("C", "maj"), ("G", "dom7")]
        b = [("D", "min"), ("A", "dom7")]
        score = progression_similarity(a, b)
        assert 0.0 <= score <= 1.0


class TestFindSimilarProgressions:
    def test_finds_exact(self):
        target = [("C", "maj"), ("G", "dom7")]
        corpus = [
            [("A", "min"), ("E", "dom7")],
            [("C", "maj"), ("G", "dom7")],  # exact match
            [("F#", "dim"), ("Bb", "aug")],
        ]
        results = find_similar_progressions(target, corpus, top_n=1)
        assert results[0][0] == 1  # index of exact match

    def test_top_n(self):
        target = [("C", "maj")]
        corpus = [[("C", "maj")]] * 10
        results = find_similar_progressions(target, corpus, top_n=3)
        assert len(results) == 3

    def test_sorted_by_score(self):
        target = [("C", "maj"), ("G", "dom7")]
        corpus = [
            [("C", "maj"), ("G", "dom7")],
            [("F#", "dim"), ("Bb", "aug")],
        ]
        results = find_similar_progressions(target, corpus)
        assert results[0][1] >= results[1][1]
