"""Tests for v53.0 — instrument_range, in_range, double_at_octave, string_quartet."""

import pytest

from code_music.engine import Note
from code_music.theory import double_at_octave, in_range, instrument_range, string_quartet


class TestInstrumentRange:
    def test_violin(self):
        low, high = instrument_range("violin")
        assert low < high
        assert low == 55  # G3
        assert high == 88  # E7

    def test_piano_widest(self):
        low, high = instrument_range("piano")
        assert high - low > 80  # piano has huge range

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown instrument"):
            instrument_range("kazoo")

    def test_all_instruments_valid(self):
        for name in [
            "violin",
            "viola",
            "cello",
            "contrabass",
            "flute",
            "oboe",
            "clarinet",
            "bassoon",
            "trumpet",
            "french_horn",
            "trombone",
            "tuba",
            "piano",
            "guitar",
            "bass_guitar",
        ]:
            low, high = instrument_range(name)
            assert low < high


class TestInRange:
    def test_middle_c_on_piano(self):
        assert in_range(Note("C", 4, 1.0), "piano") is True

    def test_low_note_on_flute(self):
        assert in_range(Note("C", 2, 1.0), "flute") is False

    def test_rest_always_valid(self):
        assert in_range(Note.rest(1.0), "violin") is True

    def test_high_violin(self):
        assert in_range(Note("E", 7, 1.0), "violin") is True
        assert in_range(Note("C", 8, 1.0), "violin") is False


class TestDoubleAtOctave:
    def test_octave_up(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0)]
        doubled = double_at_octave(notes, direction=1)
        assert doubled[0].octave == 5
        assert doubled[1].octave == 5

    def test_octave_down(self):
        notes = [Note("G", 5, 1.0)]
        doubled = double_at_octave(notes, direction=-1)
        assert doubled[0].octave == 4

    def test_preserves_pitch(self):
        notes = [Note("D", 4, 1.0)]
        doubled = double_at_octave(notes)
        assert doubled[0].pitch == "D"

    def test_rest_passthrough(self):
        notes = [Note.rest(2.0)]
        doubled = double_at_octave(notes)
        assert doubled[0].pitch is None
        assert doubled[0].duration == 2.0

    def test_preserves_velocity(self):
        notes = [Note("C", 4, 1.0, velocity=80)]
        doubled = double_at_octave(notes)
        assert doubled[0].velocity == 80


class TestStringQuartet:
    def test_returns_four_parts(self):
        melody = [Note("E", 5, 4.0), Note("G", 5, 4.0)]
        harmony = [("C", "maj"), ("G", "maj")]
        parts = string_quartet(melody, harmony)
        assert "violin_1" in parts
        assert "violin_2" in parts
        assert "viola" in parts
        assert "cello" in parts

    def test_violin_1_is_melody(self):
        melody = [Note("E", 5, 4.0)]
        harmony = [("C", "maj")]
        parts = string_quartet(melody, harmony)
        assert parts["violin_1"][0].pitch == "E"

    def test_cello_has_roots(self):
        melody = [Note("E", 5, 4.0), Note("D", 5, 4.0)]
        harmony = [("C", "maj"), ("G", "maj")]
        parts = string_quartet(melody, harmony)
        assert parts["cello"][0].pitch == "C"
        assert parts["cello"][1].pitch == "G"

    def test_part_lengths_match_harmony(self):
        melody = [Note("E", 5, 4.0)] * 4
        harmony = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]
        parts = string_quartet(melody, harmony)
        assert len(parts["violin_2"]) == 4
        assert len(parts["viola"]) == 4
        assert len(parts["cello"]) == 4
