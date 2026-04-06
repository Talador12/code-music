"""Tests for generate_phrase() — cadential phrase generator."""

from code_music.theory import generate_phrase


class TestGeneratePhrase:
    """Phrase generator produces cadence-targeted progressions."""

    def test_perfect_cadence(self):
        p = generate_phrase("C", cadence="perfect", length=4, seed=42)
        assert p["cadence_type"] == "perfect"
        assert len(p["progression"]) == 4
        # Last chord should be tonic
        assert p["progression"][-1][0] == "C"

    def test_half_cadence(self):
        p = generate_phrase("C", cadence="half", length=4, seed=42)
        assert p["cadence_type"] == "half"
        # Last chord should be dominant (G)
        assert p["progression"][-1][0] == "G"

    def test_deceptive_cadence(self):
        p = generate_phrase("C", cadence="deceptive", length=4, seed=42)
        assert p["cadence_type"] == "deceptive"
        # Last chord should be vi (A min)
        assert p["progression"][-1][0] == "A"

    def test_plagal_cadence(self):
        p = generate_phrase("C", cadence="plagal", length=4, seed=42)
        assert p["cadence_type"] == "plagal"
        # Last chord should be tonic
        assert p["progression"][-1][0] == "C"

    def test_tension_curve_present(self):
        p = generate_phrase("C", cadence="perfect", length=4, seed=42)
        assert "tension_curve" in p
        assert len(p["tension_curve"]) == 4
        for t in p["tension_curve"]:
            assert 0.0 <= t <= 1.0

    def test_longer_phrase(self):
        p = generate_phrase("C", cadence="perfect", length=8, seed=42)
        assert len(p["progression"]) == 8

    def test_short_phrase(self):
        p = generate_phrase("C", cadence="perfect", length=2, seed=42)
        assert len(p["progression"]) == 2

    def test_different_key(self):
        p = generate_phrase("G", cadence="perfect", length=4, seed=42)
        assert p["progression"][-1][0] == "G"  # tonic in G

    def test_include_melody(self):
        p = generate_phrase("C", cadence="perfect", length=4, include_melody=True, seed=42)
        assert "melody" in p
        assert len(p["melody"]) == 16  # 4 chords × 4 notes each

    def test_no_melody_by_default(self):
        p = generate_phrase("C", cadence="perfect", length=4, seed=42)
        assert "melody" not in p

    def test_seed_reproducibility(self):
        p1 = generate_phrase("C", cadence="perfect", seed=42)
        p2 = generate_phrase("C", cadence="perfect", seed=42)
        assert p1["progression"] == p2["progression"]

    def test_all_cadence_types(self):
        for cad in ["perfect", "half", "deceptive", "plagal"]:
            p = generate_phrase("C", cadence=cad, length=4, seed=42)
            assert p["cadence_type"] == cad
            assert len(p["progression"]) == 4

    def test_unknown_cadence_defaults_to_perfect(self):
        p = generate_phrase("C", cadence="not_real", length=4, seed=42)
        # Falls back to perfect cadence template
        assert len(p["progression"]) == 4
