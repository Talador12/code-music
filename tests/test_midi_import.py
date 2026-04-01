"""Tests for MIDI import (import_midi)."""

from __future__ import annotations

import tempfile
from pathlib import Path

from code_music import Note, Song, Track
from code_music.engine import midi_to_note_name
from code_music.midi import export_midi, import_midi


class TestMidiToNoteName:
    def test_middle_c(self):
        assert midi_to_note_name(60) == ("C", 4)

    def test_c_sharp_4(self):
        assert midi_to_note_name(61) == ("C#", 4)

    def test_a440(self):
        assert midi_to_note_name(69) == ("A", 4)

    def test_low_note(self):
        name, octave = midi_to_note_name(24)
        assert name == "C"
        assert octave == 1  # MIDI 24 = C1 in code-music convention

    def test_high_note(self):
        name, octave = midi_to_note_name(108)
        assert name == "C"
        assert octave == 8  # MIDI 108 = C8 in code-music convention


class TestImportMidiRoundTrip:
    def _roundtrip(self, song: Song) -> Song:
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            mid_path = Path(f.name)
        try:
            export_midi(song, mid_path)
            return import_midi(mid_path)
        finally:
            mid_path.unlink(missing_ok=True)

    def test_single_track_notes_survive(self):
        song = Song(title="Single Track", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 4, 1.0))
        tr.add(Note("E", 4, 1.0))
        tr.add(Note("G", 4, 1.0))

        imported = self._roundtrip(song)
        assert len(imported.tracks) >= 1

        # Find the track with notes (non-drum)
        lead = [
            t
            for t in imported.tracks
            if any(b.event and getattr(b.event, "pitch", None) is not None for b in t.beats)
        ]
        assert len(lead) >= 1

        pitches = [b.event.pitch for b in lead[0].beats if b.event and b.event.pitch]
        assert "C" in pitches
        assert "E" in pitches
        assert "G" in pitches

    def test_bpm_preserved(self):
        song = Song(title="Tempo Test", bpm=140)
        tr = song.add_track(Track(instrument="piano"))
        tr.add(Note("A", 4, 1.0))

        imported = self._roundtrip(song)
        assert abs(imported.bpm - 140.0) < 1.0

    def test_multiple_tracks_imported(self):
        song = Song(title="Multi Track", bpm=120)
        for inst in ["piano", "bass", "sawtooth"]:
            tr = song.add_track(Track(instrument=inst))
            tr.add(Note("C", 4, 2.0))

        imported = self._roundtrip(song)
        assert len(imported.tracks) >= 3

    def test_drum_track_imported(self):
        song = Song(title="Drums", bpm=120)
        kick = song.add_track(Track(instrument="drums_kick"))
        kick.add(Note("C", 2, 1.0))
        kick.add(Note("C", 2, 1.0))

        imported = self._roundtrip(song)
        drum_tracks = [t for t in imported.tracks if "drum" in t.instrument]
        assert len(drum_tracks) >= 1

    def test_velocity_preserved(self):
        song = Song(title="Velocity", bpm=120)
        tr = song.add_track(Track(instrument="piano"))
        tr.add(Note("C", 4, 1.0, velocity=0.3))
        tr.add(Note("E", 4, 1.0, velocity=0.9))

        imported = self._roundtrip(song)
        velocities = [
            b.event.velocity
            for t in imported.tracks
            for b in t.beats
            if b.event and getattr(b.event, "pitch", None) is not None
        ]
        # Should have both a quiet and loud note (within MIDI quantization)
        assert min(velocities) < 0.4
        assert max(velocities) > 0.7

    def test_rests_become_gaps(self):
        song = Song(title="Rests", bpm=120)
        tr = song.add_track(Track(instrument="piano"))
        tr.add(Note("C", 4, 1.0))
        tr.add(Note.rest(2.0))
        tr.add(Note("E", 4, 1.0))

        imported = self._roundtrip(song)
        track = imported.tracks[0]
        total = track.total_beats
        # Should be roughly 4 beats (1 + 2 rest + 1)
        assert total > 3.5

    def test_title_from_filename(self):
        song = Song(title="Whatever", bpm=120)
        tr = song.add_track(Track(instrument="piano"))
        tr.add(Note("C", 4, 1.0))

        with tempfile.NamedTemporaryFile(suffix=".mid", prefix="my_cool_song_", delete=False) as f:
            mid_path = Path(f.name)
        try:
            export_midi(song, mid_path)
            imported = import_midi(mid_path)
            assert "my_cool_song" in imported.title.lower().replace(" ", "_")
        finally:
            mid_path.unlink(missing_ok=True)

    def test_custom_title_override(self):
        song = Song(title="Original", bpm=120)
        tr = song.add_track(Track(instrument="piano"))
        tr.add(Note("C", 4, 1.0))

        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            mid_path = Path(f.name)
        try:
            export_midi(song, mid_path)
            imported = import_midi(mid_path, title="Custom Name")
            assert imported.title == "Custom Name"
        finally:
            mid_path.unlink(missing_ok=True)

    def test_instrument_override(self):
        song = Song(title="Override", bpm=120)
        tr = song.add_track(Track(instrument="piano"))
        tr.add(Note("C", 4, 1.0))

        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            mid_path = Path(f.name)
        try:
            export_midi(song, mid_path)
            imported = import_midi(mid_path, instrument="sawtooth")
            assert all(t.instrument == "sawtooth" for t in imported.tracks)
        finally:
            mid_path.unlink(missing_ok=True)
