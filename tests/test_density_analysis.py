"""Tests for v105.0 — density_profile, density_contrast."""

from code_music.engine import Note
from code_music.theory import density_contrast, density_profile


class TestDensityProfile:
    def test_basic(self):
        notes = [Note("C", 5, 1.0)] * 4
        profile = density_profile(notes, resolution=1.0)
        assert len(profile) == 4
        assert all(v == 1.0 for v in profile)

    def test_rests_not_counted(self):
        notes = [Note("C", 5, 1.0), Note.rest(1.0), Note("E", 5, 1.0), Note.rest(1.0)]
        profile = density_profile(notes, resolution=1.0)
        assert profile[0] == 1.0
        assert profile[1] == 0.0

    def test_empty(self):
        assert density_profile([]) == []

    def test_finer_resolution(self):
        notes = [Note("C", 5, 0.5)] * 8  # 4 beats total
        profile = density_profile(notes, resolution=0.5)
        assert len(profile) == 8


class TestDensityContrast:
    def test_builds(self):
        # First half sparse, second half dense
        first = [Note("C", 5, 2.0)]  # 1 note, 2 beats
        second = [Note("C", 5, 0.25)] * 8  # 8 notes, 2 beats
        ratio = density_contrast(first + second)
        assert ratio > 1.0

    def test_winds_down(self):
        first = [Note("C", 5, 0.25)] * 8
        second = [Note("C", 5, 2.0)]
        ratio = density_contrast(first + second)
        assert ratio < 1.0

    def test_steady(self):
        notes = [Note("C", 5, 0.5)] * 8
        ratio = density_contrast(notes)
        assert abs(ratio - 1.0) < 0.1

    def test_empty(self):
        assert density_contrast([]) == 1.0
