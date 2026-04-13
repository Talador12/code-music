"""Tests for v134 features: variation suite, critique, modulation detector."""

from code_music.engine import Note
from code_music.theory import (
    critique,
    detect_modulations,
    generate_theme_and_variations,
    twelve_bar_blues,
)

# ---------------------------------------------------------------------------
# generate_theme_and_variations
# ---------------------------------------------------------------------------


class TestThemeAndVariations:
    """Variation suite generator produces valid multi-section songs."""

    def test_default_generation(self):
        song = generate_theme_and_variations(key="C", n_variations=3, seed=42)
        assert song.title == "Theme and Variations in C"
        assert len(song.tracks) == 2  # melody + chords
        for t in song.tracks:
            assert len(t.beats) > 0

    def test_custom_theme(self):
        theme = [Note("C", 5, 0.5), Note("D", 5, 0.5), Note("E", 5, 0.5), Note("C", 5, 0.5)]
        song = generate_theme_and_variations(theme=theme, key="C", n_variations=2, seed=7)
        mel_track = next(t for t in song.tracks if t.name == "melody")
        # Theme (4 notes) + 2 variations (each ~4 notes)
        assert len(mel_track.beats) >= 8

    def test_n_variations_capped(self):
        song = generate_theme_and_variations(key="C", n_variations=100, seed=42)
        # Should cap at 7 (len of _VARIATION_RECIPES - 1)
        assert song is not None
        mel_track = next(t for t in song.tracks if t.name == "melody")
        assert len(mel_track.beats) > 0

    def test_zero_variations(self):
        song = generate_theme_and_variations(key="G", n_variations=0, seed=42)
        # Just the theme, no variations
        mel_track = next(t for t in song.tracks if t.name == "melody")
        assert len(mel_track.beats) == 16  # default theme length

    def test_chord_track_present(self):
        song = generate_theme_and_variations(key="D", n_variations=2, seed=42)
        chord_track = next(t for t in song.tracks if t.name == "chords")
        # Theme + 2 variations = 3 sections × 4 chords = 12
        assert len(chord_track.beats) == 12

    def test_seed_reproducibility(self):
        s1 = generate_theme_and_variations(key="C", seed=42)
        s2 = generate_theme_and_variations(key="C", seed=42)
        beats1 = len(s1.tracks[0].beats)
        beats2 = len(s2.tracks[0].beats)
        assert beats1 == beats2

    def test_different_key(self):
        song = generate_theme_and_variations(key="F#", n_variations=2, seed=42)
        assert "F#" in song.title

    def test_different_scale(self):
        song = generate_theme_and_variations(key="A", scale_name="minor", n_variations=2, seed=42)
        assert len(song.tracks) == 2


# ---------------------------------------------------------------------------
# critique
# ---------------------------------------------------------------------------


class TestCritique:
    """Composition critique grades progressions accurately."""

    def test_good_progression_high_score(self):
        r = critique([("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")], key="C")
        assert r["score"] >= 80
        assert r["grade"] in ("A", "B")

    def test_static_progression_low_score(self):
        r = critique([("C", "maj"), ("C", "maj"), ("C", "maj"), ("C", "maj")], key="C")
        assert r["score"] < 70
        assert len(r["issues"]) >= 2

    def test_empty_progression(self):
        r = critique([], key="C")
        assert r["score"] == 0
        assert r["grade"] == "F"

    def test_issues_list(self):
        r = critique([("C", "maj")] * 4, key="C")
        assert isinstance(r["issues"], list)
        assert all(isinstance(s, str) for s in r["issues"])

    def test_strengths_list(self):
        r = critique([("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")], key="C")
        assert isinstance(r["strengths"], list)
        assert len(r["strengths"]) > 0

    def test_suggestions_list(self):
        r = critique([("C", "maj")] * 4, key="C")
        assert isinstance(r["suggestions"], list)
        assert len(r["suggestions"]) > 0

    def test_with_melody(self):
        mel = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0), Note("C", 6, 1.0)]
        r = critique([("C", "maj"), ("G", "dom7")], melody=mel, key="C")
        assert "score" in r

    def test_wide_melody_range_flagged(self):
        mel = [Note("C", 3, 1.0), Note("C", 7, 1.0)]  # huge range
        r = critique([("C", "maj"), ("G", "dom7")], melody=mel, key="C")
        has_range_issue = any("range" in s.lower() or "span" in s.lower() for s in r["issues"])
        assert has_range_issue

    def test_unresolved_dominant_flagged(self):
        # End on V7 — unresolved
        r = critique([("C", "maj"), ("F", "maj"), ("G", "dom7")], key="C")
        has_tension_issue = any(
            "unresolved" in s.lower() or "tension" in s.lower() for s in r["issues"]
        )
        assert has_tension_issue

    def test_blues_scores_well(self):
        prog = twelve_bar_blues("C")
        r = critique(prog, key="C")
        assert r["score"] >= 50  # blues should be at least passable

    def test_score_bounds(self):
        r = critique([("C", "maj"), ("G", "dom7")], key="C")
        assert 0 <= r["score"] <= 100

    def test_grade_is_letter(self):
        r = critique([("C", "maj"), ("G", "dom7"), ("C", "maj")], key="C")
        assert r["grade"] in ("A", "B", "C", "D", "F")


