"""Tests for v90.0 — quiz_intervals, quiz_chords, grade_quiz."""

from code_music.theory import grade_quiz, quiz_chords, quiz_intervals


class TestQuizIntervals:
    def test_correct_count(self):
        qs = quiz_intervals(count=5, seed=42)
        assert len(qs) == 5

    def test_structure(self):
        qs = quiz_intervals(count=1, seed=42)
        assert "note_a" in qs[0]
        assert "note_b" in qs[0]
        assert "answer" in qs[0]

    def test_deterministic(self):
        a = quiz_intervals(count=5, seed=99)
        b = quiz_intervals(count=5, seed=99)
        assert [q["answer"] for q in a] == [q["answer"] for q in b]


class TestQuizChords:
    def test_correct_count(self):
        qs = quiz_chords(count=5, seed=42)
        assert len(qs) == 5

    def test_structure(self):
        qs = quiz_chords(count=1, seed=42)
        assert "notes" in qs[0]
        assert "answer_root" in qs[0]
        assert "answer_shape" in qs[0]

    def test_deterministic(self):
        a = quiz_chords(count=5, seed=99)
        b = quiz_chords(count=5, seed=99)
        assert [q["answer_shape"] for q in a] == [q["answer_shape"] for q in b]


class TestGradeQuiz:
    def test_perfect(self):
        result = grade_quiz(["P5", "M3"], ["P5", "M3"])
        assert result["score"] == 2
        assert result["percentage"] == 100.0

    def test_partial(self):
        result = grade_quiz(["P5", "m3"], ["P5", "M3"])
        assert result["score"] == 1
        assert result["wrong_indices"] == [1]

    def test_empty(self):
        result = grade_quiz([], [])
        assert result["score"] == 0
        assert result["percentage"] == 0.0
