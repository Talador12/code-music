"""Tests for v73.0 — quantize_rhythm, swing_quantize, humanize_timing."""

from code_music.engine import Note
from code_music.theory import humanize_timing, quantize_rhythm, swing_quantize


class TestQuantizeRhythm:
    def test_already_on_grid(self):
        notes = [Note("C", 5, 0.5), Note("E", 5, 0.25)]
        result = quantize_rhythm(notes, grid=0.25)
        assert result[0].duration == 0.5
        assert result[1].duration == 0.25

    def test_snaps_to_grid(self):
        notes = [Note("C", 5, 0.37)]  # between 0.25 and 0.5
        result = quantize_rhythm(notes, grid=0.25)
        assert result[0].duration == 0.25 or result[0].duration == 0.5

    def test_preserves_pitch(self):
        notes = [Note("G", 4, 0.3)]
        result = quantize_rhythm(notes, grid=0.25)
        assert result[0].pitch == "G"

    def test_rest_passthrough(self):
        notes = [Note.rest(0.37)]
        result = quantize_rhythm(notes, grid=0.25)
        assert result[0].pitch is None

    def test_min_grid(self):
        notes = [Note("C", 5, 0.01)]
        result = quantize_rhythm(notes, grid=0.25)
        assert result[0].duration == 0.25  # floor at grid


class TestSwingQuantize:
    def test_alternating_durations(self):
        notes = [Note("C", 5, 0.5)] * 4
        result = swing_quantize(notes, grid=0.5, swing_amount=0.66)
        # Even notes should be longer than odd
        assert result[0].duration > result[1].duration

    def test_straight_swing(self):
        notes = [Note("C", 5, 0.5)] * 4
        result = swing_quantize(notes, grid=0.5, swing_amount=0.5)
        # 0.5 swing = straight, all durations equal
        assert abs(result[0].duration - result[1].duration) < 1e-9

    def test_preserves_pitch(self):
        notes = [Note("E", 5, 0.5)]
        result = swing_quantize(notes)
        assert result[0].pitch == "E"


class TestHumanizeTiming:
    def test_adds_deviation(self):
        notes = [Note("C", 5, 0.5)] * 20
        result = humanize_timing(notes, amount=0.05, seed=42)
        # At least some durations should differ from 0.5
        assert any(abs(n.duration - 0.5) > 0.001 for n in result)

    def test_deterministic(self):
        notes = [Note("C", 5, 0.5)] * 8
        a = humanize_timing(notes, seed=99)
        b = humanize_timing(notes, seed=99)
        assert [n.duration for n in a] == [n.duration for n in b]

    def test_zero_amount_no_change(self):
        notes = [Note("C", 5, 0.5)] * 4
        result = humanize_timing(notes, amount=0.0, seed=42)
        assert all(abs(n.duration - 0.5) < 1e-9 for n in result)
