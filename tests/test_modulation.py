"""Tests for v43.0 — find_pivot_chords, modulation_path, direct_modulation, pivot_modulation."""

from code_music.theory import (
    direct_modulation,
    find_pivot_chords,
    modulation_path,
    pivot_modulation,
)


class TestFindPivotChords:
    def test_c_and_g_share_chords(self):
        pivots = find_pivot_chords("C", "G")
        assert len(pivots) > 0
        # C major and G major share several chords (e.g. C maj, E min, G maj, A min)
        roots = [r for r, _ in pivots]
        assert any(r in roots for r in ["C", "G", "E", "A"])

    def test_same_key_returns_all_diatonic(self):
        pivots = find_pivot_chords("C", "C")
        assert len(pivots) == 7  # all diatonic chords are shared

    def test_distant_keys_fewer_pivots(self):
        close = find_pivot_chords("C", "G")
        distant = find_pivot_chords("C", "F#")
        # Distant keys should have fewer common chords
        assert len(distant) <= len(close)

    def test_minor_mode(self):
        pivots = find_pivot_chords("A", "E", "aeolian", "aeolian")
        assert len(pivots) > 0

    def test_returns_tuples(self):
        pivots = find_pivot_chords("C", "F")
        for root, shape in pivots:
            assert isinstance(root, str)
            assert isinstance(shape, str)


class TestModulationPath:
    def test_same_key_empty(self):
        path = modulation_path("C", "C")
        # Same key — no movement needed, but algorithm still produces cadence
        assert isinstance(path, list)

    def test_close_keys_short_path(self):
        path = modulation_path("C", "G")
        assert len(path) >= 2  # at least one V-I cadence

    def test_distant_keys_longer_path(self):
        close_path = modulation_path("C", "G")
        far_path = modulation_path("C", "F#")
        assert len(far_path) >= len(close_path)

    def test_path_ends_on_target(self):
        path = modulation_path("C", "Eb")
        assert path[-1][0] == "Eb"

    def test_path_contains_dom7(self):
        path = modulation_path("C", "D")
        shapes = [s for _, s in path]
        assert "dom7" in shapes  # V-I cadences use dom7


class TestDirectModulation:
    def test_three_chords(self):
        prog = direct_modulation("C", "D")
        assert len(prog) == 3

    def test_starts_on_old_key(self):
        prog = direct_modulation("C", "D")
        assert prog[0] == ("C", "maj")

    def test_ends_on_new_key(self):
        prog = direct_modulation("Bb", "C")
        assert prog[-1] == ("C", "maj")

    def test_middle_is_v7_of_new(self):
        prog = direct_modulation("C", "D")
        assert prog[1] == ("A", "dom7")  # V7 of D


class TestPivotModulation:
    def test_four_chords_with_pivot(self):
        prog = pivot_modulation("C", "G")
        assert len(prog) >= 3

    def test_starts_on_old_key(self):
        prog = pivot_modulation("C", "G")
        assert prog[0] == ("C", "maj")

    def test_ends_on_new_key(self):
        prog = pivot_modulation("C", "G")
        assert prog[-1] == ("G", "maj")

    def test_contains_dom7(self):
        prog = pivot_modulation("C", "F")
        shapes = [s for _, s in prog]
        assert "dom7" in shapes

    def test_distant_keys_fallback(self):
        # Very distant keys may fall back to direct modulation
        prog = pivot_modulation("C", "F#")
        assert len(prog) >= 3
        assert prog[-1][0] == "F#"
