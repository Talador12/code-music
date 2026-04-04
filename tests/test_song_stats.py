"""Tests for v77.0 — corpus_stats, key_distribution, tempo_distribution."""

from code_music.theory import corpus_stats, key_distribution, tempo_distribution


class TestCorpusStats:
    def test_basic(self):
        progs = [
            [("C", "maj"), ("G", "dom7")],
            [("A", "min"), ("D", "min7"), ("G", "dom7")],
        ]
        stats = corpus_stats(progs)
        assert stats["total_progressions"] == 2
        assert stats["total_chords"] == 5
        assert stats["avg_length"] == 2.5

    def test_empty(self):
        stats = corpus_stats([])
        assert stats["total_progressions"] == 0
        assert stats["total_chords"] == 0

    def test_most_common(self):
        progs = [[("C", "maj")] * 5, [("C", "maj")] * 3]
        stats = corpus_stats(progs)
        assert stats["most_common_root"] == "C"
        assert stats["most_common_shape"] == "maj"


class TestKeyDistribution:
    def test_returns_counts(self):
        progs = [
            [("C", "maj"), ("F", "maj"), ("G", "dom7")],
            [("C", "maj"), ("G", "dom7"), ("C", "maj")],
        ]
        dist = key_distribution(progs)
        assert "C" in dist
        assert dist["C"] >= 1

    def test_empty(self):
        assert key_distribution([]) == {}


class TestTempoDistribution:
    def test_basic(self):
        bpms = [120.0, 125.0, 130.0, 80.0, 85.0]
        dist = tempo_distribution(bpms, bucket_size=10)
        assert "120-130" in dist
        assert "80-90" in dist

    def test_empty(self):
        assert tempo_distribution([]) == {}

    def test_single(self):
        dist = tempo_distribution([100.0])
        assert len(dist) == 1
