"""Tests for v62.0 — validate_counterpoint, grade_counterpoint."""

from code_music.engine import Note
from code_music.theory import grade_counterpoint, validate_counterpoint


class TestValidateCounterpoint:
    def test_perfect_counterpoint(self):
        cf = [Note("C", 4, 4.0), Note("E", 4, 4.0)]
        cp = [Note("G", 5, 4.0), Note("C", 5, 4.0)]  # P5, then m6 — both consonant
        violations = validate_counterpoint(cf, cp)
        # Filter out parallel checks — just checking consonance
        dissonant = [v for v in violations if "dissonant" in v]
        assert len(dissonant) == 0

    def test_dissonance_detected(self):
        cf = [Note("C", 4, 4.0)]
        cp = [Note("C#", 5, 4.0)]  # minor 2nd = dissonant
        violations = validate_counterpoint(cf, cp)
        assert any("dissonant" in v for v in violations)

    def test_voice_crossing(self):
        cf = [Note("G", 5, 4.0)]
        cp = [Note("C", 4, 4.0)]  # CP below CF
        violations = validate_counterpoint(cf, cp)
        assert any("voice crossing" in v for v in violations)

    def test_large_leap(self):
        cp = [Note("C", 4, 4.0), Note("C", 6, 4.0)]  # 2-octave leap
        cf = [Note("C", 3, 4.0), Note("C", 3, 4.0)]
        violations = validate_counterpoint(cf, cp)
        assert any("leap > octave" in v for v in violations)

    def test_rest_passthrough(self):
        cf = [Note.rest(4.0)]
        cp = [Note.rest(4.0)]
        violations = validate_counterpoint(cf, cp)
        assert len(violations) == 0


class TestGradeCounterpoint:
    def test_perfect_score(self):
        cf = [Note("C", 4, 4.0)]
        cp = [Note("G", 5, 4.0)]  # P5, consonant, no crossing
        score = grade_counterpoint(cf, cp)
        assert score == 100

    def test_deductions(self):
        cf = [Note("C", 4, 4.0)]
        cp = [Note("C#", 5, 4.0)]  # dissonant
        score = grade_counterpoint(cf, cp)
        assert score < 100

    def test_floor_at_zero(self):
        # Many violations
        cf = [Note("C", 4, 4.0)] * 20
        cp = [Note("C#", 3, 4.0)] * 20  # crossing + dissonant every bar
        score = grade_counterpoint(cf, cp)
        assert score >= 0
