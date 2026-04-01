"""Tests for v2.4: Track.merge, Track.stretch, Song.export_json/load_json."""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import numpy as np

from code_music.engine import Chord, Note, Song, Track


class TestTrackMerge:
    def test_merge_fills_rests_with_other_events(self):
        t1 = Track(instrument="piano")
        t1.add(Note("C", 4, 1.0))
        t1.add(Note.rest(1.0))

        t2 = Track(instrument="piano")
        t2.add(Note.rest(1.0))
        t2.add(Note("E", 4, 1.0))

        merged = t1.merge(t2)
        assert merged.beats[0].event.pitch == "C"
        assert merged.beats[1].event.pitch == "E"

    def test_merge_self_events_win_over_other(self):
        t1 = Track(instrument="piano")
        t1.add(Note("C", 4, 1.0))

        t2 = Track(instrument="piano")
        t2.add(Note("G", 4, 1.0))

        merged = t1.merge(t2)
        assert merged.beats[0].event.pitch == "C"

    def test_merge_preserves_metadata(self):
        t1 = Track(name="hats", instrument="drums_hat", volume=0.4, pan=0.3)
        t1.add(Note("F#", 6, 1.0))

        t2 = Track(name="ride", instrument="drums_hat", volume=0.5)
        t2.add(Note.rest(1.0))

        merged = t1.merge(t2)
        assert merged.name == "hats"
        assert merged.volume == 0.4

    def test_merge_does_not_mutate_originals(self):
        t1 = Track(instrument="piano")
        t1.add(Note.rest(1.0))

        t2 = Track(instrument="piano")
        t2.add(Note("G", 4, 1.0))

        _ = t1.merge(t2)
        assert t1.beats[0].event.pitch is None

    def test_merge_handles_chords_in_other(self):
        t1 = Track(instrument="piano")
        t1.add(Note.rest(4.0))

        t2 = Track(instrument="piano")
        t2.add(Chord("A", "min", 3, duration=4.0))

        merged = t1.merge(t2)
        assert merged.beats[0].event.root == "A"


class TestTrackStretch:
    def test_stretch_doubles_duration(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0))
        t.add(Note("E", 4, 2.0))
        stretched = t.stretch(2.0)
        assert stretched.beats[0].event.duration == 2.0
        assert stretched.beats[1].event.duration == 4.0

    def test_stretch_halves_duration(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 4.0))
        fast = t.stretch(0.5)
        assert fast.beats[0].event.duration == 2.0

    def test_stretch_preserves_pitch(self):
        t = Track(instrument="piano")
        t.add(Note("G", 5, 1.0))
        stretched = t.stretch(2.0)
        assert stretched.beats[0].event.pitch == "G"
        assert stretched.beats[0].event.octave == 5

    def test_stretch_preserves_rests(self):
        t = Track(instrument="piano")
        t.add(Note.rest(2.0))
        stretched = t.stretch(3.0)
        assert stretched.beats[0].event.pitch is None
        assert stretched.beats[0].event.duration == 6.0

    def test_stretch_preserves_metadata(self):
        t = Track(name="lead", instrument="sawtooth", volume=0.7)
        t.add(Note("C", 4, 1.0))
        stretched = t.stretch(1.5)
        assert stretched.name == "lead"
        assert stretched.instrument == "sawtooth"

    def test_stretch_total_beats_scales(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 2.0))
        t.add(Note("E", 4, 2.0))
        stretched = t.stretch(1.5)
        assert math.isclose(stretched.total_beats, 6.0)

    def test_stretch_does_not_mutate_original(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 1.0))
        _ = t.stretch(3.0)
        assert t.beats[0].event.duration == 1.0


class TestSongExportLoadJson:
    def test_export_creates_file(self):
        song = Song(title="Export Test", bpm=120)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("C", 4, 1.0))

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            json_path = Path(f.name)
        try:
            result = song.export_json(json_path)
            assert result.exists()
            assert result.stat().st_size > 0
        finally:
            json_path.unlink(missing_ok=True)

    def test_load_reconstructs_song(self):
        song = Song(title="Load Test", bpm=140)
        tr = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
        tr.add(Note("E", 2, 2.0))

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            json_path = Path(f.name)
        try:
            song.export_json(json_path)
            loaded = Song.load_json(json_path)
            assert loaded.title == "Load Test"
            assert loaded.bpm == 140
            assert loaded.tracks[0].name == "bass"
        finally:
            json_path.unlink(missing_ok=True)

    def test_roundtrip_render_matches(self):
        song = Song(title="RT Test", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("A", 4, 2.0))

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            json_path = Path(f.name)
        try:
            song.export_json(json_path)
            loaded = Song.load_json(json_path)
            np.testing.assert_array_equal(song.render(), loaded.render())
        finally:
            json_path.unlink(missing_ok=True)
