"""Tests for v78.0 — list_patterns, get_pattern, chain_patterns."""

import pytest

from code_music.theory import chain_patterns, get_pattern, list_patterns


class TestListPatterns:
    def test_returns_list(self):
        patterns = list_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) >= 20

    def test_filter_genre(self):
        jazz = list_patterns(genre="jazz")
        assert all("jazz" in p for p in jazz)

    def test_filter_difficulty(self):
        easy = list_patterns(max_difficulty=1)
        assert len(easy) > 0
        hard = list_patterns(max_difficulty=4)
        assert len(hard) >= len(easy)

    def test_sorted(self):
        patterns = list_patterns()
        assert patterns == sorted(patterns)


class TestGetPattern:
    def test_returns_notes(self):
        notes = get_pattern("blues_bend")
        assert len(notes) > 0

    def test_transposition(self):
        c_notes = get_pattern("blues_bend", key="C")
        g_notes = get_pattern("blues_bend", key="G")
        assert [n.pitch for n in c_notes] != [n.pitch for n in g_notes]

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown pattern"):
            get_pattern("nonexistent_lick")

    def test_custom_duration(self):
        notes = get_pattern("blues_bend", duration=0.25)
        assert all(n.duration == 0.25 for n in notes)


class TestChainPatterns:
    def test_chains_two(self):
        notes = chain_patterns(["blues_bend", "blues_call"])
        assert len(notes) > 10  # two patterns + connector

    def test_single_pattern(self):
        notes = chain_patterns(["rock_power"])
        assert len(notes) == 7  # just the pattern, no connector

    def test_has_connector(self):
        single = get_pattern("blues_bend")
        chained = chain_patterns(["blues_bend", "blues_call"])
        assert len(chained) > len(single)
