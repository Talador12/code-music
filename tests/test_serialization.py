"""Tests for Song JSON serialization round-trip."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np

from code_music import Chord, Note, Song, SoundDesigner, Track
from code_music.serialization import song_from_json, song_to_json

SR = 22050


class TestSongToJson:
    def test_returns_dict(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        data = song_to_json(song)
        assert isinstance(data, dict)
        assert data["title"] == "Test"
        assert data["bpm"] == 120

    def test_includes_tracks(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano", volume=0.5))
        tr.add(Note("C", 4, 1.0))
        data = song_to_json(song)
        assert len(data["tracks"]) == 1
        assert data["tracks"][0]["name"] == "lead"
        assert len(data["tracks"][0]["beats"]) == 1

    def test_includes_chords(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("C", "min7", 3, duration=4.0))
        data = song_to_json(song)
        event = data["tracks"][0]["beats"][0]["event"]
        assert event["type"] == "chord"
        assert event["root"] == "C"
        assert event["shape"] == "min7"

    def test_includes_rests(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note.rest(2.0))
        data = song_to_json(song)
        event = data["tracks"][0]["beats"][0]["event"]
        assert event["pitch"] is None

    def test_includes_custom_instruments(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        sd = SoundDesigner("my_lead").add_osc("sawtooth")
        song.register_instrument("my_lead", sd)
        data = song_to_json(song)
        assert "my_lead" in data["custom_instruments"]

    def test_as_string(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        result = song_to_json(song, as_string=True)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["title"] == "T"

    def test_to_file(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        song_to_json(song, path=path)
        loaded = json.loads(Path(path).read_text())
        assert loaded["title"] == "T"
        Path(path).unlink()

    def test_version_field(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        data = song_to_json(song)
        assert "version" in data

    def test_metadata_fields(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.composer = "Test"
        song.key_sig = "Am"
        data = song_to_json(song)
        assert data["composer"] == "Test"
        assert data["key_sig"] == "Am"


class TestSongFromJson:
    def test_round_trip_basic(self):
        song = Song(title="Round Trip", bpm=140, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano", volume=0.6, pan=0.2))
        tr.add(Note("C", 5, 1.0))
        tr.add(Note("E", 5, 0.5))
        tr.add(Note.rest(0.5))

        data = song_to_json(song)
        restored = song_from_json(data)

        assert restored.title == "Round Trip"
        assert restored.bpm == 140
        assert len(restored.tracks) == 1
        assert restored.tracks[0].name == "lead"
        assert restored.tracks[0].volume == 0.6
        assert len(restored.tracks[0].beats) == 3

    def test_round_trip_with_chords(self):
        song = Song(title="Chords", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("C", "min7", 3, duration=4.0))
        tr.add(Chord("G", "dom7", 3, duration=4.0))

        restored = song_from_json(song_to_json(song))
        assert len(restored.tracks[0].beats) == 2
        event = restored.tracks[0].beats[0].event
        assert hasattr(event, "root")
        assert event.root == "C"

    def test_round_trip_with_custom_instrument(self):
        song = Song(title="Custom", bpm=120, sample_rate=SR)
        sd = SoundDesigner("my_saw").add_osc("sawtooth", volume=0.5).filter("lowpass", cutoff=2000)
        song.register_instrument("my_saw", sd)
        tr = song.add_track(Track(name="lead", instrument="my_saw"))
        tr.add(Note("A", 4, 2.0))

        restored = song_from_json(song_to_json(song))
        assert "my_saw" in restored._custom_instruments
        audio = restored.render()
        assert np.max(np.abs(audio)) > 0.0

    def test_from_string(self):
        song = Song(title="S", bpm=120, sample_rate=SR)
        json_str = song_to_json(song, as_string=True)
        restored = song_from_json(json_str)
        assert restored.title == "S"

    def test_from_file(self):
        song = Song(title="File", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 4, 1.0))
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        song_to_json(song, path=path)
        restored = song_from_json(path)
        assert restored.title == "File"
        assert len(restored.tracks) == 1
        Path(path).unlink()

    def test_render_after_round_trip(self):
        song = Song(title="Render", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano", volume=0.5))
        tr.add(Note("C", 4, 2.0))
        tr.add(Note("E", 4, 2.0))

        restored = song_from_json(song_to_json(song))
        audio = restored.render()
        assert audio.shape[0] > 0
        assert np.max(np.abs(audio)) > 0.0

    def test_multi_track_round_trip(self):
        song = Song(title="Multi", bpm=120, sample_rate=SR)
        song.add_track(Track(name="kick", instrument="drums_kick")).add(Note("C", 2, 1.0))
        song.add_track(Track(name="pad", instrument="pad")).add(Chord("C", "min7", 3, duration=4.0))
        song.add_track(Track(name="lead", instrument="piano")).add(Note("G", 5, 1.0))

        restored = song_from_json(song_to_json(song))
        assert len(restored.tracks) == 3
        names = [t.name for t in restored.tracks]
        assert "kick" in names and "pad" in names and "lead" in names
