"""Tests for v137.0: progression_dna, progression_distance, CLI compose/analyze."""

import unittest

from code_music import (
    find_similar_progressions_dna,
    progression_distance,
    progression_dna,
)

# ---------------------------------------------------------------------------
# progression_dna
# ---------------------------------------------------------------------------


class TestProgressionDNA(unittest.TestCase):
    """Encode chord progressions as compact feature vectors."""

    def test_returns_dict(self):
        dna = progression_dna([("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")])
        assert isinstance(dna, dict)

    def test_has_expected_keys(self):
        dna = progression_dna([("C", "maj"), ("G", "maj")])
        for key in [
            "root_motion",
            "quality_dist",
            "tension_stats",
            "interval_pattern",
            "length",
            "unique_roots",
            "unique_qualities",
            "vector",
        ]:
            assert key in dna, f"Missing key: {key}"

    def test_root_motion_is_12_bins(self):
        dna = progression_dna([("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")])
        assert len(dna["root_motion"]) == 12

    def test_root_motion_sums_to_one(self):
        dna = progression_dna([("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")])
        total = sum(dna["root_motion"])
        assert abs(total - 1.0) < 0.01

    def test_quality_dist_fractions(self):
        dna = progression_dna([("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")])
        total = sum(dna["quality_dist"].values())
        assert abs(total - 1.0) < 0.01

    def test_tension_stats_present(self):
        dna = progression_dna([("C", "maj"), ("G", "dom7"), ("C", "maj")])
        for key in ["mean", "std", "min", "max", "range"]:
            assert key in dna["tension_stats"]

    def test_length_correct(self):
        prog = [("C", "maj"), ("G", "maj"), ("A", "min")]
        assert progression_dna(prog)["length"] == 3

    def test_unique_roots(self):
        dna = progression_dna([("C", "maj"), ("G", "maj"), ("C", "min")])
        assert dna["unique_roots"] == 2  # C and G

    def test_unique_qualities(self):
        dna = progression_dna([("C", "maj"), ("G", "maj"), ("A", "min")])
        assert dna["unique_qualities"] == 2  # maj and min

    def test_empty_progression(self):
        dna = progression_dna([])
        assert dna["length"] == 0
        assert len(dna["vector"]) == 22

    def test_single_chord(self):
        dna = progression_dna([("C", "maj")])
        assert dna["length"] == 1
        assert dna["interval_pattern"] == []

    def test_vector_is_flat_floats(self):
        dna = progression_dna([("C", "maj"), ("F", "maj"), ("G", "maj"), ("C", "maj")])
        assert isinstance(dna["vector"], list)
        assert all(isinstance(v, float) for v in dna["vector"])

    def test_vector_length_consistent(self):
        dna = progression_dna([("C", "maj"), ("G", "maj")])
        # 12 root_motion + 5 tension + 2 counts + 3 quality = 22
        assert len(dna["vector"]) == 22

    def test_identical_progressions_same_dna(self):
        prog = [("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")]
        dna1 = progression_dna(prog)
        dna2 = progression_dna(prog)
        assert dna1["vector"] == dna2["vector"]


# ---------------------------------------------------------------------------
# progression_distance
# ---------------------------------------------------------------------------


class TestProgressionDistance(unittest.TestCase):
    """Distance between progression DNA vectors."""

    def test_identical_is_zero(self):
        prog = [("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")]
        dna = progression_dna(prog)
        assert progression_distance(dna, dna) == 0.0

    def test_different_is_positive(self):
        dna1 = progression_dna([("C", "maj"), ("G", "maj")])
        dna2 = progression_dna([("C", "min7"), ("F", "dom7")])
        assert progression_distance(dna1, dna2) > 0.0

    def test_similar_closer_than_dissimilar(self):
        pop = progression_dna([("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")])
        pop2 = progression_dna([("G", "maj"), ("D", "maj"), ("E", "min"), ("C", "maj")])
        jazz = progression_dna([("D", "min7"), ("G", "dom7"), ("C", "maj7")])
        # Two pop progressions should be more similar than pop vs jazz
        d_pop_pop = progression_distance(pop, pop2)
        d_pop_jazz = progression_distance(pop, jazz)
        assert d_pop_pop < d_pop_jazz

    def test_empty_dna(self):
        empty = progression_dna([])
        full = progression_dna([("C", "maj"), ("G", "maj")])
        dist = progression_distance(empty, full)
        assert dist >= 0.0


