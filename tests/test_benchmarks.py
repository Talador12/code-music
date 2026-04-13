"""Benchmark suite: generation + rendering performance baselines.

Run with: pytest tests/test_benchmarks.py -v --tb=short
These are real timing tests - they assert performance stays within bounds.
If a test fails, something got significantly slower.
"""

import time
import unittest

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    compose,
    generate_form,
    generate_full_song,
    generate_fugue,
    progression_dna,
    scale,
    style_fingerprint,
    analyze_arrangement,
)


def _timed(fn, *args, **kwargs):
    """Run fn and return (result, elapsed_seconds)."""
    t0 = time.monotonic()
    result = fn(*args, **kwargs)
    return result, time.monotonic() - t0


class TestGenerationBenchmarks(unittest.TestCase):
    """Generation functions should complete within reasonable time."""

    def test_generate_full_song_under_2s(self):
        """Full song generation (4 tracks, drums/bass/chords/melody) under 2s."""
        _, elapsed = _timed(generate_full_song, "jazz", "C", 120, seed=42)
        assert elapsed < 2.0, f"generate_full_song took {elapsed:.2f}s (limit: 2s)"

    def test_compose_under_2s(self):
        """Natural language compose under 2s."""
        _, elapsed = _timed(compose, "pop in G at 128 bpm", seed=42)
        assert elapsed < 2.0, f"compose took {elapsed:.2f}s (limit: 2s)"

    def test_generate_form_sonata_under_2s(self):
        """Sonata form (16 phrases) under 2s."""
        _, elapsed = _timed(generate_form, "sonata", "C", 120, seed=42)
        assert elapsed < 2.0, f"generate_form sonata took {elapsed:.2f}s (limit: 2s)"

    def test_generate_form_all_styles_under_5s(self):
        """All 7 form styles combined under 5s."""
        t0 = time.monotonic()
        for style in [
            "sonata",
            "rondo",
            "aaba",
            "verse_chorus",
            "binary",
            "ternary",
            "theme_variations",
        ]:
            generate_form(style, seed=42)
        elapsed = time.monotonic() - t0
        assert elapsed < 5.0, f"All form styles took {elapsed:.2f}s (limit: 5s)"

    def test_generate_fugue_under_2s(self):
        """Fugue generation (3 voices) under 2s."""
        _, elapsed = _timed(generate_fugue, voices=3, key="C", seed=42)
        assert elapsed < 2.0, f"generate_fugue took {elapsed:.2f}s (limit: 2s)"

    def test_progression_dna_under_10ms(self):
        """DNA encoding of a 12-chord progression under 10ms."""
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")] * 3
        _, elapsed = _timed(progression_dna, prog)
        assert elapsed < 0.01, f"progression_dna took {elapsed * 1000:.1f}ms (limit: 10ms)"

    def test_scale_generation_under_1ms(self):
        """Scale generation (8 notes) under 1ms."""
        _, elapsed = _timed(scale, "C", "major", octave=4, length=8)
        assert elapsed < 0.001, f"scale() took {elapsed * 1000:.2f}ms (limit: 1ms)"


class TestAnalysisBenchmarks(unittest.TestCase):
    """Analysis functions should complete quickly."""

    def _make_song(self, tracks=3, notes_per_track=32):
        song = Song(title="Bench", bpm=120, key_sig="C")
        for i in range(tracks):
            tr = song.add_track(Track(name=f"track_{i}", instrument="piano"))
            pitches = ["C", "D", "E", "F", "G", "A", "B"]
            for j in range(notes_per_track):
                tr.add(Note(pitches[j % 7], 4, 0.5))
        return song

    def test_style_fingerprint_under_500ms(self):
        """Style fingerprint of a 3-track song under 500ms."""
        song = self._make_song()
        _, elapsed = _timed(style_fingerprint, song)
        assert elapsed < 0.5, f"style_fingerprint took {elapsed * 1000:.0f}ms (limit: 500ms)"

    def test_analyze_arrangement_under_500ms(self):
        """Arrangement analysis of a 3-track song under 500ms."""
        song = self._make_song()
        _, elapsed = _timed(analyze_arrangement, song)
        assert elapsed < 0.5, f"analyze_arrangement took {elapsed * 1000:.0f}ms (limit: 500ms)"


class TestRenderBenchmarks(unittest.TestCase):
    """Rendering should be faster than realtime."""

    def test_simple_render_faster_than_realtime(self):
        """A 4-beat song renders faster than its playback duration."""
        from code_music.synth import Synth

        song = Song(title="Quick", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="sine"))
        tr.extend([Note("C", 4, 1.0)] * 4)

        synth = Synth(sample_rate=22050)
        _, elapsed = _timed(synth.render_song, song)
        duration = song.duration_sec
        assert elapsed < duration, (
            f"Render took {elapsed:.2f}s for {duration:.2f}s of audio "
            f"({duration / elapsed:.1f}x realtime, should be >1x)"
        )

    def test_multitrack_render_under_5s(self):
        """A 4-track, 16-beat song renders under 5s at 22050Hz."""
        from code_music.synth import Synth

        song = Song(title="Multi", bpm=120, sample_rate=22050)
        for name, inst in [
            ("lead", "sawtooth"),
            ("bass", "bass"),
            ("pad", "pad"),
            ("hat", "drums_hat"),
        ]:
            tr = song.add_track(Track(name=name, instrument=inst))
            tr.extend([Note("C", 4 if inst != "bass" else 2, 1.0)] * 16)

        synth = Synth(sample_rate=22050)
        _, elapsed = _timed(synth.render_song, song)
        assert elapsed < 5.0, f"Multitrack render took {elapsed:.2f}s (limit: 5s)"

    def test_chord_render_under_2s(self):
        """8 chords render under 2s at 22050Hz."""
        from code_music.synth import Synth

        song = Song(title="Chords", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="piano"))
        for root in ["C", "F", "G", "A", "D", "E", "B", "C"]:
            tr.add(Chord(root, "maj", 4, duration=2.0))

        synth = Synth(sample_rate=22050)
        _, elapsed = _timed(synth.render_song, song)
        assert elapsed < 2.0, f"Chord render took {elapsed:.2f}s (limit: 2s)"


class TestCorpusBenchmarks(unittest.TestCase):
    """Corpus-scale operations should handle the full song library."""

    def test_dna_corpus_search_100_progs_under_1s(self):
        """Search 100 progressions by DNA under 1s."""
        import random

        rng = random.Random(42)
        roots = ["C", "D", "E", "F", "G", "A", "B"]
        shapes = ["maj", "min", "dom7", "min7", "maj7"]

        corpus = []
        for i in range(100):
            length = rng.randint(4, 12)
            prog = [(rng.choice(roots), rng.choice(shapes)) for _ in range(length)]
            corpus.append((f"prog_{i}", prog))

        query = [("C", "maj"), ("G", "dom7"), ("A", "min"), ("F", "maj")]

        from code_music import find_similar_progressions_dna

        _, elapsed = _timed(find_similar_progressions_dna, query, corpus, top_k=10)
        assert elapsed < 1.0, f"100-prog DNA search took {elapsed:.2f}s (limit: 1s)"


if __name__ == "__main__":
    unittest.main()
