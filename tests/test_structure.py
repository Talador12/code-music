"""Tests for v65.0 — section_similarity_matrix, detect_sections, label_form."""

from code_music.theory import detect_sections, label_form, section_similarity_matrix


class TestSectionSimilarityMatrix:
    def test_square_matrix(self):
        prog = [("C", "maj")] * 8
        matrix = section_similarity_matrix(prog, bars_per_section=4)
        assert len(matrix) == 2
        assert len(matrix[0]) == 2

    def test_self_similarity_is_1(self):
        prog = [("C", "maj"), ("G", "dom7"), ("C", "maj"), ("G", "dom7")]
        matrix = section_similarity_matrix(prog, bars_per_section=2)
        for i in range(len(matrix)):
            assert matrix[i][i] == 1.0

    def test_identical_sections_high(self):
        prog = [("C", "maj"), ("G", "dom7")] * 4
        matrix = section_similarity_matrix(prog, bars_per_section=2)
        assert matrix[0][1] == 1.0  # same content


class TestDetectSections:
    def test_repeated_sections_same_label(self):
        prog = [("C", "maj")] * 4 + [("G", "dom7")] * 4 + [("C", "maj")] * 4
        sections = detect_sections(prog, bars_per_section=4)
        assert sections[0]["label"] == sections[2]["label"]  # A...A

    def test_different_sections_different_labels(self):
        prog = [("C", "maj")] * 4 + [("F#", "dim")] * 4
        sections = detect_sections(prog, bars_per_section=4)
        assert sections[0]["label"] != sections[1]["label"]

    def test_start_end_positions(self):
        prog = [("C", "maj")] * 8
        sections = detect_sections(prog, bars_per_section=4)
        assert sections[0]["start"] == 0
        assert sections[0]["end"] == 4
        assert sections[1]["start"] == 4


class TestLabelForm:
    def test_aaba(self):
        a = [("C", "maj")] * 4
        b = [("F#", "dim"), ("Eb", "aug"), ("Bb", "min"), ("Ab", "dom7")]
        prog = a + a + b + a
        form = label_form(prog, bars_per_section=4)
        assert form == "AABA"

    def test_abab(self):
        a = [("C", "maj")] * 4
        b = [("F#", "dim")] * 4
        prog = a + b + a + b
        form = label_form(prog, bars_per_section=4)
        assert form == "ABAB"
