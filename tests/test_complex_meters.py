"""Tests for v67.0 — nested_tuplet, irrational_meter, polymetric_overlay."""

from code_music.engine import Note
from code_music.theory import irrational_meter, nested_tuplet, polymetric_overlay


class TestNestedTuplet:
    def test_3_in_5(self):
        notes = [Note("C", 5, 1.0)] * 15
        result = nested_tuplet(3, 5, notes, total_duration=4.0)
        assert len(result) == 15  # 3*5

    def test_duration_correct(self):
        notes = [Note("C", 5, 1.0)] * 6
        result = nested_tuplet(2, 3, notes, total_duration=2.0)
        assert abs(result[0].duration - 2.0 / 6) < 1e-9

    def test_truncates_excess_notes(self):
        notes = [Note("C", 5, 1.0)] * 100
        result = nested_tuplet(3, 4, notes, total_duration=4.0)
        assert len(result) == 12  # 3*4

    def test_handles_rests(self):
        notes = [Note.rest(1.0)] * 6
        result = nested_tuplet(2, 3, notes)
        assert all(n.pitch is None for n in result)

    def test_preserves_pitch(self):
        notes = [Note("E", 5, 1.0), Note("G", 5, 1.0)]
        result = nested_tuplet(1, 2, notes, total_duration=1.0)
        assert result[0].pitch == "E"


class TestIrrationalMeter:
    def test_7_12(self):
        notes = irrational_meter(7, 12)
        assert len(notes) == 7

    def test_5_6(self):
        notes = irrational_meter(5, 6)
        assert len(notes) == 5

    def test_accent_on_beat_1(self):
        notes = irrational_meter(7, 8)
        assert notes[0].velocity == 100
        assert notes[1].velocity == 70

    def test_multiple_bars(self):
        notes = irrational_meter(5, 8, bars=3)
        assert len(notes) == 15

    def test_duration_scales(self):
        # 4/4 should give standard quarter-note duration
        notes = irrational_meter(4, 4, base_duration=1.0)
        assert abs(notes[0].duration - 1.0) < 1e-9
        # 4/8 should give half the duration
        notes = irrational_meter(4, 8, base_duration=1.0)
        assert abs(notes[0].duration - 0.5) < 1e-9


class TestPolymetricOverlay:
    def test_two_meters(self):
        voices = polymetric_overlay([(3, 4), (4, 4)])
        assert len(voices) == 2

    def test_octave_offset(self):
        voices = polymetric_overlay([(3, 4), (4, 4)], octave=3)
        assert voices[0][0].octave == 3
        assert voices[1][0].octave == 4

    def test_voice_lengths(self):
        voices = polymetric_overlay([(3, 8), (5, 8)])
        assert len(voices[0]) == 3
        assert len(voices[1]) == 5
