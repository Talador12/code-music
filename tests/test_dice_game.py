"""Tests for v69.0 — dice_game, classical_minuet."""

from code_music.theory import classical_minuet, dice_game


class TestDiceGame:
    def test_16_bars(self):
        indices = dice_game(seed=42)
        assert len(indices) == 16

    def test_deterministic(self):
        assert dice_game(seed=99) == dice_game(seed=99)

    def test_different_seeds(self):
        assert dice_game(seed=1) != dice_game(seed=2)

    def test_values_from_table(self):
        indices = dice_game(seed=42)
        for idx in indices:
            assert isinstance(idx, int)
            assert 1 <= idx <= 176  # Mozart's table range

    def test_custom_bars(self):
        indices = dice_game(seed=42, bars=8)
        assert len(indices) == 8


class TestClassicalMinuet:
    def test_returns_notes(self):
        notes = classical_minuet(seed=42)
        assert len(notes) > 0

    def test_48_notes(self):
        # 16 bars * 3 notes per bar (3/4 time)
        notes = classical_minuet(seed=42)
        assert len(notes) == 48

    def test_deterministic(self):
        a = classical_minuet(seed=99)
        b = classical_minuet(seed=99)
        assert [n.pitch for n in a] == [n.pitch for n in b]

    def test_different_keys(self):
        c = classical_minuet(key="C", seed=42)
        g = classical_minuet(key="G", seed=42)
        c_pitches = [n.pitch for n in c]
        g_pitches = [n.pitch for n in g]
        assert c_pitches != g_pitches

    def test_3_4_time(self):
        notes = classical_minuet(seed=42)
        # All notes should have duration 1.0 (one beat in 3/4)
        assert all(n.duration == 1.0 for n in notes)
