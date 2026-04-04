"""Tests for v103.0 — morph_chord, chord_interpolation."""

from code_music.theory import chord_interpolation, morph_chord


class TestMorphChord:
    def test_returns_steps(self):
        result = morph_chord(("C", "maj"), ("G", "maj"), steps=4)
        assert len(result) == 5  # 4 intermediates + 1 end

    def test_first_is_source(self):
        result = morph_chord(("C", "maj"), ("G", "maj"), steps=2)
        pitches = [n.pitch for n in result[0]]
        assert "C" in pitches

    def test_last_is_target(self):
        result = morph_chord(("C", "maj"), ("G", "maj"), steps=2)
        pitches = [n.pitch for n in result[-1]]
        assert "G" in pitches

    def test_zero_steps(self):
        result = morph_chord(("C", "maj"), ("G", "maj"), steps=0)
        assert len(result) == 1


class TestChordInterpolation:
    def test_inserts_intermediates(self):
        prog = [("C", "maj"), ("G", "maj")]
        result = chord_interpolation(prog, steps_between=2)
        assert len(result) > 2

    def test_single_chord(self):
        prog = [("C", "maj")]
        result = chord_interpolation(prog)
        assert len(result) == 1

    def test_ends_on_last_chord(self):
        prog = [("C", "maj"), ("F", "maj")]
        result = chord_interpolation(prog, steps_between=2)
        last_pitches = [n.pitch for n in result[-1]]
        assert "F" in last_pitches
