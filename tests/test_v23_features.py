"""Tests for v2.3: Track.slice, CLI --info, Song.to_dict/from_dict."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from code_music.effects import EffectsChain, reverb
from code_music.engine import Chord, Note, Song, Track


class TestTrackSlice:
    def test_slice_extracts_correct_beats(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 2.0))
        t.add(Note("E", 4, 2.0))
        t.add(Note("G", 4, 2.0))
        t.add(Note("B", 4, 2.0))
        extract = t.slice(2.0, 6.0)
        assert math.isclose(extract.total_beats, 4.0)

    def test_slice_preserves_metadata(self):
        t = Track(name="lead", instrument="sawtooth", volume=0.7, pan=0.3)
        t.add(Note("C", 4, 4.0))
        extract = t.slice(1.0, 3.0)
        assert extract.name == "lead"
        assert extract.instrument == "sawtooth"

    def test_slice_from_zero(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 2.0))
        t.add(Note("E", 4, 2.0))
        extract = t.slice(0.0, 2.0)
        assert math.isclose(extract.total_beats, 2.0)

    def test_slice_to_end(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 2.0))
        t.add(Note("E", 4, 2.0))
        extract = t.slice(2.0, 4.0)
        assert math.isclose(extract.total_beats, 2.0)

    def test_slice_does_not_mutate_original(self):
        t = Track(instrument="piano")
        t.add(Note("C", 4, 4.0))
        _ = t.slice(1.0, 3.0)
        assert t.total_beats == 4.0


class TestSongToFromDict:
    def test_to_dict_returns_dict(self):
        song = Song(title="Test", bpm=140)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 4, 1.0))
        data = song.to_dict()
        assert isinstance(data, dict)
        assert data["title"] == "Test"
        assert data["bpm"] == 140

    def test_to_dict_is_json_serializable(self):
        song = Song(title="JSON Test", bpm=120)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("A", 4, 2.0))
        tr.add(Note.rest(1.0))
        tr.add(Chord("C", "maj", 3, duration=4.0))
        data = song.to_dict()
        text = json.dumps(data)
        assert len(text) > 0

    def test_from_dict_reconstructs_song(self):
        original = Song(title="Original", bpm=130)
        tr = original.add_track(Track(name="bass", instrument="bass", volume=0.6))
        tr.add(Note("E", 2, 2.0))
        tr.add(Note.rest(1.0))
        tr.add(Note("A", 2, 1.0))

        data = original.to_dict()
        restored = Song.from_dict(data)

        assert restored.title == "Original"
        assert restored.bpm == 130
        assert len(restored.tracks) == 1
        assert restored.tracks[0].name == "bass"
        assert restored.tracks[0].instrument == "bass"

    def test_roundtrip_preserves_notes(self):
        original = Song(title="Notes", bpm=120)
        tr = original.add_track(Track(instrument="piano"))
        tr.add(Note("C", 4, 1.0, velocity=0.5))
        tr.add(Note("E", 4, 2.0, velocity=0.9))

        restored = Song.from_dict(original.to_dict())
        beats = restored.tracks[0].beats
        assert beats[0].event.pitch == "C"
        assert beats[0].event.velocity == 0.5
        assert beats[1].event.pitch == "E"
        assert beats[1].event.duration == 2.0

    def test_roundtrip_preserves_chords(self):
        original = Song(title="Chords", bpm=100)
        tr = original.add_track(Track(instrument="pad"))
        tr.add(Chord("A", "min7", 3, duration=4.0))

        restored = Song.from_dict(original.to_dict())
        event = restored.tracks[0].beats[0].event
        assert event.root == "A"
        assert event.shape == "min7"
        assert event.duration == 4.0

    def test_roundtrip_preserves_rests(self):
        original = Song(title="Rests", bpm=120)
        tr = original.add_track(Track(instrument="sine"))
        tr.add(Note.rest(3.0))

        restored = Song.from_dict(original.to_dict())
        assert restored.tracks[0].beats[0].event.pitch is None
        assert restored.tracks[0].beats[0].event.duration == 3.0

    def test_roundtrip_preserves_effects_chain(self):
        original = Song(title="FX", bpm=120)
        tr = original.add_track(Track(name="pad", instrument="pad"))
        tr.add(Note("C", 4, 1.0))
        original.effects["pad"] = EffectsChain().add(reverb, room_size=0.7, wet=0.3, label="reverb")

        restored = Song.from_dict(original.to_dict())
        assert "pad" in restored.effects
        assert len(restored.effects["pad"]) == 1

    def test_roundtrip_preserves_bpm_map(self):
        from code_music.engine import bpm_ramp

        original = Song(title="Tempo", bpm=120)
        tr = original.add_track(Track(instrument="sine"))
        tr.add(Note("C", 4, 1.0))
        original.bpm_map = bpm_ramp(120, 80, bars=2)

        restored = Song.from_dict(original.to_dict())
        assert len(restored.bpm_map) == 8
        assert restored.bpm_map[0] == 120.0

    def test_roundtrip_render_matches(self):
        original = Song(title="Match", bpm=120, sample_rate=22050)
        tr = original.add_track(Track(instrument="sine"))
        tr.add(Note("A", 4, 2.0))

        restored = Song.from_dict(original.to_dict())
        orig_audio = original.render()
        rest_audio = restored.render()
        np.testing.assert_array_equal(orig_audio, rest_audio)


class TestCLIInfo:
    def test_info_flag_prints_metadata(self):
        import subprocess

        result = subprocess.run(
            [".venv/bin/python", "-m", "code_music.cli", "songs/trance_odyssey.py", "--info"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(Path(__file__).resolve().parents[1]),
        )
        assert "title" in result.stdout
        assert "bpm" in result.stdout
        assert "tracks" in result.stdout
