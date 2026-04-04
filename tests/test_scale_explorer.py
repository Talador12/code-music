"""Tests for v94.0 — suggest_scale, available_notes, avoid_notes."""

from code_music.theory import available_notes, avoid_notes, suggest_scale


class TestSuggestScale:
    def test_returns_ranked_list(self):
        result = suggest_scale(["C", "E", "G"], key="C")
        assert len(result) > 0
        assert all(isinstance(r, tuple) and len(r) == 2 for r in result)

    def test_major_triad_finds_major(self):
        result = suggest_scale(["C", "E", "G"], key="C")
        names = [r[0] for r in result[:5]]
        assert "major" in names

    def test_sorted_by_score(self):
        result = suggest_scale(["C", "Eb", "G"], key="C")
        scores = [r[1] for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_empty_notes(self):
        result = suggest_scale([], key="C")
        assert len(result) > 0


class TestAvailableNotes:
    def test_c_major(self):
        notes = available_notes("C", "major")
        assert "C" in notes
        assert "D" in notes
        assert len(notes) == 7

    def test_pentatonic(self):
        notes = available_notes("C", "pentatonic")
        assert len(notes) == 5

    def test_unknown_scale(self):
        assert available_notes("C", "nonexistent") == []


class TestAvoidNotes:
    def test_c_major(self):
        avoid = avoid_notes("C", "major")
        assert len(avoid) == 5  # 12 - 7 = 5 notes to avoid
        assert "C" not in avoid

    def test_complement(self):
        good = set(available_notes("G", "major"))
        bad = set(avoid_notes("G", "major"))
        assert len(good & bad) == 0  # no overlap
        assert len(good | bad) == 12  # covers all 12
