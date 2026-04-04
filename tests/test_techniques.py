"""Tests for v84.0 — hammer_on, pull_off, slide, palm_mute."""

from code_music.engine import Note
from code_music.theory import hammer_on, palm_mute, pull_off, slide


class TestHammerOn:
    def test_two_notes(self):
        result = hammer_on(Note("E", 4, 0.5), Note("G", 4, 0.5))
        assert len(result) == 2

    def test_second_quieter(self):
        a = Note("E", 4, 0.5, velocity=100)
        b = Note("G", 4, 0.5, velocity=100)
        result = hammer_on(a, b)
        assert result[1].velocity < result[0].velocity

    def test_first_unchanged(self):
        a = Note("E", 4, 0.5, velocity=80)
        result = hammer_on(a, Note("G", 4, 0.5))
        assert result[0].velocity == 80


class TestPullOff:
    def test_two_notes(self):
        result = pull_off(Note("G", 4, 0.5), Note("E", 4, 0.5))
        assert len(result) == 2

    def test_second_quieter(self):
        result = pull_off(Note("G", 4, 0.5, velocity=100), Note("E", 4, 0.5, velocity=100))
        assert result[1].velocity < result[0].velocity


class TestSlide:
    def test_includes_intermediates(self):
        result = slide(Note("C", 4, 1.0), Note("G", 4, 1.0), steps=3)
        assert len(result) > 2

    def test_ends_on_target(self):
        result = slide(Note("C", 4, 1.0), Note("G", 4, 1.0))
        assert result[-1].pitch == "G"

    def test_rest_passthrough(self):
        result = slide(Note.rest(1.0), Note("G", 4, 1.0))
        assert len(result) == 2


class TestPalmMute:
    def test_shortens_notes(self):
        notes = [Note("E", 3, 1.0)]
        result = palm_mute(notes, decay_factor=0.3)
        assert result[0].duration < 1.0

    def test_adds_rests(self):
        notes = [Note("E", 3, 1.0)]
        result = palm_mute(notes, decay_factor=0.3)
        assert len(result) == 2  # short note + rest
        assert result[1].pitch is None

    def test_total_duration_preserved(self):
        notes = [Note("E", 3, 2.0)]
        result = palm_mute(notes, decay_factor=0.5)
        total = sum(n.duration for n in result)
        assert abs(total - 2.0) < 1e-9

    def test_rest_passthrough(self):
        notes = [Note.rest(1.0)]
        result = palm_mute(notes)
        assert len(result) == 1
