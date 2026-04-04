"""Tests for v71.0 — texture_density, thin_texture, thicken_texture."""

from code_music.engine import Note
from code_music.theory import texture_density, thicken_texture, thin_texture


class TestTextureDensity:
    def test_returns_per_note(self):
        notes = [Note("C", 5, 1.0)] * 4
        d = texture_density(notes)
        assert len(d) == 4

    def test_empty(self):
        assert texture_density([]) == []

    def test_higher_density_with_more_notes(self):
        sparse = [Note("C", 5, 4.0)]
        dense = [Note("C", 5, 0.25)] * 16
        d_sparse = texture_density(sparse)
        d_dense = texture_density(dense)
        assert d_dense[0] > d_sparse[0]


class TestThinTexture:
    def test_reduces_sounding_notes(self):
        notes = [Note("C", 5, 0.25)] * 16
        result = thin_texture(notes, target_density=0.5, seed=42)
        sounding = sum(1 for n in result if n.pitch is not None)
        assert sounding < 16

    def test_preserves_first_and_last(self):
        notes = [Note("C", 5, 0.25)] * 8
        result = thin_texture(notes, target_density=0.1, seed=42)
        assert result[0].pitch == "C"

    def test_empty(self):
        assert thin_texture([], target_density=0.5) == []


class TestThickenTexture:
    def test_adds_notes(self):
        notes = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        result = thicken_texture(notes, target_density=4.0, seed=42)
        assert len(result) > len(notes)

    def test_empty(self):
        assert thicken_texture([], target_density=2.0) == []

    def test_preserves_original_pitches(self):
        notes = [Note("G", 5, 1.0)]
        result = thicken_texture(notes, target_density=4.0, seed=42)
        assert result[0].pitch == "G"
