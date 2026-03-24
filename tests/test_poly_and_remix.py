"""Tests for PolyphonicTrack and remix()."""


import numpy as np
import pytest

from code_music.engine import (
    Chord,
    Note,
    PolyphonicTrack,
    Song,
    Track,
    remix,
)
from code_music.synth import Synth

SR = 22050


class TestPolyphonicTrack:
    def _poly_song(self) -> tuple[Song, PolyphonicTrack]:
        song = Song(bpm=120, sample_rate=SR)
        pt = song.add_polytrack(PolyphonicTrack(name="piano", instrument="piano", volume=0.8))
        return song, pt

    def test_add_returns_self(self):
        _, pt = self._poly_song()
        assert pt.add(Note("C", 4, 1.0), at=0.0) is pt

    def test_total_beats_single_note(self):
        _, pt = self._poly_song()
        pt.add(Note("C", 4, 2.0), at=1.0)
        assert pt.total_beats == pytest.approx(3.0)

    def test_total_beats_simultaneous(self):
        _, pt = self._poly_song()
        pt.add(Note("C", 4, 1.0), at=0.0)
        pt.add(Note("E", 4, 1.0), at=0.0)  # same time
        pt.add(Note("G", 4, 1.0), at=0.0)
        assert pt.total_beats == pytest.approx(1.0)

    def test_total_beats_staggered(self):
        _, pt = self._poly_song()
        pt.add(Note("C", 4, 1.0), at=0.0)
        pt.add(Note("E", 4, 1.0), at=2.0)
        assert pt.total_beats == pytest.approx(3.0)

    def test_add_chord(self):
        _, pt = self._poly_song()
        c = Chord("C", "maj", 4, duration=2.0)
        pt.add_chord(c, at=0.0)
        assert len(pt.events) == 3  # 3 notes in major chord
        assert all(at == 0.0 for _, at in pt.events)

    def test_song_total_beats_includes_poly(self):
        song, pt = self._poly_song()
        pt.add(Note("C", 4, 4.0), at=2.0)
        # poly track goes to beat 6.0, no seq tracks
        assert song.total_beats == pytest.approx(6.0)

    def test_poly_only_song_renders(self):
        song, pt = self._poly_song()
        pt.add(Note("C", 4, 1.0), at=0.0)
        pt.add(Note("E", 4, 1.0), at=0.0)
        pt.add(Note("G", 4, 1.0), at=0.0)
        samples = Synth(SR).render_song(song)
        assert samples.shape[1] == 2
        assert np.max(np.abs(samples)) > 0.1  # actually produced sound

    def test_notes_sound_simultaneously(self):
        """Two simultaneous notes should produce more energy than one."""
        song1, pt1 = self._poly_song()
        pt1.add(Note("C", 4, 1.0), at=0.0)
        s1 = Synth(SR).render_song(song1)

        song2, pt2 = self._poly_song()
        pt2.add(Note("C", 4, 1.0), at=0.0)
        pt2.add(Note("E", 4, 1.0), at=0.0)
        s2 = Synth(SR).render_song(song2)

        # Both normalise to ~same peak, but before norm chord has more energy
        # Test that waveforms differ
        min_len = min(len(s1), len(s2))
        assert not np.allclose(s1[:min_len], s2[:min_len], atol=0.01)

    def test_note_at_offset(self):
        """Note placed at beat 2 should be silent for the first 2 beats."""
        song, pt = self._poly_song()
        pt.add(Note("A", 4, 1.0), at=2.0)
        samples = Synth(SR).render_song(song)
        beat_samples = int(2.0 * 60.0 / 120.0 * SR)
        # First 2 beats minus buffer should be silent
        silent_region = samples[: beat_samples - 100]
        assert np.max(np.abs(silent_region)) < 0.01

    def test_mixed_seq_and_poly(self):
        """Song can mix regular Track and PolyphonicTrack."""
        song = Song(bpm=120, sample_rate=SR)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("G", 4, 2.0))
        pt = song.add_polytrack(PolyphonicTrack(instrument="piano"))
        pt.add(Note("C", 4, 2.0), at=0.0)
        pt.add(Note("E", 4, 2.0), at=0.0)
        samples = Synth(SR).render_song(song)
        assert np.max(np.abs(samples)) > 0.1

    def test_pan_applied(self):
        song_l = Song(bpm=120, sample_rate=SR)
        pt_l = song_l.add_polytrack(PolyphonicTrack(instrument="piano", pan=-1.0))
        pt_l.add(Note("A", 4, 1.0), at=0.0)
        sl = Synth(SR).render_song(song_l)

        song_r = Song(bpm=120, sample_rate=SR)
        pt_r = song_r.add_polytrack(PolyphonicTrack(instrument="piano", pan=1.0))
        pt_r.add(Note("A", 4, 1.0), at=0.0)
        sr = Synth(SR).render_song(song_r)

        # Left-panned: L > R
        assert np.mean(np.abs(sl[:, 0])) > np.mean(np.abs(sl[:, 1]))
        # Right-panned: R > L
        assert np.mean(np.abs(sr[:, 1])) > np.mean(np.abs(sr[:, 0]))


