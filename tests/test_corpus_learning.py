"""Tests for v101.0 — train_style_from_corpus, continue_in_style."""

from code_music.theory import continue_in_style, train_style_from_corpus


class TestTrainStyleFromCorpus:
    def test_returns_style_dict(self):
        progs = [[("C", "maj"), ("G", "dom7"), ("C", "maj")]] * 5
        style = train_style_from_corpus(progs)
        assert "matrix" in style
        assert "root_freq" in style
        assert "avg_length" in style
        assert style["corpus_size"] == 5

    def test_empty_corpus(self):
        style = train_style_from_corpus([])
        assert style["corpus_size"] == 0


class TestContinueInStyle:
    def test_generates_progression(self):
        progs = [[("C", "maj"), ("G", "dom7"), ("C", "maj")]] * 10
        style = train_style_from_corpus(progs)
        result = continue_in_style(style, length=8, seed=42)
        assert len(result) == 8

    def test_deterministic(self):
        progs = [[("C", "maj"), ("F", "maj"), ("G", "dom7")]] * 5
        style = train_style_from_corpus(progs)
        a = continue_in_style(style, length=4, seed=99)
        b = continue_in_style(style, length=4, seed=99)
        assert a == b
