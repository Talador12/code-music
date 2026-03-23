"""Tests for pan, swing, and per-track effect wiring in Song render."""

import numpy as np

from code_music.engine import Note, Song, Track
from code_music.synth import Synth

SR = 22050


class TestPanning:
    def _song_with_pan(self, pan_val: float) -> np.ndarray:
        song = Song(bpm=120, sample_rate=SR)
        tr = song.add_track(Track(instrument="sine", pan=pan_val))
        tr.add(Note("A", 4, duration=1.0))
        return Synth(SR).render_song(song)

    def test_center_pan_is_equal_power(self):
        out = self._song_with_pan(0.0)
        np.testing.assert_allclose(
            np.mean(np.abs(out[:, 0])),
            np.mean(np.abs(out[:, 1])),
            rtol=0.01,
        )

    def test_left_pan_dominant_left(self):
        out = self._song_with_pan(-0.9)
        assert np.mean(np.abs(out[:, 0])) > np.mean(np.abs(out[:, 1]))

    def test_right_pan_dominant_right(self):
        out = self._song_with_pan(0.9)
        assert np.mean(np.abs(out[:, 1])) > np.mean(np.abs(out[:, 0]))


class TestSwing:
    def test_swing_does_not_crash(self):
        song = Song(bpm=120, sample_rate=SR)
        tr = song.add_track(Track(instrument="pluck", swing=0.5))
        tr.extend([Note("C", 4, 0.5)] * 8)
        out = Synth(SR).render_song(song)
        assert out.shape[0] > 0

    def test_swing_zero_vs_nonzero_differ(self):
        """Swing 0 and swing 0.5 should produce different output."""

        def render(swing):
            song = Song(bpm=120, sample_rate=SR)
            tr = song.add_track(Track(instrument="sine", swing=swing))
            tr.extend([Note("A", 4, 0.5)] * 8)
            return Synth(SR).render_song(song)

        straight = render(0.0)
        swung = render(0.5)
        assert not np.allclose(straight, swung)


class TestEffectsHook:
    def test_effects_dict_applied(self):
        """A track effect in song._effects should change its output."""
        song = Song(bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="mel", instrument="sine"))
        tr.add(Note("A", 4, duration=2.0))

        # Apply a zeroing effect — should silence the track
        song._effects = {"mel": lambda s, sr: np.zeros_like(s)}
        silenced = Synth(SR).render_song(song)

        assert np.max(np.abs(silenced)) < 0.01

    def test_bad_effect_does_not_crash(self):
        """A buggy effect should be silently skipped, not crash render."""
        song = Song(bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="mel", instrument="sine"))
        tr.add(Note("A", 4, duration=1.0))
        song._effects = {"mel": lambda s, sr: 1 / 0}  # will raise ZeroDivisionError
        out = Synth(SR).render_song(song)  # should not raise
        assert out.shape[0] > 0