class TestRemix:
    def _base_song(self) -> Song:
        song = Song(title="Base", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(instrument="piano"))
        tr.add(Note("C", 4, 1.0))
        tr.add(Note("E", 4, 1.0))
        tr.add(Chord("G", "maj", 3, duration=2.0))
        return song

    def test_bpm_scaled(self):
        song = self._base_song()
        r = remix(song, bpm_factor=1.5)
        assert r.bpm == pytest.approx(180.0)

    def test_bpm_unchanged_when_factor_one(self):
        song = self._base_song()
        r = remix(song)
        assert r.bpm == pytest.approx(song.bpm)

    def test_semitone_transpose_up(self):
        song = self._base_song()
        r = remix(song, semitones=7)  # up a fifth
        orig_notes = [
            b.event for b in song.tracks[0].beats if isinstance(b.event, Note) and b.event.midi
        ]
        remix_notes = [
            b.event for b in r.tracks[0].beats if isinstance(b.event, Note) and b.event.midi
        ]
        for on, rn in zip(orig_notes, remix_notes):
            assert rn.midi == on.midi + 7

    def test_semitone_transpose_down(self):
        song = self._base_song()
        r = remix(song, semitones=-5)
        orig = [b.event for b in song.tracks[0].beats if isinstance(b.event, Note) and b.event.midi]
        remixed = [b.event for b in r.tracks[0].beats if isinstance(b.event, Note) and b.event.midi]
        for on, rn in zip(orig, remixed):
            assert rn.midi == on.midi - 5

    def test_chord_transposed(self):
        song = self._base_song()
        r = remix(song, semitones=3)
        # G maj chord should become Bb maj (or equivalent)
        chord_beat = next(b for b in r.tracks[0].beats if isinstance(b.event, Chord))
        orig_chord = next(b for b in song.tracks[0].beats if isinstance(b.event, Chord))
        # Just verify root changed
        assert (
            chord_beat.event.root != orig_chord.event.root
            or chord_beat.event.octave != orig_chord.event.octave
        )

    def test_title(self):
        song = self._base_song()
        r = remix(song, title="Club Mix")
        assert r.title == "Club Mix"

    def test_default_title_adds_remix(self):
        song = self._base_song()
        r = remix(song)
        assert "Remix" in r.title

    def test_zero_transpose_preserves_notes(self):
        song = self._base_song()
        r = remix(song, semitones=0)
        orig_midis = [
            b.event.midi for b in song.tracks[0].beats if isinstance(b.event, Note) and b.event.midi
        ]
        remix_midis = [
            b.event.midi for b in r.tracks[0].beats if isinstance(b.event, Note) and b.event.midi
        ]
        assert orig_midis == remix_midis

    def test_sample_rate_preserved(self):
        song = self._base_song()
        r = remix(song)
        assert r.sample_rate == song.sample_rate

    def test_renders_without_error(self):
        song = self._base_song()
        r = remix(song, semitones=4, bpm_factor=0.9)
        samples = Synth(SR).render_song(r)
        assert samples.shape[0] > 0
        assert np.max(np.abs(samples)) <= 1.0 + 1e-6