# ---------------------------------------------------------------------------
# find_similar_progressions_dna
# ---------------------------------------------------------------------------


class TestFindSimilarProgressionsDNA(unittest.TestCase):
    """Corpus search by progression DNA."""

    def test_finds_exact_match(self):
        query = [("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")]
        corpus = [
            ("pop1", [("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")]),
            ("jazz1", [("D", "min7"), ("G", "dom7"), ("C", "maj7")]),
        ]
        results = find_similar_progressions_dna(query, corpus)
        assert results[0]["name"] == "pop1"
        assert results[0]["distance"] == 0.0

    def test_top_k_limit(self):
        query = [("C", "maj"), ("G", "maj")]
        corpus = [
            ("a", [("C", "maj"), ("G", "maj")]),
            ("b", [("D", "min"), ("A", "maj")]),
            ("c", [("F", "maj"), ("C", "maj")]),
        ]
        results = find_similar_progressions_dna(query, corpus, top_k=2)
        assert len(results) == 2

    def test_empty_corpus(self):
        assert find_similar_progressions_dna([("C", "maj")], []) == []

    def test_empty_query(self):
        assert find_similar_progressions_dna([], [("a", [("C", "maj")])]) == []

    def test_sorted_by_distance(self):
        query = [("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")]
        corpus = [
            ("jazz", [("D", "min7"), ("G", "dom7"), ("C", "maj7")]),
            ("pop_variant", [("C", "maj"), ("F", "maj"), ("G", "maj"), ("C", "maj")]),
            ("exact", [("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")]),
        ]
        results = find_similar_progressions_dna(query, corpus)
        distances = [r["distance"] for r in results]
        assert distances == sorted(distances)


# ---------------------------------------------------------------------------
# CLI compose + analyze
# ---------------------------------------------------------------------------


class TestCLICompose(unittest.TestCase):
    """CLI --compose and --analyze flags are registered."""

    def test_compose_flag_accepted(self):
        """CLI main accepts --compose without crashing on parse."""
        import io
        from contextlib import redirect_stderr, redirect_stdout

        from code_music.cli import main

        # --compose with --help should show it in usage
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                main(["--help"])
            except SystemExit:
                pass
        combined = out.getvalue() + err.getvalue()
        assert "compose" in combined.lower()

    def test_analyze_flag_accepted(self):
        """CLI main accepts --analyze in help text."""
        import io
        from contextlib import redirect_stderr, redirect_stdout

        from code_music.cli import main

        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                main(["--help"])
            except SystemExit:
                pass
        combined = out.getvalue() + err.getvalue()
        assert "analyze" in combined.lower()


class TestCLIImports(unittest.TestCase):
    """Verify all v137 exports are importable."""

    def test_import_progression_dna(self):
        from code_music import progression_dna

        assert callable(progression_dna)

    def test_import_progression_distance(self):
        from code_music import progression_distance

        assert callable(progression_distance)

    def test_import_find_similar_dna(self):
        from code_music import find_similar_progressions_dna

        assert callable(find_similar_progressions_dna)

    def test_import_from_theory(self):
        from code_music.theory import (
            find_similar_progressions_dna,
            progression_distance,
            progression_dna,
        )

        assert callable(progression_dna)
        assert callable(progression_distance)
        assert callable(find_similar_progressions_dna)


if __name__ == "__main__":
    unittest.main()
