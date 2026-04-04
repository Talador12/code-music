"""Tests for v80.0 — generate_progression, extend_progression."""

from code_music.theory import extend_progression, generate_progression


class TestGenerateProgression:
    def test_pop(self):
        prog = generate_progression(key="C", genre="pop", seed=42)
        assert len(prog) >= 4
        assert all(isinstance(r, str) and isinstance(s, str) for r, s in prog)

    def test_jazz(self):
        prog = generate_progression(key="Bb", genre="jazz", seed=42)
        assert len(prog) >= 4

    def test_blues_12_bars(self):
        prog = generate_progression(key="E", genre="blues", seed=42)
        assert len(prog) == 12

    def test_deterministic(self):
        a = generate_progression(key="C", genre="pop", seed=99)
        b = generate_progression(key="C", genre="pop", seed=99)
        assert a == b

    def test_different_keys(self):
        c = generate_progression(key="C", genre="pop", seed=42)
        g = generate_progression(key="G", genre="pop", seed=42)
        assert c != g  # different roots

    def test_custom_length(self):
        prog = generate_progression(key="C", length=8, genre="pop", seed=42)
        assert len(prog) == 8


class TestExtendProgression:
    def test_adds_bars(self):
        existing = [("C", "maj"), ("G", "dom7")]
        result = extend_progression(existing, bars=4, key="C", seed=42)
        assert len(result) == 6  # 2 + 4

    def test_preserves_original(self):
        existing = [("C", "maj")]
        result = extend_progression(existing, bars=2, key="C", seed=42)
        assert result[0] == ("C", "maj")

    def test_deterministic(self):
        existing = [("C", "maj")]
        a = extend_progression(existing, bars=4, seed=99)
        b = extend_progression(existing, bars=4, seed=99)
        assert a == b
