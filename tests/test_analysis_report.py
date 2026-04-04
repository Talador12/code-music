"""Tests for v93.0 — analysis_report."""

from code_music.theory import analysis_report


class TestAnalysisReport:
    def test_returns_string(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]
        report = analysis_report(prog, key="C")
        assert isinstance(report, str)

    def test_contains_title(self):
        report = analysis_report([("C", "maj")], title="Test Song")
        assert "Test Song" in report

    def test_contains_key(self):
        report = analysis_report([("C", "maj")], key="G")
        assert "G major" in report

    def test_contains_form(self):
        prog = [("C", "maj")] * 8
        report = analysis_report(prog, key="C")
        assert "Form:" in report

    def test_contains_complexity(self):
        prog = [("C", "maj"), ("G", "dom7")]
        report = analysis_report(prog)
        assert "Complexity:" in report

    def test_contains_tension(self):
        prog = [("C", "maj"), ("G", "dom7")]
        report = analysis_report(prog)
        assert "Tension" in report

    def test_contains_cadences(self):
        prog = [("G", "dom7"), ("C", "maj")]
        report = analysis_report(prog, key="C")
        assert "authentic" in report

    def test_empty_progression(self):
        report = analysis_report([])
        assert "0 chords" in report
