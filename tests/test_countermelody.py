"""Tests for generate_countermelody() — intelligent countermelody generation."""

from code_music.engine import Note
from code_music.theory import generate_countermelody


class TestGenerateCountermelody:
    """Countermelody generator correctness and style variants."""

    def _melody(self):
        return [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0), Note("C", 6, 1.0)]

    def _prog(self):
        return [("C", "maj"), ("C", "maj")]

    def test_independent_length_matches(self):
        mel = self._melody()
        cm = generate_countermelody(mel, self._prog(), style="independent", seed=42)
        assert len(cm) == len(mel)

    def test_independent_has_pitches(self):
        mel = self._melody()
        cm = generate_countermelody(mel, self._prog(), style="independent", seed=42)
        pitched = [n for n in cm if n.pitch is not None]
        assert len(pitched) > 0

    def test_independent_differs_from_melody(self):
        mel = self._melody()
        cm = generate_countermelody(mel, self._prog(), style="independent", seed=42)
        # At least some notes should differ from the melody
        diffs = sum(1 for m, c in zip(mel, cm) if m.pitch != c.pitch)
        assert diffs > 0

    def test_descant_above_melody(self):
        mel = self._melody()
        cm = generate_countermelody(mel, self._prog(), style="descant", seed=42)
        # Descant skips weak beats (rests)
        rests = [n for n in cm if n.pitch is None]
        pitched = [n for n in cm if n.pitch is not None]
        assert len(rests) > 0  # half should be rests
        assert len(pitched) > 0

    def test_bass_counter_below_melody(self):
        mel = self._melody()
        cm = generate_countermelody(mel, self._prog(), style="bass_counter", seed=42)
        # Bass counter should be lower octave
        for n in cm:
            if n.pitch is not None:
                assert n.octave <= 4

    def test_seed_reproducibility(self):
        mel = self._melody()
        cm1 = generate_countermelody(mel, self._prog(), seed=42)
        cm2 = generate_countermelody(mel, self._prog(), seed=42)
        pitches1 = [str(n.pitch) for n in cm1]
        pitches2 = [str(n.pitch) for n in cm2]
        assert pitches1 == pitches2

    def test_different_seeds_differ(self):
        mel = self._melody()
        cm1 = generate_countermelody(mel, self._prog(), seed=1)
        cm2 = generate_countermelody(mel, self._prog(), seed=99)
        pitches1 = [str(n.pitch) for n in cm1]
        pitches2 = [str(n.pitch) for n in cm2]
        assert pitches1 != pitches2

    def test_empty_melody(self):
        assert generate_countermelody([], [("C", "maj")]) == []

    def test_rests_preserved(self):
        mel = [Note.rest(1.0), Note("C", 5, 1.0)]
        cm = generate_countermelody(mel, [("C", "maj")], seed=42)
        assert cm[0].pitch is None  # rest preserved

    def test_multi_chord_progression(self):
        mel = [
            Note("C", 5, 1.0),
            Note("D", 5, 1.0),
            Note("E", 5, 1.0),
            Note("F", 5, 1.0),
            Note("G", 5, 1.0),
            Note("A", 5, 1.0),
            Note("B", 5, 1.0),
            Note("C", 6, 1.0),
        ]
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]
        cm = generate_countermelody(mel, prog, seed=42)
        assert len(cm) == 8

    def test_minor_key(self):
        mel = [Note("A", 4, 1.0), Note("C", 5, 1.0), Note("E", 5, 1.0)]
        prog = [("A", "min")]
        cm = generate_countermelody(mel, prog, key="A", scale_name="minor", seed=42)
        assert len(cm) == 3

    def test_invalid_style_raises(self):
        import pytest

        mel = [Note("C", 5, 1.0)]
        with pytest.raises(ValueError, match="Unknown style"):
            generate_countermelody(mel, [("C", "maj")], style="nonexistent")

    def test_velocity_scaled_down(self):
        mel = [Note("C", 5, 1.0, velocity=1.0)]
        cm = generate_countermelody(mel, [("C", "maj")], style="independent", seed=42)
        # Countermelody velocity should be lower than melody
        assert cm[0].velocity < 1.0
