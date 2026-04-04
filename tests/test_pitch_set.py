"""Tests for v104.0 — pc_set, pc_union, pc_intersection, pc_complement, transpose_set."""

from code_music.theory import pc_complement, pc_intersection, pc_set, pc_union, transpose_set


class TestPcSet:
    def test_basic(self):
        assert pc_set(["C", "E", "G"]) == {0, 4, 7}

    def test_duplicates(self):
        assert len(pc_set(["C", "C", "E"])) == 2


class TestPcUnion:
    def test_basic(self):
        result = pc_union(["C", "E"], ["G", "Bb"])
        assert "C" in result and "G" in result and "Bb" in result

    def test_overlap(self):
        result = pc_union(["C", "E"], ["E", "G"])
        assert len(result) == 3  # C, E, G (E not duplicated)


class TestPcIntersection:
    def test_basic(self):
        result = pc_intersection(["C", "E", "G"], ["E", "G", "B"])
        assert "E" in result and "G" in result
        assert "C" not in result

    def test_no_overlap(self):
        result = pc_intersection(["C"], ["F#"])
        assert result == []


class TestPcComplement:
    def test_major_triad(self):
        comp = pc_complement(["C", "E", "G"])
        assert len(comp) == 9  # 12 - 3
        assert "C" not in comp

    def test_full_chromatic(self):
        all_notes = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
        assert pc_complement(all_notes) == []


class TestTransposeSet:
    def test_up_semitone(self):
        result = transpose_set(["C", "E", "G"], 1)
        assert result == ["C#", "F", "Ab"]

    def test_identity(self):
        result = transpose_set(["C", "E"], 0)
        assert result == ["C", "E"]

    def test_octave_wraps(self):
        result = transpose_set(["B"], 1)
        assert result == ["C"]
