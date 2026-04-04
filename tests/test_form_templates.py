"""Tests for v49.0 — song_form, section_bars."""

import pytest

from code_music.theory import section_bars, song_form


class TestSongForm:
    def test_pop(self):
        form = song_form("pop")
        assert form[0] == "intro"
        assert "chorus" in form
        assert form[-1] == "outro"
        assert len(form) == 8

    def test_aaba(self):
        form = song_form("aaba")
        assert form == ["A", "A", "B", "A"]

    def test_blues(self):
        form = song_form("blues")
        assert form == ["head", "solo", "head"]

    def test_edm(self):
        form = song_form("edm")
        assert "drop" in form
        assert "buildup" in form
        assert len(form) == 7

    def test_rondo(self):
        form = song_form("rondo")
        assert form == ["A", "B", "A", "C", "A", "B", "A"]

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown form"):
            song_form("djent")


class TestSectionBars:
    def test_pop_default(self):
        bars = section_bars("pop")
        assert len(bars) == 8
        assert bars[0] == ("intro", 8)

    def test_custom_bar_count(self):
        bars = section_bars("aaba", bars_per_section=16)
        assert bars[0] == ("A", 16)
        assert len(bars) == 4

    def test_total_bars(self):
        bars = section_bars("blues", bars_per_section=12)
        total = sum(b for _, b in bars)
        assert total == 36  # 3 sections × 12 bars
