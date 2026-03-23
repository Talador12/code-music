"""Tests for engine helpers: arp, crescendo, decrescendo, transpose, humanize."""

import pytest

from code_music.engine import (
    ARP_PATTERNS,
    Chord,
    Note,
    arp,
    crescendo,
    decrescendo,
    humanize,
    repeat,
    transpose,
)


class TestArp:
    def test_up_pattern(self):
        # Major chord has 3 notes; "up" pattern [0,1,2,3] — idx 3 is out of range, so 3 notes
        c = Chord("C", "maj", 4, duration=1.0)
        result = arp(c, pattern="up", rate=0.25)
        assert len(result) == 3  # indices 0,1,2 valid; 3 is out of range for 3-note chord
        assert all(n.duration == 0.25 for n in result)

    def test_up_down_pattern(self):
        # maj7 has 4 notes, "up_down" = [0,1,2,3,2,1] — all 6 valid
        c = Chord("C", "maj7", 4, duration=1.0)
        result = arp(c, pattern="up_down", rate=0.5)
        assert len(result) == len(ARP_PATTERNS["up_down"])

    def test_custom_pattern(self):
        c = Chord("C", "maj", 4)
        result = arp(c, pattern=[0, 2, 1], rate=0.25)
        assert len(result) == 3

    def test_octave_span(self):
        c = Chord("C", "maj", 4)
        result_1 = arp(c, octaves=1)
        result_2 = arp(c, octaves=2)
        # 2 octaves should give more notes available
        assert len(result_2) >= len(result_1)

    def test_rate_respected(self):
        c = Chord("C", "maj", 4)
        result = arp(c, rate=0.125)
        assert all(n.duration == 0.125 for n in result)

    def test_all_named_patterns_work(self):
        c = Chord("A", "min7", 4)
        for name in ARP_PATTERNS:
            result = arp(c, pattern=name, rate=0.25)
            assert isinstance(result, list)


class TestCrescendoDecrescendo:
    def test_crescendo_increases_velocity(self):
        notes = [Note("C", 4, 1.0, velocity=0.5) for _ in range(4)]
        result = crescendo(notes, start_vel=0.2, end_vel=1.0)
        vels = [n.velocity for n in result]
        assert vels[0] < vels[-1]
        assert vels[0] == pytest.approx(0.2, abs=0.01)
        assert vels[-1] == pytest.approx(1.0, abs=0.01)

    def test_decrescendo_decreases_velocity(self):
        notes = [Note("C", 4, 1.0, velocity=0.5) for _ in range(4)]
        result = decrescendo(notes, start_vel=1.0, end_vel=0.1)
        vels = [n.velocity for n in result]
        assert vels[0] > vels[-1]

    def test_preserves_pitch_and_duration(self):
        notes = [Note("G", 5, 2.0, velocity=0.5)]
        result = crescendo(notes)
        assert result[0].pitch == "G"
        assert result[0].duration == 2.0

    def test_empty_list(self):
        assert crescendo([]) == []


class TestTranspose:
    def test_up_semitones(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)]
        result = transpose(notes, 7)  # up a fifth
        midis = [n.midi for n in result]
        assert midis[0] == 60 + 7  # C4 + P5 = G4 = 67

    def test_down_semitones(self):
        notes = [Note("A", 4, 1.0)]
        result = transpose(notes, -12)  # down an octave
        assert result[0].midi == 69 - 12  # A3

    def test_rest_preserved(self):
        notes = [Note.rest(1.0)]
        result = transpose(notes, 5)
        assert result[0].pitch is None

    def test_midi_int_pitch(self):
        notes = [Note(pitch=60, duration=1.0)]  # C4 as MIDI int
        result = transpose(notes, 4)
        assert result[0].midi == 64  # E4


class TestHumanize:
    def test_output_length_unchanged(self):
        notes = [Note("C", 4, 1.0, velocity=0.7) for _ in range(8)]
        result = humanize(notes)
        assert len(result) == 8

    def test_velocities_vary(self):
        notes = [Note("C", 4, 1.0, velocity=0.7) for _ in range(20)]
        result = humanize(notes, vel_spread=0.1)
        vels = [n.velocity for n in result]
        # With spread=0.1, not all velocities should be identical
        assert len(set(round(v, 4) for v in vels)) > 1

    def test_velocity_clamped(self):
        notes = [Note("C", 4, 1.0, velocity=0.05) for _ in range(10)]
        result = humanize(notes, vel_spread=0.5)
        assert all(n.velocity >= 0.05 for n in result)


class TestRepeat:
    def test_repeats_n_times(self):
        events = [Note("C", 4), Note("E", 4)]
        result = repeat(events, 3)
        assert len(result) == 6

    def test_zero_repeats(self):
        result = repeat([Note("C", 4)], 0)
        assert result == []
