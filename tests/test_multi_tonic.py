"""Tests for v64.0 — tone_row, row_transforms, interval_vector."""

from code_music.theory import interval_vector, row_transforms, tone_row


class TestToneRow:
    def test_random_row_has_12_elements(self):
        row = tone_row(seed=42)
        assert len(row) == 12

    def test_all_pitch_classes_present(self):
        row = tone_row(seed=42)
        assert sorted(row) == list(range(12))

    def test_deterministic(self):
        assert tone_row(seed=99) == tone_row(seed=99)

    def test_different_seeds_differ(self):
        assert tone_row(seed=1) != tone_row(seed=2)

    def test_from_pitches(self):
        row = tone_row(["C", "D", "E"])
        assert row == [0, 2, 4]


class TestRowTransforms:
    def test_has_four_forms(self):
        row = tone_row(seed=42)
        t = row_transforms(row)
        assert "prime" in t
        assert "retrograde" in t
        assert "inversion" in t
        assert "retrograde_inversion" in t

    def test_prime_equals_original(self):
        row = tone_row(seed=42)
        assert row_transforms(row)["prime"] == row

    def test_retrograde_is_reversed(self):
        row = tone_row(seed=42)
        assert row_transforms(row)["retrograde"] == list(reversed(row))

    def test_inversion_starts_on_same_note(self):
        row = tone_row(seed=42)
        t = row_transforms(row)
        assert t["inversion"][0] == row[0]

    def test_all_forms_have_12_notes(self):
        row = tone_row(seed=42)
        for form in row_transforms(row).values():
            assert len(form) == 12


class TestIntervalVector:
    def test_major_triad(self):
        # C major: {0, 4, 7}
        iv = interval_vector([0, 4, 7])
        assert len(iv) == 6
        assert sum(iv) == 3  # 3 pairs from 3 notes

    def test_chromatic_cluster(self):
        # {0, 1, 2} — three adjacent semitones
        iv = interval_vector([0, 1, 2])
        assert iv[0] == 2  # two instances of ic1
        assert iv[1] == 1  # one instance of ic2

    def test_single_note(self):
        iv = interval_vector([0])
        assert iv == [0, 0, 0, 0, 0, 0]

    def test_all_12(self):
        iv = interval_vector(list(range(12)))
        assert sum(iv) == 66  # C(12,2) = 66 pairs
