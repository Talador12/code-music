"""Tests for the synth renderer."""

import numpy as np

from code_music.engine import Chord, Note, Song, Track
from code_music.synth import Synth


class TestSynth:
    def setup_method(self):
        self.synth = Synth(sample_rate=22050)  # lower rate = faster tests

    def test_render_single_note(self):
        song = Song(bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("A", 4, duration=1.0))
        samples = self.synth.render_song(song)
        assert samples.ndim == 2
        assert samples.shape[1] == 2  # stereo
        assert samples.shape[0] > 0

    def test_render_rest_is_silent(self):
        song = Song(bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note.rest(2.0))
        samples = self.synth.render_song(song)
        # Silence (or near-silence — no actual notes)
        assert np.max(np.abs(samples)) < 0.01

    def test_render_chord(self):
        song = Song(bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Chord("C", "maj", 4, duration=2.0))
        samples = self.synth.render_song(song)
        assert np.max(np.abs(samples)) > 0.0

    def test_output_clamped(self):
        """Rendered output should be in [-1, 1] after normalization."""
        song = Song(bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="square"))
        tr.extend([Note(p, 4, 0.5) for p in ["C", "E", "G", "B"]])
        samples = self.synth.render_song(song)
        assert np.max(np.abs(samples)) <= 1.0 + 1e-6

    def test_all_presets_render(self):
        """Every preset should render without error."""
        for preset in Synth.PRESETS:
            song = Song(bpm=160, sample_rate=22050)
            tr = song.add_track(Track(instrument=preset))
            tr.add(Note("A", 4, duration=0.5))
            samples = self.synth.render_song(song)
            assert samples.shape[0] > 0, f"preset {preset!r} produced empty output"

    def test_multi_track_mix(self):
        """Multiple tracks should sum and still be clamped."""
        song = Song(bpm=120, sample_rate=22050)
        for _ in range(4):
            tr = song.add_track(Track(instrument="sine"))
            tr.add(Note("A", 4, duration=2.0))
        samples = self.synth.render_song(song)
        assert np.max(np.abs(samples)) <= 1.0 + 1e-6
