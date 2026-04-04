"""Tests for v95.0 — lookup_voicing, random_voicing."""

from code_music.theory import lookup_voicing, random_voicing


class TestLookupVoicing:
    def test_root_position(self):
        notes = lookup_voicing("C", "maj", position=0)
        assert len(notes) >= 3

    def test_first_inversion(self):
        notes = lookup_voicing("C", "maj", position=1)
        assert len(notes) >= 3

    def test_dom7(self):
        notes = lookup_voicing("G", "dom7", position=0)
        assert len(notes) >= 3

    def test_custom_duration(self):
        notes = lookup_voicing("C", "maj", duration=2.0)
        assert all(n.duration == 2.0 for n in notes)

    def test_wraps_position(self):
        # Position beyond available voicings wraps around
        notes = lookup_voicing("C", "maj", position=100)
        assert len(notes) >= 3


class TestRandomVoicing:
    def test_returns_notes(self):
        notes = random_voicing("C", "maj", seed=42)
        assert len(notes) >= 3

    def test_deterministic(self):
        a = random_voicing("D", "min7", seed=99)
        b = random_voicing("D", "min7", seed=99)
        assert [n.pitch for n in a] == [n.pitch for n in b]

    def test_different_seeds(self):
        # With enough tries, different seeds should sometimes give different voicings
        results = set()
        for s in range(20):
            notes = random_voicing("C", "dom7", seed=s)
            results.add(tuple(n.pitch for n in notes))
        assert len(results) > 1  # at least some variety
