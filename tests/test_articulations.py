"""Tests for articulation helpers and generative functions."""

import pytest

from code_music.engine import (
    Chord,
    Note,
    chord_prog,
    generate_melody,
    legato,
    pizzicato,
    prob,
    staccato,
)


class TestStaccato:
    def test_note_shortened(self):
        notes = [Note("C", 4, 2.0)]
        result = staccato(notes, factor=0.5)
        # Should produce the sounding note + a rest
        assert len(result) == 2
        assert result[0].pitch == "C"
        assert result[0].duration == pytest.approx(1.0)
        assert result[1].pitch is None  # rest
        assert result[1].duration == pytest.approx(1.0)

    def test_rest_passthrough(self):
        notes = [Note.rest(2.0)]
        result = staccato(notes)
        assert len(result) == 1
        assert result[0].pitch is None

    def test_default_factor(self):
        notes = [Note("A", 4, 1.0)]
        result = staccato(notes)  # default 0.5
        assert result[0].duration == pytest.approx(0.5)

    def test_multiple_notes(self):
        notes = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)]
        result = staccato(notes, factor=0.3)
        # Each note becomes 2 items (sound + rest)
        assert len(result) == 6
        for i in range(0, 6, 2):
            assert result[i].pitch is not None  # sounding note
            assert result[i + 1].pitch is None  # rest


class TestLegato:
    def test_note_extended(self):
        notes = [Note("C", 4, 1.0)]
        result = legato(notes, overlap=0.15)
        assert result[0].duration == pytest.approx(1.15)

    def test_rest_passthrough(self):
        notes = [Note.rest(1.0)]
        result = legato(notes)
        assert result[0].pitch is None
        assert result[0].duration == 1.0  # rests not extended

    def test_preserves_pitch(self):
        notes = [Note("G", 5, 2.0, velocity=0.9)]
        result = legato(notes)
        assert result[0].pitch == "G"
        assert result[0].velocity == 0.9


class TestPizzicato:
    def test_very_short(self):
        notes = [Note("C", 4, 2.0)]
        result = pizzicato(notes)
        # 0.15 * 2.0 = 0.3s sounding
        assert result[0].duration == pytest.approx(0.3, abs=0.01)

    def test_produces_rest(self):
        notes = [Note("A", 4, 1.0)]
        result = pizzicato(notes)
        assert len(result) == 2
        assert result[1].pitch is None


class TestProb:
    def test_always_plays_at_p1(self):
        n = Note("C", 4, 1.0)
        for _ in range(20):
            result = prob(n, p=1.0)
            assert result is n

    def test_never_plays_at_p0(self):
        n = Note("C", 4, 1.0)
        for _ in range(20):
            result = prob(n, p=0.0)
            assert result is not n
            assert getattr(result, "pitch", None) is None

    def test_returns_rest_duration(self):
        n = Note("C", 4, 2.0)
        result = prob(n, p=0.0)
        assert getattr(result, "duration", 0) == pytest.approx(2.0)

    def test_chord_prob(self):
        c = Chord("A", "min", 4, duration=2.0)
        result = prob(c, p=1.0)
        assert result is c


class TestChordProg:
    def test_produces_correct_length(self):
        prog = chord_prog(["A", "F", "C", "G"], ["min7", "maj7", "maj", "dom7"])
        assert len(prog) == 4

    def test_chord_roots(self):
        prog = chord_prog(["C", "G"], ["maj", "min"])
        assert prog[0].root == "C"
        assert prog[1].root == "G"

    def test_duration_applied(self):
        prog = chord_prog(["A"], ["min"], duration=2.5)
        assert prog[0].duration == 2.5

    def test_velocity_applied(self):
        prog = chord_prog(["A"], ["min"], velocity=0.42)
        assert prog[0].velocity == pytest.approx(0.42)


class TestGenerateMelody:
    def test_output_is_list_of_notes(self):
        mel = generate_melody("C", seed=42)
        assert isinstance(mel, list)
        assert all(isinstance(n, Note) for n in mel)

    def test_total_duration_matches_bars(self):
        mel = generate_melody("A", bars=4, seed=0)
        total = sum(n.duration for n in mel)
        # 4 bars × 4 beats/bar = 16 beats (8th notes at 0.5 beats each)
        assert total == pytest.approx(16.0, rel=0.05)

    def test_seed_reproducibility(self):
        m1 = generate_melody("C", bars=4, seed=42)
        m2 = generate_melody("C", bars=4, seed=42)
        assert len(m1) == len(m2)
        for n1, n2 in zip(m1, m2):
            assert n1.pitch == n2.pitch
            assert n1.duration == pytest.approx(n2.duration)

    def test_different_seeds_differ(self):
        m1 = generate_melody("C", bars=4, seed=1)
        m2 = generate_melody("C", bars=4, seed=99)
        pitches1 = [n.pitch for n in m1]
        pitches2 = [n.pitch for n in m2]
        assert pitches1 != pitches2

    def test_all_modes(self):
        for mode in ["major", "minor", "pentatonic", "blues", "dorian"]:
            mel = generate_melody("D", scale_mode=mode, bars=2, seed=0)
            assert len(mel) > 0

    def test_density_zero_all_rests(self):
        mel = generate_melody("C", bars=2, density=0.0, seed=0)
        assert all(n.pitch is None for n in mel)

    def test_density_one_all_notes(self):
        mel = generate_melody("C", bars=2, density=1.0, seed=0)
        assert any(n.pitch is not None for n in mel)
