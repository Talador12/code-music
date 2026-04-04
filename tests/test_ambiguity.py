"""Tests for v106.0 — ambiguity_score, key_certainty."""

from code_music.theory import ambiguity_score, key_certainty


class TestAmbiguityScore:
    def test_diatonic_lower_than_chromatic(self):
        diatonic = [
            ("C", "maj"),
            ("F", "maj"),
            ("G", "dom7"),
            ("C", "maj"),
            ("A", "min"),
            ("D", "min"),
            ("E", "min"),
        ]
        chromatic = [
            ("C", "maj"),
            ("F#", "maj"),
            ("Eb", "min"),
            ("A", "dom7"),
            ("Db", "maj"),
            ("G", "min"),
            ("B", "aug"),
            ("Bb", "dim"),
        ]
        assert ambiguity_score(diatonic) < ambiguity_score(chromatic)

    def test_chromatic_high(self):
        prog = [
            ("C", "maj"),
            ("F#", "maj"),
            ("Eb", "min"),
            ("A", "dom7"),
            ("Db", "maj"),
            ("G", "min"),
            ("B", "aug"),
            ("Bb", "dim"),
        ]
        score = ambiguity_score(prog)
        assert score > 0.3  # many keys fit poorly

    def test_range(self):
        prog = [("C", "maj")]
        score = ambiguity_score(prog)
        assert 0.0 <= score <= 1.0

    def test_empty(self):
        assert ambiguity_score([]) == 0.0


class TestKeyCertainty:
    def test_clear_key(self):
        # More roots = clearer key
        prog = [
            ("C", "maj"),
            ("F", "maj"),
            ("G", "dom7"),
            ("C", "maj"),
            ("A", "min"),
            ("D", "min"),
            ("E", "min"),
        ]
        result = key_certainty(prog)
        assert result["key"] == "C"
        assert result["confidence"] > 0.0

    def test_structure(self):
        result = key_certainty([("C", "maj")])
        assert "key" in result
        assert "confidence" in result
        assert "ambiguity" in result

    def test_confidence_plus_ambiguity(self):
        result = key_certainty([("G", "maj"), ("C", "maj"), ("D", "dom7")])
        assert abs(result["confidence"] + result["ambiguity"] - 1.0) < 0.01

    def test_empty(self):
        result = key_certainty([])
        assert result["confidence"] == 0.0
