"""Tests for v102.0 — note_probability, next_note_distribution."""

from code_music.engine import Note
from code_music.theory import next_note_distribution, note_probability


class TestNoteProbability:
    def test_basic(self):
        notes = [Note("C", 5, 1.0), Note("C", 5, 1.0), Note("E", 5, 1.0)]
        prob = note_probability(notes)
        assert prob["C"] > prob["E"]
        assert abs(prob["C"] - 0.6667) < 0.01

    def test_empty(self):
        assert note_probability([]) == {}

    def test_rests_excluded(self):
        notes = [Note("C", 5, 1.0), Note.rest(1.0)]
        prob = note_probability(notes)
        assert len(prob) == 1

    def test_sums_to_1(self):
        notes = [Note("C", 5, 1.0), Note("D", 5, 1.0), Note("E", 5, 1.0)]
        prob = note_probability(notes)
        assert abs(sum(prob.values()) - 1.0) < 0.01


class TestNextNoteDistribution:
    def test_basic(self):
        notes = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("C", 5, 1.0), Note("G", 5, 1.0)]
        dist = next_note_distribution(notes, "C")
        assert "E" in dist or "G" in dist

    def test_unknown_note(self):
        notes = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        dist = next_note_distribution(notes, "G")
        assert dist == {}

    def test_sums_to_1(self):
        notes = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("C", 5, 1.0), Note("G", 5, 1.0)]
        dist = next_note_distribution(notes, "C")
        if dist:
            assert abs(sum(dist.values()) - 1.0) < 0.01
