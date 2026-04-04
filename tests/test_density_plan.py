"""Tests for v91.0 — density_plan, orchestration_curve."""

from code_music.theory import density_plan, orchestration_curve


class TestDensityPlan:
    def test_build_pattern(self):
        plan = density_plan(["intro", "verse", "chorus"], ["bass", "drums", "lead"], "build")
        assert plan[0]["count"] <= plan[-1]["count"]  # builds up

    def test_strip_pattern(self):
        plan = density_plan(["chorus", "verse", "outro"], ["bass", "drums", "lead"], "strip")
        assert plan[0]["count"] >= plan[-1]["count"]  # strips down

    def test_full_pattern(self):
        plan = density_plan(["intro", "chorus"], ["a", "b", "c"], "full")
        assert all(p["count"] == 3 for p in plan)

    def test_correct_sections(self):
        plan = density_plan(["A", "B"], ["bass", "lead"])
        assert plan[0]["section"] == "A"
        assert plan[1]["section"] == "B"

    def test_min_one_instrument(self):
        plan = density_plan(["intro"] * 5, ["bass", "drums", "lead"], "strip")
        assert all(p["count"] >= 1 for p in plan)


class TestOrchestrationCurve:
    def test_returns_counts(self):
        plan = density_plan(["A", "B", "C"], ["bass", "drums", "lead"], "build")
        curve = orchestration_curve(plan)
        assert len(curve) == 3
        assert all(isinstance(c, int) for c in curve)
