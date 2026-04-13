"""Tests for v135: period builder, guided composition, melodic similarity."""

from code_music.engine import Note
from code_music.theory import (
    compose,
    find_similar_melodies,
    generate_period,
    melody_similarity,
)

# ---------------------------------------------------------------------------
# generate_period
# ---------------------------------------------------------------------------


class TestGeneratePeriod:
    """Period builder chains phrases correctly."""

    def test_default_period(self):
        p = generate_period("C", seed=42)
        assert p["antecedent"]["cadence_type"] == "half"
        assert p["consequent"]["cadence_type"] == "perfect"
        assert len(p["full_progression"]) == 8  # 4 + 4

    def test_full_progression_is_combined(self):
        p = generate_period("C", seed=42)
        ante_prog = p["antecedent"]["progression"]
        cons_prog = p["consequent"]["progression"]
        assert p["full_progression"] == ante_prog + cons_prog

    def test_tension_curve_combined(self):
        p = generate_period("C", seed=42)
        assert len(p["tension_curve"]) == len(p["full_progression"])

    def test_melody_included_by_default(self):
        p = generate_period("C", seed=42)
        assert "melody" in p
        assert len(p["melody"]) > 0

    def test_melody_excluded(self):
        p = generate_period("C", include_melody=False, seed=42)
        assert "melody" not in p

    def test_custom_cadences(self):
        p = generate_period(
            "G", antecedent_cadence="deceptive", consequent_cadence="plagal", seed=7
        )
        assert p["antecedent"]["cadence_type"] == "deceptive"
        assert p["consequent"]["cadence_type"] == "plagal"

    def test_custom_phrase_length(self):
        p = generate_period("C", phrase_length=6, seed=42)
        assert len(p["full_progression"]) == 12  # 6 + 6

    def test_seed_reproducibility(self):
        p1 = generate_period("C", seed=42)
        p2 = generate_period("C", seed=42)
        assert p1["full_progression"] == p2["full_progression"]

    def test_different_key(self):
        p = generate_period("Bb", seed=42)
        # Consequent should end on Bb (tonic) for perfect cadence
        assert p["consequent"]["progression"][-1][0] == "Bb"

    def test_antecedent_ends_on_dominant(self):
        p = generate_period("C", antecedent_cadence="half", seed=42)
        # Half cadence ends on V (G)
        assert p["antecedent"]["progression"][-1][0] == "G"


# ---------------------------------------------------------------------------
# compose
# ---------------------------------------------------------------------------


class TestCompose:
    """Guided composition parses prompts correctly."""

    def test_jazz_in_bb(self):
        s = compose("jazz ballad in Bb at 90 bpm", seed=42)
        assert s.bpm == 90
        assert "Bb" in s.title
        assert "Jazz" in s.title

    def test_fast_rock(self):
        s = compose("fast rock song in E", seed=1)
        assert s.bpm == 160  # "fast" keyword
        assert "Rock" in s.title

    def test_slow_ambient(self):
        s = compose("slow ambient drone in F", seed=3)
        assert s.bpm == 72  # "slow" keyword
        assert "Ambient" in s.title

    def test_electronic_bpm(self):
        s = compose("electronic track at 128 bpm", seed=5)
        assert s.bpm == 128

    def test_sections_extracted(self):
        s = compose("pop song with intro verse chorus outro", seed=7)
        # Should have tracks with content
        for t in s.tracks:
            assert len(t.beats) > 0

    def test_default_genre(self):
        s = compose("something beautiful in D", seed=9)
        assert "Pop" in s.title  # default genre

    def test_classical_keyword(self):
        s = compose("classical piece in G", seed=11)
        assert "Classical" in s.title

    def test_empty_prompt(self):
        s = compose("", seed=42)
        assert s is not None
        assert len(s.tracks) > 0

    def test_seed_reproducibility(self):
        s1 = compose("jazz in C", seed=42)
        s2 = compose("jazz in C", seed=42)
        assert len(s1.tracks) == len(s2.tracks)
        for t1, t2 in zip(s1.tracks, s2.tracks):
            assert len(t1.beats) == len(t2.beats)

    def test_genre_synonyms(self):
        s1 = compose("swing tune", seed=42)
        assert "Jazz" in s1.title
        s2 = compose("bebop tune", seed=42)
        assert "Jazz" in s2.title
        s3 = compose("edm banger", seed=42)
        assert "Electronic" in s3.title


