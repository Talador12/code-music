"""Tests for v96.0 — memory_game, verify_playback."""

from code_music.engine import Note
from code_music.theory import memory_game, verify_playback


class TestMemoryGame:
    def test_correct_rounds(self):
        rounds = memory_game(length=5, seed=42)
        assert len(rounds) == 5

    def test_growing_length(self):
        rounds = memory_game(length=4, seed=42)
        for i, r in enumerate(rounds):
            assert len(r) == i + 1

    def test_deterministic(self):
        a = memory_game(length=4, seed=99)
        b = memory_game(length=4, seed=99)
        for ra, rb in zip(a, b):
            assert [n.pitch for n in ra] == [n.pitch for n in rb]

    def test_notes_from_scale(self):
        rounds = memory_game(length=3, key="C", scale_name="major", seed=42)
        c_major = {"C", "D", "E", "F", "G", "A", "B"}
        for r in rounds:
            for n in r:
                assert n.pitch in c_major


class TestVerifyPlayback:
    def test_perfect(self):
        original = [Note("C", 5, 0.5), Note("E", 5, 0.5)]
        attempt = [Note("C", 5, 0.5), Note("E", 5, 0.5)]
        result = verify_playback(original, attempt)
        assert result["accuracy"] == 100.0

    def test_all_wrong(self):
        original = [Note("C", 5, 0.5), Note("E", 5, 0.5)]
        attempt = [Note("G", 5, 0.5), Note("A", 5, 0.5)]
        result = verify_playback(original, attempt)
        assert result["correct"] == 0

    def test_partial(self):
        original = [Note("C", 5, 0.5), Note("E", 5, 0.5), Note("G", 5, 0.5)]
        attempt = [Note("C", 5, 0.5), Note("D", 5, 0.5), Note("G", 5, 0.5)]
        result = verify_playback(original, attempt)
        assert result["correct"] == 2
        assert result["wrong_positions"] == [1]

    def test_short_attempt(self):
        original = [Note("C", 5, 0.5)] * 4
        attempt = [Note("C", 5, 0.5)] * 2
        result = verify_playback(original, attempt)
        assert result["correct"] == 2
        assert len(result["wrong_positions"]) == 2  # missing positions