# ---------------------------------------------------------------------------
# detect_modulations
# ---------------------------------------------------------------------------


class TestDetectModulations:
    """Modulation detector finds key changes correctly."""

    def test_no_modulation(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]
        regions = detect_modulations(prog)
        assert len(regions) == 1
        assert regions[0]["key"] == "C"

    def test_simple_modulation(self):
        # C major → G major
        prog = [
            ("C", "maj"),
            ("F", "maj"),
            ("G", "dom7"),
            ("C", "maj"),
            ("G", "maj"),
            ("C", "maj"),
            ("D", "dom7"),
            ("G", "maj"),
        ]
        regions = detect_modulations(prog, window=4)
        assert len(regions) >= 2
        keys = [r["key"] for r in regions]
        assert "C" in keys
        assert "G" in keys

    def test_regions_cover_full_progression(self):
        prog = [
            ("C", "maj"),
            ("F", "maj"),
            ("G", "dom7"),
            ("C", "maj"),
            ("G", "maj"),
            ("D", "dom7"),
            ("G", "maj"),
            ("C", "maj"),
        ]
        regions = detect_modulations(prog, window=4)
        # All chords should be covered
        total_covered = sum(r["end"] - r["start"] for r in regions)
        assert total_covered == len(prog)

    def test_regions_are_contiguous(self):
        prog = [("C", "maj")] * 4 + [("G", "maj")] * 4
        regions = detect_modulations(prog, window=4)
        for i in range(1, len(regions)):
            assert regions[i]["start"] == regions[i - 1]["end"]

    def test_pivot_chord_identified(self):
        prog = [
            ("C", "maj"),
            ("F", "maj"),
            ("G", "dom7"),
            ("C", "maj"),
            ("G", "maj"),
            ("C", "maj"),
            ("D", "dom7"),
            ("G", "maj"),
        ]
        regions = detect_modulations(prog, window=4)
        if len(regions) >= 2:
            # Second region should have a pivot chord
            assert regions[1]["pivot_chord"] is not None

    def test_short_progression(self):
        regions = detect_modulations([("C", "maj"), ("G", "dom7")])
        assert len(regions) == 1

    def test_empty_progression(self):
        regions = detect_modulations([])
        assert len(regions) == 1
        assert regions[0]["key"] == "C"  # default

    def test_single_key_region_structure(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]
        regions = detect_modulations(prog)
        r = regions[0]
        assert "key" in r
        assert "start" in r
        assert "end" in r
        assert "pivot_chord" in r
        assert r["start"] == 0
        assert r["end"] == len(prog)

    def test_custom_window_size(self):
        prog = [("C", "maj")] * 3 + [("G", "maj")] * 3
        regions_small = detect_modulations(prog, window=3)
        regions_large = detect_modulations(prog, window=5)
        # Both should find regions, but results may differ
        assert len(regions_small) >= 1
        assert len(regions_large) >= 1