# ---------------------------------------------------------------------------
# melody_similarity + find_similar_melodies
# ---------------------------------------------------------------------------


class TestMelodySimilarity:
    """Melodic similarity scores are accurate and consistent."""

    def _rising(self):
        return [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]

    def _falling(self):
        return [Note("G", 5, 1.0), Note("E", 5, 1.0), Note("C", 5, 1.0)]

    def _transposed_rising(self):
        return [Note("D", 5, 1.0), Note("F#", 5, 1.0), Note("A", 5, 1.0)]

    def test_identical_melodies(self):
        a = self._rising()
        assert melody_similarity(a, a) == 1.0

    def test_transposed_same_shape(self):
        sim = melody_similarity(self._rising(), self._transposed_rising())
        assert sim == 1.0  # same intervals, same contour, same rhythm

    def test_opposite_contour_lower(self):
        sim = melody_similarity(self._rising(), self._falling())
        assert sim < 0.6  # opposite direction

    def test_similar_more_than_opposite(self):
        sim_same = melody_similarity(self._rising(), self._transposed_rising())
        sim_opp = melody_similarity(self._rising(), self._falling())
        assert sim_same > sim_opp

    def test_empty_melody(self):
        assert melody_similarity([], self._rising()) == 0.0
        assert melody_similarity(self._rising(), []) == 0.0

    def test_single_note(self):
        a = [Note("C", 5, 1.0)]
        b = [Note("G", 5, 1.0)]
        sim = melody_similarity(a, b)
        assert 0.0 <= sim <= 1.0

    def test_different_lengths(self):
        short = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        long = self._rising()
        sim = melody_similarity(short, long)
        assert 0.0 <= sim <= 1.0

    def test_custom_weights(self):
        a = self._rising()
        b = self._falling()
        # Contour-only should penalize opposite more
        contour_only = melody_similarity(
            a, b, weights={"contour": 1.0, "interval": 0.0, "rhythm": 0.0}
        )
        rhythm_only = melody_similarity(
            a, b, weights={"contour": 0.0, "interval": 0.0, "rhythm": 1.0}
        )
        assert rhythm_only > contour_only  # same rhythm, opposite contour

    def test_score_bounds(self):
        a = self._rising()
        b = self._falling()
        sim = melody_similarity(a, b)
        assert 0.0 <= sim <= 1.0


class TestFindSimilarMelodies:
    """Corpus search returns correctly ranked results."""

    def _corpus(self):
        return [
            ("rising_D", [Note("D", 5, 1.0), Note("F#", 5, 1.0), Note("A", 5, 1.0)]),
            ("falling_G", [Note("G", 5, 1.0), Note("E", 5, 1.0), Note("C", 5, 1.0)]),
            ("static_C", [Note("C", 5, 1.0), Note("C", 5, 1.0), Note("C", 5, 1.0)]),
        ]

    def test_top_result_is_most_similar(self):
        query = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]
        results = find_similar_melodies(query, self._corpus(), top_k=3)
        assert results[0]["name"] == "rising_D"  # same contour

    def test_results_sorted_descending(self):
        query = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]
        results = find_similar_melodies(query, self._corpus(), top_k=3)
        for i in range(1, len(results)):
            assert results[i]["score"] <= results[i - 1]["score"]

    def test_top_k_limits(self):
        query = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        results = find_similar_melodies(query, self._corpus(), top_k=1)
        assert len(results) == 1

    def test_min_score_filter(self):
        query = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]
        results = find_similar_melodies(query, self._corpus(), min_score=0.9)
        for r in results:
            assert r["score"] >= 0.9

    def test_empty_corpus(self):
        query = [Note("C", 5, 1.0)]
        assert find_similar_melodies(query, []) == []

    def test_empty_query(self):
        assert find_similar_melodies([], self._corpus()) == []

    def test_result_has_melody(self):
        query = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        results = find_similar_melodies(query, self._corpus(), top_k=1)
        assert "melody" in results[0]
        assert len(results[0]["melody"]) > 0
