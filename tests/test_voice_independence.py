"""Tests for v89.0 — similar_motion_ratio, contrary_motion_ratio, voice_independence_score."""

from code_music.engine import Note
from code_music.theory import contrary_motion_ratio, similar_motion_ratio, voice_independence_score


class TestSimilarMotionRatio:
    def test_parallel_motion(self):
        a = [Note("C", 4, 1.0), Note("D", 4, 1.0), Note("E", 4, 1.0)]
        b = [Note("E", 4, 1.0), Note("F", 4, 1.0), Note("G", 4, 1.0)]
        ratio = similar_motion_ratio(a, b)
        assert ratio == 1.0  # both ascending = all similar

    def test_contrary(self):
        a = [Note("C", 4, 1.0), Note("D", 4, 1.0)]
        b = [Note("G", 4, 1.0), Note("F", 4, 1.0)]
        ratio = similar_motion_ratio(a, b)
        assert ratio == 0.0  # one up, one down = no similar

    def test_range(self):
        a = [Note("C", 4, 1.0)] * 5
        b = [Note("E", 4, 1.0)] * 5
        ratio = similar_motion_ratio(a, b)
        assert 0.0 <= ratio <= 1.0


class TestContraryMotionRatio:
    def test_contrary(self):
        a = [Note("C", 4, 1.0), Note("D", 4, 1.0)]
        b = [Note("G", 4, 1.0), Note("F", 4, 1.0)]
        ratio = contrary_motion_ratio(a, b)
        assert ratio == 1.0

    def test_parallel(self):
        a = [Note("C", 4, 1.0), Note("D", 4, 1.0)]
        b = [Note("E", 4, 1.0), Note("F", 4, 1.0)]
        ratio = contrary_motion_ratio(a, b)
        assert ratio == 0.0


class TestVoiceIndependenceScore:
    def test_single_voice(self):
        assert voice_independence_score([[Note("C", 4, 1.0)]]) == 100

    def test_parallel_low(self):
        a = [Note("C", 4, 1.0), Note("D", 4, 1.0), Note("E", 4, 1.0)]
        b = [Note("E", 4, 1.0), Note("F", 4, 1.0), Note("G", 4, 1.0)]
        score = voice_independence_score([a, b])
        assert score < 50  # parallel = low independence

    def test_range(self):
        a = [Note("C", 4, 1.0), Note("E", 4, 1.0)]
        b = [Note("G", 4, 1.0), Note("C", 4, 1.0)]
        score = voice_independence_score([a, b])
        assert 0 <= score <= 100
