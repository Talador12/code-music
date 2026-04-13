"""Tests for classify_genre() — genre classification via weighted scoring."""

from code_music.theory import (
    andalusian_cadence,
    classify_genre,
    rhythm_changes,
    twelve_bar_blues,
)


class TestClassifyGenre:
    """Genre classifier correctness and edge cases."""

    def test_pop_progression(self):
        result = classify_genre([("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")])
        assert result["genre"] == "pop"
        assert result["confidence"] > 0.5

    def test_blues_12bar(self):
        prog = twelve_bar_blues("C")
        result = classify_genre(prog, bpm=120, swing=0.5)
        assert result["genre"] == "blues"
        assert result["confidence"] > 0.5

    def test_jazz_ii_v_i(self):
        prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("C", "maj7")]
        result = classify_genre(prog, swing=0.5)
        assert result["genre"] == "jazz"
        assert result["confidence"] > 0.5

    def test_jazz_rhythm_changes(self):
        prog = rhythm_changes("Bb")
        result = classify_genre(prog, swing=0.55)
        assert result["genre"] == "jazz"

    def test_ambient_suspended(self):
        prog = [("C", "sus2"), ("G", "sus4")]
        result = classify_genre(prog, bpm=60)
        assert result["genre"] == "ambient"

    def test_classical_i_iv_v_i(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "maj"), ("C", "maj")]
        result = classify_genre(prog)
        # Classical and pop share this pattern — either is acceptable
        assert result["genre"] in ("pop", "classical")

    def test_empty_progression(self):
        result = classify_genre([])
        assert result["genre"] == "unknown"
        assert result["confidence"] == 0.0

    def test_single_chord(self):
        result = classify_genre([("C", "dom7")])
        assert isinstance(result["genre"], str)
        assert result["confidence"] >= 0.0

    def test_scores_dict_present(self):
        result = classify_genre([("C", "maj"), ("G", "maj")])
        assert "scores" in result
        assert len(result["scores"]) > 0
        # All scores between 0 and 1
        for score in result["scores"].values():
            assert 0.0 <= score <= 1.0

    def test_features_present(self):
        result = classify_genre([("D", "min7"), ("G", "dom7")])
        f = result["features"]
        assert "quality_counts" in f
        assert "root_motions" in f
        assert "seventh_ratio" in f
        assert "tension_ratio" in f
        assert "chord_count" in f
        assert f["chord_count"] == 2

    def test_bpm_helps_distinguish(self):
        prog = [("A", "min"), ("F", "maj"), ("C", "maj"), ("G", "maj")]
        slow = classify_genre(prog, bpm=65)
        fast = classify_genre(prog, bpm=170)
        # At 65 BPM, ambient or classical should score higher
        # At 170 BPM, rock should score higher
        assert slow["scores"].get("ambient", 0) >= fast["scores"].get("ambient", 0) or slow[
            "scores"
        ].get("classical", 0) >= fast["scores"].get("classical", 0)

    def test_swing_helps_distinguish(self):
        prog = [("C", "min7"), ("F", "dom7"), ("Bb", "maj7")]
        swing_result = classify_genre(prog, swing=0.55)
        straight_result = classify_genre(prog, swing=0.0)
        # Swing should boost jazz/blues scores
        jazz_swing = swing_result["scores"].get("jazz", 0)
        jazz_straight = straight_result["scores"].get("jazz", 0)
        assert jazz_swing >= jazz_straight

    def test_r_and_b_ninths(self):
        prog = [("C", "min9"), ("F", "maj9"), ("G", "dom7"), ("C", "min9")]
        result = classify_genre(prog, bpm=90)
        assert result["genre"] in ("r&b", "jazz")

    def test_electronic_minor(self):
        prog = [("A", "min"), ("F", "maj"), ("C", "maj"), ("G", "min")]
        result = classify_genre(prog, bpm=128)
        assert result["genre"] in ("electronic", "pop")

    def test_andalusian_cadence_latin(self):
        prog = andalusian_cadence("A")
        result = classify_genre(prog)
        # Andalusian is characteristic of latin/rock/classical
        assert result["genre"] in ("latin", "rock", "pop", "classical")

    def test_all_genres_scored(self):
        prog = [("C", "maj"), ("G", "dom7")]
        result = classify_genre(prog)
        expected_genres = {
            "blues",
            "jazz",
            "pop",
            "rock",
            "classical",
            "r&b",
            "latin",
            "ambient",
            "electronic",
            "metal",
        }
        assert expected_genres.issubset(set(result["scores"].keys()))
