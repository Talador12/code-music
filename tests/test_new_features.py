"""Tests for: suggest_progression, Karplus-Strong synthesis, suggest_progression moods."""

import numpy as np
import pytest

from code_music.engine import Chord, Note, Song, Track, suggest_progression
from code_music.synth import Synth

SR = 22050


# ---------------------------------------------------------------------------
# suggest_progression
# ---------------------------------------------------------------------------


class TestSuggestProgression:
    def test_returns_four_chords(self):
        prog = suggest_progression("C", mood="happy")
        assert len(prog) == 4

    def test_all_chords(self):
        prog = suggest_progression("C", mood="happy")
        assert all(isinstance(c, Chord) for c in prog)

    def test_duration_applied(self):
        prog = suggest_progression("C", mood="happy", duration=2.0)
        assert all(c.duration == 2.0 for c in prog)

    def test_velocity_applied(self):
        prog = suggest_progression("C", mood="chill", velocity=0.42)
        assert all(abs(c.velocity - 0.42) < 0.01 for c in prog)

    def test_all_moods_work(self):
        moods = ["happy", "sad", "tense", "dreamy", "epic", "groovy", "dark", "chill"]
        for mood in moods:
            prog = suggest_progression("A", mood=mood)
            assert len(prog) == 4, f"mood={mood} gave wrong count"

    def test_unknown_mood_raises(self):
        with pytest.raises(ValueError, match="Unknown mood"):
            suggest_progression("C", mood="confused")

    def test_variation_changes_chords(self):
        p0 = suggest_progression("C", mood="happy", variation=0)
        p1 = suggest_progression("C", mood="happy", variation=1)
        # Different variations should produce different progressions
        assert [c.root for c in p0] != [c.root for c in p1]

    def test_different_roots(self):
        # Same mood, different roots should give different chord roots
        pc = suggest_progression("C", mood="sad")
        pg = suggest_progression("G", mood="sad")
        assert [c.root for c in pc] != [c.root for c in pg]

    def test_usable_in_track(self):
        song = Song(bpm=120, sample_rate=SR)
        tr = song.add_track(Track(instrument="pad"))
        prog = suggest_progression("A", mood="dark", duration=2.0)
        tr.extend(prog)
        samples = Synth(SR).render_song(song)
        assert np.max(np.abs(samples)) > 0.0


# ---------------------------------------------------------------------------
# Karplus-Strong synthesis
# ---------------------------------------------------------------------------


class TestKarplusStrong:
    def _render(self, instrument: str, pitch: str = "A", octave: int = 3) -> np.ndarray:
        song = Song(bpm=120, sample_rate=SR)
        tr = song.add_track(Track(instrument=instrument))
        tr.add(Note(pitch, octave, duration=0.5))
        return Synth(SR).render_song(song)

    def test_guitar_ks_renders(self):
        samples = self._render("guitar_ks")
        assert samples.shape[0] > 0
        assert np.max(np.abs(samples)) > 0.0

    def test_banjo_ks_renders(self):
        samples = self._render("banjo_ks")
        assert np.max(np.abs(samples)) > 0.0

    def test_harp_ks_renders(self):
        samples = self._render("harp_ks", octave=4)
        assert np.max(np.abs(samples)) > 0.0

    def test_sitar_ks_renders(self):
        samples = self._render("sitar_ks", octave=4)
        assert np.max(np.abs(samples)) > 0.0

    def test_koto_ks_renders(self):
        samples = self._render("koto_ks", octave=4)
        assert np.max(np.abs(samples)) > 0.0

    def test_ks_output_clamped(self):
        for inst in ("guitar_ks", "banjo_ks", "harp_ks"):
            samples = self._render(inst)
            assert np.max(np.abs(samples)) <= 1.0 + 1e-6, f"{inst} exceeded clip"

    def test_ks_differs_from_pluck(self):
        """KS synthesis should sound different from regular pluck (additive)."""
        song_ks = Song(bpm=120, sample_rate=SR)
        song_pluck = Song(bpm=120, sample_rate=SR)
        for song, inst in [(song_ks, "guitar_ks"), (song_pluck, "pluck")]:
            tr = song.add_track(Track(instrument=inst))
            tr.add(Note("A", 3, duration=0.5))
        s_ks = Synth(SR).render_song(song_ks)
        s_pluck = Synth(SR).render_song(song_pluck)
        # Different synthesis methods = different waveforms
        assert not np.allclose(s_ks, s_pluck, atol=0.01)

    def test_ks_multiple_notes(self):
        song = Song(bpm=120, sample_rate=SR)
        tr = song.add_track(Track(instrument="guitar_ks"))
        for pitch in ["E", "A", "D", "G"]:
            tr.add(Note(pitch, 3, duration=0.25))
        samples = Synth(SR).render_song(song)
        assert samples.shape[0] > 0
        assert np.max(np.abs(samples)) <= 1.0 + 1e-6
