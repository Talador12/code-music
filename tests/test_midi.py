"""Tests for MIDI export."""

import struct
import tempfile
from pathlib import Path

from code_music.engine import Note, Song, Track
from code_music.midi import _var_len, export_midi


class TestVarLen:
    def test_single_byte_values(self):
        assert _var_len(0) == b"\x00"
        assert _var_len(127) == b"\x7f"

    def test_two_byte_values(self):
        # 128 = 0x80 → var-len = 0x81 0x00
        assert _var_len(128) == b"\x81\x00"

    def test_three_byte_values(self):
        # 16383 = 0x3FFF → var-len = 0xFF 0x7F
        assert _var_len(16383) == b"\xff\x7f"


class TestExportMidi:
    def _simple_song(self) -> Song:
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="piano", instrument="piano"))
        tr.extend([Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)])
        return song

    def test_file_created(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            out = export_midi(song, Path(tmp) / "test.mid")
            assert out.exists()
            assert out.stat().st_size > 50

    def test_midi_header(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            out = export_midi(song, Path(tmp) / "test.mid")
            data = out.read_bytes()
            # MThd magic
            assert data[:4] == b"MThd"
            # Header length = 6
            assert struct.unpack(">I", data[4:8])[0] == 6
            # Format type = 1
            assert struct.unpack(">H", data[8:10])[0] == 1

    def test_track_chunks_present(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            out = export_midi(song, Path(tmp) / "test.mid")
            data = out.read_bytes()
            # Count MTrk markers (should be at least 2: tempo + instrument)
            count = data.count(b"MTrk")
            assert count >= 2

    def test_drum_track(self):
        song = Song(title="Drums", bpm=120)
        kick = song.add_track(Track(name="kick", instrument="drums_kick"))
        kick.extend([Note("C", 2, 1.0)] * 4)
        with tempfile.TemporaryDirectory() as tmp:
            out = export_midi(song, Path(tmp) / "drums.mid")
            assert out.exists()

    def test_multi_track(self):
        song = Song(title="Multi", bpm=120)
        for inst in ["piano", "violin", "drums_kick"]:
            tr = song.add_track(Track(instrument=inst))
            tr.add(Note("C", 4, 2.0))
        with tempfile.TemporaryDirectory() as tmp:
            out = export_midi(song, Path(tmp) / "multi.mid")
            data = out.read_bytes()
            # Should have tempo track + 3 instrument tracks
            assert data.count(b"MTrk") >= 4

    def test_path_extension_forced(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            out = export_midi(song, Path(tmp) / "test.wav")  # wrong extension
            assert out.suffix == ".mid"

    def test_rests_skipped(self):
        song = Song(title="Rests", bpm=120)
        tr = song.add_track(Track(instrument="piano"))
        tr.extend([Note.rest(1.0)] * 4)
        with tempfile.TemporaryDirectory() as tmp:
            out = export_midi(song, Path(tmp) / "rests.mid")
            assert out.exists()
