"""Tests for voice_progression() — chord voicing AI."""

from code_music.theory import voice_progression


class TestVoiceProgression:
    """Voicing AI produces correct style-specific voicings."""

    def _prog(self):
        return [("D", "min7"), ("G", "dom7"), ("C", "maj7")]

    def test_classical_produces_voicings(self):
        v = voice_progression(self._prog(), style="classical")
        assert len(v) == 3
        for chord in v:
            assert len(chord) >= 3

    def test_classical_smooth_movement(self):
        v = voice_progression(self._prog(), style="classical")
        # Check that voice movement between chords is small
        for i in range(1, len(v)):
            for n1, n2 in zip(v[i - 1], v[i]):
                if n1.pitch and n2.pitch:
                    from code_music.theory._core import _semi

                    abs1 = _semi(str(n1.pitch)) + n1.octave * 12
                    abs2 = _semi(str(n2.pitch)) + n2.octave * 12
                    assert abs(abs1 - abs2) <= 12  # no voice moves more than an octave

    def test_jazz_rootless_alternates(self):
        v = voice_progression(self._prog(), style="jazz_rootless")
        assert len(v) == 3
        # Each voicing should have notes (rootless = 3-4 notes)
        for chord in v:
            assert len(chord) >= 3

    def test_quartal_stacked_fourths(self):
        v = voice_progression(self._prog(), style="quartal")
        assert len(v) == 3
        for chord in v:
            assert len(chord) == 4  # 4 layers of stacked 4ths

    def test_drop2_voicings(self):
        v = voice_progression(self._prog(), style="drop2")
        assert len(v) == 3
        for chord in v:
            assert len(chord) >= 3

    def test_shell_voicings_minimal(self):
        v = voice_progression(self._prog(), style="shell")
        assert len(v) == 3
        for chord in v:
            assert len(chord) == 2  # root + guide tone

    def test_empty_progression(self):
        assert voice_progression([]) == []

    def test_single_chord(self):
        v = voice_progression([("C", "maj")])
        assert len(v) == 1
        assert len(v[0]) >= 3

    def test_triad_progression(self):
        prog = [("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")]
        v = voice_progression(prog, style="classical")
        assert len(v) == 4

    def test_invalid_style_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Unknown voicing style"):
            voice_progression([("C", "maj")], style="nonexistent")

    def test_custom_octave(self):
        v = voice_progression(self._prog(), style="shell", octave=4)
        assert len(v) == 3
        for chord in v:
            for n in chord:
                assert n.octave >= 4

    def test_custom_duration(self):
        v = voice_progression(self._prog(), style="shell", duration=2.0)
        for chord in v:
            for n in chord:
                assert n.duration == 2.0

    def test_all_styles_produce_output(self):
        for style in ["classical", "jazz_rootless", "quartal", "drop2", "shell"]:
            v = voice_progression(self._prog(), style=style)
            assert len(v) == 3, f"{style} failed"
            for chord in v:
                assert len(chord) > 0, f"{style} produced empty chord"
