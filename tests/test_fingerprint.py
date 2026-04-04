"""Tests for v61.0 — song_fingerprint, song_similarity."""

from code_music.engine import Note
from code_music.theory import song_fingerprint, song_similarity


class TestSongFingerprint:
    def test_has_pitch_histogram(self):
        fp = song_fingerprint([("C", "maj"), ("G", "dom7")])
        assert len(fp["pitch_histogram"]) == 12

    def test_histogram_sums_to_1(self):
        fp = song_fingerprint([("C", "maj"), ("G", "dom7"), ("C", "maj")])
        assert abs(sum(fp["pitch_histogram"]) - 1.0) < 0.01

    def test_quality_dist(self):
        fp = song_fingerprint([("C", "maj"), ("G", "dom7")])
        assert "maj" in fp["quality_dist"]
        assert "dom7" in fp["quality_dist"]

    def test_chord_count(self):
        fp = song_fingerprint([("C", "maj")] * 5)
        assert fp["chord_count"] == 5

    def test_with_melody(self):
        notes = [Note("C", 5, 0.5), Note("E", 5, 0.5), Note("G", 5, 0.5)]
        fp = song_fingerprint([("C", "maj")], notes=notes)
        assert fp["avg_interval"] > 0
        assert fp["rhythm_density"] > 0

    def test_without_melody(self):
        fp = song_fingerprint([("C", "maj")])
        assert fp["avg_interval"] == 0.0
        assert fp["rhythm_density"] == 0.0


class TestSongSimilarity:
    def test_identical(self):
        fp = song_fingerprint([("C", "maj"), ("G", "dom7")])
        assert song_similarity(fp, fp) == 1.0

    def test_range(self):
        fp_a = song_fingerprint([("C", "maj")])
        fp_b = song_fingerprint([("F#", "dim")])
        score = song_similarity(fp_a, fp_b)
        assert 0.0 <= score <= 1.0

    def test_similar_keys_higher(self):
        fp_c = song_fingerprint([("C", "maj"), ("F", "maj"), ("G", "dom7")])
        fp_g = song_fingerprint([("G", "maj"), ("C", "maj"), ("D", "dom7")])
        fp_fs = song_fingerprint([("F#", "dim"), ("Bb", "aug"), ("Eb", "min")])
        # C and G progressions should be more similar than C and F#
        sim_cg = song_similarity(fp_c, fp_g)
        sim_cfs = song_similarity(fp_c, fp_fs)
        assert sim_cg >= sim_cfs
