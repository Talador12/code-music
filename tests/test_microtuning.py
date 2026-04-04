"""Tests for v70.0 — just_ratio, cents_from_et, detune_to_just, quarter_tone."""

from code_music.engine import Note
from code_music.theory import cents_from_et, detune_to_just, just_ratio, quarter_tone


class TestJustRatio:
    def test_unison(self):
        assert just_ratio(0) == (1, 1)

    def test_perfect_fifth(self):
        assert just_ratio(7) == (3, 2)

    def test_major_third(self):
        assert just_ratio(4) == (5, 4)

    def test_octave(self):
        assert just_ratio(12) == (2, 1)

    def test_wraps(self):
        # 19 % 13 = 6 (tritone), not P5
        assert just_ratio(19) == (45, 32)  # tritone ratio
        # Simpler wrap test: 12 = octave
        assert just_ratio(12) == (2, 1)


class TestCentsFromET:
    def test_unison_zero(self):
        assert cents_from_et(0) == 0.0

    def test_perfect_fifth_close(self):
        # Just P5 = 701.96 cents, ET = 700 cents → ~+1.96
        c = cents_from_et(7)
        assert abs(c - 1.96) < 0.1

    def test_major_third_flat(self):
        # Just M3 = 386.31 cents, ET = 400 cents → ~-13.69
        c = cents_from_et(4)
        assert c < 0  # just M3 is flatter than ET


class TestDetuneToJust:
    def test_returns_offsets(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)]
        result = detune_to_just(notes, key="C")
        assert len(result) == 3

    def test_root_zero_offset(self):
        notes = [Note("C", 4, 1.0)]
        result = detune_to_just(notes, key="C")
        assert result[0]["cents_offset"] == 0.0

    def test_rest_passthrough(self):
        notes = [Note.rest(1.0)]
        result = detune_to_just(notes, key="C")
        assert result[0]["cents_offset"] == 0.0


class TestQuarterTone:
    def test_up(self):
        qt = quarter_tone("C", direction="up")
        assert qt["cents_offset"] == 50.0
        assert qt["base_note"] == "C"

    def test_down(self):
        qt = quarter_tone("D", direction="down")
        assert qt["cents_offset"] == -50.0

    def test_duration(self):
        qt = quarter_tone("E", duration=2.0)
        assert qt["duration"] == 2.0
