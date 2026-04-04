"""Tests for v60.0 — suggest_substitutions, reharmonize."""

from code_music.theory import reharmonize, suggest_substitutions


class TestSuggestSubstitutions:
    def test_dom7_has_tritone_sub(self):
        subs = suggest_substitutions("G", "dom7", key="C")
        types = [s[2] for s in subs]
        assert "tritone_sub" in types

    def test_tritone_sub_correct(self):
        subs = suggest_substitutions("G", "dom7", key="C")
        tritone = [s for s in subs if s[2] == "tritone_sub"]
        assert tritone[0][0] == "C#"  # tritone of G

    def test_v_chord_has_related_ii(self):
        subs = suggest_substitutions("G", "dom7", key="C")
        types = [s[2] for s in subs]
        assert "related_ii" in types

    def test_major_has_modal_interchange(self):
        subs = suggest_substitutions("C", "maj", key="C")
        types = [s[2] for s in subs]
        assert "modal_interchange" in types

    def test_minor_has_relative(self):
        subs = suggest_substitutions("A", "min", key="C")
        types = [s[2] for s in subs]
        assert "relative" in types

    def test_returns_tuples(self):
        subs = suggest_substitutions("C", "maj", key="C")
        for root, shape, sub_type in subs:
            assert isinstance(root, str)
            assert isinstance(shape, str)
            assert isinstance(sub_type, str)


class TestReharmonize:
    def test_jazz_adds_ii_before_v(self):
        prog = [("C", "maj"), ("G", "dom7"), ("C", "maj")]
        result = reharmonize(prog, key="C", style="jazz")
        # Should have added a ii chord before V
        assert len(result) > len(prog)

    def test_modal_swaps(self):
        prog = [("C", "maj"), ("D", "min")]
        result = reharmonize(prog, key="C", style="modal")
        assert result[0] == ("C", "min")
        assert result[1] == ("D", "maj")

    def test_simple_relative(self):
        prog = [("C", "maj")]
        result = reharmonize(prog, key="C", style="simple")
        assert result[0] == ("A", "min")  # relative minor of C

    def test_preserves_length_modal(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7")]
        result = reharmonize(prog, key="C", style="modal")
        assert len(result) == len(prog)

    def test_empty_progression(self):
        assert reharmonize([], key="C") == []
