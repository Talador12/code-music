"""Tests for v92.0 — build_transition_matrix, most_likely_next, generate_from_matrix."""

from code_music.theory import build_transition_matrix, generate_from_matrix, most_likely_next


class TestBuildTransitionMatrix:
    def test_basic(self):
        progs = [[("C", "maj"), ("G", "dom7"), ("C", "maj")]]
        matrix = build_transition_matrix(progs)
        assert ("C", "maj") in matrix
        assert ("G", "dom7") in matrix[("C", "maj")]

    def test_probabilities_sum_to_1(self):
        progs = [[("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]]
        matrix = build_transition_matrix(progs)
        for transitions in matrix.values():
            total = sum(transitions.values())
            assert abs(total - 1.0) < 0.01

    def test_empty(self):
        assert build_transition_matrix([]) == {}

    def test_multiple_progs(self):
        progs = [
            [("C", "maj"), ("G", "dom7")],
            [("C", "maj"), ("F", "maj")],
        ]
        matrix = build_transition_matrix(progs)
        # C should lead to both G and F
        assert len(matrix[("C", "maj")]) == 2


class TestMostLikelyNext:
    def test_basic(self):
        progs = [[("C", "maj"), ("G", "dom7")] * 5]
        matrix = build_transition_matrix(progs)
        nxt = most_likely_next(("C", "maj"), matrix)
        assert nxt == ("G", "dom7")

    def test_missing(self):
        assert most_likely_next(("X", "y"), {}) is None


class TestGenerateFromMatrix:
    def test_correct_length(self):
        progs = [[("C", "maj"), ("G", "dom7"), ("C", "maj")]]
        matrix = build_transition_matrix(progs)
        result = generate_from_matrix(matrix, length=8, seed=42)
        assert len(result) == 8

    def test_deterministic(self):
        progs = [[("C", "maj"), ("G", "dom7")] * 5]
        matrix = build_transition_matrix(progs)
        a = generate_from_matrix(matrix, length=8, seed=99)
        b = generate_from_matrix(matrix, length=8, seed=99)
        assert a == b

    def test_empty_matrix(self):
        assert generate_from_matrix({}, length=4) == []
