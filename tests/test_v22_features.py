"""Tests for v2.2: bpm_map rendering, Track.split, Track.filter, AGENTS.md migration."""

from __future__ import annotations

import math

import numpy as np

from code_music.engine import Note, Song, Track, bpm_ramp, ritardando

SR = 22050


class TestBpmMapRendering:
    def test_bpm_map_field_exists_on_song(self):
        song = Song(bpm=120)
        assert hasattr(song, "bpm_map")
        assert song.bpm_map == []

    def test_bpm_ramp_generates_correct_length(self):
        ramp = bpm_ramp(120, 80, bars=4, beats_per_bar=4)
        assert len(ramp) == 16

    def test_bpm_ramp_endpoints(self):
        ramp = bpm_ramp(120, 80, bars=4)
        assert ramp[0] == 120.0
        assert ramp[-1] == 80.0

    def test_ritardando_slows_down(self):
        ramp = ritardando(120, bars=4)
        assert ramp[-1] < ramp[0]

    def test_song_with_bpm_map_renders(self):
        song = Song(title="Rit Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(instrument="sine"))
        for _ in range(8):
            tr.add(Note("A", 4, 1.0))
        song.bpm_map = bpm_ramp(120, 60, bars=2)
        audio = song.render()
        assert audio.shape[0] > 0
        assert np.max(np.abs(audio)) > 0.0

    def test_bpm_map_produces_longer_audio_than_flat_bpm_when_slowing(self):
        # Same notes, but one slows down — should produce more samples
        song_flat = Song(title="Flat", bpm=120, sample_rate=SR)
        t1 = song_flat.add_track(Track(instrument="sine"))
        for _ in range(8):
            t1.add(Note("A", 4, 1.0))

        song_rit = Song(title="Rit", bpm=120, sample_rate=SR)
        t2 = song_rit.add_track(Track(instrument="sine"))
        for _ in range(8):
            t2.add(Note("A", 4, 1.0))
        song_rit.bpm_map = bpm_ramp(120, 60, bars=2)

        flat_audio = song_flat.render()
        rit_audio = song_rit.render()
        # Slowing down means later notes take more time → more samples used
        # We check that the rit version has meaningful audio further into the buffer
        flat_last_nonzero = np.max(np.nonzero(np.abs(flat_audio[:, 0]) > 0.001))
        rit_last_nonzero = np.max(np.nonzero(np.abs(rit_audio[:, 0]) > 0.001))
        assert rit_last_nonzero > flat_last_nonzero


class TestTrackSplit:
    def test_split_returns_two_tracks(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 2.0))
        t.add(Note("E", 4, 2.0))
        before, after = t.split(at_beat=2.0)
        assert isinstance(before, Track)
        assert isinstance(after, Track)

    def test_split_preserves_total_beats(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 2.0))
        t.add(Note("E", 4, 2.0))
        t.add(Note("G", 4, 2.0))
        before, after = t.split(at_beat=4.0)
        assert math.isclose(before.total_beats + after.total_beats, t.total_beats)

    def test_split_at_beat_boundary(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 2.0))
        t.add(Note("E", 4, 2.0))
        before, after = t.split(at_beat=2.0)
        assert before.total_beats == 2.0
        assert after.total_beats == 2.0

    def test_split_mid_note(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 4.0))
        before, after = t.split(at_beat=1.5)
        assert math.isclose(before.total_beats, 1.5)
        assert math.isclose(after.total_beats, 2.5)

    def test_split_preserves_metadata(self):
        t = Track(name="lead", instrument="sawtooth", volume=0.7, pan=0.2)
        t.add(Note("C", 4, 4.0))
        before, after = t.split(at_beat=2.0)
        assert before.name == "lead"
        assert after.instrument == "sawtooth"

    def test_split_does_not_mutate_original(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 2.0))
        t.add(Note("E", 4, 2.0))
        _ = t.split(at_beat=2.0)
        assert len(t.beats) == 2

    def test_split_at_zero(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 2.0))
        before, after = t.split(at_beat=0.0)
        assert before.total_beats == 0.0
        assert after.total_beats == 2.0

    def test_split_handles_rests(self):
        t = Track(instrument="piano")
        t.add(Note.rest(2.0))
        t.add(Note("C", 4, 2.0))
        before, after = t.split(at_beat=2.0)
        assert before.beats[0].event.pitch is None
        assert after.beats[0].event.pitch == "C"


class TestTrackFilter:
    def test_filter_keeps_matching_events(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0, velocity=0.8))
        t.add(Note("E", 4, 1.0, velocity=0.3))
        t.add(Note("G", 4, 1.0, velocity=0.9))
        loud = t.filter(lambda e: e.velocity > 0.5)
        pitches = [b.event.pitch for b in loud.beats if b.event.pitch is not None]
        assert "C" in pitches
        assert "G" in pitches
        assert "E" not in pitches

    def test_filter_replaces_rejected_with_rests(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0, velocity=0.8))
        t.add(Note("E", 4, 1.0, velocity=0.3))
        filtered = t.filter(lambda e: e.velocity > 0.5)
        # Second beat should be a rest (replaced E)
        assert filtered.beats[1].event.pitch is None

    def test_filter_preserves_total_beats(self):
        t = Track(instrument="piano")
        for _ in range(8):
            t.add(Note("C", 4, 1.0))
        filtered = t.filter(lambda e: False)  # reject everything
        assert filtered.total_beats == t.total_beats

    def test_filter_preserves_metadata(self):
        t = Track(name="bass", instrument="bass", volume=0.6)
        t.add(Note("E", 2, 1.0))
        filtered = t.filter(lambda e: True)
        assert filtered.name == "bass"
        assert filtered.instrument == "bass"

    def test_filter_does_not_mutate_original(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0, velocity=0.8))
        _ = t.filter(lambda e: False)
        assert t.beats[0].event.pitch == "C"

    def test_filter_by_pitch(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0))
        t.add(Note("D", 4, 1.0))
        t.add(Note("C", 4, 1.0))
        only_c = t.filter(lambda e: getattr(e, "pitch", None) == "C")
        pitches = [b.event.pitch for b in only_c.beats if b.event.pitch is not None]
        assert pitches == ["C", "C"]
