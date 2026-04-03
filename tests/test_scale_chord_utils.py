"""Tests for scale_info, chord_extensions, merge_tracks."""

from code_music import Note
from code_music.theory import chord_extensions, merge_tracks, scale_info


class TestScaleInfo:
    def test_major(self):
        info = scale_info("major", "C")
        assert info["name"] == "major"
        assert info["root"] == "C"
        assert "C" in info["notes"]
        assert len(info["intervals"]) == 7

    def test_minor(self):
        info = scale_info("minor", "A")
        assert "A" in info["notes"]

    def test_chord_fits(self):
        info = scale_info("major", "C")
        assert len(info["chord_fits"]) > 0

    def test_unknown_raises(self):
        import pytest

        with pytest.raises(ValueError):
            scale_info("imaginary")


class TestChordExtensions:
    def test_basic(self):
        notes = chord_extensions("C", "maj7", ["9"])
        assert len(notes) > 4  # base + extension

    def test_auto_tensions(self):
        notes = chord_extensions("C", "min7")
        assert len(notes) >= 3

    def test_unknown_shape_raises(self):
        import pytest

        with pytest.raises(ValueError):
            chord_extensions("C", "imaginary")

    def test_returns_notes(self):
        notes = chord_extensions("G", "dom7", ["9", "13"])
        assert all(isinstance(n, Note) for n in notes)


class TestMergeTracks:
    def test_basic(self):
        a = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        b = [Note("D", 5, 1.0), Note("F", 5, 1.0)]
        merged = merge_tracks([a, b])
        assert len(merged) == 4
        assert merged[0].pitch == "C"
        assert merged[1].pitch == "D"

    def test_unequal_lengths(self):
        a = [Note("C", 5, 1.0)]
        b = [Note("D", 5, 1.0), Note("E", 5, 1.0)]
        merged = merge_tracks([a, b])
        assert len(merged) == 3

    def test_empty(self):
        assert merge_tracks([]) == []
