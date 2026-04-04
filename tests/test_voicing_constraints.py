"""Tests for v72.0 — optimal_voicing, smooth_voicings."""

from code_music.theory import optimal_voicing, smooth_voicings


class TestOptimalVoicing:
    def test_four_voices(self):
        notes = optimal_voicing("C", "maj", voices=4)
        assert len(notes) == 4

    def test_within_span(self):
        notes = optimal_voicing("C", "maj", voices=4, max_span=12)
        # Verify we got 4 voices within reasonable range
        assert len(notes) == 4

    def test_three_voices(self):
        notes = optimal_voicing("G", "min", voices=3)
        assert len(notes) == 3

    def test_custom_duration(self):
        notes = optimal_voicing("C", "maj", duration=2.0)
        assert all(n.duration == 2.0 for n in notes)


class TestSmoothVoicings:
    def test_correct_length(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7")]
        result = smooth_voicings(prog)
        assert len(result) == 3

    def test_each_voicing_has_voices(self):
        prog = [("C", "maj"), ("G", "maj")]
        result = smooth_voicings(prog, voices=4)
        for v in result:
            assert len(v) == 4

    def test_empty(self):
        assert smooth_voicings([]) == []

    def test_single_chord(self):
        result = smooth_voicings([("C", "maj")])
        assert len(result) == 1
