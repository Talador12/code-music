"""Tests for v141.0: theory course, time-stretch, pitch-shift, batch master."""

import io
import unittest
from contextlib import redirect_stdout, redirect_stderr

import numpy as np

from code_music import grade_lesson, theory_course
from code_music.effects import pitch_shift, time_stretch


# ---------------------------------------------------------------------------
# Theory Course
# ---------------------------------------------------------------------------


class TestTheoryCourse(unittest.TestCase):
    """Interactive theory course with 12 lessons."""

    def test_full_syllabus(self):
        syllabus = theory_course()
        assert isinstance(syllabus, list)
        assert len(syllabus) == 12

    def test_each_lesson_has_required_keys(self):
        for lesson in theory_course():
            for key in ["id", "title", "topic", "description", "concepts", "exercises"]:
                assert key in lesson, f"Lesson {lesson.get('id')} missing key: {key}"

    def test_get_lesson_by_id(self):
        lesson = theory_course(lesson_id=1)
        assert isinstance(lesson, dict)
        assert lesson["title"] == "Notes and Octaves"

    def test_get_lesson_by_id_last(self):
        lesson = theory_course(lesson_id=12)
        assert lesson["title"] == "Song Form"

    def test_invalid_lesson_id(self):
        result = theory_course(lesson_id=99)
        assert "error" in result

    def test_filter_by_topic_scales(self):
        lessons = theory_course(topic="scales")
        assert isinstance(lessons, list)
        assert all(l["topic"] == "scales" for l in lessons)
        assert len(lessons) >= 2

    def test_filter_by_topic_harmony(self):
        lessons = theory_course(topic="harmony")
        assert len(lessons) >= 2

    def test_filter_by_topic_none_found(self):
        lessons = theory_course(topic="nonexistent")
        assert lessons == []

    def test_exercises_have_answers(self):
        for lesson in theory_course():
            for ex in lesson["exercises"]:
                assert "answer" in ex, f"Exercise in lesson {lesson['id']} missing answer"

    def test_unique_lesson_ids(self):
        ids = [l["id"] for l in theory_course()]
        assert len(ids) == len(set(ids))


class TestGradeLesson(unittest.TestCase):
    """Grade answers for theory course lessons."""

    def test_perfect_score(self):
        result = grade_lesson(1, ["12", "G", "Db"])
        assert result["percentage"] == 100.0
        assert result["grade"] == "A"

    def test_zero_score(self):
        result = grade_lesson(1, ["wrong", "wrong", "wrong"])
        assert result["percentage"] == 0.0
        assert result["grade"] == "F"

    def test_partial_score(self):
        result = grade_lesson(1, ["12", "wrong", "wrong"])
        assert 0 < result["percentage"] < 100

    def test_case_insensitive(self):
        result = grade_lesson(1, ["12", "g", "db"])
        assert result["percentage"] == 100.0

    def test_feedback_present(self):
        result = grade_lesson(1, ["12", "G", "Db"])
        assert "feedback" in result
        assert len(result["feedback"]) == 3

    def test_feedback_marks_wrong(self):
        result = grade_lesson(1, ["12", "wrong", "Db"])
        wrong = [f for f in result["feedback"] if not f["correct"]]
        assert len(wrong) == 1

    def test_incomplete_answers(self):
        result = grade_lesson(1, ["12"])  # only 1 of 3 answers
        assert result["total"] == 3
        assert result["score"] == 1

    def test_invalid_lesson(self):
        result = grade_lesson(99, ["x"])
        assert "error" in result

    def test_all_lessons_gradeable(self):
        for lesson in theory_course():
            answers = [ex["answer"] for ex in lesson["exercises"]]
            result = grade_lesson(lesson["id"], answers)
            assert result["percentage"] == 100.0, f"Lesson {lesson['id']} self-grading failed"

    def test_imports_from_theory(self):
        from code_music.theory import grade_lesson as gl, theory_course as tc

        assert callable(gl)
        assert callable(tc)


# ---------------------------------------------------------------------------
# Time-stretch
# ---------------------------------------------------------------------------


class TestTimeStretch(unittest.TestCase):
    """Grain-based time-stretching without pitch change."""

    def test_identity(self):
        audio = np.random.randn(44100, 2) * 0.1
        result = time_stretch(audio, 44100, rate=1.0)
        np.testing.assert_array_equal(result, audio)

    def test_slow_down(self):
        audio = np.random.randn(22050, 2) * 0.1
        result = time_stretch(audio, 22050, rate=0.5)
        assert result.shape[0] > audio.shape[0]

    def test_speed_up(self):
        audio = np.random.randn(22050, 2) * 0.1
        result = time_stretch(audio, 22050, rate=2.0)
        assert result.shape[0] < audio.shape[0]

    def test_mono(self):
        audio = np.random.randn(22050) * 0.1
        result = time_stretch(audio, 22050, rate=0.75)
        assert result.ndim == 1
        assert result.shape[0] > audio.shape[0]

    def test_stereo_shape(self):
        audio = np.random.randn(22050, 2) * 0.1
        result = time_stretch(audio, 22050, rate=0.5)
        assert result.ndim == 2
        assert result.shape[1] == 2

    def test_invalid_rate(self):
        audio = np.random.randn(1000, 2)
        with self.assertRaises(ValueError):
            time_stretch(audio, 44100, rate=0)

    def test_approximate_ratio(self):
        n = 44100
        audio = np.random.randn(n, 2) * 0.1
        result = time_stretch(audio, 44100, rate=0.5)
        # Should be roughly 2x longer (within 20% tolerance for grain artifacts)
        assert result.shape[0] > n * 1.5


# ---------------------------------------------------------------------------
# Pitch-shift
# ---------------------------------------------------------------------------


class TestPitchShift(unittest.TestCase):
    """Pitch-shift via time-stretch + resample."""

    def test_identity(self):
        audio = np.random.randn(22050, 2) * 0.1
        result = pitch_shift(audio, 22050, semitones=0)
        np.testing.assert_array_equal(result, audio)

    def test_shift_up_preserves_length(self):
        audio = np.random.randn(22050, 2) * 0.1
        result = pitch_shift(audio, 22050, semitones=7)
        assert abs(result.shape[0] - audio.shape[0]) < 100

    def test_shift_down_preserves_length(self):
        audio = np.random.randn(22050, 2) * 0.1
        result = pitch_shift(audio, 22050, semitones=-5)
        assert result.shape[0] == audio.shape[0]

    def test_mono(self):
        audio = np.random.randn(22050) * 0.1
        result = pitch_shift(audio, 22050, semitones=3)
        assert result.ndim == 1

    def test_stereo_shape(self):
        audio = np.random.randn(22050, 2) * 0.1
        result = pitch_shift(audio, 22050, semitones=12)
        assert result.ndim == 2
        assert result.shape[1] == 2

    def test_octave_up(self):
        audio = np.random.randn(22050, 2) * 0.1
        result = pitch_shift(audio, 22050, semitones=12)
        assert result.shape[0] == audio.shape[0]


# ---------------------------------------------------------------------------
# Batch mastering Makefile target
# ---------------------------------------------------------------------------


class TestMakefileMaster(unittest.TestCase):
    """Makefile has a master target."""

    def test_master_target_exists(self):
        from pathlib import Path

        makefile = Path(__file__).parent.parent / "Makefile"
        content = makefile.read_text()
        assert "master:" in content
        assert "mastered" in content


if __name__ == "__main__":
    unittest.main()
